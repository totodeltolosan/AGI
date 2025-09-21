# eve_src/archetypes/archetype_vegetal.py
"""Définit l'archétype Végétal."""
import random
from PyQt6.QtGui import QColor
from eve_src.archetypes.entite import EntiteVivante
from eve_src.core.genetique import AdvancedGenome


class Vegetal(EntiteVivante):
    """Forme de vie statique qui génère de l'énergie par photosynthèse."""

    def __init__(self, x, y, genome=None):
        """TODO: Add docstring."""
        super().__init__(x, y)
        self.energie = random.uniform(10.0, 30.0)
        self.couleur = QColor("darkgreen")
        # MODIFIÉ : On crée un génome avancé et on le laisse s'initialiser
        self.genome = genome if genome else AdvancedGenome()
        self.phenotype = self.genome.get_phenotype()
        self.seuil_reproduction = 50

    def vivre(self, env, pop_dict):
        """Les végétaux font la photosynthèse et se reproduisent sur place."""
        gain_photosynthese = self.phenotype.get("physique", {}).get("metabolisme", 0.2)
        if env.saison == "Hiver":
            gain_photosynthese /= 4

        self.energie += gain_photosynthese
        self.age += 1

        if self.energie > self.seuil_reproduction:
            self.energie /= 2
            # On ne retourne plus de signal simple, on gère la reproduction ici
            # Pour l'instant, la reproduction des végétaux est désactivée
            # car elle nécessite une adaptation du moteur de simulation.

        return None

    @property
    def est_mort(self):
        """La mort est déterminée par l'énergie et l'espérance de vie."""
        esperance_vie = self.phenotype.get("biologie", {}).get("esperance_vie", 2000)
        return self.energie <= 0 or self.age > esperance_vie