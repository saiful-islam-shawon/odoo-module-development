from odoo import fields, models

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
    
    def _get_redirect_form_view(self, is_validation=False):
        """Odoo যাতে রিডাইরেক্ট ফর্ম টেমপ্লেটটি সরাসরি খুঁজে পায়"""
        self.ensure_one()
        if self.code == 'amarpay':
            # আপনার মডিউলের নাম amarpay হলে amarpay.redirect_form খুঁজবে
            return self.env.ref('amarpay.redirect_form', raise_if_not_found=False) or \
                   self.env.ref('amerpay.redirect_form', raise_if_not_found=False)
        return super()._get_redirect_form_view(is_validation=is_validation)