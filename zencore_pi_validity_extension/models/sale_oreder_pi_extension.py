from odoo import models, api, fields
from odoo.exceptions import UserError


class SaleOrderPiExtension(models.Model):
    _inherit = "sale.order"
    
    sale_order_popup_widget_ids = fields.One2many("sale.order.popup.widget", "sale_order_id")
    
    _APPROVAL_STATUS_SELECTION = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    
    ccm_approval_status = fields.Selection(
        selection=_APPROVAL_STATUS_SELECTION,
        string="CCM Status",
        default="pending",
        readonly=True,
        copy=False,
    )
    
    finance_approval_status = fields.Selection(
        selection=_APPROVAL_STATUS_SELECTION,
        string="Finance Manager Status",
        default="pending",
        readonly=True,
        copy=False,
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
        
        
    
    # test
    def approve_action(self):
        self.ensure_one()
        
        if self.env.user.has_group("zencore_groups.group_zencore_clm_ccm"):
            if self.ccm_approval_status == "pending":
                self.ccm_approval_status = "approved"

            elif self.finance_approval_status == "pending":
                # self.finance_approval_status = "approved"
                pass

            else:
                raise UserError(
                    "CCM and Finance approval are already completed."
                )
        else:
            raise UserError("sorry")

        return True
    
    
    
    def reject_action(self):
        pass
        
        
        
    