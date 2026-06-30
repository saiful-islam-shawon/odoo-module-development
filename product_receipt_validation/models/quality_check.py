from odoo import fields, models, api

class QualityCheck(models.TransientModel):
    _inherit = 'quality.check.wizard'
    
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
    
    
    
    def _get_qc_values(self):
        return {
            'fiber_characteristics': self.fiber_characteristics,
            'micronaire': self.micronaire,
            'length': self.length,
            'strength': self.strength,
            'uniformity': self.uniformity,
            'trash': self.trash,
            'color_grade': self.color_grade,
            'leaf_grade': self.leaf_grade,
            'crt_tc_no': self.crt_tc_no,
            'moisture': self.moisture,
            'uhml': self.uhml,
            'reflectance': self.reflectance,
            'short_fiber_index': self.short_fiber_index,
            'trash_pct': self.trash_pct,
        }

    def do_pass(self):
        self.current_check_id.write(self._get_qc_values())
        return super().do_pass()

    def do_fail(self):
        self.current_check_id.write(self._get_qc_values())
        return super().do_fail()