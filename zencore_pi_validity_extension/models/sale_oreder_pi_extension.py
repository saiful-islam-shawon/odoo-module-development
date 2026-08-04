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
        


    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)

        for order in orders:
            order.approval_line_ids = [
                (0, 0, {
                    "approval_level": "CCM",
                }),
                (0, 0, {
                    "approval_level": "Finance Manager",
                }),
            ]

        return orders
        
        
        
    