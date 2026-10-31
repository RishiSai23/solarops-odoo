# Technical Mastery & Codebase Knowledge Directory (`docs/technical-mastery/`)

## 1. Directory Overview
The `technical-mastery/` directory provides in-depth, code-level reverse engineering guides, framework architecture deep-dives, execution flow walkthroughs, and technical defense interview Q&A for Project SunFlow. It serves as the primary technical training handbook for developers and engineers defending the platform in hackathon evaluations and architectural audits.

## 2. Subdirectory Documentation
Currently, `technical-mastery/` contains no subdirectories. All technical guides reside directly in this directory.

## 3. File Documentation Table

| File | Responsibility |
|---|---|
| `phase4_reverse_engineering.md` | Exhaustive code-level reverse engineering of Phase 4 (Stock & Procurement): data models, field specifications, constraints, method inputs/outputs/side-effects, failure behaviors, and test mappings for `package_bom.py`, `stock_requirement.py`, `equipment_dispatch.py`, `solar_package_ext.py`, and `inventory_views.xml`. |
| `odoo_internals_explained.md` | Theoretical and architectural explanation of Odoo framework internals actively used in SunFlow (Model inheritance, recordset operations, environment, `@api.depends`, `@api.constrains`, `ir.model.access.csv`, `stock.quant`, `stock.lot`, `stock.move.line`, and Odoo 17 view compilation). |
| `phase4_execution_flow.md` | Complete end-to-end operational execution walkthrough from Package BOM configuration through demand generation, quant inspection, PO replenishment, serial allocation, native stock picking execution, and project stage progression. Includes detailed Mermaid flowcharts and sequence diagrams. |
| `judge_qa_defense.md` | Comprehensive 30-question technical defense interview guide categorized into Beginner (10), Intermediate (10), and Advanced Architecture/Failure-Handling (10) grounded strictly in actual source code and real-world failure handling. |

## 4. Architectural Relationships
- **Inbound Context**: Reverse-engineers source implementations located in `odoo_addons/sunflow_core/models/`, `odoo_addons/sunflow_core/views/`, and `odoo_addons/sunflow_core/tests/`.
- **Outbound Value**: Supplies engineers, judges, and developers with the theoretical foundation and operational rationale required to explain, test, and extend the platform into Phase 5 (Field Operations & Installation Management).

## 5. Documentation Rules
- Every technical guide added to this directory must be strictly grounded in actual source code without fictional features.
- Any change to model signatures, constraints, or execution flows must be reflected across these technical mastery guides and root `learned.md`.
- Must pass `python scripts/validate_docs.py` validation without warnings.

