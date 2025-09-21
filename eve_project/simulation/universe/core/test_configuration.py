#!/usr/bin/env python3
# Script de test et configuration pour Projet Monde v8.0

"""
Script utilitaire pour tester l'installation, diagnostiquer les problèmes
et configurer optimalement l'environnement Projet Monde.
"""

import sys
import json
import time
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Any


def tester_imports_critiques() -> Tuple[bool, List[str]]:
    """Teste l'importation de tous les modules critiques."""
    modules_critiques = [
        ("PyQt6.QtCore", "Interface graphique"),
        ("numpy", "Calculs scientifiques"),
        ("scipy", "Algorithmes avancés"),
        ("numba", "Accélération JIT"),
        ("psutil", "Monitoring système"),
    ]

    modules_agents = [
        ("agents_physiques", "Agents physiques"),
        ("agents_complexes", "Agents complexes"),
        ("agents_emergents", "Agents émergents"),
        ("etatmonde", "État du monde"),
        ("simulateur", "Simulateur principal"),
    ]

    erreurs = []
    print("=== TEST D'IMPORTATION DES MODULES ===")

    for module_name, description in modules_critiques + modules_agents:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name:<20} - {description}")
        except ImportError as e:
            erreurs.append(f"✗ {module_name:<20} - ERREUR: {e}")
            print(f"✗ {module_name:<20} - ERREUR: {e}")

    succes = len(erreurs) == 0
    return succes, erreurs


def tester_agents_individuels() -> Dict[str, Any]:
    """Teste l'instanciation de chaque agent individuellement."""
    print("\n=== TEST D'INSTANCIATION DES AGENTS ===")

    agents_tests = {}
    modules_agents = {
        "agents_physiques": [
            "MaitreTemps",
            "CalculateurLois",
            "Alchimiste",
            "Archiviste",
        ],
        "agents_complexes": [
            "Chimiste",
            "Planetologue",
            "Galacticien",
            "Astrophysicien",
        ],
        "agents_emergents": [
            "Biologiste",
            "Evolutif",
            "Sociologue",
            "PhysicienExotique",
            "AnalysteCosmique",
        ],
    }

    for module_name, classes_agents in modules_agents.items():
        try:
            module = importlib.import_module(module_name)
            agents_tests[module_name] = {}

            for classe_name in classes_agents:
                try:
                    classe = getattr(module, classe_name)
                    instance = classe()
                    agents_tests[module_name][classe_name] = "OK"
                    print(f"✓ {module_name}.{classe_name}")
                except Exception as e:
                    agents_tests[module_name][classe_name] = f"ERREUR: {e}"
                    print(f"✗ {module_name}.{classe_name} - ERREUR: {e}")

        except ImportError as e:
            agents_tests[module_name] = f"Module non importable: {e}"
            print(f"✗ Module {module_name} non importable: {e}")

    return agents_tests


def tester_creation_univers() -> bool:
    """Teste la création d'un univers minimal."""
    print("\n=== TEST DE CRÉATION D'UNIVERS ===")

    try:
        from generateurmonde import creerbigbang, TypeUnivers
        from etatmonde import EtatMonde

        # Test création Big Bang classique
        print("Test création Big Bang classique...")
        univers = creerbigbang(TypeUnivers.BIG_BANG_CLASSIQUE)

        if not isinstance(univers, EtatMonde):
            print("✗ L'univers créé n'est pas une instance EtatMonde")
            return False

        particules = len(univers.entites.get("particules", []))
        print(f"✓ Univers créé avec {particules} particules")

        if particules == 0:
            print("✗ Aucune particule créée")
            return False

        print(f"✓ Temps initial: {univers.temps}")
        print(f"✓ Paliers: {len(univers.paliers)}")
        print(f"✓ Constantes: {list(univers.constantes.keys())}")

        return True

    except Exception as e:
        print(f"✗ Erreur lors de la création d'univers: {e}")
        return False


