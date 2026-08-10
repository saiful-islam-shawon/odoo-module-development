{
    'name': 'Bkash Integration',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'bKash Payment Gateway Integration for Odoo 19',
    'author': 'saiful islam shawon',
    'depends': ['payment', 'website_payment', 'website'],
    'data': [
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}