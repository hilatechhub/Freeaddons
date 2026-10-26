# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class CashJournalReport(models.Model):
    _name = 'cash.journal.report'
    _description = 'Journal de Caisse - Relevé Mensuel'
    _order = 'month_date desc, id desc'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ============================================================================
    # FIELDS - Base
    # ============================================================================

    name = fields.Char(
        string='Numéro',
        readonly=True,
        copy=False,
        default='/',
        tracking=True
    )

    month_date = fields.Date(
        string='Mois du Relevé',
        required=True,
        tracking=True,
        help='Date du mois concerné (sera défini au 1er du mois)'
    )

    # ============================================================================
    # FIELDS - Balances
    # ============================================================================

    initial_balance = fields.Float(
        string='Solde Initial',
        required=True,
        digits=(15, 2),
        help='Solde de début de mois'
    )

    final_balance = fields.Float(
        string='Solde Final',
        compute='_compute_final_balance',
        store=True,
        digits=(15, 2),
        readonly=True,
        help='Solde = initial + somme des opérations'
    )

    # ============================================================================
    # FIELDS - State
    # ============================================================================

    state = fields.Selection(
        [
            ('open', 'Ouvert'),
            ('closed', 'Clôturé'),
        ],
        string='Statut du Relevé',
        default='open',
        tracking=True,
        help='Ouvert: en cours de saisie | Clôturé: définitivement fermé'
    )

    caisse_state = fields.Selection(
        [
            ('opened', 'Caisse Ouverte'),
            ('closed', 'Caisse Fermée'),
        ],
        string='État de la Caisse du Jour',
        default='closed',
        tracking=True,
        help='Ouvert: on peut saisir les opérations | Fermé: les opérations sont verrouillées'
    )

    # ============================================================================
    # FIELDS - Relations
    # ============================================================================

    operation_ids = fields.One2many(
        'cash.journal.operation',
        'report_id',
        string='Opérations',
        help='Entrées et sorties de caisse du mois'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Entreprise',
        default=lambda self: self.env.company,
        readonly=True,
        tracking=True
    )

    # ============================================================================
    # FIELDS - Additional
    # ============================================================================

    notes = fields.Text(
        string='Observations',
        help='Notes libres sur ce relevé'
    )

    # ============================================================================
    # COMPUTED FIELDS
    # ============================================================================

    @api.depends('initial_balance', 'operation_ids.amount', 'operation_ids.is_locked')
    def _compute_final_balance(self):
        """Calculer le solde final = solde initial + somme des montants"""
        for record in self:
            total_operations = sum(record.operation_ids.mapped('amount'))
            record.final_balance = record.initial_balance + total_operations

    # ============================================================================
    # CREATE / WRITE / UNLINK
    # ============================================================================

    @api.model
    def create(self, vals_list):
        """Générer la séquence et définir le solde initial à partir du relevé précédent"""
        for vals in vals_list:
            # Générer la séquence
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'cash.journal.report'
                ) or '/'

            # Si pas de solde initial fourni, prendre le solde final du relevé précédent clôturé
            if not vals.get('initial_balance'):
                last_closed_report = self.search(
                    [('state', '=', 'closed')],
                    order='month_date desc',
                    limit=1
                )
                if last_closed_report:
                    vals['initial_balance'] = last_closed_report.final_balance
                else:
                    vals['initial_balance'] = 0.0

        return super().create(vals_list)

    # ============================================================================
    # ACTIONS - Workflow
    # ============================================================================

    def action_open_caisse(self):
        """Ouvrir la caisse pour permettre la saisie des opérations"""
        self.ensure_one()
        if self.state != 'open':
            raise UserError(
                _('Seuls les relevés ouverts peuvent être utilisés.')
            )
        if self.caisse_state == 'opened':
            raise UserError(
                _('La caisse est déjà ouverte.')
            )
        self.caisse_state = 'opened'
        self.message_post(
            body=_('Caisse ouverte pour saisie des opérations du jour.')
        )

    def action_close_day(self):
        """Clôturer la caisse du jour : verrouille toutes les opérations non verrouillées"""
        self.ensure_one()
        if self.state != 'open':
            raise UserError(
                _('Seul un relevé ouvert peut être clôturé.')
            )
        if self.caisse_state != 'opened':
            raise UserError(
                _('La caisse doit être ouverte pour la clôturer.')
            )

        # Verrouiller toutes les opérations non verrouillées
        unlocked_operations = self.operation_ids.filtered(lambda op: not op.is_locked)
        if unlocked_operations:
            unlocked_operations.sudo().write({'is_locked': True})

        # Changer l'état de la caisse
        self.caisse_state = 'closed'

        # Message avec le solde du jour
        balance_message = _('Caisse clôturée pour la journée. Solde final: {amount:.2f}').format(
            amount=self.final_balance
        )
        self.message_post(body=balance_message)

    def action_close_monthly(self):
        """Clôturer définitivement le relevé mensuel"""
        self.ensure_one()
        if self.state != 'open':
            raise UserError(
                _('Ce relevé est déjà clôturé.')
            )

        # Fermer la caisse si elle est ouverte
        if self.caisse_state == 'opened':
            self.action_close_day()

        # Changer l'état du relevé
        self.state = 'closed'

        # Message final
        message = _('Relevé mensuel clôturé définitivement. Solde final: {amount:.2f}').format(
            amount=self.final_balance
        )
        self.message_post(body=message)

    # ============================================================================
    # CONSTRAINTS
    # ============================================================================

    @api.constrains('initial_balance')
    def _check_initial_balance(self):
        """Vérifier que le solde initial est positif"""
        for record in self:
            if record.initial_balance < 0:
                raise ValidationError(
                    _('Le solde initial doit être positif ou nul.')
                )

    @api.constrains('month_date')
    def _check_month_date_unique(self):
        """Vérifier qu'il n'y a pas deux relevés du même mois/année ouvert"""
        for record in self:
            # Extraire année et mois
            record_year = record.month_date.year
            record_month = record.month_date.month

            # Chercher d'autres relevés du même mois/année ouverts
            duplicates = self.search([
                ('id', '!=', record.id),
                ('state', '=', 'open'),
            ])

            for dup in duplicates:
                if (dup.month_date.year == record_year and
                    dup.month_date.month == record_month):
                    raise ValidationError(
                        _('Un relevé ouvert existe déjà pour le mois de {month}/{year}.').format(
                            month=record_month, year=record_year
                        )
                    )


