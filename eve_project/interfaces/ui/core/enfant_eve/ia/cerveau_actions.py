import logging

logger = logging.getLogger(__name__)


def executer_action(cerveau, plan):
    """
    Exécute les actions du plan choisi.
    Directive 47: Gestion du temps d'attente avec hiérarchie d'utilisation.
    """
    if not plan:
        # Pas de plan: chercher tâche de fond ou réflexion
        action_par_defaut = _generer_action_par_defaut(cerveau)
        _envoyer_commande(cerveau, action_par_defaut)
        return

    # Exécuter prochaine action du plan
    action = plan.prochaine_action()

    if action:
        logger.info("[IA] Exécution action: %s", action.get("type", "INCONNUE"))
        _envoyer_commande(cerveau, action)

        # Mise à jour état cerveau
        cerveau.action_en_cours = action

        # Si plan terminé, nettoyer
        if not plan.a_des_actions():
            cerveau.dernier_plan_genere = None
            logger.info("[IA] Plan '%s' terminé", plan.nom)
    else:
        # Plan sans actions: action par défaut
        action_par_defaut = _generer_action_par_defaut(cerveau)
        _envoyer_commande(cerveau, action_par_defaut)


def _envoyer_commande(cerveau, action):
    """Envoie la commande vers le jeu"""
    try:
        cerveau.queues["ia_vers_jeu"].put(action, timeout=1.0)
        logger.info("[IA] Action envoyée: %s", action)
    except Exception as e:
        logger.error("Erreur envoi commande: %s", e)


def _generer_action_par_defaut(cerveau):
    """
    Génère une action par défaut selon le mode et la situation.
    Directive 47: Hiérarchie d'utilisation du temps.
    """
    mode = cerveau.mode_actuel

    # 1. Vérifier tâches parallèles
    tache_parallele = _chercher_tache_parallele(cerveau)
    if tache_parallele:
        return tache_parallele

    # 2. Vérifier tâches de fond
    tache_de_fond = _chercher_tache_de_fond(cerveau)
    if tache_de_fond:
        return tache_de_fond

    # 3. Actions par défaut selon mode
    if mode == "VEILLE":
        # Analyser l'environnement pour déterminer le besoin
        return _determiner_action_autonome(cerveau)
    elif mode == "DEMARRAGE" or mode == "ANALYSE_SPAWN":
        return {"type": "SCANNER_ENVIRONNEMENT", "rayon": 20, "duree": 10}
    else:
        return {"type": "EVALUER_SITUATION", "duree": 5}


def _determiner_action_autonome(cerveau):
    """
    LOGIQUE D'AUTONOMIE PRINCIPALE
    Détermine automatiquement ce que l'IA doit faire selon sa situation.
    """
    try:
        # Obtenir état du monde depuis le modèle
        etat_joueur = cerveau.modele_monde.get_etat_joueur()
        inventaire = cerveau.modele_monde.get_inventaire()
        environnement = cerveau.modele_monde.get_environnement_local()

        # Analyse besoins critiques avec nos modules refactorisés
        from .planificateur_besoins import AnalyseurBesoins

        analyse = AnalyseurBesoins.analyser_besoins_globaux(
            etat_joueur, inventaire, environnement
        )

        # LOGIQUE DE DÉCISION AUTONOME
        if analyse["besoins_critiques"]:
            # Besoins critiques détectés -> Mode survie
            cerveau.mode_actuel = "survie"
            return _action_survie_immediate(analyse["besoins_critiques"])

        elif analyse["scores"]["ressources"] < 50:
            # Ressources insuffisantes -> Mode acquisition
            cerveau.mode_actuel = "exploration"  # Pour collecter ressources
            return _action_collecte_ressources(analyse["besoins_normaux"])

        elif analyse["scores"]["securite"] < 60:
            # Zone non sécurisée -> Sécurisation
            return _action_securisation_zone()

        else:
            # Situation stable -> Mode création/construction
            cerveau.mode_actuel = "creation"
            return _action_construction_creative()

    except Exception as e:
        logger.error("Erreur détermination action autonome: %s", e)
        # Action de sécurité en cas d'erreur
        return {"type": "ANALYSER_SITUATION", "duree": 10}


def _action_survie_immediate(besoins_critiques):
    """Actions de survie immédiate"""
    if "SOIGNER" in besoins_critiques:
        return {"type": "CONSOMMER_NOURRITURE", "priorite": "critique"}
    elif "MANGER" in besoins_critiques:
        return {"type": "CHERCHER_NOURRITURE", "rayon": 30}
    elif "SECURISER_ZONE" in besoins_critiques:
        return {"type": "CHERCHER_ABRI", "criteres": ["sombre", "ferme"]}
    else:
        return {"type": "EVALUER_DANGER", "action": "immediate"}


def _action_collecte_ressources(ressources_manquantes):
    """Actions de collecte de ressources"""
    if not ressources_manquantes:
        return {"type": "EXPLORER_ZONE", "objectif": "ressources_generales"}

    # Prioriser première ressource manquante
    ressource_prioritaire = ressources_manquantes[0]

    if ressource_prioritaire == "wood":
        return {"type": "COUPER_ARBRES", "quantite": 20}
    elif ressource_prioritaire == "stone":
        return {"type": "MINER_PIERRE", "quantite": 15}
    elif ressource_prioritaire == "food":
        return {"type": "CHASSER_ANIMAUX", "cibles": ["cow", "pig"]}
    else:
        return {"type": "CHERCHER_RESSOURCE", "ressource": ressource_prioritaire}


def _action_securisation_zone():
    """Actions de sécurisation de zone"""
    return {"type": "PLACER_TORCHES", "nombre": 5, "disposition": "cercle"}


def _action_construction_creative():
    """Actions de construction créative"""
    return {"type": "PLANIFIER_CONSTRUCTION", "objectif": "abri_ameliore"}


def _chercher_tache_parallele(cerveau):
    """Cherche une tâche parallèle executable pendant l'attente"""
    # Implémentation simple pour commencer
    if hasattr(cerveau, "dernier_plan_genere") and cerveau.dernier_plan_genere:
        return None  # Plan en cours, pas de parallélisme

    # Tâches simples parallèles
    taches_possibles = [
        {"type": "ORGANISER_INVENTAIRE", "duree": 5},
        {"type": "ANALYSER_ENVIRONNEMENT", "rayon": 10},
        {"type": "VERIFIER_OUTILS", "duree": 3},
    ]

    # Retourner première tâche disponible (logique simple)
    return taches_possibles[0] if taches_possibles else None


def _chercher_tache_de_fond(cerveau):
    """Cherche une tâche de fond selon les priorités"""
    taches_de_fond = (
        cerveau.taches_de_fond_disponibles
        if hasattr(cerveau, "taches_de_fond_disponibles")
        else []
    )

    if "PATROUILLE_MAINTENANCE" in taches_de_fond:
        return {"type": "PATROUILLER_BASE", "rayon": 50}
    elif "OPTIMISATION_BASE" in taches_de_fond:
        return {"type": "AMELIORER_ECLAIRAGE", "zones": ["principale"]}
    elif "GESTION_RESSOURCES" in taches_de_fond:
        return {"type": "TRIER_STOCKAGE", "methode": "par_type"}

    return None
