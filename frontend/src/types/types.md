# TypeScript Types Directory (`frontend/src/types/`)

## 1. Directory Overview
The `types/` directory contains TypeScript type definitions and interfaces that mirror domain entities across Project SunFlow, guaranteeing type safety throughout the frontend codebase.

## 2. Subdirectory Documentation
Currently, `types/` contains no subdirectories. All type definitions reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `project.ts` | Defines TypeScript interfaces for `SolarProject`, `DashboardMetrics`, `LifecycleStage`, and `SystemType`. |

## 4. Architectural Relationships
Types defined here are imported by `frontend/src/services/api.ts`, page components, and UI views to enforce strict compile-time checks on API responses.

## 5. Documentation Rules
- Every newly created TypeScript interface file must be documented in the table above.
- Breaking changes to domain models must be updated here.
