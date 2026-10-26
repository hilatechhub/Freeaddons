# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import UserError # type: ignore
from odoo.tools import float_round # type: ignore


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    cloture_taux_commission = fields.Float(
        string='Taux Commission Clôture (%)',
        digits=(5, 2),
        default=0.0,
        help="Commission retenue par la banque ou l'operateur sur ce mode de paiement (ex : 1.0 pour 1 %). Laisser 0 pour les especes."
    )


class ClotureCaisse(models.Model):
    _name = 'cloture.caisse'
    _description = 'Clôture de Caisse'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Référence', readonly=True, default='/', copy=False, tracking=True
    )
    pos_config_id = fields.Many2one(
        'pos.config', string='Point de Vente', required=True, tracking=True
    )
    session_id = fields.Many2one(
        'pos.session', string='Session POS', tracking=True,
        domain="[('config_id', '=', pos_config_id)]"
    )
    date = fields.Date(
        string='Date', default=fields.Date.today, required=True, tracking=True
    )
    manager_id = fields.Many2one(
        'res.users', string='Manager', default=lambda self: self.env.user, tracking=True
    )
    caissier_id = fields.Many2one(
        'res.users', string='Caissier du Jour', tracking=True
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('approved', 'Approuvé'),
    ], string='Statut', default='draft', tracking=True)

    line_ids = fields.One2many('cloture.caisse.line', 'cloture_id', string='Lignes')
    note = fields.Text(string='Observations')

    # --- Totaux calculés ---
    total_physique = fields.Float(
        compute='_compute_totaux', string='Total Physique', store=True, digits=(15, 2)
    )
    total_erp = fields.Float(
        compute='_compute_totaux', string='Total ERP', store=True, digits=(15, 2)
    )
    total_balance = fields.Float(
        compute='_compute_totaux', string='Total Balance', store=True, digits=(15, 2)
    )
    total_commission = fields.Float(
        compute='_compute_totaux', string='Total Commission', store=True, digits=(15, 2)
    )
    ecart_net = fields.Float(
        compute='_compute_totaux', string='Écart Net', store=True, digits=(15, 2),
        help='Écart signé : total_balance + total_commission (avant abs)'
    )
    manquant_finale = fields.Float(
        compute='_compute_totaux', string='Manquant Final', store=True, digits=(15, 2),
        help='Ecart final signe : negatif = manquant, positif = excedent'
    )
    type_manquant_final = fields.Selection([
        ('equilibre', 'Équilibré ✓'),
        ('excedent', 'Excédent'),
        ('manquant', 'Manquant'),
    ], compute='_compute_is_balanced', string='Type Manquant Final', store=True)
    is_balanced = fields.Boolean(
        compute='_compute_is_balanced', string='Équilibré', store=True
    )
    decision = fields.Selection([
        ('a_rembourser', 'À Rembourser'),
        ('non_remboursable', 'Non Remboursable'),
    ], string='Décision', tracking=True,
        compute='_compute_decision', store=True, readonly=False,
        help="Uniquement en cas de manquant ; vidée automatiquement sinon.")
    decision_label = fields.Char(
        string='Décision', compute='_compute_decision_label', store=True,
        help="Libellé de la décision, ou « - » quand aucune décision n'est requise."
    )

    @api.depends('type_manquant_final')
    def _compute_decision(self):
        # Une décision n'a de sens que sur un manquant : on la vide sinon
        for rec in self:
            if rec.type_manquant_final != 'manquant':
                rec.decision = False

    @api.depends('decision')
    def _compute_decision_label(self):
        labels = dict(self._fields['decision'].selection)
        for rec in self:
            rec.decision_label = labels.get(rec.decision) or '-'

    @api.depends('line_ids.controle_physique', 'line_ids.etat_erp',
                 'line_ids.commission', 'line_ids.balance', 'line_ids.ecart')
    def _compute_totaux(self):
        for rec in self:
            rec.total_physique = sum(rec.line_ids.mapped('controle_physique'))
            rec.total_erp = sum(rec.line_ids.mapped('etat_erp'))
            rec.total_balance = sum(rec.line_ids.mapped('balance'))
            rec.total_commission = sum(rec.line_ids.mapped('commission'))
            # Écart net signé : total_balance + total_commission
            rec.ecart_net = float_round(rec.total_balance + rec.total_commission, 2)
            # Manquant final signé (= ecart_net)
            rec.manquant_finale = rec.ecart_net

    @api.depends('ecart_net')
    def _compute_is_balanced(self):
        for rec in self:
            rec.is_balanced = rec.ecart_net == 0
            if rec.ecart_net == 0:
                rec.type_manquant_final = 'equilibre'
            elif rec.ecart_net > 0:
                rec.type_manquant_final = 'excedent'
            else:
                rec.type_manquant_final = 'manquant'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('cloture.caisse') or '/'
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Chargement depuis la session POS
    # ------------------------------------------------------------------
    def action_load_from_session(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Impossible de recharger une clôture déjà confirmée."))

        # Trouver la session si pas encore définie
        if not self.session_id:
            session = self.env['pos.session'].search([
                ('config_id', '=', self.pos_config_id.id),
                ('state', 'in', ['opened', 'closing_control']),
            ], limit=1)
            if not session:
                session = self.env['pos.session'].search([
                    ('config_id', '=', self.pos_config_id.id),
                    ('state', '=', 'closed'),
                    ('start_at', '>=', fields.Datetime.now().replace(
                        hour=0, minute=0, second=0)),
                ], order='stop_at desc', limit=1)
            if not session:
                raise UserError(_(
                    "Aucune session POS ouverte ou fermée aujourd'hui pour '%s'."
                ) % self.pos_config_id.name)
            self.session_id = session

        # Auto-remplir le caissier depuis la session
        if self.session_id.user_id and not self.caissier_id:
            self.caissier_id = self.session_id.user_id

        # Totaux ERP par mode de paiement :
        # ventes encaissees moins la monnaie rendue (paiements is_change).
        # Les remboursements des retours produits vont sur la ligne dediee.
        payment_totals = {}
        total_refund = 0.0
        for pmt in self.env['pos.payment'].search([('session_id', '=', self.session_id.id)]):
            order = pmt.pos_order_id
            is_return = order.is_refund or bool(order.lines.refunded_orderline_id)
            if pmt.amount < 0 and not pmt.is_change and is_return:
                total_refund += pmt.amount
            else:
                mid = pmt.payment_method_id.id
                payment_totals[mid] = payment_totals.get(mid, 0.0) + pmt.amount

        # Un remboursement saisi manuellement par le manager est conserve ;
        # sinon la ligne reprend uniquement les retours produits de la session.
        manual = self.line_ids.filtered(lambda l: l.is_remboursement and l.saisie_manuelle)[:1]
        refund_vals = {'etat_erp': manual.etat_erp, 'saisie_manuelle': True} if manual             else {'etat_erp': total_refund, 'saisie_manuelle': False}

        # Supprimer les lignes existantes
        self.line_ids.unlink()

        lines_vals = []
        for method_id, amount in payment_totals.items():
            method = self.env['pos.payment.method'].browse(method_id)
            taux = method.cloture_taux_commission
            lines_vals.append({
                'cloture_id': self.id,
                'payment_method_id': method_id,
                'etat_erp': amount,
                'controle_physique': 0.0,
                'has_commission': taux > 0,
                'taux_commission': taux,
                'is_remboursement': False,
            })

        # Ligne Total Remboursement (montant negatif), modifiable par le manager
        lines_vals.append(dict(refund_vals, **{
            'cloture_id': self.id,
            'payment_method_id': False,
            'is_remboursement': True,
            'controle_physique': 0.0,
            'has_commission': False,
            'taux_commission': 0.0,
        }))

        self.env['cloture.caisse.line'].with_context(cloture_loading=True).create(lines_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cloture.caisse',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------
    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Seul un brouillon peut être confirmé."))
        if not self.line_ids:
            raise UserError(_("Veuillez d'abord charger les données de la session."))
        self.state = 'confirmed'

    def action_approve(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_("Seule une clôture confirmée peut être approuvée."))
        self.state = 'approved'

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state == 'approved':
            raise UserError(_("Une clôture approuvée ne peut pas être réinitialisée."))
        self.state = 'draft'

    def action_print_report(self):
        return self.env.ref('hilatech_pos_cash_closing.action_report_cloture_caisse').report_action(self)

    def action_export_detail_to_excel(self):
        """Exporte le détail consolidé de toutes les clôtures sélectionnées en Excel."""
        import io
        import base64
        from datetime import datetime

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        except ImportError:
            raise UserError(_("La bibliothèque openpyxl n'est pas installée."))

        if not self:
            raise UserError(_("Aucun enregistrement sélectionné."))

        # Créer un classeur
        wb = Workbook()
        ws = wb.active
        ws.title = "Détails"

        # Définir les styles
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # En-têtes du tableau consolidé
        headers = [
            "Date",
            "Clôture Ref",
            "Point de Vente",
            "Mode de Paiement",
            "Contrôle Physique",
            "Etat ERP",
            "Balance",
            "Commission",
            "Écart",
            "Type",
        ]

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

        # Remplir les données de toutes les clôtures
        row = 2
        for doc in self:
            for line in doc.line_ids:
                type_ecart_label = line.type_ecart
                if line.type_ecart == 'excedent':
                    type_ecart_label = 'Excédent'
                elif line.type_ecart == 'manquant':
                    type_ecart_label = 'Manquant'
                elif line.type_ecart == 'bravo':
                    type_ecart_label = 'Équilibré'

                row_data = [
                    doc.date.strftime("%d/%m/%Y") if doc.date else "",
                    doc.name,
                    doc.pos_config_id.name,
                    line.label,
                    line.controle_physique,
                    line.etat_erp,
                    line.balance,
                    line.commission,
                    line.ecart,
                    type_ecart_label,
                ]

                for col_num, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row, column=col_num)
                    if col_num <= 3:  # Date, Ref, PdV
                        cell.value = value
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                    elif col_num == 4:  # Mode de paiement
                        cell.value = value
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                    else:
                        if isinstance(value, (int, float)):
                            cell.value = value
                            cell.number_format = '0.00'
                            cell.alignment = Alignment(horizontal="right", vertical="center")
                        else:
                            cell.value = value
                            cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = border

                row += 1

        # Ajuster les largeurs des colonnes
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 18
        ws.column_dimensions['E'].width = 16
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 12
        ws.column_dimensions['H'].width = 14
        ws.column_dimensions['I'].width = 12
        ws.column_dimensions['J'].width = 12

        # Créer un deuxième onglet pour le résumé
        ws_summary = wb.create_sheet("Résumé")

        summary_headers = [
            "Date",
            "Clôture Ref",
            "Point de Vente",
            "Total Physique",
            "Total ERP",
            "Total Balance",
            "Total Commission",
            "Manquant Final",
            "Statut",
        ]

        for col_num, header in enumerate(summary_headers, 1):
            cell = ws_summary.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

        # Remplir le résumé
        row = 2
        for doc in self:
            state_label = 'Brouillon'
            if doc.state == 'confirmed':
                state_label = 'Confirmé'
            elif doc.state == 'approved':
                state_label = 'Approuvé'

            summary_data = [
                doc.date.strftime("%d/%m/%Y") if doc.date else "",
                doc.name,
                doc.pos_config_id.name,
                doc.total_physique,
                doc.total_erp,
                doc.total_balance,
                doc.total_commission,
                doc.manquant_finale,
                state_label,
            ]

            for col_num, value in enumerate(summary_data, 1):
                cell = ws_summary.cell(row=row, column=col_num)
                if col_num <= 3:
                    cell.value = value
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                elif col_num == 9:  # Statut
                    cell.value = value
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    if isinstance(value, (int, float)):
                        cell.value = value
                        cell.number_format = '0.00'
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.border = border

            row += 1

        # Ajuster les largeurs du résumé
        ws_summary.column_dimensions['A'].width = 12
        ws_summary.column_dimensions['B'].width = 12
        ws_summary.column_dimensions['C'].width = 18
        ws_summary.column_dimensions['D'].width = 15
        ws_summary.column_dimensions['E'].width = 12
        ws_summary.column_dimensions['F'].width = 15
        ws_summary.column_dimensions['G'].width = 16
        ws_summary.column_dimensions['H'].width = 14
        ws_summary.column_dimensions['I'].width = 12

        # Générer le fichier
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        file_data = output.getvalue()

        # Créer l'attachement
        filename = f"clotures_consolidees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'res_model': 'cloture.caisse',
        })

        # Retourner l'URL de téléchargement
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_export_to_excel(self):
        """Exporte la liste des clôtures de caisse au format Excel."""
        import io
        import base64
        from datetime import datetime

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        except ImportError:
            raise UserError(_("La bibliothèque openpyxl n'est pas installée."))

        # Créer un classeur
        wb = Workbook()
        ws = wb.active
        ws.title = "Clôtures de Caisse"

        # Définir les styles
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # En-têtes
        headers = [
            "Référence",
            "Date",
            "Point de Vente",
            "Session POS",
            "Manager",
            "Caissier",
            "Total Physique",
            "Total ERP",
            "Total Commission",
            "Manquant Final",
            "Statut",
        ]

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_alignment
            cell.border = border

        # Remplir les données
        for row_num, record in enumerate(self, 2):
            state_label = dict(record._fields['state'].selection).get(record.state, record.state)
            row_data = [
                record.name,
                record.date.strftime("%d/%m/%Y") if record.date else "",
                record.pos_config_id.name,
                record.session_id.name if record.session_id else "",
                record.manager_id.name,
                record.caissier_id.name if record.caissier_id else "",
                record.total_physique,
                record.total_erp,
                record.total_commission,
                record.manquant_finale,
                state_label,
            ]

            for col_num, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = value
                cell.border = border
                if col_num >= 7 and col_num <= 10:  # Colonnes numériques
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = '0.00'
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

        # Ajuster la largeur des colonnes
        column_widths = [12, 12, 20, 15, 15, 15, 15, 15, 18, 15, 15]
        for idx, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + idx)].width = width

        # Générer le fichier
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        file_data = output.getvalue()

        # Créer l'attachement
        filename = f"clotures_caisse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'res_model': 'cloture.caisse',
        })

        # Retourner l'URL de téléchargement
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class ClotureCaisseLine(models.Model):
    _name = 'cloture.caisse.line'
    _description = 'Ligne de Clôture de Caisse'
    _order = 'is_remboursement, id'

    cloture_id = fields.Many2one(
        'cloture.caisse', string='Clôture', required=True, ondelete='cascade'
    )
    payment_method_id = fields.Many2one(
        'pos.payment.method', string='Mode de Paiement'
    )
    is_remboursement = fields.Boolean(string='Total Remboursement', default=False)

    # Label affiché dans le tableau
    label = fields.Char(
        string='Mode de Paiement', compute='_compute_label', store=True
    )

    controle_physique = fields.Float(
        string='Contrôle Physique', digits=(15, 2)
    )
    etat_erp = fields.Float(
        string='Etat ERP', digits=(15, 2),
        help="Ligne Total Remboursement : saisie manuelle du manager (montant negatif). "
             "A defaut, reprend uniquement les remboursements des retours produits de la session."
    )
    saisie_manuelle = fields.Boolean(
        string='Saisie manuelle', default=False, copy=False,
        help="Coche quand le manager a saisi lui-meme le total des remboursements."
    )
    balance = fields.Float(
        compute='_compute_amounts', string='Balance', store=True, digits=(15, 2)
    )
    has_commission = fields.Boolean(string='Commission ?', default=False)
    taux_commission = fields.Float(
        string='Taux Commission (%)', digits=(5, 2)
    )
    commission = fields.Float(
        compute='_compute_amounts', string='Commission Paiement', store=True, digits=(15, 2)
    )
    ecart = fields.Float(
        compute='_compute_amounts', string='Ecart ou Manquant', store=True, digits=(15, 2)
    )
    type_ecart = fields.Selection([
        ('none', '—'),
        ('excedent', 'Excédent'),
        ('manquant', 'Manquant'),
        ('bravo', 'Équilibré ✓'),
    ], compute='_compute_type_ecart', string='Type Écart', store=True, default='none')
    remboursement_state = fields.Selection([
        ('none', '—'),
        ('a_rembourser', 'À Rembourser'),
        ('non_remboursable', 'Non Remboursable'),
    ], string='Statut Manquant', default='none')

    def write(self, vals):
        # Le manager modifie le total des remboursements : on le garde au rechargement
        if 'etat_erp' in vals and 'saisie_manuelle' not in vals                 and not self.env.context.get('cloture_loading'):
            refunds = self.filtered('is_remboursement')
            if refunds:
                super(ClotureCaisseLine, refunds).write(dict(vals, saisie_manuelle=True))
                others = self - refunds
                return super(ClotureCaisseLine, others).write(vals) if others else True
        return super().write(vals)

    @api.depends('payment_method_id', 'is_remboursement')
    def _compute_label(self):
        for line in self:
            if line.is_remboursement:
                line.label = 'Total Remboursement'
            else:
                line.label = line.payment_method_id.name or ''

    @api.depends('controle_physique', 'etat_erp', 'has_commission',
                 'taux_commission', 'is_remboursement')
    def _compute_amounts(self):
        for line in self:
            if line.is_remboursement:
                # Remboursement : contrôle physique toujours 0, ERP = montant remboursé
                line.balance = -line.etat_erp
                line.commission = 0.0
            else:
                # Balance = Physique - ERP
                line.balance = line.controle_physique - line.etat_erp

                # Commission calculée si applicable (gross-up : physique * taux / (100 - taux))
                if line.has_commission and line.taux_commission and line.taux_commission < 100:
                    line.commission = float_round(
                        (line.controle_physique * line.taux_commission) / (100 - line.taux_commission), 2)
                else:
                    line.commission = 0.0

            # Formule de l'Écart signé = Balance + Commission
            # Positif = excédent, Négatif = manquant, Zéro = équilibré
            line.ecart = float_round(line.balance + line.commission, 2)

    @api.depends('ecart', 'is_remboursement')
    def _compute_type_ecart(self):
        for line in self:
            if line.is_remboursement:
                line.type_ecart = 'none'
            elif line.ecart == 0:
                line.type_ecart = 'bravo'
            elif line.ecart > 0:
                line.type_ecart = 'excedent'
            else:
                line.type_ecart = 'manquant'