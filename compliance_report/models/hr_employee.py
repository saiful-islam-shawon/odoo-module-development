from odoo import api, fields, models
from odoo.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # ---------------------------------------------------------
    # Others - Personal Tab
    # ---------------------------------------------------------

    father_name = fields.Char(
        string="Father's Name",
    )

    mother_name = fields.Char(
        string="Mother's Name",
    )

    present_address = fields.Text(
        string="Present Address",
    )

    experience = fields.Char(
        string="Experience",
        help="Example: 3 Years, 5 Years 6 Months",
    )

    employee_signature = fields.Image(
        string="Signature",
        max_width=1024,
        max_height=1024,
    )

    # ---------------------------------------------------------
    # Compliance Information
    # ---------------------------------------------------------

    revision_date = fields.Date(
        string="Revision Date",
    )

    basic = fields.Monetary(
        string="Basic",
        currency_field="currency_id",
        compute="_compute_basic",
        store=True,
    )

    compliance_house_rent = fields.Monetary(
        string="House Rent",
        currency_field="currency_id",
        compute="_compute_house_rent",
        store=True,
    )

    medical_allowance = fields.Monetary(
        string="Medical Allowance",
        currency_field="currency_id",
        default=750.0,
    )

    transport_allowance = fields.Monetary(
        string="Conveyance Allowance",
        currency_field="currency_id",
        default=450.0,
    )

    other_allowance = fields.Monetary(
        string="Other Allowance",
        currency_field="currency_id",
    )

    food_allowance = fields.Monetary(
        string="Food Allowance",
        currency_field="currency_id",
        default=1250.0,
    )
    
    
    @api.depends(
        "gro",
        "medical_allowance",
        "food_allowance",
        "transport_allowance",
    )
    def _compute_basic(self):
        for employee in self:

            if not employee.gro or employee.gro <= 0:
                employee.basic = 0.0
                continue

            remaining_amount = (
                employee.gro
                - (
                    employee.medical_allowance
                    + employee.food_allowance
                    + employee.transport_allowance
                )
            )

            employee.basic = (
                remaining_amount / 3.0
            ) * 2.0
            
    @api.depends(
        "gro",
        "medical_allowance",
        "food_allowance",
        "transport_allowance",
    )
    def _compute_house_rent(self):
        for employee in self:

            if not employee.gro or employee.gro <= 0:
                employee.compliance_house_rent = 0.0
                continue

            remaining_amount = (
                employee.gro
                - (
                    employee.medical_allowance
                    + employee.food_allowance
                    + employee.transport_allowance
                )
            )

            employee.compliance_house_rent = (
                remaining_amount / 3.0
            )

    # ---------------------------------------------------------
    # Gross Salary
    #
    # Basic
    # + House Rent
    # + Medical Allowance
    # + Transport Allowance
    # + Other Allowance
    # + Food Allowance
    # ---------------------------------------------------------

    gro = fields.Monetary(
        string="Gross Salary",
        currency_field="currency_id",
    )

    # ---------------------------------------------------------
    # Salary Deductions
    # ---------------------------------------------------------

    deduction = fields.Monetary(
        string="Deduction",
        currency_field="currency_id",
    )

    tax = fields.Monetary(
        string="Tax",
        currency_field="currency_id",
    )

    stamp_charge = fields.Monetary(
        string="Stamp Charge",
        currency_field="currency_id",
    )

    # ---------------------------------------------------------
    # Net Salary
    #
    # Gross Salary
    # - (Deduction + Tax + Stamp Charge)
    # ---------------------------------------------------------

    net_salary = fields.Monetary(
        string="Net Salary",
        currency_field="currency_id",
        compute="_compute_net_salary",
        store=True,
    )
    
    net_salary_display = fields.Char(
        string="Net Salary",
        compute="_compute_net_salary_display",
    )

    @api.depends(
        "earn_salary",
        "deduction",
        "tax",
        "stamp_charge",
        "absent_amount",
    )
    def _compute_net_salary(self):
        for employee in self:
            net_amount = (
                employee.earn_salary
                - (
                    employee.deduction
                    + employee.tax
                    + employee.stamp_charge
                    + employee.absent_amount
                )
            )

            employee.net_salary = float(
                Decimal(str(net_amount)).quantize(
                    Decimal("1"),
                    rounding=ROUND_HALF_UP,
                )
            )
            
            
    # net salary display
    
    @api.depends(
        "net_salary",
        "currency_id",
    )
    def _compute_net_salary_display(self):
        for employee in self:
            amount = int(employee.net_salary or 0)

            currency_symbol = (
                employee.currency_id.symbol
                if employee.currency_id
                else ""
            )

            formatted_amount = f"{amount:,}"

            if currency_symbol:
                employee.net_salary_display = (
                    f"{currency_symbol} {formatted_amount}"
                )
            else:
                employee.net_salary_display = formatted_amount

    # ---------------------------------------------------------
    # Increment
    # ---------------------------------------------------------

    increment_amount = fields.Monetary(
        string="Increment Amount",
        currency_field="currency_id",
    )

    # ---------------------------------------------------------
    # Nominee Form
    # ---------------------------------------------------------

    nominee_ids = fields.One2many(
        "hr.employee.nominee",
        "employee_id",
        string="Nominee Information",
    )

    # ---------------------------------------------------------
    # Nominee / Personal Information
    # ---------------------------------------------------------

    nominee_form_date = fields.Date(
        string="Date",
        default=fields.Date.context_today,
    )

    salary_account_no = fields.Char(
        string="Salary Account No",
    )

    total_children = fields.Integer(
        string="Total Children",
    )

    daughter_count = fields.Integer(
        string="Daughter",
    )

    son_count = fields.Integer(
        string="Son",
    )

    # ---------------------------------------------------------
    # Appointment Information
    # ---------------------------------------------------------

    appointment_letter_date = fields.Date(
        string="Appointment Letter Date",
    )

    job_application_date = fields.Date(
        string="Job Application Date",
    )

    joining_date = fields.Date(
        string="Joining Date",
    )

    compliance_grade = fields.Char(
        string="Grade",
    )

    probation_months = fields.Integer(
        string="Probation Period (Months)",
    )

    extended_probation_months = fields.Integer(
        string="Extended Probation Period (Months)",
    )

    # ---------------------------------------------------------
    # Age & Fitness Information
    # ---------------------------------------------------------

    fitness_certificate_date = fields.Date(
        string="Certificate Date",
        default=fields.Date.context_today,
    )

    physical_fitness = fields.Char(
        string="Physical Fitness",
    )

    identification_mark = fields.Char(
        string="Identification Mark",
    )
    
    
    # ---------------------------------------------------------
    # Payroll - Others
    # ---------------------------------------------------------

    mobile_bill = fields.Monetary(
        string="Mobile Bill",
        currency_field="currency_id",
    )

    attendance_bonus = fields.Monetary(
        string="Attendance Bonus",
        currency_field="currency_id",
    )
    
    
    
    # ---------------------------------------------------------
    # Compliance Attendance
    # ---------------------------------------------------------

    present_days = fields.Integer(
        string="Pr. Days",
    )

    weekly_holiday = fields.Integer(
        string="WD",
    )

    general_holiday = fields.Integer(
        string="G.H",
    )

    earned_leave = fields.Integer(
        string="EL",
    )

    casual_leave = fields.Integer(
        string="CL",
    )

    sick_leave = fields.Integer(
        string="SL",
    )

    maternity_leave = fields.Integer(
        string="ML",
    )

    absent_days = fields.Integer(
        string="Absent Days",
    )

    total_payable_days = fields.Integer(
        string="Total Payable Days",
        compute="_compute_total_payable_days",
        store=True,
    )

    earn_salary = fields.Monetary(
        string="Earn Salary",
        currency_field="currency_id",
        compute="_compute_earn_salary",
        store=True,
    )

    absent_amount = fields.Monetary(
        string="Absent Amount",
        currency_field="currency_id",
        compute="_compute_absent_amount",
        store=True,
    )
    
    
    # total payable
    @api.depends(
        "present_days",
        "weekly_holiday",
        "general_holiday",
        "earned_leave",
        "casual_leave",
        "sick_leave",
        "maternity_leave",
        "absent_days",
    )
    def _compute_total_payable_days(self):
        for employee in self:
            employee.total_payable_days = (
                employee.present_days
                + employee.weekly_holiday
                + employee.general_holiday
                + employee.earned_leave
                + employee.casual_leave
                + employee.sick_leave
                + employee.maternity_leave
                + employee.absent_days
            )
            
    
    @api.constrains("total_payable_days")
    def _check_total_payable_days(self):
        for employee in self:
            if employee.total_payable_days > 31:
                raise ValidationError(
                    "Total Payable Days cannot be greater than 31 days."
                )
            
            
    
    # absent amount
    @api.depends(
        "basic",
        "absent_days",
    )
    def _compute_absent_amount(self):
        for employee in self:
            employee.absent_amount = (
                (employee.basic / 30.0)
                * employee.absent_days
            )
            
            
    # earn salary
    @api.depends(
        "gro",
        "attendance_bonus",
    )
    def _compute_earn_salary(self):
        for employee in self:
            employee.earn_salary = (
                employee.gro
                + employee.attendance_bonus
            )