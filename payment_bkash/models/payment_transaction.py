# -*- coding: utf-8 -*-
import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# Map of bKash transactionStatus values to Odoo's internal payment states.
BKASH_STATUS_MAPPING = {
    'Completed': 'done',
    'Initiated': 'pending',
    'Authorized': 'pending',
    'Cancelled': 'cancel',
    'Failed': 'error',
}


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    bkash_payment_id = fields.Char(string="bKash Payment ID", copy=False)

    # === BUSINESS METHODS === #

    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to create the bKash payment and return the
        values needed to redirect the customer to the bKash-hosted checkout page. """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'bkash':
            return res

        base_url = self.provider_id.get_base_url()
        callback_url = f'{base_url}/payment/bkash/callback'

        create_response = self.provider_id._bkash_create_payment(
            amount=processing_values['amount'],
            currency=self.currency_id.name,
            reference=self.reference,
            callback_url=callback_url,
            payer_reference=self.partner_id.name,
        )

        payment_id = create_response.get('paymentID')
        bkash_url = create_response.get('bkashURL')
        if not payment_id or not bkash_url:
            raise ValidationError(_(
                "bKash: unexpected response received from the payment creation request."
            ))

        self.bkash_payment_id = payment_id
        # `api_url` is picked up by the generic redirect_form template (see views)
        # which simply does a browser redirect to it.
        return {'api_url': bkash_url}

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on bKash data. """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'bkash' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        payment_id = notification_data.get('paymentID')
        tx = self.search([
            ('provider_code', '=', 'bkash'),
            '|', ('reference', '=', reference), ('bkash_payment_id', '=', payment_id),
        ])
        if not tx:
            raise ValidationError(
                "bKash: " + _(
                    "No transaction found matching reference %s.", reference or payment_id
                )
            )
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on bKash data. """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'bkash':
            return

        payment_id = notification_data.get('paymentID') or self.bkash_payment_id
        status = notification_data.get('status')  # 'success' | 'failure' | 'cancel' (query param from bKash redirect)

        if status == 'cancel':
            self._set_canceled()
            return
        if status == 'failure':
            self._set_error(_("bKash: the customer's payment was declined."))
            return
            

        # status == 'success' (or unknown): execute the payment, then confirm via query.
        execute_response = self.provider_id._bkash_execute_payment(payment_id)
        tx_status = execute_response.get('transactionStatus')

        if tx_status != 'Completed':
            # Double-check with a query call before deciding it really failed —
            # execute can be called only once, a retry/duplicate callback must query instead.
            query_response = self.provider_id._bkash_query_payment(payment_id)
            tx_status = query_response.get('transactionStatus', tx_status)

        state = BKASH_STATUS_MAPPING.get(tx_status)
        if state == 'done':
            self.provider_reference = execute_response.get('trxID') or self.provider_reference
            self._set_done()
        elif state == 'pending':
            self._set_pending()
        elif state == 'cancel':
            self._set_canceled()
        else:
            self._set_error(_(
                "bKash: payment could not be verified (status: %s).", tx_status or 'unknown'
            ))



    # i can use this method for more secure. finally check product amount and sending amount same
    # def _process_notification_data(self, notification_data):
    #     """Override of `payment` to process the transaction based on bKash data."""
    #     super()._process_notification_data(notification_data)

    #     if self.provider_code != 'bkash':
    #         return

    #     payment_id = notification_data.get('paymentID') or self.bkash_payment_id
    #     status = notification_data.get('status')

    #     if status == 'cancel':
    #         self._set_canceled()
    #         return

    #     if status == 'failure':
    #         self._set_error(_("bKash: the customer's payment was declined."))
    #         return

    #     # Execute payment only once.
    #     execute_response = self.provider_id._bkash_execute_payment(payment_id)

    #     tx_status = execute_response.get('transactionStatus')
    #     bkash_amount = execute_response.get('amount')
    #     bkash_currency = execute_response.get('currency')

    #     # Verify amount.
    #     if tx_status == 'Completed':
    #         if float(bkash_amount or 0) != float(self.amount):
    #             self._set_error(_(
    #                 "bKash: payment amount mismatch. Expected %s, received %s.",
    #                 self.amount,
    #                 bkash_amount,
    #             ))
    #             return

    #         # Verify currency.
    #         if bkash_currency != self.currency_id.name:
    #             self._set_error(_(
    #                 "bKash: payment currency mismatch. Expected %s, received %s.",
    #                 self.currency_id.name,
    #                 bkash_currency,
    #             ))
    #             return

    #     if tx_status != 'Completed':
    #         # Double-check with query call.
    #         query_response = self.provider_id._bkash_query_payment(payment_id)

    #         tx_status = query_response.get(
    #             'transactionStatus',
    #             tx_status
    #         )

    #         # If query gives the final payment details, use them.
    #         if query_response.get('amount'):
    #             bkash_amount = query_response.get('amount')

    #         if query_response.get('currency'):
    #             bkash_currency = query_response.get('currency')

    #     state = BKASH_STATUS_MAPPING.get(tx_status)

    #     if state == 'done':
    #         # Verify amount/currency again using the final response.
    #         if float(bkash_amount or 0) != float(self.amount):
    #             self._set_error(_(
    #                 "bKash: payment amount mismatch. Expected %s, received %s.",
    #                 self.amount,
    #                 bkash_amount,
    #             ))
    #             return

    #         if bkash_currency != self.currency_id.name:
    #             self._set_error(_(
    #                 "bKash: payment currency mismatch. Expected %s, received %s.",
    #                 self.currency_id.name,
    #                 bkash_currency,
    #             ))
    #             return

    #         self.provider_reference = (
    #             execute_response.get('trxID')
    #             or self.provider_reference
    #         )
    #         self._set_done()

    #     elif state == 'pending':
    #         self._set_pending()

    #     elif state == 'cancel':
    #         self._set_canceled()

    #     else:
    #         self._set_error(_(
    #             "bKash: payment could not be verified (status: %s).",
    #             tx_status or 'unknown'
    #         ))
