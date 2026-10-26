#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verification du module hilatech_cash_journal
Teste la structure et les imports basiques
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")

def check_file(path, description):
    """Verifier qu'un fichier existe"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print("[OK] " + description)
        print("     -> " + str(path) + " (" + str(size) + " bytes)")
        return True
    else:
        print("[FAIL] " + description + " - MANQUANT")
        print("     -> " + str(path))
        return False

def verify_module():
    """Verification complete du module"""
    print_header("VERIFICATION DU MODULE HILATECH_CASH_JOURNAL")

    module_path = Path(__file__).parent
    all_ok = True

    # 1. Verifier structure de base
    print("1. Structure de base\n")
    files_to_check = [
        ("__init__.py", "Fichier principal __init__.py"),
        ("__manifest__.py", "Manifeste du module"),
        ("models/__init__.py", "Package models"),
        ("models/cash_journal.py", "Modeles (cash.journal.report + cash.journal.operation)"),
        ("security/ir.model.access.csv", "Permissions CRUD"),
        ("security/cash_journal_security.xml", "Groupes de securite"),
        ("data/sequence.xml", "Sequence de numerotation"),
        ("views/cash_journal_views.xml", "Vues (form, list, search, action, menus)"),
    ]

    for filename, description in files_to_check:
        filepath = module_path / filename
        if not check_file(filepath, description):
            all_ok = False

    # 2. Verifier __manifest__.py
    print("\n2. Contenu du __manifest__.py\n")
    try:
        with open(module_path / '__manifest__.py', 'r', encoding='utf-8') as f:
            manifest_content = f.read()

        # Verifier les cles essentielles
        checks = [
            ('name', 'Nom du module'),
            ('version', 'Version'),
            ('depends', 'Dependances'),
            ('data', 'Liste de donnees'),
            ('installable', 'Installable'),
        ]

        for key, desc in checks:
            if key in manifest_content:
                print("[OK] " + desc + " (" + key + ") present")
            else:
                print("[FAIL] " + desc + " (" + key + ") MANQUANT")
                all_ok = False

    except Exception as e:
        print("[FAIL] Erreur lecture __manifest__.py: " + str(e))
        all_ok = False

    # 3. Verifier modeles Python
    print("\n3. Definition des modeles\n")
    try:
        with open(module_path / 'models/cash_journal.py', 'r', encoding='utf-8') as f:
            models_content = f.read()

        models_to_check = [
            ('class CashJournalReport', 'Modele: cash.journal.report'),
            ('class CashJournalOperation', 'Modele: cash.journal.operation'),
            ('def action_open_caisse', 'Action: Ouvrir la caisse'),
            ('def action_close_day', 'Action: Cloturer caisse du jour'),
            ('def action_close_monthly', 'Action: Cloturer releve mensuel'),
            ('_compute_final_balance', 'Champ calcule: final_balance'),
            ('is_locked', 'Champ: is_locked (protection)'),
        ]

        for pattern, desc in models_to_check:
            if pattern in models_content:
                print("[OK] " + desc)
            else:
                print("[FAIL] " + desc + " - MANQUANT")
                all_ok = False

    except Exception as e:
        print("[FAIL] Erreur lecture modeles: " + str(e))
        all_ok = False

    # 4. Verifier vues XML
    print("\n4. Vues Odoo\n")
    try:
        with open(module_path / 'views/cash_journal_views.xml', 'r', encoding='utf-8') as f:
            views_content = f.read()

        views_to_check = [
            ('view_cash_journal_report_search', 'Vue Recherche'),
            ('view_cash_journal_report_list', 'Vue Liste'),
            ('view_cash_journal_report_form', 'Vue Formulaire'),
            ('action_cash_journal_report', 'Action'),
            ('menu_cash_journal_root', 'Menu principal'),
            ('menu_cash_journal_report', 'Sous-menu Releves'),
        ]

        for pattern, desc in views_to_check:
            if pattern in views_content:
                print("[OK] " + desc)
            else:
                print("[FAIL] " + desc + " - MANQUANT")
                all_ok = False

    except Exception as e:
        print("[FAIL] Erreur lecture vues: " + str(e))
        all_ok = False

    # 5. Verifier securite
    print("\n5. Configuration de securite\n")
    try:
        # Verifier CSV
        with open(module_path / 'security/ir.model.access.csv', 'r', encoding='utf-8') as f:
            csv_content = f.read()

        csv_checks = [
            ('cash_journal_report', 'Model: cash.journal.report'),
            ('cash_journal_operation', 'Model: cash.journal.operation'),
            ('group_cash_journal_user', 'Groupe: Utilisateur'),
            ('group_cash_journal_manager', 'Groupe: Gestionnaire'),
        ]

        for pattern, desc in csv_checks:
            if pattern in csv_content:
                print("[OK] " + desc)
            else:
                print("[FAIL] " + desc + " - MANQUANT")
                all_ok = False

    except Exception as e:
        print("[FAIL] Erreur lecture securite: " + str(e))
        all_ok = False

    # Resume final
    print_header("RESUME")

    if all_ok:
        print("[SUCCESS] TOUS LES TESTS REUSSIS !\n")
        print("Le module est pret a etre installe dans Odoo.")
        print("\nEtapes suivantes:")
        print("1. Installer Odoo 19 ou verifier que le conteneur est en cours d'execution")
        print("2. Redemarrer le service Odoo (docker-compose restart odoo)")
        print("3. Actualiser la liste des modules (Parametres -> Modules locaux)")
        print("4. Chercher 'Cash Journal' et cliquer 'Installer'")
        print("5. Suivre le TEST_GUIDE.md pour la validation complete")
        return 0
    else:
        print("[WARNING] ATTENTION: Des fichiers ou contenus sont manquants\n")
        print("Veuillez verifier les points marques en [FAIL] avant d'installer.")
        return 1

if __name__ == '__main__':
    sys.exit(verify_module())
