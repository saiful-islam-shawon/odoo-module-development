from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PriceList(models.Model):
    _inherit = 'product.pricelist'
    
    # add status in pricelist
    status = fields.Selection([('draft', 'Draft'),('pending', 'Pending'), ('approved', 'Approved'), ('reject', 'Reject')], string="Status", default="draft", compute="_status_change", store=True, readonly=False, tracking=True)
    approve_user_ids = fields.One2many('approve.user', 'pricelist_id', string="Users Approve", tracking=True)
    pending_update = fields.Boolean(default=False, tracking=True)
    
    @api.depends('approve_user_ids.approve', 'approve_user_ids.reject')
    def _status_change(self):
        for rec in self:
            users = rec.approve_user_ids
            
            if not users:
                rec.status = 'draft'
            elif not any(users.mapped('reject')) and not any(users.mapped('approve')) and not rec.pending_update:
                rec.status = 'draft'
            elif any(users.mapped('reject')):
                rec.status = 'reject'
            elif all(users.mapped('approve')):
                rec.status = 'approved'
            else:
                rec.status = 'pending'
                
    # tatus = approved হলে active = True, বাকি সব False
    @api.depends('status')
    def _compute_active(self):
        for rec in self:
                rec.active = rec.status == 'approved'
                
                
    # add submit button
    def action_submit(self):
        for rec in self:
            if len(rec.approve_user_ids) < 3:
                raise ValidationError("you have to add minimum 3 user")
            if len(rec.item_ids) < 1:
                raise ValidationError("You have to add at least one product")
            else:
                rec.pending_update = True
                rec.status = 'pending'
    
    
    
class ApproveUser(models.Model):
    _name = 'approve.user'
    
    user_id = fields.Many2one('res.users', string="Users", domain=lambda self: self._get_valid_user_domain())
    approve = fields.Boolean(string="Approved")
    reject = fields.Boolean(string="Reject")
    pricelist_id = fields.Many2one('product.pricelist')
    
    
    def write(self, vals):
        if vals.get('approve'):
            vals['reject'] = False
        if vals.get('reject'):
            vals['approve'] = False
        return super().write(vals)
    
    
    @api.onchange('approve', 'reject')
    def _onchange_approveAndreject(self):
        if not self.env.user.has_group('zencore_groups.group_zencore_clm_sales_manager') and self.user_id.id != self.env.user.id:
            raise ValidationError("You can't change another user data")
        
        
    
    def _get_valid_user_domain(self):
        valid_groups = [
            'zencore_groups.group_zencore_clm_sales_manager',
            'zencore_groups.group_zencore_clm_salesperson',
            'zencore_groups.group_zencore_clm_ccm',
            'zencore_groups.group_zencore_clm_warehouse',
            'zencore_groups.group_zencore_clm_tdo',
            'zencore_groups.group_zencore_clm_finance',
        ]

        user_ids = []
        for group_xml_id in valid_groups:
            group = self.env.ref(group_xml_id, raise_if_not_found=False)
            if group:
                # res.groups থেকে SQL দিয়ে user ids বের করো
                self.env.cr.execute(
                    "SELECT uid FROM res_groups_users_rel WHERE gid = %s",
                    (group.id,)
                )
                rows = self.env.cr.fetchall()
                user_ids += [row[0] for row in rows]

        if not user_ids:
            return [('id', '=', False)]

        return [('id', 'in', list(set(user_ids)))]
   