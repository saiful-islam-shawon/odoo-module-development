{
    "name": "Compliance Report",
    "version": "19.0.1.0.0",
    "summary": "Custom Compliance Reporting",
    "category": "Reporting",
    "author": "Saiful Islam Shawon",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr",
    ],
    "data": [
        "security/ir.model.access.csv",

        "views/job_application_views.xml",
        "views/appointment_letter_views.xml",
        "views/joining_letter_views.xml",
        "views/salary_increment_views.xml",
        "views/nominee_form_views.xml",
        "views/age_fitness_certificate_views.xml",
        "views/menu.xml",

        "report/job_application_report.xml",
        "report/appointment_letter_report.xml",
        "report/joining_letter_report.xml",
        "report/salary_increment_report.xml",
        "report/nominee_form_report.xml",
        "report/age_fitness_certificate_report.xml",
    ],
    "installable": True,
    "application": True,
}