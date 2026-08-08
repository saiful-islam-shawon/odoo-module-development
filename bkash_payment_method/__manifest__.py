{
    "name": "bKash Payment Provider",
    "version": "19.0.1.0.0",
    "summary": "Payment Provider: bKash",
    "description": """
        Integrate bKash Payment Gateway with Odoo.
    """,
    "category": "Accounting/Payment Providers",
    "author": "Your Company",
    "license": "LGPL-3",
    "depends": [
        "payment",
    ],
    "data": [
        'data/payment_method.xml',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/payment.templates.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            
        ],
    },
    "installable": True,
    "application": False,
}