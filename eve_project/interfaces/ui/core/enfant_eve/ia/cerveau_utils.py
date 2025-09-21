"""
Utilitaires cerveau IA (Directive 23).
Gestion commandes mentor et interactions.
"""

import logging
import time
import queue
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def gerer_commandes_mentor(cerveau) -> None:
    """Gère les commandes provenant du mentor selon Directive 23."""
    try:
        while True:
            commande = cerveau.queues["mentor_vers_ia"].get_nowait()
            _executer_commande_mentor(cerveau, commande)
    except queue.Empty:
        pass
    except Exception as e:
        logger.error(f"Erreur gestion commandes mentor: {e}")

def _executer_commande_mentor(cerveau, commande: Dict[str, Any]) -> None:
    """Exécute une commande spécifique du mentor."""
    type_commande = commande.get("type", "")
    
    if type_commande == "interrogation":
        _traiter_interrogation(cerveau, commande)
    elif type_commande == "dilemme":
        _traiter_dilemme_ethique(cerveau, commande)
    elif type_commande == "evaluation":
        _generer_evaluation_autonome(cerveau)
    elif type_commande == "pause":
        _gerer_pause_ia(cerveau, commande)
    else:
        logger.warning(f"Commande mentor inconnue: {type_commande}")

def _traiter_interrogation(cerveau, commande: Dict[str, Any]) -> None:
    """Traite une interrogation directe du mentor."""
    question = commande.get("question", "")
    
    reponse = {
        "type": "reponse_interrogation",
        "question": question,
        "reponse": _generer_reponse_contextualisee(cerveau, question),
        "etat_interne": _capturer_etat_in