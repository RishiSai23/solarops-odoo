# Tests Directory (`odoo_addons/sunflow_core/tests/`)

## 1. Directory Overview
The `tests/` directory contains Odoo automated tests for the `sunflow_core` addon, written using `odoo.tests.common.TransactionCase`. Tests are executed within the Odoo server (Docker container) with `--test-enable`, not on the host Python environment.

## 2. Subdirectory Documentation
Currently, `tests/` contains no subdirectories. All test modules reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Test package initialization importing `test_site_survey`. |
| `test_site_survey.py` | TransactionCase tests covering survey workflow transitions, submission validations, self-action prevention, approval/rejection history, quotation integration, and reset-to-draft manager restriction. |

## 4. Architectural Relationships
Tests exercise the `solar.survey` model (`models/site_survey.py`), the `solar.survey.reject.wizard` transient model (`models/survey_reject_wizard.py`), and `solar.project` quotation integration (`models/project_lifecycle.py`). They run against the `sunflow_demo` database with the `sunflow_core` module installed.

## 5. How to run
Tests cannot be executed on the host because the `odoo` Python package is not installed locally (Odoo runs containerized in Docker). Run them inside the Odoo container:

```
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d sunflow_demo -u sunflow_core --test-enable -i sunflow_core --test-tags /tests/
```
(Adjust the service name and config path to match `docker/compose.yaml`.)

## 6. Documentation Rules
- Every test module added to `tests/` must be imported in `__init__.py` and documented in the table above.
- New models or workflows covered by tests must be reflected here and in root `learned.md`.
