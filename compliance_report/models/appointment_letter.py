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
    )

    mother_name = fields.Char(    
        string="মাতার নাম",
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

    permanent_address = fields.Char(
        string="স্থায়ী ঠিকানা",
        compute="_compute_permanent_address",
    )

    present_address = fields.Char(
        string="বর্তমান ঠিকানা",
        compute="_compute_present_address",
    )

    # ---------------------------------------------------------
    # Appointment Information
    # ---------------------------------------------------------

    letter_date = fields.Date(
        string="নিয়োগপত্রের তারিখ",
    )

    application_date = fields.Date(
        string="আবেদনের তারিখ",
    )

    appointment_date = fields.Date(
        string="কার্যকর হওয়ার তারিখ",
        related="employee_id.contract_date_start",
        readonly=True,
    )

    joining_date = fields.Date(
        string="যোগদানের তারিখ",
    )

    grade = fields.Char(
        string="গ্রেড",
    )

    probation_months = fields.Integer(
        string="শিক্ষানবীশকাল (মাস)",
    )

    extended_probation_months = fields.Integer(
        string="বর্ধিত শিক্ষানবীশকাল (মাস)",
    )

    # ---------------------------------------------------------
    # Salary
    # ---------------------------------------------------------

    basic_wage = fields.Float(
        string="মূল মজুরী",
    )

    house_rent = fields.Float(
        string="বাড়ী ভাড়া",
    )

    medical_allowance = fields.Float(
        string="চিকিৎসা ভাতা",
    )

    conveyance_allowance = fields.Float(
        string="যাতায়াত ভাতা",
    )

    food_allowance = fields.Float(
        string="খাদ্য ভাতা",
    )

    total_wage = fields.Float(
        string="মোট",
        compute="_compute_total_wage",
    )

    total_wage_words = fields.Char(
        string="কথায়",
    )

    # ---------------------------------------------------------
    # Compute
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

            parts = []

            if employee.work_location_id:
                parts.append(employee.work_location_id.name)

            work_address = employee.work_contact_id

            if work_address:
                parts.extend([
                    work_address.street,
                    work_address.street2,
                    work_address.city,
                    work_address.state_id.name,
                    work_address.zip,
                    work_address.country_id.name,
                ])

            record.present_address = ", ".join(
                value for value in parts if value
            )

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

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_appointment_letter"
        ).report_action(self)
        
        