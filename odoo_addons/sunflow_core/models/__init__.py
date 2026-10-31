# -*- coding: utf-8 -*-
# Phase 1-3: Core lifecycle models
from . import project_lifecycle
from . import site_survey
from . import survey_reject_wizard
from . import solar_package
from . import installation_order
from . import warranty_registry
# Phase 4: Stock & Procurement
from . import package_bom         # solar.package.component — BOM lines
from . import stock_requirement   # solar.stock.requirement — inventory demand
from . import equipment_dispatch  # solar.equipment.dispatch / solar.equipment.dispatch.line
from . import solar_package_ext   # _inherit extensions for solar.package + solar.project
