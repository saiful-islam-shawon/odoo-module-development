from odoo import models, api, fields
from markupsafe import Markup
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SkuReclasificationRequest(models.Model):
    _name = "sku.reclassification.request"
    _description = "SKU Reclassification Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    sku_source_product = fields.Many2one(
        "product.template",
        string="Source SKU",
        tracking=True,
    )
    source_product_name = fields.Char(
        related="sku_source_product.name",
        string="Product Name",
    )
    source_product_quantity = fields.Float(
        related="sku_source_product.qty_available",
        string="Quantity On Hand",
    )
    source_product_cost_price = fields.Float(
        related="sku_source_product.standard_price",
        string="Cost Price",
    )
    source_lot_numbers = fields.Char(
        string="Lot Numbers",
        compute="_compute_source_lot_numbers",
    )

    sku_target_product = fields.Many2one(
        "product.template",
        string="Target SKU",
        tracking=True,
    )
    target_product_name = fields.Char(
        related="sku_target_product.name",
        string="Product Name",
    )
    target_product_quantity = fields.Float(
        related="sku_target_product.qty_available",
        string="Quantity On Hand",
    )
    target_product_cost_price = fields.Float(
        related="sku_target_product.standard_price",
        string="Cost Price",
    )
    target_lot_numbers = fields.Char(
        string="Lot Number",
        tracking=True,
    )

    quantity = fields.Float(string="Quantity Changes")

    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("pending", "Pending"),
            ("complete", "Complete"),
            ("cancel", "Cancel"),
            ("rejected", "Rejected"),
            ("draft", "Draft"),
        ],
        string="Status",
        default="new",
        tracking=True,
    )


    reclassification_journal_id = fields.Many2one(
        "account.move",
        string="Reclassification Journal Entry",
        readonly=True,
        copy=False,
    )
    
    factory_manager_visiblity_button = fields.Boolean(default=False)
    sales_manager_visibility_button = fields.Boolean(default=False)
    finance_manager_visibility_button = fields.Boolean(default=False)
    
    
    factory_manager_hiearicy = fields.Boolean(default=True)
    sales_manager_hiearicy = fields.Boolean(default=True)
    finance_manager_hiearicy = fields.Boolean(default=True)
    
    
    
    # =========================
    # common approval selection
    # =========================
    _APPROVAL_STATUS_SELECTION = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("cancel", "Cancelled"),
        ("rejected", "Rejected"),
        ("reset_to_draft", "Reset To Draft"),
    ]
    
    
    
    store_keeper_approval_date = fields.Datetime(
        string="Store Keeper Approval Date",
        readonly=True,
        copy=False,
    )

    factory_manager_approval_date = fields.Datetime(
        string="Factory Manager Approval Date",
        readonly=True,
        copy=False,
    )

    sales_manager_approval_date = fields.Datetime(
        string="Sales Manager Approval Date",
        readonly=True,
        copy=False,
    )

    finance_manager_approval_date = fields.Datetime(
        string="Finance Manager Approval Date",
        readonly=True,
        copy=False,
    )
    
    
    store_keeper_approved_by = fields.Many2one(
        "res.users",
        string="Store Keeper",
        readonly=True,
        copy=False,
    )

    factory_manager_approved_by = fields.Many2one(
        "res.users",
        string="Factory Manager",
        readonly=True,
        copy=False,
    )

    sales_manager_approved_by = fields.Many2one(
        "res.users",
        string="Sales Manager",
        readonly=True,
        copy=False,
    )

    finance_manager_approved_by = fields.Many2one(
        "res.users",
        string="Finance Manager",
        readonly=True,
        copy=False,
    )
    
    
    
    store_keeper_approval_status = fields.Selection(
        selection=_APPROVAL_STATUS_SELECTION,
        string="Store Keeper Status",
        default="pending",
        readonly=True,
        copy=False,
    )

    factory_manager_approval_status = fields.Selection(
        selection=_APPROVAL_STATUS_SELECTION,
        string="Factory Manager Status",
        default="pending",
        readonly=True,
        copy=False,
    )

    sales_manager_approval_status = fields.Selection(
        selection=_APPROVAL_STATUS_SELECTION,
        string="Sales Manager Status",
        default="pending",
        readonly=True,
        copy=False,
    )

    finance_manager_approval_status = fields.Selection(
        selection=_APPROVAL_STATUS_SELECTION,
        string="Finance Manager Status",
        default="pending",
        readonly=True,
        copy=False,
    )
    
    
    # note field
    description = fields.Html(string="Note")
    
    
    
    
    # =========================
    # compute display name
    # =========================
    @api.depends("sku_source_product", "sku_target_product")
    def _compute_display_name(self):
        for record in self:
            source_name = record.sku_source_product.name or "No Source"
            target_name = record.sku_target_product.name or "No Target"
            record.display_name = f"{source_name} -> {target_name}"
    

    # =========================
    # COMPUTE LOTS
    # =========================

    @api.depends("sku_source_product")
    def _compute_source_lot_numbers(self):
        StockQuant = self.env["stock.quant"].sudo()

        for rec in self:
            if not rec.sku_source_product:
                rec.source_lot_numbers = ""
                continue

            product_variants = rec.sku_source_product.product_variant_ids

            quants = StockQuant.search([
                ("product_id", "in", product_variants.ids),
                ("location_id.usage", "=", "internal"),
                ("quantity", ">", 0),
                ("lot_id", "!=", False),
            ])

            rec.source_lot_numbers = ", ".join(quants.mapped("lot_id.name"))

    @api.onchange("sku_target_product")
    def _onchange_sku_target_product(self):
        self.target_lot_numbers = False

    # =========================
    # HELPERS
    # =========================

    def _check_group(self, group_xmlid, error_message):
        if not self.env.user.has_group(group_xmlid):
            raise UserError(error_message)


    def _schedule_group_activity(self, group_xmlid, summary, note):
        group = self.env.ref(group_xmlid)
        users = group.all_user_ids

        for rec in self:
            for user in users:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    summary=summary,
                    note=note,
                    date_deadline=fields.Date.context_today(rec),
                )

    def _schedule_user_activity(self, user, summary, note):
        if not user:
            return

        for rec in self:
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=user.id,
                summary=summary,
                note=note,
                date_deadline=fields.Date.context_today(rec),
            )

    def _close_group_activities(self):
        for rec in self:
            if rec.activity_ids:
                rec.activity_ids.action_feedback()
    

    def _close_all_pending_activities(self):
        for rec in self:
            if rec.activity_ids:
                rec.activity_ids.unlink()

    # =========================
    # STOREKEEPER
    # =========================

    def change_req_by_storekeeper(self):
        self._check_group(
            "zencore_product_reclasification.store_keeper_group",
            "Only Storekeeper can submit this request.",
        )

        for rec in self:
            if rec.state not in ["new", "draft"]:
                raise UserError("Only new/draft requests can be submitted.")
            
            if not rec.target_lot_numbers or not rec.target_lot_numbers.strip():
                raise UserError("Please enter the Target Lot Number.")

            rec.state = "pending"
            rec.factory_manager_hiearicy = False
            
            # store keeper approval
            rec.store_keeper_approval_date = fields.Datetime.now()
            rec.store_keeper_approved_by = self.env.user.id
            rec.store_keeper_approval_status = "approved"

            rec.message_post(
                body=Markup(
                    "The SKU Reclassification Request was submitted by "
                    "<b>%s</b> (<b>Storekeeper</b>) and is awaiting "
                    "Factory Manager approval."
                ) % self.env.user.name
            )

        self._schedule_group_activity(
            "zencore_product_reclasification.factory_manager_group",
            "SKU Reclassification Approval",
            "Please review the SKU reclassification request.",
        )

        return True

    def cancel_by_storekeeper(self):
        self._check_group(
            "zencore_product_reclasification.store_keeper_group",
            "Only Storekeeper can cancel this request.",
        )

        for rec in self:
            if rec.state == "complete":
                raise UserError("Completed requests cannot be cancelled.")

            rec.state = "cancel"

            rec.message_post(
                body=Markup(
                    "SKU Reclassification Request was cancelled by "
                    "<b>%s</b> (<b>Storekeeper</b>)."
                ) % self.env.user.name
            )

        self._close_all_pending_activities()

        return True

    def reset_to_draft_action(self):
        self._check_group(
            "zencore_product_reclasification.store_keeper_group",
            "Only Storekeeper can reset this request.",
        )

        for rec in self:

            rec.state = "new"

            rec.message_post(
                body=Markup(
                    "SKU Reclassification Request was reset to draft by "
                    "<b>%s</b>."
                ) % self.env.user.name
            )

        self._close_all_pending_activities()

        return True

    # =========================
    # FACTORY MANAGER
    # =========================

    def approve_by_factory_manager(self):
        self._check_group(
            "zencore_product_reclasification.factory_manager_group",
            "Only Factory Manager can approve this request.",
        )

        for rec in self:
            if rec.state != "pending":
                raise UserError("Only pending requests can be approved.")
            
            # button invisible for factory manager
            rec.factory_manager_visiblity_button = True
            rec.sales_manager_hiearicy = False
            
            # factory manager approve
            rec.factory_manager_approval_date = fields.Datetime.now()
            rec.factory_manager_approved_by = self.env.user.id
            rec.factory_manager_approval_status = "approved"


            rec.message_post(
                body=Markup(
                    "SKU Reclassification Request approved by "
                    "<b>%s</b> (<b>Factory Manager</b>) and is awaiting "
                    "Sales Manager approval."
                ) % self.env.user.name
            )

        self._close_group_activities()

        self._schedule_group_activity(
            "zencore_product_reclasification.sales_manager_group",
            "SKU Reclassification Sales Approval",
            "Please review the SKU Reclassification Request.",
        )

        return True

    def reject_by_factory_manager(self):
        self._check_group(
            "zencore_product_reclasification.factory_manager_group",
            "Only Factory Manager can reject this request.",
        )

        for rec in self:
            
            # button invisible for factory manager
            rec.factory_manager_visiblity_button = True
            

            rec.state = "rejected"
            
            # factory manager rejected
            rec.factory_manager_approval_date = fields.Datetime.now()
            rec.factory_manager_approved_by = self.env.user.id
            rec.factory_manager_approval_status = "rejected"

            rec.message_post(
                body=Markup(
                    "SKU Reclassification Request was rejected by "
                    "<b>%s</b> (<b>Factory Manager</b>)."
                ) % self.env.user.name
            )

        self._close_group_activities()

        return True

    # =========================
    # SALES MANAGER
    # =========================

    def approve_by_sales_manager(self):
        self._check_group(
            "zencore_product_reclasification.sales_manager_group",
            "Only Sales Manager can approve this request.",
        )

        for rec in self:
            if rec.state != "pending":
                raise UserError("Only pending requests can be approved.")
            
            # button invisible for sales manager
            rec.sales_manager_visibility_button = True
            rec.finance_manager_hiearicy = False
            
            # sales manager approve
            rec.sales_manager_approval_date = fields.Datetime.now()
            rec.sales_manager_approved_by = self.env.user.id
            rec.sales_manager_approval_status = "approved"

            rec.message_post(
                body=Markup(
                    "SKU Reclassification Request approved by "
                    "<b>%s</b> (<b>Sales Manager</b>) and is awaiting "
                    "Finance Manager approval."
                ) % self.env.user.name
            )

        self._close_group_activities()

        self._schedule_group_activity(
            "zencore_product_reclasification.finance_manager_group",
            "SKU Reclassification Finance Approval",
            "Please review the SKU Reclassification Request.",
        )

        return True

    def reject_by_sales_manager(self):
        self._check_group(
            "zencore_product_reclasification.sales_manager_group",
            "Only Sales Manager can reject this request.",
        )

        for rec in self:
            
            # button invisible for sales manager
            rec.sales_manager_visibility_button = True
            
            
            # sales manager rejected
            rec.sales_manager_approval_date = fields.Datetime.now()
            rec.sales_manager_approved_by = self.env.user.id
            rec.sales_manager_approval_status = "rejected"
            

            rec.state = "rejected"

            rec.message_post(
                body=Markup(
                    "SKU Reclassification Request was rejected by "
                    "<b>%s</b> (<b>Sales Manager</b>)."
                ) % self.env.user.name
            )

        self._close_group_activities()

        return True

    # =========================
    # FINANCE MANAGER
    # =========================

    def finance_manager_action(self):
        self._check_group(
            "zencore_product_reclasification.finance_manager_group",
            "Only Finance Manager can complete this request.",
        )

        for rec in self:
            if rec.state == "complete":
                raise UserError("This request is already completed.")
            
            
            # button invisible for finance manager
            rec.finance_manager_visibility_button = True
            
            # finance manager approved
            rec.finance_manager_approval_date = fields.Datetime.now()
            rec.finance_manager_approved_by = self.env.user.id
            rec.finance_manager_approval_status = "approved"

            rec.approve_action()
            rec.action_create_reclassification_journal()

            rec.state = "complete"

            rec.message_post(
                body=Markup(
                    "SKU Reclassification completed by <b>%s</b> "
                    "(<b>Finance Manager</b>)."
                ) % self.env.user.name
            )

        self._close_group_activities()

        return True

    def reject_by_finance_manager(self):
        self._check_group(
            "zencore_product_reclasification.finance_manager_group",
            "Only Finance Manager can reject this request.",
        )

        for rec in self:
            
            # button invisible for finance manager
            rec.finance_manager_visibility_button = True
            
            # finance manager rejected
            rec.finance_manager_approval_date = fields.Datetime.now()
            rec.finance_manager_approved_by = self.env.user.id
            rec.finance_manager_approval_status = "rejected"
            

            rec.state = "rejected"

            rec.message_post(
                body=Markup(
                    "SKU Reclassification Request was rejected by "
                    "<b>%s</b> (<b>Finance Manager</b>)."
                ) % self.env.user.name
            )

        self._close_group_activities()

        return True

    # =========================
    # STOCK RECLASSIFICATION
    # =========================


    def approve_action(self):
        StockQuant = self.env["stock.quant"].sudo()
        StockLot = self.env["stock.lot"].sudo()

        for rec in self:
            if not rec.sku_source_product:
                raise UserError("Please select a source product.")

            if not rec.sku_target_product:
                raise UserError("Please select a target product.")

            if not rec.quantity or rec.quantity <= 0:
                raise UserError("Please select Quantity.")

            source_variants = rec.sku_source_product.product_variant_ids
            target_product = (
                rec.sku_target_product.product_variant_id 
                if hasattr(rec.sku_target_product, 'product_variant_id') and rec.sku_target_product.product_variant_id 
                else rec.sku_target_product
            )

            # টার্গেট প্রোডাক্টের Tracking 'lot' সেট আছে কিনা নিশ্চিত করুন
            if target_product.tracking == 'none':
                target_product.sudo().write({'tracking': 'lot'})
            
            
            source_quants = self.env["stock.quant"].search(
                [
                    ("product_id", "in", source_variants.ids),
                    ("company_id", "=", self.env.company.id),
                    ("quantity", ">", 0),
                ]
            )

            if not source_quants:
                raise UserError("No stock found for source product.")

            # রিজার্ভ হিসাব না করে মোট Quantity যোগ করা
            available_qty = sum(source_quants.mapped("quantity"))

            if rec.quantity > available_qty:
                raise UserError("The requested quantity exceeds the total stock.")
            
            
            lot_name = (rec.target_lot_numbers or "").strip()

            if not lot_name:
                raise UserError("Please enter the Target Lot Number.")

            target_lot = StockLot.search([
                ("name", "=", lot_name),
                ("product_id", "=", target_product.id),
                ("company_id", "=", self.env.company.id),
            ], limit=1)

            if not target_lot:
                target_lot = StockLot.create({
                    "name": lot_name,
                    "product_id": target_product.id,
                    "company_id": self.env.company.id,
                })
            

            remaining_qty = rec.quantity

            for quant in source_quants:
                if remaining_qty <= 0:
                    break

                move_qty = min(quant.available_quantity, remaining_qty)

                if move_qty <= 0:
                    continue

                # ১. Cost Price সিঙ্ক
                if quant.product_id.standard_price:
                    target_product.sudo().standard_price = quant.product_id.standard_price


                # ৪. Source Quant থেকে কমানো
                StockQuant._update_available_quantity(
                    quant.product_id,
                    quant.location_id,
                    -move_qty,
                    lot_id=quant.lot_id,
                    package_id=quant.package_id,
                    owner_id=quant.owner_id,
                )

                # ৫. Target Quant-এ বাড়ানো (নতুন target_lot সহ)
                StockQuant._update_available_quantity(
                    target_product,
                    quant.location_id,
                    move_qty,
                    lot_id=target_lot,  # নিশ্চিত হয়ে target_lot পাস করা হচ্ছে
                    package_id=quant.package_id,
                    owner_id=quant.owner_id,
                )

                remaining_qty -= move_qty

            if remaining_qty > 0:
                raise UserError("Not enough available quantity to reclassify.")

        return True
    

    # =========================
    # ACCOUNTING RECLASSIFICATION
    # =========================

    def action_create_reclassification_journal(self):
        AccountMove = self.env["account.move"].sudo()

        for rec in self:
            source_product = rec.sku_source_product.product_variant_id
            target_product = rec.sku_target_product.product_variant_id

            if not source_product:
                raise UserError("Source product not found.")

            if not target_product:
                raise UserError("Target product not found.")

            if not rec.quantity or rec.quantity <= 0:
                raise UserError("Quantity must be greater than zero.")

            applicable_unit_value = source_product.standard_price
            total_transfer_value = rec.quantity * applicable_unit_value

            if total_transfer_value <= 0:
                raise UserError("Transfer value must be greater than zero.")

            source_account = source_product.categ_id.property_stock_valuation_account_id

            if not source_account:
                raise UserError("Source product stock valuation account missing.")

            target_account = (
                target_product.categ_id.property_stock_valuation_account_id
                or source_account
            )

            journal = False

            if "property_stock_journal" in source_product.categ_id._fields:
                journal = source_product.categ_id.property_stock_journal

            if not journal:
                journal = self.env["account.journal"].sudo().search([
                    ("type", "=", "general"),
                    ("company_id", "=", self.env.company.id),
                ], limit=1)

            if not journal:
                raise UserError("No journal found.")

            move = AccountMove.create({
                "move_type": "entry",
                "journal_id": journal.id,
                "date": fields.Date.context_today(rec),
                "ref": "SKU Reclassification: %s -> %s" % (
                    source_product.display_name,
                    target_product.display_name,
                ),
                "line_ids": [
                    (0, 0, {
                        "name": "SKU Reclassification In: %s | Qty: %s | Unit Value: %s" % (
                            target_product.display_name,
                            rec.quantity,
                            applicable_unit_value,
                        ),
                        "account_id": target_account.id,
                        "product_id": target_product.id,
                        "quantity": rec.quantity,
                        "debit": total_transfer_value,
                        "credit": 0.0,
                    }),
                    (0, 0, {
                        "name": "SKU Reclassification Out: %s | Qty: %s | Unit Value: %s" % (
                            source_product.display_name,
                            rec.quantity,
                            applicable_unit_value,
                        ),
                        "account_id": source_account.id,
                        "product_id": source_product.id,
                        "quantity": rec.quantity,
                        "debit": 0.0,
                        "credit": total_transfer_value,
                    }),
                ],
            })

            move.action_post()
            rec.reclassification_journal_id = move.id

            rec.message_post(
                body=Markup(
                    "SKU Reclassification Journal Created:<br/>"
                    "Source Product: <b>%s</b><br/>"
                    "Target Product: <b>%s</b><br/>"
                    "Quantity: <b>%s</b><br/>"
                    "Unit Value: <b>%s</b><br/>"
                    "Total Transfer Value: <b>%s</b>"
                ) % (
                    source_product.display_name,
                    target_product.display_name,
                    rec.quantity,
                    applicable_unit_value,
                    total_transfer_value,
                )
            )

        return True
