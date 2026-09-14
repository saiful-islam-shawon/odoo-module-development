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

    application_date = fields.Date(
        string="তারিখ",
        default=fields.Date.context_today,
    )
    
    signature_date = fields.Date(
        string="স্বাক্ষরের তারিখ",
    )
    
    
    # ---------------------------------------------------------
    # education
    # ---------------------------------------------------------
    
    education_ids = fields.Many2many(
        "hr.resume.line",
        string="শিক্ষাগত যোগ্যতা",
        compute="_compute_education_ids",
    )
    
    
    @api.depends("employee_id")
    def _compute_education_ids(self):
        ResumeLine = self.env["hr.resume.line"]
        ResumeType = self.env["hr.resume.line.type"]

        education_type = ResumeType.search(
            [("name", "=", "Education")],
            limit=1,
        )

        for record in self:
            if not record.employee_id or not education_type:
                record.education_ids = False
                continue

            record.education_ids = ResumeLine.search([
                ("employee_id", "=", record.employee_id.id),
                ("line_type_id", "=", education_type.id),
            ])
            
            
    # ---------------------------------------------------------
    # Work Experience
    # ---------------------------------------------------------

    work_experience_ids = fields.Many2many(
        "hr.resume.line",
        string="পূর্ববর্তী কর্মসংস্থান এবং অভিজ্ঞতা",
        compute="_compute_work_experience_ids",
    )


    @api.depends("employee_id")
    def _compute_work_experience_ids(self):
        ResumeLine = self.env["hr.resume.line"]

        work_experience_type = self.env.ref(
            "compliance_report.resume_line_type_work_experience",
            raise_if_not_found=False,
        )

        for record in self:
            if not record.employee_id or not work_experience_type:
                record.work_experience_ids = False
                continue

            record.work_experience_ids = ResumeLine.search([
                ("employee_id", "=", record.employee_id.id),
                ("line_type_id", "=", work_experience_type.id),
            ])



    # ---------------------------------------------------------
    # Print
    # ---------------------------------------------------------

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_job_application"
        ).report_action(self)