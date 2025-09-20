import math
import random
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class GenerateurStructures:
    """
    Générateur de structures architecturales selon différents styles.
    Respecte Directive 61 avec focus sur la génération uniquement.
    """

    def __init__(self):
        """TODO: Add docstring."""
        pass

    def generer_structure_symetrique(self, plan: Dict) -> List[Dict]:
        """Génère une structure parfaitement symétrique (phase enfance)."""
        try:
            blocs = []
            if "dimensions" not in plan:
                return blocs

            largeur, hauteur, profondeur = plan["dimensions"]
            materiaux = plan.get("materiaux_autorises", ["wood", "stone"])

            # Génération couche par couche pour apprentissage méthodique
            for y in range(hauteur):
                for x in range(largeur):
                    for z in range(profondeur):
                        # Sélection matériau selon règles simples
                        if y == 0:  # Fondations solides
                            materiau = "stone"
                        elif y == hauteur - 1 and hauteur > 1:  # Toit simple
                            materiau = "wood"
                        elif (
                            x == 0 or x == largeur - 1 or z == 0 or z == profondeur - 1
                        ):  # Murs
                            materiau = "cobblestone"
                        else:  # Intérieur libre (air)
                            continue

                        # Ajout du bloc principal
                        bloc = {
                            "position": [x, y, z],
                            "materiau": materiau,
                            "type": "structure",
                            "importance": "haute" if y == 0 else "normale",
                        }
                        blocs.append(bloc)

            return blocs

        except Exception as e:
            logger.error(f"Erreur génération symétrique: {e}")
            return []

    def generer_structure_variee(self, plan: Dict) -> List[Dict]:
        """Génère une structure avec expérimentation (phase adolescence)."""
        try:
            blocs = []
            if "dimensions" not in plan:
                return blocs

            largeur, hauteur, profondeur = plan["dimensions"]
            materiaux = plan.get("materiaux_autorises", ["wood", "stone", "brick"])
            forme = plan.get("forme", "rectangulaire")

            # Génération selon la forme choisie
            if forme == "L_shape":
                blocs.extend(
                    self._generer_forme_L(largeur, hauteur, profondeur, materiaux)
                )
            elif forme == "circulaire_approx":
                blocs.extend(
                    self._generer_forme_circulaire(
                        largeur, hauteur, profondeur, materiaux
                    )
                )
            elif forme == "spirale_simple":
                blocs.extend(
                    self._generer_forme_spirale(largeur, hauteur, profondeur, materiaux)
                )
            else:
                # Forme standard avec variations de matériaux
                blocs.extend(
                    self._generer_forme_standard_variee(
                        largeur, hauteur, profondeur, materiaux
                    )
                )

            # Ajout d'éléments décoratifs expérimentaux
            blocs.extend(self._ajouter_decorations_experimentales(blocs, plan))

            return blocs

        except Exception as e:
            logger.error(f"Erreur génération variée: {e}")
            return []

    def generer_structure_harmonieuse(self, plan: Dict) -> List[Dict]:
        """Génère une structure harmonieuse avec l'environnement (phase adulte)."""
        try:
            blocs = []
            if "dimensions" not in plan:
                return blocs

            largeur, hauteur, profondeur = plan["dimensions"]
            materiaux_adaptes = plan.get("materiaux_adaptes", ["wood", "stone"])
            architecture_type = plan.get("architecture_type", "standard")

            # Génération selon type architectural
            if architecture_type == "integration_arbres":
                blocs.extend(
                    self._generer_integration_organique(
                        largeur, hauteur, profondeur, materiaux_adaptes
                    )
                )
            elif architecture_type == "ventilation_naturelle":
                blocs.extend(
                    self._generer_architecture_climatique(
                        largeur, hauteur, profondeur, materiaux_adaptes
                    )
                )
            elif architecture_type == "resistance_alpine":
                blocs.extend(
                    self._generer_architecture_montagnarde(
                        largeur, hauteur, profondeur, materiaux_adaptes
                    )
                )
            else:
                blocs.extend(
                    self._generer_architecture_harmonieuse_standard(
                        largeur, hauteur, profondeur, materiaux_adaptes
                    )
                )

            # Optimisation éclairage naturel
            blocs.extend(
                self._optimiser_eclairage_naturel(blocs, largeur, hauteur, profondeur)
            )

            return blocs

        except Exception as e:
            logger.error(f"Erreur génération harmonieuse: {e}")
            return []

    def _generer_forme_L(
        self, largeur: int, hauteur: int, profondeur: int, materiaux: List[str]
    ) -> List[Dict]:
        """Génère une structure en forme de L."""
        blocs = []
        branche_horizontale = largeur // 2
        branche_verticale = profondeur // 2

        for y in range(hauteur):
            materiau = materiaux[y % len(materiaux)]  # Alternance matériaux par niveau

            # Branche horizontale du L
            for x in range(branche_horizontale):
                for z in range(2):  # Épaisseur de 2
                    blocs.append(
                        {
                            "position": [x, y, z],
                            "materiau": materiau,
                            "type": "branche_horizontale",
                            "importance": "structurelle",
                        }
                    )

            # Branche verticale du L
            for z in range(2, branche_verticale):
                for x in range(2):  # Épaisseur de 2
                    blocs.append(
                        {
                            "position": [x, y, z],
                            "materiau": materiau,
                            "type": "branche_verticale",
                            "importance": "structurelle",
                        }
                    )

        return blocs

    def _generer_forme_circulaire(
        self, largeur: int, hauteur: int, profondeur: int, materiaux: List[str]
    ) -> List[Dict]:
        """Génère une approximation circulaire."""
        blocs = []
        centre_x, centre_z = largeur // 2, profondeur // 2
        rayon = min(centre_x, centre_z) - 1

        for y in range(hauteur):
            materiau = materiaux[y % len(materiaux)]

            for x in range(largeur):
                for z in range(profondeur):
                    distance = math.sqrt((x - centre_x) ** 2 + (z - centre_z) ** 2)

                    # Créer un cercle avec variations (adolescence = imparfait)
                    variation = random.uniform(-0.5, 0.5)
                    if distance <= rayon + variation:
                        blocs.append(
                            {
                                "position": [x, y, z],
                                "materiau": materiau,
                                "type": "structure_circulaire",
                                "importance": (
                                    "decorative"
                                    if distance > rayon - 1
                                    else "structurelle"
                                ),
                            }
                        )

        return blocs

    def _generer_forme_spirale(
        self, largeur: int, hauteur: int, profondeur: int, materiaux: List[str]
    ) -> List[Dict]:
        """Génère une spirale simple ascendante."""
        blocs = []
        centre_x, centre_z = largeur // 2, profondeur // 2

        for y in range(hauteur):
            rayon = max(1, min(centre_x, centre_z) - y // 2)  # Spirale qui se resserre
            angle_step = (2 * math.pi) / max(8, rayon * 2)  # Pas angulaire
            materiau = materiaux[y % len(materiaux)]

            for i in range(int(2 * math.pi / angle_step)):
                angle = i * angle_step
                x = int(centre_x + rayon * math.cos(angle))
                z = int(centre_z + rayon * math.sin(angle))

                if 0 <= x < largeur and 0 <= z < profondeur:
                    blocs.append(
                        {
                            "position": [x, y, z],
                            "materiau": materiau,
                            "type": "spirale",
                            "importance": "artistique",
                        }
                    )

        return blocs

    def _generer_forme_standard_variee(
        self, largeur: int, hauteur: int, profondeur: int, materiaux: List[str]
    ) -> List[Dict]:
        """Génère une forme standard avec variations de matériaux."""
        blocs = []

        for y in range(hauteur):
            for x in range(largeur):
                for z in range(profondeur):
                    # Variation algorithme sélection matériau
                    if y == 0:  # Fondations
                        materiau = "stone"
                    elif y == hauteur - 1:  # Toit
                        materiau = random.choice(["wood", "brick", "clay"])
                    elif (
                        x == 0 or x == largeur - 1 or z == 0 or z == profondeur - 1
                    ):  # Murs
                        # Pattern expérimental matériaux
                        index_pattern = (x + z + y) % len(materiaux)
                        materiau = materiaux[index_pattern]
                    else:  # Intérieur - parfois décoré
                        if random.random() < 0.1:  # 10% chance décoration intérieure
                            materiau = random.choice(["glass", "wool"])
                        else:
                            continue  # Vide

                    blocs.append(
                        {
                            "position": [x, y, z],
                            "materiau": materiau,
                            "type": "structure_experimentale",
                            "importance": "normale",
                        }
                    )

        return blocs

    def _generer_integration_organique(
        self, largeur: int, hauteur: int, profondeur: int, materiaux: List[str]
    ) -> List[Dict]:
        """Génère une architecture qui s'intègre organiquement dans la nature."""
        blocs = []
        centre_x, centre_z = largeur // 2, profondeur // 2

        for y in range(hauteur):
            rayon_base = min(centre_x, centre_z) - 1
            rayon_niveau = max(1, rayon_base - y // 3)  # Rétrécissement progressif

            # Sélection matériau naturel selon niveau
            if y == 0:
                materiau_principal = "moss_stone"
            elif y < hauteur // 2:
                materiau_principal = materiaux[0] if materiaux else "wood"
            else:
                materiau_principal = (
                    "leaves" if "leaves" in materiaux else materiaux[-1]
                )

            # Forme organique avec variations naturelles
            for x in range(largeur):
                for z in range(profondeur):
                    distance = math.sqrt((x - centre_x) ** 2 + (z - centre_z) ** 2)

                    # Variation organique avec bruit naturel
                    variation = 0.3 * math.sin(x * 0.5) * math.cos(z * 0.5)
                    if distance <= rayon_niveau + variation:
                        blocs.append(
                            {
                                "position": [x, y, z],
                                "materiau": materiau_principal,
                                "type": "integration_organique",
                                "importance": "harmonisation_naturelle",
                            }
                        )

        return blocs

    def _generer_architecture_climatique(
        self, largeur: int, hauteur: int, profondeur: int, materiaux: List[str]
    ) -> List[Dict]:
        """Génère une architecture adaptée au climat chaud avec ventilation naturelle."""
        blocs = []

        for y in range(hauteur):
            for x in range(largeur):
                for z in range(profondeur):
                    # Murs avec ouvertures pour ventilation
                    if x == 0 or x == largeur - 1 or z == 0 or z == profondeur - 1:
                        # Créer des ouvertures régulières pour ventilation
                        if (y + x + z) % 3 == 0 and y > 0 and y < hauteur - 1:
                            continue  # Ouverture ventilation

                        materiau = (
                            "sandstone" if "sandstone" in materiaux else materiaux[0]
                        )
                        blocs.append(
                            {
                                "position": [x, y, z],
                                "materiau": materiau,
                                "type": "mur_ventile",
                                "importance": "climatique",
                            }
                        )

                    # Fondations et toit
                    elif y == 0 or y == hauteur - 1:
                        materiau = "brick" if "brick" in materiaux else materiaux[0]
                        blocs.append(
                            {
                                "position": [x, y, z],
                                "materiau": materiau,
                                "type": "structure_climatique",
                                "importance": "structurelle",
                            }
                        )

        return blocs

    def _generer_architecture_montagnarde(
        self, largeur: int, hauteur: int, profondeur: int, materiaux: List[str]
    ) -> List[Dict]:
        """Génère une architecture résistante aux conditions alpines."""
        blocs = []
        epaisseur_mur = 2  # Structure renforcée avec murs épais

        for y in range(hauteur):
            for x in range(largeur):
                for z in range(profondeur):
                    # Murs épais pour isolation
                    if (
                        x < epaisseur_mur
                        or x >= largeur - epaisseur_mur
                        or z < epaisseur_mur
                        or z >= profondeur - epaisseur_mur
                    ):

                        if y == 0:  # Fondations renforcées
                            materiau = "stone" if "stone" in materiaux else materiaux[0]
                        elif y < hauteur // 2:  # Murs principaux
                            materiau = (
                                "andesite" if "andesite" in materiaux else materiaux[0]
                            )
                        else:  # Partie haute
                            materiau = (
                                "iron_block"
                                if "iron_block" in materiaux
                                else materiaux[0]
                            )

                        blocs.append(
                            {
                                "position": [x, y, z],
                                "materiau": materiau,
                                "type": "architecture_alpine",
                                "importance": "resistance_climatique",
                            }
                        )

        return blocs

    def _generer_architecture_harmonieuse_standard(
        self, largeur: int, hauteur: int, profondeur: int, materiaux: List[str]
    ) -> List[Dict]:
        """Génère une architecture harmonieuse standard."""
        blocs = []
        centre_x, centre_z = largeur // 2, profondeur // 2

        for y in range(hauteur):
            for x in range(largeur):
                for z in range(profondeur):
                    # Distance du centre pour harmonie radiale
                    dist_centre = math.sqrt((x - centre_x) ** 2 + (z - centre_z) ** 2)
                    max_dist = math.sqrt(centre_x**2 + centre_z**2)
                    proportion_centre = (
                        1.0 - (dist_centre / max_dist) if max_dist > 0 else 1.0
                    )

                    # Sélection harmonieuse matériaux selon position
                    if y == 0:  # Fondations
                        materiau = materiaux[0] if materiaux else "stone"
                    elif dist_centre < 2:  # Centre - matériau noble
                        materiau = materiaux[-1] if len(materiaux) > 1 else materiaux[0]
                    elif proportion_centre > 0.6:  # Zone intermédiaire
                        materiau = (
                            materiaux[len(materiaux) // 2]
                            if len(materiaux) > 2
                            else materiaux[0]
                        )
                    else:  # Périphérie
                        materiau = materiaux[0]

                    blocs.append(
                        {
                            "position": [x, y, z],
                            "materiau": materiau,
                            "type": "architecture_harmonieuse",
                            "importance": "equilibre_global",
                        }
                    )

        return blocs

    def _ajouter_decorations_experimentales(
        self, blocs: List[Dict], plan: Dict
    ) -> List[Dict]:
        """Ajoute des décorations expérimentales typiques de l'adolescence."""
        decorations = []

        if not blocs:
            return decorations

        # Trouver le point le plus haut pour décorations
        max_y = max(bloc["position"][1] for bloc in blocs)
        positions_sommets = [
            bloc["position"] for bloc in blocs if bloc["position"][1] == max_y
        ]

        # Ajout expérimental de bannières/torches
        for i, pos in enumerate(positions_sommets[:3]):  # Max 3 décorations
            if random.random() < 0.6:  # 60% chance
                decorations.append(
                    {
                        "position": [pos[0], pos[1] + 1, pos[2]],
                        "materiau": "torch" if i % 2 == 0 else "banner",
                        "type": "decoration_experimentale",
                        "importance": "artistique",
                    }
                )

        return decorations

    def _optimiser_eclairage_naturel(
        self, blocs: List[Dict], largeur: int, hauteur: int, profondeur: int
    ) -> List[Dict]:
        """Optimise l'éclairage naturel en ajoutant des ouvertures strategiques."""
        eclairage = []

        # Ajouter fenêtres selon orientation optimale
        orientations_optimales = [
            (0, hauteur // 2, profondeur // 2),  # Ouest
            (largeur - 1, hauteur // 2, profondeur // 2),  # Est
            (largeur // 2, hauteur // 2, 0),  # Nord
            (largeur // 2, hauteur // 2, profondeur - 1),  # Sud
        ]

        for x, y, z in orientations_optimales:
            eclairage.append(
                {
                    "position": [x, y, z],
                    "materiau": "glass",
                    "type": "ouverture_eclairage",
                    "importance": "confort_lumineux",
                }
            )

        return eclairage