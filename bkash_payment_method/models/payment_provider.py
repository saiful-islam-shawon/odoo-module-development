import logging
import requests
from datetime import timedelta

from odoo import models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("bkash", "bKash")],
        ondelete={"bkash": "set default"},
    )

    bkash_username = fields.Char(
        string="Username",
        required_if_provider="bkash",
    )
    bkash_password = fields.Char(
        string="Password",
        groups="base.group_system",
        required_if_provider="bkash",
    )
    bkash_app_key = fields.Char(
        string="App Key",
        required_if_provider="bkash",
    )
    bkash_app_secret = fields.Char(
        string="App Secret",
        groups="base.group_system",
        required_if_provider="bkash",
    )



    def _get_supported_currencies(self):
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'bkash':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name == 'BDT'
            )
        return supported_currencies

    # return payment method
    def _get_default_payment_method_codes(self):
        """Override of payment to return the default payment method codes."""
        default_codes = super()._get_default_payment_method_codes()
        if self.code != "bkash":
            return default_codes
        return default_codes | {"bkash"}

    
    def _bkash_get_base_url(self):
        self.ensure_one()
        if self.state == 'enabled':
            return "https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized"
        return "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized"

    def _bkash_get_access_token(self):
        """ Valid access token রিটার্ন করে, cache এ না থাকলে নতুন করে নেয়। """
        self.ensure_one()

        icp = self.env['ir.config_parameter'].sudo()
        cached_token = icp.get_param(f'payment_bkash.token.{self.id}')
        expiry = icp.get_param(f'payment_bkash.token_expiry.{self.id}')

        if cached_token and expiry and fields.Datetime.now() < fields.Datetime.from_string(expiry):
            return cached_token

        url = f"{self._bkash_get_base_url()}/checkout/token/grant"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'username': self.bkash_username,
            'password': self.bkash_password,
        }
        payload = {
            'app_key': self.bkash_app_key,
            'app_secret': self.bkash_app_secret,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            _logger.exception("bKash grant token request failed")
            raise ValidationError("bKash সার্ভারের সাথে কানেক্ট করা যাচ্ছে না।")

        data = response.json()
        access_token = data.get('id_token')
        if not access_token:
            _logger.error("bKash grant token error: %s", data)
            raise ValidationError("bKash authentication ব্যর্থ হয়েছে।")

        expires_in = int(data.get('expires_in', 3600))
        expiry_dt = fields.Datetime.now() + timedelta(seconds=expires_in - 60)

        icp.set_param(f'payment_bkash.token.{self.id}', access_token)
        icp.set_param(f'payment_bkash.token_expiry.{self.id}', fields.Datetime.to_string(expiry_dt))

        return access_token


    def _get_redirect_form_view(self, is_validation=False):
        self.ensure_one()
        if self.code != 'bkash':
            return super()._get_redirect_form_view(is_validation)
        return self.env.ref('payment_bkash.redirect_form') 