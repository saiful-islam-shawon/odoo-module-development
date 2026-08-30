import logging
import pprint

from markupsafe import Markup

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AamarpayController(http.Controller):
    _return_url = '/payment/amarpay/return'

    @http.route(
        '/payment/amarpay/pay-now/redirect/<int:tx_id>',
        type='http',
        auth='user',
        methods=['GET'],
    )
    def amarpay_pay_now_redirect(self, tx_id, **kwargs):
        tx = request.env['payment.transaction'].sudo().browse(tx_id).exists()
        if not tx or tx.provider_code != 'amarpay' or not tx.amarpay_is_pay_now:
            return request.not_found()

        if tx.company_id not in request.env.companies:
            return request.not_found()

        processing_values = tx._get_processing_values()
        redirect_form_html = processing_values.get('redirect_form_html')
        if not redirect_form_html:
            return request.render('amerpay.amarpay_pay_now_error', {
                'message': tx.state_message or 'Unable to initiate Aamarpay payment.',
            })

        return request.render('amerpay.amarpay_pay_now_redirect', {
            'redirect_form_html': Markup(redirect_form_html),
        })

    @http.route(
        _return_url,
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False,
        save_session=False,
    )
    def aamarpay_return_from_checkout(self, **post):
        _logger.info("Aamarpay Return Data: \n%s", pprint.pformat(post))

        tx = request.env['payment.transaction'].sudo()._process('amarpay', post)

        if tx and tx.state in ('done', 'cancel') and not tx.is_post_processed:
            tx._post_process()

        if tx and tx.amarpay_is_pay_now:
            partner = tx.amarpay_source_partner_id
            redirect_url = f'/odoo/contacts/{partner.id}' if partner else '/web'
            return request.render('amerpay.amarpay_pay_now_status', {
                'is_success': tx.state == 'done',
                'message': tx.state_message or (
                    'Your payment has been processed successfully.' if tx.state == 'done'
                    else 'Your payment could not be completed.'
                ),
                'redirect_url': redirect_url,
            })

        return request.redirect('/payment/status', 303)
