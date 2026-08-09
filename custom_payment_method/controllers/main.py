from odoo import http
from odoo.http import request


class BkashController(http.Controller):

    @http.route('/bkash/payment/return', type='http', auth='public', methods=['GET'], csrf=False)
    def bkash_return(self, **data):
        request.env['payment.transaction'].sudo()._process('bkash', data)
        return request.redirect('/payment/status')