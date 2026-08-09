from odoo import api, models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        rendering_values = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'bkash':
            return rendering_values

        base_url = self.provider_id.get_base_url()
        callback_url = f"{base_url}/bkash/payment/return"

        payload = {
            'mode': '0011',
            'payerReference': self.partner_id.phone or self.reference,
            'callbackURL': callback_url,
            'amount': str(self.amount),
            'currency': self.currency_id.name,
            'intent': 'sale',
            'merchantInvoiceNumber': self.reference,
        }
        response = self.provider_id._send_api_request(
            'POST', 'checkout/payment/create', json=payload, reference=self.reference,
        )

        payment_id = response.get('paymentID')
        redirect_url = response.get('bkashURL')
        if not payment_id or not redirect_url:
            self._set_error("bKash থেকে সঠিক response পাওয়া যায়নি।")
            return {}

        self.provider_reference = payment_id
        return {'api_url': redirect_url}

    def _bkash_execute_payment(self):
        self.ensure_one()
        return self.provider_id._send_api_request(
            'POST', 'checkout/payment/execute',
            json={'paymentID': self.provider_reference}, reference=self.reference,
        )

    def _bkash_query_payment(self):
        self.ensure_one()
        return self.provider_id._send_api_request(
            'POST', 'checkout/payment/status',
            json={'paymentID': self.provider_reference}, reference=self.reference,
        )

    # === core _process() flow-এর hook গুলো === #

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        """ bKash callback এ শুধু paymentID আসে, আমাদের reference না — তাই provider_reference
        দিয়ে transaction খুঁজে তার আসল reference ফেরত দিচ্ছি। """
        if provider_code != 'bkash':
            return super()._extract_reference(provider_code, payment_data)
        payment_id = payment_data.get('paymentID')
        tx = self.sudo().search(
            [('provider_reference', '=', payment_id), ('provider_code', '=', 'bkash')], limit=1
        )
        return tx.reference

    def _extract_amount_data(self, payment_data):
        if self.provider_code != 'bkash':
            return super()._extract_amount_data(payment_data)
        return None  # callback URL params এ amount থাকে না; _apply_updates এ manually check করছি

    def _apply_updates(self, payment_data):
        if self.provider_code != 'bkash':
            return super()._apply_updates(payment_data)

        self.provider_reference = payment_data.get('paymentID')

        # Idempotency: আগেই done/error হয়ে গেলে আবার process করার দরকার নাই
        if self.state in ('done', 'error', 'cancel'):
            return

        self._bkash_execute_payment()
        query_data = self._bkash_query_payment()
        status = query_data.get('transactionStatus')
        paid_amount = query_data.get('amount')

        if status != 'Completed':
            self._set_error("bKash payment completed হয়নি।")
            return

        if paid_amount and float(paid_amount) != self.amount:
            self._set_error("bKash থেকে পাওয়া amount transaction ar amount ar sathe mile nai.")
            return

        self._set_done()