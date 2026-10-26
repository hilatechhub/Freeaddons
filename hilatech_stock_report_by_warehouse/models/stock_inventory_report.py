import base64
import io
import logging
from datetime import datetime, timedelta

from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockInventoryReport(models.Model):
    _name = 'stock.inventory.report'
    _description = 'Rapport de Stock par Entrepôt'
    _auto = False
    _rec_name = 'product_id'
    _order = 'product_id, warehouse_id'
    _log_access = False

    product_id = fields.Many2one('product.product', string='Produit', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Modèle Produit', readonly=True)
    default_code = fields.Char(string='Référence', readonly=True)
    categ_id = fields.Many2one('product.category', string='Catégorie', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Entrepôt', readonly=True)
    location_id = fields.Many2one('stock.location', string='Emplacement', readonly=True)
    location_type = fields.Selection([
        ('internal', 'Emplacement Interne'),
        ('adjustment', 'Ajustement/Inventaire'),
        ('loss', 'Perte'),
        ('other', 'Autre'),
    ], string='Type d\'Emplacement', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='Unité de Mesure', readonly=True)
    quantity = fields.Float(string='Qté en Stock', readonly=True)
    reserved_quantity = fields.Float(string='Qté Réservée', readonly=True)
    available_quantity = fields.Float(string='Qté Disponible', readonly=True)
    total_available_quantity = fields.Float(string='Total Dispo (tous entrepôts)', readonly=True)
    # Stock en temps réel : date du jour, affichée dans le titre des exports
    date_filter = fields.Date(string='Date du Stock', readonly=True)

    def _query(self):
        return """
            SELECT
                ROW_NUMBER() OVER (ORDER BY sq.product_id, sl.warehouse_id, sl.id)     AS id,
                sq.product_id                                                           AS product_id,
                pp.product_tmpl_id                                                      AS product_tmpl_id,
                pp.default_code                                                         AS default_code,
                ptmpl.categ_id                                                          AS categ_id,
                sl.warehouse_id                                                         AS warehouse_id,
                sl.id                                                                   AS location_id,
                CASE
                    WHEN sl.usage = 'internal' THEN 'internal'
                    WHEN sl.usage = 'inventory' THEN 'adjustment'
                    WHEN sl.usage IN ('customer', 'supplier', 'production') THEN 'loss'
                    ELSE 'other'
                END                                                                      AS location_type,
                ptmpl.uom_id                                                            AS uom_id,
                SUM(COALESCE(sq.quantity, 0))                                           AS quantity,
                SUM(COALESCE(sq.reserved_quantity, 0))                                  AS reserved_quantity,
                SUM(COALESCE(sq.quantity, 0))
                    - SUM(COALESCE(sq.reserved_quantity, 0))                            AS available_quantity,
                (SELECT SUM(COALESCE(sq2.quantity, 0)) - SUM(COALESCE(sq2.reserved_quantity, 0))
                 FROM stock_quant sq2
                 JOIN stock_location sl2 ON sl2.id = sq2.location_id
                 WHERE sl2.usage IN ('internal', 'inventory')
                   AND sl2.warehouse_id IS NOT NULL
                   AND sq2.product_id = sq.product_id)                                 AS total_available_quantity,
                CURRENT_DATE::date                                                      AS date_filter
            FROM stock_quant sq
            JOIN product_product pp      ON pp.id = sq.product_id
            JOIN product_template ptmpl  ON ptmpl.id = pp.product_tmpl_id
            JOIN stock_location sl       ON sl.id = sq.location_id
            WHERE sl.usage IN ('internal', 'inventory')
              AND sl.warehouse_id IS NOT NULL
              AND ptmpl.active = true
              AND pp.active = true
            GROUP BY
                sq.product_id,
                pp.product_tmpl_id,
                pp.default_code,
                ptmpl.categ_id,
                sl.warehouse_id,
                sl.id,
                sl.usage,
                ptmpl.uom_id
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE VIEW %s AS (%s)""" % (self._table, self._query()))

    def _get_pivot_data(self):
        """Prépare les données pivot par entrepôt : {product_id: {warehouse_id: qty}}."""
        records = self if self else self.env['stock.inventory.report'].search([])
        warehouses = records.mapped('warehouse_id').sorted('name')
        products = records.mapped('product_id').sorted('display_name')

        pivot = {}
        product_meta = {}
        for rec in records:
            pid = rec.product_id.id
            wid = rec.warehouse_id.id

            if pid not in pivot:
                pivot[pid] = {}
                product_meta[pid] = {
                    'product': rec.product_id,
                    'categ': rec.categ_id,
                    'uom': rec.uom_id,
                    'default_code': rec.default_code or '',
                }

            # Stock physique (quantité en main) : la quantité réservée par des
            # transferts non validés ne doit pas diminuer le stock réel affiché.
            pivot[pid][wid] = pivot[pid].get(wid, 0.0) + rec.quantity

        return {
            'warehouses': warehouses,
            'products': products,
            'pivot': pivot,
            'product_meta': product_meta,
        }

    def action_print_pdf(self):
        """Imprime le rapport pivot en PDF."""
        records = self if self else self.env['stock.inventory.report'].search([])
        return (
            self.env.ref('hilatech_stock_report_by_warehouse.action_report_stock_inventory_pdf')
            .report_action(records)
        )

    def action_export_xlsx(self):
        """Génère et télécharge le rapport pivot au format XLSX."""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
        except ImportError:
            raise UserError(_(
                "La bibliothèque openpyxl est requise pour l'export Excel. "
                "Veuillez contacter votre administrateur système."
            ))

        from datetime import datetime

        # Couleurs charte graphique rouge
        RED_DARK   = 'C0392B'   # en-têtes principaux
        RED_DARKER = '7B241C'   # en-tête Total Dispo
        RED_LIGHT  = 'FADBD8'   # ligne totaux
        RED_TOTAL  = 'F1948A'   # grand total
        RED_ALT    = 'FFF5F5'   # ligne alternée

        # Lignes exportées (titre et période lus sur la première ligne plus bas)
        records = self if self else self.env['stock.inventory.report'].search([])
        data = records._get_pivot_data()
        warehouses = data['warehouses']
        products = data['products']
        pivot = data['pivot']
        product_meta = data['product_meta']

        output = io.BytesIO()
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Rapport de Stock'

        # Styles
        hdr_font   = Font(name='Arial', bold=True, color='FFFFFF', size=10)
        hdr_fill   = PatternFill(start_color=RED_DARK, end_color=RED_DARK, fill_type='solid')
        hdr_align  = Alignment(horizontal='center', vertical='center', wrap_text=True)
        total_font = Font(name='Arial', bold=True, size=10)
        total_fill = PatternFill(start_color=RED_LIGHT, end_color=RED_LIGHT, fill_type='solid')
        thin = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin'),
        )
        right_al  = Alignment(horizontal='right', vertical='center')

        # Calcul du nombre de colonnes : 3 fixes + warehouses + 1 total
        nb_cols = 3 + len(warehouses) + 1
        end_col = get_column_letter(nb_cols)

        # ── Logo société (lignes 1-3) ─────────────────────────────────────
        LOGO_ROW_HEIGHT = 25
        for r in range(1, 4):
            worksheet.row_dimensions[r].height = LOGO_ROW_HEIGHT

        try:
            from openpyxl.drawing.image import Image as XLImage
            logo_b64 = self.env.company.logo
            if logo_b64:
                logo_data = base64.b64decode(logo_b64)
                logo_io = io.BytesIO(logo_data)
                logo_img = XLImage(logo_io)
                logo_img.height = 70
                logo_img.width = 140
                worksheet.add_image(logo_img, 'A1')
        except Exception as e:
            _logger.warning("Impossible d'ajouter le logo dans l'Excel : %s", e)

        # ── Titre (ligne 4) ───────────────────────────────────────────────
        worksheet.merge_cells(f'A4:{end_col}4')
        title_cell = worksheet['A4']

        # Déterminer le titre en fonction du filtre de date
        title_text = 'RAPPORT DE STOCK PAR ENTREPÔT'
        if records and records[0].date_filter:
            title_text += f" du {records[0].date_filter.strftime('%d/%m/%Y')}"

        title_cell.value = title_text
        title_cell.font = Font(name='Arial', bold=True, size=13, color=RED_DARK)
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        worksheet.row_dimensions[4].height = 28

        # ── Date (ligne 5) ────────────────────────────────────────────────
        worksheet.merge_cells(f'A5:{end_col}5')
        date_cell = worksheet['A5']

        date_cell.value = f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        date_cell.font = Font(name='Arial', italic=True, size=9, color='555555')
        date_cell.alignment = Alignment(horizontal='right')

        # ── En-têtes principaux (ligne 7) ────────────────────────────────────────────
        HDR_ROW = 7
        worksheet.row_dimensions[HDR_ROW].height = 28

        fixed_headers = [('Produit', 42), ('Catégorie', 22), ('U.M.', 10)]
        for col_idx, (header_text, col_width) in enumerate(fixed_headers, 1):
            cell = worksheet.cell(row=HDR_ROW, column=col_idx, value=header_text)
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = hdr_align
            cell.border = thin
            worksheet.column_dimensions[get_column_letter(col_idx)].width = col_width

        wh_start_col = 4
        wh_col_idx = wh_start_col

        # Afficher les en-têtes d'entrepôts (1 colonne par entrepôt)
        for wh in warehouses:
            cell = worksheet.cell(row=HDR_ROW, column=wh_col_idx, value=wh.name)
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = hdr_align
            cell.border = thin
            worksheet.column_dimensions[get_column_letter(wh_col_idx)].width = 14
            wh_col_idx += 1

        # En-tête Total Dispo
        total_col = wh_start_col + len(warehouses)
        total_hdr_fill = PatternFill(start_color=RED_DARKER, end_color=RED_DARKER, fill_type='solid')
        cell = worksheet.cell(row=HDR_ROW, column=total_col, value='Total Stock')
        cell.font = hdr_font
        cell.fill = total_hdr_fill
        cell.alignment = hdr_align
        cell.border = thin
        worksheet.column_dimensions[get_column_letter(total_col)].width = 14

        # ── Données (à partir de la ligne 8) ─────────────────────────────
        row_idx = HDR_ROW + 1
        wh_totals = {wh.id: 0.0 for wh in warehouses}
        grand_total = 0.0

        for product in products:
            pid = product.id
            if pid not in product_meta:
                continue

            meta = product_meta[pid]
            prod_total_check = sum(
                pivot.get(pid, {}).get(wh.id, 0.0)
                for wh in warehouses
            )

            if prod_total_check < 5:
                row_fill_color = 'FFCCCC'
            elif row_idx % 2 == 0:
                row_fill_color = RED_ALT
            else:
                row_fill_color = 'FFFFFF'
            row_fill = PatternFill(start_color=row_fill_color, end_color=row_fill_color, fill_type='solid')

            fixed_data = [
                product.display_name,
                meta['categ'].name if meta['categ'] else '',
                meta['uom'].name if meta['uom'] else '',
            ]
            for col_idx, value in enumerate(fixed_data, 1):
                cell = worksheet.cell(row=row_idx, column=col_idx, value=value)
                cell.border = thin
                cell.fill = row_fill
                cell.font = Font(name='Arial', size=10)
                cell.alignment = Alignment(vertical='center')

            prod_total = 0.0
            wh_col_idx = wh_start_col
            for wh in warehouses:
                qty = pivot.get(pid, {}).get(wh.id, 0.0)
                wh_totals[wh.id] += qty
                prod_total += qty
                cell = worksheet.cell(row=row_idx, column=wh_col_idx, value=qty if qty else 0.0)
                cell.border = thin
                cell.fill = row_fill
                cell.font = Font(name='Arial', size=10)
                cell.alignment = right_al
                cell.number_format = '#,##0.000'
                wh_col_idx += 1

            grand_total += prod_total
            if prod_total < 5:
                total_prod_fill = PatternFill(start_color='FF9999', end_color='FF9999', fill_type='solid')
            else:
                total_prod_fill = PatternFill(
                    start_color='F9EBEA' if row_idx % 2 == 0 else 'FADBD8',
                    end_color='F9EBEA' if row_idx % 2 == 0 else 'FADBD8',
                    fill_type='solid',
                )
            cell = worksheet.cell(row=row_idx, column=total_col, value=prod_total)
            cell.border = thin
            cell.fill = total_prod_fill
            cell.font = Font(name='Arial', size=10, bold=True)
            cell.alignment = right_al
            cell.number_format = '#,##0.000'

            row_idx += 1

        # ── Ligne totaux ──────────────────────────────────────────────────
        total_row_data = ['TOTAL', '', '']
        for col_idx, value in enumerate(total_row_data, 1):
            cell = worksheet.cell(row=row_idx, column=col_idx, value=value)
            cell.font = total_font
            cell.fill = total_fill
            cell.border = thin
            if col_idx == 1:
                cell.alignment = Alignment(horizontal='right', vertical='center')

        wh_col_idx = wh_start_col
        for wh in warehouses:
            qty_total = wh_totals.get(wh.id, 0.0)
            cell = worksheet.cell(row=row_idx, column=wh_col_idx, value=qty_total)
            cell.font = total_font
            cell.fill = total_fill
            cell.border = thin
            cell.alignment = right_al
            cell.number_format = '#,##0.000'
            wh_col_idx += 1

        grand_fill = PatternFill(start_color=RED_TOTAL, end_color=RED_TOTAL, fill_type='solid')
        cell = worksheet.cell(row=row_idx, column=total_col, value=grand_total)
        cell.font = Font(name='Arial', bold=True, size=10)
        cell.fill = grand_fill
        cell.border = thin
        cell.alignment = right_al
        cell.number_format = '#,##0.000'

        worksheet.freeze_panes = f'A{HDR_ROW + 1}'

        workbook.save(output)
        xlsx_data = base64.b64encode(output.getvalue())

        attachment = self.env['ir.attachment'].create({
            'name': 'rapport_stock_%s.xlsx' % datetime.now().strftime('%Y%m%d_%H%M'),
            'type': 'binary',
            'datas': xlsx_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % attachment.id,
            'target': 'new',
        }
