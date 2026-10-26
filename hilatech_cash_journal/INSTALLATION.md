# Installation du Module Cash Journal

## Prérequis
- ✅ Odoo 19
- ✅ Modules: base, account, mail (dépendances)
- ✅ Accès administrateur Odoo

## Méthode 1 : Via Docker (Recommandé)

```bash
# 1. Redémarrer Odoo pour recharger les modules
cd /d/erpworkspace/okukoresto
docker-compose restart odoo

# Attendre 30-60 secondes le redémarrage
```

## Méthode 2 : Via l'interface Odoo (Plus simple)

```
1. Se connecter à Odoo (http://localhost:8069)
2. Mode développeur: Activé (menu Paramètres)
3. Aller à: Paramètres → Applications → Modules locaux
4. Cliquer le bouton "Rafraîchir la liste" (flèche circulaire)
5. Chercher dans la barre de recherche: "Cash Journal"
6. Cliquer sur le module "Cash Journal - Journal de Caisse"
7. Cliquer le bouton "Installer"
8. Attendre la fin de l'installation (peut prendre 10-30s)
9. Vous devez voir le menu "Journal de Caisse" dans le menu principal
```

## Méthode 3 : Via shell Odoo (Pour développeurs)

```python
# Dans le conteneur Odoo
docker-compose exec odoo bash

# Puis
python /app/odoo-bin -c /etc/odoo/odoo.conf -u hilatech_cash_journal -d [db_name]

# Remplacer [db_name] par le nom de votre base de données
# Ex: python /app/odoo-bin -c /etc/odoo/odoo.conf -u hilatech_cash_journal -d okukoresto
```

## Vérification de l'Installation

### Dans Odoo
- [ ] Menu "Journal de Caisse" visible dans le menu principal
- [ ] Sous-menu "Relevés de Caisse" accessible
- [ ] Bouton "Créer" fonctionnel

### Groupes de sécurité créés
```
Paramètres → Utilisateurs et droits d'accès → Groupes

Vérifier la présence de:
- Cash Journal - Utilisateur
- Cash Journal - Gestionnaire
```

### Champs et modèles
```
Paramètres → Mode développeur → Modèles

Chercher:
- cash.journal.report (doit exister)
- cash.journal.operation (doit exister)
```

## Dépannage

### Le module n'apparaît pas dans la liste
```
1. Vérifier que le conteneur Odoo est actif
   docker ps | grep odoo

2. Vérifier les logs
   docker-compose logs odoo | grep "hilatech_cash_journal"

3. Chercher des erreurs Python
   Aller dans Paramètres → Modules locaux
   Chercher dans la barre de recherche
```

### Erreur lors de l'installation
```
1. Vérifier la syntaxe XML
   grep "ERROR" /var/log/odoo/odoo.log (dans le conteneur)

2. Vérifier les dépendances
   Les modules 'base', 'account', 'mail' doivent être installés

3. Redémarrer Odoo
   docker-compose restart odoo
```

### Le module ne s'installe pas
```
1. Nettoyer le cache
   - Vider le navigateur (Ctrl+Shift+Del)
   - Rafraîchir la liste des modules

2. Forcer la mise à jour
   - Mode développeur activé
   - Paramètres → Mode développeur
   - Cliquer "Réinitialiser les données à déployer"
```

## Après Installation

1. **Tester le module**
   - Suivre le guide TEST_GUIDE.md

2. **Assigner les droits**
   - Paramètres → Utilisateurs et droits d'accès
   - Ajouter des utilisateurs aux groupes "Cash Journal"
   - Assigner "Cash Journal - Utilisateur" et/ou "Cash Journal - Gestionnaire"

3. **Configurer les opérations**
   - Paramètres → Données de base → Partenaires
   - Créer/vérifier les partenaires qui seront utilisés pour "Reçu par"

## Support

Si vous rencontrez des problèmes:
1. Vérifier verify_module.py (lance la vérification automatique)
2. Consulter TEST_GUIDE.md (guide détaillé des tests)
3. Vérifier les logs Odoo: `docker-compose logs odoo`
