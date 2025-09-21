"""
Perception et analyse environnement IA (Directive 6).
Traitement données sensorielles et détection patterns.
"""

import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def mettre_a_jour_perception(cerveau, etat_monde: Dict[str, Any]) -> None:
    """Met à jour perception IA selon nouvel état monde."""
    try:
        _traiter_donnees_joueur(cerveau, etat_monde.get("etat_joueur", {}))
        _traiter_entites_proches(cerveau, etat_monde.get("entites_proches", []))
        _traiter_scan_local(cerveau, etat_monde.get("scan_local_3d", []))
        _detecter_evenements_critiques(cerveau, etat_monde)

    except Exception as e:
        logger.error(f"Erreur mise à jour perception: {e}")


def _traiter_donnees_joueur(cerveau, etat_joueur: Dict[str, Any]) -> None:
    """Traite données spécifiques au joueur IA."""
    try:
        cerveau.position_actuelle = etat_joueur.get("position", {})
        cerveau.vie_actuelle = etat_joueur.get("vie", 100)
        cerveau.faim_actuelle = etat_joueur.get("faim", 100)
        cerveau.inventaire_actuel = etat_joueur.get("inventaire", {})

        if cerveau.vie_actuelle < 20:
            logger.warning("Vie critique détectée")
            cerveau.mode_actuel = "SURVIE"

    except Exception as e:
        logger.error(f"Erreur traitement données joueur: {e}")


def _traiter_entites_proches(cerveau, entites: List[Dict[str, Any]]) -> None:
    """Traite entités dans zone de perception."""
    try:
        for entite in entites:
            tags_generes = _generer_tags_contextuels(entite)

            id_entite = f"entite_{entite.get('id', 'inconnu')}"
            cerveau.modele_monde.graphe_connaissances.ajouter_ou_mettre_a_jour_concept(
                id_entite,
                {
                    "type_noeud": "Entite",
                    "donnees": entite,
                    "tags": tags_generes,
                    "derniere_observation": time.time(),
                },
            )

    except Exception as e:
        logger.error(f"Erreur traitement entités: {e}")


def _traiter_scan_local(cerveau, blocs: List[Dict[str, Any]]) -> None:
    """Traite scan 3D local de l'environnement."""
    try:
        for bloc in blocs:
            position_key = f"bloc_{bloc.get('position', {})}"

            cerveau.modele_monde.graphe_connaissances.ajouter_ou_mettre_a_jour_concept(
                position_key,
                {
                    "type_noeud": "Bloc",
                    "donnees": bloc,
                    "tags": ["terrain", bloc.get("type", "inconnu")],
                    "derniere_observation": time.time(),
                },
            )

    except Exception as e:
        logger.error(f"Erreur traitement scan local: {e}")


def cataloguer_entite_decouverte(cerveau, entite: Dict[str, Any]) -> None:
    """Catalogue nouvelle entité découverte."""
    try:
        type_entite = entite.get("type", "inconnu")

        if not _entite_deja_connue(cerveau, type_entite):
            logger.info(f"Nouvelle entité cataloguée: {type_entite}")

            cerveau.modele_monde.graphe_connaissances.ajouter_ou_mettre_a_jour_concept(
                f"type_entite_{type_entite}",
                {
                    "type_noeud": "TypeEntite",
                    "donnees": {
                        "type": type_entite,
                        "premiere_decouverte": time.time(),
                    },
                    "tags": ["nouveau", "a_etudier"],
                    "compteur_observations": 1,
                },
            )

    except Exception as e:
        logger.error(f"Erreur catalogage entité: {e}")


def _entite_deja_connue(cerveau, type_entite: str) -> bool:
    """Vérifie si type entité déjà connu."""
    concept_id = f"type_entite_{type_entite}"
    return (
        cerveau.modele_monde.graphe_connaissances.obtenir_noeud(concept_id) is not None
    )


