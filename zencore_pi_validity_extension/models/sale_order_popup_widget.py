from odoo import models, api, fields
from odoo.exceptions import UserError


class SaleOrderPopupWidget(models.Model):
    _name = "sale.order.popup.widget"
    _description = "Sale Order PI Validity Extension Request"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        required=True,
        readonly=True,
        ondelete="cascade",
    )

    validity_date = fields.Date(
        string="Old Expiration Date",
        required=True,
        readonly=True,
    )

    new_date = fields.Date(
        string="New Expiration Date",
        required=True,
    )
    
    
    
    
    def action_apply_extension(self):
        self.ensure_one()
        
        if self.new_date <= self.validity_date:
            raise UserError(
                "New Expiration Date must be greater than the current Expiration Date."
            )

        difference = (
            self.new_date - self.validity_date
        ).days

        self.sale_order_id.approval_line_ids.unlink()

        approval_lines = [
            (0, 0, {
                "approval_level": "CCM",
            })
        ]
        
        # remove all activity for ccm and finance manager
        self.sale_order_id._remove_group_activity(
            "zencore_groups.group_zencore_clm_ccm"
        )

        self.sale_order_id._remove_group_activity(
            "zencore_groups.group_zencore_clm_finance"
        )
        
        # create activity for ccm
        self.sale_order_id._create_group_activity(
            "zencore_groups.group_zencore_clm_ccm",
            "PI Extension Approval",
        )
        
        
        
        if difference >= 30:
            approval_lines.append(
                (0, 0, {
                    "approval_level": "Finance Manager",
                })
            )

        self.sale_order_id.write({
            "new_date": self.new_date,
            "approval_line_ids": approval_lines,
        })

        return {
            "type": "ir.actions.act_window_close",
        }