import time
import math
import random
import logging
from typing import Dict, List, Any, Tuple, Optional
from collections import deque

logger = logging.getLogger(__name__)


class CacheRaisonnement:
    """
    Gestionnaire de cache pour le raisonnement.
    Respecte Directive 61 avec focus sur la gestion du cache uniquement.
    """

    def __init__(self, duree_cache: int = 30):
        """TODO: Add docstring."""
        self._cache_positions_sures = {}
        self._cache_ressources = {}
        self._cache_timestamp = 0
        self._duree_cache = duree_cache

    def obtenir_position_sure(
        self, cache_key: str
    ) -> Optional[Tuple[float, float, float]]:
        """Obtient une position sûre du cache."""
        if self._cache_valide() and cache_key in self._cache_positions_sures:
            return self._cache_positions_sures[cache_key]
        return None

    def stocker_position_sure(
        self, cache_key: str, position: Tuple[float, float, float]
    ):
        """Stocke une position sûre dans le cache."""
        self._cache_positions_sures[cache_key] = position
        self._cache_timestamp = time.time()

    def obtenir_ressource(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Obtient une ressource du cache."""
        if self._cache_valide() and cache_key in self._cache_ressources:
            return self._cache_ressources[cache_key]
        return None

    def stocker_ressource(self, cache_key: str, ressource: Dict[str, Any]):
        """Stocke une ressource dans le cache."""
        self._cache_ressources[cache_key] = ressource
        self._cache_timestamp = time.time()

    def _cache_valide(self) -> bool:
        """Vérifie si le cache est valide."""
        return (time.time() - self._cache_timestamp) < self._duree_cache

    def nettoyer_caches_expires(self):
        """Nettoie les caches expirés."""
        if not self._cache_valide():
            self._cache_positions_sures.clear()
            self._cache_ressources.clear()

    def invalider_tous_caches(self):
        """Invalide tous les caches."""
        self._cache_positions_sures.clear()
        self._cache_ressources.clear()
        self._cache_timestamp = 0


class CalculateurMetriques:
    """
    Calculateur de métriques et utilitaires pour le raisonnement.
    Respecte Directive 61 avec focus sur les calculs uniquement.
    """

    @staticmethod
    def initialiser_regles_survie() -> Dict[str, Any]:
        """Initialise les règles de survie."""
        return {
            "abri_requis": {
                "conditions": ["nuit", "mobs_proches", "vie_faible", "pas_abri"],
                "priorite": 10,
                "actions": ["construire_abri", "eclairer_zone", "barricader"],
            },
            "nourriture_urgente": {
                "conditions": ["faim < 6", "pas_nourriture_inventaire"],
                "priorite": 9,
                "actions": ["chercher_animaux", "collecter_fruits", "chasser"],
            },
            "outils_manquants": {
                "conditions": ["pas_outils", "ressources_disponibles"],
                "priorite": 7,
                "actions": ["craft_table", "craft_outils_bois", "ameliorer_outils"],
            },
        }

    @staticmethod
    def initialiser_patterns_ressources() -> Dict[str, Any]:
        """Initialise les patterns de localisation des ressources."""
        return {
            "wood": {
                "biomes_optimaux": ["forêt", "jungle", "taiga"],
                "altitude_optimale": (60, 120),
                "indicateurs": ["leaves", "log", "sapling"],
                "methode_detection": "visuelle_surface",
            },
            "stone": {
                "biomes_optimaux": ["montagne", "collines", "grottes"],
                "altitude_optimale": (0, 80),
                "indicateurs": ["cobblestone", "stone", "gravel"],
                "methode_detection": "mining_surface",
            },
            "iron": {
                "biomes_optimaux": ["montagne", "collines"],
                "altitude_optimale": (15, 60),
                "indicateurs": ["stone", "cave_openings", "ravines"],
                "methode_detection": "mining_profond",
            },
            "food": {
                "biomes_optimaux": ["plaines", "forêt", "rivières"],
                "altitude_optimale": (60, 100),
                "indicateurs": ["animals", "wheat", "water"],
                "methode_detection": "observation_faune_flore",
            },
        }

    @staticmethod
    def evaluer_securite_position(
        position: Tuple[float, float, float], modele_monde
    ) -> float:
        """Évalue la sécurité d'une position (0-100)."""
        try:
            x, y, z = position
            score = 50  # Score de base

            # Bonus d'altitude
            if 60 <= y <= 90:
                score += 20
            elif y > 100:
                score -= 10

            # Vérifier proximité eau (sécuritaire)
            carte = getattr(modele_monde, "carte_du_monde", {})
            for pos_str, bloc_type in carte.items():
                if "water" in str(bloc_type):
                    try:
                        pos_eau = tuple(map(float, pos_str.split(",")))
                        distance = CalculateurMetriques.calculer_distance_3d(
                            position, pos_eau
                        )
                        if distance < 20:
                            score += 15
                            break
                    except:
                        continue

            # Éviter lave
            for pos_str, bloc_type in carte.items():
                if "lava" in str(bloc_type):
                    try:
                        pos_lave = tuple(map(float, pos_str.split(",")))
                        distance = CalculateurMetriques.calculer_distance_3d(
                            position, pos_lave
                        )
                        if distance < 10:
                            score -= 30
                            break
                    except:
                        continue

            return max(0, min(100, score))

        except Exception as e:
            logger.error(f"Erreur évaluation sécurité: {e}")
            return 25

    @staticmethod
    def calculer_distance_3d(
        pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]
    ) -> float:
        """Calcule la distance 3D entre deux positions."""
        try:
            return math.sqrt(
                (pos1[0] - pos2[0]) ** 2
                + (pos1[1] - pos2[1]) ** 2
                + (pos1[2] - pos2[2]) ** 2
            )
        except:
            return 999.0

    @staticmethod
    def chercher_abris_existants(
        carte: Dict, position_actuelle: List[float]
    ) -> List[Tuple[Tuple[float, float, float], float]]:
        """Cherche des abris existants dans la carte."""
        abris_potentiels = []
        x, y, z = position_actuelle[:3]

        for pos_str, bloc_type in carte.items():
            if any(
                abri in str(bloc_type) for abri in ["house", "cave", "shelter", "roof"]
            ):
                try:
                    pos = tuple(map(float, pos_str.split(",")))
                    distance = CalculateurMetriques.calculer_distance_3d((x, y, z), pos)
                    if distance < 50:
                        abris_potentiels.append((pos, distance))
                except:
                    continue

        return abris_potentiels

    @staticmethod
    def analyser_sources_animales(
        entites: List[Dict], position_actuelle: List[float]
    ) -> List[Dict]:
        """Analyse les sources de nourriture animales."""
        sources = []
        animaux_comestibles = ["cow", "pig", "chicken", "sheep", "rabbit"]

        for entite in entites:
            if entite.get("type", "") in animaux_comestibles:
                pos_entite = entite.get("position", position_actuelle)
                distance = CalculateurMetriques.calculer_distance_3d(
                    position_actuelle, pos_entite
                )

                if distance < 30:
                    valeurs_nutritives = {
                        "cow": 8,
                        "pig": 6,
                        "chicken": 4,
                        "sheep": 5,
                        "rabbit": 3,
                    }
                    sources.append(
                        {
                            "type": "animal",
                            "espece": entite["type"],
                            "position": pos_entite,
                            "distance": distance,
                            "valeur_nutritive": valeurs_nutritives.get(
                                entite["type"], 2
                            ),
                        }
                    )

        return sources

    @staticmethod
    def analyser_sources_vegetales(
        carte: Dict, position_actuelle: List[float]
    ) -> List[Dict]:
        """Analyse les sources de nourriture végétales."""
        sources = []
        plantes_comestibles = ["wheat", "carrot", "potato", "apple", "berry"]

        for pos_str, bloc_type in carte.items():
            if any(plante in str(bloc_type) for plante in plantes_comestibles):
                try:
                    pos = tuple(map(float, pos_str.split(",")))
                    distance = CalculateurMetriques.calculer_distance_3d(
                        position_actuelle, pos
                    )

                    if distance < 25:
                        valeurs = {
                            "wheat": 5,
                            "carrot": 3,
                            "potato": 1,
                            "apple": 4,
                            "berry": 2,
                        }
                        valeur = next(
                            (v for p, v in valeurs.items() if p in str(bloc_type)), 1
                        )

                        sources.append(
                            {
                                "type": "vegetale",
                                "espece": bloc_type,
                                "position": pos,
                                "distance": distance,
                                "valeur_nutritive": valeur,
                            }
                        )
                except:
                    continue

        return sources

    @staticmethod
    def calculer_score_priorite_nourriture(source: Dict) -> float:
        """Calcule le score de priorité pour une source de nourriture."""
        valeur = source.get("valeur_nutritive", 1)
        facilite = source.get("facilite_collecte", 0.5)
        distance_norm = max(0.1, 1.0 - (source["distance"] / 50.0))
        return valeur * facilite * distance_norm

    @staticmethod
    def extraire_contexte_actuel(modele_monde) -> Dict:
        """Extrait le contexte actuel depuis le modèle du monde."""
        try:
            return {
                "position": modele_monde.get_position_joueur(),
                "stats": modele_monde.get_stats_joueur(),
                "inventaire": modele_monde.get_inventaire_simplifie(),
                "environnement": modele_monde.get_etat_environnement(),
                "timestamp": time.time(),
            }
        except Exception as e:
            logger.error(f"Erreur extraction contexte: {e}")
            return {"timestamp": time.time(), "erreur": "contexte_indisponible"}

    @staticmethod
    def classifier_probleme(description_probleme: str) -> str:
        """Classifie un problème selon son type."""
        description_lower = description_probleme.lower()

        if any(
            mot in description_lower
            for mot in ["manque", "besoin", "plus de", "épuisé"]
        ):
            return "manque_ressource"
        elif any(
            mot in description_lower
            for mot in ["monstre", "hostile", "danger", "attaque"]
        ):
            return "menace_hostile"
        elif any(
            mot in description_lower
            for mot in ["lent", "inefficace", "optimiser", "améliorer"]
        ):
            return "inefficacite_construction"
        elif any(
            mot in description_lower
            for mot in ["déplacement", "transport", "route", "chemin"]
        ):
            return "probleme_deplacement"
        elif any(
            mot in description_lower
            for mot in ["stockage", "inventaire", "organisation", "tri"]
        ):
            return "gestion_ressources"
        else:
            return "probleme_general"

    @staticmethod
    def calculer_statistiques_raisonnement(
        historique: deque, cache: CacheRaisonnement
    ) -> Dict:
        """Calcule les statistiques de raisonnement."""
        if not historique:
            return {"message": "Aucune déduction effectuée"}

        types_problemes = {}
        for deduction in historique:
            type_prob = deduction.get("probleme", {}).get("type", "inconnu")
            types_problemes[type_prob] = types_problemes.get(type_prob, 0) + 1

        return {
            "total_deductions": len(historique),
            "types_problemes_traites": types_problemes,
            "derniere_deduction": historique[-1]["timestamp"] if historique else 0,
            "cache_positions": len(cache._cache_positions_sures),
            "cache_ressources": len(cache._cache_ressources),
            "cache_validite": "valide" if cache._cache_valide() else "expiré",
        }