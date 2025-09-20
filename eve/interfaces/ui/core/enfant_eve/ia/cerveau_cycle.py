"""
Gestion cycles IA et séquences démarrage (Directive 54).
Orchestration temporelle processus cognitifs.
"""

import time
import queue
import logging
from enfant_eve.ia import cerveau_utils
from enfant_eve.ia import cerveau_perception
from enfant_eve.ia import cerveau_decision
from enfant_eve.ia import cerveau_actions
from enfant_eve.ia import cerveau_apprentissage
from enfant_eve.ia import cerveau_autonomie

logger = logging.getLogger(__name__)


def sequence_demarrage(cerveau):
    """Séquence démarrage avec analyse environnement (Directive 54)."""
    cerveau.mode_actuel = "ANALYSE_SPAWN"
    duree = cerveau.config.get("ia", {}).get("duree_analyse_spawn_min", 0.1) * 60
    temps_fin = time.time() + duree

    logger.info("Séquence démarrage (%.1fs)", duree)

    cerveau_autonomie.initialiser_autonomie(cerveau)

    while time.time() < temps_fin and cerveau.running:
        try:
            etat_monde = cerveau.queues["jeu_vers_ia"].get(timeout=0.5)
            if etat_monde:
                cerveau.modele_monde.update(etat_monde)
                cerveau_perception.mettre_a_jour_perception(cerveau, etat_monde)
                _analyser_spawn_progressif(cerveau, etat_monde)

        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Erreur séquence démarrage: {e}")

    cerveau_autonomie.forcer_mode_autonome(cerveau)
    logger.info("Séquence démarrage terminée - IA maintenant autonome")


def boucle_principale(cerveau):
    """Boucle principale d'orchestration IA avec autonomie complète."""
    logger.info("Boucle principale démarrée")

    derniere_evaluation_autonomie = time.time()

    while cerveau.running:
        try:
            cerveau_utils.gerer_commandes_mentor(cerveau)

            if time.time() - derniere_evaluation_autonomie > 10:
                cerveau_autonomie.evaluer_et_changer_mode(cerveau)
                derniere_evaluation_autonomie = time.time()

            try:
                etat_monde = cerveau.queues["jeu_vers_ia"].get(timeout=2.0)
                cerveau.progres_recent = time.time()
                cerveau_perception.mettre_a_jour_perception(cerveau, etat_monde)

            except queue.Empty:
                logger.debug("Aucun état monde reçu - continuation autonome")
                pass
            except Exception as e:
                logger.error(f"Erreur lecture état monde: {e}")

            cerveau_decision.cycle_decision_principal(cerveau)
            cerveau_actions.executer_actions_planifiees(cerveau)

            time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Interruption clavier détectée")
            break
        except Exception as e:
            logger.error(f"Erreur critique boucle principale: {e}")
            break

    logger.info("Boucle principale arrêtée")


def _analyser_spawn_progressif(cerveau, etat_monde):
    """Analyse progressive de l'environnement de spawn."""
    try:
        position_spawn = etat_monde.get("etat_joueur", {}).get("position", {})

        if position_spawn:
            cerveau.position_spawn = position_spawn

        entites_visibles = etat_monde.get("entites_proches", [])
        for entite in entites_visibles:
            cerveau_perception.cataloguer_entite_decouverte(cerveau, entite)

    except Exception as e:
        logger.error(f"Erreur analyse spawn: {e}")
