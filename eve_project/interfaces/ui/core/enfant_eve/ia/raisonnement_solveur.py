"""
Solveur de problèmes par raisonnement (Directive 1).
Résolution systématique problèmes complexes.
"""

import logging
import time
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SolveurRaisonnement:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, modele_monde):
        self.modele_monde = modele_monde
        self.strategies = {}
        self.historique_solutions = []

    def resoudre_probleme(self, probleme: Dict[str, Any]) -> Dict[str, Any]:
        """Résout problème par analyse systématique."""
        solution = {
            "probleme": probleme,
            "timestamp": time.time(),
            "approche": "",
            "etapes": [],
            "ressources_requises": [],
            "faisabilite": 0.0,
            "duree_estimee": 0,
            "alternatives": [],
        }

        type_probleme = probleme.get("type", "")

        if type_probleme == "acces":
            solution = self._resoudre_acces(probleme, solution)
        elif type_probleme == "ressource":
            solution = self._resoudre_ressource(probleme, solution)
        elif type_probleme == "construction":
            solution = self._resoudre_construction(probleme, solution)
        elif type_probleme == "survie":
            solution = self._resoudre_survie(probleme, solution)
        else:
            solution = self._resoudre_generique(probleme, solution)

        self._enregistrer_solution(solution)
        return solution

    def _resoudre_acces(
        self, probleme: Dict[str, Any], solution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Résout problèmes d'accès terrain."""
        destination = probleme.get("destination", {})
        obstacles = probleme.get("obstacles", [])

        solution["approche"] = "contournement_adaptatif"
        solution["etapes"] = [
            "analyser_terrain",
            "identifier_obstacles",
            "evaluer_alternatives",
            "choisir_route_optimale",
        ]

        if len(obstacles) > 5:
            solution["alternatives"] = ["tunnel", "pont", "contournement"]
            solution["faisabilite"] = 0.6
        else:
            solution["alternatives"] = ["contournement", "degagement"]
            solution["faisabilite"] = 0.8

        solution["duree_estimee"] = len(obstacles) * 60
        return solution

    def _resoudre_ressource(
        self, probleme: Dict[str, Any], solution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Résout problèmes de ressources."""
        ressource_cible = probleme.get("ressource", "")
        quantite_requise = probleme.get("quantite", 1)

        solution["approche"] = "acquisition_optimisee"
        solution["etapes"] = [
            "localiser_sources",
            "evaluer_accessibilite",
            "planifier_collecte",
            "optimiser_transport",
        ]

        sources_connues = self._rechercher_sources_ressource(ressource_cible)

        if len(sources_connues) >= 2:
            solution["faisabilite"] = 0.9
            solution["duree_estimee"] = quantite_requise * 30
        else:
            solution["faisabilite"] = 0.5
            solution["duree_estimee"] = quantite_requise * 90
            solution["alternatives"] = ["exploration_etendue", "substitution"]

        return solution

    def _resoudre_construction(
        self, probleme: Dict[str, Any], solution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Résout problèmes de construction."""
        projet = probleme.get("projet", {})
        contraintes = probleme.get("contraintes", [])

        solution["approche"] = "construction_planifiee"
        solution["etapes"] = [
            "analyser_site",
            "calculer_materiaux",
            "planifier_sequence",
            "executer_construction",
        ]

        complexite = len(contraintes) + projet.get("taille", 1)

        if complexite < 5:
            solution["faisabilite"] = 0.9
            solution["duree_estimee"] = complexite * 120
        else:
            solution["faisabilite"] = 0.6
            solution["duree_estimee"] = complexite * 180
            solution["alternatives"] = ["construction_modulaire", "simplification"]

        return solution

    def _resoudre_survie(
        self, probleme: Dict[str, Any], solution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Résout problèmes de survie urgents."""
        menace = probleme.get("menace", {})
        urgence = probleme.get("urgence", 0.5)

        solution["approche"] = "survie_adaptative"

        if urgence > 0.8:
            solution["etapes"] = ["action_immediate", "securisation", "stabilisation"]
            solution["faisabilite"] = 0.7
        else:
            solution["etapes"] = [
                "evaluation",
                "preparation",
                "action",
                "consolidation",
            ]
            solution["faisabilite"] = 0.9

        solution["duree_estimee"] = int(300 / (urgence + 0.1))
        solution["alternatives"] = ["fuite", "confrontation", "camouflage"]

        return solution

    def _resoudre_generique(
        self, probleme: Dict[str, Any], solution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Résout problèmes génériques."""
        solution["approche"] = "analyse_systematique"
        solution["etapes"] = [
            "decomposer_probleme",
            "identifier_contraintes",
            "generer_options",
            "evaluer_solutions",
        ]
        solution["faisabilite"] = 0.5
        solution["duree_estimee"] = 600

        return solution

    def _rechercher_sources_ressource(self, ressource: str) -> List[Dict[str, Any]]:
        """Recherche sources connues d'une ressource."""
        sources = []

        if hasattr(self.modele_monde, "graphe_connaissances"):
            graphe = self.modele_monde.graphe_connaissances

            for noeud_data in graphe.noeuds.values():
                donnees = noeud_data.get("donnees", {})
                if ressource in donnees.get("ressources", []):
                    sources.append(donnees)

        return sources

    def _enregistrer_solution(self, solution: Dict[str, Any]) -> None:
        """Enregistre solution dans historique."""
        self.historique_solutions.append(solution)

        if len(self.historique_solutions) > 200:
            self.historique_solutions = self.historique_solutions[-150:]

    def evaluer_efficacite_solutions(self) -> Dict[str, Any]:
        """Évalue efficacité des solutions passées."""
        if not self.historique_solutions:
            return {"efficacite_globale": 0.0}

        solutions_reussies = []
        for sol in self.historique_solutions:
            if sol.get("succes", True) is not False:
                solutions_reussies.append(sol)

        taux_succes = len(solutions_reussies) / len(self.historique_solutions)

        return {
            "efficacite_globale": taux_succes,
            "solutions_total": len(self.historique_solutions),
            "solutions_reussies": len(solutions_reussies),
            "approches_preferees": self._analyser_approches_preferees(),
        }

    def _analyser_approches_preferees(self) -> List[str]:
        """Analyse les approches les plus utilisées."""
        approches = {}

        for solution in self.historique_solutions:
            approche = solution.get("approche", "inconnue")
            approches[approche] = approches.get(approche, 0) + 1

        approches_triees = sorted(approches.items(), key=lambda x: x[1], reverse=True)
        return [approche for approche, count in approches_triees[:3]]

    def optimiser_strategie(self, feedback: Dict[str, Any]) -> None:
        """Optimise stratégies selon feedback."""
        try:
            type_probleme = feedback.get("type_probleme", "")
            succes = feedback.get("succes", False)
            duree_reelle = feedback.get("duree_reelle", 0)

            if type_probleme in self.strategies:
                strategie = self.strategies[type_probleme]

                if succes:
                    strategie["taux_succes"] = strategie.get("taux_succes", 0.5) * 1.1
                else:
                    strategie["taux_succes"] = strategie.get("taux_succes", 0.5) * 0.9

                strategie["duree_moyenne"] = (
                    strategie.get("duree_moyenne", duree_reelle) + duree_reelle
                ) / 2
            else:
                self.strategies[type_probleme] = {
                    "taux_succes": 0.7 if succes else 0.3,
                    "duree_moyenne": duree_reelle,
                    "utilisations": 1,
                }

        except Exception as e:
            logger.error(f"Erreur optimisation stratégie: {e}")