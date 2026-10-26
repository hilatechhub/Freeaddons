# -*- coding: utf-8 -*-
{
    'name': "POS Stock Restriction - Block Out-of-Stock Sales",
    'summary': "Prevent the Point of Sale from selling products with no stock "
               "or more than the real quantity on hand, with a clear popup alert.",
    'description': """
POS Stock Restriction
=====================
Blocks, in the Point of Sale, the sale of storable products that are out of
stock or whose ordered quantity exceeds the real quantity on hand in the
stock location of the Point of Sale. A popup informs the cashier each time.
    """,
    'version': '19.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'author': "HILATECH",
    'maintainer': "HILATECH SARL",
    'support': "support@hilatech.co",
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'hilatech_restrick_salespos/static/src/app/**/*',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
