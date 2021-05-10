from odoo import fields, api, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    def post(self):
        moves = self.env['account.move']
        if not self._context.get('force_post'):
            for rec in self :
                order_id = self.env['pos.order'].search([
                    ('account_move','=',rec.id),
                ])
                if order_id :
                    moves += rec
        return super(AccountMove, self-moves).post()
