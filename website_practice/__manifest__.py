{
    'name': 'Website Practice Theme',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Shawon',
    'category': 'Theme/Corporate',  # ✅ এটা must
    'depends': ['website'],
    'data': [
        'views/homepage.xml',
    ],
    'assets': {
        'web.assets_frontend': [
           'website_practice/static/src/scss/homepage.scss',
           
            # CDN - Font Awesome 6
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
           
           #js
           'website_practice/static/src/js/homepage.js',

            
        ],
        
    },
    'installable': True,
    'application': False,
}

