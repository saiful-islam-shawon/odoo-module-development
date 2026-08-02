# -*- coding: utf-8 -*-

{
    "name": "Zencore Leave Approval",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Time Off",
    "summary": "Manage employee leave requests and approval workflow",
    "description": """
Zencore Leave Approval
======================

This module extends the Odoo Time Off application with a custom
leave request and approval workflow.

Main Features
-------------
* Employee leave request management
* Multi-stage leave approval
* Approval history and tracking
* User activities and notifications
    """,

    "author": "Zencore Solution Limited",
    "maintainer": "Zencore Solution Limited",
    "license": "LGPL-3",

    "depends": [
        "hr_holidays",
        "mail",
    ],

    "data": [
        'views/leave_view.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}