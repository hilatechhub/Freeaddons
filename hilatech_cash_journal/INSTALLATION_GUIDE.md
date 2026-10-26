# Guide d'Installation - Cash Journal pour Odoo 19

## 📋 Table des Matières

1. [Pré-requis](#pré-requis)
2. [Installation du Module](#installation-du-module)
3. [Configuration Initiale](#configuration-initiale)
4. [Premiers Pas](#premiers-pas)
5. [Dépannage](#dépannage)
6. [Support](#support)

---

## 🔧 Pré-requis

Avant d'installer Cash Journal, assurez-vous que:

### Système
- ✅ Odoo 19.0 installé et fonctionnel
- ✅ PostgreSQL 12+ configuré
- ✅ Python 3.8+ disponible
- ✅ Accès administrateur Odoo

### Dépendances Obligatoires (Modules Odoo)
Ces modules sont standards et généralement pré-installés:
- `base` - Module de base Odoo
- `account` - Module comptable
- `mail` - Module de messages/notifications

### Navigateurs Supportés
- Chrome/Chromium (dernière version)
- Firefox (dernière version)
- Safari (dernière version)
- Edge (dernière version)

---

## 📦 Installation du Module

### Méthode 1: Via l'App Store Odoo (Recommandé)

1. **Connectez-vous à Odoo** en tant qu'administrateur
2. Allez à **Apps** (menu principal)
3. Activez le **Mode Développeur** (coin bas-droit)
4. Cliquez sur **Rechercher**
5. Tapez "**Cash Journal**"
6. Cliquez sur **Installer**
7. Attendez la confirmation d'installation

L'installation prend généralement 2-5 minutes.

### Méthode 2: Installation Manuelle

1. **Téléchargez** le module hilatech_cash_journal
2. **Placez-le** dans votre dossier `addons`:
   ```
   /path/to/odoo/addons/hilatech_cash_journal/
   ```
3. **Redémarrez Odoo** ou forcez la mise à jour:
   ```bash
   ./odoo-bin -u all
   ```
4. **Allez à Apps** et **Mettez à jour** la liste
5. **Recherchez** "Cash Journal" et **Installez**

### Méthode 3: En Ligne de Commande

```bash
# Redémarrer Odoo avec le nouvel addon
./odoo-bin -c /path/to/odoo.conf \
  -u all \
  --addons-path=/path/to/addons,/path/to/hilatech_addons

# Ou pour un déploiement rapide
cd /path/to/hilatech_cash_journal
odoo-cli install cash_journal
```

---

## ⚙️ Configuration Initiale

### Étape 1: Vérifier l'Installation

1. Allez à **Journal de Caisse** dans le menu
2. Vous devriez voir 3 options:
   - ✅ Relevés de Caisse
   - ✅ Rapport de Caisse
   - ✅ Listes des Opérations

### Étape 2: Configurer les Utilisateurs

Le module crée automatiquement 2 rôles. Pour les assigner:

1. Allez à **Paramètres > Utilisateurs & Sociétés > Utilisateurs**
2. **Ouvrez l'utilisateur** à configurer
3. **Allez à l'onglet Accès**
4. **Sous "Groupes"**, sélectionnez:
   - `Cash Journal / Utilisateur` - Pour la saisie simple
   - `Cash Journal / Gestionnaire` - Pour les clôtures

**Recommandation:**
- Caissiers → Groupe "Utilisateur"
- Directeurs/Comptables → Groupe "Gestionnaire"
- Directeurs généraux → Groupe "Gestionnaire"

### Étape 3: Configurer la Séquence (Optionnel)

La séquence `JRN/ANNÉE/NUMÉRO` est créée automatiquement.
Pour personnaliser (optionnel):

1. Allez à **Paramètres > Numérotation & Séquences > Séquences**
2. **Recherchez** "cash.journal.report"
3. **Modifiez le format** si désiré (ex: "CAI/2026/%s" pour "CAI/2026/00001")

### Étape 4: Configurer les Couleurs Company (Optionnel)

Pour que les rapports PDF utilisent vos couleurs:

1. Allez à **Paramètres > Sociétés**
2. **Ouvrez votre société**
3. **Sous "Couleurs"**, définissez:
   - `Couleur principale` - Pour les en-têtes PDF (ex: #1f4788)
   - `Couleur secondaire` - Pour les fonds (ex: #f5f5f5)

---

## 🚀 Premiers Pas

### Créer votre Premier Relevé Mensuel

1. Allez à **Journal de Caisse > Relevés de Caisse**
2. Cliquez sur **Créer**
3. **Mois du Relevé**: Sélectionnez le mois (ex: Mars 2026)
4. **Solde Initial**: Entrez le solde de début (ex: 1000,00)
   - Si c'est votre 1er relevé, entrez le montant initial
   - Sinon, il est hérité automatiquement du précédent
5. **Cliquez Enregistrer**

✅ Votre numéro (ex: JRN/2026/00001) est généré automatiquement!

### Ouvrir la Caisse du Jour

1. **Ouvrez le relevé** que vous avez créé
2. Cliquez sur le bouton **"Ouvrir la caisse"** (vert)
3. Le bouton disparaît, et vous pouvez maintenant saisir des opérations

### Saisir les Opérations

1. **Dans le relevé ouvert**, allez à l'onglet **"Opérations"**
2. Cliquez sur **"Ajouter une ligne"**
3. Complétez les champs:
   - **Date**: Date de l'opération
   - **Description**: Raison (ex: "Vente ticket restaurant")
   - **Reçu par**: Qui a reçu l'argent
   - **Montant**: +1000 (entrée) ou -50 (sortie)
4. **Enregistrez**

✅ Automatiquement:
- Le type (Entrée/Sortie) est détecté
- Le solde final se recalcule
- L'opération reste modifiable

### Clôturer la Caisse du Jour

1. **Ouvrez le relevé** avec opérations saisies
2. Cliquez sur **"Clôturer la caisse du jour"** (orange)
3. Confirmez: "Êtes-vous sûr?"
4. ✅ Toutes les opérations du jour sont maintenant **verrouillées**

Vous pouvez toujours ajouter des opérations demain!

### Clôturer le Relevé Mensuel

**Attention**: Cette action est IRRÉVERSIBLE!

1. **Ouvrez le relevé** quand le mois est terminé
2. Cliquez sur **"Clôturer le relevé mensuel"** (rouge)
3. Confirmez: "Êtes-vous sûr?"
4. ✅ Le relevé est **définitivement fermé**

Impossible de modifier les opérations après!

---

## 📊 Générer des Rapports

### Rapport PDF (depuis un relevé)

1. Allez à **Journal de Caisse > Relevés de Caisse**
2. **Ouvrez un relevé** déjà clôturé
3. Cliquez sur **"Imprimer"** en haut à droite
4. Sélectionnez **"Rapport de Caisse"**
5. ✅ PDF généré avec vos couleurs company!

### Rapport Excel (par plage de dates)

1. Allez à **Journal de Caisse > Rapport de Caisse**
2. Sélectionnez:
   - **Date de Début**: Ex: 01/03/2026
   - **Date de Fin**: Ex: 31/03/2026
3. Cliquez sur **"Générer Excel"**
4. ✅ Fichier Excel téléchargé automatiquement!

### Consulter les Opérations

1. Allez à **Journal de Caisse > Listes des Opérations**
2. Consultez **tous les mouvements de caisse**
3. **Basculez à la vue graphique** pour voir les totaux par relevé
4. Utilisez les **filtres** pour affiner

---

## 🌍 Changer la Langue

Pour utiliser le module en Français, Anglais ou Espagnol:

1. Allez à **Paramètres > Traductions > Charger une traduction**
2. Sélectionnez votre langue (ex: Français)
3. Cliquez **Charger**
4. **Rafraîchissez votre page** (F5)
5. ✅ Interface en français!

**Langues supportées:**
- 🇫🇷 Français (fr_FR)
- 🇬🇧 Anglais (en_US)
- 🇪🇸 Espagnol (es_ES)

---

## 🐛 Dépannage

### Problème: Module n'apparaît pas dans Apps

**Solution:**
1. Allez à **Paramètres > Modules > Mettre à jour la liste**
2. Attendez 30 secondes
3. Recherchez "Cash Journal" à nouveau
4. Si encore absent: vérifiez que le dossier est dans `addons`
5. Redémarrez Odoo

### Problème: Erreur "Permissions insuffisantes"

**Solution:**
1. Vérifiez que votre utilisateur est dans le groupe approprié
2. Allez à **Paramètres > Utilisateurs**
3. Ouvrez **votre utilisateur**
4. Ajoutez le groupe **Cash Journal / Utilisateur**
5. Déconnectez/reconnectez-vous

### Problème: Cannot write operation (Impossible de modifier)

**Raison:** L'opération est verrouillée (jour fermé ou relevé clôturé)

**Solution:**
- Impossible de modifier une opération verrouillée
- C'est volontaire pour la sécurité!
- Pour corriger: contactez votre administrateur

### Problème: Relevé précédent ne donne pas le solde initial

**Raison:** Le relevé précédent n'est pas fermé (état ≠ "Clôturé")

**Solution:**
1. Allez à **Journal de Caisse > Relevés de Caisse**
2. **Clôturez le relevé précédent** complètement
3. Créez un **nouveau relevé**
4. Le solde initial sera hérité automatiquement

### Problème: Erreur "Modèle non trouvé" avec PDF

**Raison:** Template PDF mal référencée

**Solution:**
1. Assurez-vous que `report_template.xml` existe
2. Redémarrez Odoo (`-u all` si nécessaire)
3. Régénérez le PDF

### Problème: PDF ne s'affiche pas avec headers/footers

**Raison:** Layout Odoo n'est pas chargé

**Solution:**
1. Vérifiez que module `web` est installé
2. Vérifiez les couleurs company configurées
3. Redémarrez Odoo
4. Testez à nouveau

---

## 📞 Support

### Questions Fréquentes

**Q: Puis-je modifier une opération après la clôture du jour?**
R: Non, c'est volontaire pour la sécurité. Toutes les opérations sont verrouillées après clôture.

**Q: Comment corriger une erreur de saisie?**
R: Pendant le jour, vous pouvez modifier/supprimer l'opération. Après clôture du jour, impossible.
Solution: Créer une opération inverse (ex: -1000) le jour suivant.

**Q: Le rapport PDF manque-t-il des données?**
R: Assurez-vous que le relevé est clôturé et contient des opérations. Un relevé vide donnera peu de contenu.

**Q: Puis-je supprimer un relevé?**
R: Oui, si aucune opération n'y est liée. Une fois des opérations créées, c'est bloqué pour sécurité.

**Q: Comment exporter tous mes relevés?**
R: Utilisez le **Rapport de Caisse** avec la plage de dates appropriée (ex: année entière).

### Contact Hilatech

Pour toute question ou problème:

📧 **Email**: support@hilatech.com
🌐 **Web**: https://hilatech.com
📞 **Tél**: +1 (855) HILATECH

**Heures de support:**
- Lun-Ven: 9h-17h (heure US)
- Sam: 9h-12h (sur demande)
- Dim: Urgences uniquement

---

## 📚 Documentation Supplémentaire

- **README.md** - Vue d'ensemble complète du module
- **CHANGELOG.md** - Historique des versions
- **index.html** - Description détaillée (App Store Odoo)
- **APPSTORE_DESCRIPTION.txt** - Résumé pour App Store

---

## ✅ Checklist de Démarrage

Avant de commencer, vérifiez:

- [ ] Odoo 19 installé et fonctionnel
- [ ] Module Cash Journal installé
- [ ] Utilisateurs configurés avec permissions
- [ ] Couleurs company définies (optionnel)
- [ ] Premier relevé créé
- [ ] Caisse ouverte et opérations saisies
- [ ] Caisse clôturée et rapport généré

---

**Bravo! Vous êtes prêt à utiliser Cash Journal! 🎉**

Pour toute question, contactez: **support@hilatech.com**

Merci d'avoir choisi Hilatech! 🙏
