from odoo import fields, models


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

    compliance_house_rent = fields.Monetary(
        string="House Rent",
        currency_field="currency_id",
    )

    other_allowance = fields.Monetary(
        string="Other Allowance",
        currency_field="currency_id",
    )

    increment_amount = fields.Monetary(
        string="Increment Amount",
        currency_field="currency_id",
    )
    
    medical_allowance = fields.Monetary(
        string="Medical Allowance",
        currency_field="currency_id",
    )

    transport_allowance = fields.Monetary(
        string="Transport Allowance",
        currency_field="currency_id",
    )
    
    basic = fields.Monetary(
        string="Basic",
        currency_field="currency_id",
    )
    
    gro = fields.Monetary(
        string="Gro",
        currency_field="currency_id",
    )
    
    deduction = fields.Monetary(
        string="Deduction",
        currency_field="currency_id",
    )
    
    net_salary = fields.Monetary(
        string="Net Salary",
        currency_field="currency_id",
    )
    
    
    
    # -----------------------------------------------------------------
    # Nominee Form
    # -----------------------------------------------------------------
    
    nominee_ids = fields.One2many(
        "hr.employee.nominee",
        "employee_id",
        string="Nominee Information",
    )