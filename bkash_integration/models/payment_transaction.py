import logging
import requests
from werkzeug import urls
import json
from urllib.parse import urlparse, parse_qs, urlunparse

from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    bkash_payment_id = fields.Char(string="bKash Payment ID", readonly=True)

    def _get_specific_processing_values(self, processing_values):
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'bkash':
            return res

        id_token = self.provider_id._bkash_get_grant_token()
        redirect_url = self._bkash_create_payment(id_token)

        parsed_url = urlparse(redirect_url)
        clean_action_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        query_params = parse_qs(parsed_url.query)

        inputs_html = ''.join([
            f'<input type="hidden" name="{key}" value="{value[0]}"/>' 
            for key, value in query_params.items()
        ])

        return {
            'redirect_form_html': f'<form id="o_payment_redirect_form" action="{clean_action_url}" method="get">{inputs_html}</form>',
        }

    def _bkash_create_payment(self, id_token):
        self.ensure_one()
        base_url = self.provider_id._get_bkash_api_url()
        endpoint = f"{base_url}/tokenized/checkout/create"

        odoo_base_url = self.get_base_url()
        callback_url = urls.url_join(odoo_base_url, '/payment/bkash/callback')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': id_token,
            'x-app-key': self.provider_id.bkash_app_key,
        }

        payload = {
            'mode': '0011',
            'payerReference': self.partner_phone or '01700000000',
            'callbackURL': callback_url,
            'amount': str(round(self.amount, 2)),
            'currency': 'BDT',
            'intent': 'sale',
            'merchantInvoiceNumber': self.reference,
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response_data = json.loads(response.text, strict=False)

            if response.status_code == 200 and response_data.get('statusCode') == '0000':
                self.bkash_payment_id = response_data.get('paymentID')
                _logger.info("bKash Payment Created successfully. PaymentID: %s", self.bkash_payment_id)
                return response_data.get('bkashURL')
            else:
                error_msg = response_data.get('statusMessage', 'Failed to create bKash payment')
                _logger.error("bKash Create Payment Error: %s", error_msg)
                raise UserError(_("bKash Payment Initiation Failed: %s", error_msg))

        except requests.exceptions.RequestException as e:
            _logger.error("bKash Connection Error during create payment: %s", str(e))
            raise UserError(_("Could not connect to bKash Payment Server: %s", str(e)))

    def _bkash_execute_payment(self):
        self.ensure_one()
        id_token = self.provider_id._bkash_get_grant_token()

        base_url = self.provider_id._get_bkash_api_url()
        endpoint = f"{base_url}/tokenized/checkout/execute"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': id_token,
            'x-app-key': self.provider_id.bkash_app_key,
        }

        payload = {
            'paymentID': self.bkash_payment_id,
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response_data = json.loads(response.text, strict=False)

            if response.status_code == 200 and response_data.get('statusCode') == '0000':
                _logger.info("bKash Payment Executed Successfully for Ref: %s", self.reference)
                self._process_feedback_data(response_data)
                return True
            else:
                error_msg = response_data.get('statusMessage', 'bKash Execution Failed')
                _logger.error("bKash Execute Payment Error: %s", error_msg)
                self._set_canceled(state_message=error_msg)
                return False

        except requests.exceptions.RequestException as e:
            _logger.error("bKash Connection Error during Execute Payment: %s", str(e))
            self._set_error(_("Could not verify bKash payment due to network error."))
            return False

    def _process_feedback_data(self, data):
        self.ensure_one()
        if self.provider_code != 'bkash':
            return super()._process_feedback_data(data)

        trx_id = data.get('trxID')
        self.provider_reference = trx_id
        # _set_done() কল করার সাথে সাথে Odoo স্বয়ংক্রিয়ভাবে _create_payment() কে ট্রিগার করবে
        self._set_done()
        
        

    # akhane theke journal and sell order create korar jonno code kora hoyche
    def _get_payment_values(self):
        # Odoo transaction থেকে প্রাথমিক পেমেন্ট ভ্যালু তৈরি
        res = {
            'amount': self.amount,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'ref': self.reference,
        }
        
        if self.provider_code == 'bkash':
            # প্রোভাইডারে সেট করা জার্নাল বা ডিফল্ট ব্যাংক জার্নাল সিলেক্ট
            journal = self.provider_id.journal_id or self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
            
            if journal:
                # ১. bkash কোডের লাইন খোঁজা
                pm_line = journal.inbound_payment_method_line_ids.filtered(
                    lambda l: l.payment_method_id.code == 'bkash'
                )
                
                # ২. না পেলে যেকোনো প্রথম ইনবাউন্ড লাইন সিলেক্ট
                if not pm_line and journal.inbound_payment_method_line_ids:
                    pm_line = journal.inbound_payment_method_line_ids[0]
                
                if pm_line:
                    res.update({
                        'journal_id': journal.id,
                        'payment_method_line_id': pm_line.id,
                        'payment_method_id': pm_line.payment_method_id.id,
                    })
                
        return res

    def _create_payment(self, **extra_create_values):
        for tx in self:
            if tx.provider_code == 'bkash':
                payment_vals = tx._get_payment_values()
                if 'payment_method_line_id' in payment_vals:
                    extra_create_values.update({
                        'journal_id': payment_vals.get('journal_id'),
                        'payment_method_line_id': payment_vals.get('payment_method_line_id'),
                    })

        return super()._create_payment(**extra_create_values)