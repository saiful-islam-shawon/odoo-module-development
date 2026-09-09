from odoo import api, fields, models


class SalaryIncrement(models.Model):
    _name = "compliance.salary.increment"
    _description = "Salary Increment and Revision"
    _order = "id desc"

    # Employee
    employee_id = fields.Many2one(
        "hr.employee",
        string="নাম",
    )

    # Present Address
    present_address = fields.Char(
        string="বর্তমান ঠিকানা",
    )

    # Manual Information
    letter_date = fields.Date(
        string="তারিখ",
    )

    receiver_name = fields.Char(
        string="প্রিয়",
    )

    effective_date = fields.Date(
        string="বেতন বৃদ্ধির কার্যকর তারিখ",
    )

    revised_salary = fields.Float(
        string="সংশোধিত মোট বেতন",
    )

    # Salary Details
    basic_salary = fields.Float(
        string="মূল বেতন",
    )

    house_rent = fields.Float(
        string="বাড়ি ভাড়া",
    )

    others = fields.Float(
        string="অন্যান্য",
    )

    increment_amount = fields.Float(
        string="৫% বৃদ্ধিতে",
    )

    total_salary = fields.Float(
        string="মোট",
        compute="_compute_total_salary",
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

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_salary_increment"
        ).report_action(self)