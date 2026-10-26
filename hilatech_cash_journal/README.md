# 💰 Module Journal de Caisse - hilatech_cash_journal

**Version:** 19.0.1.0.0 | **Odoo:** 19 | **Status:** ✅ Prêt à tester

## 🎯 Description

Module complet de gestion du flux de caisse d'une entreprise permettant :

✅ **Relevés mensuels** avec solde initial et final calculé automatiquement
✅ **Opérations quotidiennes** (entrées/sorties avec montant signé)
✅ **Workflow quotidien** intuitif : Ouvrir caisse → Saisir opérations → Clôturer caisse
✅ **Verrouillage automatique** des opérations après clôture du jour
✅ **Protection des données** : opérations verrouillées non modifiables
✅ **Gestion des permissions** avec 2 rôles (Utilisateur & Gestionnaire)

---

## 📦 Structure du Module

```
hilatech_cash_journal/
├── models/                      # Modèles Odoo
│   ├── __init__.py
│   └── cash_journal.py          # cash.journal.report + cash.journal.operation
├── views/                       # Interfaces utilisateur
│   └── cash_journal_views.xml   # Formulaires, listes, recherches, menus
├── security/                    # Sécurité et permissions
│   ├── cash_journal_security.xml  # Groupes d'utilisateurs
│   └── ir.model.access.csv      # Droits CRUD
├── data/                        # Données initiales
│   └── sequence.xml             # Séquence de numérotation
├── __init__.py                  # Imports principaux
├── __manifest__.py              # Manifeste du module
└── 📄 Guides (cf. ci-dessous)
```

---

## 🔧 Modèles de Données

### 1. `cash.journal.report` — Relevé Mensuel

| Champ | Type | Description |
|-------|------|-------------|
| `name` | Char | Numéro auto-généré (JRN/2026/00001) |
| `month_date` | Date | Mois du relevé |
| `initial_balance` | Float | Solde initial saisi |
| `final_balance` | Float | Solde final (calculé = initial + opérations) |
| `state` | Selection | `open` / `closed` |
| `caisse_state` | Selection | `opened` / `closed` (quotidien) |
| `operation_ids` | One2many | Lien vers les opérations |
| `user_id` | Many2one | Responsable |
| `notes` | Text | Observations libres |

**Actions Workflow:**
- `action_open_caisse()` → Active la saisie du jour
- `action_close_day()` → Verrouille les opérations + calcule solde
- `action_close_monthly()` → Clôture définitive du relevé

### 2. `cash.journal.operation` — Opération

| Champ | Type | Description |
|-------|------|-------------|
| `date` | Date | Date de l'opération |
| `description` | Char | Description / Motif |
| `received_by` | Many2one | Partenaire / Employé |
| `amount` | Float | Montant (+ entrée, - sortie) |
| `is_locked` | Boolean | Verrouillée après clôture |
| `operation_type` | Selection | `income` / `expense` (computed) |

**Protections:**
- Opérations verrouillées non modifiables (UserError)
- Date doit être dans le mois du relevé
- Montant ≠ 0

---

## 🎮 Workflow Utilisateur

### 1️⃣ Créer Relevé Mensuel
```
Menu → Journal de Caisse → Relevés → Créer
Remplir: Mois (ex: 01/03/2026), Solde Initial (ex: 10000)
Enregistrer → Numéro généré automatiquement
```

### 2️⃣ Ouvrir Caisse (Chaque Jour)
```
Bouton "Ouvrir la caisse"
→ Caisse passe à "Ouverte"
→ Champ "Opérations" devient éditable
```

### 3️⃣ Saisir Opérations
```
Onglet "Opérations du Mois" → Ajouter ligne
- Date: 01/03/2026
- Description: "Dépôt client ABC"
- Reçu par: [Sélectionner]
- Montant: 5000 (+ entrée) ou -1000 (- sortie)

Enregistrer
→ Solde final recalculé automatiquement
```

### 4️⃣ Clôturer Caisse du Jour
```
Bouton "Clôturer la caisse du jour"
→ Confirmer
→ Opérations grisées & verrouillées (is_locked=True)
→ Caisse passe à "Fermée"
→ Message avec solde final du jour affiché
```

### 5️⃣ Jour Suivant - Réouvrir Caisse
```
Bouton "Ouvrir la caisse"
→ Caisse "Ouverte"
→ Anciennes opérations grisées (toujours verrouillées)
→ Nouvelles opérations saisissables
```

### 6️⃣ Clôturer Relevé Mensuel
```
Bouton "Clôturer le relevé mensuel"
→ État: "Clôturé"
→ Aucune modification possible
→ Historique conservé définitivement
```

---

## 🔐 Sécurité & Permissions

### Groupes Créés
```
✅ Cash Journal - Utilisateur
   → Créer/Lire/Modifier les relevés et opérations
   → NE PEUT PAS supprimer
   → Utilisé par: Trésorier, Comptable

✅ Cash Journal - Gestionnaire
   → Accès COMPLET (Créer/Lire/Modifier/Supprimer)
   → Peut clôturer définitivement
   → Utilisé par: Directeur financier
```

