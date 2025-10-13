# Frontend Dashboard (Next.js)

This directory hosts the Next.js 14 dashboard for Legacy Skye Steward. The app consumes the FastAPI backend to present KPI summaries, top-performing menu items, staff praise, and recent handovers.

## Quick Start

```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

The development server runs at http://localhost:3000. Ensure the backend is already running so data loads correctly.

## Smoke Test

You can validate component rendering without starting Next.js:

```bash
cd frontend
npm install
npm run smoke
```

## Troubleshooting

- **Error "Cannot find module 'tailwindcss'"**: Run `npm i -D tailwindcss postcss autoprefixer` to reinstall Tailwind tooling.
- **Modules that only differ in casing**: On Windows, open the project using a consistent path casing (e.g. `C:\Dev\LegacySkyeSteward\frontend`). If the casing changes, stop the dev server and run `npm run dev` again.
- **API calls failing**: Confirm `NEXT_PUBLIC_API_BASE` in `.env.local` matches the backend URL (default `http://127.0.0.1:8000`).
