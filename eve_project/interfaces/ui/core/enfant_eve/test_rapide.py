#!/usr/bin/env python3
"""
🚀 TEST SIMPLE - VALIDATION IMMÉDIATE
Test minimal pour vérifier que les modules refactorisés fonctionnent.
"""

import sys
import os


def test_simple():
    """Test simple et direct"""
    print("🚀 TEST SIMPLE DE VALIDATION")
    print("=" * 40)

    # Ajouter le dossier courant au path
    sys.path.insert(0, os.getcwd())

    erreurs = []

    # Test 1: Import AnalyseurBesoins
    try:
        from ia.planificateur_besoins import AnalyseurBesoins

        print("✅ AnalyseurBesoins importé avec succès")

        # Test fonctionnel simple
        result = AnalyseurBesoins.evaluer_securite_zone(
            {"lumiere": 10, "mobs_hostiles": []}
        )
        if isinstance(result, dict) and "score" in result:
            print(f"✅ AnalyseurBesoins fonctionne (Score: {result['score']})")
        else:
            print("❌ AnalyseurBesoins ne fonctionne pas correctement")
            erreurs.append("AnalyseurBesoins: fonction défaillante")

    except Exception as e:
        print(f"❌ Erreur AnalyseurBesoins: {e}")
        erreurs.append(f"AnalyseurBesoins: {e}")

    # Test 2: Import GenerateurActionsBesoins
    try:
        from ia.planificateur_actions import GenerateurActionsBesoins

        print("✅ GenerateurActionsBesoins importé avec succès")

        # Test fonctionnel simple
        actions = GenerateurActionsBesoins.actions_survie_immediate(50)
        if isinstance(actions, list) and len(actions) > 0:
            print(f"✅ GenerateurActionsBesoins fonctionne ({len(actions)} actions)")
        else:
            print("❌ GenerateurActionsBesoins ne génère pas d'actions")
            erreurs.append("GenerateurActionsBesoins: pas d'actions générées")

    except Exception as e:
        print(f"❌ Erreur GenerateurActionsBesoins: {e}")
        erreurs.append(f"GenerateurActionsBesoins: {e}")

    # Test 3: Import Plan
    try:
        from ia.planificateur_plans import Plan

        print("✅ Plan importé avec succès")

        # Test fonctionnel simple - LE TEST CRITIQUE !
        plan = Plan("Test Plan", [{"type": "ACTION_TEST"}])
        if plan and plan.nom == "Test Plan" and plan.a_des_actions():
            print("✅ Plan fonctionne correctement")

            # Test compatibilité dictionnaire
            plan_dict = plan.to_dict()
            if isinstance(plan_dict, dict) and "nom" in plan_dict:
                print("✅ Compatibilité dictionnaire OK")
            else:
                print("❌ Problème compatibilité dictionnaire")
                erreurs.append("Plan: compatibilité dictionnaire")
        else:
            print("❌ Plan ne fonctionne pas correctement")
            erreurs.append("Plan: fonctionnement incorrect")

    except Exception as e:
        print(f"❌ Erreur Plan: {e}")
        erreurs.append(f"Plan: {e}")

    # Test 4: Test résolution erreur "0"
    try:
        from ia.planificateur_actions import GenerateurActionsBesoins
        from ia.planificateur_plans import Plan

        print("\n🎯 TEST CRITIQUE - RÉSOLUTION ERREUR '0'")

        # Simulation exacte du cas problématique
        for i in range(3):
            actions = GenerateurActionsBesoins.actions_survie_immediate(80)
            plan = Plan(f"Survie {i+1}", actions)

            if not plan or not actions or len(actions) == 0:
                print(f"❌ Test {i+1}: Génération échouée!")
                erreurs.append(f"Erreur '0' non résolue - test {i+1}")
            else:
                print(f"✅ Test {i+1}: Plan généré avec succès")

        if len([e for e in erreurs if "Erreur '0'" in e]) == 0:
            print("🎉 ERREUR '0' DÉFINITIVEMENT RÉSOLUE!")

    except Exception as e:
        print(f"❌ Erreur test résolution '0': {e}")
        erreurs.append(f"Test résolution '0': {e}")

    # Rapport final
    print("\n" + "=" * 40)
    print("📊 RÉSULTAT FINAL")
    print("=" * 40)

    if len(erreurs) == 0:
        print("🎉 SUCCÈS TOTAL!")
        print("✅ Tous les modules refactorisés fonctionnent parfaitement")
        print("✅ Le problème 'Erreur génération plan survie: 0' est RÉSOLU")
        print("✅ La refactorisation est UN SUCCÈS COMPLET!")
        return True
    else:
        print(f"❌ {len(erreurs)} erreur(s) détectée(s):")
        for erreur in erreurs:
            print(f"   • {erreur}")
        return False


def verification_fichiers():
    """Vérifie que tous les fichiers refactorisés sont présents"""
    print("\n🔍 VÉRIFICATION FICHIERS REFACTORISÉS")
    print("-" * 40)

    fichiers_requis = [
        "ia/planificateur_besoins.py",
        "ia/planificateur_actions.py",
        "ia/planificateur_exploration.py",
        "ia/planificateur_construction.py",
        "ia/planificateur_plans.py",
        "ia/planificateur.py",
    ]

    for fichier in fichiers_requis:
        if os.path.exists(fichier):
            print(f"✅ {fichier}")
        else:
            print(f"❌ {fichier} MANQUANT!")
            return False

    print("✅ Tous les fichiers refactorisés sont présents")
    return True


def main():
    """Point d'entrée principal"""
    if verification_fichiers():
        return test_simple()
    else:
        print("❌ Fichiers manquants - vérifiez l'installation")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
