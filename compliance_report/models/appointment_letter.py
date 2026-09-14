from odoo import api, fields, models


class AppointmentLetter(models.Model):
    _name = "compliance.appointment.letter"
    _description = "Appointment Letter"
    _order = "id desc"

    # ---------------------------------------------------------
    # Employee
    # ---------------------------------------------------------

    employee_id = fields.Many2one(
        "hr.employee",
        string="নাম",
    )

    father_or_husband_name = fields.Char(
        string="পিতা/স্বামীর নাম",
        related="employee_id.father_name",
        readonly=True,
    )

    mother_name = fields.Char(
        string="মাতার নাম",
        related="employee_id.mother_name",
        readonly=True,
    )

    nid_number = fields.Char(
        string="জাতীয় পরিচয় পত্র নং",
        related="employee_id.identification_id",
        readonly=True,
    )

    employee_code = fields.Char(
        string="আইডি নং",
        related="employee_id.barcode",
        readonly=True,
    )

    department_id = fields.Many2one(
        "hr.department",
        string="বিভাগ",
        related="employee_id.department_id",
        readonly=True,
    )

    job_id = fields.Many2one(
        "hr.job",
        string="পদ",
        related="employee_id.job_id",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Address
    # ---------------------------------------------------------

    permanent_address = fields.Char(
        string="স্থায়ী ঠিকানা",
        compute="_compute_permanent_address",
    )

    present_address = fields.Text(
        string="বর্তমান ঠিকানা",
        related="employee_id.present_address",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Appointment Information - Employee Related
    # ---------------------------------------------------------

    letter_date = fields.Date(
        string="নিয়োগপত্রের তারিখ",
        related="employee_id.appointment_letter_date",
        readonly=True,
    )
    
    signature_date = fields.Date(
        string="স্বাক্ষরের তারিখ",
    )

    application_date = fields.Date(
        string="আবেদনের তারিখ",
        related="employee_id.job_application_date",
        readonly=True,
    )

    appointment_date = fields.Date(
        string="কার্যকর হওয়ার তারিখ",
        related="employee_id.contract_date_start",
        readonly=True,
    )

    joining_date = fields.Date(
        string="যোগদানের তারিখ",
        related="employee_id.joining_date",
        readonly=True,
    )

    grade = fields.Char(
        string="গ্রেড",
        related="employee_id.compliance_grade",
        readonly=True,
    )

    probation_months = fields.Integer(
        string="শিক্ষানবীশকাল (মাস)",
        related="employee_id.probation_months",
        readonly=True,
    )

    extended_probation_months = fields.Integer(
        string="বর্ধিত শিক্ষানবীশকাল (মাস)",
        related="employee_id.extended_probation_months",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Salary - Employee Compliance Information
    # ---------------------------------------------------------

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="employee_id.currency_id",
        readonly=True,
    )

    basic_wage = fields.Monetary(
        string="মূল মজুরী",
        related="employee_id.basic",
        currency_field="currency_id",
        readonly=True,
    )

    house_rent = fields.Monetary(
        string="বাড়ী ভাড়া",
        related="employee_id.compliance_house_rent",
        currency_field="currency_id",
        readonly=True,
    )

    medical_allowance = fields.Monetary(
        string="চিকিৎসা ভাতা",
        related="employee_id.medical_allowance",
        currency_field="currency_id",
        readonly=True,
    )

    conveyance_allowance = fields.Monetary(
        string="যাতায়াত ভাতা",
        related="employee_id.transport_allowance",
        currency_field="currency_id",
        readonly=True,
    )

    food_allowance = fields.Monetary(
        string="খাদ্য ভাতা",
        related="employee_id.food_allowance",
        currency_field="currency_id",
        readonly=True,
    )

    total_wage = fields.Monetary(
        string="মোট",
        compute="_compute_total_wage",
        currency_field="currency_id",
    )

    total_wage_words = fields.Char(
        string="কথায়",
    )

    # ---------------------------------------------------------
    # Permanent Address
    # ---------------------------------------------------------

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

            parts = [
                employee.private_street,
                employee.private_street2,
                employee.private_city,
                employee.private_state_id.name,
                employee.private_zip,
                employee.private_country_id.name,
            ]

            record.permanent_address = ", ".join(
                value for value in parts if value
            )

    # ---------------------------------------------------------
    # Total Wage
    # ---------------------------------------------------------

    @api.depends(
        "basic_wage",
        "house_rent",
        "medical_allowance",
        "conveyance_allowance",
        "food_allowance",
    )
    def _compute_total_wage(self):
        for record in self:
            record.total_wage = (
                record.basic_wage
                + record.house_rent
                + record.medical_allowance
                + record.conveyance_allowance
                + record.food_allowance
            )

    # ---------------------------------------------------------
    # Print
    # ---------------------------------------------------------

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_appointment_letter"
        ).report_action(self)