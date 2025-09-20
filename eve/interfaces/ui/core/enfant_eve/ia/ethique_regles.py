import time
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RegleEthique:
    """
    Représente une règle éthique éco-bâtisseuse.
    Implémente la Directive 13 (Éthique éco-bâtisseuse).
    """

    nom: str
    description: str
    priorite: int
    pattern_violation: str
    correction_suggeree: str
    severite: int

    def __post_init__(self):
        """TODO: Add docstring."""
        self.violations = 0
        self.derniere_verification = time.time()
        self.actif = True

    def incrementer_violations(self):
        """Incrémente le compteur de violations."""
        self.violations += 1
        self.derniere_verification = time.time()

    def est_applicable(self, plan: Dict) -> bool:
        """Vérifie si la règle s'applique au plan donné."""
        type_plan = plan.get("type", "inconnu")

        if self.nom == "preservation_nature" and type_plan in [
            "construction",
            "exploitation",
        ]:
            return True
        elif self.nom == "anti_gaspillage" and "ressources" in plan:
            return True
        elif self.nom == "durabilite_construction" and type_plan == "construction":
            return True
        elif self.nom == "respect_biomes" and "position" in plan:
            return True
        elif self.nom == "equilibre_ecosysteme" and type_plan == "exploitation":
            return True
        elif self.nom == "recherche_ethique" and type_plan == "recherche":
            return True
        elif self.nom == "exploitation_moderee":
            return True

        return False


def creer_regles_eco_batisseuse() -> List[RegleEthique]:
    """
    Crée les 7 règles éthiques fondamentales de l'éco-bâtisseuse.
    Conforme aux Directives D48 et D52.
    """
    return [
        RegleEthique(
            nom="preservation_nature",
            description="Préserver la beauté naturelle et éviter la destruction massive",
            priorite=1,
            pattern_violation="destruction_massive|deforestation|pollution",
            correction_suggeree="construction_harmonieuse",
            severite=2,
        ),
        RegleEthique(
            nom="anti_gaspillage",
            description="Éviter le gaspillage de ressources et optimiser l'utilisation",
            priorite=2,
            pattern_violation="gaspillage|surplus_inutile|stockage_excessif",
            correction_suggeree="optimisation_ressources",
            severite=3,
        ),
        RegleEthique(
            nom="durabilite_construction",
            description="Privilégier des constructions durables et fonctionnelles",
            priorite=2,
            pattern_violation="materiaux_fragiles|construction_temporaire",
            correction_suggeree="materiaux_durables",
            severite=3,
        ),
        RegleEthique(
            nom="respect_biomes",
            description="Respecter les caractéristiques uniques de chaque biome",
            priorite=3,
            pattern_violation="inadaptation_biome|ignorance_environnement",
            correction_suggeree="adaptation_locale",
            severite=4,
        ),
        RegleEthique(
            nom="equilibre_ecosysteme",
            description="Maintenir l'équilibre des écosystèmes locaux",
            priorite=2,
            pattern_violation="desequilibre|surexploitation|extinction",
            correction_suggeree="exploitation_durable",
            severite=2,
        ),
        RegleEthique(
            nom="recherche_ethique",
            description="Mener des recherches éthiques sans exploitation",
            priorite=1,
            pattern_violation="exploit_potentiel|experimentation_destructive",
            correction_suggeree="observation_controlee",
            severite=1,
        ),
        RegleEthique(
            nom="exploitation_moderee",
            description="Limiter l'exploitation aux besoins réels",
            priorite=3,
            pattern_violation="surexploitation|extraction_massive",
            correction_suggeree="extraction_mesuree",
            severite=4,
        ),
    ]


def obtenir_regle_par_nom(regles: List[RegleEthique], nom_regle: str) -> RegleEthique:
    """Retourne une règle par son nom."""
    for regle in regles:
        if regle.nom == nom_regle:
            return regle
    return None


def calculer_score_global_regles(regles: List[RegleEthique]) -> float:
    """Calcule un score global basé sur les violations des règles."""
    if not regles:
        return 1.0

    score_total = 0.0
    poids_total = 0.0

    for regle in regles:
        if regle.actif:
            poids = 6 - regle.priorite
            penalite = min(regle.violations * 0.1, 0.5)
            score_regle = max(0.0, 1.0 - penalite)

            score_total += score_regle * poids
            poids_total += poids

    return score_total / poids_total if poids_total > 0 else 1.0