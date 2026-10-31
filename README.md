# Project SunFlow — Unified Solar Operations & Lifecycle ERP

> **Odoo × GCET Hackathon Finale**  
> *Target Business Scenario: SunPower Solutions (Residential & Commercial Solar Operations)*

[![Documentation Validation](https://img.shields.io/badge/Docs-100%25%20Validated-brightgreen.svg)](#documentation-system)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Engine%20Odoo%20%2B%20FastAPI-blue.svg)](#system-architecture)
[![Tech Stack](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite%20%2B%20Tailwind-purple.svg)](#tech-stack)

---

## ☀️ The Core Thesis
> **ONE CUSTOMER. ONE PROJECT RECORD. ONE CONNECTED OPERATIONAL LIFECYCLE.**

Project SunFlow bridges the critical divide between customer acquisition, engineering feasibility, field execution, and post-installation warranty management. Rather than operating in isolated silos, every team works on a unified, authoritative project lifecycle anchored in **Odoo ERP**.

---

## 🚀 The 19-Stage Solar Operations Lifecycle
SunFlow models and automates the complete operational journey:
1. **Customer Enquiry & CRM**: Lead intake & energy needs.
2. **Lead Qualification**: Bill verification & solar feasibility.
3. **Site Survey**: Digital rooftop assessment (tilt, azimuth, shading, sanctioned load).
4. **Solar Package Configuration**: 1 kW to 5 kW On-Grid/Off-Grid/Hybrid selection.
5. **Automated BOM Generation**: Dynamic calculation of panels, inverters, cables, and BOS.
6. **Quotation & Sales Order**: Milestone-based commercial proposals.
7. **Advance Payment Tracking**: Automated milestone invoice & payment reconciliation.
8. **Inventory Reservation**: Warehouse allocation of certified equipment.
9. **Serial Number Traceability**: Barcode/QR scanning for high-value components into `stock.lot`.
10. **Dispatch Management**: Logistics tracking & delivery verification.
11. **Technician Scheduling**: Allocation of certified field installation crews.
12. **Installation Execution**: Step-by-step checklist with geo-stamped photos & electrical readings.
13. **Digital Customer Acceptance**: Customer sign-off & electronic handover certificate.
14. **Automatic Warranty Registration**: Serial-linked multi-year equipment warranties.
15. **After-Sales Service & Ticketing**: Customer support portal & SLA dispatch.
16. **Warranty Validation & RMA**: Serial validation preventing warranty fraud.
17. **Project Profitability**: Real-time margin analytics (Revenue vs Materials, Labor, Logistics).
18. **Subsidy Tracking**: Government subsidy application tracking (e.g., PM Surya Ghar).
19. **Management Analytics**: Executive KPI dashboards & operational throughput metrics.

---

## 🏗️ System Architecture

- **Authoritative ERP Core**: Odoo 17 / 18 + PostgreSQL (`odoo_addons/sunflow_core`)
- **API & Orchestration Gateway**: Python 3.10+ FastAPI (`backend/`)
- **Modern Executive & Field Client**: React 18 + Vite + TypeScript + Tailwind CSS (`frontend/`)
- **Deployment**: Docker Compose multi-service stack (`docker/`)

---

## 📖 Mandatory Agent & Developer Navigation
Before modifying code in this repository, please review:
- [`AGENTS.md`](./AGENTS.md) — Comprehensive guide for AI coding agents.
- [`learned.md`](./learned.md) — Architectural and business domain knowledge repository.
- [`progress.md`](./progress.md) — Single source of truth for implementation progress.
- [`ENGINEERING_PROTOCOL.md`](./ENGINEERING_PROTOCOL.md) — Code quality & commit guidelines.
- **Directory Markdown Files**: Every directory contains `<directory_name>/<directory_name>.md`.

---

## 🛠️ Quick Start

### Validate Documentation Integrity
```bash
python scripts/validate_docs.py
```

### Run Backend API Gateway
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Run Frontend Client
```bash
cd frontend
npm install
npm run dev
```

### Run Full Stack with Docker
```bash
docker compose -f docker/docker-compose.yml up -d
```
