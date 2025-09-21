"""
Module abstraction et généralisation (Directive 27).
Crée concepts abstraits à partir d'expériences concrètes.
"""

import logging
import time
from typing import Dict, Any, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class ModuleAbstraction:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, modele_monde):
        self.modele_monde = modele_monde
        self.concepts_abstraits = {}
        self.patterns_detectes = []

    def generer_abstraction(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Génère concepts abstraits depuis expériences."""
        if len(experiences) < 3:
            return {}

        patterns = self._detecter_patterns(experiences)
        concept = self._creer_concept_abstrait(patterns)

        if concept:
            id_concept = f"concept_{len(self.concepts_abstraits)}"
            self.concepts_abstraits[id_concept] = concept

            self.modele_monde.graphe_connaissances.ajouter_noeud(
                id_concept,
                {
                    "type_noeud": "Concept",
                    "niveau_abstraction": concept["niveau"],
                    "donnees": concept,
                    "tags": ["abstrait", "generalise"],
                },
            )

        return concept

    def _detecter_patterns(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Détecte patterns récurrents dans expériences."""
        patterns = {
            "sequences_actions": defaultdict(int),
            "conditions_succes": defaultdict(int),
            "contextes_frequents": defaultdict(int),
            "resultats_types": defaultdict(int),
        }

        for exp in experiences:
            if "actions" in exp:
                sequence = tuple(exp["actions"])
                patterns["sequences_actions"][sequence] += 1

            if "succes" in exp and exp["succes"]:
                contexte = exp.get("contexte", {})
                for cle, valeur in contexte.items():
                    patterns["conditions_succes"][f"{cle}:{valeur}"] += 1

            if "resultat" in exp:
                patterns["resultats_types"][exp["resultat"]] += 1

        return patterns

    def _creer_concept_abstrait(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Crée concept abstrait depuis patterns."""
        if not patterns:
            return {}

        sequence_commune = self._extraire_sequence_commune(
            patterns["sequences_actions"]
        )
        conditions_clefs = self._extraire_conditions_clefs(
            patterns["conditions_succes"]
        )

        concept = {
            "timestamp": time.time(),
            "niveau": self._calculer_niveau_abstraction(patterns),
            "sequence_type": sequence_commune,
            "conditions_applicabilite": conditions_clefs,
            "taux_succes_predit": self._predire_taux_succes(patterns),
            "domaines_application": self._identifier_domaines(patterns),
        }

        return concept

    def _extraire_sequence_commune(self, sequences: Dict) -> List[str]:
        """Extrait séquence d'actions la plus commune."""
        if not sequences:
            return []

        sequence_freq = max(sequences.items(), key=lambda x: x[1])
        return list(sequence_freq[0])

    def _extraire_conditions_clefs(self, conditions: Dict) -> List[str]:
        """Extrait conditions clefs pour succès."""
        seuil_frequence = max(1, len(conditions) * 0.3)

        conditions_clefs = [
            condition
            for condition, freq in conditions.items()
            if freq >= seuil_frequence
        ]

        return conditions_clefs

    def _calculer_niveau_abstraction(self, patterns: Dict[str, Any]) -> int:
        """Calcule niveau d'abstraction du concept."""
        nb_patterns = sum(len(p) for p in patterns.values())

        if nb_patterns > 20:
            return 3
        elif nb_patterns > 10:
            return 2
        else:
            return 1

    def _predire_taux_succes(self, patterns: Dict[str, Any]) -> float:
        """Prédit taux de succès du concept."""
        succes_total = sum(patterns["conditions_succes"].values())
        echecs_total = sum(patterns["resultats_types"].values()) - succes_total

        if succes_total + echecs_total == 0:
            return 0.5

        return succes_total / (succes_total + echecs_total)

    def _identifier_domaines(self, patterns: Dict[str, Any]) -> List[str]:
        """Identifie domaines d'application du concept."""
        domaines = set()

        for sequence in patterns["sequences_actions"]:
            for action in sequence:
                if "construire" in action:
                    domaines.add("construction")
                elif "explorer" in action:
                    domaines.add("exploration")
                elif "collecter" in action:
                    domaines.add("ressources")
                elif "combattre" in action:
                    domaines.add("combat")

        return list(domaines)

    def appliquer_concept(
        self, concept_id: str, situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Applique concept abstrait à nouvelle situation."""
        if concept_id not in self.concepts_abstraits:
            return {}

        concept = self.concepts_abstraits[concept_id]

        applicabilite = self._evaluer_applicabilite(concept, situation)

        if applicabilite > 0.6:
            return {
                "concept_applicable": True,
                "actions_suggerees": concept["sequence_type"],
                "confiance": applicabilite,
                "adaptations_requises": self._identifier_adaptations(
                    concept, situation
                ),
            }

        return {"concept_applicable": False}

    def _evaluer_applicabilite(
        self, concept: Dict[str, Any], situation: Dict[str, Any]
    ) -> float:
        """Évalue si concept s'applique à situation."""
        score = 0.0
        conditions = concept.get("conditions_applicabilite", [])

        if not conditions:
            return 0.5

        for condition in conditions:
            if ":" in condition:
                cle, valeur = condition.split(":", 1)
                if cle in situation and str(situation[cle]) == valeur:
                    score += 1.0

        return score / len(conditions)

    def _identifier_adaptations(
        self, concept: Dict[str, Any], situation: Dict[str, Any]
    ) -> List[str]:
        """Identifie adaptations nécessaires pour appliquer concept."""
        adaptations = []

        sequence = concept.get("sequence_type", [])

        for action in sequence:
            if "construire" in action and "materiaux" not in situation:
                adaptations.append("obtenir_materiaux")
            elif "explorer" in action and situation.get("energie", 100) < 50:
                adaptations.append("recuperer_energie")

        return adaptations