import re
import logging
from typing import Dict, List, Tuple, Any

from .ethique_regles import RegleEthique, creer_regles_eco_batisseuse

logger = logging.getLogger(__name__)


class ValidateurEcoBatisseuse:
    """
    Validateur spécialisé pour les règles éco-bâtisseuse.
    Implémente la logique de validation des plans.
    """

    def __init__(self):
        """TODO: Add docstring."""
        self.regles = creer_regles_eco_batisseuse()
        self.historique_validations = []

    def valider_contre_regles(self, plan: Dict) -> Tuple[bool, List[str]]:
        """
        Valide un plan contre toutes les règles éthiques applicables.
        Retourne (validité, liste_violations).
        """
        try:
            violations = []

            for regle in self.regles:
                if not regle.actif or not regle.est_applicable(plan):
                    continue

                violation_detectee = self._detecter_violation(plan, regle)
                if violation_detectee:
                    violations.append(f"{regle.nom}:{violation_detectee}")
                    regle.incrementer_violations()
                    logger.debug(
                        f"Violation détectée: {regle.nom} - {violation_detectee}"
                    )

            valide = len(violations) == 0

            self.historique_validations.append(
                {
                    "plan": plan.get("nom", "inconnu"),
                    "valide": valide,
                    "violations": violations,
                    "regles_appliquees": [
                        r.nom for r in self.regles if r.est_applicable(plan)
                    ],
                }
            )

            return valide, violations

        except Exception as e:
            logger.error(f"Erreur validation éthique: {e}")
            return True, []

    def _detecter_violation(self, plan: Dict, regle: RegleEthique) -> str:
        """Détecte une violation spécifique d'une règle."""
        try:
            if regle.nom == "preservation_nature":
                return self._verifier_preservation_nature(plan)
            elif regle.nom == "anti_gaspillage":
                return self._verifier_anti_gaspillage(plan)
            elif regle.nom == "durabilite_construction":
                return self._verifier_durabilite_construction(plan)
            elif regle.nom == "respect_biomes":
                return self._verifier_respect_biomes(plan)
            elif regle.nom == "equilibre_ecosysteme":
                return self._verifier_equilibre_ecosysteme(plan)
            elif regle.nom == "recherche_ethique":
                return self._verifier_recherche_ethique(plan)
            elif regle.nom == "exploitation_moderee":
                return self._verifier_exploitation_moderee(plan)

            return ""

        except Exception as e:
            logger.error(f"Erreur détection violation {regle.nom}: {e}")
            return ""

    def _verifier_preservation_nature(self, plan: Dict) -> str:
        """Vérifie les violations de préservation de la nature."""
        zone_impact = plan.get("zone_impact", 0)
        if zone_impact > 100:
            return "zone_impact_excessive"

        if "destruction_massive" in plan.get("tags", []):
            return "destruction_massive_detectee"

        return ""

    def _verifier_anti_gaspillage(self, plan: Dict) -> str:
        """Vérifie les violations de gaspillage."""
        ressources = plan.get("ressources_necessaires", {})

        for ressource, quantite in ressources.items():
            if quantite > 1000:
                return f"gaspillage_{ressource}"

        return ""

    def _verifier_durabilite_construction(self, plan: Dict) -> str:
        """Vérifie la durabilité des constructions."""
        materiaux = plan.get("materiaux_autorises", [])
        materiaux_fragiles = ["wood", "wool", "leaves"]

        if all(mat in materiaux_fragiles for mat in materiaux):
            return "materiaux_non_durables"

        return ""

    def _verifier_respect_biomes(self, plan: Dict) -> str:
        """Vérifie le respect des biomes."""
        biome_cible = plan.get("biome_cible")
        materiaux = plan.get("materiaux_autorises", [])

        if biome_cible == "desert" and "ice" in materiaux:
            return "inadaptation_biome_desert"
        elif biome_cible == "ocean" and "sand" in materiaux:
            return "inadaptation_biome_ocean"

        return ""

    def _verifier_equilibre_ecosysteme(self, plan: Dict) -> str:
        """Vérifie l'équilibre des écosystèmes."""
        if plan.get("type") == "exploitation":
            taux_exploitation = plan.get("taux_exploitation", 0)
            if taux_exploitation > 0.7:
                return "surexploitation_detectee"

        return ""

    def _verifier_recherche_ethique(self, plan: Dict) -> str:
        """Vérifie l'éthique de la recherche."""
        tags = plan.get("tags", [])
        if "[exploit_potentiel]" in tags:
            return "exploitation_potentielle"

        if plan.get("methode") == "experimentation_destructive":
            return "methode_destructive"

        return ""

    def _verifier_exploitation_moderee(self, plan: Dict) -> str:
        """Vérifie la modération de l'exploitation."""
        if "extraction_massive" in plan.get("description", ""):
            return "extraction_excessive"

        quantite_cible = plan.get("quantite_cible", 0)
        if quantite_cible > 5000:
            return "objectif_excessif"

        return ""