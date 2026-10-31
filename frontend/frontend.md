# Frontend Directory (`frontend/`)

## 1. Directory Overview
The `frontend/` directory houses the Single-Page Application (SPA) client for Project SunFlow, built with React 18, Vite, TypeScript, and Tailwind CSS. It delivers executive operations dashboards and field technician mobile-optimized workflows.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `src/` | React application source code, including pages, components, API client services, and TypeScript types. |

## 3. File Documentation

| File | Responsibility |
|---|---|
| `index.html` | Application HTML entrypoint with metadata, solar favicon, and root DOM mount point. |
| `package.json` | Node package manager definition with dependencies (React, Lucide, Tailwind) and dev scripts. |
| `postcss.config.js` | PostCSS configuration plugin pipeline for Tailwind CSS and Autoprefixer. |
| `tailwind.config.js` | Tailwind design system configuration with custom solar amber and navy palettes. |
| `tsconfig.json` | TypeScript compiler options enforcing strict typing, module resolution, and JSX support. |
| `vite.config.ts` | Vite bundler configuration including React plugin and reverse proxy to the FastAPI backend. |

## 4. Architectural Relationships
The frontend communicates over HTTP with `backend/` via `/api/v1` routes, displaying live lifecycle data sourced from Odoo ERP.

## 5. Documentation Rules
- Any configuration file added to `frontend/` must be listed in the table above.
- Changes to dependencies or build scripts must be documented here and reflected in root `learned.md`.
