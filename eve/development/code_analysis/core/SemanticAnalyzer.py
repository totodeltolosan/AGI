"""
PROJET PROMETHEUS - MODULE SPÉCIALISÉ SEMANTICANALYZER (V1.0)

Mission: Agir comme un expert de l'analyse sémantique. Ce module est le
"cerveau interprétatif" qui identifie les concepts de programmation
pertinents à partir d'une analyse textuelle.

Responsabilités:
- Charger la carte des concepts de code.
- Recevoir une analyse (titre, mots-clés, etc.) d'une page.
- Appliquer une logique de scoring pour déterminer les concepts les plus probables.
- Retourner une liste classée des concepts identifiés.
"""

from typing import List, Dict


# --- CLASSE DE COULEURS PARTAGÉE ---
class Colors:
    OKCYAN = "\033[96m"
    MAGENTA = "\033[95m"
    ENDC = "\033[0m"


class SemanticAnalyzer:
    """
    Spécialiste de l'identification de concepts programmables dans une analyse textuelle.
    """

    def __init__(self, local_reader):
        """
        Initialise l'analyseur sémantique.

        Args:
            local_reader: L'instance du LocalReader pour accéder à la carte des concepts.
        """
        self.local_reader = local_reader
        self.concepts_map = self.local_reader.concepts_map
        print(
            f"{Colors.OKCYAN}[SEMANTIC-ANALYZER] - Module d'analyse sémantique initialisé.{Colors.ENDC}"
        )
        print(
            f"{Colors.OKCYAN}[SEMANTIC-ANALYZER] - {len(self.concepts_map)} concepts connus.{Colors.ENDC}"
        )

    def identify_concepts_from_analysis(
        self, analysis: Dict, max_concepts: int = 5
    ) -> List[str]:
        """
        Méthode principale. Identifie les concepts à partir d'une analyse structurée.
        C'est la logique déplacée depuis l'ancien CodeHunter.
        """
        concept_scores = {}

        # Récupération des données d'analyse
        title = analysis.get("title", "").lower()
        keywords = analysis.get("keywords", [])
        definitions = analysis.get("definitions", {})

        # Itération sur chaque concept connu de notre carte
        for concept_data in self.concepts_map:
            concept_name = concept_data.get("name")
            if not concept_name:
                continue

            current_score = 0

            # 1. Analyse du titre (poids le plus élevé)
            if concept_name in title:
                current_score += 15

            # 2. Analyse des mots-clés
            for keyword in keywords:
                if keyword.lower() == concept_name:
                    current_score += 10  # Correspondance exacte
                elif concept_name in keyword.lower():
                    current_score += 5  # Correspondance partielle

            # 3. Analyse des définitions
            for def_key, def_value in definitions.items():
                def_text = f"{def_key} {def_value}".lower()
                if concept_name in def_text:
                    current_score += 8

            if current_score > 0:
                concept_scores[concept_name] = current_score

        # Tri par score pour obtenir les concepts les plus pertinents
        sorted_concepts = sorted(
            concept_scores.items(), key=lambda item: item[1], reverse=True
        )

        # Extrait uniquement les noms des concepts
        final_concepts = [concept for concept, score in sorted_concepts]

        if final_concepts:
            print(
                f"{Colors.MAGENTA}[SEMANTIC-ANALYZER] - 🎯 Concepts identifiés avec scoring: {', '.join(final_concepts[:max_concepts])}{Colors.ENDC}"
            )

        return final_concepts[:max_concepts]
