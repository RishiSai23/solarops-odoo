# Tests Directory (`odoo_addons/sunflow_core/tests/`)

## 1. Directory Overview
The `tests/` directory contains Odoo-style unit and integration tests for the `sunflow_core` module. Tests use `odoo.tests.common.TransactionCase`, which wraps each test in a database transaction that is automatically rolled back, ensuring no test data pollutes the production database.

## 2. Subdirectory Documentation
Currently, `tests/` contains no subdirectories. All test files reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Python package initialization importing all test modules so Odoo's test runner discovers them. |
| `test_phase4_inventory.py` | **Phase 4 test suite** with 25 test cases across 5 test classes: `TestPackageBOM` (BOM creation, quantity constraints, serial flags), `TestStockRequirementGeneration` (requirement generation from BOM, shortage calculation), `TestSerialNumberValidation` (lot-product mismatch rejection, duplicate-allocation prevention), `TestDispatchWorkflow` (dispatch state machine, serial completeness flag), and `TestProjectStockIntegration` (end-to-end: package → requirements → dispatch → project stage). |
| `test_survey_lifecycle.py` | **Site Survey & Project Lifecycle Integration Test Suite** with 10 TransactionCase tests covering: draft survey quotation guard, rejected survey quotation guard, conditional survey resolution requirement, feasible survey approval progression (`lead` -> `survey` -> `feasibility` -> `quotation`), technical grid load compatibility (`kw_capacity <= sanctioned_load_kw`), multiple survey precedence, rejection without silent invalidation, and automated quotation order generation. |
| `verify_runtime_e2e.py` | **Phase 4 End-to-End Integration Gate verification script** executed inside genuine Odoo 17 (`odoo shell -d sunflow_test`) covering the entire 15-step runtime lifecycle: package creation, BOM setup, requirement generation, PO creation & confirmation, serialized incoming receipt, stock recalculation, dispatch validation, duplicate serial prevention, and ACL user verification. |

## 4. Architectural Relationships
Tests import and exercise the models defined in `odoo_addons/sunflow_core/models/`. They use Odoo's `TransactionCase` framework, which requires a running Odoo instance with a test database. Tests are executed via:

```
./odoo-bin -d <test_db> --test-enable -u sunflow_core --stop-after-init
```

## 5. Documentation Rules
- Every new test file must be imported in `__init__.py` and documented in the table above.
- Tests must not use `@unittest.skip` to pass — all tests must genuinely pass.
- Do not mark Phase requirements as complete until the corresponding tests pass.

