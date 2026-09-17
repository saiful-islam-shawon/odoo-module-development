from odoo import fields, models
from datetime import date


class ComplianceBulkReportWizard(models.TransientModel):
    _name = "compliance.bulk.report.wizard"
    _description = "Compliance Bulk Report Wizard"

    employee_ids = fields.Many2many(
        "hr.employee",
        string="Selected Employees",
        readonly=True,
    )
    

    # ---------------------------------------------------------
    # Open Wizard
    # ---------------------------------------------------------

    def _get_wizard_action(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "All Reports",
            "res_model": "compliance.bulk.report.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    # ---------------------------------------------------------
    # Get / Create Compliance Records
    # ---------------------------------------------------------

    def _get_or_create_records(self, model_name):
        self.ensure_one()

        Model = self.env[model_name]
        records = Model.browse()

        for employee in self.employee_ids:

            # ---------------------------------------------
            # Rules:
            #
            # 0 record  -> create
            # 1 record  -> use existing
            # >1 record -> use newest record
            # ---------------------------------------------

            record = Model.search(
                [
                    ("employee_id", "=", employee.id),
                ],
                order="id desc",
                limit=1,
            )

            if not record:
                record = Model.create({
                    "employee_id": employee.id,
                })

            records |= record

        return records

    # ---------------------------------------------------------
    # Job Application
    # ---------------------------------------------------------

    def action_print_job_application(self):
        self.ensure_one()

        records = self._get_or_create_records(
            "compliance.job.application"
        )

        return self.env.ref(
            "compliance_report.action_report_job_application"
        ).report_action(records)

    # ---------------------------------------------------------
    # Appointment Letter
    # ---------------------------------------------------------

    def action_print_appointment_letter(self):
        self.ensure_one()

        records = self._get_or_create_records(
            "compliance.appointment.letter"
        )

        return self.env.ref(
            "compliance_report.action_report_appointment_letter"
        ).report_action(records)

    # ---------------------------------------------------------
    # Joining Letter
    # ---------------------------------------------------------

    def action_print_joining_letter(self):
        self.ensure_one()

        records = self._get_or_create_records(
            "compliance.joining.letter"
        )

        return self.env.ref(
            "compliance_report.action_report_joining_letter"
        ).report_action(records)

    # ---------------------------------------------------------
    # Salary Increment
    # ---------------------------------------------------------

    def action_print_salary_increment(self):
        self.ensure_one()

        records = self._get_or_create_records(
            "compliance.salary.increment"
        )

        return self.env.ref(
            "compliance_report.action_report_salary_increment"
        ).report_action(records)

    # ---------------------------------------------------------
    # Nominee Form
    # ---------------------------------------------------------

    def action_print_nominee_form(self):
        self.ensure_one()

        records = self._get_or_create_records(
            "compliance.nominee.form"
        )

        return self.env.ref(
            "compliance_report.action_report_nominee_form"
        ).report_action(records)

    # ---------------------------------------------------------
    # Age & Fitness Certificate
    # ---------------------------------------------------------

    def action_print_age_fitness_certificate(self):
        self.ensure_one()

        records = self._get_or_create_records(
            "compliance.age.fitness.certificate"
        )

        return self.env.ref(
            "compliance_report.action_report_age_fitness_certificate"
        ).report_action(records)
        
        
    # new wizerd
    def action_open_monthly_salary_report(self):
        self.ensure_one()

        monthly_wizard = self.env[
            "compliance.monthly.salary.wizard"
        ].create({
            "employee_ids": [(6, 0, self.employee_ids.ids)],
        })

        monthly_wizard._prepare_lines()

        return {
            "type": "ir.actions.act_window",
            "name": "Monthly Salary Report",
            "res_model": "compliance.monthly.salary.wizard",
            "res_id": monthly_wizard.id,
            "view_mode": "form",
            "target": "new",
        }