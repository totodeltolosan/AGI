"""
PROJET PROMETHEUS - MODULE CODEHUNTER (V3.0 - LE MANAGER)

Mission: Orchestrer le processus de recherche et de validation de code
en déléguant le travail à des modules spécialisés.

Architecture:
- Utilise LocalReader pour trouver le contenu pertinent.
- Utilise ContentExtractor pour extraire les blocs de code.
- Utilise CodeValidator pour filtrer les candidats techniquement.
- Utilise ValidationPresenter pour obtenir l'approbation finale du Superviseur.
- Utilise SemanticAnalyzer pour identifier les concepts à chasser.
"""

import os
import re
from typing import List, Dict

# Import des spécialistes
from LocalReader import LocalReader
from CodeValidator import CodeValidator
from ValidationPresenter import ValidationPresenter
from ContentExtractor import ContentExtractor
from SemanticAnalyzer import SemanticAnalyzer


# --- CLASSE DE COULEURS PARTAGÉE ---
class Colors:
    OKCYAN = "\033[96m"
    MAGENTA = "\033[95m"
    ENDC = "\033[0m"


class CodeHunter:
    """
    Chef d'orchestre pour la recherche et la validation d'exemples de code.
    """

    def __init__(self, supervisor_interface):
        """
        Initialise le CodeHunter et tous ses spécialistes.
        """
        self.supervisor = supervisor_interface

        # Création des instances des modules spécialisés
        self.local_reader = LocalReader()
        self.code_validator = CodeValidator(self.supervisor, self.local_reader)
        self.validation_presenter = ValidationPresenter(self.supervisor)
        self.content_extractor = ContentExtractor(self.supervisor)
        self.semantic_analyzer = SemanticAnalyzer(self.local_reader)

        self._display_code_info(f"Module initialisé avec ses 5 spécialistes.")

    def identify_concepts_in_analysis(self, analysis: Dict) -> List[str]:
        """
        Délègue l'identification des concepts au SemanticAnalyzer.
        """
        return self.semantic_analyzer.identify_concepts_from_analysis(analysis)

    def hunt_for_concept(self, concept_name: str) -> List[Dict]:
        """
        Méthode principale. Orchestre le cycle complet de recherche et validation pour UN concept.
        """
        self._display_code_info(
            f"Lancement de la chasse au code pour le concept: '{concept_name}'"
        )
        validated_examples = []

        # Étape 1: Délégation au LocalReader pour trouver le contenu
        content_result = self.local_reader.find_content_for_concept(concept_name)
        if not content_result:
            return []  # Le lecteur n'a rien trouvé, la chasse s'arrête.

        source_path, content = content_result

        # Étape 2: Extraction des blocs de code depuis le contenu Markdown
        code_candidates = self._extract_code_from_markdown(content)
        if not code_candidates:
            self._display_code_info(
                f"Aucun bloc de code trouvé dans '{os.path.basename(source_path)}'."
            )
            return []

        self._display_code_info(
            f"{len(code_candidates)} candidats de code trouvés. Début de la validation."
        )

        # Étape 3 & 4: Délégation au CodeValidator et au Presenter
        for i, snippet in enumerate(code_candidates):
            self._display_code_info(
                f"Analyse du candidat {i+1}/{len(code_candidates)}..."
            )

            # Délégation de la validation technique au CodeValidator
            validation_report = self.code_validator.validate_snippet(
                snippet, concept_name
            )

            if validation_report:
                # Le code est techniquement valide et pertinent.
                snippet_data = {
                    "snippet": snippet,
                    "url": source_path,  # La source est un chemin local
                    "final_score": 0,  # Le scoring peut être réintroduit plus tard
                }

                # Délégation de la présentation finale au ValidationPresenter
                approved_snippet = self.validation_presenter.present_for_final_approval(
                    snippet_data, concept_name, validation_report
                )

                if approved_snippet:
                    validated_examples.append(approved_snippet)
                    self._display_code_info(
                        "Exemple approuvé et ajouté à la collection."
                    )

        self._display_code_info(
            f"Chasse terminée. {len(validated_examples)} exemple(s) final(aux) validé(s) pour '{concept_name}'."
        )
        return validated_examples

    def _extract_code_from_markdown(self, markdown_text: str) -> List[str]:
        """
        Extrait les blocs de code Python à partir d'un texte au format Markdown.
        """
        pattern = r"```python\n(.*?)\n```"
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        return [match.strip() for match in matches]

    # Méthode utilitaire pour l'affichage
    def _display_code_info(self, message: str):
        if hasattr(self.supervisor, "display_code_info"):
            self.supervisor.display_code_info(message)
        else:
            print(f"{Colors.MAGENTA}[CODE-HUNTER] - {message}{Colors.ENDC}")
