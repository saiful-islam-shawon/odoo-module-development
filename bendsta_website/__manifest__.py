# -*- coding: utf-8 -*-
{
    'name': 'Bendsta Website',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Custom website building blocks and snippets for Bendsta',
    'description': """
        Bendsta Website Customization
        ==============================
        This module provides custom building blocks, responsive snippets, 
        and layout components for the Odoo 19 Website builder.
    """,
    'author': 'Bendsta',
    'license': 'LGPL-3',
    'depends': [
        'website',
    ],
    'data': [
        "views/snippets/snippets.xml",
        "views/snippets/hero_section.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            "bendsta_website/static/src/scss/hero_section.scss",
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}