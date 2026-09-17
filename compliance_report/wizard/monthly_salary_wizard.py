from datetime import date

from odoo import fields, models


class ComplianceMonthlySalaryWizard(models.TransientModel):
    _name = "compliance.monthly.salary.wizard"
    _description = "Monthly Salary Report Wizard"

    # ---------------------------------------------------------
    # Period
    # ---------------------------------------------------------

    month = fields.Selection(
        selection=[
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        string="Month",
        required=True,
        default=lambda self: str(date.today().month),
    )

    year = fields.Integer(
        string="Year",
        required=True,
        default=lambda self: date.today().year,
    )

    # ---------------------------------------------------------
    # Employees
    # ---------------------------------------------------------

    employee_ids = fields.Many2many(
        "hr.employee",
        string="Employees",
        readonly=True,
    )

    line_ids = fields.One2many(
        "compliance.monthly.salary.wizard.line",
        "wizard_id",
        string="Salary Information",
    )

    # ---------------------------------------------------------
    # Prepare Preview Lines
    # ---------------------------------------------------------

    def _prepare_lines(self):
        self.ensure_one()

        self.line_ids = [(5, 0, 0)]

        lines = []

        for employee in self.employee_ids:
            lines.append(
                (
                    0,
                    0,
                    {
                        "employee_id": employee.id,
                    },
                )
            )

        self.line_ids = lines

    # ---------------------------------------------------------
    # Print
    #
    # IMPORTANT:
    # We print THIS wizard record, not hr.employee.
    # Therefore QWeb receives:
    # docs = compliance.monthly.salary.wizard
    # ---------------------------------------------------------

    def action_print_report(self):
        self.ensure_one()

        return self.env.ref(
            "compliance_report.action_report_monthly_salary"
        ).report_action(self)


class ComplianceMonthlySalaryWizardLine(models.TransientModel):
    _name = "compliance.monthly.salary.wizard.line"
    _description = "Monthly Salary Report Preview Line"
    _order = "id"

    wizard_id = fields.Many2one(
        "compliance.monthly.salary.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        readonly=True,
    )

    # ---------------------------------------------------------
    # Employee
    # ---------------------------------------------------------

    employee_code = fields.Char(
        string="Emp. ID",
        related="employee_id.barcode",
        readonly=True,
    )

    employee_name = fields.Char(
        string="Name",
        related="employee_id.name",
        readonly=True,
    )

    job_id = fields.Many2one(
        "hr.job",
        string="Designation",
        related="employee_id.job_id",
        readonly=True,
    )

    grade = fields.Char(
        string="Grade",
        related="employee_id.compliance_grade",
        readonly=True,
    )

    joining_date = fields.Date(
        string="Joining Date",
        related="employee_id.joining_date",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Attendance
    # ---------------------------------------------------------

    present_days = fields.Integer(
        string="Pr. Days",
        related="employee_id.present_days",
        readonly=True,
    )

    weekly_holiday = fields.Integer(
        string="WD",
        related="employee_id.weekly_holiday",
        readonly=True,
    )

    general_holiday = fields.Integer(
        string="G.H",
        related="employee_id.general_holiday",
        readonly=True,
    )

    earned_leave = fields.Integer(
        string="EL",
        related="employee_id.earned_leave",
        readonly=True,
    )

    casual_leave = fields.Integer(
        string="CL",
        related="employee_id.casual_leave",
        readonly=True,
    )

    sick_leave = fields.Integer(
        string="SL",
        related="employee_id.sick_leave",
        readonly=True,
    )

    maternity_leave = fields.Integer(
        string="ML",
        related="employee_id.maternity_leave",
        readonly=True,
    )

    absent_days = fields.Integer(
        string="Absent Days",
        related="employee_id.absent_days",
        readonly=True,
    )

    total_payable_days = fields.Integer(
        string="Total Payable Days",
        related="employee_id.total_payable_days",
        readonly=True,
    )

    # ---------------------------------------------------------
    # Salary
    # ---------------------------------------------------------

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="employee_id.currency_id",
        readonly=True,
    )

    basic = fields.Monetary(
        string="Basic",
        related="employee_id.basic",
        currency_field="currency_id",
        readonly=True,
    )

    house_rent = fields.Monetary(
        string="House Rent",
        related="employee_id.compliance_house_rent",
        currency_field="currency_id",
        readonly=True,
    )

    medical_allowance = fields.Monetary(
        string="Medical Allowance",
        related="employee_id.medical_allowance",
        currency_field="currency_id",
        readonly=True,
    )

    conveyance_allowance = fields.Monetary(
        string="Conveyance Allowance",
        related="employee_id.transport_allowance",
        currency_field="currency_id",
        readonly=True,
    )

    food_allowance = fields.Monetary(
        string="Food Allowance",
        related="employee_id.food_allowance",
        currency_field="currency_id",
        readonly=True,
    )

    gross_salary = fields.Monetary(
        string="Gross Salary",
        related="employee_id.gro",
        currency_field="currency_id",
        readonly=True,
    )

    attendance_bonus = fields.Monetary(
        string="Attendance Bonus",
        related="employee_id.attendance_bonus",
        currency_field="currency_id",
        readonly=True,
    )

    earn_salary = fields.Monetary(
        string="Earn Salary",
        related="employee_id.earn_salary",
        currency_field="currency_id",
        readonly=True,
    )

    absent_amount = fields.Monetary(
        string="Absent Amount",
        related="employee_id.absent_amount",
        currency_field="currency_id",
        readonly=True,
    )

    tax = fields.Monetary(
        string="Tax Amount",
        related="employee_id.tax",
        currency_field="currency_id",
        readonly=True,
    )

    stamp_charge = fields.Monetary(
        string="Stamp",
        related="employee_id.stamp_charge",
        currency_field="currency_id",
        readonly=True,
    )

    net_salary = fields.Monetary(
        string="Net Salary",
        related="employee_id.net_salary",
        currency_field="currency_id",
        readonly=True,
    )