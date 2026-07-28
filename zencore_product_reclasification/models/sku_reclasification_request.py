from odoo import models, api, fields
from markupsafe import Markup
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SkuReclasificationRequest(models.Model):
    _name = "sku.reclassification.request"
    _description = "SKU Reclassification Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    sku_source_product = fields.Many2one('product.template', string="Sku Source Product", tracking=True)
    sku_target_product = fields.Many2one('product.template', string="Sku Target Product", tracking=True)
    quantity = fields.Integer(string="quantity changes")
    # state = fields.Selection(selection=[("new", "New"),("pending", "Pending"),("complete", "Complete"),], string="Status", default="new", tracking=True)
    
    
    def approve_action(self):
        StockQuant = self.env["stock.quant"].sudo()

        for rec in self:
            if not rec.sku_source_product:
                raise UserError("Please select a source product.")

            if not rec.sku_target_product:
                raise UserError("Please select a target product.")

            if not rec.quantity or rec.quantity <= 0:
                raise UserError("Please select Quantity.")

            source_variants = rec.sku_source_product.product_variant_ids
            target_product = rec.sku_target_product.product_variant_id

            if rec.quantity > rec.sku_source_product.qty_available:
                raise UserError("The requested quantity exceeds the available stock.")

            source_quants = StockQuant.search([
                ("product_id", "in", source_variants.ids),
                ("location_id.usage", "=", "internal"),
                ("company_id", "=", self.env.company.id),
                ("quantity", ">", 0),
            ])

            if not source_quants:
                raise UserError("No internal stock found for source product.")

            remaining_qty = rec.quantity

            for quant in source_quants:
                if remaining_qty <= 0:
                    break

                move_qty = min(quant.quantity, remaining_qty)

                StockQuant._update_available_quantity(
                    quant.product_id,
                    quant.location_id,
                    -move_qty,
                    lot_id=quant.lot_id,
                    package_id=quant.package_id,
                    owner_id=quant.owner_id,
                )

                StockQuant._update_available_quantity(
                    target_product,
                    quant.location_id,
                    move_qty,
                )

                remaining_qty -= move_qty

            if remaining_qty > 0:
                raise UserError("Not enough available quantity to reclassify.")

        return True
    
    
    
    
    
    # def action_jurnal(self):
    #     for rec in self:
    #         product = rec.sku_source_product.product_variant_id
            
    #         moves = self.env["stock.move"].search([
    #             ("product_id", "=", product.id),
    #             ("state", "=", "done"),
    #         ])
            
            
            
    #         for move in moves:
    #             for valuation in move.stock_valuation_layer_ids:
    #                 print(valuation.account_move_id.name)
                    
    #                 account_move = valuation.account_move_id

    #                 print(account_move.name)
    #                 print(account_move.date)
    #                 print(account_move.ref)
    #                 print(account_move.journal_id.name)
                    
                    
    #                 for line in account_move.line_ids:
    #                     print("Account :", line.account_id.name)
    #                     print("Debit   :", line.debit)
    #                     print("Credit  :", line.credit)
    
    
    
    def action_manufacturing_journal(self):
        for rec in self:
            product = rec.sku_source_product.product_variant_id

            productions = self.env["mrp.production"].search([
                ("product_id", "=", product.id),
                ("state", "=", "done"),
            ])

            if not productions:
                raise UserError("No completed Manufacturing Order found.")

            for production in productions:
                print("=" * 60)
                print("MO:", production.name)

                finished_moves = production.move_finished_ids.filtered(
                    lambda move: move.product_id == product
                )

                refs = set()
                refs.add(production.name)

                for move in finished_moves:
                    refs.add(move.display_name)

                    if "reference" in move._fields and move.reference:
                        refs.add(move.reference)

                    if "origin" in move._fields and move.origin:
                        refs.add(move.origin)

                    if "description_picking" in move._fields and move.description_picking:
                        refs.add(move.description_picking)

                account_moves = self.env["account.move"]

                for ref in refs:
                    moves = self.env["account.move"].search([
                        ("state", "=", "posted"),
                        "|",
                        ("ref", "ilike", ref),
                        ("line_ids.name", "ilike", ref),
                    ])
                    account_moves |= moves

                if not account_moves:
                    print("No Journal Entries found for:", production.name)
                    print("=" * 60)
                    continue

                for account_move in account_moves:
                    print("Journal Entry:", account_move.name)
                    print("Journal:", account_move.journal_id.name)
                    print("Date:", account_move.date)
                    print("Reference:", account_move.ref)

                    print("----- Journal Lines -----")

                    for line in account_move.line_ids:
                        print(
                            line.account_id.display_name,
                            "Debit:", line.debit,
                            "Credit:", line.credit,
                        )

                    print("=" * 60)

        return True
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # # work for storekeeper group
    # def storekeeper_action(self):   
    #     factory_manager_group = self.env.ref("zencore_product_reclasification.factory_manager_group")
    #     factory_managers = factory_manager_group.all_user_ids
        
    #     for rec in self:
    #         rec.state = "pending"
            
    #         for user in factory_managers:
    #             rec.activity_schedule(
    #                 "mail.mail_activity_data_todo",
    #                 user_id=user.id,
    #                 summary=("SKU Reclassification Approval"),
    #                 note=(
    #                     "Please review the SKU reclassification request "
    #                     "from %s to %s."
    #                 ) % (
    #                     rec.sku_source_product.display_name,
    #                     rec.sku_target_product.display_name,
    #                 ),
    #                 date_deadline=fields.Date.today(),
    #             )
                
    #         rec.message_post(
    #             body=Markup(
    #                 "The SKU Reclassification Request was submitted by "
    #                 "<b>%s</b> (<b>Storekeeper</b>) and is awaiting "
    #                 "Factory Manager approval."
    #             ) % self.env.user.name
    #         )
            
    #     return True
    
    
    
    
    
    # # work for factory manager group
    # def factory_manager_action(self):
    #     factory_manager_group = self.env.ref(
    #         "zencore_product_reclasification.factory_manager_group"
    #     )

    #     sales_manager_group = self.env.ref(
    #         "zencore_product_reclasification.sales_manager_group"
    #     )

    #     sales_managers = sales_manager_group.all_user_ids

    #     todo_activity_type = self.env.ref(
    #         "mail.mail_activity_data_todo"
    #     )

    #     for rec in self:
    #         factory_activities = rec.activity_ids.filtered(
    #             lambda activity:
    #                 activity.active
    #                 and activity.activity_type_id == todo_activity_type
    #                 and activity.user_id in factory_manager_group.all_user_ids
    #                 and activity.summary ==("SKU Reclassification Approval")
    #         )

    #         # যে Factory Manager approve করেছে তার activity
    #         current_user_activity = factory_activities.filtered(
    #             lambda activity: activity.user_id == self.env.user
    #         )

    #         if current_user_activity:
    #             current_user_activity.action_feedback(
    #                 feedback=(
    #                     "SKU Reclassification Request approved by %s "
    #                     "(Factory Manager)."
    #                 ) % self.env.user.name
    #             )

    #         # অন্য Factory Manager-দের pending activity remove
    #         remaining_activities = (
    #             factory_activities - current_user_activity
    #         )

    #         if remaining_activities:
    #             remaining_activities.action_cancel()

    #         # Sales Manager-দের নতুন activity
    #         for user in sales_managers:
    #             rec.activity_schedule(
    #                 "mail.mail_activity_data_todo",
    #                 user_id=user.id,
    #                 summary=("SKU Reclassification Sales Approval"),
    #                 note=(
    #                     "Please review the SKU Reclassification Request."
    #                 ),
    #                 date_deadline=fields.Date.context_today(rec),
    #             )

    #     return True
    
    
    
    
    # def sales_manager_action(self):

    #     sales_manager_group = self.env.ref(
    #         "zencore_product_reclasification.sales_manager_group"
    #     )

    #     finance_manager_group = self.env.ref(
    #         "zencore_product_reclasification.finance_manager_group"
    #     )

    #     todo_activity_type = self.env.ref(
    #         "mail.mail_activity_data_todo"
    #     )

    #     finance_managers = finance_manager_group.all_user_ids


    #     for rec in self:
    #         # এই request-এর Sales Manager approval activities
    #         sales_activities = rec.activity_ids.filtered(
    #             lambda activity:
    #                 activity.active
    #                 and activity.activity_type_id == todo_activity_type
    #                 and activity.user_id in sales_manager_group.all_user_ids
    #                 and activity.summary
    #                 ==("SKU Reclassification Sales Approval")
    #         )

    #         # যে Sales Manager approve করেছে তার activity
    #         current_user_activity = sales_activities.filtered(
    #             lambda activity:
    #                 activity.user_id == self.env.user
    #         )


    #         # অন্য Sales Manager-দের activity
    #         remaining_activities = (
    #             sales_activities - current_user_activity
    #         )

    #         # Current Sales Manager-এর activity Done + feedback
    #         current_user_activity.action_feedback(
    #             feedback=(
    #                 "SKU Reclassification Request approved by %s "
    #                 "(Sales Manager)."
    #             ) % self.env.user.name
    #         )

    #         # অন্য Sales Manager-দের activity cancel
    #         if remaining_activities:
    #             remaining_activities.action_cancel()

    #         # Finance Manager-দের নতুন activity
    #         for user in finance_managers:
    #             rec.activity_schedule(
    #                 "mail.mail_activity_data_todo",
    #                 user_id=user.id,
    #                 summary=(
    #                     "SKU Reclassification Finance Approval"
    #                 ),
    #                 note=(
    #                     "Please review the SKU Reclassification Request "
    #                     "from %s to %s."
    #                 ) % (
    #                     rec.sku_source_product.display_name,
    #                     rec.sku_target_product.display_name,
    #                 ),
    #                 date_deadline=fields.Date.context_today(rec),
    #             )

    #         # Chatter history
    #         rec.message_post(
    #             body=Markup(
    #                 (
    #                     "The SKU Reclassification Request was approved by "
    #                     "<b>%s</b> (<b>Sales Manager</b>) and is now "
    #                     "awaiting Finance Manager approval."
    #                 )
    #             ) % self.env.user.name
    #         )

    #     return True
    
    
    
    
    # def finance_manager_action(self):

    #     finance_manager_group = self.env.ref(
    #         "zencore_product_reclasification.finance_manager_group"
    #     )

    #     todo_activity_type = self.env.ref(
    #         "mail.mail_activity_data_todo"
    #     )

    #     for rec in self:
    #         # এই request-এর Finance Manager activities খুঁজে বের করা
    #         finance_activities = rec.activity_ids.filtered(
    #             lambda activity:
    #                 activity.active
    #                 and activity.activity_type_id == todo_activity_type
    #                 and activity.user_id
    #                 in finance_manager_group.all_user_ids
    #                 and activity.summary
    #                 ==("SKU Reclassification Finance Approval")
    #         )

    #         # বর্তমানে approve করা Finance Manager-এর activity
    #         current_user_activity = finance_activities.filtered(
    #             lambda activity:
    #                 activity.user_id == self.env.user
    #         )

    #         # অন্য Finance Manager-দের pending activities
    #         remaining_activities = (
    #             finance_activities - current_user_activity
    #         )

    #         # Current Finance Manager-এর activity Done + feedback
    #         current_user_activity.action_feedback(
    #             feedback=(
    #                 "SKU Reclassification Request approved by %s "
    #                 "(Finance Manager)."
    #             ) % self.env.user.name
    #         )

    #         # অন্য Finance Manager-দের activities cancel
    #         if remaining_activities:
    #             remaining_activities.action_cancel()

    #         # Chatter history
    #         rec.message_post(
    #             body=Markup(
    #                 (
    #                     "The SKU Reclassification Request received final "
    #                     "approval from <b>%s</b> "
    #                     "(<b>Finance Manager</b>)."
    #                 )
    #             ) % self.env.user.name
    #         )
            
            
    #         # other work
    #         source_name = rec.sku_source_product.name
    #         target_name = rec.sku_target_product.name

    #         rec.sku_source_product.write({
    #             "name": target_name,
    #         })

    #         rec.sku_target_product.write({
    #             "name": source_name,
    #         })

    #     return True
    