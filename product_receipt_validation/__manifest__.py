{
    'name': 'Zencore Product Receipt Validation',
    'summary': 'This is made for product receipt validation',
    'category': 'msa',
    'author': 'Zencore Solution LTD',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'stock', 'purchase', 'mail', 'quality_control'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/security.xml',
        # action
        'views/custom_inherit.xml',
        # menu
        'views/group_approval_views.xml',
        'views/qc_parameter.xml',
        'views/quality_check.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}