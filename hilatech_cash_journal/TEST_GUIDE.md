# 🧪 Guide de Test - Module Cash Journal

## ✅ Checklist de Vérification Avant Test

- [x] Syntaxe Python validée
- [x] Fichiers XML structurés correctement
- [x] Structure du module complète
- [x] Modèles définis avec champs requis
- [x] Sécurité configurée (2 groupes + permissions)
- [x] Séquence créée (JRN/YYYY/NNNNN)
- [x] Vues créées (list, form, search, action, menus)

---

## 📦 Installation du Module

### Via Docker (Recommended)
```bash
# 1. Terminal - Dans le répertoire racine okukoresto
docker-compose restart odoo

# 2. Interface Odoo - Paramètres → Modules locaux
#    - Cliquer "Rafraîchir la liste"
#    - Chercher: "Cash Journal"
#    - Installer le module
```

### Ou manuellement via Odoo
```
Paramètres → Applications → Modules locaux
Rafraîchir → Chercher "Cash Journal" → Installer
```

---

## 🎯 Scénario de Test Complet

### Phase 1 : Création du Relevé

**Étapes** :
```
1. Menu: Journal de Caisse → Relevés de Caisse
2. Bouton Créer

Remplir le formulaire:
├─ Mois du Relevé: 2026-03-01 (ou 1er du mois courant)
├─ Solde Initial: 10000.00
└─ Cliquer Enregistrer

✓ Expected: Numéro auto-généré (format: JRN/2026/00001)
```

### Phase 2 : Ouvrir la Caisse

**Étapes** :
```
1. Dans le formulaire du relevé créé
2. Cliquer bouton "Ouvrir la caisse"
3. Rafraîchir la page (F5)

✓ Expected Visuel:
   - Bouton "Ouvrir la caisse" = INVISIBLE
   - Bouton "Clôturer caisse du jour" = VISIBLE & ACTIF
   - État caisse = "Caisse Ouverte" (badge vert)
   - Solde final affiché: 10000.00 (= solde initial)
```

### Phase 3 : Ajouter Opérations

**Étapes** :
```
1. Onglet "Opérations du Mois"
2. Cliquer "Ajouter une ligne" (ou éditer en bas)

OPÉRATION 1 - ENTRÉE:
├─ Date: 2026-03-01
├─ Description: Dépôt du client Martin
├─ Reçu par: [Sélectionner un contact/partenaire]
├─ Montant: 5000.00
└─ Ligne couleur: VERTE (decoration-success)

OPÉRATION 2 - ENTRÉE:
├─ Date: 2026-03-01
├─ Description: Encaissement chèque XYZ
├─ Reçu par: [Contact]
├─ Montant: 2500.00
└─ Ligne couleur: VERTE

OPÉRATION 3 - SORTIE:
├─ Date: 2026-03-01
├─ Description: Achat fournitures papier
├─ Reçu par: [Fournisseur ABC]
├─ Montant: -1000.00
└─ Ligne couleur: ROUGE (decoration-danger)

3. Enregistrer le formulaire

✓ Expected:
   - Solde Final = 10000 + 5000 + 2500 - 1000 = 16500.00
   - Montants visibles en bas avec "Total: 6500.00"
   - Aucune ligne n'est grisée (is_locked = False)
```

### Phase 4 : Clôturer la Caisse du Jour

**Étapes** :
```
1. Cliquer bouton "Clôturer la caisse du jour"
2. Confirmer le dialogue popup

✓ Expected:
   - Message: "Caisse clôturée... Solde final: 16500.00"
   - Les 3 opérations deviennent GRISÉES (decoration-muted)
   - Champ "Verrouillée" = TRUE pour chaque ligne
   - État caisse = "Caisse Fermée" (badge rouge)
   - Bouton "Clôturer caisse du jour" = INVISIBLE
   - Bouton "Ouvrir la caisse" = VISIBLE & ACTIF
```

### Phase 5 : Tenter Modification (Doit Échouer)

**Étapes** :
```
1. Dans les opérations, essayer de:
   - Modifier la description de la ligne 1
   - OU cliquer suppression (X)

✓ Expected ERROR:
   Popup: "Cette opération est verrouillée et ne peut pas être modifiée..."
```

### Phase 6 : Ouvrir Caisse Suivante

**Étapes** :
```
1. Cliquer "Ouvrir la caisse"
2. Ajouter nouvelle opération:
   - Date: 2026-03-02
   - Description: Dépôt jour 2
   - Montant: +3000.00

✓ Expected:
   - Anciennes opérations (03-01) = GRISÉES (still locked)
   - Nouvelle opération (03-02) = NOIRE (normal)
   - Solde Final = 16500 + 3000 = 19500.00
```

