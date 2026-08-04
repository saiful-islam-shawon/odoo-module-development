from odoo import models, api, fields
from odoo.exceptions import UserError


class SaleOrderPiExtension(models.Model):
    _inherit = "sale.order"

    new_date = fields.Date(string="date")
    
    sale_order_popup_widget_ids = fields.One2many("sale.order.popup.widget", "sale_order_id")
    
    approval_line_ids = fields.One2many(
        "sale.order.approval.line",
        "sale_order_id",
    )
    
    
    def action_request_pi_extension(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Request PI Extension",
            "res_model": "sale.order.popup.widget",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sale_order_id": self.id,
                "default_validity_date": self.validity_date,
            },
        }
        

        
    def _create_group_activity(self, group_xmlid, summary):
        self.ensure_one()

        group = self.env.ref(group_xmlid)
        todo_type = self.env.ref("mail.mail_activity_data_todo")

        for user in group.user_ids:
            self.activity_schedule(
                activity_type_id=todo_type.id,
                user_id=user.id,
                summary=summary,
            )
        
    
    
    def _remove_group_activity(self, group_xmlid):
        self.ensure_one()

        group = self.env.ref(group_xmlid)

        activities = self.env["mail.activity"].search([
            ("res_model", "=", "sale.order"),
            ("res_id", "=", self.id),
            ("user_id", "in", group.user_ids.ids),
        ])

        activities.unlink()
        
        
    