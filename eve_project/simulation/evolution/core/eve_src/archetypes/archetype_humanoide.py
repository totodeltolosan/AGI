# eve_src/archetypes/archetype_humanoide.py
"""
Définit l'archétype Humanoïde, capable d'intelligence supérieure,
d'utilisation d'outils et de modification de son environnement.
"""
from eve_src.config import CONFIG
from eve_src.archetypes.archetype_animal import Animal
from eve_src.core.physique import calculer_degats


class Humanoide(Animal):
    """
    Implémentation de l'archétype Humanoïde. Hérite de l'Animal mais y ajoute
    la technologie (inventaire, artisanat) et un potentiel d'intelligence accru.
    """

    def __init__(self, x, y, genome=None):
        """Initialise l'humanoïde, son génome spécialisé et son inventaire."""
        super().__init__(x, y, genome)

        # Spécialisation du génome pour l'humanoïde (si c'est une première génération)
        if genome is None:
            # Les humanoïdes ont un potentiel d'intelligence et de coopération plus élevé
            self.genome.data["cerveau"]["intelligence"] = [0.5]  # Gène de base
            self.genome.data["social"]["cooperation"] = [0.4]

        # ========================================================================
        # ===== FONDATIONS POUR LE FUTUR (TECHNOLOGIE) =====
        # ========================================================================
        self.inventaire = {"bois": 0, "pierre": 0}
        self.outils = []  # ex: "lance_en_pierre"
        # ========================================================================

    def vivre(self, env, pop_dict):
        """
        Le cycle de vie de l'humanoïde est plus complexe : il inclut la survie
        de base, mais aussi la collecte de matériaux et l'artisanat.
        """
        # D'abord, on exécute la logique de vie de base de l'Animal (déplacement, etc.)
        # Note : super().vivre() n'est pas appelé directement pour mieux contrôler la logique
        self.age += 1
        if self.en_gestation > 0:
            self.en_gestation -= 1
            if self.en_gestation == 0:
                return "naissance_humanoide", self.creer_enfant()

        # Le coût métabolique est plus élevé pour un cerveau plus complexe
        cout_cerveau = sum(
            abs(p) for row in self.genome.data["cerveau"]["poids"] for p in row
        )
        self.energie -= (
            cout_cerveau * CONFIG["genetique"]["cout_energie_par_poids_neuronal"] * 1.2
        )  # Taxe d'intelligence
        self.energie -= (
            CONFIG["evolution"]["cout_de_vie"] * self.genome.data["physique"]["taille"]
        )

        # --- Logique de décision et d'action ---
        perception = self.percevoir(env, pop_dict)
        action = self.decision_action(perception)

        if action < 5:  # Mouvements
            self._gerer_mouvement(action, env)
        elif action < 9:  # Attaques
            self._gerer_attaque(action, pop_dict)  # Utilise maintenant les outils

        # --- Logique spécifique à l'humanoïde ---
        self._gerer_collecte(env)
        self._gerer_artisanat()

        # L'alimentation est gérée comme un animal (omnivore par défaut)
        self._gerer_alimentation(env, pop_dict)
        return None

    def _gerer_collecte(self, env):
        """Ramasse les ressources technologiques sur sa case."""
        pos = (self.x, self.y)
        if pos in env.bois:
            self.inventaire["bois"] += 1
            env.bois.remove(pos)
        if pos in env.pierre:
            self.inventaire["pierre"] += 1
            env.pierre.remove(pos)

    def _gerer_artisanat(self):
        """Vérifie l'inventaire et fabrique des outils si possible."""
        # Recette simple pour une lance
        if (
            "lance_en_pierre" not in self.outils
            and self.inventaire["bois"] >= 2
            and self.inventaire["pierre"] >= 1
        ):
            self.inventaire["bois"] -= 2
            self.inventaire["pierre"] -= 1
            self.outils.append("lance_en_pierre")
            # POUR LE FUTUR : D'autres recettes pourraient être ajoutées ici
            # (hache, pioche, abri...)

    def _gerer_attaque(self, action, pop_dict):
        """Surcharge de la méthode d'attaque pour utiliser les outils."""
        if self.genome.data["alimentation"]["type"] == "herbivore":
            return

        self.energie -= CONFIG["predation"]["cout_attaque"]
        cibles = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = cibles[action - 5]
        cible_pos = (self.x + dx, self.y + dy)

        if cible_pos in pop_dict and isinstance(pop_dict[cible_pos], Animal):
            cible = pop_dict[cible_pos]
            if (
                cible.genome.data["social"]["id_tribu"]
                != self.genome.data["social"]["id_tribu"]
            ):

                # Le combat utilise la formule de base de `physique.py`
                degats = calculer_degats(self, cible)

                # MODIFIÉ : Les outils augmentent les dégâts
                if "lance_en_pierre" in self.outils:
                    degats *= 1.5

                cible.recevoir_degats(
                    degats
                )  # Utilise la nouvelle méthode standardisée

                if cible.est_mort:
                    self.energie += CONFIG["predation"]["gain_energie_predation"]

    # POUR LE FUTUR : de nouvelles méthodes surchargeront celles de l'Animal
    # def communiquer_complexe(self): ...
    # def construire(self, env): ...
