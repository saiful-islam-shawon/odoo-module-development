from odoo import api, fields, models


class SalaryIncrement(models.Model):
    _name = "compliance.salary.increment"
    _description = "Salary Increment and Revision"
    _order = "id desc"

    # ---------------------------------------------------------
    # Employee
    # ---------------------------------------------------------

    employee_id = fields.Many2one(
        "hr.employee",
        string="নাম",
    )

    # ---------------------------------------------------------
    # Employee Related Information
    # ---------------------------------------------------------

    present_address = fields.Text(
        string="বর্তমান ঠিকানা",
        related="employee_id.present_address",
        readonly=True,
    )

    effective_date = fields.Date(
        string="বেতন বৃদ্ধির কার্যকর তারিখ",
        related="employee_id.revision_date",
        readonly=True,
    )

    revised_salary = fields.Monetary(
        string="সংশোধিত মোট বেতন",
        related="employee_id.gro",
        currency_field="currency_id",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Manual Information
    # ---------------------------------------------------------

    letter_date = fields.Date(
        string="তারিখ",
    )

    receiver_name = fields.Char(
        string="প্রিয়",
    )

    # ---------------------------------------------------------
    # Salary Details
    # ---------------------------------------------------------

    basic_salary = fields.Monetary(
        string="মূল বেতন",
        related="employee_id.basic",
        currency_field="currency_id",
        readonly=True,
    )

    house_rent = fields.Monetary(
        string="বাড়ি ভাড়া",
        related="employee_id.compliance_house_rent",
        currency_field="currency_id",
        readonly=True,
    )

    others = fields.Monetary(
        string="অন্যান্য",
        related="employee_id.other_allowance",
        currency_field="currency_id",
        readonly=True,
    )

    increment_amount = fields.Monetary(
        string="৫% বৃদ্ধিতে",
        related="employee_id.increment_amount",
        currency_field="currency_id",
        readonly=True,
    )

    # Currency for Monetary fields
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="employee_id.currency_id",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Total
    # ---------------------------------------------------------

    total_salary = fields.Monetary(
        string="মোট",
        compute="_compute_total_salary",
        currency_field="currency_id",
    )

    @api.depends(
        "basic_salary",
        "house_rent",
        "others",
        "increment_amount",
    )
    def _compute_total_salary(self):
        for record in self:
            record.total_salary = (
                record.basic_salary
                + record.house_rent
                + record.others
                + record.increment_amount
            )

    # ---------------------------------------------------------
    # Print
    # ---------------------------------------------------------

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_salary_increment"
        ).report_action(self)