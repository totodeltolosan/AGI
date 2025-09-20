import random
import logging
from typing import Dict, List, Any, Optional
from enum import Enum

from .creativite_generateurs import GenerateurStructures

logger = logging.getLogger(__name__)


class PhaseVie(Enum):
    """Énumération des phases de vie de l'IA."""

    ENFANCE = "ENFANCE"
    ADOLESCENCE = "ADOLESCENCE"
    ADULTE = "ADULTE"
    MAITRISE = "MAITRISE"


class StyleArchitectural(Enum):
    """Énumération des styles architecturaux disponibles."""

    FONCTIONNEL = "fonctionnel"
    EXPERIMENTALE = "experimentale"
    HARMONIEUX = "harmonieux"
    ARTISTIQUE = "artistique"
    MONUMENTALE = "monumentale"


class GestionnaireStyles:
    """
    Gestionnaire des styles architecturaux selon les phases de vie.
    Respecte Directive 61 avec séparation claire des responsabilités.
    """

    def __init__(self):
        """TODO: Add docstring."""
        self.generateur = GenerateurStructures()
        self.styles_phase = {
            PhaseVie.ENFANCE.value: self._style_enfance,
            PhaseVie.ADOLESCENCE.value: self._style_adolescence,
            PhaseVie.ADULTE.value: self._style_adulte,
            PhaseVie.MAITRISE.value: self._style_maitrise,
        }

    def appliquer_style_phase(self, plan_base: Dict, phase_de_vie: str) -> Dict:
        """Applique le style correspondant à la phase de vie."""
        try:
            style_handler = self.styles_phase.get(phase_de_vie)
            if not style_handler:
                logger.warning(f"Phase inconnue {phase_de_vie}, utilisation ENFANCE")
                style_handler = self.styles_phase[PhaseVie.ENFANCE.value]

            return style_handler(plan_base)

        except Exception as e:
            logger.error(f"Erreur application style {phase_de_vie}: {e}")
            return self._style_enfance(plan_base)

    def _style_enfance(self, plan_base: Dict) -> Dict:
        """Style enfance : symétrie parfaite et simplicité."""
        try:
            plan = plan_base.copy()

            # Forcer dimensions paires pour symétrie
            dimensions = plan.get("dimensions", [8, 4, 8])
            plan["dimensions"] = [
                dimensions[0] + (dimensions[0] % 2),
                max(2, dimensions[1]),
                dimensions[2] + (dimensions[2] % 2),
            ]

            # Matériaux de base uniquement
            plan["materiaux_autorises"] = ["wood", "stone", "dirt", "cobblestone"]
            plan["materiaux_interdits"] = [
                "diamond_block",
                "emerald_block",
                "gold_block",
            ]

            # Caractéristiques enfance
            plan["forme"] = "rectangulaire"
            plan["style"] = StyleArchitectural.FONCTIONNEL.value
            plan["decorations"] = "minimales"
            plan["complexite_max"] = 3
            plan["symetrie_parfaite"] = True

            # Génération structure avec symétrie
            plan["blocs_generes"] = self.generateur.generer_structure_symetrique(plan)
            plan["score_complexite"] = self._calculer_score_complexite_enfance(plan)

            return plan

        except Exception as e:
            logger.error(f"Erreur style enfance: {e}")
            return plan_base

    def _style_adolescence(self, plan_base: Dict) -> Dict:
        """Style adolescence : expérimentation et variété."""
        try:
            plan = plan_base.copy()

            # Élargissement palette matériaux
            plan["materiaux_autorises"] = [
                "wood",
                "stone",
                "brick",
                "glass",
                "wool",
                "iron_block",
                "clay",
                "sandstone",
                "mossy_cobblestone",
                "planks",
            ]

            # Formes expérimentales
            formes_experimentales = [
                "rectangulaire",
                "L_shape",
                "T_shape",
                "croix",
                "circulaire_approx",
                "zigzag",
                "spirale_simple",
                "asymetrique",
            ]
            plan["forme"] = random.choice(formes_experimentales)
            plan["style"] = StyleArchitectural.EXPERIMENTALE.value

            # Caractéristiques adolescence
            plan["decorations"] = "moderees_colorees"
            plan["complexite_max"] = 6
            plan["variation_hauteurs"] = True
            plan["experimentation_active"] = True
            plan["couleurs_vives"] = True
            plan["tolerance_imperfection"] = 0.3

            # Génération structure variée
            plan["blocs_generes"] = self.generateur.generer_structure_variee(plan)
            plan["score_creativite"] = self._calculer_score_creativite_adolescence(plan)

            return plan

        except Exception as e:
            logger.error(f"Erreur style adolescence: {e}")
            return plan_base

    def _style_adulte(self, plan_base: Dict) -> Dict:
        """Style adulte : harmonie parfaite avec l'environnement."""
        try:
            plan = plan_base.copy()

            # Adaptation à l'environnement
            environnement = plan_base.get("contexte_environnemental", {})
            if environnement:
                plan = self._adapter_environnement_intelligent(plan, environnement)

            # Palette matériaux raffinée
            plan["materiaux_autorises"] = [
                "wood",
                "stone",
                "brick",
                "glass",
                "quartz",
                "prismarine",
                "emerald_block",
                "lapis_block",
                "obsidian",
                "purpur_block",
                "sea_lantern",
                "end_stone",
                "nether_brick",
            ]

            # Caractéristiques de maturité
            plan["forme"] = "organique_complexe"
            plan["style"] = StyleArchitectural.HARMONIEUX.value
            plan["decorations"] = "sophistiquees"
            plan["complexite_max"] = 10
            plan["integration_paysage"] = True
            plan["innovations_technologiques"] = True
            plan["durabilite_environnementale"] = True

            # Génération harmonieuse
            plan["blocs_generes"] = self.generateur.generer_structure_harmonieuse(plan)
            plan["score_harmonie"] = self._calculer_score_harmonie_adulte(plan)

            return plan

        except Exception as e:
            logger.error(f"Erreur style adulte: {e}")
            return plan_base

    def _style_maitrise(self, plan_base: Dict) -> Dict:
        """Style maîtrise : œuvres monumentales et innovations majeures."""
        # Hérite du style adulte avec améliorations monumentales
        plan = self._style_adulte(plan_base)

        # Améliorations spécifiques maîtrise
        plan["style"] = StyleArchitectural.MONUMENTALE.value
        plan["complexite_max"] = 15
        plan["innovations_majeures"] = True
        plan["heritage_artistique"] = True

        return plan

    def _adapter_environnement_intelligent(
        self, plan: Dict, environnement: Dict
    ) -> Dict:
        """Adaptation intelligente selon l'environnement."""
        try:
            biome = environnement.get("biome", "tempéré")

            # Adaptations selon biome
            adaptations_biome = {
                "desert": {
                    "materiaux_adaptes": ["sandstone", "brick", "terracotta", "glass"],
                    "architecture_type": "ventilation_naturelle",
                },
                "forest": {
                    "materiaux_adaptes": ["wood", "leaves", "moss_stone", "glass"],
                    "architecture_type": "integration_arbres",
                },
                "mountain": {
                    "materiaux_adaptes": ["stone", "andesite", "iron_block", "snow"],
                    "architecture_type": "resistance_alpine",
                },
                "ocean": {
                    "materiaux_adaptes": [
                        "prismarine",
                        "sea_lantern",
                        "glass",
                        "quartz",
                    ],
                    "architecture_type": "amphibie",
                },
            }

            adaptation = adaptations_biome.get(biome, adaptations_biome["forest"])
            plan.update(adaptation)

            return plan

        except Exception as e:
            logger.error(f"Erreur adaptation environnement: {e}")
            return plan

    def ameliorer_originalite(self, plan: Dict, phase_de_vie: str) -> Dict:
        """Améliore l'originalité d'un plan selon la phase de vie."""
        try:
            ameliorations = {
                "ENFANCE": self._ameliorer_originalite_enfance,
                "ADOLESCENCE": self._ameliorer_originalite_adolescence,
                "ADULTE": self._ameliorer_originalite_adulte,
                "MAITRISE": self._ameliorer_originalite_maitrise,
            }

            amelioration_func = ameliorations.get(
                phase_de_vie, self._ameliorer_originalite_enfance
            )
            return amelioration_func(plan)

        except Exception as e:
            logger.error(f"Erreur amélioration originalité: {e}")
            return plan

    def _ameliorer_originalite_enfance(self, plan: Dict) -> Dict:
        """Améliorations simples pour phase enfance."""
        if "materiaux_autorises" in plan:
            plan["materiaux_autorises"].append("wool_red")
        plan["elements_decoratifs"] = [{"type": "drapeau_simple", "couleur": "rouge"}]
        return plan

    def _ameliorer_originalite_adolescence(self, plan: Dict) -> Dict:
        """Améliorations expérimentales pour phase adolescence."""
        variations = [
            {"type": "tour_observation", "hauteur_bonus": random.randint(2, 5)},
            {"type": "pont_connexion", "longueur": random.randint(3, 8)},
            {"type": "jardin_suspendu", "niveau": random.randint(1, 3)},
        ]
        plan["elements_decoratifs"] = random.sample(variations, random.randint(1, 2))
        return plan

    def _ameliorer_originalite_adulte(self, plan: Dict) -> Dict:
        """Améliorations harmonieuses pour phase adulte."""
        innovations = [
            {"type": "jardin_zen", "style": "japonais"},
            {"type": "fontaine_centrale", "animation": "eau_courante"},
            {"type": "observatoire_astronomique", "equipement": ["telescope"]},
        ]
        plan["innovations_architecturales"] = random.sample(innovations, 1)
        return plan

    def _ameliorer_originalite_maitrise(self, plan: Dict) -> Dict:
        """Améliorations monumentales pour phase maîtrise."""
        plan = self._ameliorer_originalite_adulte(plan)
        elements_monumentaux = [
            {"type": "dome_geodesique", "materiau": "glass", "diametre": 20},
            {"type": "spire_cristalline", "hauteur": 30, "materiau": "quartz"},
        ]
        plan["elements_monumentaux"] = [random.choice(elements_monumentaux)]
        return plan

    def _calculer_score_complexite_enfance(self, plan: Dict) -> float:
        """Score de complexité pour phase enfance."""
        score = 0.0
        dimensions = plan.get("dimensions", [1, 1, 1])
        volume = dimensions[0] * dimensions[1] * dimensions[2]
        score += min(30, volume / 10)
        if plan.get("symetrie_parfaite"):
            score += 20
        return min(100.0, score)

    def _calculer_score_creativite_adolescence(self, plan: Dict) -> float:
        """Score de créativité pour phase adolescence."""
        score = 0.0
        forme = plan.get("forme", "rectangulaire")
        scores_forme = {"L_shape": 25, "circulaire_approx": 35, "spirale_simple": 40}
        score += scores_forme.get(forme, 15)
        if plan.get("experimentation_active"):
            score += 25
        return min(100.0, score)

    def _calculer_score_harmonie_adulte(self, plan: Dict) -> float:
        """Score d'harmonie pour phase adulte."""
        score = 0.0
        if plan.get("materiaux_adaptes"):
            score += 30
        if plan.get("integration_paysage"):
            score += 25
        if plan.get("durabilite_environnementale"):
            score += 20
        return min(100.0, score)

    def obtenir_styles_disponibles(self) -> List[str]:
        """Retourne la liste des styles disponibles."""
        return list(self.styles_phase.keys())