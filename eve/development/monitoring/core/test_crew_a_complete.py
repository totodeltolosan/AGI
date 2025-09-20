#!/usr/bin/env python3
"""
Script de test pour l'exécution complète du Crew A EVE GENESIS
Test de l'ingénieur adaptatif avec 41 agents et 40 tâches

🤖 EVE GENESIS CREW A - TEST COMPLET
🧬 L'Ingénieur Adaptatif & Supervisable
📊 41 Agents | 40 Tâches | 6 Missions Critiques

Ce script lance une exécution complète du Crew A qui va :
- Construire l'infrastructure projet EVE GENESIS
- Générer le code source complet
- Créer les tests et la documentation
- Packager l'application
- Déployer intelligemment
- Créer le monde virtuel initial
- Éveiller EVE pour la première fois
"""

import sys
import os
import time
import json
import subprocess
import traceback
import threading
from pathlib import Path
from datetime import datetime, timedelta

# Vérification des imports optionnels
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil non disponible - monitoring système limité")

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests non disponible - vérification Ollama limitée")


class CrewATestMonitor:
    """Moniteur pour l'exécution du Crew A."""

    def __init__(self):
        """TODO: Add docstring."""
        self.start_time = datetime.now()
        self.stats = {
            "tasks_completed": 0,
            "agents_active": 0,
            "errors_count": 0,
            "memory_peak": 0,
            "cpu_peak": 0,
        }
        self.running = True

    def log_with_timestamp(self, message, level="INFO"):
        """Log avec timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        elapsed = datetime.now() - self.start_time
        print(f"[{timestamp}] [{level}] {message} (Elapsed: {elapsed})")

    def monitor_system(self):
        """Monitoring système en arrière-plan."""
        while self.running and PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=1)

                self.stats["memory_peak"] = max(
                    self.stats["memory_peak"], memory.percent
                )
                self.stats["cpu_peak"] = max(self.stats["cpu_peak"], cpu)

                # Log périodique toutes les 5 minutes
                if (datetime.now() - self.start_time).seconds % 300 == 0:
                    self.log_with_timestamp(
                        f"System: RAM {memory.percent:.1f}% | CPU {cpu:.1f}% | "
                        f"Peak RAM {self.stats['memory_peak']:.1f}% | Peak CPU {self.stats['cpu_peak']:.1f}%",
                        "MONITOR",
                    )

                time.sleep(30)  # Vérification toutes les 30 secondes
            except Exception as e:
                self.log_with_timestamp(f"Erreur monitoring: {e}", "ERROR")
                time.sleep(60)

    def stop(self):
        """Arrêt du monitoring."""
        self.running = False


def check_prerequisites():
    """Vérification complète des prérequis système."""
    print("🔍 VÉRIFICATION DES PRÉREQUIS SYSTÈME")
    print("=" * 50)

    checks = []

    # 1. Version Python
    python_version = sys.version_info
    python_ok = python_version >= (3, 10)
    checks.append(
        (
            "Python >= 3.10",
            python_ok,
            f"{python_version.major}.{python_version.minor}.{python_version.micro}",
        )
    )

    # 2. Système de fichiers
    current_dir = Path.cwd()
    crew_a_path = current_dir / "crew_a"
    structure_ok = crew_a_path.exists()
    checks.append(("Structure crew_a", structure_ok, f"Chemin: {crew_a_path}"))

    # 3. RAM disponible (si psutil disponible)
    if PSUTIL_AVAILABLE:
        memory = psutil.virtual_memory()
        ram_ok = memory.available > 8 * 1024**3  # 8GB
        checks.append(
            ("RAM > 8GB", ram_ok, f"{memory.available / (1024**3):.1f}GB disponible")
        )

        # 4. Espace disque
        disk = psutil.disk_usage(".")
        disk_ok = disk.free > 10 * 1024**3  # 10GB
        checks.append(
            ("Disque > 10GB", disk_ok, f"{disk.free / (1024**3):.1f}GB libre")
        )

        # 5. CPU
        cpu_count = psutil.cpu_count()
        cpu_ok = cpu_count >= 4
        checks.append(("CPU >= 4 cores", cpu_ok, f"{cpu_count} cœurs"))
    else:
        checks.append(("Monitoring système", False, "psutil non installé"))

    # 6. Ollama (si requests disponible)
    if REQUESTS_AVAILABLE:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            ollama_ok = response.status_code == 200
            if ollama_ok:
                models = response.json().get("models", [])
                llama3_ok = any("llama3" in model.get("name", "") for model in models)
                checks.append(("Ollama actif", True, f"{len(models)} modèles"))
                checks.append(("Modèle llama3", llama3_ok, "Requis pour Crew A"))
            else:
                checks.append(("Ollama actif", False, f"HTTP {response.status_code}"))
        except Exception as e:
            checks.append(("Ollama actif", False, f"Erreur: {str(e)[:50]}"))
    else:
        checks.append(("Vérification Ollama", False, "requests non installé"))

    # 7. Dépendances Python critiques
    critical_deps = ["pathlib", "json", "subprocess", "threading", "datetime"]
    missing_critical = []
    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_critical.append(dep)

    deps_critical_ok = len(missing_critical) == 0
    checks.append(
        (
            "Dépendances critiques",
            deps_critical_ok,
            (
                f"Manquantes: {missing_critical}"
                if missing_critical
                else "Toutes présentes"
            ),
        )
    )

    # 8. Dépendances optionnelles
    optional_deps = ["crewai", "pydantic", "yaml"]
    missing_optional = []
    for dep in optional_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_optional.append(dep)

    deps_optional_ok = len(missing_optional) == 0
    checks.append(
        (
            "Dépendances optionnelles",
            deps_optional_ok,
            (
                f"Manquantes: {missing_optional}"
                if missing_optional
                else "Toutes présentes"
            ),
        )
    )

    # Affichage des résultats
    print()
    all_critical_ok = True
    warnings = []

    for name, ok, detail in checks:
        status = "✅" if ok else "❌"
        print(f"{status} {name}: {detail}")

        # Identification des problèmes critiques vs warnings
        if not ok:
            if name in ["Python >= 3.10", "Structure crew_a", "Dépendances critiques"]:
                all_critical_ok = False
            else:
                warnings.append(name)

    print(f"\n📊 RÉSUMÉ:")
    print(f"✅ Vérifications critiques: {'RÉUSSIES' if all_critical_ok else 'ÉCHEC'}")
    if warnings:
        print(f"⚠️ Avertissements: {len(warnings)} ({', '.join(warnings)})")

    return all_critical_ok, len(warnings), checks


def prepare_environment():
    """Préparation de l'environnement d'exécution."""
    print("\n🏗️ PRÉPARATION DE L'ENVIRONNEMENT")
    print("-" * 40)

    # Création des dossiers nécessaires
    required_dirs = [
        "logs",
        "temp",
        "output",
        "data/backups",
        "data/reports",
        "monitoring",
    ]

    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Dossier créé/vérifié: {dir_path}")

    # Variables d'environnement
    env_vars = {
        "EVE_ENV": "test",
        "EVE_LOG_LEVEL": "INFO",
        "EVE_TEST_MODE": "true",
        "PYTHONPATH": str(Path.cwd()),
    }

    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ Variable d'environnement: {key}={value}")

    print("✅ Environnement préparé")


def execute_crew_a():
    """Exécution principale du Crew A."""
    print("\n🚀 LANCEMENT DU CREW A EVE GENESIS")
    print("=" * 60)
    print("⚠️ ATTENTION: Cette exécution peut prendre 2-6 heures")
    print("📊 41 agents vont travailler séquentiellement sur 40 tâches")
    print("🎯 Objectif: Construction complète d'EVE GENESIS\n")

    monitor = CrewATestMonitor()

    try:
        # Démarrage du monitoring système
        if PSUTIL_AVAILABLE:
            monitor_thread = threading.Thread(target=monitor.monitor_system)
            monitor_thread.daemon = True
            monitor_thread.start()
            monitor.log_with_timestamp("Monitoring système démarré", "SYSTEM")

        # Changement vers le répertoire crew_a
        crew_a_path = Path("crew_a")
        original_cwd = os.getcwd()

        if not crew_a_path.exists():
            raise FileNotFoundError("❌ Dossier crew_a non trouvé")

        os.chdir(crew_a_path)
        monitor.log_with_timestamp(f"Répertoire de travail: {os.getcwd()}", "SETUP")

        # Configuration de la commande d'exécution
        main_script = Path("src/eve_genesis___crew_a_construction_eveil/main.py")
        if not main_script.exists():
            raise FileNotFoundError(f"❌ Script principal non trouvé: {main_script}")

        cmd = [sys.executable, str(main_script), "run"]
        monitor.log_with_timestamp(f"Commande: {' '.join(cmd)}", "SETUP")

        # Lancement du processus principal
        monitor.log_with_timestamp("🚀 DÉMARRAGE DE L'EXÉCUTION CREW A", "START")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
        )

        # Collecte des logs en temps réel
        output_lines = []
        error_lines = []
        task_count = 0

        while True:
            # Lecture de la sortie standard
            output = process.stdout.readline()
            if output:
                line = output.strip()
                output_lines.append(line)

                # Détection des événements importants
                if "Task" in line and "completed" in line:
                    task_count += 1
                    monitor.stats["tasks_completed"] = task_count
                    monitor.log_with_timestamp(
                        f"Tâche terminée #{task_count}: {line[:100]}", "TASK"
                    )

                elif "Agent" in line and ("starting" in line or "created" in line):
                    monitor.stats["agents_active"] += 1
                    monitor.log_with_timestamp(f"Agent actif: {line[:100]}", "AGENT")

                elif "ERROR" in line.upper() or "FAILED" in line.upper():
                    monitor.stats["errors_count"] += 1
                    monitor.log_with_timestamp(f"ERREUR DÉTECTÉE: {line}", "ERROR")

                elif any(
                    keyword in line for keyword in ["SUCCESS", "COMPLETED", "FINISHED"]
                ):
                    monitor.log_with_timestamp(f"SUCCÈS: {line[:100]}", "SUCCESS")

                # Log périodique de progression
                if len(output_lines) % 50 == 0:
                    monitor.log_with_timestamp(
                        f"Progression: {len(output_lines)} lignes | {task_count} tâches",
                        "PROGRESS",
                    )

            # Lecture des erreurs
            error = process.stderr.readline()
            if error:
                line = error.strip()
                error_lines.append(line)
                monitor.log_with_timestamp(f"STDERR: {line}", "ERROR")

            # Vérification de fin de processus
            if process.poll() is not None:
                break

            # Sécurité anti-blocage
            if len(output_lines) > 100000:  # Plus de 100k lignes = problème potentiel
                monitor.log_with_timestamp(
                    "AVERTISSEMENT: Sortie très volumineuse détectée", "WARNING"
                )

        # Récupération des dernières lignes
        remaining_output, remaining_errors = process.communicate()
        if remaining_output:
            output_lines.extend(remaining_output.strip().split("\n"))
        if remaining_errors:
            error_lines.extend(remaining_errors.strip().split("\n"))

        # Analyse du résultat
        return_code = process.returncode
        execution_time = datetime.now() - monitor.start_time

        monitor.log_with_timestamp(f"🏁 EXÉCUTION TERMINÉE", "END")
        monitor.log_with_timestamp(f"Code de retour: {return_code}", "RESULT")
        monitor.log_with_timestamp(f"Temps total: {execution_time}", "RESULT")

        # Retour au répertoire original
        os.chdir(original_cwd)
        monitor.stop()

        # Création du rapport détaillé
        result = {
            "success": return_code == 0,
            "return_code": return_code,
            "execution_time": str(execution_time),
            "start_time": monitor.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "statistics": monitor.stats,
            "output_summary": {
                "total_lines": len(output_lines),
                "error_lines": len(error_lines),
                "last_10_outputs": output_lines[-10:] if output_lines else [],
                "last_10_errors": error_lines[-10:] if error_lines else [],
            },
        }

        return result

    except Exception as e:
        execution_time = datetime.now() - monitor.start_time
        monitor.log_with_timestamp(f"ERREUR CRITIQUE: {e}", "CRITICAL")
        monitor.log_with_timestamp(f"Traceback: {traceback.format_exc()}", "DEBUG")
        monitor.stop()

        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "execution_time": str(execution_time),
            "statistics": monitor.stats,
        }


def generate_report(prereq_checks, result):
    """Génération du rapport final complet."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"logs/crew_a_execution_report_{timestamp}.json"

    # Construction du rapport complet
    full_report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "test_version": "1.0.0",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "working_directory": str(Path.cwd()),
        },
        "prerequisites": {
            "checks": dict(
                [
                    (check[0], {"passed": check[1], "detail": check[2]})
                    for check in prereq_checks
                ]
            ),
            "summary": {
                "all_critical_passed": result.get("success", False),
                "warnings_count": len([c for c in prereq_checks if not c[1]]),
            },
        },
        "execution": result,
        "recommendations": [],
    }

    # Génération de recommandations
    if not result.get("success", False):
        full_report["recommendations"].append(
            "Vérifier les logs d'erreur pour identifier les problèmes"
        )
        full_report["recommendations"].append(
            "S'assurer qu'Ollama est démarré avec le modèle llama3:8b"
        )
        full_report["recommendations"].append(
            "Vérifier que les dépendances Python sont installées"
        )

    if result.get("statistics", {}).get("errors_count", 0) > 0:
        full_report["recommendations"].append(
            "Analyser les erreurs détectées pendant l'exécution"
        )

    # Sauvegarde du rapport
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n📄 RAPPORT COMPLET SAUVEGARDÉ: {report_file}")
        return report_file
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du rapport: {e}")
        return None


