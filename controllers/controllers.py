# -*- coding: utf-8 -*-
from odoo import http

# class Remiseglobale(http.Controller):
#     @http.route('/remiseglobale/remiseglobale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/remiseglobale/remiseglobale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('remiseglobale.listing', {
#             'root': '/remiseglobale/remiseglobale',
#             'objects': http.request.env['remiseglobale.remiseglobale'].search([]),
#         })

#     @http.route('/remiseglobale/remiseglobale/objects/<model("remiseglobale.remiseglobale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('remiseglobale.object', {
#             'object': obj
#         })