
# -*- coding: utf-8 -*-
"""
SunFlow demo data seeder for Odoo 17.

Creates up to:
  300 solar.package
  300 solar.package.component (one BOM line per package)
  300 solar.stock.requirement
  300 solar.equipment.dispatch
  300 solar.equipment.dispatch.line (one line per dispatch)

Also creates demo customers and solar projects when needed.

Safe to rerun:
  - Uses stable DEMO-SUNFLOW names/notes to find existing records.
  - Does not delete existing business records.
  - Does not validate deliveries or deduct inventory.
"""

from odoo import fields
from odoo.exceptions import UserError


TARGET = 300
PREFIX = "DEMO-SUNFLOW"

Package = env["solar.package"].sudo()
Component = env["solar.package.component"].sudo()
Requirement = env["solar.stock.requirement"].sudo()
Dispatch = env["solar.equipment.dispatch"].sudo()
DispatchLine = env["solar.equipment.dispatch.line"].sudo()
Project = env["solar.project"].sudo()
Partner = env["res.partner"].sudo()
Product = env["product.product"].sudo()
ProductTemplate = env["product.template"].sudo()

# ---------------------------------------------------------
# 1. Validate that the required models are loaded
# ---------------------------------------------------------

required_models = [
    "solar.package",
    "solar.package.component",
    "solar.stock.requirement",
    "solar.equipment.dispatch",
    "solar.equipment.dispatch.line",
    "solar.project",
]

missing_models = [
    model_name
    for model_name in required_models
    if model_name not in env.registry.models
]

if missing_models:
    raise UserError(
        "Required SunFlow models are not loaded: %s"
        % ", ".join(missing_models)
    )

# ---------------------------------------------------------
# 2. Find or create demo stockable products
# ---------------------------------------------------------

def get_or_create_demo_product(code, name):
    """Create a dedicated zero-stock product for demo requirements."""
    template = ProductTemplate.search(
        [("default_code", "=", code)],
        limit=1
    )

    if not template:
        unit = env.ref("uom.product_uom_unit")

        template = ProductTemplate.create({
            "name": name,
            "default_code": code,
            "detailed_type": "product",
            "uom_id": unit.id,
            "uom_po_id": unit.id,
            "sale_ok": True,
            "purchase_ok": True,
        })

    product = template.product_variant_id

    if not product:
        raise UserError(
            "Could not create a product variant for %s" % name
        )

    return product


products = [
    get_or_create_demo_product(
        "DEMO-SOLAR-PANEL",
        "DEMO Solar PV Panel 550W"
    ),
    get_or_create_demo_product(
        "DEMO-SOLAR-INVERTER",
        "DEMO Solar Inverter 5kW"
    ),
    get_or_create_demo_product(
        "DEMO-SOLAR-BATTERY",
        "DEMO Solar Battery 5kWh"
    ),
]

component_types = ["panel", "inverter", "battery"]

# ---------------------------------------------------------
# 3. Create 300 demo customers and solar projects
# ---------------------------------------------------------

demo_projects = []

for index in range(1, TARGET + 1):
    email = "demo.sunflow.%03d@example.com" % index
    customer_name = "%s Customer %03d" % (PREFIX, index)

    partner = Partner.search(
        [("email", "=", email)],
        limit=1
    )

    if not partner:
        partner = Partner.create({
            "name": customer_name,
            "email": email,
            "phone": "+91 90000 %05d" % index,
            "city": [
                "Chennai",
                "Coimbatore",
                "Madurai",
                "Salem",
                "Tiruchirappalli",
            ][(index - 1) % 5],
            "customer_rank": 1,
        })

    project = Project.search(
        [("partner_id", "=", partner.id)],
        limit=1
    )

    if not project:
        project = Project.create({
            "partner_id": partner.id,
            "kw_capacity": [1.0, 2.0, 3.0, 5.0][(index - 1) % 4],
            "system_type": [
                "on_grid",
                "off_grid",
                "hybrid",
            ][(index - 1) % 3],
            "contract_amount": 75000 + (index * 1250),
            "actual_cost": 50000 + (index * 800),
        })

    demo_projects.append(project)

# ---------------------------------------------------------
# 4. Create 300 solar packages
# ---------------------------------------------------------

packages = []

