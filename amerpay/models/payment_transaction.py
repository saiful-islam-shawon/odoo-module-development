import json
import logging
import pprint
import requests
from urllib.parse import urlparse, parse_qsl
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code not in ('amarpay', 'amerpay'):
            return res

        # Aamarpay শুধুমাত্র BDT সাপোর্ট করে
        if self.currency_id.name != 'BDT':
            raise ValidationError(
                _("Aamarpay শুধুমাত্র BDT currency সাপোর্ট করে। বর্তমান currency: %s", self.currency_id.name)
            )

        base_url = self.provider_id.get_base_url().rstrip('/')
        return_url = f"{base_url}/payment/amarpay/return"

        payload = {
            "store_id": self.provider_id.amarpay_store_id,
            "tran_id": self.reference,
            "success_url": return_url,
            "fail_url": return_url,
            "cancel_url": return_url,
            "amount": str(self.amount),
            "currency": self.currency_id.name,
            "signature_key": self.provider_id.amarpay_signature_key,
            "desc": f"Payment for {self.reference}",
            "cus_name": self.partner_name or "Customer",
            "cus_email": self.partner_email or "customer@example.com",
            "cus_phone": self.partner_phone or "01700000000",
            "type": "json"
        }

        api_url = self.provider_id._amarpay_get_api_url()
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(api_url, data=json.dumps(payload), headers=headers, timeout=20)
            res_data = response.json()
            if res_data.get('result') == 'true' and res_data.get('payment_url'):
                payment_url = res_data.get('payment_url')
                # যদি payment_url-এ ফুল ডোমেইন না থাকে তবে যোগ করা
                if not payment_url.startswith('http'):
                    base_gateway = "https://sandbox.aamarpay.com/" if self.provider_id.amarpay_sandbox else "https://secure.aamarpay.com/"
                    payment_url = f"{base_gateway}{payment_url.lstrip('/')}"

                # payment_url-এর ভেতরে session/token সহ query string থাকে
                # (যেমন ?opt=xxx&mer_id=yyy)। কিন্তু method="get" form submit
                # করার সময় browser action attribute-এর query string ফেলে
                # দিয়ে ফর্মের হিডেন ইনপুট দিয়ে নতুন query বানায়। তাই query
                # params আলাদা করে হিডেন ইনপুট হিসেবে পাঠাতে হবে, নাহলে
                # Aamarpay "direct access restricted" দেখাবে।
                parsed_url = urlparse(payment_url)
                action_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                query_params = dict(parse_qsl(parsed_url.query))

                return {
                    'api_url': action_url,
                    'amarpay_params': query_params,
                }
            else:
                raise ValidationError(_("Aamarpay Error: %s", res_data.get('reason', 'Payment initiation failed')))
        except Exception as e:
            _logger.exception("Aamarpay API Connection error: %s", str(e))
            raise ValidationError(_("Could not reach Aamarpay: %s", str(e)))

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        """ Odoo 19-এর payment framework-এ payment_data থেকে reference বের করার জন্য
        এই method override করতে হয় (আগের _get_tx_from_notification_data-এর বদলে)। """
        if provider_code != 'amarpay':
            return super()._extract_reference(provider_code, payment_data)
        return payment_data.get('mer_txnid') or payment_data.get('tran_id')

    def _extract_amount_data(self, payment_data):
        """ Base class-এর default {} return করলে amount validation-এ KeyError হয়,
        তাই None return করে built-in amount check skip করা হচ্ছে — amount/status
        verify আমরা নিজেরাই _apply_updates-এ server-to-server call দিয়ে করি। """
        if self.provider_code != 'amarpay':
            return super()._extract_amount_data(payment_data)
        return None

    def _apply_updates(self, payment_data):
        """ Odoo 19-এ এটাই সঠিক override পয়েন্ট (আগের _process_notification_data-এর
        বদলে)। এখানে super() কল করার দরকার নেই। """
        if self.provider_code != 'amarpay':
            return super()._apply_updates(payment_data)

        pg_txnid = payment_data.get('pg_txnid')
        if not pg_txnid:
            # pg_txnid ছাড়া verify করার উপায় নেই, তাই client-এর দাবি করা
            # status এখানে trust না করে সরাসরি error ধরে নেওয়া হচ্ছে
            self._set_error(_("Aamarpay থেকে pg_txnid পাওয়া যায়নি, transaction verify করা সম্ভব হয়নি."))
            return

        # গুরুত্বপূর্ণ: client/browser থেকে আসা pay_status কখনোই সরাসরি trust
        # করা উচিত না (কেউ চাইলে fake POST পাঠাতে পারে)। তাই এখানে ignore
        # করে শুধু Aamarpay-এর server-to-server verification API থেকে
        # পাওয়া status-ই trust করা হচ্ছে।
        verify_url = self.provider_id._amarpay_get_verification_url()
        params = {
            'request_id': self.reference,
            'store_id': self.provider_id.amarpay_store_id,
            'signature_key': self.provider_id.amarpay_signature_key,
            'type': 'json'
        }

        try:
            response = requests.get(verify_url, params=params, timeout=20)
            result = response.json()
        except Exception as e:
            _logger.exception("Aamarpay verification failed: %s", str(e))
            raise ValidationError(_("Could not verify transaction with Aamarpay."))

        verified_status = result.get('pay_status')
        _logger.info("Aamarpay verification result for %s: %s", self.reference, pprint.pformat(result))

        if verified_status == 'Successful' and float(result.get('amount', 0.0)) == self.amount:
            self._set_done()
        elif verified_status in ('Cancel', 'Canceled', 'Cancelled'):
            self._set_canceled(_("Payment was canceled by the customer."))
        else:
            self._set_error(
                _("Aamarpay verification failed or amount mismatch. Status: %s", verified_status)
            )
