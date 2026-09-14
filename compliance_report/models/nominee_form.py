from odoo import fields, models


class NomineeForm(models.Model):
    _name = "compliance.nominee.form"
    _description = "Nominee Form"
    _order = "id desc"

    # ---------------------------------------------------------
    # Employee Information
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Employee Related Nominee Information
    # ---------------------------------------------------------

    form_date = fields.Date(
        string="তারিখ",
        related="employee_id.nominee_form_date",
        readonly=True,
    )

    salary_account_no = fields.Char(
        string="বেতনের হিসাব নং",
        related="employee_id.salary_account_no",
        readonly=True,
    )

    total_children = fields.Integer(
        string="সন্তান সংখ্যা",
        related="employee_id.total_children",
        readonly=True,
    )

    daughter_count = fields.Integer(
        string="মেয়ে",
        related="employee_id.daughter_count",
        readonly=True,
    )

    son_count = fields.Integer(
        string="ছেলে",
        related="employee_id.son_count",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Nominees
    # ---------------------------------------------------------

    nominee_ids = fields.One2many(
        related="employee_id.nominee_ids",
        string="Nominee Information",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Print
    # ---------------------------------------------------------

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_nominee_form"
        ).report_action(self)