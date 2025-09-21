"""
Planificateur principal IA (Directive 7).
Génère et exécute plans d'action hiérarchiques.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from enfant_eve.ia.planificateur_besoins import PlanificateurBesoins
from enfant_eve.ia.planificateur_actions import PlanificateurActions

logger = logging.getLogger(__name__)


class Planificateur:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, modele_monde, config):
        self.modele_monde = modele_monde
        self.config = config

        self.plan_actuel = None
        self.pile_objectifs = []
        self.historique_plans = []

        self.planificateur_besoins = PlanificateurBesoins(config)
        self.planificateur_actions = PlanificateurActions(modele_monde)

    def generer_plan(self, objectif_principal: str) -> Optional[Dict[str, Any]]:
        """Génère plan pour objectif donné."""
        try:
            besoins = self.planificateur_besoins.analyser_besoins(objectif_principal)

            plan = {
                "objectif": objectif_principal,
                "timestamp": time.time(),
                "besoins": besoins,
                "actions": [],
                "priorite": self._calculer_priorite(objectif_principal),
                "estimation_duree": 0,
            }

            actions = self.planificateur_actions.generer_sequence(besoins)
            plan["actions"] = actions
            plan["estimation_duree"] = sum(a.get("duree_estimee", 60) for a in actions)

            self.plan_actuel = plan
            self.historique_plans.append(plan)

            logger.info(f"Plan généré: {objectif_principal} ({len(actions)} actions)")
            return plan

        except Exception as e:
            logger.error(f"Erreur génération plan: {e}")
            return None

    def obtenir_prochaine_action(self) -> Optional[Dict[str, Any]]:
        """Obtient prochaine action du plan actuel."""
        if not self.plan_actuel or not self.plan_actuel.get("actions"):
            return None

        return self.plan_actuel["actions"].pop(0)

    def ajuster_plan(self, contexte_echec: Dict[str, Any]):
        """Ajuste plan en cas d'échec."""
        if not self.plan_actuel:
            return

        logger.warning(f"Ajustement plan requis: {contexte_echec}")

        self.plan_actuel["echecs"] = self.plan_actuel.get("echecs", [])
        self.plan_actuel["echecs"].append(
            {"timestamp": time.time(), "contexte": contexte_echec}
        )

        if len(self.plan_actuel["echecs"]) >= 3:
            logger.error("Plan abandonné après 3 échecs")
            self.plan_actuel = None

    def evaluer_progres(self) -> float:
        """Évalue progrès du plan actuel."""
        if not self.plan_actuel:
            return 0.0

        actions_totales = len(self.plan_actuel.get("actions_originales", []))
        actions_restantes = len(self.plan_actuel.get("actions", []))

        if actions_totales == 0:
            return 1.0

        return 1.0 - (actions_restantes / actions_totales)

    def _calculer_priorite(self, objectif: str) -> int:
        """Calcule priorité d'un objectif."""
        priorites = {
            "survie": 100,
            "securite": 80,
            "nourriture": 70,
            "abri": 60,
            "exploration": 40,
            "construction": 30,
            "optimisation": 20,
        }

        for cle, priorite in priorites.items():
            if cle in objectif.lower():
                return priorite

        return 50

    def planifier_cycle_adaptation(self, duree_cycle: int):
        """Planifie adaptation aux cycles environnementaux."""
        cycle_plan = {
            "type": "cycle_adaptation",
            "duree": duree_cycle,
            "phases": [
                {"nom": "preparation", "duree": duree_cycle * 0.2},
                {"nom": "execution", "duree": duree_cycle * 0.6},
                {"nom": "consolidation", "duree": duree_cycle * 0.2},
            ],
        }

        return cycle_plan