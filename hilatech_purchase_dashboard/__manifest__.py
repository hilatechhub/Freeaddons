# -*- coding: utf-8 -*-
{
    'name': "Purchase Dashboard: Suppliers, Vendor Debt & KPIs",
    'version': '19.0.1.0.0',
    'category': 'Productivity/Dashboard',
    'summary': "Purchase dashboard for Odoo 19: purchase orders, total purchases, vendor debt, "
               "orders not received or not invoiced, top suppliers and purchases by category.",
    'description': """
Purchase Dashboard: Suppliers, Vendor Debt & KPIs
=================================================
A ready-to-use purchase dashboard in the Dashboards app (Finance group),
built on Odoo spreadsheet dashboards.

- 5 KPI tiles: confirmed purchase orders, total purchases, vendor debt
  (unpaid vendor bills), orders not received, orders not invoiced.
- Bar charts: top suppliers by purchase amount, purchases by product category,
  vendor debt by supplier.
- Global filters: period and supplier.
- Click any tile or chart to open the matching filtered list.
- New menus: confirmed / not received / not invoiced purchase orders,
  unpaid vendor bills.
    """,
    'author': 'HILATECH',
    'website': 'https://hilatech.co',
    'support': 'support@hilatech.co',
    'license': 'LGPL-3',
    'icon': 'static/description/icon.png',
    'images': ['static/description/banner.gif'],
    'depends': ['spreadsheet_dashboard', 'purchase', 'purchase_stock', 'account'],
    'data': [
        'data/purchase_actions.xml',
        'data/dashboards.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'post_upgrade_hook': 'post_upgrade_hook',
    'installable': True,
    'auto_install': False,
}
