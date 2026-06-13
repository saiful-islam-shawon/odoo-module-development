from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    validity_date = fields.Date(string="Expiration")
    new_date = fields.Date(string="New Date")
    approve = fields.Boolean(string="Approved")
    reject = fields.Boolean(string="Reject")
    approve_finance = fields.Boolean(string="Approved")
    reject_finance = fields.Boolean(string="Rejected")
    status_text = fields.Char(string="Status", compute="_compute_status")
    approver_groups = fields.Char(string="Designation / Group", compute="_compute_groups")
    ccm_group_check = fields.Boolean(default=False)
    # sudu finance group and ccm group ar jonno oi page dakha jabe
    finance_group_check = fields.Boolean(
        compute="_compute_finance_group_check",
        store=False  # ✅ জরুরি
    )
    # finance manager hide rule
    finance_manager_hide_rule = fields.Boolean(default=True)
    # initial page hide rule
    intial_page_hide_rule = fields.Boolean(default=True)
    # =============================
    approval_line_ids = fields.One2many(
        'sale.order.approval.line',
        'order_id',
        string='Approval History'
    )
    # =================================
    
    # ==================================================
    # finance_group_check
    @api.depends_context('uid')  # ✅ এটা দাও
    def _compute_finance_group_check(self):
        for rec in self:
            is_ccm = self.env.user.has_group('zencore_groups.group_zencore_clm_ccm')
            is_finance = self.env.user.has_group('zencore_groups.group_zencore_clm_finance')
            
            if is_ccm or is_finance:
                rec.finance_group_check = False  # ✅ Page visible
            else:
                rec.finance_group_check = True   # ❌ Page hidden
                
    # =================================================
    
    
    
                

    # =================================================
    # jai user approve koreche sa kon kon group ar under aa ache
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
                
    # ======================================================
                

    # ===================================================
    # approve or reject change hole status change hobe
    @api.depends('approve', 'reject')
    def _compute_status(self):
        for rec in self:
            if rec.reject:
                rec.status_text = "Rejected"
            elif rec.approve:
                rec.status_text = "Approved"
            else:
                rec.status_text = "Pending"
                
                
    # ====================================================
    
    # ====================================================
    # akta popup window open hobe setting theke exact button aa click korle
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
        
    # =====================================================
                

    # ======================================================
    # popup theke apply button aa ckick korle ai action apply hobe
    # date calculation
    def action_apply_extension(self):
        self.ensure_one()
        if not self.new_date:
            raise UserError('Please enter a new validity date.')
        if self.new_date <= self.validity_date:
            raise UserError('New date must be after current validity date.')
        
        
        diffrence = (self.new_date - self.validity_date).days
        
        # initial page hide rule
        self.write({
            'intial_page_hide_rule': False
        })
        
        if diffrence <= 30:
            # শুধু CCM approve করবে
            self.write({
                'finance_manager_hide_rule': True,
            })
        else:
            # CCM + Finance দুজনেই approve করবে
            self.write({
                'finance_manager_hide_rule': False,
            }) 
        

        # self.write({'validity_date': self.new_date})
        return {'type': 'ir.actions.act_window_close'}
    
    # =======================================================
    
    # =======================================================
    # change validaty date by ccm group
    # def write(self, vals):
    #     result = super().write(vals)
    #     for rec in self:
    #         # <= 30 days: CCM approve করলেই validity_date update হবে
    #         if vals.get('approve') and rec.finance_manager_hide_rule:
    #             rec.validity_date = rec.new_date

    #         # > 30 days: Finance approve করলে validity_date update হবে
    #         if vals.get('approve_finance') and not rec.finance_manager_hide_rule:
    #             rec.validity_date = rec.new_date

    #     return result
    
    
    
    def write(self, vals):
        result = super().write(vals)
        for rec in self:
            # CCM approve করলে line add করো
            if vals.get('approve'):
                groups = rec.env.user.group_ids.filtered(
                    lambda g: g.name in ['CCM', 'Finance', 'Salesperson', 'Sales Manager']
                )
                designation = ', '.join(groups.mapped('name'))
                rec.approval_line_ids.create({
                    'order_id': rec.id,
                    'name': rec.env.user.name,
                    'designation': designation,
                    'approve_date': fields.Datetime.now(),
                    'status': 'approved',
                })
                
                if rec.finance_manager_hide_rule:
                    # validaty_date change
                    rec.validity_date = rec.new_date

            # CCM reject করলে line add করো
            if vals.get('reject'):
                groups = rec.env.user.group_ids.filtered(
                    lambda g: g.name in ['CCM', 'Finance', 'Salesperson', 'Sales Manager']
                )
                designation = ', '.join(groups.mapped('name'))
                rec.approval_line_ids.create({
                    'order_id': rec.id,
                    'name': rec.env.user.name,
                    'designation': designation,
                    'approve_date': fields.Datetime.now(),
                    'status': 'rejected',
                })

            # Finance approve করলে line add করো
            if vals.get('approve_finance'):
                groups = rec.env.user.group_ids.filtered(
                    lambda g: g.name in ['CCM', 'Finance', 'Salesperson', 'Sales Manager']
                )
                designation = ', '.join(groups.mapped('name'))
                rec.approval_line_ids.create({
                    'order_id': rec.id,
                    'name': rec.env.user.name,
                    'designation': designation,
                    'approve_date': fields.Datetime.now(),
                    'status': 'approved',
                })
                
                # validaty_date change
                rec.validity_date = rec.new_date

            # ✅ Finance reject করলে line add করো
            if vals.get('reject_finance'):
                groups = rec.env.user.group_ids.filtered(
                    lambda g: g.name in ['CCM', 'Finance', 'Salesperson', 'Sales Manager']
                )
                designation = ', '.join(groups.mapped('name'))
                rec.approval_line_ids.create({
                    'order_id': rec.id,
                    'name': rec.env.user.name,
                    'designation': designation,
                    'approve_date': fields.Datetime.now(),
                    'status': 'rejected',  # ✅ rejected
                })

        return result
    
    # ============================================================
    
    
    
    
# =============================================================
# show data in a list view
    

class SaleOrderApprovalLine(models.Model):
    _name = 'sale.order.approval.line'
    _description = 'Sale Order Approval History'

    order_id = fields.Many2one(
        'sale.order',
        string='Order',
        ondelete='cascade'
    )
    name = fields.Char(string='Name')
    designation = fields.Char(string='Designation')
    approve_date = fields.Datetime(string='Approve Date')
    status = fields.Selection([
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ], string='Status', default='pending')
    
    
    
        
    
    