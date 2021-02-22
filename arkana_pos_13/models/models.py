# -*- coding: utf-8 -*-

from odoo import models, fields, api


class POSConfig(models.Model):
    _inherit = 'pos.config'

    image = fields.Binary('image')

    