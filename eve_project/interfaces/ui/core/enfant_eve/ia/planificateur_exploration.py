import logging
from typing import Dict, List, Tuple, Any
import math
import random

logger = logging.getLogger(__name__)


class StrategieExploration:
    """
    Stratégies d'exploration intelligente du monde.
    Implémente différents patterns d'exploration selon les objectifs.
    """

    def __init__(self):
        """TODO: Add docstring."""
        self.zones_explorees = set()
        self.zones_interdites = set()
        self.points_interet = {}
        self.patterns_disponibles = [
            "spirale",
            "quadrillage",
            "rayonnant",
            "adaptatif",
            "opportuniste",
        ]

    def planifier_exploration_systematique(self, zone_cible: Dict) -> List[Dict]:
        """
        Planifie une exploration systématique d'une zone.
        Utilise le pattern optimal selon la taille et le terrain.
        """
        try:
            taille_zone = zone_cible.get("taille", 50)
            type_terrain = zone_cible.get("terrain", "normal")
            objectif = zone_cible.get("objectif", "general")

            # Sélectionner pattern optimal
            pattern = self._choisir_pattern_optimal(taille_zone, type_terrain, objectif)

            # Générer séquence d'actions
            actions = self._generer_actions_pattern(pattern, zone_cible)

            # Ajouter actions de sécurité et préparation
            actions_completes = (
                self._actions_preparation_exploration(zone_cible)
                + actions
                + self._actions_finalisation_exploration()
            )

            return actions_completes[:12]  # Limiter à 12 actions

        except Exception as e:
            logger.error(f"Erreur planification exploration: {e}")
            return [
                {"type": "EXPLORER_ALEATOIRE", "duree": 300},
                {"type": "SCANNER_ENVIRONNEMENT", "rayon": 20},
            ]

    def generer_hypotheses_exploration(self, observations: List[Dict]) -> List[str]:
        """
        Génère des hypothèses d'exploration basées sur les observations.
        Utilise l'analyse de patterns pour prédire zones intéressantes.
        """
        try:
            hypotheses = []

            # Analyser patterns dans observations
            patterns = self._analyser_patterns_observations(observations)

            # Générer hypothèses selon patterns détectés
            for pattern_type, details in patterns.items():
                if pattern_type == "minerai_concentre":
                    hypotheses.append(f"Gisement probable à {details['direction']}")
                elif pattern_type == "structure_artificielle":
                    hypotheses.append(
                        f"Village/donjon possible vers {details['position']}"
                    )
                elif pattern_type == "biome_transition":
                    hypotheses.append(
                        f"Nouveau biome accessible via {details['passage']}"
                    )
                elif pattern_type == "ressource_rare":
                    hypotheses.append(f"Zone riche en {details['ressource']} détectée")

            # Ajouter hypothèses génériques si aucun pattern clair
            if not hypotheses:
                hypotheses.extend(
                    [
                        "Exploration radiale pour cartographie générale",
                        "Recherche de points d'eau et abris naturels",
                        "Identification de routes commerciales potentielles",
                    ]
                )

            return hypotheses[:5]  # Limiter à 5 hypothèses

        except Exception as e:
            logger.error(f"Erreur génération hypothèses: {e}")
            return ["Exploration générale recommandée"]

    def calculer_zone_optimale_next(self, position_actuelle: Tuple[int, int]) -> Dict:
        """
        Calcule la prochaine zone optimale à explorer.
        Considère distance, potentiel et risques.
        """
        try:
            zones_candidates = self._identifier_zones_candidates(position_actuelle)

            meilleure_zone = None
            meilleur_score = -1

            for zone in zones_candidates:
                score = self._evaluer_zone_exploration(zone, position_actuelle)

                if score > meilleur_score:
                    meilleur_score = score
                    meilleure_zone = zone

            return meilleure_zone or {
                "position": (position_actuelle[0] + 100, position_actuelle[1]),
                "taille": 50,
                "priorite": "normale",
                "score": 50,
            }

        except Exception as e:
            logger.error(f"Erreur calcul zone optimale: {e}")
            return {
                "position": (0, 0),
                "taille": 30,
                "priorite": "normale",
                "score": 40,
            }

    def adapter_exploration_contexte(self, contexte: Dict) -> Dict:
        """
        Adapte la stratégie d'exploration selon le contexte actuel.
        Modifie paramètres selon ressources, temps et objectifs.
        """
        try:
            strategie_base = {
                "vitesse": "normale",
                "profondeur": "standard",
                "securite": "equilibree",
                "focus": "general",
            }

            # Adaptations selon ressources disponibles
            if contexte.get("ressources_limitees", False):
                strategie_base["vitesse"] = "rapide"
                strategie_base["profondeur"] = "superficielle"
                strategie_base["focus"] = "ressources_essentielles"

            # Adaptations selon temps disponible
            temps_limite = contexte.get("temps_limite", None)
            if temps_limite and temps_limite < 1800:  # Moins de 30 min
                strategie_base["vitesse"] = "acceleree"
                strategie_base["securite"] = "prudente"

            # Adaptations selon objectifs spécifiques
            objectif = contexte.get("objectif_principal", "")
            if "combat" in objectif.lower():
                strategie_base["focus"] = "structures_defensives"
                strategie_base["securite"] = "aggressive"
            elif "construction" in objectif.lower():
                strategie_base["focus"] = "materiaux_construction"
                strategie_base["profondeur"] = "detaillee"

            return strategie_base

        except Exception as e:
            logger.error(f"Erreur adaptation exploration: {e}")
            return {"vitesse": "normale", "profondeur": "standard", "focus": "general"}

    def _choisir_pattern_optimal(self, taille: int, terrain: str, objectif: str) -> str:
        """Choisit le pattern d'exploration optimal"""
        if taille < 30:
            return "rayonnant"
        elif terrain == "montagne":
            return "adaptatif"
        elif "ressource" in objectif:
            return "quadrillage"
        elif taille > 100:
            return "spirale"
        else:
            return "rayonnant"

    def _generer_actions_pattern(self, pattern: str, zone: Dict) -> List[Dict]:
        """Génère les actions selon le pattern choisi"""
        actions = []
        centre = zone.get("position", (0, 0))
        taille = zone.get("taille", 50)

        if pattern == "spirale":
            actions.extend(self._actions_spirale(centre, taille))
        elif pattern == "quadrillage":
            actions.extend(self._actions_quadrillage(centre, taille))
        elif pattern == "rayonnant":
            actions.extend(self._actions_rayonnant(centre, taille))
        else:  # adaptatif par défaut
            actions.extend(self._actions_adaptatif(centre, taille))

        return actions

    def _actions_spirale(self, centre: Tuple[int, int], taille: int) -> List[Dict]:
        """Génère actions pour pattern spirale"""
        return [
            {"type": "DEPLACER_CENTRE", "position": centre},
            {"type": "INITIALISER_SPIRALE", "rayon_initial": 10},
            {"type": "EXPLORER_SPIRALE_HORAIRE", "pas": 5, "tours": 3},
            {"type": "DOCUMENTER_DECOUVERTES", "methode": "systematique"},
        ]

    def _actions_quadrillage(self, centre: Tuple[int, int], taille: int) -> List[Dict]:
        """Génère actions pour pattern quadrillage"""
        return [
            {"type": "DIVISER_ZONE_GRILLE", "cellules": "9x9"},
            {"type": "EXPLORER_CELLULE_PAR_CELLULE", "ordre": "gauche_droite"},
            {"type": "MARQUER_CELLULES_COMPLETEES", "systeme": "coordonnees"},
        ]

    def _actions_rayonnant(self, centre: Tuple[int, int], taille: int) -> List[Dict]:
        """Génère actions pour pattern rayonnant"""
        return [
            {"type": "ETABLIR_POINT_CENTRAL", "position": centre},
            {"type": "EXPLORER_DIRECTION_NORD", "distance": taille // 2},
            {"type": "RETOUR_CENTRE", "chemin": "direct"},
            {"type": "EXPLORER_DIRECTION_EST", "distance": taille // 2},
            {"type": "EXPLORER_DIRECTION_SUD", "distance": taille // 2},
            {"type": "EXPLORER_DIRECTION_OUEST", "distance": taille // 2},
        ]

    def _actions_adaptatif(self, centre: Tuple[int, int], taille: int) -> List[Dict]:
        """Génère actions pour pattern adaptatif"""
        return [
            {"type": "ANALYSER_TERRAIN_LOCAL", "rayon": 20},
            {"type": "ADAPTER_ROUTE_TERRAIN", "eviter": ["eau", "lave"]},
            {"type": "EXPLORER_OPPORTUNISTE", "priorite": "points_interet"},
        ]

    def _actions_preparation_exploration(self, zone: Dict) -> List[Dict]:
        """Actions de préparation avant exploration"""
        return [
            {"type": "VERIFIER_EQUIPEMENT", "obligatoire": ["carte", "torches"]},
            {"type": "EVALUER_RISQUES_ZONE", "niveau": zone.get("danger", "normal")},
        ]

    def _actions_finalisation_exploration(self) -> List[Dict]:
        """Actions de finalisation après exploration"""
        return [
            {"type": "COMPILER_RAPPORT", "format": "carte_annotee"},
            {"type": "PLANIFIER_EXPLORATION_SUIVANTE", "base": "decouvertes"},
        ]

    def _analyser_patterns_observations(self, observations: List[Dict]) -> Dict:
        """Analyse les patterns dans les observations"""
        patterns = {}

        # Analyser concentrations de minerai
        minerais = [obs for obs in observations if obs.get("type") == "minerai"]
        if len(minerais) > 3:
            patterns["minerai_concentre"] = {"direction": "nord", "densite": "elevee"}

        # Analyser structures artificielles
        structures = [obs for obs in observations if obs.get("artificiel", False)]
        if structures:
            patterns["structure_artificielle"] = {
                "position": "proximite",
                "type": "inconnu",
            }

        return patterns

    def _identifier_zones_candidates(self, position: Tuple[int, int]) -> List[Dict]:
        """Identifie les zones candidates pour exploration"""
        candidates = []

        # Générer zones autour de la position actuelle
        for direction in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nouvelle_zone = {
                "position": (
                    position[0] + direction[0] * 100,
                    position[1] + direction[1] * 100,
                ),
                "taille": random.randint(40, 80),
                "terrain": "inconnu",
            }
            candidates.append(nouvelle_zone)

        return candidates

    def _evaluer_zone_exploration(
        self, zone: Dict, position_actuelle: Tuple[int, int]
    ) -> float:
        """Évalue le potentiel d'une zone pour exploration"""
        score = 50.0

        # Pénalité distance
        distance = math.sqrt(
            (zone["position"][0] - position_actuelle[0]) ** 2
            + (zone["position"][1] - position_actuelle[1]) ** 2
        )
        score -= distance / 20

        # Bonus taille appropriée
        if 40 <= zone["taille"] <= 80:
            score += 10

        return max(0, min(100, score))