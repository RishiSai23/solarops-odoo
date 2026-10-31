# SolarOps — Backend & Odoo Environment

This directory houses the complete backend infrastructure, native Odoo 17 addon modules, Docker orchestration, and technical documentation for **SolarOps**.

---

## 1. Prerequisites

Before starting the environment, verify that the following tools are installed on Windows 11:

- **Docker Desktop** (with the WSL 2 backend enabled)
- **Git**
- **PowerShell 7+** or Windows PowerShell

---

## 2. Environment Configuration

The Docker Compose setup uses environment variables defined in `.env` to configure PostgreSQL credentials and host port bindings without hardcoding secrets.

1. Navigate to the `backend/` directory or prepare the file from the repository root:
   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```
2. Review `backend/.env` and adjust the variables if needed:
   - `POSTGRES_DB`: Target database name (default: `postgres`).
   - `POSTGRES_USER`: Database user (default: `odoo`).
   - `POSTGRES_PASSWORD`: Database password (change from placeholder for production).
   - `ODOO_PORT`: Host port mapping for Odoo web interface (default: `8069`).

> [!IMPORTANT]
> The `.env` file contains local secrets and must never be committed to Git. It is excluded by `.gitignore`.

---

## 3. Docker Service Architecture

The environment defines two containerized services via `backend/compose.yaml`:
- **`db`**: PostgreSQL 15 container with an automated health check (`pg_isready`). Internal network only; port 5432 is not exposed to the host.
- **`odoo`**: Odoo 17 Community container mounting `./addons` to `/mnt/extra-addons` and configured to wait until PostgreSQL is healthy.

---

## 4. Starting the Environment

To start the SolarOps containers from the repository root:

```powershell
# Validate the compose file syntax
docker compose -f backend/compose.yaml --env-file backend/.env config

# Start containers in detached mode
docker compose -f backend/compose.yaml --env-file backend/.env up -d
```

### Checking Status and Logs

```powershell
# View running service status and health checks
docker compose -f backend/compose.yaml ps

# Stream logs from Odoo service
docker compose -f backend/compose.yaml logs -f odoo

# Stream logs from Database service
docker compose -f backend/compose.yaml logs -f db
```

---

## 5. Accessing Odoo

Once the Odoo service log indicates it is listening:

1. Open your browser and navigate to:
   ```
   http://localhost:8069
   ```
2. If prompted by the Odoo Database Manager, create a new database:
   - **Database Name**: `solarops_dev` (or preferred name)
   - **Email / Password**: Your administrator credentials
   - **Demo data**: Leave unchecked for a clean development database.

---

## 6. Installing the SolarOps Addon

Once logged into Odoo as an administrator:

1. Enable Developer Mode:
   - Go to **Settings** -> Scroll down to **Developer Tools** -> Click **Activate the developer mode**.
2. Update the App List:
   - Navigate to the **Apps** menu.
   - Click **Update Apps List** in the top navigation bar.
   - Confirm by clicking **Update**.
3. Install SolarOps:
   - In the Apps search bar, remove the default `Apps` filter.
   - Search for `SolarOps` or `solar_management`.
   - Click **Activate** (or **Install**).
4. Verify Security & Menu:
   - Verify that the `Solar Management` category and `SolarOps User` / `SolarOps Manager` groups exist in **Settings** -> **Users & Companies** -> **Groups**.
   - Note: The root `SolarOps` menu will be visible in the navigation once sub-menus and actions are added in subsequent modules.

---

## 7. Stopping the Environment

To stop the containers without losing database data:

```powershell
docker compose -f backend/compose.yaml down
```

To stop containers and remove persistent volumes (irreversible data reset):

```powershell
docker compose -f backend/compose.yaml down -v
```
