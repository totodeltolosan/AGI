"""
PROJET PROMETHEUS - MODULE SYSTEMINTERFACE (V1.0)

Mission: Gérer toute l'interaction avec le Superviseur. Affiche les menus,
pose les questions, et appelle les méthodes appropriées du PrometheusCore.
Ce module est l'unique point de contact avec l'utilisateur.
"""

# --- IMPORTS NÉCESSAIRES ---
import time
from datetime import datetime


# --- CLASSE DE COULEURS (copiée depuis prometheus_core.py) ---
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    MAGENTA = "\033[95m"


# ==============================================================================
# === BLOC 1 : CLASSE SUPERVISORINTERFACE (À COLLER ICI) ===
# ==============================================================================
class SupervisorInterface:
    @staticmethod
    def display_info(message: str):
        print(f"{Colors.OKCYAN}[PROMETHEUS] - {message}{Colors.ENDC}")

    @staticmethod
    def display_error(message: str):
        print(f"{Colors.FAIL}[PROMETHEUS] - {message}{Colors.ENDC}")

    @staticmethod
    def display_code_info(message: str):
        print(f"{Colors.MAGENTA}[CODE-HUNTER] - {message}{Colors.ENDC}")

    @staticmethod
    def get_authorization(prompt_text: str) -> str:
        prompt = (
            f"\n{Colors.WARNING}{Colors.BOLD}[PROMETHEUS] - AUTORISATION REQUISE{Colors.ENDC}\n"
            f"{Colors.WARNING}{prompt_text}{Colors.ENDC}\n> Acceptez-vous ? (oui/non/quitter): "
        )
        while True:
            response = input(prompt).lower().strip()
            if response in ["oui", "o", "non", "n", "quitter", "q"]:
                return response
            print(f"{Colors.FAIL}Réponse invalide.{Colors.ENDC}")

    @staticmethod
    def get_user_choice(prompt_text: str) -> str:
        prompt = f"\n{Colors.OKCYAN}{prompt_text}{Colors.ENDC}\n> "
        return input(prompt).lower().strip()


# ==============================================================================
# === BLOC 2 : CLASSE SYSTEMINTERFACE (SQUELETTE) ===
# ==============================================================================


