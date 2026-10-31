"""
Odoo XML-RPC Connector Client
------------------------------
Manages authentication, connection pooling, and remote procedure calls
to the authoritative Odoo ERP instance.
"""

import xmlrpc.client
import logging
from typing import Optional, Dict, Any, List
from app.config import settings
from app.odoo.mock_adapter import MockOdooAdapter

logger = logging.getLogger("sunflow.odoo")

class OdooClient:
    def __init__(self):
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.username = settings.ODOO_USER
        self.password = settings.ODOO_PASSWORD
        self.uid: Optional[int] = None
        self.mock_adapter = MockOdooAdapter()
        self.use_mock = settings.SANDBOX_FALLBACK

    def authenticate(self) -> bool:
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common', allow_none=True)
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                logger.info(f"Successfully authenticated with Odoo ERP (UID: {self.uid})")
                self.use_mock = False
                return True
        except Exception as e:
            logger.warning(f"Could not connect to Odoo server at {self.url} ({e}). Falling back to Sandbox Adapter.")
            self.use_mock = True
        return self.use_mock

    def get_projects(self, stage: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.use_mock or not self.uid:
            return self.mock_adapter.get_projects(stage)
        try:
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object', allow_none=True)
            domain = []
            if stage:
                domain.append(('stage', '=', stage))
            records = models.execute_kw(
                self.db, self.uid, self.password,
                'solar.project', 'search_read',
                [domain],
                {'fields': ['id', 'name', 'partner_id', 'stage', 'kw_capacity', 'contract_amount', 'actual_cost', 'gross_margin', 'installation_date', 'completion_date']}
            )
            # Normalize records
            normalized = []
            for r in records:
                partner_name = r['partner_id'][1] if isinstance(r.get('partner_id'), (list, tuple)) else "Unknown"
                normalized.append({
                    "id": r["id"],
                    "name": r.get("name", ""),
                    "partner_name": partner_name,
                    "kw_capacity": r.get("kw_capacity", 0.0),
                    "system_type": "on_grid",
                    "stage": r.get("stage", "lead"),
                    "contract_amount": r.get("contract_amount", 0.0),
                    "actual_cost": r.get("actual_cost", 0.0),
                    "gross_margin": r.get("gross_margin", 0.0),
                    "installation_date": r.get("installation_date"),
                    "completion_date": r.get("completion_date"),
                })
            return normalized
        except Exception as e:
            logger.error(f"Error fetching projects from Odoo: {e}. Falling back to sandbox.")
            return self.mock_adapter.get_projects(stage)

    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_mock or not self.uid:
            return self.mock_adapter.create_project(data)
        try:
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object', allow_none=True)
            # Search or create customer partner
            partner_ids = models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search',
                [[['name', '=', data['partner_name']]]]
            )
            if partner_ids:
                partner_id = partner_ids[0]
            else:
                partner_id = models.execute_kw(
                    self.db, self.uid, self.password,
                    'res.partner', 'create',
                    [{'name': data['partner_name']}]
                )

            project_vals = {
                'partner_id': partner_id,
                'kw_capacity': data['kw_capacity'],
                'system_type': data.get('system_type', 'on_grid'),
                'contract_amount': data['contract_amount'],
                'actual_cost': data['contract_amount'] * 0.68,
                'stage': 'lead'
            }
            new_id = models.execute_kw(
                self.db, self.uid, self.password,
                'solar.project', 'create',
                [project_vals]
            )
            return {
                "id": new_id,
                "name": f"SPF-{new_id:04d}",
                "partner_name": data["partner_name"],
                "kw_capacity": data["kw_capacity"],
                "system_type": data.get("system_type", "on_grid"),
                "stage": "lead",
                "contract_amount": data["contract_amount"],
                "actual_cost": data["contract_amount"] * 0.68,
                "gross_margin": data["contract_amount"] * 0.32,
            }
        except Exception as e:
            logger.error(f"Odoo create_project error: {e}. Falling back to sandbox.")
            return self.mock_adapter.create_project(data)

odoo_client = OdooClient()