class CashJournalOperation(models.Model):
    _name = 'cash.journal.operation'
    _description = 'Journal de Caisse - Opération'
    _order = 'date desc, id desc'

    # ============================================================================
    # FIELDS - Relations
    # ============================================================================

    report_id = fields.Many2one(
        'cash.journal.report',
        string='Relevé',
        required=True,
        ondelete='cascade',
        readonly=True
    )

    # ============================================================================
    # FIELDS - Base
    # ============================================================================

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )

    description = fields.Char(
        string='Description/Motif',
        required=True,
        tracking=True,
        help='Description de l\'opération (reçu, dépense, etc.)'
    )

    received_by = fields.Many2one(
        'res.partner',
        string='Reçu par / Payé par',
        required=True,
        help='Partner ou employé qui a reçu ou perçu l\'argent'
    )

    amount = fields.Float(
        string='Montant',
        required=True,
        digits=(15, 2),
        tracking=True,
        help='Montant positif = entrée | Montant négatif = sortie'
    )

    # ============================================================================
    # FIELDS - State
    # ============================================================================

    is_locked = fields.Boolean(
        string='Verrouillée',
        default=False,
        readonly=True,
        tracking=True,
        help='Vrai = opération verrouillée après clôture du jour, ne peut plus être modifiée'
    )

    # ============================================================================
    # COMPUTED FIELDS
    # ============================================================================

    @api.depends('amount')
    def _compute_operation_type(self):
        """Déterminer le type d'opération basé sur le signe du montant"""
        for record in self:
            if record.amount > 0:
                record.operation_type = 'income'
            elif record.amount < 0:
                record.operation_type = 'expense'
            else:
                record.operation_type = 'neutral'

    operation_type = fields.Selection(
        [
            ('income', 'Entrée'),
            ('expense', 'Sortie'),
            ('neutral', 'Neutre'),
        ],
        string='Type',
        compute='_compute_operation_type',
        store=True
    )

    # ============================================================================
    # WRITE / UNLINK - Protections
    # ============================================================================

    def write(self, vals):
        """Protéger l'opération si verrouillée, caisse fermée ou relevé clôturé"""
        # Autoriser la modification du champ is_locked lui-même (pour le verrouillage)
        if set(vals.keys()) == {'is_locked'}:
            return super().write(vals)

        for record in self:
            # Vérifier si le relevé est clôturé
            if record.report_id.state == 'closed':
                raise UserError(
                    _('Ce relevé mensuel est clôturé. Aucune modification n\'est possible.')
                )
            # Vérifier si la caisse du jour est fermée
            if record.report_id.caisse_state == 'closed':
                raise UserError(
                    _('La caisse du jour est fermée. Aucune modification n\'est possible.')
                )
            # Vérifier si l'opération est verrouillée
            if record.is_locked:
                raise UserError(
                    _('Cette opération est verrouillée et ne peut pas être modifiée. '
                      'Elle a été enregistrée lors de la clôture de la caisse du jour.')
                )
        return super().write(vals)

    def unlink(self):
        """Protéger l'opération si verrouillée, caisse fermée ou relevé clôturé"""
        for record in self:
            # Vérifier si le relevé est clôturé
            if record.report_id.state == 'closed':
                raise UserError(
                    _('Ce relevé mensuel est clôturé. Aucune suppression d\'opération n\'est possible.')
                )
            # Vérifier si la caisse du jour est fermée
            if record.report_id.caisse_state == 'closed':
                raise UserError(
                    _('La caisse du jour est fermée. Aucune suppression d\'opération n\'est possible.')
                )
            # Vérifier si l'opération est verrouillée
            if record.is_locked:
                raise UserError(
                    _('Cette opération est verrouillée et ne peut pas être supprimée. '
                      'Elle a été enregistrée lors de la clôture de la caisse du jour.')
                )
        return super().unlink()

    # ============================================================================
    # CONSTRAINTS
    # ============================================================================

    @api.constrains('report_id')
    def _check_report_closed(self):
        """Vérifier que le relevé n'est pas clôturé et que la caisse n'est pas fermée"""
        for record in self:
            if record.report_id.state == 'closed':
                raise ValidationError(
                    _('Ce relevé mensuel est clôturé. Aucune opération ne peut être créée ou modifiée.')
                )
            if record.report_id.caisse_state == 'closed':
                raise ValidationError(
                    _('La caisse du jour est fermée. Aucune opération ne peut être créée ou modifiée.')
                )

    @api.constrains('amount', 'date')
    def _check_operation_constraints(self):
        """Vérifier les contraintes d'opération"""
        for record in self:
            # Montant ne peut pas être zéro
            if record.amount == 0:
                raise ValidationError(
                    _('Le montant doit être différent de zéro.')
                )

            # La date ne peut pas être dans le futur
            if record.date > fields.Date.today():
                raise ValidationError(
                    _('La date de l\'opération ne peut pas être dans le futur.')
                )

            # La date doit être dans le mois du relevé
            if record.report_id.month_date:
                report_month = record.report_id.month_date.month
                report_year = record.report_id.month_date.year
                if (record.date.month != report_month or
                    record.date.year != report_year):
                    raise ValidationError(
                        _('La date de l\'opération doit être dans le mois du relevé.')
                    )


