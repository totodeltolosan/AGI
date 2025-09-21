import logging
from typing import Dict, List, Any, Tuple
import math

logger = logging.getLogger(__name__)


class OptimisateurConstruction:
    """
    Optimisateur de plans de construction et d'architecture.
    Implémente l'adaptation des constructions selon la phase de vie et les objectifs.
    """

    @staticmethod
    def adapter_construction_phase(phase_de_vie: str, objectif: str) -> Dict:
        """
        Adapte un plan de construction selon la phase de vie et l'objectif.
        Retourne un plan détaillé avec matériaux et spécifications.
        """
        try:
            # Plan de base selon la phase de vie
            if phase_de_vie == "survie":
                plan_base = OptimisateurConstruction._plan_construction_survie()
            elif phase_de_vie == "developpement":
                plan_base = OptimisateurConstruction._plan_construction_developpement()
            elif phase_de_vie == "expansion":
                plan_base = OptimisateurConstruction._plan_construction_expansion()
            else:
                plan_base = OptimisateurConstruction._plan_construction_survie()

            # Enrichir avec métadonnées de qualité
            plan_base.update(
                {
                    "objectif_specifique": objectif,
                    "phase_origine": phase_de_vie,
                    "niveau_qualite": "standard",
                    "duree_construction": "10-30_heures",
                    "niveau_detail": "fonctionnel",
                }
            )

            # Ajuster selon l'objectif spécifique
            OptimisateurConstruction._ajuster_selon_objectif(plan_base, objectif)

            return plan_base

        except Exception as e:
            logger.error(f"Erreur adaptation construction phase: {e}")
            return {
                "type": "construction",
                "objectif": objectif,
                "style": "simple",
                "materiaux": ["wood"],
            }

    @staticmethod
    def evaluer_efficacite_construction(
        plan: Dict, ressources_disponibles: Dict
    ) -> float:
        """
        Évalue l'efficacité d'un plan de construction (0-1).
        Considère disponibilité ressources, complexité et faisabilité.
        """
        try:
            score_efficacite = 1.0

            # Évaluer disponibilité des matériaux
            materiaux_requis = plan.get("materiaux", [])
            for materiau in materiaux_requis:
                quantite_requise = plan.get("quantites", {}).get(materiau, 10)
                quantite_disponible = ressources_disponibles.get(materiau, 0)

                if quantite_disponible < quantite_requise:
                    deficit = (
                        quantite_requise - quantite_disponible
                    ) / quantite_requise
                    score_efficacite -= deficit * 0.3

            # Pénalité pour complexité excessive
            complexite = plan.get("niveau_detail", "simple")
            if complexite == "perfectionniste":
                score_efficacite -= 0.2
            elif complexite == "detaille":
                score_efficacite -= 0.1

            # Bonus pour plans adaptés à la phase
            if plan.get("phase_origine") == "survie" and len(materiaux_requis) <= 2:
                score_efficacite += 0.1

            return max(0.0, min(1.0, score_efficacite))

        except Exception as e:
            logger.error(f"Erreur évaluation efficacité: {e}")
            return 0.5

    @staticmethod
    def optimiser_utilisation_materiaux(
        plan_construction: Dict, inventaire: Dict
    ) -> Dict:
        """
        Optimise l'utilisation des matériaux disponibles.
        Propose substitutions et optimisations pour maximiser l'efficacité.
        """
        try:
            plan_optimise = plan_construction.copy()
            materiaux_originaux = plan_construction.get("materiaux", [])

            # Mapping des substitutions possibles
            substitutions = {
                "stone": ["cobblestone", "andesite", "granite"],
                "wood": ["oak_wood", "birch_wood", "spruce_wood"],
                "iron": ["steel", "reinforced_iron"],
                "glass": ["sand", "quartz"],
            }

            # Appliquer substitutions selon disponibilité
            materiaux_optimises = []
            for materiau in materiaux_originaux:
                if inventaire.get(materiau, 0) >= 10:
                    materiaux_optimises.append(materiau)
                else:
                    # Chercher substitution disponible
                    substitution_trouvee = False
                    for substitut in substitutions.get(materiau, []):
                        if inventaire.get(substitut, 0) >= 10:
                            materiaux_optimises.append(substitut)
                            substitution_trouvee = True
                            break

                    if not substitution_trouvee:
                        materiaux_optimises.append(materiau)  # Garder original

            plan_optimise["materiaux"] = materiaux_optimises

            # Ajuster quantités selon disponibilité
            plan_optimise["quantites_optimisees"] = (
                OptimisateurConstruction._calculer_quantites_optimales(
                    materiaux_optimises, inventaire
                )
            )

            # Calculer score d'optimisation
            plan_optimise["score_optimisation"] = (
                OptimisateurConstruction._calculer_score_optimisation(
                    plan_optimise, inventaire
                )
            )

            return plan_optimise

        except Exception as e:
            logger.error(f"Erreur optimisation matériaux: {e}")
            return plan_construction

    @staticmethod
    def _plan_construction_survie() -> Dict:
        """Plan de construction pour phase survie"""
        return {
            "type": "abri_survie",
            "style": "fonctionnel",
            "materiaux": ["wood", "dirt"],
            "dimensions": {"largeur": 5, "longueur": 5, "hauteur": 3},
            "fonctionnalites": ["protection", "stockage_basique"],
            "quantites": {"wood": 20, "dirt": 15},
        }

    @staticmethod
    def _plan_construction_developpement() -> Dict:
        """Plan de construction pour phase développement"""
        return {
            "type": "maison_intermediate",
            "style": "equilibre",
            "materiaux": ["wood", "stone", "glass"],
            "dimensions": {"largeur": 8, "longueur": 10, "hauteur": 4},
            "fonctionnalites": ["confort", "ateliers", "stockage_organise"],
            "quantites": {"wood": 40, "stone": 30, "glass": 8},
        }

    @staticmethod
    def _plan_construction_expansion() -> Dict:
        """Plan de construction pour phase expansion"""
        return {
            "type": "complexe_avance",
            "style": "architectural",
            "materiaux": ["stone", "iron", "glass", "redstone"],
            "dimensions": {"largeur": 15, "longueur": 20, "hauteur": 6},
            "fonctionnalites": ["automatisation", "defense", "production", "luxe"],
            "quantites": {"stone": 80, "iron": 25, "glass": 20, "redstone": 15},
        }

    @staticmethod
    def _ajuster_selon_objectif(plan: Dict, objectif: str):
        """Ajuste le plan selon l'objectif spécifique"""
        if "ferme" in objectif.lower():
            plan["specialisation"] = "agricole"
            plan["fonctionnalites"] = [
                "zones_culture",
                "stockage_recoltes",
                "irrigation",
            ]
            plan["materiaux"].append("water_bucket")

        elif "defense" in objectif.lower():
            plan["specialisation"] = "militaire"
            plan["fonctionnalites"] = ["murs_fortifies", "tours_guet", "pieges"]
            plan["materiaux"].extend(["obsidian", "iron_bars"])

        elif "mine" in objectif.lower():
            plan["specialisation"] = "industrielle"
            plan["fonctionnalites"] = [
                "puits_extraction",
                "systemes_transport",
                "fonderies",
            ]
            plan["materiaux"].extend(["rails", "minecart"])

        elif "maison" in objectif.lower():
            plan["specialisation"] = "residentielle"
            plan["fonctionnalites"] = ["confort", "stockage", "ateliers"]
            plan["materiaux"].extend(["wool", "carpet"])

        elif "monument" in objectif.lower():
            plan["specialisation"] = "ceremonielle"
            plan["fonctionnalites"] = ["espace_celebration", "symbolisme", "visibilite"]
            plan["materiaux"].extend(["gold", "diamond_block"])

    @staticmethod
    def _calculer_quantites_optimales(
        materiaux: List[str], inventaire: Dict
    ) -> Dict[str, int]:
        """Calcule les quantités optimales selon l'inventaire"""
        quantites = {}

        for materiau in materiaux:
            disponible = inventaire.get(materiau, 0)

            # Utiliser au maximum 80% de ce qui est disponible
            quantite_optimale = min(disponible * 0.8, 50)  # Max 50 par matériau
            quantites[materiau] = int(quantite_optimale)

        return quantites

    @staticmethod
    def _calculer_score_optimisation(plan: Dict, inventaire: Dict) -> float:
        """Calcule le score d'optimisation du plan"""
        score = 0.0
        materiaux = plan.get("materiaux", [])
        quantites = plan.get("quantites_optimisees", {})

        for materiau in materiaux:
            quantite_voulue = quantites.get(materiau, 0)
            quantite_disponible = inventaire.get(materiau, 0)

            if quantite_disponible >= quantite_voulue:
                score += 1.0
            else:
                ratio = quantite_disponible / max(quantite_voulue, 1)
                score += ratio

        return score / max(len(materiaux), 1)