def main():
    """Fonction principale orchestrant tout le test."""
    print("🤖 EVE GENESIS CREW A - TEST D'EXÉCUTION COMPLET")
    print("🧬 L'Ingénieur Adaptatif & Supervisable 41 Agents")
    print("=" * 70)
    print(f"🕐 Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Phase 1: Vérification des prérequis
        critical_ok, warnings_count, prereq_checks = check_prerequisites()

        if not critical_ok:
            print("\n❌ ÉCHEC DES PRÉREQUIS CRITIQUES")
            print("Les problèmes suivants doivent être résolus:")
            for check in prereq_checks:
                if not check[1] and check[0] in [
                    "Python >= 3.10",
                    "Structure crew_a",
                    "Dépendances critiques",
                ]:
                    print(f"  - {check[0]}: {check[2]}")
            return False

        if warnings_count > 0:
            print(f"\n⚠️ {warnings_count} AVERTISSEMENT(S) DÉTECTÉ(S)")
            print(
                "L'exécution peut continuer mais certaines fonctionnalités peuvent être limitées."
            )

        print("\n✅ PRÉREQUIS VALIDÉS - PRÊT POUR L'EXÉCUTION")

        # Phase 2: Préparation de l'environnement
        prepare_environment()

        # Phase 3: Confirmation de lancement
        print(f"\n⚠️ DERNIÈRE CONFIRMATION:")
        print(f"- Durée estimée: 2-6 heures")
        print(f"- 41 agents vont s'exécuter séquentiellement")
        print(f"- 40 tâches complexes seront traitées")
        print(f"- Consommation intensive des ressources")
        print(f"- Création de nombreux fichiers")

        print(f"\n🚀 LANCEMENT AUTOMATIQUE DANS 5 SECONDES...")
        for i in range(5, 0, -1):
            print(f"⏱️ {i}...")
            time.sleep(1)

        # Phase 4: Exécution principale
        print(f"\n🎯 DÉBUT DE L'EXÉCUTION DU CREW A")
        result = execute_crew_a()

        # Phase 5: Analyse des résultats
        print(f"\n📊 ANALYSE DES RÉSULTATS:")
        if result.get("success"):
            print("✅ EXÉCUTION RÉUSSIE!")
            print(f"✅ Temps d'exécution: {result['execution_time']}")
            print(
                f"✅ Tâches complétées: {result.get('statistics', {}).get('tasks_completed', 'Unknown')}"
            )
            print(
                f"✅ Agents utilisés: {result.get('statistics', {}).get('agents_active', 'Unknown')}"
            )
        else:
            print("❌ EXÉCUTION ÉCHOUÉE")
            print(f"❌ Erreur: {result.get('error', 'Unknown')}")
            print(f"❌ Code retour: {result.get('return_code', 'Unknown')}")

        # Phase 6: Génération du rapport final
        report_file = generate_report(prereq_checks, result)

        print(f"\n🏁 TEST TERMINÉ")
        print(f"📄 Rapport détaillé: {report_file}")
        print(f"🕐 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return result.get("success", False)

    except KeyboardInterrupt:
        print(f"\n⚠️ INTERRUPTION UTILISATEUR")
        print(f"Test arrêté manuellement")
        return False

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE NON GÉRÉE:")
        print(f"❌ {e}")
        print(f"❌ Traceback complet:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print(__doc__)
    success = main()
    exit_code = 0 if success else 1
    print(f"\n🚪 Code de sortie: {exit_code}")
    sys.exit(exit_code)