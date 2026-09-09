from odoo import fields, models


class NomineeForm(models.Model):
    _name = "compliance.nominee.form"
    _description = "Nominee Form"
    _order = "id desc"

    # Employee Information
    employee_id = fields.Many2one(
        "hr.employee",
        string="কর্মকর্তা/কর্মচারীর নাম",
    )

    job_id = fields.Many2one(
        "hr.job",
        string="পদবী",
        related="employee_id.job_id",
        readonly=True,
    )

    joining_date = fields.Date(
        string="যোগদানের তারিখ",
        related="employee_id.contract_date_start",
        readonly=True,
    )

    form_date = fields.Date(
        string="তারিখ",
    )

    salary_account_no = fields.Char(
        string="বেতনের হিসাব নং",
    )

    total_children = fields.Integer(
        string="সন্তান সংখ্যা",
    )

    daughter_count = fields.Integer(
        string="মেয়ে",
    )

    son_count = fields.Integer(
        string="ছেলে",
    )

    # Nominee A
    nominee_a_name = fields.Char(
        string="নোমিনি (ক) নাম",
    )

    nominee_a_age = fields.Char(
        string="নোমিনি (ক) বয়স",
    )

    nominee_a_relation = fields.Char(
        string="নোমিনি (ক) সম্পর্ক",
    )

    nominee_a_address = fields.Char(
        string="নোমিনি (ক) স্থায়ী ঠিকানা",
    )

    nominee_a_percentage = fields.Float(
        string="নোমিনি (ক) অর্থপ্রাপ্তির শতকরা হার",
    )

    # Nominee B
    nominee_b_name = fields.Char(
        string="নোমিনি (খ) নাম",
    )

    nominee_b_age = fields.Char(
        string="নোমিনি (খ) বয়স",
    )

    nominee_b_relation = fields.Char(
        string="নোমিনি (খ) সম্পর্ক",
    )

    nominee_b_address = fields.Char(
        string="নোমিনি (খ) স্থায়ী ঠিকানা",
    )

    nominee_b_percentage = fields.Float(
        string="নোমিনি (খ) অর্থপ্রাপ্তির শতকরা হার",
    )

    # Only Image Field
    nominee_photo = fields.Image(
        string="নোমিনি ছবি",
        max_width=1024,
        max_height=1024,
    )

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_nominee_form"
        ).report_action(self)