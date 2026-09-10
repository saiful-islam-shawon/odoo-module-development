from odoo import api, fields, models


class HrEmployeeNominee(models.Model):
    _name = "hr.employee.nominee"
    _description = "Employee Nominee"
    _order = "id asc"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
    )

    name = fields.Char(
        string="Nominee Name",
    )

    nid = fields.Char(
        string="Nominee NID",
    )

    date_of_birth = fields.Date(
        string="Nominee DOB",
    )

    age = fields.Integer(
        string="Age",
        compute="_compute_age",
    )

    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Nominee Gender",
    )

    relation = fields.Char(
        string="Nominee Relation",
    )

    permanent_address = fields.Text(
        string="Permanent Address",
    )

    share_percentage = fields.Float(
        string="Share Percentage",
    )

    photo = fields.Image(
        string="Nominee Photo",
        max_width=1024,
        max_height=1024,
    )

    document = fields.Binary(
        string="Attach Document",
        attachment=True,
    )

    @api.depends("date_of_birth")
    def _compute_age(self):
        today = fields.Date.today()

        for record in self:
            if not record.date_of_birth:
                record.age = 0
                continue

            dob = record.date_of_birth

            record.age = (
                today.year
                - dob.year
                - (
                    (today.month, today.day)
                    < (dob.month, dob.day)
                )
            )