class SystemInterface:
    """
    Chef d'orchestre du menu utilisateur et de l'interaction.
    """

    def __init__(self, prometheus_core):
        """
        Initialise l'interface en recevant une instance du coeur du système.
        """
        self.core = prometheus_core
        self.supervisor = prometheus_core.supervisor

    # ==========================================================================
    # === BLOC 3 : MÉTHODES DE MENU (À COLLER ICI) ===
    # ==========================================================================
    def _add_urls_to_queue(self, links: list):
        """GESTION DE LA FILE D'ATTENTE DES URLs"""
        while True:
            print(f"\n=== Liens trouvés (premiers {LINK_DISPLAY_LIMIT}) ===")
            display_links = links[:LINK_DISPLAY_LIMIT]

            for i, link in enumerate(display_links):
                print(f"  {Colors.OKGREEN}{i+1}:{Colors.ENDC} {link}")

            choice = self.supervisor.get_user_choice(
                f"Entrez les numéros des liens à ajouter à la file d'attente (ex: 1,3,5), 'tous', ou 'aucun' :"
            )

            if choice == "aucun":
                break

            selected_indices = []
            if choice == "tous":
                selected_indices = range(len(display_links))
            else:
                try:
                    selected_indices = [
                        int(num.strip()) - 1 for num in choice.split(",")
                    ]
                except ValueError:
                    self.supervisor.display_error("Entrée invalide.")
                    continue

            new_urls_added = 0
            for index in selected_indices:
                if 0 <= index < len(display_links):
                    url = display_links[index]
                    if url not in self.visited_urls and url not in self.urls_to_visit:
                        self.urls_to_visit.append(url)
                        new_urls_added += 1

            self.supervisor.display_info(
                f"➕ {new_urls_added} nouvelle(s) URL(s) ajoutée(s) à la file d'attente."
            )
            break

    def search_code_for_concept(self, concept: str) -> List[Dict]:
        """
        NOUVEL ORCHESTRATEUR V7.0

        Délègue la chasse au code complète au module CodeHunter.
        Retourne une liste d'exemples validés par le Superviseur.
        """
        self.supervisor.display_code_info(
            f"Délégation de la chasse au code pour '{concept}' au module CodeHunter."
        )

        # L'appel est maintenant unique et simple
        validated_examples = self.code_hunter.hunt_for_concept(concept)

        return validated_examples

    def _reanalyze_with_code_hunting(self, url: str):
        """
        RÉANALYSE COMPLÈTE V6.0 AVEC RECHERCHE DE CODE

        Utilise le CodeHunter modulaire pour l'identification et la recherche.
        """
        if url not in self.knowledge_base:
            self.supervisor.display_error("URL non trouvée dans la base.")
            return

        raw_content = self.knowledge_base[url].get("raw_content", "")
        if not raw_content:
            self.supervisor.display_error("Pas de contenu brut disponible.")
            return

        self.supervisor.display_info(f"🔄 RÉANALYSE COMPLÈTE V6.0 de: {url}")

        # Phase 2: Analyse cognitive
        analysis = self.analyst.analyze(url, raw_content, [])

        # Phase 3: Identification des concepts programmables (CodeHunter modulaire)
        identified_concepts = self.code_hunter.identify_concepts_in_analysis(analysis)

        if not identified_concepts:
            self.supervisor.display_info(
                "❌ Aucun concept programmable identifié sur cette page."
            )
            code_concepts = {
                "identified_concepts": [],
                "code_examples": {},
                "last_code_search": datetime.now().isoformat(),
            }
        else:
            self.supervisor.display_code_info(
                f"🎯 {len(identified_concepts)} concepts programmables identifiés: {', '.join(identified_concepts)}"
            )

            # Demande d'autorisation pour la recherche de code
            response = self.supervisor.get_authorization(
                f"Lancer la recherche de code pour ces {len(identified_concepts)} concepts ?"
            )

            code_examples = {}
            if response == "oui":
                for concept in identified_concepts:
                    search_result = self.search_code_for_concept(concept)
                    if search_result["examples"]:
                        code_examples[concept] = search_result

            code_concepts = {
                "identified_concepts": identified_concepts,
                "code_examples": code_examples,
                "last_code_search": datetime.now().isoformat(),
            }

        # Affichage des résultats
        self._display_analysis_results(analysis, code_concepts)

        # Sauvegarde complète
        self.save_knowledge(url, raw_content, analysis, code_concepts)

    def _display_analysis_results(self, analysis: dict, code_concepts: dict):
        """AFFICHAGE DES RÉSULTATS D'ANALYSE V6.0"""
        print(f"\n{Colors.HEADER}=== RÉSULTATS DE L'ANALYSE V6.0 ==={Colors.ENDC}")
        print(f"{Colors.OKGREEN}Titre:{Colors.ENDC} {analysis['title']}")
        print(f"{Colors.OKGREEN}Résumé:{Colors.ENDC} {analysis['summary'][:200]}...")
        print(
            f"{Colors.OKGREEN}Mots-clés:{Colors.ENDC} {', '.join(analysis['keywords'])}"
        )
        print(
            f"{Colors.OKGREEN}Définitions trouvées:{Colors.ENDC} {len(analysis['definitions'])}"
        )

        # V6.0: Affichage des résultats de code
        identified = code_concepts.get("identified_concepts", [])
        examples = code_concepts.get("code_examples", {})

        print(
            f"{Colors.MAGENTA}Concepts programmables identifiés:{Colors.ENDC} {len(identified)}"
        )
        if identified:
            for concept in identified:
                status = "✅ Avec code" if concept in examples else "⏳ Sans code"
                print(f"  • {concept} {status}")

        print(f"{Colors.MAGENTA}Exemples de code validés:{Colors.ENDC} {len(examples)}")
        for concept, data in examples.items():
            print(f"  • {concept}: {len(data.get('examples', []))} exemples")

    def _consult_code_examples(self):
        """CONSULTATION DES EXEMPLES DE CODE PAR CONCEPT"""
        all_examples = {}

        # Collecte de tous les exemples de code
        for url, data in self.knowledge_base.items():
            code_concepts = data.get("code_concepts", {})
            code_examples = code_concepts.get("code_examples", {})

            for concept, examples_data in code_examples.items():
                if concept not in all_examples:
                    all_examples[concept] = []
                all_examples[concept].extend(examples_data.get("examples", []))

        if not all_examples:
            self.supervisor.display_info(
                "❌ Aucun exemple de code trouvé dans la base de connaissances."
            )
            return

        # Affichage du menu des concepts
        print(f"\n{Colors.HEADER}=== CONCEPTS AVEC EXEMPLES DE CODE ==={Colors.ENDC}")
        concepts = list(all_examples.keys())

        for i, concept in enumerate(concepts, 1):
            count = len(all_examples[concept])
            print(f"  {Colors.OKGREEN}{i}:{Colors.ENDC} {concept} ({count} exemples)")

        try:
            choice = int(
                self.supervisor.get_user_choice(
                    "Numéro du concept à consulter (ou 0 pour annuler):"
                )
            )
            if choice == 0:
                return
            elif 1 <= choice <= len(concepts):
                concept = concepts[choice - 1]
                examples = all_examples[concept]

                print(
                    f"\n{Colors.HEADER}=== EXEMPLES POUR '{concept.upper()}' ==={Colors.ENDC}"
                )

                for i, example in enumerate(examples, 1):
                    print(
                        f"\n{Colors.WARNING}--- Exemple {i}/{len(examples)} ---{Colors.ENDC}"
                    )
                    print(
                        f"{Colors.OKCYAN}Source: {example.get('url', 'Inconnue')}{Colors.ENDC}"
                    )
                    print(
                        f"{Colors.OKCYAN}Statut: {example.get('validation_status', 'Non spécifié')}{Colors.ENDC}"
                    )
                    print(f"{Colors.OKBLUE}Code:{Colors.ENDC}")

                    # Affichage du code avec numérotation
                    snippet = example.get("snippet", "")
                    lines = snippet.split("\n")
                    for line_num, line in enumerate(lines, 1):
                        print(f"{Colors.WARNING}{line_num:2d}:{Colors.ENDC} {line}")

                    if i < len(examples):
                        input(
                            f"\n{Colors.OKCYAN}Appuyez sur Entrée pour l'exemple suivant...{Colors.ENDC}"
                        )
            else:
                self.supervisor.display_error("Numéro invalide.")
        except ValueError:
            self.supervisor.display_error("Entrée invalide.")

    def _search_new_examples_for_concept(self):
        """
        RECHERCHE DE NOUVEAUX EXEMPLES POUR UN CONCEPT SPÉCIFIQUE (V7.0)
        Utilise la nouvelle architecture de spécialistes.
        """
        concept = (
            input(
                f"\n{Colors.OKCYAN}Entrez le nom du concept (ex: fonction, boucle, classe): {Colors.ENDC}"
            )
            .strip()
            .lower()
        )

        if not concept:
            self.supervisor.display_error("Concept vide.")
            return

        # La vérification de l'existence du concept est maintenant gérée par les modules internes
        # (LocalReader, etc.), donc plus besoin de la faire ici.

        # --- NOUVELLE LOGIQUE D'APPEL ---
        # Lancement de la recherche via la méthode qui orchestre le CodeHunter
        validated_examples = self.search_code_for_concept(concept)

        if validated_examples:
            # --- NOUVELLE LOGIQUE DE SAUVEGARDE ---
            # On crée une entrée spéciale dans la base de connaissances pour cette recherche manuelle.
            special_url = (
                f"MANUAL_SEARCH_{concept}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # On prépare la structure de données pour les exemples de code.
            # La clé est le concept, la valeur est la liste des exemples.
            code_examples_data = {concept: validated_examples}

            code_concepts = {
                "identified_concepts": [concept],
                "code_examples": code_examples_data,
                "last_code_search": datetime.now().isoformat(),
            }

            # On crée une analyse factice pour cette entrée.
            analysis = {
                "title": f"Recherche manuelle: {concept}",
                "summary": f"Résultats d'une recherche manuelle d'exemples de code pour le concept '{concept}'.",
                "keywords": [concept],
                "definitions": {},
                "related_concepts": [],
            }

            # On sauvegarde la nouvelle connaissance.
            self.save_knowledge(
                special_url,
                f"Contenu généré par une recherche manuelle pour: {concept}",
                analysis,
                code_concepts,
            )

            self.supervisor.display_code_info(
                f"💾 {len(validated_examples)} nouvel(s) exemple(s) sauvegardé(s) pour '{concept}'"
            )
        else:
            # Ce message est maintenant géré par les modules internes, mais on garde une confirmation.
            self.supervisor.display_info(
                f"❌ La chasse au code n'a retourné aucun exemple validé pour '{concept}'."
            )

    def _reanalyze_with_code_hunting_menu(self):
        """MENU POUR LA RÉANALYSE COMPLÈTE V6.0"""
        if not self.knowledge_base:
            self.supervisor.display_info("Aucune page en base pour réanalyse.")
            return

        print(
            f"\n{Colors.MAGENTA}=== RÉANALYSE COMPLÈTE V6.0 AVEC RECHERCHE DE CODE ==={Colors.ENDC}"
        )
        urls = list(self.knowledge_base.keys())

        for i, url in enumerate(urls[:10]):
            title = (
                self.knowledge_base[url]
                .get("analysis", {})
                .get("title", "Titre inconnu")
            )
            if title in ["Titre inconnu", "Titre à réanalyser"]:
                if "/wiki/" in url:
                    title = url.split("/wiki/")[-1].replace("_", " ")
            print(f"  {Colors.OKGREEN}{i+1}:{Colors.ENDC} {title}")

        try:
            choice = int(
                self.supervisor.get_user_choice(
                    "Numéro de la page à réanalyser (ou 0 pour annuler):"
                )
            )
            if choice == 0:
                return
            elif 1 <= choice <= len(urls):
                url = urls[choice - 1]
                self._reanalyze_with_code_hunting(url)
            else:
                self.supervisor.display_error("Numéro invalide.")
        except ValueError:
            self.supervisor.display_error("Entrée invalide.")

    def _reanalyze_existing_page(self):
        """RÉANALYSE SIMPLE V5.0 (Maintenue pour compatibilité)"""
        if not self.knowledge_base:
            self.supervisor.display_info("Aucune page en base pour réanalyse.")
            return

        print(
            f"\n{Colors.OKCYAN}=== PAGES DISPONIBLES POUR RÉANALYSE V5.0 ==={Colors.ENDC}"
        )
        urls = list(self.knowledge_base.keys())

        for i, url in enumerate(urls[:10]):
            title = (
                self.knowledge_base[url]
                .get("analysis", {})
                .get("title", "Titre inconnu")
            )
            if title in ["Titre inconnu", "Titre à réanalyser"]:
                if "/wiki/" in url:
                    title = (
                        url.split("/wiki/")[-1]
                        .replace("_", " ")
                        .replace("%28", "(")
                        .replace("%29", ")")
                    )
            print(f"  {Colors.OKGREEN}{i+1}:{Colors.ENDC} {title}")
            print(f"      └── {Colors.WARNING}{url}{Colors.ENDC}")

        try:
            choice = int(
                self.supervisor.get_user_choice(
                    "Numéro de la page à réanalyser (ou 0 pour annuler):"
                )
            )
            if choice == 0:
                return
            elif 1 <= choice <= len(urls):
                url = urls[choice - 1]
                raw_content = self.knowledge_base[url].get("raw_content", "")

                if raw_content:
                    self.supervisor.display_info(f"🔄 Réanalyse en cours de: {url}")
                    analysis = self.analyst.analyze(url, raw_content, [])

                    # Affichage des résultats
                    print(
                        f"\n{Colors.HEADER}=== RÉSULTATS DE L'ANALYSE V5.0 ==={Colors.ENDC}"
                    )
                    print(f"{Colors.OKGREEN}Titre:{Colors.ENDC} {analysis['title']}")
                    print(
                        f"{Colors.OKGREEN}Résumé:{Colors.ENDC} {analysis['summary'][:200]}..."
                    )
                    print(
                        f"{Colors.OKGREEN}Mots-clés:{Colors.ENDC} {', '.join(analysis['keywords'])}"
                    )
                    print(
                        f"{Colors.OKGREEN}Définitions trouvées:{Colors.ENDC} {len(analysis['definitions'])}"
                    )
                    if analysis["definitions"]:
                        for concept, definition in list(
                            analysis["definitions"].items()
                        )[:3]:
                            print(f"  • {concept}: {definition[:100]}...")

                    # Sauvegarde avec préservation des code_concepts existants
                    existing_code = self.knowledge_base[url].get(
                        "code_concepts",
                        {
                            "identified_concepts": [],
                            "code_examples": {},
                            "last_code_search": None,
                        },
                    )
                    self.save_knowledge(url, raw_content, analysis, existing_code)
                else:
                    self.supervisor.display_error(
                        "Pas de contenu brut disponible pour cette page."
                    )
            else:
                self.supervisor.display_error("Numéro invalide.")
        except ValueError:
            self.supervisor.display_error("Entrée invalide.")

    def _explore_from_existing_links(self):
        """EXPLORATION DEPUIS LES LIENS EXISTANTS (V5.0 - Maintenue)"""
        available_links = []

        for url, data in self.knowledge_base.items():
            analysis = data.get("analysis", {})
            related_concepts = analysis.get("related_concepts", [])
            for link in related_concepts:
                if link not in self.visited_urls and link not in available_links:
                    available_links.append(link)

        if not available_links:
            self.supervisor.display_info(
                "❌ Aucun nouveau lien trouvé dans les analyses existantes."
            )
            response = self.supervisor.get_authorization(
                "Les pages n'ont peut-être pas été analysées avec V5.0. Voulez-vous d'abord réanalyser toutes les pages existantes ?"
            )

            if response == "oui":
                self._batch_reanalyze_all_pages()
                return
            else:
                self.supervisor.display_info(
                    "💡 Conseil: Utilisez l'option 1 pour réanalyser une page individuellement."
                )
                return

        self.supervisor.display_info(
            f"📊 {len(available_links)} liens disponibles depuis les pages analysées."
        )
        self._add_urls_to_queue(available_links)

    def _batch_reanalyze_all_pages(self):
        """RÉANALYSE EN LOT (V5.0 - Maintenue)"""
        if not self.knowledge_base:
            self.supervisor.display_info("Aucune page à réanalyser.")
            return

        pages_to_process = []
        for url, data in self.knowledge_base.items():
            raw_content = data.get("raw_content", "")
            if raw_content:
                pages_to_process.append((url, raw_content))

        if not pages_to_process:
            self.supervisor.display_error("Aucune page avec du contenu brut trouvée.")
            return

        self.supervisor.display_info(
            f"🔄 Réanalyse en lot de {len(pages_to_process)} pages..."
        )

        success_count = 0
        for i, (url, raw_content) in enumerate(pages_to_process, 1):
            print(
                f"{Colors.OKCYAN}[{i}/{len(pages_to_process)}] Analyse de: {url.split('/')[-1]}{Colors.ENDC}"
            )

            try:
                analysis = self.analyst.analyze(url, raw_content, [])

                # Préservation des code_concepts existants
                existing_code = self.knowledge_base[url].get(
                    "code_concepts",
                    {
                        "identified_concepts": [],
                        "code_examples": {},
                        "last_code_search": None,
                    },
                )

                self.save_knowledge(url, raw_content, analysis, existing_code)
                success_count += 1

            except Exception as e:
                self.supervisor.display_error(f"Erreur lors de l'analyse de {url}: {e}")

        self.supervisor.display_info(
            f"✅ Réanalyse en lot terminée: {success_count}/{len(pages_to_process)} pages traitées avec succès."
        )
