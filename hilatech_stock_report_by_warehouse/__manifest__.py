# -*- coding: utf-8 -*-
{
    'name': 'Realtime Stock Report by Warehouse (PDF & Excel)',
    'version': '19.0.1.1.0',
    'category': 'Inventory/Reporting',
    'summary': "Realtime stock report by warehouse: every product with its live quantity "
               "in each warehouse, pivot and list views, PDF and Excel export, low stock in red.",
    'description': """
Realtime Stock Report by Warehouse (PDF & Excel)
================================================
A realtime stock report by warehouse: your live stock, one column per warehouse,
ready to print or export.

- Pivot view: products by category in rows, one column per warehouse.
- List view: warehouse, location, on hand, reserved and available quantities,
  total available across all warehouses.
- Low stock (under 5 units) highlighted in red.
- PDF export: one column per warehouse, product totals and grand total.
- Excel export: company logo, title, generation date, frozen header,
  one column per warehouse, totals.
- Menu: Inventory > Reporting > Stock Report.
    """,
    'author': 'HILATECH',
    'website': 'https://hilatech.co',
    'support': 'support@hilatech.co',
    'license': 'LGPL-3',
    'icon': 'static/description/icon.png',
    'images': ['static/description/banner.gif'],
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_inventory_report_views.xml',
        'report/report_stock_inventory_template.xml',
        'report/report_stock_inventory_action.xml',
    ],
    'installable': True,
    'auto_install': False,
}