def _generer_tags_contextuels(entite: Dict[str, Any]) -> List[str]:
    """Génère tags contextuels pour une entité."""
    tags = []
    nom = entite.get("nom", "").lower()
    type_entite = entite.get("type", "")

    tags.append(f"type_{type_entite}")

    if "mob" in type_entite:
        tags.append("entite_vivante")
        if entite.get("hostile", False):
            tags.append("dangereux")
        else:
            tags.append("passif")

    if any(animal in nom for animal in ["pig", "cow", "sheep"]):
        tags.extend(["source_nourriture", "elevage_possible"])

    if any(materiau in nom for materiau in ["wood", "log"]):
        tags.extend(["materiau_construction", "ressource_renouvelable"])

    if any(minerai in nom for minerai in ["ore", "iron", "diamond"]):
        tags.extend(["materiau_precieux", "ressource_limitee"])

    return tags


def _detecter_evenements_critiques(cerveau, etat_monde: Dict[str, Any]) -> None:
    """Détecte événements critiques nécessitant attention immédiate."""
    try:
        etat_joueur = etat_monde.get("etat_joueur", {})
        evenement = etat_monde.get("dernier_evenement")

        vie_actuelle = etat_joueur.get("vie", 100)
        if vie_actuelle < 20:
            logger.warning(f"Situation critique: Vie faible ({vie_actuelle})")
            cerveau.mode_actuel = "SURVIE"

        if evenement and not _evenement_connu(cerveau, evenement):
            logger.info(f"Événement inconnu détecté: {evenement.get('type')}")
            _protocole_premier_contact(cerveau, evenement)

        if _detecter_comportement_anormal(etat_monde):
            logger.warning("Comportement anormal du jeu détecté")
            _rapport_anomalie(cerveau, etat_monde)

    except Exception as e:
        logger.error(f"Erreur détection événements critiques: {e}")


def _evenement_connu(cerveau, evenement: Dict[str, Any]) -> bool:
    """Vérifie si un type d'événement est déjà connu du cerveau."""
    type_evenement = evenement.get("type", "")
    graphe = cerveau.modele_monde.graphe_connaissances

    for concept_id, concept_data in graphe.get("noeuds", {}).items():
        if "evenement" in concept_data.get("tags", []) and type_evenement in concept_id:
            return True

    return False


def _protocole_premier_contact(cerveau, evenement: Dict[str, Any]) -> None:
    """Protocole de gestion d'événements inconnus (Directive 59)."""
    try:
        type_evenement = evenement.get("type", "inconnu")

        cerveau.modele_monde.ajouter_ou_mettre_a_jour_concept(
            f"evenement_{type_evenement}",
            {
                "tags": ["evenement", "inconnu", "a_etudier"],
                "type_noeud": "Evenement",
                "premiere_observation": time.time(),
                "donnees_brutes": evenement,
            },
        )

        if cerveau.mode_actuel not in ["MAINTENANCE", "SURVIE"]:
            cerveau.mode_actuel = "EXPLORATION"

        logger.info(f"Nouvel événement catalogué: {type_evenement}")

    except Exception as e:
        logger.error(f"Erreur protocole premier contact: {e}")


def _detecter_comportement_anormal(etat_monde: Dict[str, Any]) -> bool:
    """Détecte les comportements anormaux du jeu (bugs potentiels) selon Directive 80."""
    etat_joueur = etat_monde.get("etat_joueur", {})

    position = etat_joueur.get("position", {})
    if position.get("y", 0) < -100 or position.get("y", 0) > 1000:
        return True

    vie = etat_joueur.get("vie", 0)
    if vie < 0 or vie > 1000:
        return True

    return False


def _rapport_anomalie(cerveau, etat_monde: Dict[str, Any]) -> None:
    """Génère un rapport d'anomalie selon Directive 80."""
    try:
        rapport = {
            "timestamp": time.time(),
            "type": "comportement_anormal_jeu",
            "etat_monde": etat_monde,
            "actions_recommandees": ["redemarrer_connexion", "signaler_bug"],
        }

        if hasattr(cerveau, "rapports_anomalies"):
            cerveau.rapports_anomalies.append(rapport)
        else:
            cerveau.rapports_anomalies = [rapport]

        logger.warning("Rapport d'anomalie généré")

    except Exception as e:
        logger.error(f"Erreur génération rapport anomalie: {e}")
