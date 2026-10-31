# SolarOps – Solar Installation Management System

**A Native Odoo 17 ERP Solution for End-to-End Solar Operations**

SolarOps is a modular solar installation management system built natively on Odoo 17. It is designed to manage the complete lifecycle of solar installation operations, from customer enquiries and site surveys to quotations, inventory, installation, warranties, and after-sales service.

## Project Overview

Solar companies often manage customer acquisition, technical surveys, inventory, installation teams, payments, and maintenance through disconnected systems.

SolarOps brings these operations together through a unified Odoo-based platform, providing a centralized source of truth for every customer and solar project.

**Core Principle: One Customer. One Project Record. One Connected Operational Lifecycle.**

## Key Business Workflows

The system is designed to support the following workflows:

1. **Lead Management** – Capture and qualify customer enquiries.
2. **Site Survey Management** – Record rooftop measurements, orientation, shading, and technical feasibility.
3. **Solar Package Configuration** – Configure On-Grid and Off-Grid solar packages.
4. **Bill of Materials Generation** – Determine required panels, inverters, cables, mounting structures, and accessories.
5. **Quotation and Sales** – Generate quotations and manage sales orders.
6. **Payment Tracking** – Track advance and remaining payments.
7. **Inventory Management** – Coordinate equipment availability and warehouse operations.
8. **Serial Number Traceability** – Track serialized solar equipment throughout its lifecycle.
9. **Installation Management** – Coordinate technicians, installation schedules, and completion records.
10. **Warranty Management** – Track equipment warranties and coverage periods.
11. **After-Sales Service** – Manage complaints, repairs, and warranty claims.
12. **Project Costing and Reporting** – Monitor project profitability, expenses, technician hours, and operational performance.

## Technology Stack

| Component | Technology |
|---|---|
| ERP Platform | Odoo 17 Community Edition |
| Backend | Python |
| Database | PostgreSQL 15 |
| ORM | Odoo ORM |
| User Interface | Native Odoo Views and Web Client |
| Reporting | Odoo QWeb Reports |
| Infrastructure | Docker and Docker Compose |
| Version Control | Git and GitHub |

## Repository Structure

```text
solarops-odoo/
│
├── backend/
│   ├── addons/
│   │   └── solar_management/
│   │       ├── __init__.py
│   │       ├── __manifest__.py
│   │       ├── models/
│   │       ├── security/
│   │       ├── views/
│   │       └── data/
│   │
│   ├── config/
│   ├── docs/
│   │   ├── ARCHITECTURE.md
│   │   ├── PROJECT_CONTEXT.md
│   │   └── DEVELOPMENT_TRACKER.md
│   │
│   ├── compose.yaml
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   └── README.md
│
├── .gitignore
└── README.md
```

The primary application is the native Odoo addon located at:

`backend/addons/solar_management/`

The `frontend/` directory is reserved for potential future extensions. The core application uses Odoo's native interface rather than a separate frontend application.

## Architecture

SolarOps follows a modular monolithic architecture using Odoo's native framework.

- **Business Logic:** Python models and methods using the Odoo ORM.
- **Database:** PostgreSQL.
- **Security:** Odoo access control lists, security groups, and record rules.
- **User Interface:** Native Odoo XML views and menus.
- **Automation:** Odoo workflows, scheduled actions, and model methods.
- **Infrastructure:** Dockerized Odoo and PostgreSQL services.

Where appropriate, the system will integrate with Odoo's native applications, including CRM, Sales, Inventory, Purchase, Accounting, Project, Field Service, and Helpdesk.

## Development Setup

### Prerequisites

- Docker Desktop
- Git
- A modern web browser

### 1. Clone the repository

```bash
git clone https://github.com/RishiSai23/solarops-odoo.git
cd solarops-odoo
```

### 2. Configure environment variables

Copy the example environment file:

```powershell
Copy-Item backend/.env.example backend/.env
```

Update the environment values in `backend/.env` if necessary.

### 3. Start the application

```powershell
docker compose -f backend/compose.yaml --env-file backend/.env up -d
```

### 4. Access Odoo

Open:

`http://localhost:8069`

Create or select your development database and install the SolarOps addon through the Odoo Apps interface.

### 5. Stop the application

```powershell
docker compose -f backend/compose.yaml --env-file backend/.env down
```

To preserve development database data, do not add the `-v` flag.

## Security and Configuration

- Environment-specific credentials are stored in the ignored `backend/.env` file.
- `backend/.env.example` documents the required configuration variables.
- Database credentials and runtime data must not be committed to Git.
- Odoo's native security mechanisms are used for access control.

## Development Roadmap

The implementation is divided into independently reviewable modules:

1. Foundation and Environment Setup
2. Lead Management
3. Site Survey Management
4. Solar Package and BOM Configuration
5. Quotation and Sales Order Management
6. Payment Management
7. Inventory and Serial Number Tracking
8. Installation Management
9. Warranty Management
10. After-Sales Service Management
11. Project Costing and Profitability
12. Subsidy and Documentation Management
13. Dashboards and Reporting
14. Integration and End-to-End Validation

Each module will be designed, implemented, manually verified, and documented before proceeding to the next.

## Project Context

**Project:** SolarOps  
**Event:** Odoo × GCET Hackathon 2026  
**Platform:** Odoo 17 Community Edition  
**Database:** PostgreSQL 15  
**Repository:** https://github.com/RishiSai23/solarops-odoo

---

*SolarOps – Connecting every stage of the solar installation lifecycle through one unified ERP platform.*