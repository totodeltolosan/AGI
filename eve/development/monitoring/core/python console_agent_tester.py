#!/usr/bin/env python3
"""
EVE GENESIS - Console Agent Tester
Testeur d'agents en mode console (sans tkinter)
"""

import subprocess
import threading
import json
import yaml
import os
import sys
import time
import requests
from datetime import datetime
import signal


class ConsoleAgentTester:
    def __init__(self):
        self.api_process = None
        self.api_running = False
        self.agents_data = {"crew_a": {}, "crew_b": {}}
        self.test_results = {}

        # Configuration paths
        self.crew_paths = {
            "crew_a": "crew_a/src/eve_genesis___crew_a_construction_eveil",
            "crew_b": "crew_b/src/eve_genesis___crew_b",
        }

        # Setup signal handler pour arrêt propre
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        """Gestion arrêt propre avec Ctrl+C"""
        print("\n🛑 Arrêt en cours...")
        if self.api_running:
            self.stop_api()
        sys.exit(0)

    def print_header(self):
        """Affiche l'en-tête"""
        print("=" * 80)
        print("🤖 EVE GENESIS - TESTEUR D'AGENTS CONSOLE")
        print("=" * 80)
        print()

    def print_menu(self):
        """Affiche le menu principal"""
        print("\n📋 MENU PRINCIPAL:")
        print("1. 🚀 Démarrer/Arrêter API Orchestrator")
        print("2. 📊 Charger configurations agents")
        print("3. 👀 Voir liste des agents")
        print("4. 🧪 Tester un agent spécifique")
        print("5. ⚡ Test rapide tous agents (config seulement)")
        print("6. 🚀 Test complet tous agents")
        print("7. 📈 Voir statistiques")
        print("8. 🧹 Nettoyer résultats")
        print("9. ❌ Quitter")
        print("-" * 50)

    def print_status(self):
        """Affiche le statut actuel"""
        api_status = "✅ Active" if self.api_running else "❌ Arrêtée"
        crew_a_count = len(self.agents_data.get("crew_a", {}))
        crew_b_count = len(self.agents_data.get("crew_b", {}))
        tests_count = len(self.test_results)

        print(
            f"📊 STATUT: API {api_status} | Crew A: {crew_a_count} agents | Crew B: {crew_b_count} agents | Tests: {tests_count}"
        )

    def load_agents_config(self):
        """Charge les configurations des agents"""
        print("📦 Chargement des configurations...")

        for crew, base_path in self.crew_paths.items():
            agents_file = os.path.join(base_path, "config", "agents.yaml")
            try:
                if os.path.exists(agents_file):
                    with open(agents_file, "r", encoding="utf-8") as f:
                        self.agents_data[crew] = yaml.safe_load(f) or {}
                    print(
                        f"  ✅ {crew.upper()}: {len(self.agents_data[crew])} agents chargés"
                    )
                else:
                    self.agents_data[crew] = {}
                    print(f"  ⚠️ {crew.upper()}: Fichier agents.yaml non trouvé")
            except Exception as e:
                print(f"  ❌ {crew.upper()}: Erreur de chargement - {e}")
                self.agents_data[crew] = {}

        total_agents = sum(len(agents) for agents in self.agents_data.values())
        print(f"📊 Total: {total_agents} agents chargés")

    def list_agents(self):
        """Affiche la liste des agents"""
        print("\n👥 LISTE DES AGENTS:")
        print("-" * 80)

        for crew, agents in self.agents_data.items():
            if agents:
                print(f"\n🔧 {crew.upper()} ({len(agents)} agents):")
                for i, (agent_name, config) in enumerate(agents.items(), 1):
                    status = self.test_results.get(f"{crew}_{agent_name}", "⏳")
                    role = config.get("role", "N/A")[:50]
                    print(f"  {i:2d}. {status} {agent_name}")
                    print(f"      Rôle: {role}")
            else:
                print(f"\n🔧 {crew.upper()}: Aucun agent trouvé")

    def toggle_api(self):
        """Démarre ou arrête l'API"""
        if not self.api_running:
            self.start_api()
        else:
            self.stop_api()

    def start_api(self):
        """Démarre l'API Orchestrator"""
        print("🚀 Démarrage de l'API Orchestrator...")

        try:
            self.api_process = subprocess.Popen(
                [sys.executable, "api_orchestrator.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            print("⏳ Attente du démarrage de l'API...")
            time.sleep(3)

            if self.check_api_health():
                self.api_running = True
                print("✅ API Orchestrator démarrée avec succès!")
                print("🌐 Accessible sur: http://127.0.0.1:8000/docs")
            else:
                print("❌ L'API ne répond pas")
                self.stop_api()

        except Exception as e:
            print(f"❌ Erreur lors du démarrage de l'API: {e}")

    def stop_api(self):
        """Arrête l'API Orchestrator"""
        print("🛑 Arrêt de l'API Orchestrator...")

        try:
            if self.api_process:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)

            self.api_running = False
            print("✅ API Orchestrator arrêtée")

        except Exception as e:
            print(f"❌ Erreur lors de l'arrêt de l'API: {e}")

    def check_api_health(self):
        """Vérifie si l'API répond"""
        try:
            response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
            return response.status_code == 200
        except:
            return False

    def test_specific_agent(self):
        """Teste un agent spécifique"""
        # Sélection du crew
        print("\n🔧 Sélection du crew:")
        print("1. Crew A (Construction)")
        print("2. Crew B (Enrichissement)")

        try:
            crew_choice = input("Votre choix (1 ou 2): ").strip()
            crew = (
                "crew_a"
                if crew_choice == "1"
                else "crew_b" if crew_choice == "2" else None
            )

            if not crew:
                print("❌ Choix invalide")
                return

            if not self.agents_data[crew]:
                print(f"❌ Aucun agent trouvé pour {crew.upper()}")
                return

            # Affichage des agents
            agents_list = list(self.agents_data[crew].keys())
            print(f"\n👥 Agents disponibles dans {crew.upper()}:")
            for i, agent_name in enumerate(agents_list, 1):
                status = self.test_results.get(f"{crew}_{agent_name}", "⏳")
                print(f"  {i:2d}. {status} {agent_name}")

            # Sélection de l'agent
            try:
                agent_choice = (
                    int(input(f"\nSélectionnez un agent (1-{len(agents_list)}): ")) - 1
                )
                if 0 <= agent_choice < len(agents_list):
                    agent_name = agents_list[agent_choice]
                    self.run_single_agent_test(crew, agent_name)
                else:
                    print("❌ Numéro invalide")
            except ValueError:
                print("❌ Veuillez entrer un numéro valide")

        except KeyboardInterrupt:
            print("\n🛑 Test annulé")

    def run_single_agent_test(self, crew, agent_name):
        """Exécute le test d'un seul agent"""
        print(f"\n🧪 TEST DE L'AGENT: {agent_name}")
        print("=" * 60)

        try:
            # 1. Test configuration
            print("📋 1. Validation de la configuration...")
            if not self.validate_agent_config(crew, agent_name):
                self.test_results[f"{crew}_{agent_name}"] = "❌"
                print(f"❌ {agent_name}: ÉCHEC (Configuration invalide)")
                return

            # 2. Test structure fichiers
            print("📁 2. Vérification de la structure...")
            if not self.check_crew_structure(crew):
                self.test_results[f"{crew}_{agent_name}"] = "⚠️"
                print(f"⚠️ {agent_name}: ATTENTION (Structure incomplète)")

            # 3. Test API (si active)
            if self.api_running:
                print("🌐 3. Test de communication API...")
                if self.check_api_health():
                    print("   ✅ API accessible")
                else:
                    print("   ⚠️ Problème de communication API")
            else:
                print("🌐 3. API non démarrée - test ignoré")

            # Résultat final
            self.test_results[f"{crew}_{agent_name}"] = "✅"
            print(f"🎉 {agent_name}: TEST RÉUSSI!")

        except Exception as e:
            self.test_results[f"{crew}_{agent_name}"] = "❌"
            print(f"💥 {agent_name}: ERREUR - {e}")

    def validate_agent_config(self, crew, agent_name):
        """Valide la configuration d'un agent"""
        try:
            config = self.agents_data[crew][agent_name]

            # Champs obligatoires
            required_fields = ["role", "goal", "backstory"]
            for field in required_fields:
                if field not in config or not config[field]:
                    print(f"   ❌ Champ manquant: {field}")
                    return False

            # Validation qualité
            if len(config["role"]) < 10:
                print(f"   ❌ Rôle trop court: {len(config['role'])} caractères")
                return False

            if len(config["goal"]) < 30:
                print(f"   ❌ Objectif trop court: {len(config['goal'])} caractères")
                return False

            if len(config["backstory"]) < 50:
                print(
                    f"   ❌ Backstory trop courte: {len(config['backstory'])} caractères"
                )
                return False

            print(f"   ✅ Configuration valide")
            return True

        except Exception as e:
            print(f"   ❌ Erreur de validation: {e}")
            return False

    def check_crew_structure(self, crew):
        """Vérifie la structure des fichiers du crew"""
        base_path = self.crew_paths[crew]
        required_files = [
            "config/agents.yaml",
            "config/tasks.yaml",
            "crew.py",
            "main.py",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(base_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)

        if missing_files:
            print(f"   ⚠️ Fichiers manquants: {', '.join(missing_files)}")
            return False

        print(f"   ✅ Structure complète")
        return True

    def quick_test_all(self):
        """Test rapide de tous les agents (config seulement)"""
        print("\n⚡ TEST RAPIDE DE TOUS LES AGENTS")
        print("=" * 60)

        total_agents = 0
        for crew, agents in self.agents_data.items():
            if agents:
                print(f"\n🔧 Test {crew.upper()} ({len(agents)} agents):")
                for agent_name in agents:
                    if self.validate_agent_config(crew, agent_name):
                        self.test_results[f"{crew}_{agent_name}"] = "✅"
                        print(f"  ✅ {agent_name}")
                    else:
                        self.test_results[f"{crew}_{agent_name}"] = "❌"
                        print(f"  ❌ {agent_name}")
                    total_agents += 1

        self.show_statistics()
        print(f"\n⚡ Test rapide terminé - {total_agents} agents testés")

    def full_test_all(self):
        """Test complet de tous les agents"""
        print("\n🚀 TEST COMPLET DE TOUS LES AGENTS")
        print("=" * 60)

        total_agents = 0
        for crew, agents in self.agents_data.items():
            if agents:
                print(f"\n🔧 Test complet {crew.upper()}:")
                for agent_name in agents:
                    print(f"\n  Testing: {agent_name}")
                    self.run_single_agent_test(crew, agent_name)
                    total_agents += 1
                    time.sleep(0.5)  # Pause entre tests

        self.show_statistics()
        print(f"\n🏁 Test complet terminé - {total_agents} agents testés")

    def show_statistics(self):
        """Affiche les statistiques des tests"""
        if not self.test_results:
            print("\n📊 Aucun test effectué")
            return

        total = len(self.test_results)
        success = sum(1 for result in self.test_results.values() if result == "✅")
        warning = sum(1 for result in self.test_results.values() if result == "⚠️")
        failed = total - success - warning

        success_rate = (success / total) * 100 if total > 0 else 0

        print(f"\n📊 STATISTIQUES:")
        print(f"   Total testés: {total}")
        print(f"   ✅ Réussis: {success}")
        print(f"   ⚠️ Avertissements: {warning}")
        print(f"   ❌ Échecs: {failed}")
        print(f"   📈 Taux de réussite: {success_rate:.1f}%")

        # Détail des échecs
        if failed > 0:
            print(f"\n❌ AGENTS EN ÉCHEC:")
            for test_id, result in self.test_results.items():
                if result == "❌":
                    crew, agent = test_id.split("_", 1)
                    print(f"   - {agent} ({crew.upper()})")

    def clear_results(self):
        """Nettoie les résultats"""
        self.test_results.clear()
        print("🧹 Résultats nettoyés")

    def run(self):
        """Boucle principale du programme"""
        self.print_header()

        while True:
            try:
                self.print_status()
                self.print_menu()

                choice = input("Votre choix: ").strip()

                if choice == "1":
                    self.toggle_api()
                elif choice == "2":
                    self.load_agents_config()
                elif choice == "3":
                    self.list_agents()
                elif choice == "4":
                    self.test_specific_agent()
                elif choice == "5":
                    self.quick_test_all()
                elif choice == "6":
                    self.full_test_all()
                elif choice == "7":
                    self.show_statistics()
                elif choice == "8":
                    self.clear_results()
                elif choice == "9":
                    print("👋 Au revoir!")
                    if self.api_running:
                        self.stop_api()
                    break
                else:
                    print("❌ Choix invalide. Veuillez entrer un numéro entre 1 et 9.")

                input("\n⏸️ Appuyez sur Entrée pour continuer...")
                print("\n" + "=" * 80 + "\n")

            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                if self.api_running:
                    self.stop_api()
                break
            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")


def main():
    """Point d'entrée principal"""
    # Vérifier les dépendances
    try:
        import yaml
        import requests
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez avec: pip install pyyaml requests")
        sys.exit(1)

    # Lancer l'application
    tester = ConsoleAgentTester()
    tester.run()


if __name__ == "__main__":
    main()
