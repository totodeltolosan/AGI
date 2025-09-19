# Fichier : agents_complexes.py
# Module des agents de complexité intermédiaire - Chimie stellaire, planétologie et structures galactiques

import logging
import random
from typing import TYPE_CHECKING, List

import numpy as np

from etatmonde import EtatMonde, Atome, Etoile, Planete, Galaxie, Particule

if TYPE_CHECKING:
    from etatmonde import EtatMonde

try:
    from scipy.spatial import cKDTree
except ImportError:
    cKDTree = None

logger = logging.getLogger(__name__)


class Chimiste:
    """Rôle : Maître de la Fusion Stellaire et des Supernovae"""

    def __init__(self):
        """Initialise les paramètres de fusion stellaire."""
        self.elements_forge = [
            "helium",
            "carbone",
            "oxygene",
            "neon",
            "magnesium",
            "silicium",
            "soufre",
            "calcium",
            "fer",
            "nickel",
        ]
        self.masse_critique_supernova = 800.0  # Seuil pour déclencher une supernova
        self.taux_fusion_base = 0.0001  # Taux de fusion très conservateur

    def chimiste(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Gère le cycle de vie des étoiles : fusion, évolution et supernovae."""
        etoiles: List[Etoile] = etatmonde.entites.get("etoiles", [])
        if not etoiles:
            return etatmonde

        etoiles_a_supernova = []
        nouveaux_atomes = []
        nouvelles_particules = []

        for etoile in etoiles:
            # Initialisation de l'inventaire si nécessaire
            if not hasattr(etoile, "inventaire_elements"):
                etoile.inventaire_elements = {
                    "hydrogene": etoile.masse * 0.73,  # Composition stellaire réaliste
                    "helium": etoile.masse * 0.25,
                }

            hydrogene_disponible = etoile.inventaire_elements.get("hydrogene", 0)

            # Fusion nucléaire progressive
            if hydrogene_disponible > 0:
                # Taux de fusion dépendant de la masse et température
                taux_base = self.taux_fusion_base
                facteur_masse = min(etoile.masse / 100, 10)  # Limitation facteur masse
                facteur_temperature = min(
                    etoile.temperature / 5000, 5
                )  # Limitation température

                taux_fusion = min(
                    hydrogene_disponible
                    * taux_base
                    * facteur_masse
                    * facteur_temperature,
                    hydrogene_disponible * 0.01,  # Maximum 1% par cycle
                )

                etoile.inventaire_elements["hydrogene"] -= taux_fusion

                # Création d'hélium (fusion principale)
                helium_produit = taux_fusion * 0.9  # Efficacité de fusion
                etoile.inventaire_elements["helium"] = (
                    etoile.inventaire_elements.get("helium", 0) + helium_produit
                )

                # Fusion d'éléments lourds pour les étoiles massives
                if etoile.masse > 200:  # Étoiles massives seulement
                    helium_disponible = etoile.inventaire_elements.get("helium", 0)

                    if (
                        helium_disponible > etoile.masse * 0.1
                    ):  # Seuil d'hélium pour fusion secondaire
                        taux_fusion_secondaire = (
                            taux_fusion * 0.1
                        )  # 10% du taux principal

                        for i, element in enumerate(
                            self.elements_forge[1:]
                        ):  # Skip hélium
                            if i < 6:  # Éléments légers à moyens
                                quantite = taux_fusion_secondaire * random.uniform(
                                    0.005, 0.02
                                )
                            else:  # Éléments lourds (fer, nickel)
                                quantite = taux_fusion_secondaire * random.uniform(
                                    0.001, 0.005
                                )

                            etoile.inventaire_elements[element] = (
                                etoile.inventaire_elements.get(element, 0) + quantite
                            )

                # Évolution thermique réaliste
                if taux_fusion > 0:
                    # Augmentation température proportionnelle mais limitée
                    augmentation_temp = (
                        taux_fusion / etoile.masse
                    ) * 50  # Facteur réduit
                    etoile.temperature = min(
                        etoile.temperature + augmentation_temp,
                        50000,  # Température max réaliste pour étoiles
                    )

                    # Luminosité suit température (loi Stefan-Boltzmann simplifiée)
                    facteur_luminosite = 1 + (taux_fusion / etoile.masse) * 0.001
                    etoile.luminosite = min(
                        etoile.luminosite * facteur_luminosite,
                        1000,  # Plafond luminosité
                    )

            # Vérification condition supernova
            hydrogene_epuise = hydrogene_disponible < etoile.masse * 0.02  # 2% restant
            masse_suffisante = etoile.masse > self.masse_critique_supernova

            if masse_suffisante and hydrogene_epuise:
                etoiles_a_supernova.append(etoile)

        # Traitement des supernovae
        for etoile in etoiles_a_supernova:
            logger.info(
                f"SUPERNOVA au Temps {etatmonde.temps}! "
                f"Étoile (Masse: {etoile.masse:.2f}, T: {etoile.temperature:.0f}K) explose."
            )

            # Éjection d'éléments avec distribution réaliste
            for element, quantite in etoile.inventaire_elements.items():
                if quantite > 0.1:  # Seuil minimum pour créer des atomes
                    # Nombre d'atomes limité pour la performance
                    nb_atomes = max(1, min(int(quantite / 15), 40))

                    for _ in range(nb_atomes):
                        # Direction aléatoire d'éjection
                        direction = np.random.randn(3)
                        direction = direction / np.linalg.norm(direction)

                        # Vitesse d'éjection variable selon l'élément
                        if element in ["fer", "nickel"]:  # Éléments lourds
                            vitesse = np.random.uniform(3, 8)
                        else:  # Éléments légers
                            vitesse = np.random.uniform(8, 20)

                        # Distance d'éjection
                        distance_ejection = np.random.uniform(0.5, 3.0)

                        nouvel_atome = Atome(
                            type=element,
                            masse=quantite / nb_atomes,
                            position=etoile.position + direction * distance_ejection,
                            vecteur=etoile.vecteur + direction * vitesse,
                        )
                        nouveaux_atomes.append(nouvel_atome)

            # Génération de particules énergétiques (limitée)
            nb_particules = min(int(etoile.masse / 80), 15)  # Très limité
            for _ in range(nb_particules):
                direction = np.random.randn(3)
                direction = direction / np.linalg.norm(direction)
                vitesse = np.random.uniform(15, 35)  # Particules rapides
                distance = np.random.uniform(0.2, 1.0)

                nouvelle_particule = Particule(
                    masse=np.random.uniform(0.05, 0.5),
                    position=etoile.position + direction * distance,
                    vecteur=etoile.vecteur + direction * vitesse,
                )
                nouvelles_particules.append(nouvelle_particule)

        # Mise à jour de l'état du monde
        if etoiles_a_supernova:
            # Retirer les étoiles qui ont explosé
            etatmonde.entites["etoiles"] = [
                e for e in etoiles if e not in etoiles_a_supernova
            ]

            # Ajouter les nouveaux atomes et particules
            etatmonde.entites["atomes"].extend(nouveaux_atomes)
            etatmonde.entites["particules"].extend(nouvelles_particules)

            # Enregistrement du palier
            if not any("PremiereSupernova" in p for p in etatmonde.paliers):
                etatmonde.paliers.append(
                    f"[Temps: {etatmonde.temps}] - PremiereSupernova"
                )

            logger.info(
                f"Supernova terminée : {len(nouveaux_atomes)} atomes et "
                f"{len(nouvelles_particules)} particules éjectés"
            )

        return etatmonde


class Planetologue:
    """Rôle : Architecte Planétaire"""

    def __init__(self):
        """Initialise les paramètres de formation planétaire."""
        self.rayon_detection_disque = 25.0
        self.masse_minimale_planete = 30.0  # Réduit pour plus de formations
        self.elements_planetaires = [
            "oxygene",
            "silicium",
            "fer",
            "carbone",
            "magnesium",
        ]

    def planetologue(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Forme des planètes à partir d'atomes lourds autour d'étoiles jeunes."""
        if cKDTree is None:
            return etatmonde

        etoiles: List[Etoile] = etatmonde.entites.get("etoiles", [])
        atomes: List[Atome] = etatmonde.entites.get("atomes", [])

        if not etoiles or not atomes:
            return etatmonde

        # Filtrer les atomes planétaires (éléments lourds)
        atomes_planetaires = [a for a in atomes if a.type in self.elements_planetaires]

        if len(atomes_planetaires) < self.masse_minimale_planete:
            return etatmonde

        positions_etoiles = np.array([e.position for e in etoiles])
        positions_atomes = np.array([a.position for a in atomes_planetaires])

        arbre_etoiles = cKDTree(positions_etoiles)
        arbre_atomes = cKDTree(positions_atomes)

        nouvelles_planetes = []
        indices_atomes_consommes = set()

        for i, etoile in enumerate(etoiles):
            # Conditions pour formation planétaire
            temperature_appropriee = 3000 <= etoile.temperature <= 8000
            masse_appropriee = (
                50 <= etoile.masse <= 1000
            )  # Ni trop petite ni trop massive

            if not (temperature_appropriee and masse_appropriee):
                continue

            # Chercher les atomes dans le disque d'accrétion
            indices_voisins = arbre_atomes.query_ball_point(
                etoile.position, r=self.rayon_detection_disque
            )

            # Filtrer les atomes non encore consommés
            atomes_candidats = [
                idx for idx in indices_voisins if idx not in indices_atomes_consommes
            ]

            if len(atomes_candidats) >= self.masse_minimale_planete:
                # Calculer propriétés de la future planète
                composition = {}
                masse_totale = 0
                position_moyenne = np.zeros(3)
                vecteur_moyen = np.zeros(3)

                for idx in atomes_candidats:
                    atome = atomes_planetaires[idx]
                    composition[atome.type] = (
                        composition.get(atome.type, 0) + atome.masse
                    )
                    masse_totale += atome.masse
                    position_moyenne += atome.position * atome.masse
                    vecteur_moyen += atome.vecteur * atome.masse
                    indices_atomes_consommes.add(idx)

                position_moyenne /= masse_totale
                vecteur_moyen /= masse_totale

                # Classification planétaire basée sur composition
                fer_ratio = composition.get("fer", 0) / masse_totale
                carbone_ratio = composition.get("carbone", 0) / masse_totale
                oxygene_ratio = composition.get("oxygene", 0) / masse_totale

                if fer_ratio > 0.3:
                    type_planete = "tellurique"
                elif carbone_ratio > 0.2:
                    type_planete = "riche_carbone"
                elif oxygene_ratio > 0.4:
                    type_planete = "riche_oxygene"
                else:
                    type_planete = "composite"

                # Calcul température planétaire réaliste
                distance_etoile = np.linalg.norm(position_moyenne - etoile.position)
                distance_etoile = max(distance_etoile, 1.0)  # Éviter division par zéro

                # Formule simplifiée de température d'équilibre
                temperature_planete = max(
                    50,  # Température minimale absolue
                    min(
                        (etoile.luminosite * 150) / (distance_etoile**1.5),
                        1000,  # Température maximale
                    ),
                )

                # Ajustement orbital pour stabilité
                vitesse_orbitale_ideale = np.sqrt(
                    etoile.masse * 0.001 / distance_etoile
                )
                direction_orbitale = np.cross(
                    position_moyenne - etoile.position,
                    [0, 0, 1],  # Axe z comme référence
                )
                if np.linalg.norm(direction_orbitale) > 0:
                    direction_orbitale = direction_orbitale / np.linalg.norm(
                        direction_orbitale
                    )
                    vecteur_orbital = direction_orbitale * vitesse_orbitale_ideale
                    vecteur_moyen = (vecteur_moyen + vecteur_orbital) / 2

                nouvelle_planete = Planete(
                    masse=masse_totale,
                    position=position_moyenne,
                    vecteur=vecteur_moyen,
                    type=type_planete,
                    composition=composition,
                    temperature=temperature_planete,
                    etoile_parente_id=str(etoile.id),
                )
                nouvelles_planetes.append(nouvelle_planete)

                logger.info(
                    f"Formation planétaire au Temps {etatmonde.temps}: "
                    f"Planète {type_planete} (Masse: {masse_totale:.2f}, "
                    f"T: {temperature_planete:.1f}K, Distance: {distance_etoile:.1f}) "
                    f"formée autour de l'étoile {str(etoile.id)[:8]}..."
                )

        # Mise à jour de l'état du monde
        if nouvelles_planetes:
            etatmonde.entites["planetes"].extend(nouvelles_planetes)

            # Retirer les atomes consommés de manière efficace
            atomes_planetaires_filtres = [
                a
                for i, a in enumerate(atomes_planetaires)
                if i not in indices_atomes_consommes
            ]

            # Reconstituer la liste complète d'atomes
            atomes_non_planetaires = [
                a for a in atomes if a.type not in self.elements_planetaires
            ]
            etatmonde.entites["atomes"] = (
                atomes_non_planetaires + atomes_planetaires_filtres
            )

            # Enregistrement du palier
            if not any("PremierePlanete" in p for p in etatmonde.paliers):
                etatmonde.paliers.append(
                    f"[Temps: {etatmonde.temps}] - PremierePlanete"
                )

        return etatmonde


class Galacticien:
    """Rôle : Organisateur de Structures Galactiques"""

    def __init__(self):
        """Initialise les paramètres de formation galactique."""
        self.seuil_etoiles_galaxie = 30  # Réduit pour faciliter formation
        self.rayon_galaxie = 80.0  # Réduit pour être plus réaliste
        self.cycles_formation = 500  # Plus fréquent que 1000

    def galacticien(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Détecte et forme des galaxies à partir d'amas d'étoiles."""
        # Opère périodiquement pour simuler l'échelle de temps galactique
        if etatmonde.temps % self.cycles_formation != 0:
            return etatmonde

        if cKDTree is None:
            return etatmonde

        etoiles: List[Etoile] = etatmonde.entites.get("etoiles", [])
        if len(etoiles) < self.seuil_etoiles_galaxie:
            return etatmonde

        positions_etoiles = np.array([e.position for e in etoiles])
        arbre_etoiles = cKDTree(positions_etoiles)

        indices_traitees = np.zeros(len(etoiles), dtype=bool)
        nouvelles_galaxies = []

        for i, etoile in enumerate(etoiles):
            if indices_traitees[i]:
                continue

            # Recherche des voisins stellaires
            indices_voisins = arbre_etoiles.query_ball_point(
                etoile.position, r=self.rayon_galaxie
            )

            if len(indices_voisins) >= self.seuil_etoiles_galaxie:
                # Marquer toutes ces étoiles comme traitées
                indices_traitees[indices_voisins] = True

                # Calculer propriétés galactiques
                etoiles_galaxie = [etoiles[idx] for idx in indices_voisins]
                masses = np.array([e.masse for e in etoiles_galaxie])
                positions = np.array([e.position for e in etoiles_galaxie])

                centre_de_masse = np.average(positions, weights=masses, axis=0)
                masse_totale = np.sum(masses)

                # Calcul du rayon effectif de la galaxie
                distances_centre = np.linalg.norm(positions - centre_de_masse, axis=1)
                rayon_effectif = np.percentile(distances_centre, 90)  # 90e percentile

                # Classification galactique simple
                ratio_forme = np.std(distances_centre) / np.mean(distances_centre)
                if ratio_forme < 0.3:
                    type_galaxie = "elliptique"
                elif ratio_forme > 0.7:
                    type_galaxie = "irreguliere"
                else:
                    type_galaxie = "spirale"

                nouvelle_galaxie = Galaxie(
                    centre_de_masse=centre_de_masse,
                    nombre_etoiles=len(etoiles_galaxie),
                    masse=masse_totale,
                    position=centre_de_masse,
                    rayon=rayon_effectif,
                    type_galaxie=type_galaxie,
                )
                nouvelles_galaxies.append(nouvelle_galaxie)

                logger.info(
                    f"Formation galactique au Temps {etatmonde.temps}: "
                    f"Nouvelle galaxie {type_galaxie} avec {len(etoiles_galaxie)} étoiles "
                    f"(Masse totale: {masse_totale:.2f}, Rayon: {rayon_effectif:.1f})"
                )

        if nouvelles_galaxies:
            etatmonde.entites["galaxies"].extend(nouvelles_galaxies)

            # Enregistrement du palier
            if not any("PremiereGalaxie" in p for p in etatmonde.paliers):
                etatmonde.paliers.append(
                    f"[Temps: {etatmonde.temps}] - PremiereGalaxie"
                )

        return etatmonde


class Astrophysicien:
    """Rôle : Formateur d'Étoiles (version optimisée)"""

    def __init__(self):
        """Initialise les paramètres de formation stellaire."""
        self.seuil_densite_atomes = 100  # Seuil réaliste
        self.rayon_effondrement = 4.0  # Rayon d'accrétion
        self.types_atomes_stellaires = [
            "hydrogene",
            "helium",
        ]  # Combustible stellaire principal

    def astrophysicien(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """
        Protocole de formation stellaire optimisé.
        Forme des étoiles à partir d'atomes d'hydrogène et d'hélium.
        """
        if cKDTree is None:
            return etatmonde

        atomes: List[Atome] = etatmonde.entites.get("atomes", [])

        # Filtrer les atomes utilisables pour formation stellaire
        atomes_stellaires = [
            a for a in atomes if a.type in self.types_atomes_stellaires
        ]

        if len(atomes_stellaires) < self.seuil_densite_atomes:
            return etatmonde

        positions = np.array([a.position for a in atomes_stellaires])
        arbre_positions = cKDTree(positions)

        # Recherche de voisinage pour chaque atome
        indices_voisins = arbre_positions.query_ball_point(
            positions, r=self.rayon_effondrement
        )

        indices_deja_traites = np.zeros(len(atomes_stellaires), dtype=bool)
        nouvelles_etoiles: List[Etoile] = []

        # Tri par densité décroissante
        densites = [len(voisins) for voisins in indices_voisins]
        ordre_traitement = np.argsort(densites)[::-1]  # Ordre décroissant

        for idx in ordre_traitement:
            if indices_deja_traites[idx]:
                continue

            voisins = indices_voisins[idx]
            if len(voisins) >= self.seuil_densite_atomes:
                # Marquer tous les voisins comme traités
                indices_deja_traites[voisins] = True

                # Collecter les atomes pour formation stellaire
                atomes_a_consommer = [atomes_stellaires[i] for i in voisins]

                # Calculs de formation
                masses = [a.masse for a in atomes_a_consommer]
                positions_atomes = [a.position for a in atomes_a_consommer]
                vecteurs_atomes = [a.vecteur for a in atomes_a_consommer]

                masse_totale = sum(masses)
                position_moyenne = np.average(positions_atomes, weights=masses, axis=0)
                vecteur_moyen = np.average(vecteurs_atomes, weights=masses, axis=0)

                # Classification stellaire selon masse
                if masse_totale > 600:
                    type_etoile = "supergéante"
                    temp_base = 8000
                elif masse_totale > 300:
                    type_etoile = "géante"
                    temp_base = 6000
                elif masse_totale > 150:
                    type_etoile = "etoile_moyenne"
                    temp_base = 5000
                else:
                    type_etoile = "naine"
                    temp_base = 3500

                # Propriétés stellaires réalistes
                temperature = temp_base + np.random.normal(0, 500)
                temperature = max(2000, min(temperature, 15000))  # Limites réalistes

                # Luminosité selon relation masse-luminosité
                luminosite = (masse_totale / 100) ** 3.5
                luminosite = max(0.1, min(luminosite, 100))  # Limites raisonnables

                nouvelle_etoile = Etoile(
                    type=type_etoile,
                    masse=masse_totale,
                    position=position_moyenne,
                    vecteur=vecteur_moyen,
                    temperature=temperature,
                    luminosite=luminosite,
                )

                # Initialiser composition stellaire
                nouvelle_etoile.inventaire_elements = {
                    "hydrogene": masse_totale * 0.73,
                    "helium": masse_totale * 0.25,
                    "elements_lourds": masse_totale * 0.02,
                }

                nouvelles_etoiles.append(nouvelle_etoile)

                logger.info(
                    f"Accrétion stellaire au Temps {etatmonde.temps}: "
                    f"Nouvelle étoile {type_etoile} (Masse: {masse_totale:.2f}, "
                    f"T: {temperature:.0f}K) formée à partir de {len(voisins)} atomes."
                )

        # Mise à jour de l'état du monde
        if nouvelles_etoiles:
            etatmonde.entites["etoiles"].extend(nouvelles_etoiles)

            # Retirer les atomes consommés de manière efficace
            ids_consommes = {
                atomes_stellaires[i].id
                for i, traite in enumerate(indices_deja_traites)
                if traite
            }

            # Garder tous les atomes non consommés
            etatmonde.entites["atomes"] = [
                a for a in atomes if a.id not in ids_consommes
            ]

            # Enregistrement du palier si première étoile
            if not any("PremiereEtoile" in p for p in etatmonde.paliers):
                etatmonde.paliers.append(f"[Temps: {etatmonde.temps}] - PremiereEtoile")

        return etatmonde