### Permissions CRUD
```
Model: cash.journal.report
- Utilisateur: ✅ Read, Write, Create | ❌ Delete
- Gestionnaire: ✅ Read, Write, Create, Delete

Model: cash.journal.operation
- Utilisateur: ✅ Read, Write, Create | ❌ Delete
- Gestionnaire: ✅ Read, Write, Create, Delete
(Mais is_locked=True empêche modification quelque soit le rôle)
```

---

## 📝 Documentation & Guides

| Fichier | Contenu |
|---------|---------|
| **INSTALLATION.md** | Installation du module dans Odoo (3 méthodes) |
| **TEST_GUIDE.md** | Guide de test détaillé avec tous les scénarios |
| **QUICK_TEST.md** | Test rapide en 5 minutes (checklist) |
| **verify_module.py** | Script Python de vérification automatique |

---

## 🚀 Installation Rapide

### Option 1 : Via Interface Odoo (Simple)
```
1. Paramètres → Applications → Modules locaux
2. Rafraîchir la liste
3. Chercher "Cash Journal"
4. Installer
```

### Option 2 : Via Docker (Recommandé)
```bash
cd /d/erpworkspace/okukoresto
docker-compose restart odoo
# Attendre 30-60s puis actualiser interface Odoo
```

### Option 3 : Via Shell Odoo
```bash
docker-compose exec odoo bash
python /app/odoo-bin -c /etc/odoo/odoo.conf -u hilatech_cash_journal -d okukoresto
```

---

## ✅ Vérification Automatique

Un script de vérification a été créé pour valider l'installation :

```bash
# Depuis le répertoire du module
python verify_module.py

# Résultat attendu:
# [SUCCESS] TOUS LES TESTS REUSSIS !
# Le module est pret a etre installe dans Odoo.
```

---

## 🧪 Tests Rapides

Après installation, suivez **QUICK_TEST.md** pour valider en 5 minutes :

1. ✅ Créer relevé avec solde initial 10000
2. ✅ Ouvrir caisse
3. ✅ Ajouter 3 opérations (entrées/sorties)
4. ✅ Vérifier solde final calculé correctement
5. ✅ Clôturer caisse → opérations verrouillées
6. ✅ Essayer modifier → erreur attendue
7. ✅ Ouvrir caisse jour suivant → nouvelle saisie OK
8. ✅ Clôturer relevé mensuel → clôture définitive

---

## 📊 Exemple de Flux Complet

```
[JOUR 1 - MATIN]
Créer relevé: Initial = 10000
Ouvrir caisse

[JOUR 1 - JOURNÉE]
Ajouter opération: +5000 (entrée client)
Ajouter opération: +2500 (chèque)
Ajouter opération: -1000 (fournitures)
→ Solde final = 16500

[JOUR 1 - SOIR]
Clôturer caisse du jour
→ Opérations verrouillées
→ Solde: 16500 (final du jour)

[JOUR 2 - MATIN]
Ouvrir caisse
Ajouter opération: +3000 (dépôt jour 2)
→ Solde final = 19500

[JOUR 2 - SOIR]
Clôturer caisse du jour

[FIN DU MOIS]
Clôturer relevé mensuel
→ Relevé "Clôturé" définitivement
→ Historique conservé
```

---

## 🐛 Dépannage

### Le module n'apparaît pas
```
Vérifier:
1. docker ps (Odoo en cours d'exécution?)
2. Logs: docker-compose logs odoo | grep "hilatech_cash_journal"
3. Rafraîchir page: Ctrl+Shift+Del + F5
```

### Erreur lors de création d'opération
```
Vérifier:
1. Date dans le mois du relevé (ex: 01-31/03/2026)
2. Montant ≠ 0
3. Partenaire sélectionné dans "Reçu par"
```

### Les opérations ne se verrouillent pas
```
Vérifier:
1. Cliquer "Clôturer caisse du jour" (pas "Clôturer relevé")
2. Attendre le message "Caisse clôturée..."
3. Rafraîchir la page (F5)
```

---

## 💡 Points Techniques

- **Séquence:** JRN/%(year)s/%(seq)5d → JRN/2026/00001
- **Computed Field:** final_balance se recalcule automatiquement
- **Protection:** is_locked empêche write() et unlink() via override Python
- **Tracking:** Tous les changements d'état et montants tracés dans le chatter
- **Constraints:** Validation des montants, dates, unicité mois/année

---

## 📞 Support

Pour toute question ou problème:
1. Consulter les guides: INSTALLATION.md, TEST_GUIDE.md
2. Lancer verify_module.py pour validation
3. Vérifier les logs Odoo
4. Contacter l'équipe de développement

---

## 📄 Dépendances

- Odoo 19
- Module `base` (obligatoire)
- Module `account` (obligatoire)
- Module `mail` (pour chatter)

---

## 🎉 Bonne utilisation !

Le module est prêt à être utilisé. Pour tout besoin supplémentaire, n'hésitez pas à consulter les guides fournis.
