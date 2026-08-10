import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class BkashController(http.Controller):

    @http.route('/payment/bkash/callback', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def bkash_callback(self, **data):
        """bKash Callback URL endpoint"""
        _logger.info("bKash Callback received with data: %s", data)

        payment_id = data.get('paymentID')
        status = data.get('status')

        if not payment_id:
            _logger.error("bKash Callback missing paymentID.")
            return request.redirect('/payment/status')

        # ১. bKash Payment ID দিয়ে ওডু ট্রানজেকশন খুঁজে বের করা
        tx_sudo = request.env['payment.transaction'].sudo().search([
            ('bkash_payment_id', '=', payment_id)
        ], limit=1)

        if not tx_sudo:
            _logger.error("No Odoo transaction found for bKash paymentID: %s", payment_id)
            return request.redirect('/payment/status')

        # ২. কাস্টমার যদি পেমেন্ট কনফার্ম করে (status == 'success')
        if status == 'success':
            # Execute Payment API কল করে পেমেন্ট ক্যাপচার করা
            tx_sudo._bkash_execute_payment()
        else:
            # কাস্টমার যদি ক্যানসেল করে বা ব্যর্থ হয়
            _logger.warning("bKash Payment status was not success: %s", status)
            tx_sudo._set_canceled(state_message=f"bKash Payment Status: {status}")

        # ৩. ওডুর স্ট্যান্ডার্ড পেমেন্ট স্ট্যাটাস পেজে রিডাইরেক্ট করা
        return request.redirect('/payment/status')