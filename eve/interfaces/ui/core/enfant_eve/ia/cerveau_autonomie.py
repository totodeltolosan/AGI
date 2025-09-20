import logging
import time

logger = logging.getLogger(__name__)


def evaluer_et_changer_mode(cerveau):
    """
    MOTEUR D'AUTONOMIE PRINCIPAL
    Évalue la situation et change automatiquement le mode de l'IA.
    Directive 32: Modes opératoires avec hiérarchie stricte.
    """
    try:
        situation = _analyser_situation_complete(cerveau)
        nouveau_mode = _determiner_mode_optimal(situation, cerveau.mode_actuel)

        if nouveau_mode != cerveau.mode_actuel:
            _changer_mode_ia(cerveau, nouveau_mode, situation)
            return True

        return False

    except Exception as e:
        logger.error("Erreur évaluation autonomie: %s", e)
        return False


def _analyser_situation_complete(cerveau):
    """Analyse complète de la situation actuelle"""
    try:
        # Récupérer état du monde
        etat_joueur = cerveau.modele_monde.get_etat_joueur()
        inventaire = cerveau.modele_monde.get_inventaire()
        environnement = cerveau.modele_monde.get_environnement_local()

        # Utiliser nos modules refactorisés pour l'analyse
        from enfant_eve.ia.planificateur_besoins import AnalyseurBesoins

        # Analyse des besoins
        analyse_besoins = AnalyseurBesoins.analyser_besoins_globaux(
            etat_joueur, inventaire, environnement
        )

        # Évaluation sécurité
        eval_securite = AnalyseurBesoins.evaluer_securite_zone(environnement)

        # Situation synthétique
        situation = {
            "health": etat_joueur.get("health", 20),
            "hunger": etat_joueur.get("hunger", 20),
            "inventaire_total": sum(inventaire.values()) if inventaire else 0,
            "ressources_critiques": len(analyse_besoins.get("besoins_critiques", [])),
            "score_securite": eval_securite.get("score", 50),
            "score_survie": analyse_besoins["scores"].get("survie", 50),
            "score_ressources": analyse_besoins["scores"].get("ressources", 50),
            "besoins_critiques": analyse_besoins.get("besoins_critiques", []),
            "besoins_normaux": analyse_besoins.get("besoins_normaux", []),
            "temps_depuis_spawn": time.time()
            - getattr(cerveau, "temps_spawn", time.time()),
        }

        logger.info(
            "[AUTONOMIE] Situation analysée: survie=%d, ressources=%d, sécurité=%d",
            situation["score_survie"],
            situation["score_ressources"],
            situation["score_securite"],
        )

        return situation

    except Exception as e:
        logger.error("Erreur analyse situation: %s", e)
        # Situation par défaut en cas d'erreur
        return {
            "health": 20,
            "hunger": 20,
            "inventaire_total": 0,
            "ressources_critiques": 1,
            "score_securite": 50,
            "score_survie": 50,
            "score_ressources": 30,
            "besoins_critiques": ["ANALYSER"],
            "besoins_normaux": [],
            "temps_depuis_spawn": 60,
        }


def _determiner_mode_optimal(situation, mode_actuel):
    """
    Détermine le mode optimal selon la hiérarchie des priorités.
    Directive 32: Hiérarchie stricte survie > exploration > création.
    """

    # PHASE 1: DÉMARRAGE (Directive 54)
    if situation["temps_depuis_spawn"] < 120:  # Première 2 minutes
        if mode_actuel in ["DEMARRAGE", "ANALYSE_SPAWN"]:
            return "ANALYSE_SPAWN"  # Continuer analyse
        else:
            return "survie"  # Passer à survie après analyse

    # PHASE 2: HIÉRARCHIE DES PRIORITÉS

    # 1. SURVIE (Priorité absolue)
    if _besoin_survie_critique(situation):
        return "survie"

    # 2. SÉCURITÉ (Priorité haute)
    if _besoin_securisation(situation):
        return "survie"  # Mode survie inclut sécurisation

    # 3. RESSOURCES (Priorité normale)
    if _besoin_ressources(situation):
        return "exploration"  # Pour collecter ressources

    # 4. DÉVELOPPEMENT (Priorité basse)
    if _conditions_construction(situation):
        return "creation"

    # 5. DÉFAUT - Exploration pour découverte
    return "exploration"


