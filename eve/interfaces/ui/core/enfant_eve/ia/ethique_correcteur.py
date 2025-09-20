import time
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CorrectorEthique:
    """
    Correcteur spécialisé pour les violations éthiques.
    Applique des corrections automatiques selon le type de violation.
    """

    def appliquer_correction(self, plan: Dict, violation: str) -> Dict:
        """Applique une correction spécialisée selon le type de violation."""
        try:
            plan_corrige = plan.copy()

            if "preservation_nature" in violation:
                return self._corriger_preservation_nature(plan_corrige, violation)
            elif "anti_gaspillage" in violation:
                return self._corriger_gaspillage(plan_corrige, violation)
            elif "durabilite_construction" in violation:
                return self._corriger_durabilite(plan_corrige, violation)
            elif "respect_biomes" in violation:
                return self._corriger_respect_biomes(plan_corrige, violation)
            elif "equilibre_ecosysteme" in violation:
                return self._corriger_equilibre(plan_corrige, violation)
            elif "recherche_ethique" in violation:
                return self._corriger_recherche(plan_corrige, violation)
            elif "exploitation_moderee" in violation:
                return self._corriger_exploitation(plan_corrige, violation)

            return plan_corrige

        except Exception as e:
            logger.error(f"Erreur correction violation {violation}: {e}")
            return plan

    def _corriger_preservation_nature(self, plan: Dict, violation: str) -> Dict:
        """Corrige les violations de préservation de la nature."""
        if "zone_impact_excessive" in violation:
            plan["zone_impact"] = min(plan.get("zone_impact", 0), 50)

        if "destruction_massive" in violation:
            tags = plan.get("tags", [])
            tags = [tag for tag in tags if "destruction" not in tag]
            plan["tags"] = tags

        return plan

    def _corriger_gaspillage(self, plan: Dict, violation: str) -> Dict:
        """Corrige les violations de gaspillage."""
        ressources = plan.get("ressources_necessaires", {})

        for ressource, quantite in ressources.items():
            if quantite > 1000:
                ressources[ressource] = min(quantite, 500)

        plan["ressources_necessaires"] = ressources
        return plan

    def _corriger_durabilite(self, plan: Dict, violation: str) -> Dict:
        """Corrige les violations de durabilité."""
        if "materiaux_non_durables" in violation:
            materiaux_durables = ["stone", "brick", "iron_block"]
            plan["materiaux_autorises"] = materiaux_durables

        return plan

    def _corriger_respect_biomes(self, plan: Dict, violation: str) -> Dict:
        """Corrige les violations de respect des biomes."""
        biome = plan.get("biome_cible", "plains")

        materiaux_adaptes = {
            "desert": ["sand", "sandstone", "cactus"],
            "ocean": ["prismarine", "sea_lantern", "kelp"],
            "forest": ["wood", "leaves", "moss"],
            "mountain": ["stone", "snow", "ice"],
        }

        plan["materiaux_autorises"] = materiaux_adaptes.get(biome, ["stone", "wood"])
        return plan

    def _corriger_equilibre(self, plan: Dict, violation: str) -> Dict:
        """Corrige les violations d'équilibre écosystémique."""
        if "surexploitation" in violation:
            plan["taux_exploitation"] = min(plan.get("taux_exploitation", 0), 0.3)

        return plan

    def _corriger_recherche(self, plan: Dict, violation: str) -> Dict:
        """Corrige les violations d'éthique de recherche."""
        if "exploitation_potentielle" in violation:
            tags = plan.get("tags", [])
            tags = [tag for tag in tags if "[exploit_potentiel]" not in tag]
            tags.append("[etude_scientifique]")
            plan["tags"] = tags
            plan["methode"] = "observation_controlee"

        return plan

    def _corriger_exploitation(self, plan: Dict, violation: str) -> Dict:
        """Corrige les violations d'exploitation modérée."""
        if "extraction_excessive" in violation:
            plan["quantite_cible"] = min(plan.get("quantite_cible", 0), 1000)

        if "objectif_excessif" in violation:
            plan["quantite_cible"] = min(plan.get("quantite_cible", 0), 2000)

        return plan


