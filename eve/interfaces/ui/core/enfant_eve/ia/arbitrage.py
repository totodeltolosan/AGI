"""
Module arbitrage et résolution conflits (Directive 16).
Gère conflits entre modules et priorise décisions.
"""

import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ModuleArbitrage:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, config_arbitrage):
        self.config = config_arbitrage
        self.regles_priorite = self._initialiser_regles()
        self.conflits_resolus = []

    def _initialiser_regles(self) -> Dict[str, int]:
        """Initialise règles de priorité entre modules."""
        return {
            "survie": 100,
            "ethique": 90,
            "securite": 80,
            "planification": 70,
            "apprentissage": 60,
            "creativite": 50,
            "optimisation": 40,
        }

    def arbitrer_conflit(
        self, decisions_concurrentes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Arbitre entre décisions concurrentes."""
        if len(decisions_concurrentes) <= 1:
            return decisions_concurrentes[0] if decisions_concurrentes else {}

        conflit = {
            "timestamp": time.time(),
            "decisions": decisions_concurrentes,
            "decision_finale": {},
            "justification": "",
            "modules_impliques": [],
        }

        decision_choisie = self._resoudre_par_priorite(decisions_concurrentes)
        conflit["decision_finale"] = decision_choisie
        conflit["justification"] = self._generer_justification(
            decision_choisie, decisions_concurrentes
        )
        conflit["modules_impliques"] = [
            d.get("module_source", "") for d in decisions_concurrentes
        ]

        self.conflits_resolus.append(conflit)
        return conflit

    def _resoudre_par_priorite(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Résout conflit selon priorités des modules."""
        decisions_avec_score = []

        for decision in decisions:
            module_source = decision.get("module_source", "")
            urgence = decision.get("urgence", 0.5)
            impact = decision.get("impact", 0.5)

            priorite_module = self.regles_priorite.get(module_source, 30)
            score_total = priorite_module + (urgence * 20) + (impact * 10)

            decisions_avec_score.append((score_total, decision))

        decisions_avec_score.sort(key=lambda x: x[0], reverse=True)
        return decisions_avec_score[0][1]

    def _generer_justification(
        self, decision_choisie: Dict[str, Any], toutes_decisions: List[Dict[str, Any]]
    ) -> str:
        """Génère justification pour choix de décision."""
        module_gagnant = decision_choisie.get("module_source", "inconnu")
        urgence = decision_choisie.get("urgence", 0.0)

        if urgence > 0.8:
            return f"Décision {module_gagnant} choisie pour urgence critique"
        elif module_gagnant in ["survie", "ethique"]:
            return f"Décision {module_gagnant} choisie pour priorité fondamentale"
        else:
            return f"Décision {module_gagnant} choisie selon règles de priorité"

    def evaluer_coherence_globale(self, plan_global: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue cohérence du plan global."""
        evaluation = {
            "score_coherence": 0.0,
            "conflits_detectes": [],
            "recommandations": [],
            "actions_incompatibles": [],
        }

        actions = plan_global.get("actions", [])

        for i, action1 in enumerate(actions):
            for j, action2 in enumerate(actions[i + 1 :], i + 1):
                conflit = self._detecter_conflit_actions(action1, action2)
                if conflit:
                    evaluation["conflits_detectes"].append(
                        {
                            "action1": action1,
                            "action2": action2,
                            "type_conflit": conflit,
                        }
                    )

        evaluation["score_coherence"] = self._calculer_score_coherence(evaluation)
        evaluation["recommandations"] = self._generer_recommandations(evaluation)

        return evaluation

    def _detecter_conflit_actions(
        self, action1: Dict[str, Any], action2: Dict[str, Any]
    ) -> str:
        """Détecte conflits entre deux actions."""
        type1 = action1.get("type", "")
        type2 = action2.get("type", "")

        if type1 == "construire" and type2 == "detruire":
            if action1.get("position") == action2.get("position"):
                return "construction_destruction_meme_lieu"

        elif type1 == "explorer" and type2 == "construire":
            if action1.get("zone") == action2.get("zone"):
                return "exploration_construction_concurrent"

        elif type1 == "collecter" and type2 == "collecter":
            if action1.get("ressource") == action2.get("ressource"):
                return "double_collecte_meme_ressource"

        return ""

    def _calculer_score_coherence(self, evaluation: Dict[str, Any]) -> float:
        """Calcule score de cohérence globale."""
        nb_conflits = len(evaluation["conflits_detectes"])

        if nb_conflits == 0:
            return 1.0
        elif nb_conflits <= 2:
            return 0.7
        elif nb_conflits <= 5:
            return 0.4
        else:
            return 0.1

    def _generer_recommandations(self, evaluation: Dict[str, Any]) -> List[str]:
        """Génère recommandations pour améliorer cohérence."""
        recommandations = []

        for conflit in evaluation["conflits_detectes"]:
            type_conflit = conflit["type_conflit"]

            if "meme_lieu" in type_conflit:
                recommandations.append("Espacer actions géographiquement")
            elif "concurrent" in type_conflit:
                recommandations.append("Séquencer actions temporellement")
            elif "double" in type_conflit:
                recommandations.append("Éliminer actions redondantes")

        if evaluation["score_coherence"] < 0.5:
            recommandations.append("Révision majeure du plan requise")

        return list(set(recommandations))

    def prioriser_urgences(
        self, taches_urgentes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Priorise tâches selon urgence et importance."""
        taches_avec_score = []

        for tache in taches_urgentes:
            urgence = tache.get("urgence", 0.5)
            importance = tache.get("importance", 0.5)
            difficulte = tache.get("difficulte", 0.5)

            score = (urgence * 0.4) + (importance * 0.4) + ((1.0 - difficulte) * 0.2)
            taches_avec_score.append((score, tache))

        taches_avec_score.sort(key=lambda x: x[0], reverse=True)
        return [tache for score, tache in taches_avec_score]