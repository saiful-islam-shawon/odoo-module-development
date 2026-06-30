from odoo import models, fields, api

class QcParameter(models.Model):
    _inherit = 'quality.check'
    
    
    fiber_characteristics = fields.Float(string="Fiber Characteristics")
    micronaire = fields.Float(string="Micronaire")
    length = fields.Float(string="Length")
    strength = fields.Float(string="Strength")
    uniformity = fields.Float(string="Uniformity")
    trash = fields.Float(string="Trash (%)")
    color_grade = fields.Char(string="Color Grade")
    leaf_grade = fields.Float(string="Leaf grade")
    crt_tc_no = fields.Char(string="Crt_tc_no")
    moisture = fields.Float(string="Moisture (%)")
    uhml = fields.Float(string="Uhml")
    reflectance = fields.Float(string="Reflectance")
    short_fiber_index = fields.Float(string="Short fibre index")
    trash_pct = fields.Float(string="trash_pct")
    
