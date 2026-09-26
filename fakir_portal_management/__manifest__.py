{
    "name": "Fakir Portal Management",
    "version": "19.0.1.0.0",
    "summary": "CRM Portal Management for Fakir",
    "description": """
Fakir Portal Management
    """,
    "author": "Saiful Islam Shawon",
    "category": "CRM",
    "license": "LGPL-3",

    "depends": [
        "base",
        "website",
        "portal",
        "crm",
        "utm",
    ],

    "data": [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",

        # Website Template
        "views/crm_template.xml",
        "views/backend_send_mail_views.xml",
        "views/portal_crm_template.xml",

        # Website Menu
        "views/website_menu.xml",
    ],

    "assets": {
        "web.assets_frontend": [
            "fakir_portal_management/static/src/scss/crm.scss",
            "fakir_portal_management/static/src/js/crm.js",
            
            "fakir_portal_management/static/src/scss/portal_crm.scss",
            "fakir_portal_management/static/src/js/portal_crm.js",
        ],
    },

    "installable": True,
    "application": True,
    "auto_install": False,
}