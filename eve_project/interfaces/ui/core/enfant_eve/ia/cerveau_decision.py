import logging

logger = logging.getLogger(__name__)


def generer_plan(cerveau):
    """
    Génère un plan d'action selon le mode actuel et la situation.
    Utilise les modules refactorisés pour une vraie autonomie.
    """
    try:
        # Vérifier que le planificateur est disponible
        if not hasattr(cerveau, "planificateur") or not cerveau.planificateur:
            logger.warning("Planificateur non disponible")
            return _generer_plan_de_secours(cerveau)

        # Obtenir phase de vie comportementale
        phase_de_vie = getattr(cerveau.comportement, "phase_de_vie", "ENFANCE")

        # Générer plans selon mode actuel
        plans = _generer_plans_selon_mode(cerveau, phase_de_vie)

        if not plans:
            logger.warning("Aucun plan généré par le planificateur")
            return _generer_plan_de_secours(cerveau)

        # Choisir le meilleur plan
        plan_choisi = _choisir_meilleur_plan(cerveau, plans)

        if plan_choisi:
            # Validation éthique
            if hasattr(cerveau, "ethique") and cerveau.ethique:
                if not cerveau.ethique.valider_plan(plan_choisi):
                    logger.warning("Plan rejeté par validation éthique")
                    return _generer_plan_de_secours(cerveau)

            logger.info(
                "[DÉCISION] Plan choisi: %s (%d actions)",
                plan_choisi.nom,
                len(plan_choisi.actions_initiales),
            )
            return plan_choisi

        # Aucun plan valide
        return _generer_plan_de_secours(cerveau)

    except Exception as e:
        logger.error("Erreur génération plan: %s", e, exc_info=True)
        return _generer_plan_de_secours(cerveau)


def _generer_plans_selon_mode(cerveau, phase_de_vie):
    """Génère des plans selon le mode opératoire actuel"""
    try:
        comportement_dict = _extraire_comportement(cerveau)
        mode = cerveau.mode_actuel

        logger.debug(
            "[DÉCISION] Génération plans mode: %s, phase: %s", mode, phase_de_vie
        )

        # Appeler le planificateur refactorisé
        plans = cerveau.planificateur.mettre_a_jour_objectifs(
            comportement_dict, mode, phase_de_vie
        )

        if plans and len(plans) > 0:
            logger.info(
                "[DÉCISION] %d plan(s) généré(s) pour mode %s", len(plans), mode
            )
            return plans
        else:
            logger.warning(
                "[DÉCISION] Planificateur n'a généré aucun plan pour mode %s", mode
            )
            return []

    except Exception as e:
        logger.error("Erreur génération plans mode %s: %s", cerveau.mode_actuel, e)
        return []


def _extraire_comportement(cerveau):
    """Extrait les données comportementales pour le planificateur"""
    try:
        if hasattr(cerveau, "comportement") and cerveau.comportement:
            # Extraire données comportementales réelles
            return {
                "agressivite": getattr(cerveau.comportement, "agressivite", 0.3),
                "creativite": getattr(cerveau.comportement, "creativite", 0.7),
                "prudence": getattr(cerveau.comportement, "prudence", 0.6),
                "curiosite": getattr(cerveau.comportement, "curiosite", 0.8),
                "phase_de_vie": getattr(
                    cerveau.comportement, "phase_de_vie", "ENFANCE"
                ),
            }
        else:
            # Valeurs par défaut
            return {
                "agressivite": 0.3,
                "creativite": 0.7,
                "prudence": 0.6,
                "curiosite": 0.8,
                "phase_de_vie": "ENFANCE",
            }
    except Exception as e:
        logger.warning("Erreur extraction comportement: %s", e)
        return {
            "agressivite": 0.3,
            "creativite": 0.7,
            "prudence": 0.6,
            "curiosite": 0.8,
        }