for index in range(1, TARGET + 1):
    package_name = "%s Package %03d" % (PREFIX, index)

    package = Package.search(
        [("name", "=", package_name)],
        limit=1
    )

    capacity = [1.0, 2.0, 3.0, 5.0][(index - 1) % 4]
    system_type = [
        "on_grid",
        "off_grid",
        "hybrid",
    ][(index - 1) % 3]

    if not package:
        panel_wattage = 550
        panel_count = max(
            2,
            int((capacity * 1000) / panel_wattage)
        )

        package = Package.create({
            "name": package_name,
            "capacity_kw": capacity,
            "system_type": system_type,
            "panel_wattage": panel_wattage,
            "panel_count": panel_count,
            "inverter_capacity_kw": capacity,
            "battery_bank_kwh": (
                capacity * 2 if system_type != "on_grid" else 0.0
            ),
            "base_price": 65000 * capacity,
            "active": True,
            "description": (
                "Demo package generated for SunFlow hackathon."
            ),
        })

    packages.append(package)

# ---------------------------------------------------------
# 5. Create one BOM component per package
# ---------------------------------------------------------

for index, package in enumerate(packages):
    component = Component.search(
        [("package_id", "=", package.id)],
        limit=1
    )

    if not component:
        product_index = index % len(products)
        product = products[product_index]

        Component.create({
            "package_id": package.id,
            "product_id": product.id,
            "quantity": 1.0,
            "component_type": component_types[product_index],
            "is_serialized": False,
            "notes": "SunFlow demo BOM component",
        })

# ---------------------------------------------------------
# 6. Create 300 stock requirements and calculate status
# ---------------------------------------------------------

requirements_created = 0

for index in range(1, TARGET + 1):
    project = demo_projects[index - 1]
    package = packages[index - 1]

    component = Component.search(
        [("package_id", "=", package.id)],
        limit=1
    )

    if not component:
        raise UserError(
            "Missing BOM component for package %s" % package.name
        )

    requirement = Requirement.search([
        ("project_id", "=", project.id),
        ("package_component_id", "=", component.id),
    ], limit=1)

    if not requirement:
        requirement = Requirement.create({
            "project_id": project.id,
            "package_component_id": component.id,
            "product_id": component.product_id.id,
            "component_type": component.component_type,
            "required_qty": 10.0 + (index % 20),
            "is_serialized": component.is_serialized,
            "status": "draft",
        })
        requirements_created += 1

    # Use the actual stock-check business logic.
    requirement.action_check_stock()

# ---------------------------------------------------------
# 7. Create 300 draft equipment dispatches
# ---------------------------------------------------------

dispatches_created = 0
dispatch_lines_created = 0

for index in range(1, TARGET + 1):
    project = demo_projects[index - 1]
    product = products[0]

    marker = "%s-DISPATCH-%03d" % (PREFIX, index)

    dispatch = Dispatch.search(
        [("notes", "=", marker)],
        limit=1
    )

    if not dispatch:
        dispatch = Dispatch.create({
            "project_id": project.id,
            "dispatch_date": fields.Date.today(),
            "state": "draft",
            "notes": marker + " - Demo dispatch; not physically dispatched.",
        })
        dispatches_created += 1

    # Add a non-serialized line so the dispatch form is populated.
    existing_line = DispatchLine.search(
        [("dispatch_id", "=", dispatch.id)],
        limit=1
    )

    if not existing_line:
        DispatchLine.create({
            "dispatch_id": dispatch.id,
            "product_id": product.id,
            "component_type": "panel",
            "quantity": 1.0 + (index % 5),
            "is_serialized": False,
        })
        dispatch_lines_created += 1

# ---------------------------------------------------------
# 8. Commit and print verification counts
# ---------------------------------------------------------

env.cr.commit()

print("\n==========================================")
print(" SUNFLOW DEMO DATA SEED COMPLETED")
print("==========================================")

print("Solar Packages:",
      Package.search_count([("name", "like", PREFIX + " Package %")]))

print("Package Components:",
      Component.search_count([
          ("notes", "=", "SunFlow demo BOM component")
      ]))

print("Demo Projects:",
      Project.search_count([
          ("partner_id.email", "like", "demo.sunflow.%@example.com")
      ]))

print("Stock Requirements:",
      Requirement.search_count([
          ("project_id.partner_id.email", "like",
           "demo.sunflow.%@example.com")
      ]))

print("Stock Shortages:",
      Requirement.search_count([
          ("project_id.partner_id.email", "like",
           "demo.sunflow.%@example.com"),
          ("status", "in", ["shortage", "partial"])
      ]))

print("Equipment Dispatches:",
      Dispatch.search_count([
          ("notes", "like", PREFIX + "-DISPATCH-%")
      ]))

print("Dispatch Lines:",
      DispatchLine.search_count([
          ("dispatch_id.notes", "like", PREFIX + "-DISPATCH-%")
      ]))

print("\nNew requirements created:", requirements_created)
print("New dispatches created:", dispatches_created)
print("New dispatch lines created:", dispatch_lines_created)
print("Dispatches remain in Draft state.")
print("No stock picking was validated.")
print("==========================================\n")
