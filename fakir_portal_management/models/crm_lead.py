from odoo import models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_open_fakir_send_mail(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Send Mail",
            "res_model": "fakir.crm.send.mail.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_lead_id": self.id,
            },
        }
