# solarops-odoo
Native Odoo Solar Installation Management System – managing leads, site surveys, quotations, inventory, installations, warranties and service operations.

## Repository Overview

SolarOps is structured into two top-level application directories to maintain clean architectural boundaries:

- **`backend/`**: Contains the native Odoo 17 modular application, custom addons, Docker infrastructure (`compose.yaml`), environment configurations, and technical documentation.
  - Native Addon Location: [`backend/addons/solar_management`](backend/addons/solar_management)
  - Backend Documentation & Setup Guide: [`backend/README.md`](backend/README.md)
  - System Architecture: [`backend/docs/ARCHITECTURE.md`](backend/docs/ARCHITECTURE.md)
  - Development Roadmap: [`backend/docs/DEVELOPMENT_TRACKER.md`](backend/docs/DEVELOPMENT_TRACKER.md)
  - Domain Context: [`backend/docs/PROJECT_CONTEXT.md`](backend/docs/PROJECT_CONTEXT.md)
- **`frontend/`**: Reserved for future architectural extensions (e.g., custom client portals, dedicated technician mobile web apps). See [`frontend/README.md`](frontend/README.md).

For quickstart setup, Docker execution, and Odoo addon installation instructions, refer to [`backend/README.md`](backend/README.md).
