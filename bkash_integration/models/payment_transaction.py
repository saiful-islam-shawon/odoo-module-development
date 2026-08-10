import logging
import requests
from werkzeug import urls
import json

from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # bKash API থেকে প্রাপ্ত পেমেন্ট ট্র্যাকিং আইডি
    bkash_payment_id = fields.Char(string="bKash Payment ID", readonly=True)

    def _get_specific_processing_values(self, processing_values):
        """Odoo-র স্ট্যান্ডার্ড মেথড: পেমেন্ট প্রসেস করার সময় এই মেথড কল হয়"""
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'bkash':
            return res

        # ১. bKash API Grant Token সংগ্রহ করা
        id_token = self.provider_id._bkash_get_grant_token()

        # ২. Create Payment API Call করে bKash Checkout URL জেনারেট করা
        redirect_url = self._bkash_create_payment(id_token)

        # ৩. কাস্টমারকে bKash URL-এ রিডাইরেক্ট করার জন্য রিটার্ন করা
        return {
            'redirect_url': redirect_url,
        }

    def _bkash_create_payment(self, id_token):
        """bKash Create Payment API Request"""
        self.ensure_one()

        base_url = self.provider_id._get_bkash_api_url()
        endpoint = f"{base_url}/tokenized/checkout/create"

        # ওডু থেকে ওয়েবসাইট বেস ইউআরএল (Return URL) তৈরি করা
        odoo_base_url = self.get_base_url()
        callback_url = urls.url_join(odoo_base_url, '/payment/bkash/callback')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': id_token,
            'x-app-key': self.provider_id.bkash_app_key,
        }

        payload = {
            'mode': '0011',  # 0011 = Checkout with Tokenized API
            'payerReference': self.partner_phone or '01700000000',
            'callbackURL': callback_url,
            'amount': str(round(self.amount, 2)),
            'currency': 'BDT',
            'intent': 'sale',
            'merchantInvoiceNumber': self.reference,  # Odoo Transaction Reference
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            # strict=False ব্যবহার করে সেফলি JSON পার্স করা
            response_data = json.loads(response.text, strict=False)

            if response.status_code == 200 and response_data.get('statusCode') == '0000':
                # bKash Payment ID ট্রানজেকশনে সেভ করে রাখা
                self.bkash_payment_id = response_data.get('paymentID')
                _logger.info("bKash Payment Created successfully. PaymentID: %s", self.bkash_payment_id)
                
                # bKash Redirect URL রিটার্ন করা
                return response_data.get('bkashURL')
            else:
                error_msg = response_data.get('statusMessage', 'Failed to create bKash payment')
                _logger.error("bKash Create Payment Error: %s", error_msg)
                raise UserError(_("bKash Payment Initiation Failed: %s", error_msg))

        except requests.exceptions.RequestException as e:
            _logger.error("bKash Connection Error during create payment: %s", str(e))
            raise UserError(_("Could not connect to bKash Payment Server: %s", str(e)))


    
    def _bkash_execute_payment(self):
        """bKash Execute Payment API Call এবং Response ভ্যালিডেশন"""
        self.ensure_one()

        # ১. Fresh Grant Token নেওয়া
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
            # strict=False ব্যবহার করে সেফলি JSON পার্স করা
            response_data = json.loads(response.text, strict=False)

            # status_code 200 এবং bKash response status '0000' হলে পেমেন্ট সফল
            if response.status_code == 200 and response_data.get('statusCode') == '0000':
                _logger.info("bKash Payment Executed Successfully for Ref: %s", self.reference)
                
                # bKash Transaction ID (trxID) সেভ করা এবং Odoo Transaction 'done' করা
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
        """bKash Response থেকে Odoo Transaction State আপডেট করা"""
        self.ensure_one()
        if self.provider_code != 'bkash':
            return super()._process_feedback_data(data)

        # bKash এর প্রদানকৃত আসল Transaction ID (trxID)
        trx_id = data.get('trxID')
        
        # ওডু ট্রানজেকশনে bKash trxID এবং স্টেটাস সেট করা
        self.provider_reference = trx_id
        self._set_done()