class UtilitairesEthique:
    """
    Utilitaires pour les calculs et rapports éthiques.
    Contient les méthodes déplacées du module principal.
    """

    def calculer_score_ethique(self, violations: List[str]) -> float:
        """Calcule un score éthique de 0 à 1."""
        if not violations:
            return 1.0

        score_base = 1.0
        for violation in violations:
            severite = self.obtenir_severite_violation(violation, [])
            penalite = (6 - severite) / 10.0
            score_base -= penalite

        return max(0.0, score_base)

    def evaluer_niveau_risque(self, violations: List[str]) -> str:
        """Évalue le niveau de risque éthique."""
        if not violations:
            return "aucun"

        severite_max = self.calculer_severite_max(violations, [])
        if severite_max <= 1:
            return "critique"
        elif severite_max <= 2:
            return "élevé"
        elif severite_max <= 3:
            return "modéré"
        else:
            return "faible"

    def evaluer_durabilite(self, plan: Dict) -> float:
        """Évalue la durabilité d'un plan de construction."""
        score = 0.5
        materiaux = plan.get("materiaux_autorises", [])
        materiaux_durables = ["stone", "brick", "iron_block", "obsidian"]

        if any(mat in materiaux_durables for mat in materiaux):
            score += 0.3

        if plan.get("fonctionnel", False):
            score += 0.2

        return min(1.0, score)

    def evaluer_impact_environnemental(self, plan: Dict) -> float:
        """Évalue l'impact environnemental d'un plan d'exploitation."""
        score = 1.0
        zone_impact = plan.get("zone_impact", 0)

        if zone_impact > 50:
            score -= 0.3
        if zone_impact > 100:
            score -= 0.3

        if plan.get("compensation"):
            score += 0.2

        return max(0.0, score)

    def evaluer_ethique_scientifique(self, plan: Dict) -> float:
        """Évalue l'éthique scientifique d'un plan de recherche."""
        score = 0.8

        if plan.get("approche") == "observation_controlee":
            score += 0.2

        if "[exploit_potentiel]" in plan.get("tags", []):
            score -= 0.5

        return max(0.0, min(1.0, score))

    def obtenir_severite_violation(self, violation: str, regles: List) -> int:
        """Obtient la sévérité d'une violation."""
        severites = {
            "preservation_nature": 2,
            "anti_gaspillage": 3,
            "durabilite_construction": 3,
            "respect_biomes": 4,
            "equilibre_ecosysteme": 2,
            "recherche_ethique": 1,
            "exploitation_moderee": 4,
        }

        for nom_regle, severite in severites.items():
            if nom_regle in violation:
                return severite

        return 3

    def calculer_severite_max(self, violations: List[str], regles: List) -> int:
        """Calcule la sévérité maximale parmi les violations."""
        if not violations:
            return 5

        severites = [self.obtenir_severite_violation(v, regles) for v in violations]
        return min(severites) if severites else 5

    def generer_recommandations_plan(self, violations: List[str]) -> List[str]:
        """Génère des recommandations basées sur les violations."""
        recommandations = []

        for violation in violations:
            if "preservation_nature" in violation:
                recommandations.append("Réduire la zone d'impact du projet")
            elif "gaspillage" in violation:
                recommandations.append("Optimiser l'utilisation des ressources")
            elif "durabilite" in violation:
                recommandations.append("Utiliser des matériaux plus durables")
            elif "recherche_ethique" in violation:
                recommandations.append("Adopter une approche d'observation contrôlée")

        return recommandations

    def generer_rapport_complet(self, historique: List[Dict], regles: List) -> Dict:
        """Génère un rapport complet sur les performances éthiques."""
        if not historique:
            return {"message": "Aucune donnée disponible"}

        total_validations = len(historique)
        validations_reussies = sum(1 for h in historique if h.get("valide", False))
        taux_reussite = (
            validations_reussies / total_validations if total_validations > 0 else 0
        )

        return {
            "total_validations": total_validations,
            "taux_reussite": taux_reussite,
            "violations_frequentes": self._analyser_violations_frequentes(historique),
            "tendance": "amelioration" if taux_reussite > 0.8 else "attention_requise",
            "timestamp": time.time(),
        }

    def _analyser_violations_frequentes(self, historique: List[Dict]) -> Dict:
        """Analyse les violations les plus fréquentes."""
        compteur_violations = {}

        for record in historique:
            for violation in record.get("violations", []):
                type_violation = violation.split(":")[0]
                compteur_violations[type_violation] = (
                    compteur_violations.get(type_violation, 0) + 1
                )

        return dict(
            sorted(compteur_violations.items(), key=lambda x: x[1], reverse=True)
        )
