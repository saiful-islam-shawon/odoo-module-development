from odoo import api, fields, models
from odoo.exceptions import ValidationError
from markupsafe import Markup


class PriceList(models.Model):
    _inherit = 'product.pricelist'
    
    # ==================== FIELDS ====================
    
    # Pricelist এর current status track করে
    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('reject', 'Rejected')
    ], string="Status", default="draft", tracking=True, store=True)
    
    # Approver user list — approve.user model এর সাথে One2many relation
    approve_user_ids = fields.One2many(
        'approve.user', 'pricelist_id', 
        string="Users Approve", 
        tracking=True
    )
    
    # Submit করা হয়েছে কিনা track করে — status logic এ ব্যবহার হয়
    pending_update = fields.Boolean(default=False)
    
    # Current login user approve করেছে কিনা check করে
    is_approved = fields.Boolean(compute="_approver_check")
    
    # Pricelist name field readonly হবে কিনা — group ভেদে control করে
    is_name_readonly = fields.Boolean(compute='_compute_name_readonly')
    
    # Approver tab এর পুরো field readonly হবে কিনা — group ও status ভেদে
    is_approver_readonly = fields.Boolean(compute='_compute_approver_readonly')
    
    # Approver list এর user_id column readonly হবে কিনা — group ও status ভেদে
    is_user_id_readonly = fields.Boolean(compute='_compute_user_id_readonly')
    
    # Valid group এর user থেকে already selected বাদ দিয়ে available user list
    # domain এ ব্যবহার হয় যাতে duplicate user select না হয়
    selected_user_ids = fields.Many2many(
        'res.users',
        compute='_compute_selected_user_ids'
    )
    
    
    # ==================== COMPUTE METHODS ====================
    
    # approve_user_ids এর user_id change হলে recompute হয়
    # valid group এর user বের করে, already selected বাদ দিয়ে available list তৈরি করে
    @api.depends('approve_user_ids.user_id')
    def _compute_selected_user_ids(self):
        valid_groups = [
            'zencore_groups.group_zencore_clm_sales_manager',
            'zencore_groups.group_zencore_clm_salesperson',
            'zencore_groups.group_zencore_clm_ccm',
            'zencore_groups.group_zencore_clm_warehouse',
            'zencore_groups.group_zencore_clm_tdo',
            'zencore_groups.group_zencore_clm_finance',
        ]

        # প্রতিটা valid group এর user ids বের করো SQL দিয়ে
        valid_user_ids = []
        for group_xml_id in valid_groups:
            group = self.env.ref(group_xml_id, raise_if_not_found=False)
            if group:
                self.env.cr.execute(
                    "SELECT uid FROM res_groups_users_rel WHERE gid = %s",
                    (group.id,)
                )
                rows = self.env.cr.fetchall()
                valid_user_ids += [row[0] for row in rows]

        # Duplicate ids বাদ দাও
        valid_user_ids = list(set(valid_user_ids))

        for rec in self:
            # এই pricelist এ already যোগ করা user ids
            already_selected = rec.approve_user_ids.mapped('user_id').ids

            # Valid users থেকে already selected বাদ দিয়ে available list তৈরি করো
            available_ids = [
                uid for uid in valid_user_ids
                if uid not in already_selected
            ]

            rec.selected_user_ids = self.env['res.users'].browse(available_ids)

    
    # Status change হলে recompute হয়
    # Sales Manager → approved/reject এ readonly
    # অন্য group → শুধু approved এ readonly
    @api.depends('status')
    def _compute_approver_readonly(self):
        user = self.env.user
        is_manager = user.has_group(
            'zencore_groups.group_zencore_clm_sales_manager'
        )
        for rec in self:
            if is_manager:
                rec.is_approver_readonly = rec.status in ('approved', 'reject')
            else:
                rec.is_approver_readonly = rec.status == 'approved'

    
    # Status change হলে recompute হয়
    # Sales Manager → pending/draft এ edit করতে পারবে
    # অন্য group → সবসময় readonly (user_id পরিবর্তন করতে পারবে না)
    @api.depends('status')
    def _compute_user_id_readonly(self):
        user = self.env.user
        is_manager = user.has_group(
            'zencore_groups.group_zencore_clm_sales_manager'
        )
        for rec in self:
            if is_manager:
                rec.is_user_id_readonly = rec.status not in ('pending', 'draft')
            else:
                rec.is_user_id_readonly = True

    
    # Status change হলে recompute হয়
    # Sales Manager (একা বা অন্য group সহ) → approved/reject এ readonly
    # অন্য যেকোনো group → সবসময় readonly
    @api.depends('status')
    def _compute_name_readonly(self):
        user = self.env.user
        is_manager = user.has_group(
            'zencore_groups.group_zencore_clm_sales_manager'
        )
        is_other = (
            user.has_group('zencore_groups.group_zencore_clm_salesperson') or
            user.has_group('zencore_groups.group_zencore_clm_ccm') or
            user.has_group('zencore_groups.group_zencore_clm_warehouse') or
            user.has_group('zencore_groups.group_zencore_clm_tdo') or
            user.has_group('zencore_groups.group_zencore_clm_finance') or
            user.has_group('base.group_system')
        )

        for rec in self:
            if is_manager and is_other:
                # দুটো group এ থাকলে Manager priority পাবে
                rec.is_name_readonly = rec.status in ('approved', 'reject')
            elif is_manager:
                # শুধু Manager → approved/reject এ readonly
                rec.is_name_readonly = rec.status in ('approved', 'reject')
            else:
                # অন্য যেকোনো group → সবসময় readonly
                rec.is_name_readonly = True


    # approve/reject change হলে status automatically update হয়
    # Logic: reject আছে → reject | সবাই approve → approved | কেউ না → draft/pending
    @api.depends('approve_user_ids.approve', 'approve_user_ids.reject')
    def _status_change(self):
        for rec in self:
            users = rec.approve_user_ids

            if not users:
                # কোনো user নেই → draft
                rec.status = 'draft'
            elif not any(users.mapped('reject')) and not any(users.mapped('approve')) and not rec.pending_update:
                # কেউ approve/reject করেনি এবং submit হয়নি → draft
                rec.status = 'draft'
            elif any(users.mapped('reject')):
                # যেকোনো একজন reject করলে → reject
                rec.status = 'reject'
            elif all(users.mapped('approve')):
                # সবাই approve করলে → approved
                rec.status = 'approved'
            else:
                # কেউ কেউ approve করেছে কিন্তু সবাই না → pending
                rec.status = 'pending'


    # ==================== ACTION METHODS ====================

    # Submit button click করলে চলে
    # Minimum 3 user এবং 1 product check করে, তারপর pending করে activity create করে
    def action_submit(self):
        for rec in self:
            if len(rec.approve_user_ids) < 3:
                raise ValidationError("you have to add minimum 3 user")
            if len(rec.item_ids) < 1:
                raise ValidationError("You have to add at least one product")
            else:
                rec.pending_update = True
                rec.status = 'pending'

                # প্রতিটা approver এর জন্য To-Do activity create করো
                activity_type = self.env.ref('mail.mail_activity_data_todo')
                for approver in rec.approve_user_ids:
                    rec.activity_schedule(
                        activity_type_id=activity_type.id,
                        summary='To-Do',
                        note='Please review the Pricelist',
                        date_deadline=fields.Date.today(),
                        user_id=approver.user_id.id,
                    )

    
    # Approve button click করলে চলে
    # Current user approver list এ আছে কিনা check করে, থাকলে approve করে
    def action_approve(self):
        for rec in self:
            current_user = self.env.user
            approver = rec.approve_user_ids.filtered(
                lambda a: a.user_id.id == current_user.id
            )
            if not approver:
                raise ValidationError("You are not in the approver list!")
            approver.sudo().write({'approve': True, 'reject': False})

    
    # Reject button click করলে চলে
    # Current user approver list এ আছে কিনা check করে, থাকলে reject করে
    def action_reject(self):
        for rec in self:
            current_user = self.env.user
            approver = rec.approve_user_ids.filtered(
                lambda a: a.user_id.id == current_user.id
            )
            if not approver:
                raise ValidationError("You are not in the approver list!")
            approver.sudo().write({'approve': False, 'reject': True})

    
    # Current login user approve করেছে কিনা check করে
    # Header এ Approve/Reject button show/hide করতে ব্যবহার হয়
    @api.depends('approve_user_ids.approve')
    def _approver_check(self):
        for rec in self:
            approver = rec.approve_user_ids.filtered(
                lambda a: a.user_id.id == self.env.uid
            )
            rec.is_approved = approver.approve if approver else False


    # ==================== SEARCH OVERRIDE ====================

    # Pricelist search override — শুধু approved pricelist দেখাবে
    # Exception: superuser, show_all_pricelist context, internal system call
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        # Superuser হলে সব দেখাবে
        if self.env.su:
            return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)

        # Pricelist নিজের view তে সব দেখাবে
        if self.env.context.get('show_all_pricelist'):
            return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)

        # System internal call হলে block করবো না
        if not kwargs.get('active_test', True):
            return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)

        # বাকি সব ক্ষেত্রে শুধু approved pricelist দেখাবে
        domain = [('status', '=', 'approved')] + domain
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)




