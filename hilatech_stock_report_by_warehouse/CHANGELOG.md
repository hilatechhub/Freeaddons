# Changelog - Rapport de Stock par Emplacement

## Version 19.0.3.0.0 - Mouvements de Stock Global (Emplacements + Ajustements + Pertes)

### Nouvelles Fonctionnalités

#### 1. **Détail par Type d'Emplacement**
Le rapport affiche maintenant 3 colonnes par entrepôt:
- **Emplacement Interne** : Stock en emplacements de gestion (usage='internal')
- **Ajustement/Inventaire** : Stock en emplacements d'ajustement (usage='inventory')
- **Perte** : Stock en emplacements de perte/hors bilan (customer, supplier, production)

#### 2. **Vue Pivot Détaillée**
```
Mois/Année 
├─ Catégorie
│  └─ Produit
     [Entrepôt A]           [Entrepôt B]
     Interne | Ajustement | Perte | Interne | Ajustement | Perte | TOTAL
```

#### 3. **Colonnes Additionnelles**
- `location_id` : Référence à l'emplacement spécifique
- `location_type` : Type d'emplacement (internal, adjustment, loss, other)

#### 4. **Rapports Améliorés**
- **PDF** : Tableau avec 3 sous-colonnes par entrepôt (Interne, Ajustement, Perte)
- **Excel** : En-têtes sur 2 lignes avec fusion de cellules pour meilleure lisibilité
  - Ligne 1 : Nom de l'entrepôt (fusionné sur 3 colonnes)
  - Ligne 2 : Type d'emplacement (Interne, Ajustement, Perte)

### Vue du Stock Global

Vous pouvez maintenant voir:
- ✅ Stock en emplacements internes (disponible pour vente/production)
- ✅ Stock en ajustement (hors exploitation temporaire)
- ✅ Stock en perte (produits hors bilan)
- ✅ **Total par entrepôt** = Interne + Ajustement + Perte

### Exemple de Tableau PDF

```
┌─────────────┬──────────────┬────┬─────────────────────────┬─────────────────────────┐
│   Produit   │  Catégorie   │ U.M│ Entrepôt A              │ Entrepôt B              │
│             │              │    │ Int | Adj | Perte │ Tot │ Int | Adj | Perte │ Tot │
├─────────────┼──────────────┼────┼─────────────────────────┼─────────────────────────┤
│ Produit XYZ │ Électronique │ Pc │ 100 │ 5  │  2   │ 107 │ 80  │ 10 │  1   │ 91  │
│ Produit ABC │ Alimentation │ Kg │ 500 │ 20 │  5   │ 525 │ 300 │ 15 │  3   │ 318 │
├─────────────┴──────────────┴────┴─────────────────────────┴─────────────────────────┤
│ TOTAL                              │ 600 │ 25 │  7   │ 632 │ 380 │ 25 │  4   │ 409 │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Version 19.0.2.0.0 - Filtres de Date et Regroupement par Mois

### Nouvelles Fonctionnalités

#### 1. **Filtres de Date**
- **Stock Actuel** : Affiche le stock en temps réel (sans filtre)
- **Stock à une Date Fixe** : Permet de sélectionner une date spécifique pour voir le stock à ce moment-là
- **Plage de Dates** : Permet de sélectionner une période avec regroupement par mois/année

#### 2. **Interface de Filtre**
- Nouveau formulaire transient `stock.inventory.filter` avec 3 modes de filtrageAccessible via :
  - Menu Action "Filtrer par Date" dans le rapport
  - Bouton d'action dans la barre d'outils
- Options :
  - Voir le Rapport avec les filtres
  - Exporter en PDF avec les filtres
  - Exporter en Excel avec les filtres

#### 3. **Vue Pivot Améliorée**
- Ajout du regroupement par **Mois/Année** en première ligne
- Structure : Mois > Catégorie > Produit (lignes), Entrepôt (colonnes)
- Permet d'analyser les tendances mensuelles du stock

#### 4. **Rapport PDF et Excel**
- Le titre affiche maintenant la date du rapport filtrée
- Exemple: "RAPPORT DE STOCK PAR ENTREPÔT du 31/12/2025"
- Affichage de la période si applicable

#### 5. **Colonnes Additionnelles**
- `date_filter` : Date du stock affichée
- `month_year` : Format MM/YYYY pour regroupement

### Modifications Techniques

**Fichiers Modifiés :**
- `__manifest__.py` : Ajout de la nouvelle vue de filtre
- `models/stock_inventory_report.py` : Ajout des champs et de la logique de filtre
- `models/__init__.py` : Import du nouveau modèle transient
- `views/stock_inventory_report_views.xml` : Ajout regroupement par mois, colonnes dates
- `report/report_stock_inventory_template.xml` : Affichage date filtrée
- `report/report_stock_inventory_action.xml` : Action serveur pour ouvrir le filtre
- `security/ir.model.access.csv` : Droits d'accès pour le filtre

**Fichiers Créés :**
- `models/stock_inventory_filter.py` : Modèle transient pour les filtres
- `views/stock_inventory_filter_views.xml` : Interface de filtre

### Utilisation

1. **Ouvrir le Rapport**
   - Menu : Inventaire > Reporting > Rapport de stock

2. **Appliquer un Filtre**
   - Cliquer sur l'action "Filtrer par Date" (bouton dans la barre d'outils)
   - Sélectionner le type de filtre :
     - **Stock Actuel** : Vue en temps réel
     - **Stock à une Date Fixe** : Saisir la date
     - **Plage de Dates** : Saisir date début et fin, cocher "Regrouper par Mois"

3. **Voir le Rapport**
   - Cliquer "Voir le Rapport" pour rafraîchir avec les nouveaux filtres
   - Cliquer "PDF" pour télécharger le rapport filtrée en PDF
   - Cliquer "Excel" pour télécharger le rapport filtrée en Excel

### Exemple de Scenarios

**Scenario 1 : État actuel du stock**
- Filtre : Stock Actuel
- Vue : Stock en temps réel par emplacement

**Scenario 2 : Stock à fin de mois**
- Filtre : Stock à une Date Fixe
- Date : 31/01/2025
- Résultat : État du stock au 31/01/2025

**Scenario 3 : Évolution par mois**
- Filtre : Plage de Dates
- Dates : 01/01/2025 - 31/03/2025
- Regrouper par Mois : ✓
- Vue : Stock par mois (JAN, FEV, MAR) et par emplacement

### Notes

- Le stock affiché reste basé sur `stock_quant` (état actuel)
- Pour un calcul historique complet (via `stock_move`), une version future peut être ajoutée
- Les dates sont stockées en tant que contexte pour flexibilité
- Compatible avec les exports Excel et PDF existants

### Permissions

- Groupe `stock.group_stock_user` : Accès lecture + utilisation du filtre
- Groupe `stock.group_stock_manager` : Accès complet
