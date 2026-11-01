# -*- coding: utf-8 -*-
"""
SunFlow Solar Package Extensions.

This file is reserved for Odoo model extensions.
Do not execute demo-data generation code at import time.

Odoo imports this module while loading the registry.
An Odoo environment (env) is not available at module level.
"""

from odoo import models


class SolarPackageExtension(models.Model):
    """
    Extension hook for the solar.package model.

    Add custom fields and methods here when required.
    """

    _inherit = "solar.package"