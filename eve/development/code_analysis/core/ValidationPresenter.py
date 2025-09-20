"""
PROJET PROMETHEUS - MODULE SPÉCIALISÉ VALIDATIONPRESENTER (V1.0)

Mission: Agir comme l'interface de présentation pour la validation finale
par le Superviseur. Ce module est "l'avocat" qui présente les preuves.

Responsabilités:
- Recevoir un snippet de code et son rapport de validation technique.
- Le présenter de manière claire et informative au Superviseur.
- Recueillir la décision finale (oui/non/quitter).
- Retourner le snippet enrichi avec les informations de validation si approuvé.
"""

import re
from datetime import datetime
from typing import Dict, List


# --- CLASSE DE COULEURS PARTAGÉE ---
class Colors:
    """TODO: Add docstring."""
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class ValidationPresenter:
    """
    Spécialiste de la présentation des candidats de code au Superviseur.
    """

    def __init__(self, supervisor_interface):
        """
        Initialise le présentateur.

        Args:
            supervisor_interface: L'interface pour parler au Superviseur.
        """
        self.supervisor = supervisor_interface
        print(
            f"{Colors.OKCYAN}[PRESENTER] - Module de présentation initialisé.{Colors.ENDC}"
        )

    def present_for_final_approval(
        self, snippet_data: Dict, concept_name: str, validation_report: Dict
    ) -> Dict | None:
        """
        Présente un snippet pré-validé au Superviseur pour l'approbation finale.

        Args:
            snippet_data (Dict): Le dictionnaire original du snippet (contenant snippet, url, etc.).
            concept_name (str): Le nom du concept que le code est censé illustrer.
            validation_report (Dict): Le rapport technique du CodeValidator.

        Returns:
            Dict | None: Le snippet_data enrichi si approuvé, sinon None.
        """
        snippet = snippet_data.get("snippet", "")
        source_url = snippet_data.get("url", "Source inconnue")
        quality_score = snippet_data.get("final_score", 0)

        print(f"\n{Colors.HEADER}--- VALIDATION FINALE DU SUPERVISEUR ---{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Concept:{Colors.ENDC} {concept_name}")
        print(f"{Colors.OKBLUE}Source:{Colors.ENDC} {source_url}")

        constructs = validation_report.get("constructs", [])
        if constructs:
            print(
                f"{Colors.OKGREEN}Constructions détectées:{Colors.ENDC} {', '.join(constructs)}"
            )

        print(
            f"{Colors.OKBLUE}Code ({validation_report.get('line_count', 0)} lignes):{Colors.ENDC}"
        )
        self._display_code_snippet(snippet)

        # Analyse pédagogique (peut être déplacée ici si nécessaire)
        # if self._is_educational_code(snippet):
        #     print(f"{Colors.OKGREEN}📚 Code pédagogique détecté{Colors.ENDC}")

        prompt = (
            f"Validez-vous cet exemple pour illustrer '{concept_name}' ?\n"
            f"   (Score qualité: {quality_score}, Constructions: {', '.join(constructs) if constructs else 'basique'})"
        )
        response = self.supervisor.get_authorization(prompt)

        if response == "oui":
            # Enrichir le snippet avec les informations de validation
            enriched_snippet = {
                **snippet_data,
                "validated_by": "Superviseur",
                "validated_at": datetime.now().isoformat(),
                "validation_status": "VALIDÉ",
                "validation_context": {
                    "concept": concept_name,
                    "quality_score": quality_score,
                    "constructs": constructs,
                },
            }
            return enriched_snippet

        # Retourne None si 'non' ou 'quitter'
        return None

    def _display_code_snippet(self, code: str):
        """Affichage amélioré du code avec numérotation."""
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            print(f"{Colors.WARNING}{i:2d}:{Colors.ENDC} {line}")