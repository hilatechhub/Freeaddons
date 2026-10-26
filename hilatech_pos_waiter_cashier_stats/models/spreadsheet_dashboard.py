# -*- coding: utf-8 -*-
import base64
import logging

from odoo import models
from odoo.fields import Command
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

MODULE = 'hilatech_pos_waiter_cashier_stats'
EXPENSE_NAME = 'dashboard_expenses'
EXPENSE_FILE = f'{MODULE}/data/files/expense_dashboard.json'
VERSION_PARAM = f'{MODULE}.expense_dashboard_version'


class SpreadsheetDashboard(models.Model):
    _inherit = 'spreadsheet.dashboard'

    def _register_hook(self):
        super()._register_hook()
        # hr_expense est une dépendance facultative : le tableau de bord "Suivi des dépenses"
        # est créé dès que l'application Notes de frais est installée (avant ou après ce
        # module) et retiré si elle est désinstallée. Appelé à chaque chargement du registre.
        try:
            with self.env.cr.savepoint():
                self._hl_sync_expense_dashboard()
        except Exception:
            _logger.exception('Synchronisation du tableau de bord Suivi des dépenses impossible')

    def _hl_sync_expense_dashboard(self):
        dashboard = self.env.ref(f'{MODULE}.{EXPENSE_NAME}', raise_if_not_found=False)
        if 'hr.expense' not in self.env:
            if dashboard:
                dashboard.sudo().unlink()
                _logger.info('Tableau de bord Suivi des dépenses retiré (application Notes de frais absente)')
        else:
            # Version du module qui a écrit le tableau de bord : il est rafraîchi une seule
            # fois après chaque mise à jour du module, comme les tableaux de bord en XML.
            version = self.env['ir.module.module'].sudo().search([('name', '=', MODULE)], limit=1).latest_version
            params = self.env['ir.config_parameter'].sudo()
            if not dashboard:
                dashboard = self.sudo().create({
                    'name': 'Suivi des dépenses',
                    'dashboard_group_id': self.env.ref('spreadsheet_dashboard.spreadsheet_dashboard_group_finance').id,
                    'group_ids': [Command.link(self.env.ref('hr_expense.group_hr_expense_manager').id)],
                    'sequence': 45,
                    'spreadsheet_binary_data': self._hl_expense_file_data(),
                    'sample_dashboard_file_path': EXPENSE_FILE,
                })
                # noupdate : conservé lors des mises à jour du module, supprimé à sa désinstallation
                self.env['ir.model.data'].sudo().create({
                    'module': MODULE, 'name': EXPENSE_NAME, 'model': self._name,
                    'res_id': dashboard.id, 'noupdate': True,
                })
                params.set_param(VERSION_PARAM, version)
                _logger.info('Tableau de bord Suivi des dépenses créé (application Notes de frais installée)')
            elif params.get_param(VERSION_PARAM) != version:
                dashboard.sudo().spreadsheet_binary_data = self._hl_expense_file_data()
                params.set_param(VERSION_PARAM, version)
                _logger.info('Tableau de bord Suivi des dépenses mis à jour (version %s)', version)
        self.env['account.journal']._hl_check_treasury_expenses()

    def _hl_expense_file_data(self):
        with file_open(EXPENSE_FILE, 'rb') as f:
            return base64.b64encode(f.read())
