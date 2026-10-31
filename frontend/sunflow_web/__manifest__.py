# -*- coding: utf-8 -*-
{
    'name': 'SunFlow Web - Native Frontend',
    'version': '17.0.1.0.0',
    'summary': 'Native Odoo 17 OWL frontend foundation for SunFlow Solar Operations',
    'description': """
SunFlow Web Frontend
====================
Native Odoo 17 frontend using OWL, ES modules, QWeb templates, and SCSS.
Provides shared workspace layout, reusable components, and role-ready foundation.
    """,
    'author': 'SunFlow Team',
    'category': 'Operations/Solar',
    'website': 'https://github.com/RishiSai23/solarops-odoo',
    'depends': [
        'web',
        'sunflow_core',
    ],
    'data': [
        'views/menu_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Styles
            'sunflow_web/static/src/scss/variables.scss',
            'sunflow_web/static/src/scss/layout.scss',
            'sunflow_web/static/src/scss/components.scss',
            # JavaScript entry
            'sunflow_web/static/src/js/main.js',
            # Components
            'sunflow_web/static/src/components/layout/WorkspaceLayout.js',
            'sunflow_web/static/src/components/navigation/Sidebar.js',
            'sunflow_web/static/src/components/navigation/Header.js',
            'sunflow_web/static/src/components/common/KpiCard.js',
            'sunflow_web/static/src/components/common/StatusBadge.js',
            'sunflow_web/static/src/components/common/DataTable.js',
            'sunflow_web/static/src/components/common/LoadingState.js',
            'sunflow_web/static/src/components/common/EmptyState.js',
            # Dashboard
            'sunflow_web/static/src/components/dashboard/director_dashboard/DirectorDashboard.js',
            # Templates (extra)
            'sunflow_web/static/src/components/dashboard/director_dashboard/DirectorDashboard.xml',
            # Templates
            'sunflow_web/static/src/components/layout/WorkspaceLayout.xml',
            'sunflow_web/static/src/components/navigation/Sidebar.xml',
            'sunflow_web/static/src/components/navigation/Header.xml',
            'sunflow_web/static/src/components/common/KpiCard.xml',
            'sunflow_web/static/src/components/common/StatusBadge.xml',
            'sunflow_web/static/src/components/common/DataTable.xml',
            'sunflow_web/static/src/components/common/LoadingState.xml',
            'sunflow_web/static/src/components/common/EmptyState.xml',
            'sunflow_web/static/src/components/dashboard/director_dashboard/DirectorDashboard.xml',
            'sunflow_web/static/src/xml/templates.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
