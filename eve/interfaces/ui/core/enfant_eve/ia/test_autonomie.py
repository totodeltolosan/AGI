#!/usr/bin/env python3
"""Test rapide autonomie IA"""

import sys
import os
import time


def test_rapide():
    """TODO: Add docstring."""
    print("🧪 TEST RAPIDE AUTONOMIE IA")
    print("=" * 40)

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.getcwd())))

    try:
        from ia.planificateur_besoins import AnalyseurBesoins
        from ia.planificateur_actions import GenerateurActionsBesoins

        print("✅ Modules refactorisés disponibles")

        # Test action autonome basique
        etat = {"health": 10, "hunger": 5}
        inventaire = {"wood": 2}
        environnement = {"lumiere": 6, "mobs_hostiles": ["zombie"]}

        analyse = AnalyseurBesoins.analyser_besoins_globaux(
            etat, inventaire, environnement
        )
        actions = GenerateurActionsBesoins.actions_survie_immediate(80)

        if actions and len(actions) > 0 and actions[0]["type"] != "ATTENDRE":
            print(f"✅ Actions autonomes générées: {actions[0]['type']}")
            print("🎉 AUTONOMIE PRÊTE À ÊTRE INTÉGRÉE!")
            return True
        else:
            print("❌ Problème génération actions")
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    test_rapide()