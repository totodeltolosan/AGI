# eve_src/core/physique.py
"""Centralise les formules physiques et mathématiques de la simulation."""


def calculer_degats(attaquant, defenseur):
    """
    Calcule les dégâts d'une attaque basés sur les gènes.
    Retourne l'énergie perdue par le défenseur.
    """
    puissance_attaque = attaquant.genome.data["social"]["agressivite"] * 20
    reduction_degats = defenseur.genome.data["physique"]["robustesse_defense"] * 10
    degats = puissance_attaque - reduction_degats
    return max(0, degats)
