from odoo import models, api, fields
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    total_value = fields.Float(string="Total Value")
    true_after_request = fields.Boolean(default=False)
    first_tiem = fields.Boolean(default=False)
    
    
    def button_validate(self):
        for rec in self:
            
            total = sum(rec.move_ids.mapped('product_uom_qty'))
            quantity = sum(rec.move_ids.mapped('quantity'))
            percentage = ((total - quantity)/total)*100
            
            if total == 0:
                continue
            
            if percentage > 0.4 and self.first_tiem == False:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'RD Approval',
                    'res_model': 'group.approval',  # TransientModel
                    'view_mode': 'form',
                    'target': 'new',  # popup এ খুলবে
                    'context': {'default_picking_id': rec.id}
                }
            
            
        return super().button_validate()
    
    def action_discrepency(self):
        for rec in self:
            rec.sudo().write({'true_after_request': False, 'first_tiem': True})
    
    
class GroupApproval(models.TransientModel):
    _name = 'group.approval'
    
    req = fields.Boolean(string="Request")
    picking_id = fields.Many2one('stock.picking', string="Receipt")
    
    
    
    def action_request(self):
        for rec in self:   
            rec.picking_id.sudo().write({'true_after_request': True})
            
            users = self.env['res.users'].search([('active', '=', True)])
            
            for user in users:
                if user.has_group('product_receipt_validation.procurement_officer_group'):
                    print('Scheduling for user:', user.name)
                    try:
                        rec.picking_id.activity_schedule(
                            'mail.mail_activity_data_todo',
                            user_id=user.id,
                            note='Receipt validation approval required!',
                            summary='Approval Required',
                        )
                        print('Activity scheduled successfully!')
                    except Exception as e:
                        print('Error:', e)
        
        return {'type': 'ir.actions.act_window_close'}