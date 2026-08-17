{
    'name': 'Map Learning',
    'version': '19.0.1.0.0',
    'category': 'Learning',
    'summary': 'Step by step Map and Leaflet integration learning module',
    'author': 'Saiful Islam Shaon',
    'depends': ['base', 'web'],
    'data': [
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # আমরা পর্যায়ক্রমে এখানে Leaflet JS, CSS এবং OWL JS/XML ফাইল যোগ করব
            
            # Custom OWL Files
            'map_learning/static/src/js/map_learning.js',
            'map_learning/static/src/xml/map_learning.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}