# Docker Configuration Directory (`docker/`)

## 1. Directory Overview
The `docker/` directory contains container definitions and configuration files for orchestrating the local Project SunFlow environment, including PostgreSQL 16, Odoo 17, and the FastAPI API gateway.

## 2. Subdirectory Documentation
Currently, `docker/` contains no subdirectories. All orchestration definitions reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `docker-compose.yml` | Multi-container Docker Compose configuration defining PostgreSQL, Odoo 17, volume persistence, and FastAPI API gateway services. |
| `odoo.conf` | Odoo 17 server configuration file configuring the extra-addons path for `sunflow_core` and database connection credentials. |

## 4. Architectural Relationships
`docker/docker-compose.yml` mounts `odoo_addons/` into the `/mnt/extra-addons` directory inside the Odoo container, builds the `backend/` gateway service, and wires them to PostgreSQL.

## 5. Documentation Rules
- Any new Docker configuration file or script added to `docker/` must be recorded in the table above.
- Changes to container ports, environment variables, or service names must be documented here and reflected in root `learned.md`.
