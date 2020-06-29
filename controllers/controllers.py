# -*- coding: utf-8 -*-
from odoo import http

# class AlhamraAkademik(http.Controller):
#     @http.route('/alhamra_akademik/alhamra_akademik/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alhamra_akademik/alhamra_akademik/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alhamra_akademik.listing', {
#             'root': '/alhamra_akademik/alhamra_akademik',
#             'objects': http.request.env['alhamra_akademik.alhamra_akademik'].search([]),
#         })

#     @http.route('/alhamra_akademik/alhamra_akademik/objects/<model("alhamra_akademik.alhamra_akademik"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alhamra_akademik.object', {
#             'object': obj
#         })