def _choisir_meilleur_plan(cerveau, plans):
    """Choisit le meilleur plan parmi ceux proposés"""
    try:
        if not plans or len(plans) == 0:
            return None

        # Si un seul plan, le retourner
        if len(plans) == 1:
            return plans[0]

        # Utiliser l'arbitre si disponible
        if hasattr(cerveau, "arbitre") and cerveau.arbitre:
            try:
                plan_choisi = cerveau.arbitre.prioriser_objectifs(
                    plans, cerveau.mode_actuel
                )
                if plan_choisi:
                    return plan_choisi
            except Exception as e:
                logger.warning("Erreur arbitrage: %s", e)

        # Sélection par priorité simple
        return _selection_par_priorite(plans)

    except Exception as e:
        logger.error("Erreur choix plan: %s", e)
        return plans[0] if plans else None


def _selection_par_priorite(plans):
    """Sélection simple par priorité des plans"""
    try:
        # Tri par priorité (critique > haute > normale > basse)
        ordre_priorite = {"critique": 4, "haute": 3, "normale": 2, "basse": 1}

        plans_tries = sorted(
            plans,
            key=lambda p: ordre_priorite.get(getattr(p, "priorite", "normale"), 2),
            reverse=True,
        )

        return plans_tries[0]

    except Exception as e:
        logger.error("Erreur sélection priorité: %s", e)
        return plans[0] if plans else None


def _generer_plan_de_secours(cerveau):
    """Génère un plan de secours quand le planificateur principal échoue"""
    try:
        from .planificateur_plans import Plan

        mode = getattr(cerveau, "mode_actuel", "survie")

        # Plans de secours selon le mode
        if mode == "survie":
            actions_secours = [
                {"type": "EVALUER_SANTE", "duree": 3},
                {"type": "CHERCHER_NOURRITURE", "rayon": 20},
                {"type": "SECURISER_POSITION", "duree": 10},
            ]
            return Plan("Plan de secours - Survie", actions_secours)

        elif mode == "exploration":
            actions_secours = [
                {"type": "SCANNER_ENVIRONNEMENT", "rayon": 30},
                {"type": "COLLECTER_RESSOURCES_VISIBLES", "priorite": "wood"},
                {"type": "EXPLORER_DIRECTION", "direction": "nord", "distance": 50},
            ]
            return Plan("Plan de secours - Exploration", actions_secours)

        elif mode == "creation":
            actions_secours = [
                {"type": "ANALYSER_TERRAIN", "zone": "locale"},
                {"type": "COLLECTER_MATERIAUX", "types": ["wood", "stone"]},
                {"type": "CONSTRUIRE_ABRI_SIMPLE", "taille": "3x3"},
            ]
            return Plan("Plan de secours - Construction", actions_secours)

        else:
            # Plan générique
            actions_secours = [
                {"type": "ANALYSER_SITUATION", "duree": 5},
                {"type": "EVALUER_OPTIONS", "duree": 3},
                {"type": "PRENDRE_DECISION", "methode": "simple"},
            ]
            return Plan("Plan de secours - Générique", actions_secours)

    except Exception as e:
        logger.error("Erreur génération plan secours: %s", e)
        # Plan minimal en dernier recours
        from .planificateur_plans import Plan

        return Plan("Plan minimal", [{"type": "ANALYSER_SITUATION", "duree": 10}])


def forcer_nouveau_plan(cerveau):
    """Force la génération d'un nouveau plan (pour débogage)"""
    try:
        # Nettoyer plan actuel
        cerveau.dernier_plan_genere = None
        cerveau.action_en_cours = None

        # Générer nouveau plan
        nouveau_plan = generer_plan(cerveau)

        if nouveau_plan:
            cerveau.dernier_plan_genere = nouveau_plan
            logger.info("[DÉCISION] Nouveau plan forcé: %s", nouveau_plan.nom)
            return nouveau_plan
        else:
            logger.warning("[DÉCISION] Impossible de forcer nouveau plan")
            return None

    except Exception as e:
        logger.error("Erreur forçage nouveau plan: %s", e)
        return None
