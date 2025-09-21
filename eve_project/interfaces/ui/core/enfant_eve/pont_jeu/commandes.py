"""
Classes commandes IA vers Minetest (Directive 74).
Définit actions possibles du joueur IA.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class CommandeBase:
    """TODO: Add docstring."""
    type: str
    timestamp: float


@dataclass
    """TODO: Add docstring."""
class Avancer(CommandeBase):
    direction: str
    distance: float


    """TODO: Add docstring."""
@dataclass
class Tourner(CommandeBase):
    angle: float

    """TODO: Add docstring."""

@dataclass
class Sauter(CommandeBase):
    force: float = 1.0
        """TODO: Add docstring."""


@dataclass
class Creuser(CommandeBase):
    position: Dict[str, int]
        """TODO: Add docstring."""
    outil: Optional[str] = None


@dataclass
class Placer(CommandeBase):
    """TODO: Add docstring."""
    position: Dict[str, int]
    bloc_type: str


    """TODO: Add docstring."""
@dataclass
class Attaquer(CommandeBase):
    id_entite: str

    """TODO: Add docstring."""
        """TODO: Add docstring."""

@dataclass
class Utiliser(CommandeBase):
    id_objet: str
    position: Optional[Dict[str, int]] = None


class ExecuteurCommandes:
    def __init__(self, connexion):
        self.connexion = connexion

    def executer(self, commande):
        """Exécute commande via connexion Minetest."""
        try:
            commande_json = self._convertir_json(commande)
            success = self.connexion.envoyer_commande(commande_json)

            if not success:
                logger.warning(f"Échec exécution commande: {commande.type}")

        except Exception as e:
            logger.error(f"Erreur exécution commande: {e}")

    def _convertir_json(self, commande) -> Dict[str, Any]:
        """Convertit commande en format JSON Minetest."""
        if isinstance(commande, dict):
            return commande

        return {"action": commande.type, "parametres": commande.__dict__}