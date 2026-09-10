from odoo import api, fields, models


class JobApplication(models.Model):
    _name = "compliance.job.application"
    _description = "Job Application"
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

    father_name = fields.Char(
        string="পিতার নাম",
        related="employee_id.father_name",
        readonly=True,
    )

    mother_name = fields.Char(
        string="মাতার নাম",
        related="employee_id.mother_name",
        readonly=True,
    )

    present_address = fields.Text(
        string="বর্তমান ঠিকানা",
        related="employee_id.present_address",
        readonly=True,
    )

    experience = fields.Char(
        string="অভিজ্ঞতা",
        related="employee_id.experience",
        readonly=True,
    )

    mobile = fields.Char(
        string="মোবাইল নং",
        related="employee_id.mobile_phone",
        readonly=True,
    )

    email = fields.Char(
        string="ইমেইল",
        related="employee_id.work_email",
        readonly=True,
    )

    job_position = fields.Char(
        string="আবেদনের পদের নাম",
        related="employee_id.department_id.name",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Permanent Address
    # Employee Private Address
    # ---------------------------------------------------------

    permanent_address = fields.Char(
        string="স্থায়ী ঠিকানা",
        compute="_compute_permanent_address",
    )

    @api.depends(
        "employee_id.private_street",
        "employee_id.private_street2",
        "employee_id.private_city",
        "employee_id.private_state_id",
        "employee_id.private_zip",
        "employee_id.private_country_id",
    )
    def _compute_permanent_address(self):
        for record in self:

            employee = record.employee_id

            if not employee:
                record.permanent_address = False
                continue

            address_parts = [
                employee.private_street,
                employee.private_street2,
                employee.private_city,
                employee.private_state_id.name,
                employee.private_zip,
                employee.private_country_id.name,
            ]

            record.permanent_address = ", ".join(
                part for part in address_parts if part
            )

    # ---------------------------------------------------------
    # Manual Job Application Information
    # ---------------------------------------------------------

    education_1 = fields.Char(
        string="শিক্ষাগত যোগ্যতা ১",
    )

    education_2 = fields.Char(
        string="শিক্ষাগত যোগ্যতা ২",
    )

    previous_company = fields.Char(
        string="কোম্পানির নাম",
    )

    previous_job_position = fields.Char(
        string="পদের নাম",
    )

    employment_duration = fields.Char(
        string="সময়কাল",
    )

    application_date = fields.Date(
        string="তারিখ",
        default=fields.Date.context_today,
    )

    # ---------------------------------------------------------
    # Print
    # ---------------------------------------------------------

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_job_application"
        ).report_action(self)