import logging
import requests

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class BkashController(http.Controller):

    @http.route('/payment/bkash/return', type='http', auth='public', methods=['GET'], csrf=False)
    def bkash_return(self, **data):
        _logger.info("bKash return data: %s", data)

        payment_id = data.get('paymentID')
        status = data.get('status')

        tx_sudo = request.env['payment.transaction'].sudo().search(
            [('provider_reference', '=', payment_id), ('provider_code', '=', 'bkash')]
        )
        if not tx_sudo:
            _logger.error("bKash return: no transaction found for paymentID %s", payment_id)
            return request.redirect('/payment/status')

        if status != 'success':
            tx_sudo._set_canceled()
            return request.redirect('/payment/status')

        try:
            execute_data = tx_sudo._bkash_execute_payment(payment_id)
        except ValidationError:
            tx_sudo._set_error("bKash payment execute করা যায়নি।")
            return request.redirect('/payment/status')

        trx_status = execute_data.get('transactionStatus')
        if trx_status == 'Completed':
            tx_sudo._set_done()
        else:
            tx_sudo._set_canceled()

        return request.redirect('/payment/status')