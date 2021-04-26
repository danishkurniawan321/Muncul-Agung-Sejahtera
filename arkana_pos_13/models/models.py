# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.account.wizard.pos_box import CashBox


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

    # def unlink(self):
    #     res = super(PosBoxOut).unlink()
    #     self.ps_id.cash_register_total_entry_encoding =  self.ps_id.cash_register_total_entry_encoding - self.amount
    #     return res


class PosBoxOut(PosBox):
    _inherit = 'cash.box.out'

    ps_id = fields.Many2one('pos.session')
    currency_id = fields.Many2one('res.currency', related='ps_id.config_id.currency_id', string="Currency")

    def _calculate_values_for_statement_line(self, record):
        values = super(PosBoxOut, self)._calculate_values_for_statement_line(record)
        values['ps_id'] = self.ps_id.id
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'pos.session' and active_ids:
            values['ref'] = self.env[active_model].browse(active_ids)[0].name
        return values

class POSSession(models.Model):
    _inherit = 'pos.session'
    

    cbo_ids = fields.Many2many('cash.box.out', compute='compute_cbo_ids', string="Cashs In/Out")
    cbo_id = fields.One2many('cash.box.out', 'ps_id', string='Cash In/Out')


    @api.onchange('cbo_ids')
    def onchange_cbo_ids(self):
        print(self.cash_register_total_entry_encoding)
        print(self.cbo_ids)



    @api.depends('payment_method_ids', 'order_ids', 'cash_register_balance_start', 'cash_register_id')
    def _compute_cash_balance(self):
        for session in self:
            cash_payment_method = session.payment_method_ids.filtered('is_cash_count')[:1]
            if cash_payment_method:
                total_cash_payment = sum(session.order_ids.mapped('payment_ids').filtered(lambda payment: payment.payment_method_id == cash_payment_method).mapped('amount'))
                # session.cash_register_total_entry_encoding = session.cash_register_id.total_entry_encoding + (
                #     0.0 if session.state == 'closed' else total_cash_payment
                # )
                total_amount = 0 
                for i in self.cbo_ids:
                    total_amount += i.amount
                session.cash_register_total_entry_encoding = total_amount
                # session.cash_register_total_entry_encoding = session.cash_register_id.total_entry_encoding + (total_amount if session.state == 'closed' else total_cash_payment)
                session.cash_register_balance_end = session.cash_register_balance_start + session.cash_register_total_entry_encoding
                session.cash_register_difference = session.cash_register_balance_end_real - session.cash_register_balance_end




    def compute_cbo_ids(self):
        try:
            self.cbo_ids = self.env['cash.box.out'].search([('ps_id','=',self.id)]).ids
            
            # total_amount = 0 
            # for i in self.cbo_ids:
            #     total_amount += i.amount
            # self.cash_register_total_entry_encoding = total_amount
        except:
            pass

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