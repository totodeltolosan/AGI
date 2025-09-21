"""
Analyse échecs pour apprentissage (Directive 5).
Extraction leçons et adaptation comportement.
"""

import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def analyser_echec_pour_apprentissage(
    cerveau, echec_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyse un échec pour en extraire des leçons selon Directive 5."""
    try:
        analyse = {
            "timestamp": time.time(),
            "type_echec": echec_data.get("type", "inconnu"),
            "contexte": echec_data.get("contexte", {}),
            "causes_identifiees": [],
            "lecons_extraites": [],
            "actions_correctives": [],
            "niveau_gravite": _evaluer_gravite_echec(echec_data),
        }

        analyse["causes_identifiees"] = _identifier_causes_echec(cerveau, echec_data)
        analyse["lecons_extraites"] = _extraire_lecons_echec(
            analyse["causes_identifiees"]
        )
        analyse["actions_correctives"] = _generer_actions_correctives(analyse)

        _integrer_lecon_echec(cerveau, analyse)

        if analyse["niveau_gravite"] > 0.7:
            _declencher_adaptation_urgente(cerveau, analyse)

        return analyse

    except Exception as e:
        logger.error(f"Erreur analyse échec: {e}")
        return {}


def _evaluer_gravite_echec(echec_data: Dict[str, Any]) -> float:
    """Évalue la gravité d'un échec sur une échelle 0-1."""
    gravite_base = 0.3

    type_echec = echec_data.get("type", "")
    if "critique" in type_echec or "fatal" in type_echec:
        gravite_base = 0.9
    elif "majeur" in type_echec or "important" in type_echec:
        gravite_base = 0.7
    elif "mineur" in type_echec:
        gravite_base = 0.2

    impact = echec_data.get("impact", {})
    facteur_impact = 0.0

    if impact.get("survie", False):
        facteur_impact += 0.4
    if impact.get("mission", False):
        facteur_impact += 0.3
    if impact.get("ressources", False):
        facteur_impact += 0.2

    gravite_finale = min(gravite_base + facteur_impact, 1.0)
    return gravite_finale


def _identifier_causes_echec(cerveau, echec_data: Dict[str, Any]) -> List[str]:
    """Identifie les causes probables d'un échec."""
    causes = []

    contexte = echec_data.get("contexte", {})

    if contexte.get("ressources_insuffisantes", False):
        causes.append("manque_ressources")

    if contexte.get("information_incomplete", False):
        causes.append("donnees_insuffisantes")

    if contexte.get("temps_limite_depasse", False):
        causes.append("gestion_temps")

    if contexte.get("erreur_planification", False):
        causes.append("planification_defaillante")

    historique_similaire = _rechercher_echecs_similaires(cerveau, echec_data)
    if historique_similaire:
        causes.append("pattern_recurrent")

    if not causes:
        causes.append("cause_inconnue")

    return causes


def _extraire_lecons_echec(causes: List[str]) -> List[str]:
    """Extrait des leçons concrètes des causes identifiées."""
    lecons = []

    mapping_lecons = {
        "manque_ressources": "anticiper_besoins_ressources",
        "donnees_insuffisantes": "ameliorer_collecte_information",
        "gestion_temps": "optimiser_planification_temporelle",
        "planification_defaillante": "renforcer_verification_plans",
        "pattern_recurrent": "identifier_pattern_echec_systematique",
    }

    for cause in causes:
        if cause in mapping_lecons:
            lecons.append(mapping_lecons[cause])
        else:
            lecons.append(f"analyser_cause_{cause}")

    return lecons


def _generer_actions_correctives(analyse: Dict[str, Any]) -> List[str]:
    """Génère des actions correctives basées sur l'analyse."""
    actions = []

    for lecon in analyse.get("lecons_extraites", []):
        if "ressources" in lecon:
            actions.append("implementer_surveillance_ressources")
        elif "information" in lecon:
            actions.append("augmenter_phase_exploration")
        elif "temps" in lecon:
            actions.append("ajuster_estimation_duree")
        elif "verification" in lecon:
            actions.append("ajouter_checkpoints_validation")

    return actions


def _integrer_lecon_echec(cerveau, analyse: Dict[str, Any]) -> None:
    """Intègre une leçon d'échec dans la base de connaissances."""
    try:
        if not hasattr(cerveau, "lecons_echecs"):
            cerveau.lecons_echecs = []

        cerveau.lecons_echecs.append(analyse)

        if len(cerveau.lecons_echecs) > 100:
            cerveau.lecons_echecs = cerveau.lecons_echecs[-80:]

        for action in analyse.get("actions_correctives", []):
            _appliquer_action_corrective(cerveau, action)

    except Exception as e:
        logger.error(f"Erreur intégration leçon: {e}")


def _appliquer_action_corrective(cerveau, action: str) -> None:
    """Applique une action corrective dans le comportement du cerveau."""
    if action == "implementer_surveillance_ressources":
        cerveau.config_comportement["surveillance_ressources"] = True
    elif action == "augmenter_phase_exploration":
        cerveau.config_comportement["duree_exploration"] *= 1.2
    elif action == "ajuster_estimation_duree":
        cerveau.config_comportement["marge_securite_temps"] = 1.5
    elif action == "ajouter_checkpoints_validation":
        cerveau.config_comportement["validation_etapes"] = True


def _rechercher_echecs_similaires(
    cerveau, echec_actuel: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Recherche des échecs similaires dans l'historique."""
    if not hasattr(cerveau, "lecons_echecs"):
        return []

    echecs_similaires = []
    type_actuel = echec_actuel.get("type", "")

    for echec_passe in cerveau.lecons_echecs[-20:]:
        if echec_passe.get("type_echec", "") == type_actuel:
            echecs_similaires.append(echec_passe)

    return echecs_similaires


def _declencher_adaptation_urgente(cerveau, analyse: Dict[str, Any]) -> None:
    """Déclenche une adaptation urgente pour les échecs graves."""
    logger.warning(f"Échec grave détecté: {analyse['type_echec']}")

    cerveau.mode_actuel = "ADAPTATION_URGENTE"
    cerveau.priorite_apprentissage = "MAXIMAL"

    for action in analyse.get("actions_correctives", []):
        _appliquer_action_corrective(cerveau, action)
