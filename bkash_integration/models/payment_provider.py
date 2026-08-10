import logging
import requests
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import json

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('bkash', 'bKash')],
        ondelete={'bkash': 'set default'}
    )

    # bKash API Credentials
    bkash_app_key = fields.Char(
        string="bKash App Key",
        groups='base.group_system'
    )
    bkash_app_secret = fields.Char(
        string="bKash App Secret",
        groups='base.group_system'
    )
    bkash_username = fields.Char(
        string="bKash Username",
        groups='base.group_system'
    )
    bkash_password = fields.Char(
        string="bKash Password",
        groups='base.group_system'
    )


    def _get_bkash_api_url(self):
        """bKash Sandbox vs Production URL Return করবে"""
        self.ensure_one()
        if self.state == 'enabled':
            return 'https://tokenized.pay.bka.sh/v1.2.0-beta'
        else:
            return 'https://tokenized.sandbox.bka.sh/v1.2.0-beta'



    def _bkash_get_grant_token(self):
        """bKash API থেকে Grant Token (id_token) সংগ্রহ করার মেথড"""
        self.ensure_one()
        
        base_url = self._get_bkash_api_url()
        endpoint = f"{base_url}/tokenized/checkout/token/grant"

        headers = {
            'Content-Type': 'application/json',
            'username': self.bkash_username or '',
            'password': self.bkash_password or '',
        }

        payload = {
            'app_key': self.bkash_app_key or '',
            'app_secret': self.bkash_app_secret or '',
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response_data = json.loads(response.text, strict=False)

            # bKash সফলভাবে টোকেন দিলে statusCode '0000' পাঠায়
            if response.status_code == 200 and response_data.get('statusCode') == '0000':
                _logger.info("bKash Grant Token retrieved successfully.")
                return response_data.get('id_token')
            else:
                error_msg = response_data.get('statusMessage', 'Unknown bKash API Error')
                _logger.error("bKash Grant Token Error: %s", error_msg)
                raise UserError(_("bKash Token Generation Failed: %s", error_msg))

        except (json.JSONDecodeError, ValueError):
            _logger.error("bKash API Raw Response Parsing Error: %s", response.text)
            raise UserError(_("bKash Response Parsing Error: %s", response.text))
        except requests.exceptions.RequestException as e:
            _logger.error("bKash Connection Error: %s", str(e))
            raise UserError(_("Could not connect to bKash Payment Server: %s", str(e)))