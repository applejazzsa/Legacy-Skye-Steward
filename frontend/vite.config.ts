import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBase = env.VITE_API_BASE || 'http://127.0.0.1:8000'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        // Anything starting with /api will be proxied to FastAPI
        '/api': {
          target: apiBase,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path, // keep /api prefix as-is
        },
      },
    },
  }
})
