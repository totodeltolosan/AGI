"""
Module raisonnement principal (Directive 1).
Logique, analyse et résolution de problèmes.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ModuleRaisonnement:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, modele_monde):
        self.modele_monde = modele_monde
        self.regles_logiques = []
        self.historique_raisonnements = []

    def analyser_situation(self, contexte: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse situation et génère conclusions."""
        analyse = {
            "contexte": contexte,
            "faits_extraits": [],
            "regles_appliquees": [],
            "conclusions": [],
            "certitude": 0.0,
        }

        analyse["faits_extraits"] = self._extraire_faits(contexte)
        analyse["regles_appliquees"] = self._appliquer_regles(analyse["faits_extraits"])
        analyse["conclusions"] = self._generer_conclusions(analyse["regles_appliquees"])
        analyse["certitude"] = self._calculer_certitude(analyse)

        self.historique_raisonnements.append(analyse)
        return analyse

    def _extraire_faits(self, contexte: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait faits observables du contexte."""
        faits = []

        if "etat_joueur" in contexte:
            joueur = contexte["etat_joueur"]

            if joueur.get("vie", 100) < 50:
                faits.append({"type": "vie_faible", "valeur": joueur["vie"]})

            if joueur.get("faim", 100) < 30:
                faits.append({"type": "faim_elevee", "valeur": joueur["faim"]})

        if "entites_proches" in contexte:
            for entite in contexte["entites_proches"]:
                if "hostile" in entite.get("type", ""):
                    faits.append({"type": "danger_present", "entite": entite})
                elif "nourriture" in entite.get("tags", []):
                    faits.append({"type": "nourriture_disponible", "entite": entite})

        return faits

    def _appliquer_regles(self, faits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applique règles logiques aux faits."""
        regles_activees = []

        for fait in faits:
            if fait["type"] == "vie_faible":
                regles_activees.append(
                    {
                        "regle": "priorite_survie",
                        "condition": fait,
                        "conclusion": "action_urgente_requise",
                    }
                )

            elif fait["type"] == "danger_present":
                regles_activees.append(
                    {
                        "regle": "evitement_danger",
                        "condition": fait,
                        "conclusion": "fuir_ou_combattre",
                    }
                )

            elif fait["type"] == "faim_elevee" and fait["valeur"] < 10:
                regles_activees.append(
                    {
                        "regle": "survie_alimentaire",
                        "condition": fait,
                        "conclusion": "chercher_nourriture_urgent",
                    }
                )

        return regles_activees

    def _generer_conclusions(self, regles: List[Dict[str, Any]]) -> List[str]:
        """Génère conclusions finales."""
        conclusions = []
        priorites = []

        for regle in regles:
            conclusion = regle["conclusion"]

            if "urgent" in conclusion:
                priorites.append(("URGENT", conclusion))
            elif "danger" in conclusion:
                priorites.append(("DANGER", conclusion))
            else:
                priorites.append(("NORMAL", conclusion))

        priorites.sort(key=lambda x: {"URGENT": 0, "DANGER": 1, "NORMAL": 2}[x[0]])
        conclusions = [p[1] for p in priorites]

        return conclusions

    def _calculer_certitude(self, analyse: Dict[str, Any]) -> float:
        """Calcule niveau de certitude de l'analyse."""
        nb_faits = len(analyse["faits_extraits"])
        nb_regles = len(analyse["regles_appliquees"])

        if nb_faits == 0:
            return 0.1

        certitude_base = min(nb_regles / nb_faits, 1.0)

        for regle in analyse["regles_appliquees"]:
            if regle["regle"] in ["priorite_survie", "evitement_danger"]:
                certitude_base += 0.2

        return min(certitude_base, 1.0)

    def resoudre_probleme(
        self, probleme: str, contraintes: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Résout problème avec contraintes données."""
        solution = {
            "probleme": probleme,
            "contraintes": contraintes,
            "approche": "",
            "etapes": [],
            "faisabilite": 0.0,
        }

        if "chemin" in probleme.lower():
            solution = self._resoudre_chemin(solution)
        elif "ressource" in probleme.lower():
            solution = self._resoudre_ressource(solution)
        elif "construction" in probleme.lower():
            solution = self._resoudre_construction(solution)
        else:
            solution["approche"] = "analyse_generale"
            solution["etapes"] = ["analyser", "planifier", "executer"]
            solution["faisabilite"] = 0.5

        return solution

    def _resoudre_chemin(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Résout problèmes de cheminement."""
        solution["approche"] = "pathfinding"
        solution["etapes"] = [
            "analyser_terrain",
            "calculer_route_optimale",
            "verifier_obstacles",
            "executer_deplacement",
        ]
        solution["faisabilite"] = 0.8
        return solution

    def _resoudre_ressource(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Résout problèmes de ressources."""
        solution["approche"] = "optimisation_ressources"
        solution["etapes"] = [
            "evaluer_besoins",
            "localiser_sources",
            "planifier_collecte",
            "optimiser_stockage",
        ]
        solution["faisabilite"] = 0.7
        return solution

    def _resoudre_construction(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Résout problèmes de construction."""
        solution["approche"] = "planification_construction"
        solution["etapes"] = [
            "analyser_site",
            "calculer_materiaux",
            "planifier_sequence",
            "executer_construction",
        ]
        solution["faisabilite"] = 0.6
        return solution