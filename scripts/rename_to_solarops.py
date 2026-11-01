# -*- coding: utf-8 -*-
"""
Renames 'SunFlow Solar' to 'SolarOps' across source and config files.
"""

replacements = [
    (
        'odoo_addons/sunflow_core/views/menu_views.xml',
        'name="SunFlow Solar"',
        'name="SolarOps"'
    ),
    (
        'odoo_addons/sunflow_core/__manifest__.py',
        "'name': 'SunFlow Core — Solar Operations & Lifecycle ERP'",
        "'name': 'SolarOps Core — Solar Operations & Lifecycle ERP'"
    ),
    (
        'odoo_addons/sunflow_core/views/views.md',
        'the "SunFlow Solar" top-level menu',
        'the "SolarOps" top-level menu'
    ),
    (
        'frontend/preview/index.html',
        '<div class="o_sunflow_sidebar_header">SunFlow Solar</div>',
        '<div class="o_sunflow_sidebar_header">SolarOps</div>'
    ),
    (
        'frontend/src/components/navigation/Sidebar.tsx',
        '<div className="font-semibold">SunFlow Solar</div>',
        '<div className="font-semibold">SolarOps</div>'
    ),
    (
        'frontend/sunflow_web/__manifest__.py',
        "'summary': 'Native Odoo 17 OWL frontend foundation for SunFlow Solar Operations'",
        "'summary': 'Native Odoo 17 OWL frontend foundation for SolarOps Operations'"
    ),
]

for path, old, new in replacements:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if old in content:
            content = content.replace(old, new)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated {path}")
        else:
            print(f"[SKIP] Target string not found in {path}")
    except Exception as e:
        print(f"[ERROR] Failed {path}: {e}")

