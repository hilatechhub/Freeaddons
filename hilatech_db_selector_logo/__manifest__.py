{
    'name': 'Database Selector Logo - Custom Logo on the Odoo Database Page',
    'summary': 'Replace the Odoo logo on the database selection page with your own, from Settings.',
    'description': """
Database Selector Logo
======================

Replace the Odoo logo shown on the database selection page (before logging in)
with your own logo, from Settings > Database Selector.

Companion of "Odoo 19 Backend Theme" (hilatech_admin_theme_backend), usable on its own.

IMPORTANT - server configuration
--------------------------------
The database selection page is displayed before any database is chosen, so Odoo only
loads the modules listed in server_wide_modules for it. Add this module to odoo.conf and
restart Odoo:

    server_wide_modules = base,web,hilatech_db_selector_logo

The logo is stored in Odoo's data directory and is shared by all databases of the server.
This module contains no web assets, so it is safe to load server-wide.

Support: support@hilatech.co - https://hilatech.co
    """,
    'version': '19.0.1.0.0',
    'category': 'Themes/Backend',
    'license': 'LGPL-3',
    'author': 'HILATECH',
    'website': 'https://hilatech.co',
    'support': 'support@hilatech.co',
    'icon': '/hilatech_db_selector_logo/static/description/icon.png',
    'depends': ['base_setup'],
    'data': ['views/res_config_settings_view.xml'],
    'installable': True,
    'application': False,
}
