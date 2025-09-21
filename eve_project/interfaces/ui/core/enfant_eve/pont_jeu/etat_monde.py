"""
Structure état monde reçu de Minetest (Directive 75).
Définit format JSON standardisé.
"""

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class EtatJoueur:
    """TODO: Add docstring."""
    position: Dict[str, float]
    vie: int
    faim: int
    inventaire: Dict[str, int]
    orientation: float


@dataclass
    """TODO: Add docstring."""
class EntiteProche:
    id: str
    type: str
    position: Dict[str, float]
    distance: float
    proprietes: Dict[str, Any]


    """TODO: Add docstring."""
@dataclass
class BlocLocal:
    position: Dict[str, int]
    type: str
    resistance: float
    outils_requis: List[str]

    """TODO: Add docstring."""

@dataclass
class EtatMonde:
    timestamp: float
    etat_joueur: EtatJoueur
    entites_proches: List[EntiteProche]
    scan_local_3d: List[BlocLocal]
    evenements: List[Dict[str, Any]]

    @classmethod
    def depuis_json(cls, donnees: Dict[str, Any]) -> "EtatMonde":
        """Crée EtatMonde depuis données JSON."""
        return cls(
            timestamp=donnees.get("timestamp", 0.0),
            etat_joueur=EtatJoueur(**donnees.get("etat_joueur", {})),
            entites_proches=[
                EntiteProche(**e) for e in donnees.get("entites_proches", [])
            ],
            scan_local_3d=[BlocLocal(**b) for b in donnees.get("scan_local_3d", [])],
            evenements=donnees.get("evenements", []),
        )