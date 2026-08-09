from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import ValidationError


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('bkash', "bKash")],
        ondelete={'bkash': 'set default'},
    )

    bkash_app_key = fields.Char(string="App Key", groups='base.group_system')
    bkash_app_secret = fields.Char(string="App Secret", groups='base.group_system')
    bkash_username = fields.Char(string="Username", groups='base.group_system')
    bkash_password = fields.Char(string="Password", groups='base.group_system')

    # === CONFIG === #

    def _get_supported_currencies(self):
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'bkash':
            bdt = self.env.ref('base.BDT')
            return supported_currencies.filtered(lambda c: c == bdt)
        return supported_currencies

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'bkash':
            return default_codes
        return default_codes | {'bkash'}

    def _get_redirect_form_view(self, is_validation=False):
        self.ensure_one()
        if self.code != 'bkash':
            return super()._get_redirect_form_view(is_validation)
        return self.env.ref('payment_bkash.redirect_form')

    def _bkash_get_base_url(self):
        self.ensure_one()
        if self.state == 'enabled':
            return "https://tokenized.pay.bka.sh/v1.2.0-beta/tokenized"
        return "https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized"

    def _bkash_get_access_token(self):
        """ Cache করা valid access token ফেরত দেয়, না থাকলে নতুন করে নেয়। """
        self.ensure_one()
        icp = self.env['ir.config_parameter'].sudo()
        cached_token = icp.get_param(f'payment_bkash.token.{self.id}')
        expiry = icp.get_param(f'payment_bkash.token_expiry.{self.id}')

        if cached_token and expiry and fields.Datetime.now() < fields.Datetime.from_string(expiry):
            return cached_token

        response = self._send_api_request('POST', 'checkout/token/grant', json={
            'app_key': self.bkash_app_key,
            'app_secret': self.bkash_app_secret,
        })

        access_token = response.get('id_token')
        if not access_token:
            raise ValidationError("bKash authentication ব্যর্থ হয়েছে।")

        expires_in = int(response.get('expires_in', 3600))
        expiry_dt = fields.Datetime.now() + timedelta(seconds=expires_in - 60)
        icp.set_param(f'payment_bkash.token.{self.id}', access_token)
        icp.set_param(f'payment_bkash.token_expiry.{self.id}', fields.Datetime.to_string(expiry_dt))
        return access_token

    # === REQUEST HOOKS (core _send_api_request এর জন্য) === #

    def _build_request_url(self, endpoint, **kwargs):
        if self.code != 'bkash':
            return super()._build_request_url(endpoint, **kwargs)
        return f"{self._bkash_get_base_url()}/{endpoint}"

    def _build_request_headers(self, method, endpoint, payload, **kwargs):
        headers = super()._build_request_headers(method, endpoint, payload, **kwargs)
        if self.code != 'bkash':
            return headers

        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if endpoint == 'checkout/token/grant':
            # token নেওয়ার call এ username/password লাগে, bearer token লাগে না
            headers.update({
                'username': self.bkash_username,
                'password': self.bkash_password,
            })
        else:
            headers.update({
                'Authorization': self._bkash_get_access_token(),
                'X-APP-Key': self.bkash_app_key,
            })
        return headers