import logging
import uuid
import requests

from odoo import models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'bkash':
            return res

        base_url = self.provider_id.get_base_url()
        callback_url = f"{base_url}/payment/bkash/return"

        payload = {
            'mode': '0011',
            'payerReference': self.partner_id.phone or self.reference,
            'callbackURL': callback_url,
            'amount': str(self.amount),
            'currency': self.currency_id.name,
            'intent': 'sale',
            'merchantInvoiceNumber': self.reference,
        }
        headers = self._bkash_get_headers()

        url = f"{self.provider_id._bkash_get_base_url()}/checkout/create"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            _logger.exception("bKash create payment request failed")
            raise ValidationError("bKash payment শুরু করা যাচ্ছে না।")

        data = response.json()
        payment_id = data.get('paymentID')
        redirect_url = data.get('bkashURL')

        if not payment_id or not redirect_url:
            _logger.error("bKash create payment error: %s", data)
            raise ValidationError("bKash থেকে সঠিক response পাওয়া যায়নি।")

        self.provider_reference = payment_id

        return {'api_url': redirect_url}

    def _bkash_get_headers(self):
        access_token = self.provider_id._bkash_get_access_token()
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': access_token,
            'X-APP-Key': self.provider_id.bkash_app_key,
        }

    def _bkash_execute_payment(self, payment_id):
        self.ensure_one()
        headers = self._bkash_get_headers()
        url = f"{self.provider_id._bkash_get_base_url()}/checkout/execute"

        try:
            response = requests.post(
                url, json={'paymentID': payment_id}, headers=headers, timeout=30
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            _logger.exception("bKash execute payment failed")
            raise ValidationError("bKash execute payment ব্যর্থ হয়েছে।")

        return response.json()