class ApproveUser(models.Model):
    _name = 'approve.user'
    _rec_name = 'user_id'
    
    # ==================== FIELDS ====================
    
    # Approver user — শুধু valid group এর user দেখাবে domain এ
    user_id = fields.Many2one(
        'res.users',
        string="Users",
        domain=lambda self: self._get_valid_user_domain()
    )
    
    # User approve করেছে কিনা
    approve = fields.Boolean(string="Approved")
    
    # User reject করেছে কিনা
    reject = fields.Boolean(string="Reject")
    
    # কোন pricelist এর approver — Many2one relation
    pricelist_id = fields.Many2one('product.pricelist')


    # ==================== CRUD OVERRIDE ====================

    # Duplicate user check — create এর সময়
    # একই pricelist এ একই user দুইবার add করা যাবে না
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            pricelist_id = vals.get('pricelist_id')
            user_id = vals.get('user_id')

            if pricelist_id and user_id:
                # নতুন list এ একই user দুইবার আছে কিনা check
                new_users = [v.get('user_id') for v in vals_list]
                if new_users.count(user_id) > 1:
                    user = self.env['res.users'].browse(user_id)
                    raise ValidationError(
                        f"'{user.name}' already added in approver list!"
                    )

                # Database এ already আছে কিনা check
                existing = self.search([
                    ('pricelist_id', '=', pricelist_id),
                    ('user_id', '=', user_id),
                ])
                if existing:
                    user = self.env['res.users'].browse(user_id)
                    raise ValidationError(
                        f"'{user.name}' already added in approver list!"
                    )

        return super().create(vals_list)


    # Duplicate user check — constraint (double protection)
    # create/write উভয় ক্ষেত্রেই চলে
    @api.constrains('user_id', 'pricelist_id')
    def _check_duplicate_user(self):
        for rec in self:
            duplicate = self.search([
                ('pricelist_id', '=', rec.pricelist_id.id),
                ('user_id', '=', rec.user_id.id),
                ('id', '!=', rec.id),  # নিজেকে বাদ দাও
            ])
            if duplicate:
                raise ValidationError(
                    f"'{rec.user_id.name}' already added in approver list!"
                )


    # approve/reject write হলে চলে
    # approve → reject False করে, reject → approve False করে (mutually exclusive)
    # তারপর pricelist status update করে এবং chatter এ message post করে
    def write(self, vals):
        # approve এবং reject একসাথে True হতে পারবে না
        if vals.get('approve'):
            vals['reject'] = False
        if vals.get('reject'):
            vals['approve'] = False

        result = super().write(vals)

        for rec in self:
            if rec.pricelist_id:
                # Pricelist এর status update করো
                rec.pricelist_id._status_change()

                # Approve হলে chatter এ message post করো
                if vals.get('approve'):
                    rec.pricelist_id.message_post(
                        body=Markup(
                            "Approvers: <b>{approver}</b><br/>Approved By: <b>{user}</b>"
                        ).format(
                            approver=rec.user_id.name,
                            user=self.env.user.name,
                        ),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
                # Reject হলে chatter এ message post করো
                elif vals.get('reject'):
                    rec.pricelist_id.message_post(
                        body=Markup(
                            "Approvers: <b>{reject}</b><br/>Rejected By: <b>{user}</b>"
                        ).format(
                            reject=rec.user_id.name,
                            user=self.env.user.name,
                        ),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
        return result


    # ==================== VALIDATION ====================

    # একজন user অন্য user এর approve/reject change করতে পারবে না
    # Exception: Sales Manager যেকোনো user এর data change করতে পারবে
    @api.onchange('approve', 'reject')
    def _onchange_approveAndreject(self):
        if (
            not self.env.user.has_group('zencore_groups.group_zencore_clm_sales_manager')
            and self.user_id.id != self.env.user.id
        ):
            raise ValidationError("You can't change another user data")


    # ==================== DOMAIN HELPER ====================

    # Valid group এর user ids বের করে domain তৈরি করে
    # শুধু এই groups এর user গুলোই approver হিসেবে select করা যাবে
    def _get_valid_user_domain(self):
        valid_groups = [
            'zencore_groups.group_zencore_clm_sales_manager',
            'zencore_groups.group_zencore_clm_salesperson',
            'zencore_groups.group_zencore_clm_ccm',
            'zencore_groups.group_zencore_clm_warehouse',
            'zencore_groups.group_zencore_clm_tdo',
            'zencore_groups.group_zencore_clm_finance',
        ]

        # প্রতিটা group এর user ids SQL দিয়ে বের করো
        user_ids = []
        for group_xml_id in valid_groups:
            group = self.env.ref(group_xml_id, raise_if_not_found=False)
            if group:
                self.env.cr.execute(
                    "SELECT uid FROM res_groups_users_rel WHERE gid = %s",
                    (group.id,)
                )
                rows = self.env.cr.fetchall()
                user_ids += [row[0] for row in rows]

        # কোনো user না পেলে কাউকেই দেখাবে না
        if not user_ids:
            return [('id', '=', False)]

        return [('id', 'in', list(set(user_ids)))]