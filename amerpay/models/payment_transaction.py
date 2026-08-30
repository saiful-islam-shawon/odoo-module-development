import json
import logging
import pprint
import time
from urllib.parse import parse_qsl, urlparse

import requests

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    amarpay_tran_id = fields.Char(string="Aamarpay Transaction ID", copy=False)
    amarpay_is_pay_now = fields.Boolean(string='Aamarpay Pay Now', copy=False, readonly=True)
    amarpay_payer_name = fields.Char(string='Aamarpay Payer Name', copy=False, readonly=True)
    amarpay_payer_phone = fields.Char(string='Aamarpay Payer Phone', copy=False, readonly=True)
    amarpay_payer_email = fields.Char(string='Aamarpay Payer Email', copy=False, readonly=True)
    amarpay_payer_address = fields.Text(string='Aamarpay Payer Address', copy=False, readonly=True)
    amarpay_source_partner_id = fields.Many2one('res.partner', string='Aamarpay Source Contact', copy=False)

    @api.model
    def _get_specific_create_values(self, provider_code, values):
        res = super()._get_specific_create_values(provider_code, values)
        if provider_code == 'amarpay' and values.get('amarpay_is_pay_now'):
            res.update({
                'partner_name': values.get('amarpay_payer_name') or 'Customer',
                'partner_email': values.get('amarpay_payer_email') or 'customer@example.com',
                'partner_phone': values.get('amarpay_payer_phone') or '01700000000',
                'partner_address': values.get('amarpay_payer_address') or '',
            })
        return res

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code not in ('amarpay', 'amerpay'):
            return res

        if self.currency_id.name != 'BDT':
            raise ValidationError(
                _("Aamarpay only supports BDT currency. Current currency: %s", self.currency_id.name)
            )

        base_url = self.provider_id.get_base_url().rstrip('/')
        return_url = f"{base_url}/payment/amarpay/return"

        tran_id = f"{self.reference}-{int(time.time())}"
        self.amarpay_tran_id = tran_id

        payload = {
            "store_id": self.provider_id.amarpay_store_id,
            "tran_id": tran_id,
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
            "cus_add1": self.partner_address or "",
            "type": "json"
        }

        api_url = self.provider_id._amarpay_get_api_url()
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(api_url, data=json.dumps(payload), headers=headers, timeout=20)
            response.raise_for_status()
            res_data = response.json()
            _logger.info("Aamarpay initiation raw response: %s", res_data)

            if res_data.get('result') == 'true' and res_data.get('payment_url'):
                payment_url = res_data.get('payment_url')
                if not payment_url.startswith('http'):
                    base_gateway = (
                        "https://sandbox.aamarpay.com/"
                        if self.provider_id.state == 'test' or self.provider_id.amarpay_sandbox
                        else "https://secure.aamarpay.com/"
                    )
                    payment_url = f"{base_gateway}{payment_url.lstrip('/')}"

                parsed_url = urlparse(payment_url)
                action_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                query_params = dict(parse_qsl(parsed_url.query))

                return {
                    'api_url': action_url,
                    'amarpay_params': query_params,
                }

            reason = res_data.get('reason') or 'Payment initiation failed'
            self._set_error(_("Aamarpay Error: %s", reason))
            raise ValidationError(_("Aamarpay Error: %s", reason))
        except ValidationError:
            raise
        except Exception as e:
            _logger.exception("Aamarpay API Connection error: %s", str(e))
            self._set_error(_("Could not reach Aamarpay: %s", str(e)))
            raise ValidationError(_("Could not reach Aamarpay: %s", str(e)))

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        if provider_code != 'amarpay':
            return super()._extract_reference(provider_code, payment_data)
        mer_txnid = payment_data.get('mer_txnid') or payment_data.get('tran_id')
        tx = self.sudo().search([
            ('provider_code', '=', 'amarpay'),
            ('amarpay_tran_id', '=', mer_txnid),
        ], limit=1)
        return tx.reference if tx else mer_txnid

    def _extract_amount_data(self, payment_data):
        if self.provider_code != 'amarpay':
            return super()._extract_amount_data(payment_data)
        return None

    def _apply_updates(self, payment_data):
        if self.provider_code != 'amarpay':
            return super()._apply_updates(payment_data)

        pg_txnid = payment_data.get('pg_txnid')
        if not pg_txnid:
            self._set_error(_("Aamarpay did not return pg_txnid, so the transaction could not be verified."))
            return

        verify_url = self.provider_id._amarpay_get_verification_url()
        params = {
            'request_id': self.amarpay_tran_id or self.reference,
            'store_id': self.provider_id.amarpay_store_id,
            'signature_key': self.provider_id.amarpay_signature_key,
            'type': 'json'
        }

        try:
            response = requests.get(verify_url, params=params, timeout=20)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            _logger.exception("Aamarpay verification failed: %s", str(e))
            raise ValidationError(_("Could not verify transaction with Aamarpay."))

        verified_status = result.get('pay_status')
        _logger.info(
            "Aamarpay verification result for %s: %s",
            self.reference,
            pprint.pformat(result),
        )

        try:
            verified_amount = float(result.get('amount', 0.0))
        except (TypeError, ValueError):
            verified_amount = 0.0

        amount_matches = float_compare(
            verified_amount,
            self.amount,
            precision_rounding=self.currency_id.rounding,
        ) == 0

        if verified_status == 'Successful' and amount_matches:
            self.provider_reference = result.get('pg_txnid') or pg_txnid
            self._set_done()
        elif verified_status in ('Cancel', 'Canceled', 'Cancelled'):
            self._set_canceled(_("Payment was canceled by the customer."))
        else:
            self._set_error(
                _("Aamarpay verification failed or amount mismatch. Status: %s", verified_status)
            )

    def _create_payment(self, **extra_create_values):
        self.ensure_one()
        if self.provider_code != 'amarpay' or not self.amarpay_is_pay_now:
            return super()._create_payment(**extra_create_values)

        journal = self.provider_id._amarpay_ensure_journal()
        payment_method_line = journal.inbound_payment_method_line_ids.filtered(
            lambda line: line.payment_provider_id == self.provider_id
        )[:1]

        if not payment_method_line:
            self.provider_id._ensure_payment_method_line()
            payment_method_line = journal.inbound_payment_method_line_ids.filtered(
                lambda line: line.payment_provider_id == self.provider_id
            )[:1]

        if not payment_method_line:
            raise ValidationError(_("Aamarpay payment method line could not be created on the AamarPay journal."))

        reference = f'{self.reference} - {self.provider_reference or self.amarpay_tran_id or ""}'
        payment_values = {
            'amount': abs(self.amount),
            'payment_type': 'inbound',
            'currency_id': self.currency_id.id,
            'partner_id': False,
            'partner_type': 'customer',
            'journal_id': journal.id,
            'company_id': self.provider_id.company_id.id,
            'payment_method_line_id': payment_method_line.id,
            'payment_transaction_id': self.id,
            'memo': reference,
            'amarpay_payer_name': self.amarpay_payer_name,
            'amarpay_payer_phone': self.amarpay_payer_phone,
            'amarpay_payer_email': self.amarpay_payer_email,
            'amarpay_payer_address': self.amarpay_payer_address,
            'amarpay_transaction_reference': self.provider_reference or self.amarpay_tran_id,
            **extra_create_values,
        }

        payment = self.env['account.payment'].create(payment_values)
        payment.action_post()
        self.payment_id = payment
        return payment
