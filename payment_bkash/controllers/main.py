# -*- coding: utf-8 -*-
import logging

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class BkashController(http.Controller):
    _callback_url = '/payment/bkash/callback'

    @http.route(_callback_url, type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def bkash_callback(self, **data):
        """ bKash redirects the customer's browser here after they authorize
        (or cancel/fail) the payment on the bKash-hosted checkout page.

        Query params received: paymentID, status ('success' | 'failure' | 'cancel')
        """
        _logger.info("bKash: callback received with data:\n%s", data)
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('bkash', data)
        tx_sudo._handle_notification_data('bkash', data)
        return request.redirect('/payment/status')
