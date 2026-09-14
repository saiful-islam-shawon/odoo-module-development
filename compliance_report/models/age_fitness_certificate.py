from odoo import api, fields, models


class AgeFitnessCertificate(models.Model):
    _name = "compliance.age.fitness.certificate"
    _description = "Age and Fitness Certificate"
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

    gender = fields.Selection(
        related="employee_id.sex",
        string="লিঙ্গ",
        readonly=True,
    )

    birthday = fields.Date(
        related="employee_id.birthday",
        string="জন্ম তারিখ",
        readonly=True,
    )

    father_name = fields.Char(
        string="বাবার নাম",
        related="employee_id.father_name",
        readonly=True,
    )

    mother_name = fields.Char(
        string="মায়ের নাম",
        related="employee_id.mother_name",
        readonly=True,
    )

    present_address = fields.Text(
        string="বর্তমান ঠিকানা / মেইলিং ঠিকানা",
        related="employee_id.present_address",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Age
    # ---------------------------------------------------------

    age = fields.Integer(
        string="বয়স",
        compute="_compute_age",
    )

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
    # Manual Certificate Information
    # ---------------------------------------------------------

    serial_no = fields.Char(
        string="সিরিয়াল নং",
        related="employee_id.barcode",
        readonly=True,
    )

    certificate_date = fields.Date(
        string="তারিখ",
        related="employee_id.fitness_certificate_date",
        readonly=True,
    )

    physical_fitness = fields.Char(
        string="শারীরিক সুস্থতা",
        related="employee_id.physical_fitness",
        readonly=True,
    )

    identification_mark = fields.Char(
        string="সনাক্তকরণ চিহ্ন",
        related="employee_id.identification_mark",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Print
    # ---------------------------------------------------------

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_age_fitness_certificate"
        ).report_action(self)