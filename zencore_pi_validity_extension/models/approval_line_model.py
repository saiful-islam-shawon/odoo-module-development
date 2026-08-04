from odoo import models, fields
from odoo.exceptions import UserError

class SaleOrderApprovalLine(models.Model):
    _name = "sale.order.approval.line"
    _description = "Sale Order Approval Line"

    sale_order_id = fields.Many2one(
        "sale.order",
        required=True,
        ondelete="cascade",
    )

    validity_date = fields.Date(
    related="sale_order_id.validity_date",
    string="Old Date",
    readonly=True,
    )

    new_date = fields.Date(
        related="sale_order_id.new_date",
        string="New Date",
        readonly=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="Approved By",
        readonly=True,
    )

    approval_level = fields.Char()

    approve_date = fields.Datetime(string="Approve Date", default=fields.Date.today,)

    status = fields.Selection([
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="pending")



    def action_approve(self):
        self.ensure_one()

        if self.status == "approved":
            raise UserError("You have already approved this request.")
            return

        if self.status == "rejected":
            raise UserError("This request has already been rejected.")
            return

        if self.approval_level == "CCM":
            if not self.env.user.has_group("zencore_groups.group_zencore_clm_ccm"):
                raise UserError("Only CCM can approve this line.")

        elif self.approval_level == "Finance Manager":
            if not self.env.user.has_group("zencore_groups.group_zencore_clm_finance"):
                raise UserError("Only Finance Manager can approve this line.")

            # CCM approval check
            ccm_line = self.sale_order_id.approval_line_ids.filtered(
                lambda l: l.approval_level == "CCM"
            )

            if not ccm_line or ccm_line.status != "approved":
                raise UserError(
                    "CCM approval is required before Finance Manager approval."
                )
        
        
        self.write({
            "status": "approved",
            "approve_date": fields.Datetime.now(),
            "user_id": self.env.user.id,
        })

        # কত দিনের extension
        difference = (
            self.sale_order_id.new_date - self.sale_order_id.validity_date
        ).days

      
        
        if difference < 30:

            self.sale_order_id.write({
                "validity_date": self.sale_order_id.new_date,
            })

            self.sale_order_id._remove_group_activity(
                "zencore_groups.group_zencore_clm_ccm"
            )

        elif self.approval_level == "CCM":

            self.sale_order_id._remove_group_activity(
                "zencore_groups.group_zencore_clm_ccm"
            )

            self.sale_order_id._create_group_activity(
                "zencore_groups.group_zencore_clm_finance",
                "Finance Approval Required"
            )

        elif self.approval_level == "Finance Manager":

            self.sale_order_id.write({
                "validity_date": self.sale_order_id.new_date,
            })

            self.sale_order_id._remove_group_activity(
                "zencore_groups.group_zencore_clm_finance"
            )

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }


    

    # rejected action
    def action_reject(self):
        self.ensure_one()

        # Already processed check
        if self.status == "approved":
            raise UserError("This request has already been approved.")

        if self.status == "rejected":
            raise UserError("You have already rejected this request.")

        # Permission check
        if self.approval_level == "CCM":
            if not self.env.user.has_group("zencore_groups.group_zencore_clm_ccm"):
                raise UserError("Only CCM can reject this line.")

        elif self.approval_level == "Finance Manager":
            if not self.env.user.has_group("zencore_groups.group_zencore_clm_finance"):
                raise UserError("Only Finance Manager can reject this line.")

            # Finance reject করার আগে CCM approve থাকতে হবে
            ccm_line = self.sale_order_id.approval_line_ids.filtered(
                lambda l: l.approval_level == "CCM"
            )

            if not ccm_line or ccm_line.status != "approved":
                raise UserError(
                    "CCM approval is required before Finance Manager rejection."
                )

        self.write({
            "status": "rejected",
            "approve_date": fields.Datetime.now(),
            "user_id": self.env.user.id,
        })
        
        
        # remove all activity
        self.sale_order_id._remove_group_activity(
            "zencore_groups.group_zencore_clm_ccm"
        )

        self.sale_order_id._remove_group_activity(
            "zencore_groups.group_zencore_clm_finance"
        )

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }