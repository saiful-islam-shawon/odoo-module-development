# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

import requests

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# bKash Tokenized Checkout (URL Based) API base URLs
BKASH_URLS = {
    'test': 'https://tokenized.sandbox.bka.sh/v1.2.0-beta',
    'enabled': 'https://tokenized.pay.bka.sh/v1.2.0-beta',
}

TIMEOUT = 30  # bKash requires a 30s timeout on all API calls


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('bkash', "bKash")],
        ondelete={'bkash': 'set default'},
    )

    # Credentials shared by bKash during PGW onboarding.
    bkash_app_key = fields.Char(
        string="App Key",
        help="The App Key provided by bKash during merchant onboarding.",
        required_if_provider='bkash',
    )
    bkash_app_secret = fields.Char(
        string="App Secret",
        help="The App Secret provided by bKash during merchant onboarding.",
        required_if_provider='bkash',
        groups='base.group_system',
    )
    bkash_username = fields.Char(
        string="Username",
        help="The API username provided by bKash.",
        required_if_provider='bkash',
    )
    bkash_password = fields.Char(
        string="Password",
        help="The API password provided by bKash.",
        required_if_provider='bkash',
        groups='base.group_system',
    )

    # Cached token so we don't call /token/grant on every request.
    bkash_id_token = fields.Char(string="Cached ID Token", groups='base.group_system', copy=False)
    bkash_refresh_token = fields.Char(string="Cached Refresh Token", groups='base.group_system', copy=False)
    bkash_token_expiry = fields.Datetime(string="ID Token Expiry", groups='base.group_system', copy=False)

    # === BUSINESS METHODS === #

    def _get_supported_currencies(self):
        """ Override of `payment` to restrict bKash to BDT only. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'bkash':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name == 'BDT'
            )
        return supported_currencies

    def _bkash_get_api_url(self):
        self.ensure_one()
        return BKASH_URLS['enabled'] if self.state == 'enabled' else BKASH_URLS['test']

    def _bkash_get_headers(self, with_auth=True):
        self.ensure_one()
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if with_auth:
            headers['Authorization'] = self._bkash_get_id_token()
            headers['X-App-Key'] = self.bkash_app_key
        return headers

    def _bkash_get_id_token(self):
        """ Return a valid id_token, requesting or refreshing one from bKash if needed. """
        self.ensure_one()
        now = fields.Datetime.now()
        if self.bkash_id_token and self.bkash_token_expiry and self.bkash_token_expiry > now:
            return self.bkash_id_token

        if self.bkash_refresh_token:
            data = self._bkash_call(
                'POST', '/tokenized/checkout/token/refresh',
                payload={
                    'app_key': self.bkash_app_key,
                    'app_secret': self.bkash_app_secret,
                    'refresh_token': self.bkash_refresh_token,
                },
                with_auth=False,
                raise_on_status_error=False,
            )
            if data and data.get('id_token'):
                self._bkash_store_tokens(data)
                return self.bkash_id_token

        # Fall back to a fresh grant if there's no refresh token or the refresh failed.
        data = self._bkash_call(
            'POST', '/tokenized/checkout/token/grant',
            payload={
                'app_key': self.bkash_app_key,
                'app_secret': self.bkash_app_secret,
            },
            headers_override={
                'username': self.bkash_username,
                'password': self.bkash_password,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
        )
        self._bkash_store_tokens(data)
        return self.bkash_id_token

    def _bkash_store_tokens(self, data):
        self.ensure_one()
        # id_token is valid 1h, refresh_token 28 days; refresh 5 min early to be safe.
        self.sudo().write({
            'bkash_id_token': data.get('id_token'),
            'bkash_refresh_token': data.get('refresh_token') or self.bkash_refresh_token,
            'bkash_token_expiry': fields.Datetime.now() + timedelta(minutes=55),
        })

    def _bkash_call(self, method, endpoint, payload=None, with_auth=True,
                     headers_override=None, raise_on_status_error=True):
        """ Generic helper to call the bKash API and return the parsed JSON body. """
        self.ensure_one()
        url = self._bkash_get_api_url() + endpoint
        headers = headers_override if headers_override is not None else self._bkash_get_headers(with_auth=with_auth)
        try:
            response = requests.request(
                method, url, json=payload, headers=headers, timeout=TIMEOUT
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            _logger.exception("bKash: could not reach endpoint %s", url)
            if raise_on_status_error:
                raise ValidationError(_(
                    "bKash: could not establish the connection to the API (%s).", error
                ))
            return {}
        data = response.json()
        if data.get('statusCode') and data.get('statusCode') != '0000':
            _logger.warning("bKash error response from %s: %s", url, data)
            if raise_on_status_error:
                raise ValidationError(_(
                    "bKash: %s", data.get('statusMessage') or data.get('errorMessage') or 'Unknown error'
                ))
        return data

    def _bkash_create_payment(self, amount, currency, reference, callback_url, payer_reference=None):
        """ Call /tokenized/checkout/create and return the response (contains bkashURL & paymentID). """
        self.ensure_one()
        payload = {
            'mode': '0011',  # Checkout (URL based) mode
            'payerReference': (payer_reference or reference)[:20],
            'callbackURL': callback_url,
            'amount': str(amount),
            'currency': currency,
            'intent': 'sale',
            'merchantInvoiceNumber': reference[:255],
        }
        return self._bkash_call('POST', '/tokenized/checkout/create', payload=payload)

    def _bkash_execute_payment(self, payment_id):
        self.ensure_one()
        return self._bkash_call('POST', f'/tokenized/checkout/execute/{payment_id}', payload={})

    def _bkash_query_payment(self, payment_id):
        self.ensure_one()
        return self._bkash_call('GET', f'/tokenized/checkout/payment/status/{payment_id}')

    # === CRUD METHODS === #

    @api.model
    def _get_removal_values(self, unlink_values):
        removal_values = super()._get_removal_values(unlink_values)
        removal_values.update({
            'bkash_id_token': False,
            'bkash_refresh_token': False,
        })
        return removal_values

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes for bKash. """
        self.ensure_one()
        if self.code != 'bkash':
            return super()._get_default_payment_method_codes()
        return ['bkash']
