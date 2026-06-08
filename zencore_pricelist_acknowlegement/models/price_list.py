from odoo import api, fields, models
from odoo.exceptions import ValidationError
from markupsafe import Markup


class PriceList(models.Model):
    _inherit = 'product.pricelist'
    
    # add status in pricelist
    status = fields.Selection([('draft', 'Draft'),('pending', 'Pending'), ('approved', 'Approved'), ('reject', 'Rejected')], string="Status", default="draft", tracking=True, store=True)
    approve_user_ids = fields.One2many('approve.user', 'pricelist_id', string="Users Approve", tracking=True)
    pending_update = fields.Boolean(default=False)
    is_approved = fields.Boolean(compute="_approver_check")
    
    
    
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
                
                
                # activity type খোঁজো
                activity_type = self.env.ref('mail.mail_activity_data_todo')
                
                # প্রতিটা approver user এর জন্য activity create করো
                for approver in rec.approve_user_ids:
                    rec.activity_schedule(
                        activity_type_id=activity_type.id,
                        summary='To-Do',
                        note='Please review the Pricelist',
                        date_deadline=fields.Date.today(),
                        user_id=approver.user_id.id,
                    )
                    
                    
    # add approve and reject button
    def action_approve(self):
        for rec in self:
            current_user = self.env.user
            approver = rec.approve_user_ids.filtered(lambda a: a.user_id.id == current_user.id)
            if not approver:
                raise ValidationError("You are not in the approver list!")
            approver.sudo().write({'approve': True, 'reject': False})

    def action_reject(self):
        for rec in self:
            current_user = self.env.user
            approver = rec.approve_user_ids.filtered(lambda a: a.user_id.id == current_user.id)
            if not approver:
                raise ValidationError("You are not in the approver list!")
            approver.sudo().write({'approve': False, 'reject': True})
            
    # approver check
    @api.depends('approve_user_ids.approve')
    def _approver_check(self):
        for rec in self:
            approver = rec.approve_user_ids.filtered(
                lambda a: a.user_id.id == self.env.uid
            )
            rec.is_approved = approver.approve if approver else False
            
            
            

    # active check
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        # system/superuser হলে block করবো না
        if self.env.su:
            return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
        
        # pricelist নিজের view তে সব দেখাবে
        if self.env.context.get('show_all_pricelist'):
            return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
        
        # active_test=False মানে system internally call করছে — block করবো না
        if not kwargs.get('active_test', True):
            return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)

        domain = [('status', '=', 'approved')] + domain
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
    
    
    
    
class ApproveUser(models.Model):
    _name = 'approve.user'
    _rec_name = 'user_id'
    
    user_id = fields.Many2one('res.users', string="Users", domain=lambda self: self._get_valid_user_domain())
    approve = fields.Boolean(string="Approved")
    reject = fields.Boolean(string="Reject")
    pricelist_id = fields.Many2one('product.pricelist')

    
    
    def write(self, vals):
        if vals.get('approve'):
            vals['reject'] = False
        if vals.get('reject'):
            vals['approve'] = False
        result = super().write(vals)
        # status update trigger করো
        for rec in self:
            if rec.pricelist_id:
                rec.pricelist_id._status_change()
                
                # chatter এ message add করো
                if vals.get('approve'):
                    rec.pricelist_id.message_post(
                        body=Markup("Approvers: <b>{approver}</b><br/>Approved By: <b>{user}</b>").format(
                            approver=rec.user_id.name,
                            user=self.env.user.name,
                        ),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
                elif vals.get('reject'):
                    rec.pricelist_id.message_post(
                        body=Markup("Approvers: <b>{reject}</b><br/>Rejected By: <b>{user}</b>").format(
                            reject=rec.user_id.name,
                            user=self.env.user.name,
                        ),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
        return result
    
    
    # akjon user onno user ar data change korte parbe na
    @api.onchange('approve', 'reject')
    def _onchange_approveAndreject(self):
        if not self.env.user.has_group('zencore_groups.group_zencore_clm_sales_manager') and self.user_id.id != self.env.user.id:
            raise ValidationError("You can't change another user data")
        
        
    # sudu grooup ar under aa thaka oi user gulor data ii cole asbe
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
   