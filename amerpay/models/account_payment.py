from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    amarpay_payer_name = fields.Char(string='Aamarpay Payer Name', copy=False)
    amarpay_payer_phone = fields.Char(string='Aamarpay Payer Phone', copy=False)
    amarpay_payer_email = fields.Char(string='Aamarpay Payer Email', copy=False)
    amarpay_payer_address = fields.Text(string='Aamarpay Payer Address', copy=False)
    amarpay_transaction_reference = fields.Char(
        string='Aamarpay Transaction Reference',
        copy=False,
        index=True,
    )
