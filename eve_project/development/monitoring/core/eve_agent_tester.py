#!/usr/bin/env python3
"""
EVE GENESIS - Agent Tester
Interface graphique pour tester chaque agent individuellement
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import json
import yaml
import os
import sys
import time
import requests
from datetime import datetime


class EVEAgentTester:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, root):
        self.root = root
        self.root.title("EVE GENESIS - Testeur d'Agents")
        self.root.geometry("1200x800")

        # Variables
        self.api_process = None
        self.api_running = False
        self.agents_data = {"crew_a": {}, "crew_b": {}}
        self.test_results = {}

        # Setup GUI
        self.setup_gui()

        # Charger les configurations agents
        self.load_agents_config()

    def setup_gui(self):
        """Création de l'interface graphique"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Titre
        title_label = ttk.Label(
            main_frame,
            text="🤖 EVE GENESIS - Testeur d'Agents",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Frame gauche - Contrôles
        control_frame = ttk.LabelFrame(main_frame, text="Contrôles", padding="10")
        control_frame.grid(
            row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10)
        )

        # Bouton démarrer API
        self.api_button = ttk.Button(
            control_frame, text="🚀 Démarrer API", command=self.toggle_api
        )
        self.api_button.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W + tk.E)

        # Status API
        self.api_status = ttk.Label(
            control_frame, text="❌ API Arrêtée", foreground="red"
        )
        self.api_status.grid(row=1, column=0, columnspan=2, pady=5)

        # Séparateur
        ttk.Separator(control_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, pady=10, sticky=tk.W + tk.E
        )

        # Selection Crew
        ttk.Label(control_frame, text="Crew à tester:").grid(
            row=3, column=0, sticky=tk.W
        )
        self.crew_var = tk.StringVar(value="crew_a")
        crew_combo = ttk.Combobox(
            control_frame,
            textvariable=self.crew_var,
            values=["crew_a", "crew_b"],
            state="readonly",
        )
        crew_combo.grid(row=3, column=1, sticky=tk.W + tk.E, padx=(5, 0))
        crew_combo.bind("<<ComboboxSelected>>", self.on_crew_change)

        # Liste des agents
        ttk.Label(control_frame, text="Agents:").grid(
            row=4, column=0, sticky=tk.W, pady=(10, 0)
        )

        # Frame pour la liste des agents avec scrollbar
        agents_frame = ttk.Frame(control_frame)
        agents_frame.grid(
            row=5, column=0, columnspan=2, pady=5, sticky=tk.W + tk.E + tk.N + tk.S
        )

        # Listbox avec scrollbar
        scrollbar = ttk.Scrollbar(agents_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.agents_listbox = tk.Listbox(
            agents_frame, yscrollcommand=scrollbar.set, height=10
        )
        self.agents_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.agents_listbox.yview)

        # Boutons de test
        test_frame = ttk.Frame(control_frame)
        test_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.W + tk.E)

        ttk.Button(
            test_frame,
            text="🧪 Tester Agent Sélectionné",
            command=self.test_selected_agent,
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            test_frame, text="🚀 Tester Tous les Agents", command=self.test_all_agents
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            test_frame, text="🧹 Nettoyer Résultats", command=self.clear_results
        ).pack(fill=tk.X, pady=2)

        # Configuration du grid pour le control_frame
        control_frame.columnconfigure(1, weight=1)
        control_frame.rowconfigure(5, weight=1)

        # Frame droite - Résultats
        results_frame = ttk.LabelFrame(
            main_frame, text="Résultats des Tests", padding="10"
        )
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)

        # Progress bar
        self.progress = ttk.Progressbar(results_frame, mode="determinate")
        self.progress.grid(row=0, column=0, sticky=tk.W + tk.E, pady=(0, 10))

        # Zone de texte pour les résultats
        self.results_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, width=60, height=25
        )
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame bas - Statistiques
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiques", padding="10")
        stats_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        self.stats_label = ttk.Label(stats_frame, text="Aucun test effectué")
        self.stats_label.pack()

    def load_agents_config(self):
        """Charge les configurations des agents depuis les fichiers YAML"""
        try:
            # Crew A
            crew_a_path = (
                "crew_a/src/eve_genesis___crew_a_construction_eveil/config/agents.yaml"
            )
            if os.path.exists(crew_a_path):
                with open(crew_a_path, "r", encoding="utf-8") as f:
                    self.agents_data["crew_a"] = yaml.safe_load(f)

            # Crew B
            crew_b_path = "crew_b/src/eve_genesis___crew_b/config/agents.yaml"
            if os.path.exists(crew_b_path):
                with open(crew_b_path, "r", encoding="utf-8") as f:
                    self.agents_data["crew_b"] = yaml.safe_load(f)

            self.update_agents_list()
            self.log_result("✅ Configurations d'agents chargées avec succès")

        except Exception as e:
            self.log_result(f"❌ Erreur lors du chargement des configs: {e}")

    def update_agents_list(self):
        """Met à jour la liste des agents selon le crew sélectionné"""
        self.agents_listbox.delete(0, tk.END)

        crew = self.crew_var.get()
        if crew in self.agents_data:
            for agent_name, agent_config in self.agents_data[crew].items():
                # Indicateur de statut
                status = self.test_results.get(f"{crew}_{agent_name}", "⏳")
                self.agents_listbox.insert(tk.END, f"{status} {agent_name}")

    def on_crew_change(self, event=None):
        """Appelé quand l'utilisateur change de crew"""
        self.update_agents_list()

    def toggle_api(self):
        """Démarre ou arrête l'API orchestrator"""
        if not self.api_running:
            self.start_api()
        else:
            self.stop_api()

    def start_api(self):
        """Démarre api_orchestrator.py en arrière-plan"""
        try:
            self.log_result("🚀 Démarrage de l'API Orchestrator...")

            # Lancer le processus en arrière-plan
            self.api_process = subprocess.Popen(
                [sys.executable, "api_orchestrator.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Attendre un peu pour que l'API démarre
            time.sleep(3)

            # Vérifier si l'API répond
            if self.check_api_health():
                self.api_running = True
                self.api_button.config(text="🛑 Arrêter API")
                self.api_status.config(text="✅ API Active", foreground="green")
                self.log_result("✅ API Orchestrator démarrée avec succès")
            else:
                self.log_result("❌ L'API ne répond pas")
                self.stop_api()

        except Exception as e:
            self.log_result(f"❌ Erreur démarrage API: {e}")

    def stop_api(self):
        """Arrête l'API orchestrator"""
        try:
            if self.api_process:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)

            self.api_running = False
            self.api_button.config(text="🚀 Démarrer API")
            self.api_status.config(text="❌ API Arrêtée", foreground="red")
            self.log_result("🛑 API Orchestrator arrêtée")

        except Exception as e:
            self.log_result(f"❌ Erreur arrêt API: {e}")

    def check_api_health(self):
        """Vérifie si l'API répond"""
        try:
            response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
            return response.status_code == 200
        except:
            return False

    def test_selected_agent(self):
        """Teste l'agent sélectionné"""
        selection = self.agents_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Attention", "Veuillez sélectionner un agent à tester"
            )
            return

        if not self.api_running:
            messagebox.showerror(
                "Erreur", "L'API doit être démarrée pour tester les agents"
            )
            return

        # Récupérer le nom de l'agent
        agent_text = self.agents_listbox.get(selection[0])
        agent_name = agent_text.split(" ", 1)[1]  # Enlever le status emoji

        # Lancer le test en thread séparé
        thread = threading.Thread(
            target=self.run_agent_test, args=(self.crew_var.get(), agent_name)
        )
        thread.daemon = True
        thread.start()

    def test_all_agents(self):
        """Teste tous les agents du crew sélectionné"""
        if not self.api_running:
            messagebox.showerror(
                "Erreur", "L'API doit être démarrée pour tester les agents"
            )
            return

        crew = self.crew_var.get()
        agents = list(self.agents_data[crew].keys())

        # Lancer les tests en thread séparé
        thread = threading.Thread(target=self.run_all_tests, args=(crew, agents))
        thread.daemon = True
        thread.start()

    def run_agent_test(self, crew, agent_name):
        """Execute le test d'un agent spécifique"""
        self.log_result(f"\n🧪 Test de l'agent: {agent_name} ({crew})")
        self.log_result("=" * 50)

        try:
            # Simuler un test d'agent (à adapter selon votre implémentation)
            # Ici vous pourriez appeler l'API pour tester un agent spécifique

            # Pour l'instant, simulation d'un test
            self.log_result(
                f"📋 Configuration: {self.agents_data[crew][agent_name]['role']}"
            )
            self.log_result(
                f"🎯 Objectif: {self.agents_data[crew][agent_name]['goal']}"
            )

            # Simuler test (remplacer par vrai test)
            time.sleep(2)  # Simulation temps de test

            # Test basique: vérifier si l'agent est bien configuré
            success = self.validate_agent_config(crew, agent_name)

            if success:
                self.test_results[f"{crew}_{agent_name}"] = "✅"
                self.log_result(f"✅ Agent {agent_name}: TEST RÉUSSI")
            else:
                self.test_results[f"{crew}_{agent_name}"] = "❌"
                self.log_result(f"❌ Agent {agent_name}: TEST ÉCHOUÉ")

        except Exception as e:
            self.test_results[f"{crew}_{agent_name}"] = "❌"
            self.log_result(f"❌ Erreur test {agent_name}: {e}")

        finally:
            # Mettre à jour l'affichage
            self.root.after(0, self.update_agents_list)
            self.root.after(0, self.update_stats)

    def run_all_tests(self, crew, agents):
        """Execute tous les tests d'agents"""
        self.log_result(f"\n🚀 Test de tous les agents de {crew.upper()}")
        self.log_result("=" * 60)

        total = len(agents)
        self.progress["maximum"] = total

        for i, agent_name in enumerate(agents):
            self.progress["value"] = i
            self.run_agent_test(crew, agent_name)

        self.progress["value"] = total
        self.log_result(f"\n🏁 Tests terminés pour {crew.upper()}")
        self.root.after(0, self.update_stats)

    def validate_agent_config(self, crew, agent_name):
        """Valide la configuration d'un agent"""
        try:
            config = self.agents_data[crew][agent_name]

            # Vérifications basiques
            required_fields = ["role", "goal", "backstory"]
            for field in required_fields:
                if field not in config or not config[field]:
                    self.log_result(f"  ❌ Champ manquant: {field}")
                    return False

            # Vérifications spécifiques
            if len(config["role"]) < 5:
                self.log_result(f"  ❌ Rôle trop court")
                return False

            if len(config["goal"]) < 20:
                self.log_result(f"  ❌ Objectif trop court")
                return False

            self.log_result(f"  ✅ Configuration valide")
            return True

        except Exception as e:
            self.log_result(f"  ❌ Erreur validation: {e}")
            return False

    def clear_results(self):
        """Nettoie les résultats de tests"""
        self.results_text.delete(1.0, tk.END)
        self.test_results.clear()
        self.progress["value"] = 0
        self.update_agents_list()
        self.update_stats()
        self.log_result("🧹 Résultats nettoyés")

    def update_stats(self):
        """Met à jour les statistiques"""
        total_tests = len(self.test_results)
        if total_tests == 0:
            self.stats_label.config(text="Aucun test effectué")
            return

        success = sum(1 for result in self.test_results.values() if result == "✅")
        failed = total_tests - success

        success_rate = (success / total_tests) * 100

        stats_text = f"Tests: {total_tests} | Réussis: {success} | Échoués: {failed} | Taux de réussite: {success_rate:.1f}%"
        self.stats_label.config(text=stats_text)

    def log_result(self, message):
        """Ajoute un message dans la zone de résultats"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()

    def on_closing(self):
        """Appelé à la fermeture de l'application"""
        if self.api_running:
            self.stop_api()
        self.root.destroy()


def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    app = EVEAgentTester(root)

    # Gérer la fermeture proprement
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Démarrer l'interface
    root.mainloop()


if __name__ == "__main__":
    main()