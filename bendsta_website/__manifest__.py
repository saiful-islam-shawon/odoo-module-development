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
        'website_blog',
    ],

    'data': [
        'views/snippets/snippets.xml',
        'views/snippets/hero_section.xml',
        'views/snippets/blog_card_design.xml',
        'views/snippets/s_bendsta_hero.xml',
        'views/snippets/s_bendsta_about.xml',
        'views/snippets/s_bendsta_market_insights.xml',
        'views/snippets/s_bendsta_thr_solutions.xml',
        'views/snippets/s_bendsta_global_regulations.xml',
        'views/snippets/s_bendsta_framework.xml',
        'views/snippets/s_bendsta_summit.xml',
        'views/snippets/s_bendsta_contact.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'bendsta_website/static/src/scss/hero_section.scss',
            'bendsta_website/static/src/scss/blog_card_design.scss',
            'bendsta_website/static/src/js/blog_card_design.js',
            'bendsta_website/static/src/scss/bendsta.scss',
            'bendsta_website/static/src/js/bendsta_global_regulations.js',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}