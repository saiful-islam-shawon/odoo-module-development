from odoo import models, api, fields



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
        self.sale_order_id.validity_date = self.new_date