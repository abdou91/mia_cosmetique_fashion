# -*- coding: utf-8 -*-
from odoo import http

# class MyaBoutique(http.Controller):
#     @http.route('/mya_boutique/mya_boutique/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mya_boutique/mya_boutique/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mya_boutique.listing', {
#             'root': '/mya_boutique/mya_boutique',
#             'objects': http.request.env['mya_boutique.mya_boutique'].search([]),
#         })

#     @http.route('/mya_boutique/mya_boutique/objects/<model("mya_boutique.mya_boutique"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mya_boutique.object', {
#             'object': obj
#         })