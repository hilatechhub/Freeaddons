# -*- coding: utf-8 -*-
{
    'name': "Restaurant KPI Dashboards - POS Sales, Waiter & Cashier Stats, Customer Debt, Delivery, Treasury",
    'version': '19.0.1.1.0',
    'category': 'Sales/Point of Sale',
    'summary': "Restaurant management KPIs in Odoo: POS sales, average ticket, sales per hour, "
               "best waiters and cashiers, customer invoices and debt, delivery sales, treasury and expenses.",
    'description': """
Restaurant KPI Dashboards
=========================
Four ready-to-use dashboards to run your restaurant from Odoo, plus an
optional Expenses dashboard.

- Restaurant KPI: total sales, average sale per order and per guest, cancelled
  orders, sales per hour, sales per table, top products and top categories.
- Stat Serveur: best waiter and best cashier by revenue and by number of orders.
  Every POS order records its waiter (who sent the order) and its cashier
  (who validated the payment).
- Invoices & customer debt: invoiced amount, average invoice, unpaid customer
  invoices (customer debt) and delivery sales (customers flagged "Client livraison").
- Treasury: POS sales, vendor bills, balance and one card per bank / cash journal,
  generated automatically.
- Back office: Waiter and Cashier columns on POS orders, Customer debt and
  Delivery sales menus.
- Optional, with the Expenses app (hr_expense, not required): "Suivi des
  depenses" dashboard (to report, to validate, to reimburse, total, top
  categories and employees) and paid expenses added to the treasury charges.
  Created automatically as soon as the Expenses app is installed.
    """,
    'author': 'HILATECH',
    'website': 'https://hilatech.co',
    'support': 'support@hilatech.co',
    'license': 'LGPL-3',
    'price': 30.0,
    'currency': 'USD',
    'icon': 'static/description/icon.png',
    'images': ['static/description/banner.gif'],
    'depends': ['point_of_sale', 'pos_restaurant', 'account', 'spreadsheet_dashboard'],
    'data': [
        'views/pos_order_views.xml',
        'views/kpi_views.xml',
        'data/dashboards.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'hilatech_pos_waiter_cashier_stats/static/src/js/staff_capture.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
