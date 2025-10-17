import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'node:path';

// Helper: read a JSON file from /mock
function readMock(file: string) {
  const p = path.resolve(process.cwd(), 'mock', file);
  return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '{}';
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const API_MODE = (env.VITE_API_MODE || 'mock').toLowerCase();
  const API_BASE = env.VITE_API_BASE || 'http://127.0.0.1:8000';

  return {
    plugins: [react()],
    server: {
      port: 5173,
      // Transparent mock: serve JSON for /api/* only in mock mode
      configureServer(server) {
        if (API_MODE === 'mock') {
          server.middlewares.use((req, res, next) => {
            if (!req.url) return next();

            // Map your frontend calls to mock files
            if (req.url.startsWith('/api/analytics/kpi-summary')) {
              res.setHeader('Content-Type', 'application/json; charset=utf-8');
              res.end(readMock('kpi-summary.json'));
              return;
            }
            if (req.url.startsWith('/api/incidents')) {
              res.setHeader('Content-Type', 'application/json; charset=utf-8');
              res.end(readMock('incidents.json'));
              return;
            }
            if (req.url.startsWith('/api/handovers/recent')) {
              res.setHeader('Content-Type', 'application/json; charset=utf-8');
              res.end(readMock('handovers-recent.json'));
              return;
            }
            if (req.url.startsWith('/api/analytics/top-items')) {
              res.setHeader('Content-Type', 'application/json; charset=utf-8');
              res.end(readMock('top-items.json'));
              return;
            }

            next();
          });
        }
      },
      // When API_MODE=live, proxy all /api to your backend
      proxy: API_MODE === 'live'
        ? {
            '/api': {
              target: API_BASE,
              changeOrigin: true,
              secure: false
            }
          }
        : undefined
    }
  };
});
