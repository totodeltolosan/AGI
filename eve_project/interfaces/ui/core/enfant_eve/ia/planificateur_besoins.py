import logging
from typing import Dict, List, Any
import time

logger = logging.getLogger(__name__)


class AnalyseurBesoins:
    """
    Analyseur de besoins stratégiques pour la survie et le développement.
    Implémente l'évaluation des conditions et l'identification des ressources critiques.
    """

    @staticmethod
    def analyser_besoins_globaux(
        etat_joueur: Dict, inventaire: Dict, environnement: Dict
    ) -> Dict:
        """
        Analyse complète des besoins prioritaires selon l'état actuel.
        Retourne un diagnostic structuré avec scores et recommandations.
        """
        try:
            analyse = {
                "timestamp": time.time(),
                "besoins_critiques": [],
                "besoins_normaux": [],
                "opportunites": [],
                "scores": {},
            }

            # Analyser survie immédiate
            survie_score = AnalyseurBesoins._evaluer_survie(etat_joueur, inventaire)
            analyse["scores"]["survie"] = survie_score

            if survie_score < 50:
                analyse["besoins_critiques"].extend(
                    AnalyseurBesoins._identifier_besoins_survie(etat_joueur, inventaire)
                )

            # Analyser ressources
            ressources_score = AnalyseurBesoins._evaluer_ressources(inventaire)
            analyse["scores"]["ressources"] = ressources_score

            if ressources_score < 70:
                analyse["besoins_normaux"].extend(
                    AnalyseurBesoins.identifier_ressources_manquantes(
                        inventaire, "intermediaire"
                    )
                )

            # Analyser sécurité environnementale
            securite_eval = AnalyseurBesoins.evaluer_securite_zone(environnement)
            analyse["scores"]["securite"] = securite_eval["score"]

            if securite_eval["score"] < 60:
                analyse["besoins_critiques"].append("SECURISER_ZONE")

            return analyse

        except Exception as e:
            logger.error(f"Erreur analyse besoins globaux: {e}")
            return {
                "besoins_critiques": ["SURVIE_IMMEDIATE"],
                "besoins_normaux": ["COLLECTER_RESSOURCES"],
                "scores": {"survie": 50, "ressources": 50, "securite": 50},
            }

    @staticmethod
    def evaluer_securite_zone(environnement: Dict) -> Dict:
        """
        Évalue la sécurité d'une zone selon luminosité, mobs et terrain.
        Retourne score 0-100 avec recommandations adaptées.
        """
        try:
            score_securite = 100
            niveau_lumiere = environnement.get("lumiere", 8)
            mobs_proches = environnement.get("mobs_hostiles", [])
            terrain = environnement.get("type_terrain", "normal")

            # Pénalités selon luminosité
            if niveau_lumiere <= 7:
                score_securite -= 20
            if niveau_lumiere <= 4:
                score_securite -= 30

            # Pénalités selon mobs
            score_securite -= len(mobs_proches) * 10

            # Ajustements terrain
            if terrain == "cave":
                score_securite -= 15
            elif terrain == "nether":
                score_securite -= 25
            elif terrain == "ocean":
                score_securite -= 10

            score_final = max(0, min(100, score_securite))

            return {
                "score": score_final,
                "niveau": (
                    "sure"
                    if score_final > 70
                    else "risquee" if score_final > 40 else "dangereuse"
                ),
                "recommandations": AnalyseurBesoins._generer_recommandations_securite(
                    score_final, niveau_lumiere, mobs_proches
                ),
            }

        except Exception as e:
            logger.error(f"Erreur évaluation sécurité zone: {e}")
            return {
                "score": 50,
                "niveau": "inconnue",
                "recommandations": ["Rester vigilant"],
            }

    @staticmethod
    def identifier_ressources_manquantes(inventaire: Dict, niveau: str) -> List[str]:
        """
        Identifie les ressources manquantes selon le niveau de développement.
        Système de priorités dynamique et adaptatif.
        """
        try:
            seuils_requis = AnalyseurBesoins._obtenir_seuils_niveau(niveau)
            manquantes = []

            for ressource, quantite_min in seuils_requis.items():
                quantite_actuelle = inventaire.get(ressource, 0)

                if quantite_actuelle < quantite_min:
                    deficit = quantite_min - quantite_actuelle
                    manquantes.append(
                        {
                            "ressource": ressource,
                            "deficit": deficit,
                            "priorite": AnalyseurBesoins._calculer_priorite_ressource(
                                ressource, deficit, niveau
                            ),
                        }
                    )

            # Trier par priorité (plus haute en premier)
            manquantes.sort(key=lambda x: x["priorite"], reverse=True)

            # Retourner seulement les noms des ressources pour compatibilité
            return [item["ressource"] for item in manquantes[:5]]

        except Exception as e:
            logger.error(f"Erreur identification ressources manquantes: {e}")
            return ["wood", "stone", "food"]

    @staticmethod
    def _evaluer_survie(etat_joueur: Dict, inventaire: Dict) -> int:
        """Évalue le niveau de survie immédiate (0-100)"""
        score = 100

        # Vérifier santé
        health = etat_joueur.get("health", 20)
        if health < 10:
            score -= 40
        elif health < 15:
            score -= 20

        # Vérifier faim
        hunger = etat_joueur.get("hunger", 20)
        if hunger < 6:
            score -= 30
        elif hunger < 12:
            score -= 15

        # Vérifier nourriture en inventaire
        food_count = inventaire.get("food", 0)
        if food_count == 0:
            score -= 25

        return max(0, score)

    @staticmethod
    def _evaluer_ressources(inventaire: Dict) -> int:
        """Évalue la suffisance des ressources (0-100)"""
        score = 0
        essentielles = ["wood", "stone", "food", "coal"]

        for ressource in essentielles:
            quantite = inventaire.get(ressource, 0)
            if quantite > 10:
                score += 25
            elif quantite > 5:
                score += 15
            elif quantite > 0:
                score += 5

        return min(100, score)

    @staticmethod
    def _identifier_besoins_survie(etat_joueur: Dict, inventaire: Dict) -> List[str]:
        """Identifie les besoins critiques de survie"""
        besoins = []

        if etat_joueur.get("health", 20) < 10:
            besoins.append("SOIGNER")
        if etat_joueur.get("hunger", 20) < 6:
            besoins.append("MANGER")
        if inventaire.get("food", 0) == 0:
            besoins.append("TROUVER_NOURRITURE")

        return besoins

    @staticmethod
    def _obtenir_seuils_niveau(niveau: str) -> Dict[str, int]:
        """Retourne les seuils de ressources requis par niveau"""
        seuils = {
            "debutant": {"wood": 20, "stone": 10, "food": 8},
            "intermediaire": {"wood": 50, "stone": 30, "coal": 15, "iron": 10},
            "avance": {"iron": 25, "diamond": 5, "redstone": 10, "gold": 8},
        }
        return seuils.get(niveau, seuils["debutant"])

    @staticmethod
    def _calculer_priorite_ressource(
        ressource: str, deficit: int, niveau: str
    ) -> float:
        """Calcule la priorité d'une ressource manquante"""
        priorites_base = {
            "food": 10.0,
            "wood": 9.0,
            "stone": 8.0,
            "coal": 7.0,
            "iron": 6.0,
            "diamond": 3.0,
        }

        priorite_base = priorites_base.get(ressource, 5.0)
        multiplicateur_deficit = min(2.0, deficit / 10.0)

        return priorite_base * multiplicateur_deficit

    @staticmethod
    def _generer_recommandations_securite(
        score: int, lumiere: int, mobs: List
    ) -> List[str]:
        """Génère des recommandations de sécurité"""
        recommandations = []

        if score < 40:
            recommandations.append("Zone dangereuse - chercher refuge immédiatement")
        if lumiere <= 7:
            recommandations.append("Placer des torches pour améliorer l'éclairage")
        if len(mobs) > 0:
            recommandations.append(f"Éviter ou éliminer {len(mobs)} mob(s) hostile(s)")
        if score > 70:
            recommandations.append("Zone sûre pour la construction")

        return recommandations
