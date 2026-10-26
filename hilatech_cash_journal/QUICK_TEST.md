# ⚡ Test Rapide du Module (5 min)

## Phase 1 : Créer un Relevé

```
Menu: Journal de Caisse → Relevés de Caisse → Créer

Données:
├─ Mois: 01/03/2026 (ou 1er du mois courant)
├─ Solde Initial: 10000
└─ Sauvegarder

✓ Numéro généré: JRN/2026/00001
```

## Phase 2 : Ouvrir la Caisse

```
Bouton: "Ouvrir la caisse"

✓ État caisse = "Caisse Ouverte"
✓ Solde final = 10000 (= initial)
```

## Phase 3 : Ajouter 3 Opérations

**Opération 1:**
```
Date: 2026-03-01
Description: Entrée test
Reçu par: [Choisir un contact]
Montant: 5000
```

**Opération 2:**
```
Date: 2026-03-01
Description: Entrée client
Reçu par: [Contact]
Montant: 2500
```

**Opération 3:**
```
Date: 2026-03-01
Description: Dépense fournitures
Reçu par: [Fournisseur]
Montant: -1000
```

**Sauvegarder**

✓ Solde final = 16500 (10000 + 5000 + 2500 - 1000)

## Phase 4 : Clôturer la Caisse du Jour

```
Bouton: "Clôturer la caisse du jour"
Confirmer

✓ Opérations grisées
✓ État caisse = "Caisse Fermée"
✓ Message: "Caisse clôturée... Solde final: 16500.00"
```

## Phase 5 : Essayer de Modifier (Doit Échouer)

```
Cliquer sur une opération
Modifier la description

✓ ERREUR: "Cette opération est verrouillée..."
```

## Phase 6 : Ouvrir Caisse (Jour Suivant)

```
Bouton: "Ouvrir la caisse"

Ajouter opération:
├─ Date: 2026-03-02
├─ Description: Dépôt jour 2
└─ Montant: 3000

✓ Solde final = 19500 (16500 + 3000)
✓ Anciennes opérations = grisées (locked)
✓ Nouvelle opération = noire (unlocked)
```

## Phase 7 : Clôturer le Relevé

```
Bouton: "Clôturer le relevé mensuel"
Confirmer

✓ État relevé = "Clôturé"
✓ Tous les boutons disparus
✓ Liste = couleur VERTE
```

---

## ✅ Résultat Final

| Étape | Test | Résultat |
|-------|------|---------|
| 1 | Créer relevé | JRN/2026/00001 |
| 2 | Ouvrir caisse | État: Ouverte |
| 3 | Solde final | 16500 (correct) |
| 4 | Verrouillage | Opérations grisées |
| 5 | Protection | Erreur: locked |
| 6 | Jour suivant | Nouvelle saisie OK |
| 7 | Clôture | État: Clôturé |

## 🎉 Si tous passent → Module FONCTIONNEL !
