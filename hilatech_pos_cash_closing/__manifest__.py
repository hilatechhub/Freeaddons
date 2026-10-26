# -*- coding: utf-8 -*-
{
    'name': 'POS Cash Closing - Daily Cash Count, Shortage & Overage Control',
    'version': '19.0.1.0.0',
    'price': 25.0,
    'currency': 'USD',
    'category': 'Point of Sale',
    'summary': 'Daily POS cash closing: count the cash, compare with Odoo, '
               'detect shortages and overages per payment method, approve and print.',
    'description': """
POS Cash Closing
================
End-of-day cash closing for the Odoo Point of Sale.

* Loads the expected amounts (ERP) per payment method from the POS session
  (change given back included; refunds = product returns, or entered manually)
* The manager enters the physical count per payment method
* Automatic balance, card / mobile money commission and gap per line
* Shortage / overage / balanced status, with a refund decision on shortages
* Approval workflow: Draft, Confirmed, Approved, with full chatter history
* Printable PDF closing report
* Excel exports (closing list and consolidated detail)
* Analysis per cashier: graph and pivot of shortages and overages
""",
    'author': 'HILATECH',
    'website': 'https://hilatech.co',
    'support': 'support@hilatech.co',
    'maintainer': 'HILATECH',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'mail'],
    'external_dependencies': {'python': ['openpyxl']},
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/cloture_caisse_views.xml',
        'views/pos_payment_method_views.xml',
        'views/cloture_caisse_analytics.xml',
        'views/actions.xml',
        'views/menus.xml',
        'report/report_action.xml',
        'report/report_template.xml',
    ],
    'icon': 'static/description/icon.png',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
}