def _besoin_survie_critique(situation):
    """Vérifie si la survie est en danger critique"""
    return (
        situation["health"] < 10
        or situation["hunger"] < 6
        or situation["score_survie"] < 40
        or len(situation["besoins_critiques"]) > 0
    )


def _besoin_securisation(situation):
    """Vérifie si la zone nécessite sécurisation"""
    return situation["score_securite"] < 60


def _besoin_ressources(situation):
    """Vérifie si des ressources sont nécessaires"""
    return (
        situation["score_ressources"] < 60
        or situation["inventaire_total"] < 50
        or len(situation["besoins_normaux"]) > 2
    )


def _conditions_construction(situation):
    """Vérifie si les conditions pour construire sont réunies"""
    return (
        situation["score_survie"] > 70
        and situation["score_securite"] > 70
        and situation["score_ressources"] > 60
        and situation["inventaire_total"] > 100
    )


def _changer_mode_ia(cerveau, nouveau_mode, situation):
    """Change le mode de l'IA et notifie"""
    ancien_mode = cerveau.mode_actuel
    cerveau.mode_actuel = nouveau_mode

    # Nettoyer plan précédent si changement majeur
    if _changement_majeur(ancien_mode, nouveau_mode):
        cerveau.dernier_plan_genere = None
        cerveau.action_en_cours = None

    # Logging du changement
    logger.info(
        "[AUTONOMIE] Changement mode: %s -> %s (survie=%d, ressources=%d)",
        ancien_mode,
        nouveau_mode,
        situation["score_survie"],
        situation["score_ressources"],
    )

    # Notification GUI
    _notifier_changement_mode(cerveau, ancien_mode, nouveau_mode, situation)


def _changement_majeur(ancien_mode, nouveau_mode):
    """Détermine si le changement de mode est majeur"""
    changements_majeurs = [
        ("exploration", "survie"),
        ("creation", "survie"),
        ("creation", "exploration"),
    ]
    return (ancien_mode, nouveau_mode) in changements_majeurs


def _notifier_changement_mode(cerveau, ancien_mode, nouveau_mode, situation):
    """Notifie le changement de mode à l'interface"""
    try:
        notification = {
            "type": "CHANGEMENT_MODE",
            "ancien_mode": ancien_mode,
            "nouveau_mode": nouveau_mode,
            "raison": _generer_raison_changement(situation),
            "timestamp": time.time(),
        }

        cerveau.queues["ia_vers_gui"].put(notification, timeout=0.5)

    except Exception as e:
        logger.warning("Erreur notification GUI: %s", e)


def _generer_raison_changement(situation):
    """Génère une explication du changement de mode"""
    if situation["score_survie"] < 40:
        return "Survie critique détectée"
    elif situation["score_securite"] < 60:
        return "Zone non sécurisée"
    elif situation["score_ressources"] < 60:
        return "Ressources insuffisantes"
    elif situation["inventaire_total"] > 100:
        return "Conditions favorables à la construction"
    else:
        return "Exploration pour développement"


def forcer_mode_autonome(cerveau):
    """Force l'IA à sortir du mode VEILLE et devenir autonome"""
    if cerveau.mode_actuel in ["VEILLE", "ATTENTE"]:
        # Analyse forcée pour déterminer action
        situation = _analyser_situation_complete(cerveau)
        nouveau_mode = _determiner_mode_optimal(situation, cerveau.mode_actuel)

        if nouveau_mode != cerveau.mode_actuel:
            _changer_mode_ia(cerveau, nouveau_mode, situation)
            logger.info("[AUTONOMIE] IA forcée en mode autonome: %s", nouveau_mode)
            return True

    return False


def initialiser_autonomie(cerveau):
    """Initialise le système d'autonomie au démarrage"""
    cerveau.temps_spawn = time.time()
    cerveau.derniere_evaluation_autonomie = time.time()

    # Forcer première évaluation
    forcer_mode_autonome(cerveau)

    logger.info("[AUTONOMIE] Système d'autonomie initialisé")
