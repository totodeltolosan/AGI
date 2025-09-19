# eve_src/archetypes/archetype_insecte.py
"""Définit l'archétype Insecte."""
import random
from PyQt6.QtGui import QColor
from eve_src.config import CONFIG
from eve_src.archetypes.entite import EntiteVivante
from eve_src.archetypes.archetype_vegetal import Vegetal
from eve_src.core.genetique import AdvancedGenome


class Insecte(EntiteVivante):
    """Forme de vie simple, mobile, herbivore et à reproduction rapide."""

    def __init__(self, x, y, genome=None):
        super().__init__(x, y)
        self.energie = 50
        self.couleur = QColor("gray")
        # MODIFIÉ : On crée un génome avancé
        self.genome = genome if genome else AdvancedGenome()
        self.phenotype = self.genome.get_phenotype()
        self.seuil_reproduction = 80

    def vivre(self, env, pop_dict):
        """Les insectes bougent aléatoirement, mangent des végétaux."""
        self.age += 1
        self.energie -= 0.5
        dx, dy = random.randint(-1, 1), random.randint(-1, 1)
        nx, ny = self.x + dx, self.y + dy
        if (
            0 <= nx < env.taille
            and 0 <= ny < env.taille
            and (nx, ny) not in env.obstacles
        ):
            self.x, self.y = nx, ny

        pos = (self.x, self.y)
        if pos in pop_dict and isinstance(pop_dict[pos], Vegetal):
            cible = pop_dict[pos]
            gain = CONFIG["evolution"]["gain_energie_vegetal"]
            energie_prise = min(cible.energie, gain)
            self.energie += energie_prise
            cible.energie -= energie_prise
        # La reproduction sera gérée par le moteur de simulation
        return None

    @property
    def est_mort(self):
        """La mort est déterminée par l'énergie et l'espérance de vie."""
        esperance_vie = self.phenotype.get("biologie", {}).get("esperance_vie", 200)
        return self.energie <= 0 or self.age > esperance_vie
