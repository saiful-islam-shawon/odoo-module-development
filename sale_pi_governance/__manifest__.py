{
    'name': "Sale Pi Governance",
    'summary': "Sale PI Validity Extension & Product Substitution Governance",
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'zencore_groups'],
    'data': [
        # security
        # action
        'views/sale_order_view.xml',
        'views/sale_popup_wizerd.xml',
        # menu
    ],
    'installable': True,
    'auto-install': True,
    'application': True
}