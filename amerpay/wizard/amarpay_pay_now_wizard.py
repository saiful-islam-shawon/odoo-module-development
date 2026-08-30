from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


class AamarpayPayNowWizard(models.TransientModel):
    _name = 'amarpay.pay.now.wizard'
    _description = 'Aamarpay Pay Now'

    source_partner_id = fields.Many2one('res.partner', string='Source Contact', readonly=True)
    payer_name = fields.Char(string='Customer Name', required=True)
    payer_phone = fields.Char(string='Phone', required=True)
    payer_email = fields.Char(string='Email', required=True)
    payer_address = fields.Text(string='Address', required=True)
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self._default_bdt_currency(),
    )

    def _default_bdt_currency(self):
        return self.env['res.currency'].search([('name', '=', 'BDT')], limit=1)

    def action_pay_now(self):
        self.ensure_one()

        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero."))
        if not self.currency_id or self.currency_id.name != 'BDT':
            raise ValidationError(_("Aamarpay Pay Now only supports BDT."))

        provider = self.env['payment.provider'].sudo().search([
            ('code', '=', 'amarpay'),
            ('company_id', '=', self.env.company.id),
            ('state', 'in', ('test', 'enabled')),
        ], limit=1)
        if not provider:
            raise UserError(_("No enabled/test Aamarpay payment provider was found for the current company."))

        if not provider.amarpay_store_id or not provider.amarpay_signature_key:
            raise UserError(_("Please configure the Aamarpay Store ID and Signature Key first."))

        provider._amarpay_ensure_journal()

        payment_method = self.env['payment.method'].sudo().search([
            ('code', '=', 'amarpay'),
            ('provider_ids', 'in', provider.id),
            ('active', '=', True),
        ], limit=1)
        if not payment_method:
            payment_method = provider.payment_method_ids.filtered(lambda pm: pm.active)[:1]
        if not payment_method:
            raise UserError(_("No Aamarpay payment method is available on the provider."))

        tx_model = self.env['payment.transaction'].sudo()
        reference = tx_model._compute_reference('amarpay', prefix='AAMARPAY-PAYNOW')

        tx = tx_model.create({
            'provider_id': provider.id,
            'payment_method_id': payment_method.id,
            'reference': reference,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'operation': 'online_redirect',
            'partner_id': provider.company_id.partner_id.id,
            'amarpay_is_pay_now': True,
            'amarpay_payer_name': self.payer_name,
            'amarpay_payer_phone': self.payer_phone,
            'amarpay_payer_email': self.payer_email,
            'amarpay_payer_address': self.payer_address,
            'amarpay_source_partner_id': self.source_partner_id.id,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/payment/amarpay/pay-now/redirect/{tx.id}',
            'target': 'self',
        }
