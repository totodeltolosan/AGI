# eve_src/archetypes/archetype_animal.py
"""Définit l'archétype Animal, qui exprime un phénotype complexe."""
from PyQt6.QtGui import QColor
from eve_src.config import CONFIG
from eve_src.archetypes.entite import EntiteVivante
from eve_src.core.genetique import AdvancedGenome
from eve_src.archetypes.archetype_vegetal import Vegetal
from eve_src.archetypes.archetype_insecte import Insecte
from eve_src.core.physique import calculer_degats


class Animal(EntiteVivante):
    """Implémentation de l'archétype Animal, piloté par un AdvancedGenome."""

    def __init__(self, x, y, genome: AdvancedGenome = None):
        """TODO: Add docstring."""
        super().__init__(x, y)
        self.energie = CONFIG["organisme"]["energie_initiale"]
        self.en_gestation = 0
        self.etat = "normal"
        self.genome = genome if genome else AdvancedGenome()
        self.phenotype = self.genome.get_phenotype()
        self.update_couleur()

    def update_couleur(self):
        """Met à jour la couleur en fonction du phénotype de la tribu."""
        tribu_id_gene = self.phenotype.get("social", {}).get(
            "tribu_id", [random.random(), 0.9, 1.0]
        )
        self.couleur = QColor.fromHsvF(*tribu_id_gene)

    def percevoir(self, env, pop_dict):
        """Construit le vecteur de perception pour le cerveau."""
        perception = []
        # ... (la logique de perception reste similaire mais doit être adaptée)
        # Pour la stabilité, nous laissons une perception simple pour l'instant
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = self.x + dx, self.y + dy
                pos = (nx, ny)
                is_food = pos in pop_dict and (
                    isinstance(pop_dict[pos], (Vegetal, Insecte))
                )
                perception.append(1.0 if pos in env.cadavres or is_food else 0.0)
                perception.append(1.0 if pos in env.obstacles else 0.0)
                if (
                    pos in pop_dict
                    and pop_dict[pos] is not self
                    and isinstance(pop_dict[pos], Animal)
                ):
                    perception.append(1.0)  # Voit un autre animal
                else:
                    perception.append(0.0)
        perception.append(1.0)
        return perception

    def decision_action(self, perception):
        """Calcule la sortie du réseau neuronal."""
        valeurs_sortie = [0.0] * CONFIG["cerveau"]["neurones_sortie"]
        brain_gene = self.genome.get_all_genes().get("cerveau_neural_network")
        if not brain_gene:
            return 4
        poids_plats = brain_gene.sequence
        num_entrees = CONFIG["cerveau"]["neurones_entree"]
        num_sorties = CONFIG["cerveau"]["neurones_sortie"]
        if len(poids_plats) < num_entrees * num_sorties:
            return 4
        poids = [
            poids_plats[i * num_sorties : (i + 1) * num_sorties]
            for i in range(num_entrees)
        ]
        for i, p_val in enumerate(perception):
            if p_val > 0 and i < len(poids):
                for j in range(num_sorties):
                    if j < len(poids[i]):
                        valeurs_sortie[j] += p_val * poids[i][j]
        return valeurs_sortie.index(max(valeurs_sortie))

    def vivre(self, env, pop_dict):
        """Exécute un cycle de vie basé sur le phénotype."""
        self.age += 1
        self.phenotype = self.genome.get_phenotype()  # Mise à jour du phénotype

        # Logique de vie simplifiée pour utiliser le phénotype
        vitesse = self.phenotype.get("physique", {}).get("vitesse", 1.0)
        cout_de_vie_pheno = CONFIG["evolution"]["cout_de_vie"] * self.phenotype.get(
            "physique", {}
        ).get("taille", 1.0)
        self.energie -= cout_de_vie_pheno

        perception = self.percevoir(env, pop_dict)
        action = self.decision_action(perception)

        if action < 5:
            mvt = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
            dx, dy = mvt[action]
            nx, ny = self.x + int(dx * vitesse), self.y + int(dy * vitesse)
            if (
                0 <= nx < env.taille
                and 0 <= ny < env.taille
                and (nx, ny) not in env.obstacles
            ):
                self.x, self.y = nx, ny

        if self.energie > CONFIG["evolution"]["seuil_reproduction"]:
            self.lancer_reproduction()
        return None

    def lancer_reproduction(self):
        """Initialise la reproduction."""
        self.etat = "cherche_partenaire"

    @property
    def est_mort(self):
        """La mort est déterminée par l'énergie et l'espérance de vie."""
        esperance_vie = self.phenotype.get("biologie", {}).get("esperance_vie", 1000)
        return self.energie <= 0 or self.age > esperance_vie