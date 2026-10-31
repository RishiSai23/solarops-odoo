# -*- coding: utf-8 -*-
{
    'name': 'SolarOps',
    'version': '17.0.2.2.0',
    'category': 'Services',
    'summary': 'Solar installation lifecycle management: customer inquiries, technical surveys, and project operations.',
    'description': """
SolarOps: Solar Installation Lifecycle Management
=================================================
A comprehensive native Odoo 17 solution designed to streamline the complete
solar installation operational lifecycle:

Key Capabilities:
-----------------
* Customer leads and initial solar enquiries (WhatsApp, Website, Phone)
* Technical rooftop pre-qualification, consumption profiling & feasibility checks
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
    'depends': [
        'base',
        'crm',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/crm_stages.xml',
        'wizards/solar_lead_reason_wizard_views.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
