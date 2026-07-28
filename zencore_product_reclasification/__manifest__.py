# -*- coding: utf-8 -*-

{
    "name": "Zencore Product Reclassification",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Controlled finished goods SKU reclassification workflow",
    "description": """
    Zencore Product Reclassification
    ================================

    Provides a controlled workflow for reclassifying finished goods
    from a source SKU to a target SKU.

    Main Features
    -------------
    * Storekeeper reclassification request
    * Factory Manager approval
    * Sales Manager approval
    * Finance Manager approval
    * Source and target SKU validation
    * Source lot and target lot management
    * Automatic inventory reclassification
    * Stock valuation tracking
    * Complete approval and audit history
    """,

    "author": "Saiful Islam Shawon",
    "license": "LGPL-3",

    "depends": [
        "base",
        "mail",
        "stock",
        "stock_account",
        "mrp",
        "account",
        "mrp_account",
    ],

    "data": [
        # security
        'security/ir.model.access.csv',
        'security/security.xml',
        # action 
        'views/sku_reclasification_request.xml',
        # view
        'views/menu.xml',
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}