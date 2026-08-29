# -*- coding: utf-8 -*-

{
    'name': 'Aamarpay Payment Provider',
    'version': '19.0.1.0.0',
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
    """,
    'author': 'Saiful Islam Shawon',
    'license': 'LGPL-3',
    'depends': [
        'payment',
    ],
    'data': [
       'views/payment_provider_data.xml',
       'views/payment_provider_views.xml',
       'views/payment_form_templates.xml',
       'views/payment_method_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}