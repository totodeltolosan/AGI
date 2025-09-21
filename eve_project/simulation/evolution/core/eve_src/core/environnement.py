# eve_src/core/environnement.py
"""
Définit la classe Environnement.
Cette version est spécifiquement adaptée pour être compatible avec le moteur
de simulation existant, sans optimisations de grille spatiale.
"""
import random
from eve_src.config import CONFIG


class Environnement:
    """Gère le monde, ses cycles, son terrain, ses ressources et obstacles."""

    def __init__(self, taille):
        """Initialise l'environnement."""
        self.taille = taille
        self.ressources = set()
        self.obstacles = set()
        self.terrain = [[1.0 for _ in range(taille)] for _ in range(taille)]
        self.cadavres = {}
        self.saison = "Été"
        self.cycle_saisonnier = 0

        # NOTE : Les ressources technologiques sont prévues pour le futur
        self.bois = set()
        self.pierre = set()

        self.generer_monde()

    def generer_monde(self):
        """Génère les obstacles, le terrain et les ressources initiales."""
        # Génération des obstacles
        for _ in range(CONFIG["environnement"]["nombre_obstacles"]):
            t_obs = random.randint(2, CONFIG["environnement"]["taille_obstacle_max"])
            x_s, y_s = random.randint(0, self.taille - t_obs), random.randint(
                0, self.taille - t_obs
            )
            is_h = random.random() > 0.5
            for i in range(t_obs):
                self.obstacles.add((x_s + i, y_s) if is_h else (x_s, y_s + i))

        # Génération du terrain difficile
        if CONFIG["environnement"]["terrain_variable"]:
            for _ in range(int(self.taille / 3)):
                x_c, y_c = random.randint(0, self.taille - 1), random.randint(
                    0, self.taille - 1
                )
                radius = random.randint(int(self.taille / 25), int(self.taille / 10))
                for y in range(max(0, y_c - radius), min(self.taille, y_c + radius)):
                    for x in range(
                        max(0, x_c - radius), min(self.taille, x_c + radius)
                    ):
                        if (x, y) not in self.obstacles:
                            self.terrain[y][x] = CONFIG["environnement"][
                                "cout_mouvement_difficile"
                            ]

        # Génération des ressources de crafting (pour le futur)
        for _ in range(int((self.taille**2) * 0.005)):
            x, y = random.randint(0, self.taille - 1), random.randint(
                0, self.taille - 1
            )
            if (x, y) not in self.obstacles:
                self.bois.add((x, y))
        for _ in range(int((self.taille**2) * 0.005)):
            x, y = random.randint(0, self.taille - 1), random.randint(
                0, self.taille - 1
            )
            if (x, y) not in self.obstacles:
                self.pierre.add((x, y))

    def update_cycle(self):
        """Met à jour les cycles saisonniers et la décomposition."""
        if CONFIG["cycles_temporels"]["saisons_activees"]:
            d_saison = CONFIG["cycles_temporels"]["duree_saison"]
            self.cycle_saisonnier = (self.cycle_saisonnier + 1) % d_saison
            self.saison = "Été" if self.cycle_saisonnier < d_saison / 2 else "Hiver"

        # Décomposition des cadavres
        for pos in list(self.cadavres.keys()):
            self.cadavres[pos] -= 0.5
            if self.cadavres[pos] <= 0:
                del self.cadavres[pos]
