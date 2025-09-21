import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def analyser_cycles_apprentissage(cerveau) -> Dict[str, Any]:
    """Analyse les cycles d'apprentissage selon Directive 8."""
    try:
        if not hasattr(cerveau, "historique_apprentissage"):
            return {}

        analyse = {
            "timestamp": time.time(),
            "cycles_detectes": [],
            "tendances": {},
            "efficacite_globale": 0.0,
            "recommandations": [],
        }

        donnees_recentes = cerveau.historique_apprentissage[-50:]

        analyse["cycles_detectes"] = _detecter_cycles_temporels(donnees_recentes)
        analyse["tendances"] = _analyser_tendances_apprentissage(donnees_recentes)
        analyse["efficacite_globale"] = _calculer_efficacite_globale(donnees_recentes)
        analyse["recommandations"] = _generer_recommandations_cycles(analyse)

        return analyse

    except Exception as e:
        logger.error(f"Erreur analyse cycles: {e}")
        return {}


def _detecter_cycles_temporels(donnees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Détecte des cycles temporels dans l'apprentissage."""
    cycles = []

    if len(donnees) < 10:
        return cycles

    timestamps = [d.get("timestamp", 0) for d in donnees]
    potentiels = [d.get("potentiel", 0) for d in donnees]

    for i in range(len(potentiels) - 5):
        sequence = potentiels[i : i + 5]

        if _est_cycle_croissant(sequence):
            cycles.append(
                {
                    "type": "croissance",
                    "debut": timestamps[i],
                    "fin": timestamps[i + 4],
                    "amplitude": max(sequence) - min(sequence),
                }
            )

        elif _est_cycle_decroissant(sequence):
            cycles.append(
                {
                    "type": "regression",
                    "debut": timestamps[i],
                    "fin": timestamps[i + 4],
                    "amplitude": max(sequence) - min(sequence),
                }
            )

    return cycles


def _est_cycle_croissant(sequence: List[float]) -> bool:
    """Vérifie si une séquence représente une croissance."""
    croissances = 0
    for i in range(len(sequence) - 1):
        if sequence[i + 1] > sequence[i]:
            croissances += 1
    return croissances >= 3


def _est_cycle_decroissant(sequence: List[float]) -> bool:
    """Vérifie si une séquence représente une décroissance."""
    decroissances = 0
    for i in range(len(sequence) - 1):
        if sequence[i + 1] < sequence[i]:
            decroissances += 1
    return decroissances >= 3


def _analyser_tendances_apprentissage(
    donnees: List[Dict[str, Any]],
) -> Dict[str, float]:
    """Analyse les tendances générales d'apprentissage."""
    if len(donnees) < 3:
        return {}

    potentiels = [d.get("potentiel", 0) for d in donnees]

    tendance_generale = (potentiels[-1] - potentiels[0]) / len(potentiels)

    variabilite = _calculer_variabilite(potentiels)

    acceleration = 0.0
    if len(potentiels) >= 6:
        premiere_moitie = sum(potentiels[: len(potentiels) // 2]) / (
            len(potentiels) // 2
        )
        seconde_moitie = sum(potentiels[len(potentiels) // 2 :]) / (
            len(potentiels) - len(potentiels) // 2
        )
        acceleration = seconde_moitie - premiere_moitie

    return {
        "tendance_generale": tendance_generale,
        "variabilite": variabilite,
        "acceleration": acceleration,
        "stabilite": 1.0 - variabilite,
    }


def _calculer_variabilite(valeurs: List[float]) -> float:
    """Calcule la variabilité d'une série de valeurs."""
    if len(valeurs) < 2:
        return 0.0

    moyenne = sum(valeurs) / len(valeurs)
    variance = sum((v - moyenne) ** 2 for v in valeurs) / len(valeurs)

    return min(variance**0.5, 1.0)


def _calculer_efficacite_globale(donnees: List[Dict[str, Any]]) -> float:
    """Calcule l'efficacité globale de l'apprentissage."""
    if not donnees:
        return 0.0

    potentiels = [d.get("potentiel", 0) for d in donnees]

    efficacite_moyenne = sum(potentiels) / len(potentiels)

    progression = 0.0
    if len(potentiels) >= 2:
        progression = max(0, potentiels[-1] - potentiels[0])

    consistance = 1.0 - _calculer_variabilite(potentiels)

    efficacite_globale = (
        efficacite_moyenne * 0.4 + progression * 0.3 + consistance * 0.3
    )

    return min(efficacite_globale, 1.0)


def _generer_recommandations_cycles(analyse: Dict[str, Any]) -> List[str]:
    """Génère des recommandations basées sur l'analyse des cycles."""
    recommandations = []

    efficacite = analyse.get("efficacite_globale", 0.0)
    tendances = analyse.get("tendances", {})

    if efficacite < 0.3:
        recommandations.append("augmenter_diversite_experiences")

    if tendances.get("variabilite", 0.0) > 0.7:
        recommandations.append("stabiliser_environnement_apprentissage")

    if tendances.get("tendance_generale", 0.0) < 0:
        recommandations.append("revoir_strategies_apprentissage")

    cycles_regression = [
        c for c in analyse.get("cycles_detectes", []) if c.get("type") == "regression"
    ]
    if len(cycles_regression) > 2:
        recommandations.append("identifier_facteurs_regression")

    if tendances.get("acceleration", 0.0) > 0.5:
        recommandations.append("maintenir_dynamique_positive")

    return recommandations
