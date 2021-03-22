# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero

class stockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    before_price =  fields.Float(string='Sales Price Before', compute='_difference_price')
    lst_price =  fields.Float(string='Sales Price Now', compute='_difference_price')
    difference_price =  fields.Float(string='Difference Price' , compute='_difference_price')

    def _difference_price(self):
        move = self.env['stock.inventory.line'].search([('inventory_id','=',self.move_id.inventory_id.id),('product_id','=',self.product_id.id)])
        self.before_price = move.before_price
        self.lst_price = move.lst_price
        self.difference_price = self.lst_price - self.before_price

class stockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    before_price =  fields.Float(string='Sales Price Before', related='product_id.list_price')
    lst_price =  fields.Float(string='Sales Price Now')
    difference_price =  fields.Float(string='Difference Price' , compute='_difference_price')

    def _difference_price(self):
        self.difference_price = self.lst_price - self.before_price

class stockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_validate(self):
        if not self.exists():
            return
        self.ensure_one()
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_("Only a stock manager can validate an inventory adjustment."))
        if self.state != 'confirm':
            raise UserError(_(
                "You can't validate the inventory '%s', maybe this inventory " +
                "has been already validated or isn't ready.") % (self.name))

        for l in self.line_ids:
            l.product_id.write({'list_price': l.lst_price})


        inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot', 'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
        lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1, precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
        if inventory_lines and not lines:
            wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in inventory_lines.mapped('product_id')]
            wiz = self.env['stock.track.confirmation'].create({'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'res_id': wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        return True