# -*- coding: utf-8 -*-
# from odoo import http


# class ArkanaPos14(http.Controller):
#     @http.route('/arkana_pos_14/arkana_pos_14/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/arkana_pos_14/arkana_pos_14/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('arkana_pos_14.listing', {
#             'root': '/arkana_pos_14/arkana_pos_14',
#             'objects': http.request.env['arkana_pos_14.arkana_pos_14'].search([]),
#         })

#     @http.route('/arkana_pos_14/arkana_pos_14/objects/<model("arkana_pos_14.arkana_pos_14"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('arkana_pos_14.object', {
#             'object': obj
#         })
