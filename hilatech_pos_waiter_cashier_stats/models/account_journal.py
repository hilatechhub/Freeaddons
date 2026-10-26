# -*- coding: utf-8 -*-
import base64
import json
import logging

from odoo import api, models
from odoo.tools import file_open

_logger = logging.getLogger(__name__)

TEMPLATE = 'hilatech_pos_waiter_cashier_stats/data/files/treasury_dashboard.json'
DASHBOARD = 'hilatech_pos_waiter_cashier_stats.dashboard_treasury'
EXPENSE_PIVOT = 'tres-pivot-expense'
FIRST_ROW = 6           # première ligne des journaux dans la feuille Data
CARDS_TOP = 140         # position verticale de la première carte journal
COLORS = {
    'bank': ['#EFF6FF', '#E0F2FE', '#DBEAFE', '#CFFAFE', '#CCFBF1'],
    'cash': ['#FEF2F2', '#FEE2E2', '#FFF7ED', '#FEF3C7', '#FCE7F3'],
}


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model_create_multi
    def create(self, vals_list):
        journals = super().create(vals_list)
        if any(j.type in ('bank', 'cash') for j in journals):
            self._hl_refresh_treasury_dashboard()
        return journals

    def write(self, vals):
        res = super().write(vals)
        if {'type', 'name', 'active'} & set(vals) and any(j.type in ('bank', 'cash') for j in self):
            self._hl_refresh_treasury_dashboard()
        return res

    @api.model
    def _hl_refresh_treasury_dashboard(self):
        """Regénère le tableau de bord Trésorerie : une carte par journal banque / caisse."""
        dashboard = self.env.ref(DASHBOARD, raise_if_not_found=False)
        if not dashboard:
            return
        with file_open(TEMPLATE, 'r') as f:
            data = json.load(f)
        figures = data['sheets'][0]['figures']
        cells = data['sheets'][1]['cells']
        if 'hr.expense' in self.env:
            self._hl_add_treasury_expenses(data)
        journals = self.sudo().with_context(active_test=True).search(
            [('type', 'in', ['bank', 'cash'])], order='type, name')
        # Plusieurs sociétés : le nom de la société distingue les journaux homonymes
        multi_company = len(journals.company_id) > 1

        for idx, journal in enumerate(journals):
            row = FIRST_ROW + idx
            name = f'{journal.name} ({journal.company_id.name})' if multi_company else journal.name
            cells[f'A{row}'] = name
            cells[f'B{row}'] = ('=IFERROR(PIVOT.VALUE(4,"amount_company_currency_signed:sum",'
                                f'"journal_id",{journal.id}),0)')
            cells[f'C{row}'] = f'=FORMAT.LARGE.NUMBER(B{row})'
            colors = COLORS.get(journal.type, COLORS['bank'])
            figures.append({
                'id': f'tres-sc-journal-{journal.id}',
                'width': 545, 'height': 100, 'tag': 'chart',
                'data': {
                    'type': 'scorecard',
                    'title': {'text': ('\U0001f3e6 ' if journal.type == 'bank' else '\U0001f4b5 ') + name,
                              'bold': True, 'color': '#434343', 'align': 'center'},
                    'background': colors[idx % len(colors)],
                    'keyValue': f'Data!C{row}',
                    'baselineMode': 'text', 'baselineColorDown': '#DC6965', 'baselineColorUp': '#00A04A',
                    'humanize': False,
                    'chartId': f'tres-sc-journal-{journal.id}',
                },
                'offset': {'x': 555 if idx % 2 else 0, 'y': CARDS_TOP + (idx // 2) * 115},
                'col': 0, 'row': 0,
            })

        total_row = FIRST_ROW + len(journals)
        cells[f'A{total_row}'] = 'Total Tresorerie'
        cells[f'B{total_row}'] = ('=' + '+'.join(f'B{FIRST_ROW + i}' for i in range(len(journals)))) if journals else '0'
        cells[f'C{total_row}'] = f'=FORMAT.LARGE.NUMBER(B{total_row})'
        total = next(f for f in figures if f['id'] == 'tres-sc-total')
        total['data']['keyValue'] = f'Data!C{total_row}'
        total['offset'] = {'x': 0, 'y': CARDS_TOP + ((len(journals) + 1) // 2) * 115}
        total['width'], total['height'] = 1100, 120

        dashboard.sudo().spreadsheet_binary_data = base64.b64encode(json.dumps(data).encode())
        _logger.info('Treasury dashboard refreshed with %s journals', len(journals))

    @api.model
    def _hl_add_treasury_expenses(self, data):
        """Application Notes de frais installée : les charges = achats + dépenses payées."""
        data['pivots'][EXPENSE_PIVOT] = {
            'type': 'ODOO', 'model': 'hr.expense', 'name': 'Dépenses', 'formulaId': '3',
            'domain': [['state', '=', 'paid']], 'context': {}, 'sortedColumn': None,
            'measures': [{'id': 'total_amount:sum', 'fieldName': 'total_amount', 'aggregator': 'sum'}],
            'columns': [], 'rows': [],
            'actionXmlId': 'hr_expense.hr_expense_actions_all',
            'fieldMatching': {'tres-filter-date-001': {'chain': 'date', 'type': 'date', 'offset': 0}},
        }
        cells = data['sheets'][1]['cells']
        cells['A3'], cells['B3'], cells['C3'] = 'Dépenses', '=IFERROR(PIVOT.VALUE(3,"total_amount:sum"),0)', '=FORMAT.LARGE.NUMBER(B3)'
        cells['A4'], cells['B4'] = 'Charges', '=B2+B3'
        cells['E1'] = '=CONCATENATE("Achats : ",TEXT(B2,"#,##0"),"  |  Dépenses : ",TEXT(B3,"#,##0"))'
        figures = {f['id']: f for f in data['sheets'][0]['figures']}
        charges = figures['tres-sc-charges']
        charges['data']['title']['text'] = '\U0001f4b8 Charges (achats + dépenses)'
        charges['data'].update({'baseline': 'Data!E1', 'baselineMode': 'text', 'baselineDescr': {'text': ''}})
        # La balance (ventes - charges) déduit donc aussi les dépenses payées
        figures['tres-sc-balance']['data']['title']['text'] = '⚖️ Balance (ventes - charges)'

    @api.model
    def _hl_check_treasury_expenses(self):
        """Regénère la trésorerie si la présence des dépenses ne correspond plus à hr_expense."""
        dashboard = self.env.ref(DASHBOARD, raise_if_not_found=False)
        if not dashboard or not dashboard.spreadsheet_binary_data:
            return
        data = json.loads(base64.b64decode(dashboard.sudo().spreadsheet_binary_data))
        if (EXPENSE_PIVOT in data.get('pivots', {})) != ('hr.expense' in self.env):
            self._hl_refresh_treasury_dashboard()