class CashJournalPdfReport(models.TransientModel):
    _name = 'cash.journal.pdf.report'
    _description = 'Rapport PDF de Caisse'

    # ============================================================================
    # FIELDS
    # ============================================================================

    date_start = fields.Date(
        string='Date de Début',
        required=True,
        default=fields.Date.context_today,
        help='Date de début du rapport'
    )

    date_end = fields.Date(
        string='Date de Fin',
        required=True,
        default=fields.Date.context_today,
        help='Date de fin du rapport'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Entreprise',
        default=lambda self: self.env.company,
        readonly=True
    )

    # ============================================================================
    # ACTIONS
    # ============================================================================

    def action_generate_pdf(self):
        """Générer le rapport PDF avec le layout standard d'Odoo"""
        self.ensure_one()
        if self.date_start > self.date_end:
            raise UserError(
                _('La date de début doit être inférieure ou égale à la date de fin.')
            )

        # Vérifier qu'il y a des relevés
        reports = self.env['cash.journal.report'].search([
            ('month_date', '>=', self.date_start),
            ('month_date', '<=', self.date_end),
        ])

        if not reports:
            raise UserError(
                _('Aucun relevé trouvé pour la période sélectionnée.')
            )

        # Utiliser le rapport Qweb avec le layout standard d'Odoo
        return self.env.ref('hilatech_cash_journal.report_cash_journal_pdf').report_action(self)

    def action_generate_excel(self):
        """Générer le rapport Excel"""
        self.ensure_one()
        if self.date_start > self.date_end:
            raise UserError(
                _('La date de début doit être inférieure ou égale à la date de fin.')
            )

        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            from openpyxl.drawing.image import Image
        except ImportError:
            raise UserError(
                _('La bibliothèque openpyxl n\'est pas installée. '
                  'Veuillez installer openpyxl pour générer des rapports Excel.')
            )

        # Récupérer les relevés et opérations dans la plage de dates
        reports = self.env['cash.journal.report'].search([
            ('month_date', '>=', self.date_start),
            ('month_date', '<=', self.date_end),
        ], order='month_date desc')

        if not reports:
            raise UserError(
                _('Aucun relevé trouvé pour la période sélectionnée.')
            )

        # Créer le workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Rapport de Caisse'

        # En-têtes
        row = 1

        # Logo et infos company
        ws[f'A{row}'] = self.company_id.name
        ws[f'A{row}'].font = Font(name='Arial', size=16, bold=True)
        ws.merge_cells(f'A{row}:F{row}')
        row += 1

        ws[f'A{row}'] = f'Rapport de Caisse'
        ws[f'A{row}'].font = Font(name='Arial', size=14, bold=True)
        ws.merge_cells(f'A{row}:F{row}')
        row += 1

        ws[f'A{row}'] = f'Du {self.date_start.strftime("%d/%m/%Y")} au {self.date_end.strftime("%d/%m/%Y")}'
        ws[f'A{row}'].font = Font(name='Arial', size=11)
        ws.merge_cells(f'A{row}:F{row}')
        row += 2

        # Styles
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        subheader_fill = PatternFill(start_color='d9e1f2', end_color='d9e1f2', fill_type='solid')
        subheader_font = Font(bold=True)

        total_initial = 0
        total_final = 0
        total_operations_amount = 0

        for report in reports:
            # En-tête du relevé
            ws.cell(row=row, column=1, value=f"Relevé: {report.name} - {report.month_date.strftime('%B %Y')}")
            ws[f'A{row}'].font = subheader_font
            ws[f'A{row}'].fill = subheader_fill
            ws.merge_cells(f'A{row}:F{row}')
            row += 1

            # Infos du relevé
            ws.cell(row=row, column=1, value='Solde Initial')
            ws.cell(row=row, column=2, value=report.initial_balance)
            ws.cell(row=row, column=3, value='Responsable')
            ws.cell(row=row, column=4, value=report.user_id.name)
            ws.cell(row=row, column=5, value='État')
            ws.cell(row=row, column=6, value=report.state.upper())

            for col in range(1, 7):
                ws.cell(row=row, column=col).border = border
                if col == 2:
                    ws.cell(row=row, column=col).number_format = '#,##0.00'

            row += 1

            # En-têtes des opérations
            headers = ['Date', 'Description', 'Reçu par', 'Type', 'Montant', 'Verrouillé']
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = border

            row += 1

            # Opérations du relevé
            total_ops = 0
            for op in report.operation_ids:
                ws.cell(row=row, column=1, value=op.date)
                ws.cell(row=row, column=2, value=op.description)
                ws.cell(row=row, column=3, value=op.received_by.name or '')

                # Type d'opération
                if op.amount > 0:
                    ws.cell(row=row, column=4, value='Entrée')
                elif op.amount < 0:
                    ws.cell(row=row, column=4, value='Sortie')
                else:
                    ws.cell(row=row, column=4, value='Neutre')

                ws.cell(row=row, column=5, value=op.amount)
                ws.cell(row=row, column=6, value='Oui' if op.is_locked else 'Non')

                for col in range(1, 7):
                    cell = ws.cell(row=row, column=col)
                    cell.border = border
                    if col == 5:
                        cell.number_format = '#,##0.00'

                total_ops += op.amount
                total_operations_amount += op.amount
                row += 1

            # Solde final du relevé
            ws.cell(row=row, column=1, value='Solde Final')
            ws.cell(row=row, column=2, value=report.final_balance)
            ws.cell(row=row, column=2).font = Font(bold=True)
            ws.cell(row=row, column=2).number_format = '#,##0.00'
            ws.cell(row=row, column=5, value='Total Mois')
            ws.cell(row=row, column=6, value=total_ops)
            ws.cell(row=row, column=6).font = Font(bold=True)
            ws.cell(row=row, column=6).number_format = '#,##0.00'

            for col in range(1, 7):
                ws.cell(row=row, column=col).border = border

            total_initial += report.initial_balance
            total_final += report.final_balance
            row += 2

        # Ligne de total général
        ws.cell(row=row, column=1, value='TOTAL GÉNÉRAL')
        ws.cell(row=row, column=1).font = Font(bold=True, size=12)
        ws.cell(row=row, column=1).fill = PatternFill(start_color='f0f0f0', end_color='f0f0f0', fill_type='solid')
        ws.cell(row=row, column=2, value=total_initial)
        ws.cell(row=row, column=2).font = Font(bold=True, size=12)
        ws.cell(row=row, column=2).number_format = '#,##0.00'
        ws.cell(row=row, column=2).fill = PatternFill(start_color='f0f0f0', end_color='f0f0f0', fill_type='solid')
        ws.cell(row=row, column=5, value='Total Opérations')
        ws.cell(row=row, column=5).font = Font(bold=True, size=12)
        ws.cell(row=row, column=5).fill = PatternFill(start_color='f0f0f0', end_color='f0f0f0', fill_type='solid')
        ws.cell(row=row, column=6, value=total_operations_amount)
        ws.cell(row=row, column=6).font = Font(bold=True, size=12)
        ws.cell(row=row, column=6).number_format = '#,##0.00'
        ws.cell(row=row, column=6).fill = PatternFill(start_color='f0f0f0', end_color='f0f0f0', fill_type='solid')

        row += 1
        ws.cell(row=row, column=1, value='')
        ws.cell(row=row, column=2, value=total_final)
        ws.cell(row=row, column=2).font = Font(bold=True, size=12)
        ws.cell(row=row, column=2).number_format = '#,##0.00'
        ws.cell(row=row, column=2).fill = PatternFill(start_color='f0f0f0', end_color='f0f0f0', fill_type='solid')

        # Ajuster les largeurs des colonnes
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15

        # Sauvegarder et retourner
        import io
        import base64

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        # Créer un attachement
        filename = f'rapport_caisse_{self.date_start.strftime("%d_%m_%Y")}_au_{self.date_end.strftime("%d_%m_%Y")}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
