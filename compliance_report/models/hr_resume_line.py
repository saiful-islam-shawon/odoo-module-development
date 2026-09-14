from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrResumeLine(models.Model):
    _inherit = "hr.resume.line"

    # ---------------------------------------------------------
    # Work Experience
    # ---------------------------------------------------------

    company_name = fields.Char(
        string="Company Name",
    )

    job_position = fields.Char(
        string="Job Position",
    )

    work_duration = fields.Char(
        string="Duration",
        compute="_compute_work_duration",
    )

    is_work_experience = fields.Boolean(
        string="Is Work Experience",
        compute="_compute_is_work_experience",
    )

    # ---------------------------------------------------------
    # Detect Work Experience Type
    # ---------------------------------------------------------

    @api.depends("line_type_id")
    def _compute_is_work_experience(self):
        work_type = self.env.ref(
            "compliance_report.resume_line_type_work_experience",
            raise_if_not_found=False,
        )

        for record in self:
            record.is_work_experience = bool(
                work_type
                and record.line_type_id == work_type
            )

    # ---------------------------------------------------------
    # Duration
    # ---------------------------------------------------------

    @api.depends("date_start", "date_end")
    def _compute_work_duration(self):
        today = fields.Date.today()

        for record in self:
            record.work_duration = False

            if not record.date_start:
                continue

            end_date = record.date_end or today

            if end_date < record.date_start:
                continue

            difference = relativedelta(
                end_date,
                record.date_start,
            )

            years = difference.years
            months = difference.months

            parts = []

            if years:
                parts.append(
                    f"{years} Year{'s' if years != 1 else ''}"
                )

            if months:
                parts.append(
                    f"{months} Month{'s' if months != 1 else ''}"
                )

            if not parts:
                parts.append("Less than 1 Month")

            record.work_duration = " ".join(parts)

    # ---------------------------------------------------------
    # Generate Standard Resume Title Automatically
    # ---------------------------------------------------------

    @api.onchange(
        "line_type_id",
        "company_name",
        "job_position",
    )
    def _onchange_work_experience_name(self):
        for record in self:
            if not record.is_work_experience:
                continue

            values = [
                record.job_position,
                record.company_name,
            ]

            record.name = " - ".join(
                value for value in values if value
            )
            
            
    # ---------------------------------------------------------
    # Education
    # ---------------------------------------------------------

    institution_name = fields.Char(
        string="Institution Name",
    )

    education_result = fields.Float(
        string="Result",
        digits=(10, 2),
    )

    education_result_out_of = fields.Float(
        string="Out Of",
        digits=(10, 2),
    )

    passing_year = fields.Integer(
        string="Passing Year",
    )

    is_education = fields.Boolean(
        string="Is Education",
        compute="_compute_is_education",
    )


    @api.depends("line_type_id")
    def _compute_is_education(self):
        for record in self:
            record.is_education = (
                record.line_type_id.name == "Education"
                if record.line_type_id
                else False
            )