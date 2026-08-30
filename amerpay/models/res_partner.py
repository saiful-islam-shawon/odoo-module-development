from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_amarpay_pay_now(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pay Now',
            'res_model': 'amarpay.pay.now.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_partner_id': self.id,
            },
        }
