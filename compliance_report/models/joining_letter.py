from odoo import fields, models


class JoiningLetter(models.Model):
    _name = "compliance.joining.letter"
    _description = "Joining Letter"
    _order = "id desc"

    # Employee
    employee_id = fields.Many2one(
        "hr.employee",
        string="নাম",
    )

    # Employee Job Position
    job_id = fields.Many2one(
        "hr.job",
        string="পদ",
        related="employee_id.job_id",
        readonly=True,
    )

    # Contract From Date
    contract_date_start = fields.Date(
        string="যোগদানের তারিখ",
        related="employee_id.contract_date_start",
        readonly=True,
    )

    # Employee Mobile
    mobile = fields.Char(
        string="মোবাইল",
        related="employee_id.mobile_phone",
        readonly=True,
    )

    # Employee Email
    email = fields.Char(
        string="ইমেইল",
        related="employee_id.work_email",
        readonly=True,
    )

    # Manual / Optional
    receiver_name = fields.Char(
        string="প্রাপক",
    )

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_joining_letter"
        ).report_action(self)