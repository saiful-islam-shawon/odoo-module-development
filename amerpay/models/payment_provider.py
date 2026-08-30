from odoo import _, fields, models
from odoo.exceptions import UserError


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('amarpay', 'Aamarpay')],
        ondelete={'amarpay': 'set default'}
    )
    amarpay_store_id = fields.Char(
        string="Store ID",
        required_if_provider='amarpay',
        groups='base.group_system'
    )
    amarpay_signature_key = fields.Char(
        string="Signature Key",
        required_if_provider='amarpay',
        groups='base.group_system'
    )
    amarpay_sandbox = fields.Boolean(
        string="Use Sandbox",
        default=True
    )

    def _amarpay_get_api_url(self):
        self.ensure_one()
        if self.state == 'test' or self.amarpay_sandbox:
            return 'https://sandbox.aamarpay.com/jsonpost.php'
        return 'https://secure.aamarpay.com/jsonpost.php'

    def _amarpay_get_verification_url(self):
        self.ensure_one()
        if self.state == 'test' or self.amarpay_sandbox:
            return 'https://sandbox.aamarpay.com/api/v1/trxcheck/request.php'
        return 'https://secure.aamarpay.com/api/v1/trxcheck/request.php'

    def _amarpay_ensure_journal(self):
        self.ensure_one()

        if self.code != 'amarpay':
            return self.env['account.journal']

        bdt = self.env['res.currency'].with_context(active_test=False).search([
            ('name', '=', 'BDT'),
        ], limit=1)
        if not bdt:
            raise UserError(_("BDT currency was not found in Odoo."))
        if not bdt.active:
            raise UserError(_("Please activate the BDT currency before using Aamarpay."))

        self._setup_payment_method('amarpay')

        journal = self.journal_id
        if not (journal and journal.type == 'bank' and journal.name == 'AamarPay'):
            journal = self.env['account.journal'].search([
                ('company_id', '=', self.company_id.id),
                ('type', '=', 'bank'),
                ('name', '=', 'AamarPay'),
            ], limit=1)

        if not journal:
            journal = self.env['account.journal'].create({
                'name': 'AamarPay',
                'type': 'bank',
                'company_id': self.company_id.id,
                'currency_id': bdt.id,
            })
        elif journal.currency_id != bdt:
            journal.currency_id = bdt

        self.journal_id = journal
        self._ensure_payment_method_line()
        return journal

    def _get_redirect_form_view(self, is_validation=False):
        self.ensure_one()
        if self.code == 'amarpay':
            return self.env.ref('amerpay.redirect_form', raise_if_not_found=False)
        return super()._get_redirect_form_view(is_validation=is_validation)
