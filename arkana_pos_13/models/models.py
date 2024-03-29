# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.account.wizard.pos_box import CashBox
from odoo.exceptions import UserError


class POSConfig(models.Model):
    _inherit = 'pos.config'

    image = fields.Binary('image')

    


class PosBox(CashBox):
    _register = False

    def run(self):
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])

        if active_model == 'pos.session':
            bank_statements = [session.cash_register_id for session in self.env[active_model].browse(active_ids) if session.cash_register_id]
            if not bank_statements:
                raise UserError(_("There is no cash register for this PoS Session"))
            return self._run(bank_statements)
        else:
            return super(PosBox, self).run()


class PosBoxOut(PosBox):
    _inherit = 'cash.box.out'

    ps_id = fields.Many2one('pos.session')
    currency_id = fields.Many2one('res.currency', related='ps_id.config_id.currency_id', string="Currency")

    def _calculate_values_for_statement_line(self, record):
        values = super(PosBoxOut, self)._calculate_values_for_statement_line(record)
        # values['ps_id'] = self.env.context.get('active_id', False)
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'pos.session' and active_ids:
            values['ref'] = self.env[active_model].browse(active_ids)[0].name
        return values

class POSSession(models.Model):
    _inherit = 'pos.session'

    @api.depends('statement_ids.line_ids')
    def _compute_statement_line(self):
        for rec in self :
            rec.statement_line_ids = rec.mapped('statement_ids.line_ids')

    cbo_ids = fields.Many2many('cash.box.out', compute='compute_cbo_ids', string="Cashs In/Out")
    cbo_id = fields.One2many('cash.box.out', 'ps_id', string='Cash In/Out')
    statement_line_ids = fields.Many2many('account.bank.statement.line', compute='_compute_statement_line', string="Cashs In/Out", inverse=lambda self: self)

    @api.onchange('cbo_ids')
    def onchange_cbo_ids(self):
        print(self.cash_register_total_entry_encoding)
        print(self.cbo_ids)

    def compute_cbo_ids(self):
        try:
            self.cbo_ids = self.env['cash.box.out'].search([('ps_id','=',self.id)]).ids

            # total_amount = 0
            # for i in self.cbo_ids:
            #     total_amount += i.amount
            # self.cash_register_total_entry_encoding = total_amount
        except:
            pass

    def write(self, vals):
        if 'statement_line_ids' in vals:
            all_statement_line_ids = self.mapped('statement_ids.line_ids.id')
            for data in vals['statement_line_ids']:
                if data[0] == 6 :
                    existing_statement_line_ids = data[2]
                    statement_line_ids = self.env['account.bank.statement.line'].search([
                        ('id','in',all_statement_line_ids),
                        ('id','not in',existing_statement_line_ids),
                    ])
                    statement_line_ids.unlink()
        return super(POSSession, self).write(vals)

    # def _reconcile_account_move_lines(self, data):
    #     # jangan reconcile account move line dari invoice
    #     final_order_account_move_receivable_lines = {}
    #     order_account_move_receivable_lines = data.get('order_account_move_receivable_lines', {})
    #     data['order_account_move_receivable_lines'] = {}
    #     for id, move_lines in order_account_move_receivable_lines.items():
    #         final_move_lines = self.env['account.move.line']
    #         for line in move_lines :
    #             if line.move_id.type != 'out_invoice':
    #                 final_move_lines += line
    #         if final_move_lines :
    #             data['order_account_move_receivable_lines'][id] = final_order_account_move_receivable_lines
    #     return super(POSSession, self)._reconcile_account_move_lines(data)

class POSOrder(models.Model):
    _inherit = 'pos.order'


    def pos_order(self, session_id):
        pos = self.env['pos.order'].search([('session_id','=',session_id)])
        data = [{}]
        no = 0
        name_product = []
        total_penjualan = 0
        qty_penjualan = 0
        partner_penjualan = []
        for x in pos:
            data.append(\
                        {'pos_id' : x.id, 'product': x.lines.mapped('product_id').mapped('name'),\
                        'qty' : x.lines.mapped('qty'), \
                        'price' : x.lines.mapped('price_unit'), \
                        'subtotal' : x.lines.mapped('price_subtotal_incl'), \
                        'total': x.amount_total, 'partner_id': x.partner_id.name})
            partner_penjualan.append(str(x.partner_id.name))
            name_product.append(x.lines.mapped('product_id').mapped('name'))
            total_penjualan += int(x.amount_total)
            qty_penjualan += sum(x.lines.mapped('qty'))
        data[0]['total_penjualan'] = int(total_penjualan)
        data[0]['qty_penjualan'] = int(qty_penjualan)
        data[0]['partner_penjualan'] = partner_penjualan
        data[0]['name_product'] = name_product
        
        return data

    @api.model
    def _process_order(self, order, draft, existing_order):
        if 'to_invoice' in order and 'data' in order :
            order['data']['to_invoice'] = order['to_invoice']
        res = super(POSOrder, self)._process_order(order, draft, existing_order)
        return res