### Phase 7 : Clôturer le Relevé Mensuel

**Étapes** :
```
1. Cliquer "Clôturer le relevé mensuel"
2. Confirmer dialogue "Action irréversible"

✓ Expected:
   - État du relevé = "Clôturé"
   - Tous les boutons = INVISIBLE (greyed out)
   - Toutes les opérations = GRISÉES (readonly)
   - Message: "Relevé mensuel clôturé définitivement..."
   - Dans liste: État = "Clôturé" (badge vert)
```

---

## 🐛 Tests de Validation (Edge Cases)

### Test A : Contrainte Date
```
1. Créer opération avec date future (2026-12-31)
2. Enregistrer

✓ Expected ERROR: "La date ne peut pas être dans le futur"
```

### Test B : Contrainte Montant Zéro
```
1. Ajouter opération avec Montant: 0.00
2. Enregistrer

✓ Expected ERROR: "Le montant doit être différent de zéro"
```

### Test C : Date Hors du Mois
```
1. Relevé pour Mars 2026
2. Ajouter opération avec date Février 2026

✓ Expected ERROR: "La date doit être dans le mois du relevé"
```

### Test D : Deux Relevés Même Mois
```
1. Créer relevé #1 pour Mars 2026 (état: ouvert)
2. Créer relevé #2 pour Mars 2026

✓ Expected ERROR: "Un relevé ouvert existe déjà pour le mois"
(Après clôture du #1, le #2 peut être créé)
```

### Test E : Permissions
```
1. Connecter avec utilisateur groupe "Cash Journal - Utilisateur"
2. Vérifier: CAN CREATE, CAN READ, CAN WRITE, CANNOT DELETE

3. Connecter avec groupe "Cash Journal - Gestionnaire"
4. Vérifier: CAN CREATE, CAN READ, CAN WRITE, CAN DELETE
```

---

## 📊 Vérifications Visuelles

- [ ] Menu "Journal de Caisse" visible dans la nav principale
- [ ] Sous-menu "Relevés de Caisse" présent
- [ ] Liste affiche: name, month_date, initial_balance, final_balance, state, caisse_state
- [ ] Coleurs de décoration:
  - Relevé clôturé = ligne VERTE
  - Relevé ouvert + caisse ouvert = ligne BLEUE
  - Relevé ouvert + caisse fermé = ligne JAUNE
- [ ] Opérations entrées = VERTES (amount > 0)
- [ ] Opérations sorties = ROUGES (amount < 0)
- [ ] Opérations verrouillées = GRISÉES

---

## 🔍 Logs & Débogage

### Logs Odoo
```bash
# Terminal - Pour voir les erreurs en temps réel
docker-compose logs -f odoo

# Chercher: "ERROR", "WARNING", "except"
```

### Mode Debug Navigateur
```
1. Chrome: F12 → Console
2. Chercher erreurs JavaScript
3. Onglet Network: vérifier appels API
```

### Requête API Directe (Avancé)
```bash
curl -X POST http://localhost:8069/api/models/cash.journal.report \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "model": "cash.journal.report",
      "method": "fields_get",
      "args": [[], ["string", "type", "help"]],
    }
  }'
```

---

## ✨ Résumé des Résultats Attendus

| Étape | Action | Résultat Attendu | Status |
|-------|--------|------------------|--------|
| 1 | Créer relevé | Numéro auto (JRN/2026/00001) | ✅ |
| 2 | Ouvrir caisse | État = Caisse Ouverte | ✅ |
| 3 | Ajouter opérations | Solde final mis à jour | ✅ |
| 4 | Clôturer jour | Opérations verrouillées | ✅ |
| 5 | Modifier opération | ERROR "verrouillée" | ✅ |
| 6 | Ouvrir caisse | Nouvelles opérations possibles | ✅ |
| 7 | Clôturer relevé | État = Clôturé définitif | ✅ |
| 8 | Permissions | User/Manager respectées | ✅ |

---

## 📝 Notes

- Tous les champs de date utilisent `default=fields.Date.context_today`
- Le solde final est COMPUTÉ (store=True) donc toujours à jour
- Les messages POST du chatter trackent les actions
- Le tracking=True permet de voir l'historique des changements d'état

---

## 🚀 Support

Si erreurs rencontrées:
1. Vérifier logs Docker: `docker-compose logs odoo`
2. Vérifier permissions: Paramètres → Utilisateurs et droits d'accès
3. Vérifier installation: Paramètres → Modules locaux (search "Cash Journal")

Bonne chance ! 🍀
