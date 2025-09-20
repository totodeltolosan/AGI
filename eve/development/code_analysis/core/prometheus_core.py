import json
import os
import time
import re  # Gardé pour une utilisation potentielle dans le futur
from datetime import datetime

# --- IMPORTS DES MODULES SPÉCIALISÉS (ARCHITECTURE V7.0) ---
from SupervisorInterface import (
    SupervisorInterface,
)  # On suppose que la classe est dans son propre fichier
from WebExplorer import WebExplorer
from Analyst import Analyst
from CodeHunter import CodeHunter

# --- CONSTANTES DE CONFIGURATION ---
KNOWLEDGE_BASE_FILE = "knowledge_base.json"
STATUS_HTML_FILE = "prometheus_status.html"
HTML_TEMPLATE_FILE = "prometheus_status.html"
LOG_LIMIT = 20
WIKIPEDIA_START_URL = "https://fr.wikipedia.org/wiki/Programmation_informatique"
LINK_DISPLAY_LIMIT = 50


class PrometheusCore:
    """
    CŒUR DU SYSTÈME PROMETHEUS V6.0 - L'APPRENTI (VERSION MODULAIRE)

    Architecture modulaire combinant:
    - Phase 1: Exploration et collecte (Cartographe)
    - Phase 2: Analyse et structuration (Analyste)
    - Phase 3: Recherche et validation de code (CodeHunter) ← MODULE SÉPARÉ
    """

    def __init__(self):
        """TODO: Add docstring."""
        self.supervisor = SupervisorInterface()
        self.explorer = WebExplorer(self.supervisor)
        self.analyst = Analyst(self.supervisor)

        # V6.0: CodeHunter comme module séparé
        self.code_hunter = CodeHunter(self.supervisor)

        self.knowledge_base = {}
        self.logs = []
        self.current_status = "Initialisation..."
        self.urls_to_visit = []
        self.visited_urls = set()
        self._ensure_files_exist()
        self.load_data()

    def _ensure_files_exist(self):
        """Assure l'existence des fichiers nécessaires"""
        if not os.path.exists(KNOWLEDGE_BASE_FILE):
            with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as f:
                f.write("{}")

    def load_data(self):
        """CHARGEMENT DES DONNÉES AVEC MIGRATION V6.0"""
        try:
            with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)

            # V5.0 → V6.0: MIGRATION DES STRUCTURES
            migration_needed = False
            migrated_count = 0

            for url, data in self.knowledge_base.items():
                # Migration V4.x → V5.0 (si nécessaire)
                if "content" in data and "raw_content" not in data:
                    data["raw_content"] = data["content"]
                    del data["content"]
                    migration_needed = True
                    migrated_count += 1

                if "analysis" not in data:
                    data["analysis"] = {
                        "title": "Titre à réanalyser",
                        "summary": "Analyse en attente",
                        "keywords": [],
                        "definitions": {},
                        "related_concepts": [],
                    }
                    migration_needed = True

                # V6.0: NOUVELLE SECTION CODE_CONCEPTS
                if "code_concepts" not in data:
                    data["code_concepts"] = {
                        "identified_concepts": [],
                        "code_examples": {},
                        "last_code_search": None,
                    }
                    migration_needed = True

            if migration_needed:
                with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
                self.supervisor.display_info(
                    f"🔄 MIGRATION V6.0 RÉUSSIE : Structure 'code_concepts' ajoutée"
                )

            self.visited_urls = set(self.knowledge_base.keys())
            self.supervisor.display_info(
                f"📚 {len(self.visited_urls)} URLs chargées avec architecture V6.0."
            )
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log_action(
                f"ERREUR CRITIQUE: Impossible de charger la base de connaissances. {e}"
            )
            exit(1)

    def save_knowledge(
        self, url: str, raw_content: str, analysis: dict, code_concepts: dict = None
    ):
        """
        SAUVEGARDE DE LA CONNAISSANCE COMPLÈTE (V6.0)

        Nouvelle architecture intégrant:
        - raw_content: Le contenu brut de la page
        - analysis: L'analyse structurée de l'Analyste
        - code_concepts: Les exemples de code du CodeHunter
        """
        if code_concepts is None:
            code_concepts = {
                "identified_concepts": [],
                "code_examples": {},
                "last_code_search": None,
            }

        self.knowledge_base[url] = {
            "raw_content": raw_content,
            "visited_at": datetime.now().isoformat(),
            "analysis": analysis,
            "code_concepts": code_concepts,
        }
        try:
            with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)

            self.supervisor.display_info(
                f"💾 Connaissance sauvegardée: {analysis.get('title', 'Titre inconnu')}"
            )

        except IOError as e:
            self.supervisor.display_error(
                f"ERREUR CRITIQUE: Impossible de sauvegarder la base de connaissances. {e}"
            )

    """TODO: Add docstring."""
    def log_action(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        if len(self.logs) > LOG_LIMIT:
            self.logs.pop(0)
                """TODO: Add docstring."""

    def update_status_html(self):
        # Simplifiée pour cette version - peut être étendue selon les besoins
        pass

    def run(self):
        """
        BOUCLE DE VIE PRINCIPALE DU SYSTÈME V6.0 - L'APPRENTI (MODULAIRE)

        Cycle triple: Exploration → Analyse → Recherche de Code (CodeHunter séparé)
        """
        self.log_action("🚀 Système Prometheus V6.0 (L'Apprenti) démarré.")
        self.supervisor.display_info(
            "🧠 PHASE 2 ACTIVÉE - Capacités d'analyse cognitives"
        )
        self.supervisor.display_code_info(
            "💻 PHASE 3 ACTIVÉE - Recherche et validation de code (Module séparé)"
        )

        # Affichage des statistiques du CodeHunter
        stats = self.code_hunter.get_search_statistics()
        self.supervisor.display_code_info(
            f"📊 CodeHunter: {stats['concepts_loaded']} concepts, {stats['trusted_sources']} sources"
        )

        while True:
            self.update_status_html()

            # PRIORITÉ 1: Traiter la file d'attente
            if self.urls_to_visit:
                current_url = self.urls_to_visit.pop(0)
                self.supervisor.display_info(
                    f"🎯 Prochaine cible dans la file d'attente : {current_url}"
                )

                response = self.supervisor.get_authorization(
                    f"Explorer et analyser cette URL avec recherche de code ?"
                )
                if response == "quitter":
                    break
                if response == "non":
                    self.supervisor.display_info(f"❌ URL {current_url} ignorée.")
                    self.visited_urls.add(current_url)
                    continue

                # PHASE 1: Exploration (Cartographe)
                exploration_result = self.explorer.explore_url(current_url)
                self.visited_urls.add(current_url)

                if exploration_result:
                    new_links, raw_content = exploration_result
                    self.supervisor.display_info(
                        f"✅ Exploration réussie. {len(new_links)} nouveaux liens trouvés."
                    )

                    # PHASE 2: Analyse cognitive (Analyste)
                    analysis = self.analyst.analyze(current_url, raw_content, new_links)

                    # PHASE 3: Recherche de code (CodeHunter modulaire)
                    identified_concepts = (
                        self.code_hunter.identify_programmable_concepts(analysis)
                    )

                    code_concepts = {
                        "identified_concepts": identified_concepts,
                        "code_examples": {},
                        "last_code_search": datetime.now().isoformat(),
                    }

                    if identified_concepts:
                        self.supervisor.display_code_info(
                            f"🎯 {len(identified_concepts)} concepts programmables identifiés"
                        )
                        response = self.supervisor.get_authorization(
                            f"Lancer la recherche de code pour ces concepts ?"
                        )

                        if response == "oui":
                            for concept in identified_concepts[
                                :3
                            ]:  # Limite pour éviter la surcharge
                                search_result = self.search_code_for_concept(concept)
                                if search_result["examples"]:
                                    code_concepts["code_examples"][
                                        concept
                                    ] = search_result

                    # Sauvegarde de la connaissance complète
                    self.save_knowledge(
                        current_url, raw_content, analysis, code_concepts
                    )

                    # Proposition d'URLs à explorer
                    if new_links:
                        self._add_urls_to_queue(new_links)

            # PRIORITÉ 2: Si la file est vide, gérer intelligemment selon la situation
            else:
                self.supervisor.display_info(
                    "📭 La file d'attente d'exploration est vide."
                )

                # VÉRIFICATION PRÉALABLE : Le point de départ a-t-il déjà été exploré ?
                if WIKIPEDIA_START_URL not in self.visited_urls:
                    response = self.supervisor.get_authorization(
                        f"Voulez-vous commencer une nouvelle exploration depuis le point de départ ({WIKIPEDIA_START_URL}) ?"
                    )
                    if response == "quitter":
                        break
                    elif response == "oui":
                        self.urls_to_visit.append(WIKIPEDIA_START_URL)
                        continue  # Retourner au début de la boucle

                # Menu d'alternatives V6.0
                print(
                    f"\n{Colors.WARNING}=== OPTIONS DISPONIBLES V6.0 ==={Colors.ENDC}"
                )
                print(
                    f"{Colors.OKGREEN}1.{Colors.ENDC} Réanalyser une page existante (tester l'Analyste V5.0)"
                )
                print(
                    f"{Colors.OKGREEN}2.{Colors.ENDC} Explorer les liens des pages déjà visitées"
                )
                print(
                    f"{Colors.OKGREEN}3.{Colors.ENDC} Entrer une URL Wikipedia manuelle"
                )
                print(
                    f"{Colors.MAGENTA}4.{Colors.ENDC} 🆕 Réanalyse complète avec recherche de code (V6.0)"
                )
                print(
                    f"{Colors.MAGENTA}5.{Colors.ENDC} 🆕 Consulter les exemples de code par concept"
                )
                print(
                    f"{Colors.MAGENTA}6.{Colors.ENDC} 🆕 Rechercher de nouveaux exemples pour un concept"
                )
                print(f"{Colors.OKGREEN}7.{Colors.ENDC} Quitter le système")

                choice = self.supervisor.get_user_choice("Choisissez une option (1-7):")

                if choice == "1":
                    self._reanalyze_existing_page()
                elif choice == "2":
                    self._explore_from_existing_links()
                elif choice == "3":
                    self._add_manual_url()
                elif choice == "4":
                    self._reanalyze_with_code_hunting_menu()
                elif choice == "5":
                    self._consult_code_examples()
                elif choice == "6":
                    self._search_new_examples_for_concept()
                elif choice == "7" or choice == "quitter":
                    break
                else:
                    self.supervisor.display_error("Option invalide.")
                    time.sleep(2)

            time.sleep(1)

    def _add_manual_url(self):
        """AJOUT MANUEL D'UNE URL WIKIPEDIA (V5.0 - Maintenue)"""
        url = input(
            f"\n{Colors.OKCYAN}Entrez l'URL Wikipedia complète (ou 'annuler'): {Colors.ENDC}"
        )

        if url.lower() == "annuler":
            return

        if not url.startswith("https://fr.wikipedia.org/wiki/"):
            self.supervisor.display_error(
                "URL invalide. Doit commencer par 'https://fr.wikipedia.org/wiki/'"
            )
            return

        if url in self.visited_urls:
            self.supervisor.display_info("Cette URL a déjà été visitée.")
            response = self.supervisor.get_authorization("Voulez-vous la réanalyser ?")
            if response == "oui":
                self._force_reanalyze_url(url)
            return

        if url in self.urls_to_visit:
            self.supervisor.display_info("Cette URL est déjà dans la file d'attente.")
            return

        self.urls_to_visit.append(url)
        self.supervisor.display_info(f"✅ URL ajoutée à la file d'attente: {url}")

    def _force_reanalyze_url(self, url: str):
        """FORCER LA RÉANALYSE D'UNE URL (V5.0 - Maintenue)"""
        if url in self.visited_urls:
            self.visited_urls.remove(url)
        self.urls_to_visit.append(url)
        self.supervisor.display_info(f"🔄 URL programmée pour re-exploration: {url}")


if __name__ == "__main__":
    try:
        print(
            f"{Colors.BOLD}{Colors.HEADER}--- DÉMARRAGE DU PROJET PROMETHEUS V6.0 (L'APPRENTI MODULAIRE) ---{Colors.ENDC}"
        )
        print(
            f"{Colors.OKCYAN}🧠 CAPACITÉS COGNITIVES: Analyse sémantique, extraction de connaissances{Colors.ENDC}"
        )
        print(
            f"{Colors.MAGENTA}💻 CAPACITÉS DE CODE: Recherche, validation et catalogue d'exemples (Module séparé){Colors.ENDC}"
        )
        print(
            f"{Colors.OKCYAN}📚 ARCHITECTURE: Collecte → Analyse → Recherche de Code{Colors.ENDC}"
        )
        core = PrometheusCore()
        core.run()
    except KeyboardInterrupt:
        print(
            f"\n{Colors.FAIL}⏹️ Arrêt manuel du système par le Superviseur.{Colors.ENDC}"
        )