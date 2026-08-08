# -*- coding: utf-8 -*-
{
    'name': "bKash Payment Provider",
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': "Payment Provider: bKash Implementation (Bangladesh Mobile Financial Service)",
    'description': """bKash Payment Provider

Integrates bKash Tokenized Checkout (URL Based) API with Odoo's payment
framework so customers can pay Sales Orders, Invoices and eCommerce orders
using their bKash wallet.
""",
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'author': "Zencore Solution Limited",
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'post_init_hook': 'post_init_hook',
}
