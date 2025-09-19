# eve_src/archetypes/entite.py
"""Définit la classe de base abstraite pour toute entité vivante."""
import uuid
from abc import ABC, abstractmethod
from PyQt6.QtGui import QColor
from eve_src.core.genetique import AdvancedGenome


class EntiteVivante(ABC):
    """Classe de base pour toutes les formes de vie dans EVE."""

    def __init__(self, x, y):
        self.id = uuid.uuid4()
        self.x, self.y = x, y
        self.age, self.energie = 0, 1.0
        self.genome: AdvancedGenome = None
        self.sante = "sain"
        self.couleur = QColor("magenta")
        self.phenotype: dict = {}

    @abstractmethod
    def vivre(self, env, pop_dict):
        """Méthode abstraite pour le cycle de vie d'une entité."""

    @property
    def est_mort(self):
        """Vérifie si l'entité doit être considérée comme morte."""
        return self.energie <= 0

    def __repr__(self):
        """Fournit une représentation textuelle claire de l'entité pour le débogage."""
        return (
            f"<{self.__class__.__name__} id={str(self.id)[:8]} "
            f"pos=({self.x}, {self.y}) energie={self.energie:.1f}>"
        )
