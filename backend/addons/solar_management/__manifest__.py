# -*- coding: utf-8 -*-
{
    'name': 'SolarOps',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'Solar installation lifecycle management.',
    'description': """
SolarOps: Solar Installation Lifecycle Management
=================================================
A comprehensive native Odoo 17 solution designed to streamline the complete
solar installation operational lifecycle:

Key Capabilities:
-----------------
* Customer leads and initial solar enquiries
* Technical rooftop site surveys and feasibility assessments
* Solar packages and Bills of Materials (BOM)
* Quotations, financing, and sales order processing
* Payment milestones, invoicing, and subsidy tracking
* Inventory control and serialized equipment tracking (panels, inverters, batteries)
* Installation scheduling, execution, and commissioning
* Warranty tracking and certificate issuance
* After-sales ticketing, preventative maintenance, and field repairs
* End-to-end project costing, margins, and operational profitability analytics
    """,
    'author': 'SolarOps Development Team',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'data/sequences.xml',
        'views/menu_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
