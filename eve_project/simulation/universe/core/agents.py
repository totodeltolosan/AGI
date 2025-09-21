# Fichier : agents.py
# Point d'entrée principal - Importe tous les agents des modules spécialisés

"""
Module principal d'agents qui importe et expose toutes les classes d'agents
des modules spécialisés. Maintient la compatibilité avec l'architecture existante.
"""

import logging

# Importation de tous les agents depuis les modules spécialisés
from agents_physiques import MaitreTemps, CalculateurLois, Alchimiste, Archiviste

from agents_complexes import Chimiste, Planetologue, Galacticien, Astrophysicien

from agents_emergents import (
    Biologiste,
    Evolutif,
    Sociologue,
    PhysicienExotique,
    AnalysteCosmique,
)

logger = logging.getLogger(__name__)

# Exposition de toutes les classes pour compatibilité
__all__ = [
    # Agents physiques de base
    "MaitreTemps",
    "CalculateurLois",
    "Alchimiste",
    "Archiviste",
    # Agents de complexité intermédiaire
    "Chimiste",
    "Planetologue",
    "Galacticien",
    "Astrophysicien",
    # Agents d'émergence
    "Biologiste",
    "Evolutif",
    "Sociologue",
    "PhysicienExotique",
    "AnalysteCosmique",
]

# Log d'information sur l'architecture modulaire
logger.info("Module d'agents modulaire chargé - Architecture étendue disponible.")
logger.info(
    f"Agents disponibles : {len(__all__)} classes réparties sur 3 modules spécialisés."
)
