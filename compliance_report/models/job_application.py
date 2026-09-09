from odoo import api, fields, models


class JobApplication(models.Model):
    _name = "compliance.job.application"
    _description = "Job Application"
    _order = "id desc"

    employee_id = fields.Many2one(
        "hr.employee",
        string="নাম",
    )

    father_name = fields.Char(string="পিতার নাম")
    mother_name = fields.Char(string="মাতার নাম")

    permanent_address = fields.Char(
        string="স্থায়ী ঠিকানা",
        compute="_compute_permanent_address",
    )

    present_address = fields.Char(
        string="বর্তমান ঠিকানা",
        compute="_compute_present_address",
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

    education_1 = fields.Char(string="শিক্ষাগত যোগ্যতা ১")
    education_2 = fields.Char(string="শিক্ষাগত যোগ্যতা ২")

    previous_company = fields.Char(string="কোম্পানির নাম")
    previous_job_position = fields.Char(string="পদের নাম")
    employment_duration = fields.Char(string="সময়কাল")
    experience = fields.Char(string="অভিজ্ঞতা")

    application_date = fields.Date(
        string="তারিখ",
        default=fields.Date.context_today,
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

    @api.depends(
        "employee_id.work_location_id",
        "employee_id.work_contact_id",
    )
    def _compute_present_address(self):
        for record in self:
            employee = record.employee_id

            if not employee:
                record.present_address = False
                continue

            address_parts = []

            # Work Location
            if employee.work_location_id:
                address_parts.append(employee.work_location_id.name)

            # Work Address
            work_address = employee.work_contact_id

            if work_address:
                address_parts.extend([
                    work_address.street,
                    work_address.street2,
                    work_address.city,
                    work_address.state_id.name,
                    work_address.zip,
                    work_address.country_id.name,
                ])

            record.present_address = ", ".join(
                part for part in address_parts if part
            )

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_job_application"
        ).report_action(self)