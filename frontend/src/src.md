# Frontend Source Directory (`frontend/src/`)

## 1. Directory Overview
The `src/` directory contains the source code for the SunFlow React application, including stylesheets, API communication services, TypeScript domain types, and UI components.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `services/` | HTTP client services and API connectors communicating with the backend gateway. |
| `types/` | Domain TypeScript interfaces matching Odoo and FastAPI models. |

## 3. File Documentation

| File | Responsibility |
|---|---|
| `index.css` | Global styling, Tailwind directives (`@tailwind base;`, etc.), and CSS root variables. |

## 4. Architectural Relationships
Code in `src/` imports types from `types/`, triggers API calls via `services/`, and is compiled into the production bundle by Vite.

## 5. Documentation Rules
- Every newly created file or component subfolder in `src/` must be documented in this file.
