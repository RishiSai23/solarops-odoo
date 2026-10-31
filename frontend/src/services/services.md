# Services Directory (`frontend/src/services/`)

## 1. Directory Overview
The `services/` directory contains centralized API client services and data fetchers that communicate with the FastAPI backend orchestration layer.

## 2. Subdirectory Documentation
Currently, `services/` contains no subdirectories. All service modules reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `api.ts` | Centralized asynchronous HTTP client communicating with backend endpoints (`/api/v1/health`, `/api/v1/projects`, `/api/v1/analytics/dashboard`). |

## 4. Architectural Relationships
`services/api.ts` is consumed by React view pages and components (`frontend/src/pages/Dashboard.tsx`) to retrieve remote operational data.

## 5. Documentation Rules
- Every service module created here must be listed in the table above with its API responsibility.
- Changes in endpoint URLs or payloads must be updated in this file.
