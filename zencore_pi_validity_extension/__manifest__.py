# -*- coding: utf-8 -*-

{
    "name": "Zencore PI Validity Extension",

    "version": "19.0.1.0.0",

    "category": "Sales",

    "summary": "Manage and extend Proforma Invoice validity periods",

    "description": """
PI Validity Extension
=====================

This module extends the Proforma Invoice validity functionality.

Features:
---------
* Manage PI validity dates
* Request PI validity extensions
* Track validity extension information
* Integrate with the Sales workflow
    """,

    "author": "Saiful Islam Shawon",

    "license": "LGPL-3",

    "depends": [
        "mail",
        "sale",
        "zencore_groups",
    ],

    "data": [
        
        # sale_order_popup_widget security
        'security/ir.model.access.csv',
        
        # action server
        'views/sale_action_server.xml',
        
        # sale_order_inherit view
        'views/sale_order_inherit_view.xml',
        
        # popup widget
        'views/sale_popup_wizerd.xml',

        # approval line form
        'views/approval_line_form.xml',
    ],
    "installable": True,

    "application": True,

    "auto_install": False,
}