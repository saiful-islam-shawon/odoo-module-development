{
    'name': "Zencore PriceList Acknowledgement",
    'description': "You can find pricelist acknowledgement data",
    'version': '19.0.1.0.0',
    'category': 'msa',
    'author': "Zencore Solution",
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'zencore_groups'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/security.xml',
        # action
        # inherit
        'views/pricelist_view.xml',
        # menu
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}