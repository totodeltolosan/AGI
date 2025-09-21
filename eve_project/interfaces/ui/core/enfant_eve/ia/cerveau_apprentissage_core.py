import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def mettre_a_jour_connaissances(cerveau, nouvelles_donnees: Dict[str, Any]) -> None:
    """Met à jour les connaissances du cerveau selon Directive 1."""
    try:
        for cle, valeur in nouvelles_donnees.items():
            if cle in cerveau.connaissances:
                ancienne_valeur = cerveau.connaissances[cle]
                cerveau.connaissances[cle] = valeur

                evolution = _mesurer_evolution_connaissances(ancienne_valeur, valeur)
                cerveau.historique_apprentissage.append(
                    {
                        "timestamp": time.time(),
                        "cle": cle,
                        "evolution": evolution,
                        "potentiel": _evaluer_potentiel_evolutif(evolution),
                    }
                )
            else:
                cerveau.connaissances[cle] = valeur

        _auto_organiser_memoire(cerveau)

    except Exception as e:
        logger.error(f"Erreur mise à jour connaissances: {e}")


def _mesurer_evolution_connaissances(
    ancienne_valeur: Any, nouvelle_valeur: Any
) -> Dict[str, float]:
    """Mesure l'évolution quantitative des connaissances."""
    evolution = {
        "ampleur_changement": 0.0,
        "type_evolution": "stable",
        "potentiel_generalisation": 0.0,
    }

    try:
        if isinstance(ancienne_valeur, (int, float)) and isinstance(
            nouvelle_valeur, (int, float)
        ):
            diff_relative = abs(nouvelle_valeur - ancienne_valeur) / (
                abs(ancienne_valeur) + 1e-6
            )
            evolution["ampleur_changement"] = min(diff_relative, 1.0)

            if diff_relative > 0.1:
                evolution["type_evolution"] = "significatif"
            elif diff_relative > 0.01:
                evolution["type_evolution"] = "modere"

        elif isinstance(ancienne_valeur, str) and isinstance(nouvelle_valeur, str):
            if ancienne_valeur != nouvelle_valeur:
                evolution["ampleur_changement"] = 0.5
                evolution["type_evolution"] = "qualitatif"

        elif isinstance(ancienne_valeur, list) and isinstance(nouvelle_valeur, list):
            diff_taille = abs(len(nouvelle_valeur) - len(ancienne_valeur))
            evolution["ampleur_changement"] = min(
                diff_taille / (len(ancienne_valeur) + 1), 1.0
            )

            if diff_taille > 0:
                evolution["type_evolution"] = (
                    "expansion"
                    if len(nouvelle_valeur) > len(ancienne_valeur)
                    else "reduction"
                )

        evolution["potentiel_generalisation"] = _calculer_potentiel_generalisation(
            ancienne_valeur, nouvelle_valeur, evolution["ampleur_changement"]
        )

    except Exception as e:
        logger.warning(f"Erreur mesure évolution: {e}")

    return evolution


def _evaluer_potentiel_evolutif(evolution: Dict[str, float]) -> float:
    """Évalue le potentiel d'évolution future basé sur l'évolution actuelle."""
    base_score = evolution.get("ampleur_changement", 0.0)

    if evolution.get("type_evolution") == "significatif":
        multiplicateur = 1.5
    elif evolution.get("type_evolution") == "expansion":
        multiplicateur = 1.3
    elif evolution.get("type_evolution") == "qualitatif":
        multiplicateur = 1.2
    else:
        multiplicateur = 1.0

    potentiel_base = base_score * multiplicateur
    potentiel_generalisation = evolution.get("potentiel_generalisation", 0.0)

    return min(potentiel_base + potentiel_generalisation * 0.3, 1.0)


def _calculer_potentiel_generalisation(
    ancienne_valeur: Any, nouvelle_valeur: Any, ampleur: float
) -> float:
    """Calcule le potentiel de généralisation d'un apprentissage."""
    if ampleur < 0.1:
        return 0.0

    if isinstance(nouvelle_valeur, list) and len(nouvelle_valeur) > 3:
        return min(len(nouvelle_valeur) * 0.1, 0.8)

    if isinstance(nouvelle_valeur, dict) and len(nouvelle_valeur) > 2:
        return min(len(nouvelle_valeur) * 0.15, 0.9)

    return ampleur * 0.5


def _auto_organiser_memoire(cerveau) -> None:
    """Organisation automatique de la mémoire selon Directive 15."""
    try:
        if len(cerveau.historique_apprentissage) > 1000:
            cerveau.historique_apprentissage = cerveau.historique_apprentissage[-800:]

        apprentissages_significatifs = [
            entry
            for entry in cerveau.historique_apprentissage[-100:]
            if entry.get("potentiel", 0) > 0.5
        ]

        if len(apprentissages_significatifs) >= 5:
            _generer_pattern_apprentissage(cerveau, apprentissages_significatifs)

    except Exception as e:
        logger.error(f"Erreur auto-organisation mémoire: {e}")


def _generer_pattern_apprentissage(
    cerveau, apprentissages: List[Dict[str, Any]]
) -> None:
    """Génère des patterns à partir des apprentissages significatifs."""
    try:
        patterns_emergents = {}

        for apprentissage in apprentissages:
            cle = apprentissage.get("cle", "")
            evolution = apprentissage.get("evolution", {})

            pattern_key = f"pattern_{evolution.get('type_evolution', 'unknown')}"

            if pattern_key not in patterns_emergents:
                patterns_emergents[pattern_key] = {
                    "occurrences": 0,
                    "ampleur_moyenne": 0.0,
                    "domaines": set(),
                }

            patterns_emergents[pattern_key]["occurrences"] += 1
            patterns_emergents[pattern_key]["ampleur_moyenne"] += evolution.get(
                "ampleur_changement", 0.0
            )
            patterns_emergents[pattern_key]["domaines"].add(
                cle.split("_")[0] if "_" in cle else "general"
            )

        for pattern_key, pattern_data in patterns_emergents.items():
            if pattern_data["occurrences"] >= 3:
                pattern_data["ampleur_moyenne"] /= pattern_data["occurrences"]
                pattern_data["domaines"] = list(pattern_data["domaines"])

                cerveau.patterns_apprentissage[pattern_key] = pattern_data

                logger.info(f"Pattern émergent détecté: {pattern_key}")

    except Exception as e:
        logger.error(f"Erreur génération patterns: {e}")
