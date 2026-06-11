from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    validity_date = fields.Date(string="Expiration")
    new_date = fields.Date(string="New Date")
    approve = fields.Boolean(string="Approved")
    reject = fields.Boolean(string="Reject")
    status_text = fields.Char(string="Status", compute="_compute_status")
    approver_groups = fields.Char(string="Designation / Group", compute="_compute_groups")
    ccm_group_check = fields.Boolean(default=False)
    finance_group_check = fields.Boolean(default=False)
    
    # approve check
    @api.onchange('approve')
    def approve_onchange(self):
        
        difference_date = (self.new_date - self.validity_date).days

        if difference_date <= 30:
            # sudu ccm group approve korbe
            if self.env.user.has_group("zencore_groups.group_zencore_clm_ccm"):
                self.ccm_group_check = True
        elif difference_date > 30:
            # CCM and Finance duita group check korte hobe
            if (self.env.user.has_group("zencore_groups.group_zencore_clm_ccm") and
                self.env.user.has_group("zencore_groups.group_zencore_clm_finance")):
                self.finance_group_check = True
                

    # group add
    @api.depends('write_uid')
    def _compute_groups(self):
        allowed_groups = [
            'Salesperson',
            'Sales Manager',
            'CCM',
            'Warehouse',
            'TDO',
            'Finance',
        ]

        for rec in self:
            if rec.write_uid:
                groups = rec.write_uid.group_ids.filtered(
                    lambda g: g.name in allowed_groups
                )
                rec.approver_groups = ', '.join(groups.mapped('name'))
            else:
                rec.approver_groups = ''
                

    # status change
    @api.depends('approve', 'reject')
    def _compute_status(self):
        for rec in self:
            if rec.reject:
                rec.status_text = "Rejected"
            elif rec.approve:
                rec.status_text = "Approved"
            else:
                rec.status_text = "Pending"
    
    # new window pop-up to get new date
    def action_request_pi_extension(self):  
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request PI Extension',
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sale_pi_governance.sale_popup_wizerd_view_form').id,
            'target': 'new',
            
        }
                
    
    # date calculation
    def action_apply_extension(self):
        self.ensure_one()
        if not self.new_date:
            raise UserError('Please enter a new validity date.')
        if self.new_date <= self.validity_date:
            raise UserError('New date must be after current validity date.')
        
        
        print('shawon')
        print('created date', self.create_date)
        
        difference_date = self.new_date - self.validity_date
        print('difference', difference_date)        # timedelta
        print('difference days', difference_date.days)  # শুধু দিন সংখ্যা
        

        # self.write({'validity_date': self.new_date})
        return {'type': 'ir.actions.act_window_close'}
              
    
    
    