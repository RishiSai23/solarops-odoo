# -*- coding: utf-8 -*-
"""
solar.package & solar.project — Extended with BOM component lines & stock generation.
====================================================================================
This file adds Phase 4 fields and methods:
  - SolarPackageExtended: adds component_ids (BOM lines) and action_view_components.
  - SolarProjectExtended: adds package_id, stock_requirement_ids, dispatch_ids,
    smart buttons, stock status computation, and dispatch creation actions.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SolarPackageExtended(models.Model):
    """Extends solar.package with BOM component lines."""
    _inherit = 'solar.package'

    component_ids = fields.One2many(
        'solar.package.component',
        'package_id',
        string='Bill of Materials',
        help='Component products and quantities required for one installation of this package.',
    )
    component_count = fields.Integer(
        string='# BOM Lines',
        compute='_compute_component_count',
        store=True,
    )

    @api.depends('component_ids')
    def _compute_component_count(self):
        for rec in self:
            rec.component_count = len(rec.component_ids)

    def action_view_components(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bill of Materials — %s') % self.name,
            'res_model': 'solar.package.component',
            'view_mode': 'tree,form',
            'domain': [('package_id', '=', self.id)],
            'context': {'default_package_id': self.id},
        }


class SolarProjectExtended(models.Model):
    """Extends solar.project with Phase 4 stock & procurement links."""
    _inherit = 'solar.project'

    package_id = fields.Many2one(
        'solar.package',
        string='Solar Package',
        tracking=True,
        help='The solar package template selected for this installation.',
    )
    stock_requirement_ids = fields.One2many(
        'solar.stock.requirement',
        'project_id',
        string='Stock Requirements',
    )
    dispatch_ids = fields.One2many(
        'solar.equipment.dispatch',
        'project_id',
        string='Equipment Dispatches',
    )
    stock_ready = fields.Boolean(
        string='Stock Ready',
        compute='_compute_stock_ready',
        store=False,
        help='True when all stock requirements have status "available" or "reserved".',
    )
    has_shortage = fields.Boolean(
        string='Has Shortage',
        compute='_compute_stock_ready',
        store=False,
    )
    requirement_count = fields.Integer(
        string='# Requirements',
        compute='_compute_requirement_count',
        store=True,
    )
    dispatch_count = fields.Integer(
        string='# Dispatches',
        compute='_compute_dispatch_count',
        store=True,
    )

    @api.depends('stock_requirement_ids')
    def _compute_requirement_count(self):
        for rec in self:
            rec.requirement_count = len(rec.stock_requirement_ids)

    @api.depends('dispatch_ids')
    def _compute_dispatch_count(self):
        for rec in self:
            rec.dispatch_count = len(rec.dispatch_ids)

    @api.depends('stock_requirement_ids', 'stock_requirement_ids.status')
    def _compute_stock_ready(self):
        for rec in self:
            if not rec.stock_requirement_ids:
                rec.stock_ready = False
                rec.has_shortage = False
                continue
            reqs = rec.stock_requirement_ids
            rec.has_shortage = any(
                r.status in ('shortage', 'partial') for r in reqs
            )
            rec.stock_ready = all(
                r.status in ('available', 'reserved', 'dispatched') for r in reqs
            )

    def action_generate_stock_requirements(self):
        """
        Generate solar.stock.requirement records from the project's
        solar.package BOM. Called after the sales order is confirmed.

        Rules:
          - Only runs if package_id is set.
          - Clears existing 'draft' requirements before regenerating.
          - Does not delete 'reserved' or 'dispatched' requirements.
          - Creates one requirement line per BOM component.
        """
        self.ensure_one()
        if not self.package_id:
            raise UserError(_(
                'Please assign a Solar Package to this project before '
                'generating stock requirements.'
            ))
        if not self.package_id.component_ids:
            raise UserError(_(
                'The selected package "%s" has no BOM components defined. '
                'Please configure the Bill of Materials first.'
            ) % self.package_id.name)

        # Remove only draft requirements (do not disturb in-progress ones)
        draft_reqs = self.stock_requirement_ids.filtered(lambda r: r.status == 'draft')
        draft_reqs.unlink()

        # Create one requirement per BOM line
        for comp in self.package_id.component_ids:
            self.env['solar.stock.requirement'].create({
                'project_id': self.id,
                'package_component_id': comp.id,
                'product_id': comp.product_id.id,
                'component_type': comp.component_type,
                'required_qty': comp.quantity,
                'is_serialized': comp.is_serialized,
                'status': 'draft',
            })

        # Immediately check stock for all new requirements
        self.stock_requirement_ids.action_check_stock()

        # Advance stage if currently at 'order'
        if self.stage == 'order':
            self.stage = 'procurement'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Stock Requirements Generated'),
                'message': _(
                    '%d requirement line(s) created for package "%s". '
                    'Review shortages in the Inventory tab.'
                ) % (len(self.stock_requirement_ids), self.package_id.name),
                'sticky': False,
                'type': 'success',
            },
        }

    def action_check_all_stock(self):
        """Refresh stock snapshots for all requirements of this project."""
        self.ensure_one()
        if not self.stock_requirement_ids:
            raise UserError(_('No stock requirements exist for this project yet.'))
        self.stock_requirement_ids.action_check_stock()

    def action_view_requirements(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Requirements — %s') % self.name,
            'res_model': 'solar.stock.requirement',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_dispatches(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Equipment Dispatches — %s') % self.name,
            'res_model': 'solar.equipment.dispatch',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_create_dispatch(self):
        """
        Create a new equipment dispatch record pre-populated from
        the project's stock requirements.
        """
        self.ensure_one()
        if not self.stock_requirement_ids:
            raise UserError(_(
                'Generate stock requirements before creating a dispatch.'
            ))

        dispatch = self.env['solar.equipment.dispatch'].create({
            'project_id': self.id,
        })

        # Populate dispatch lines from requirements
        for req in self.stock_requirement_ids.filtered(
            lambda r: r.status not in ('dispatched',)
        ):
            self.env['solar.equipment.dispatch.line'].create({
                'dispatch_id': dispatch.id,
                'product_id': req.product_id.id,
                'component_type': req.component_type,
                'quantity': req.required_qty,
                'is_serialized': req.is_serialized,
                'stock_requirement_id': req.id,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'solar.equipment.dispatch',
            'res_id': dispatch.id,
            'view_mode': 'form',
            'target': 'current',
        }
