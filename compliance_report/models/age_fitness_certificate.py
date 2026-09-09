from datetime import date

from odoo import api, fields, models


class AgeFitnessCertificate(models.Model):
    _name = "compliance.age.fitness.certificate"
    _description = "Age and Fitness Certificate"
    _order = "id desc"

    # Employee
    employee_id = fields.Many2one(
        "hr.employee",
        string="নাম",
    )

    gender = fields.Selection(
        [
            ("male", "পুরুষ"),
            ("female", "মহিলা"),
            ("other", "অন্যান্য"),
        ],
        string="লিঙ্গ",
    )

    birthday = fields.Date(
        related="employee_id.birthday",
        string="জন্ম তারিখ",
        readonly=True,
    )

    age = fields.Integer(
        string="বয়স",
        compute="_compute_age",
    )

    # Manual Information
    serial_no = fields.Char(
        string="সিরিয়াল নং",
    )

    certificate_date = fields.Date(
        string="তারিখ",
    )

    father_name = fields.Char(
        string="বাবার নাম",
    )

    mother_name = fields.Char(
        string="মায়ের নাম",
    )

    physical_fitness = fields.Char(
        string="শারীরিক সুস্থতা",
    )

    identification_mark = fields.Char(
        string="সনাক্তকরণ চিহ্ন",
    )

    # Addresses
    permanent_address = fields.Char(
        string="স্থায়ী ঠিকানা",
        compute="_compute_permanent_address",
    )

    present_address = fields.Char(
        string="বর্তমান ঠিকানা / মেইলিং ঠিকানা",
        compute="_compute_present_address",
    )

    # ---------------------------------------------------------
    # Age
    # ---------------------------------------------------------

    @api.depends("birthday")
    def _compute_age(self):
        today = fields.Date.today()

        for record in self:
            if not record.birthday:
                record.age = 0
                continue

            birthday = record.birthday

            record.age = (
                today.year
                - birthday.year
                - (
                    (today.month, today.day)
                    < (birthday.month, birthday.day)
                )
            )

    # ---------------------------------------------------------
    # Permanent Address = Private Address
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
                part for part in parts if part
            )

    # ---------------------------------------------------------
    # Present Address = Work Address
    # ---------------------------------------------------------

    @api.depends(
        "employee_id.address_id",
        "employee_id.address_id.street",
        "employee_id.address_id.street2",
        "employee_id.address_id.city",
        "employee_id.address_id.state_id",
        "employee_id.address_id.zip",
        "employee_id.address_id.country_id",
    )
    def _compute_present_address(self):
        for record in self:
            work_address = record.employee_id.address_id

            if not work_address:
                record.present_address = False
                continue

            parts = [
                work_address.street,
                work_address.street2,
                work_address.city,
                work_address.state_id.name,
                work_address.zip,
                work_address.country_id.name,
            ]

            record.present_address = ", ".join(
                part for part in parts if part
            )

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_age_fitness_certificate"
        ).report_action(self)