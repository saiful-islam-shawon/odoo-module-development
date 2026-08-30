# -*- coding: utf-8 -*-

{
    'name': 'Aamarpay Payment Provider',
    'version': '19.0.1.1.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Aamarpay Payment Gateway Integration for Odoo 19',
    'description': """
Aamarpay Payment Provider
=========================

This module integrates Aamarpay Payment Gateway with Odoo 19.

Features:
---------
* Aamarpay payment provider configuration
* Sandbox and production mode support
* Payment transaction handling
* Payment request generation
* Success callback handling
* Failed payment handling
* Cancel payment handling
* Transaction verification
* Integration with Odoo Payment Provider
* Pay Now action from the Contact form
* Standalone customer collection through Aamarpay
* Automatic posted account.payment in a dedicated AamarPay bank journal
    """,
    'author': 'Saiful Islam Shawon',
    'license': 'LGPL-3',
    'depends': [
        'payment',
        'account_payment',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_form_templates.xml',
        'views/payment_method_data.xml',
        'views/res_partner_views.xml',
        'wizard/amarpay_pay_now_wizard_views.xml',
        'views/account_payment_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
