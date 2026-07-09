{
    'name': "Learn Website",
    'summary': "This module is made for learning website development",
    'category': "Theme/Corporate",
    'version': "19.0.1.0.0",
    'license': "LGPL-3",

    'depends': [
        'website',
    ],

    'data': [
        
        # homepage
        'views/home_page.xml',
        
        # company card
        'views/snippets/company_card_template.xml',
        
        # company card step
        'views/snippets/company_card_step_template.xml',
        
        # hero section
        'views/snippets/hero_section.xml',
        
        # snippet
        'views/snippets/snippet.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            
            # home page
            'learning_website/static/src/scss/home_page.scss',
            'learning_website/static/src/js/homepage.js',
            
            # company card
            'learning_website/static/src/scss/company_card.scss',
            
            # company card step
            'learning_website/static/src/scss/company_card_step.scss',
            
            # hero section
            'learning_website/static/src/scss/hero_section.scss',
            'learning_website/static/src/js/hero_section.js',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}