def tester_cycle_simulation() -> bool:
    """Teste un cycle complet de simulation."""
    print("\n=== TEST DE CYCLE DE SIMULATION ===")

    try:
        from generateurmonde import creerbigbang, TypeUnivers
        from agents_physiques import MaitreTemps, CalculateurLois

        # Création d'un petit univers de test
        univers = creerbigbang(TypeUnivers.BIG_BANG_CLASSIQUE)
        temps_initial = univers.temps

        # Test des agents de base
        maitre_temps = MaitreTemps()
        calculateur = CalculateurLois()

        print("Test MaitreTemps...")
        univers = maitre_temps.maitretemps(univers)
        if univers.temps != temps_initial + 1:
            print(f"✗ Temps non incrémenté correctement: {univers.temps}")
            return False
        print(f"✓ Temps incrémenté: {temps_initial} → {univers.temps}")

        print("Test CalculateurLois...")
        univers_avant = len(univers.entites.get("particules", []))
        univers = calculateur.calculateurlois(univers)
        univers_apres = len(univers.entites.get("particules", []))
        print(
            f"✓ Calcul gravitationnel effectué (particules: {univers_avant} → {univers_apres})"
        )

        # Nettoyage
        calculateur.fermer_pool()

        return True

    except Exception as e:
        print(f"✗ Erreur lors du test de simulation: {e}")
        return False


def optimiser_configuration() -> Dict[str, Any]:
    """Génère une configuration optimisée selon les ressources système."""
    print("\n=== OPTIMISATION DE LA CONFIGURATION ===")

    import psutil

    # Détection des ressources système
    ram_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count()

    print(f"Ressources détectées: {ram_gb:.1f} GB RAM, {cpu_count} CPU cores")

    # Configuration adaptative
    config = {
        "simulation": {
            "fps_interface": 60 if ram_gb > 8 else 30,
            "taille_queue": min(20, max(10, int(ram_gb * 2))),
            "intervalle_sauvegarde_minutes": 10 if ram_gb > 16 else 30,
        },
        "performance": {
            "threads_calcul": max(1, cpu_count - 1),
            "optimization_level": "high" if ram_gb > 8 else "medium",
            "parallel_physics": ram_gb > 4,
            "cache_spatial_enabled": ram_gb > 8,
        },
        "agents": {"tolerance_erreur": 10 if ram_gb > 16 else 5},
    }

    print(f"Configuration optimisée générée:")
    print(f"  - FPS interface: {config['simulation']['fps_interface']}")
    print(f"  - Threads calcul: {config['performance']['threads_calcul']}")
    print(f"  - Taille queue: {config['simulation']['taille_queue']}")

    return config


def main():
    """Point d'entrée principal du script de test."""
    print("PROJET MONDE v8.0 - SCRIPT DE TEST ET CONFIGURATION")
    print("=" * 60)

    # Test des imports
    imports_ok, erreurs_import = tester_imports_critiques()

    if not imports_ok:
        print(f"\n❌ ERREURS D'IMPORTATION DÉTECTÉES:")
        for erreur in erreurs_import:
            print(f"   {erreur}")
        print("\nRecommandations:")
        print("1. Vérifiez que vous êtes dans le bon environnement virtuel")
        print("2. Relancez: pip install -r requirements.txt")
        print("3. Pour numba, essayez: conda install numba -c conda-forge")
        return 1

    # Test des agents
    resultats_agents = tester_agents_individuels()

    # Test de création d'univers
    creation_ok = tester_creation_univers()

    # Test de simulation
    simulation_ok = tester_cycle_simulation()

    # Optimisation de configuration
    config_optimisee = optimiser_configuration()

    # Rapport final
    print("\n" + "=" * 60)
    print("RAPPORT FINAL:")
    print(f"✓ Imports: {'OK' if imports_ok else 'ERREURS'}")
    print(f"✓ Création univers: {'OK' if creation_ok else 'ERREUR'}")
    print(f"✓ Cycle simulation: {'OK' if simulation_ok else 'ERREUR'}")

    # Sauvegarde de la configuration optimisée
    if imports_ok and creation_ok and simulation_ok:
        try:
            with open("config_optimisee.json", "w", encoding="utf-8") as f:
                json.dump(config_optimisee, f, indent=2, ensure_ascii=False)
            print("✓ Configuration optimisée sauvegardée dans 'config_optimisee.json'")
        except Exception as e:
            print(f"✗ Erreur sauvegarde config: {e}")

    if imports_ok and creation_ok and simulation_ok:
        print("\n🚀 INSTALLATION RÉUSSIE - PRÊT POUR LE LANCEMENT!")
        print("\nCommandes de lancement disponibles:")
        print("  python lancement.py                    # Lancement standard")
        print("  python lancement.py --diagnostic       # Diagnostic système")
        print("  python lancement.py --type univers_biopret --fps 120")
        print("  python lancement.py --config config_optimisee.json")
        return 0
    else:
        print("\n❌ DES PROBLÈMES ONT ÉTÉ DÉTECTÉS")
        print(
            "Consultez les erreurs ci-dessus et corrigez avant de lancer la simulation."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
