# Fichier : generateurmonde.py
# Version 9.0 ("Forge Cosmologique Robuste") - Générateur d'univers validé et optimisé.

"""
Module responsable de la création de l'état initial de l'univers.
Version robuste avec validation stricte, templates réutilisables et
architecture modulaire pour différents scénarios cosmologiques.
"""

import logging
import random
from typing import List, Dict, Optional, Tuple, Union, Any
from enum import Enum
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from etatmonde import EtatMonde, Particule, Atome, Etoile, Planete

logger = logging.getLogger(__name__)

# ========================================================================
# CONFIGURATION ET ÉNUMÉRATIONS
# ========================================================================


class TypeUnivers(Enum):
    """Énumération des différents types d'univers générables."""

    BIG_BANG_CLASSIQUE = "bigbang_classique"
    UNIVERS_MATURE = "univers_mature"
    LABORATOIRE_STELLAIRE = "laboratoire_stellaire"
    CHAOS_PRIMORDIAL = "chaos_primordial"
    UNIVERS_BIOPRET = "univers_biopret"
    LABORATOIRE_DENSE = "laboratoire_dense"  # Nouveau type pour plus d'interactions
    UNIVERS_VIDE = "univers_vide"  # Pour tests


class TypeDistribution(Enum):
    """Types de distributions spatiales disponibles."""

    UNIFORME = "uniforme"
    GAUSSIENNE = "gaussienne"
    COQUILLE = "coquille"
    AMAS = "amas"
    SPIRALE = "spirale"


@dataclass
class ParametresCosmologiques:
    """Paramètres physiques configurables avec validation automatique."""

    # Paramètres spatiaux
    rayon_initial: float = 10.0
    distribution_spatiale: TypeDistribution = TypeDistribution.UNIFORME

    # Paramètres énergétiques
    energie_cinetique_base: float = 0.1
    chaos_initial: float = 0.5
    facteur_expansion: float = 1e-5

    # Populations d'entités
    nombre_particules: int = 10000
    nombre_atomes: int = 0
    nombre_etoiles_initiales: int = 0
    nombre_planetes_initiales: int = 0

    # Paramètres de distribution des masses
    masse_log_mean: float = 0.0
    masse_log_sigma: float = 0.5
    masse_min: float = 0.01
    masse_max: float = 1000.0

    # Graine pour reproductibilité
    seed_aleatoire: Optional[int] = None

    def __post_init__(self):
        """Validation automatique des paramètres."""
        # Validation des valeurs physiques
        self.rayon_initial = max(1.0, min(self.rayon_initial, 1000.0))
        self.energie_cinetique_base = max(0.0, min(self.energie_cinetique_base, 10.0))
        self.chaos_initial = max(0.0, min(self.chaos_initial, 5.0))

        # Validation des populations
        self.nombre_particules = max(0, min(self.nombre_particules, 100000))
        self.nombre_atomes = max(0, min(self.nombre_atomes, 50000))
        self.nombre_etoiles_initiales = max(0, min(self.nombre_etoiles_initiales, 1000))
        self.nombre_planetes_initiales = max(
            0, min(self.nombre_planetes_initiales, 100)
        )

        # Validation des masses
        self.masse_min = max(1e-6, self.masse_min)
        self.masse_max = max(self.masse_min, min(self.masse_max, 1e6))

        logger.debug(f"Paramètres cosmologiques validés : {self}")


# ========================================================================
# VALIDATEURS ET UTILITAIRES
# ========================================================================


class ValidateurCosmologique:
    """Classe utilitaire pour valider les paramètres cosmologiques."""

    @staticmethod
    def valider_positions_non_collisions(
        positions: NDArray[np.float64], distance_min: float = 0.1
    ) -> NDArray[np.float64]:
        """
        Valide et corrige les positions pour éviter les collisions.

        Args:
            positions: Array des positions à valider
            distance_min: Distance minimale entre entités

        Returns:
            Positions corrigées
        """
        if len(positions) < 2:
            return positions

        positions_corrigees = positions.copy()

        # Vérification basique des collisions (algorithme simple)
        for i in range(len(positions_corrigees)):
            for j in range(i + 1, len(positions_corrigees)):
                distance = np.linalg.norm(
                    positions_corrigees[i] - positions_corrigees[j]
                )

                if distance < distance_min:
                    # Séparer les entités en collision
                    direction = positions_corrigees[i] - positions_corrigees[j]
                    if np.linalg.norm(direction) == 0:
                        direction = np.random.randn(3)

                    direction = direction / np.linalg.norm(direction)
                    deplacement = direction * (distance_min - distance) / 2

                    positions_corrigees[i] += deplacement
                    positions_corrigees[j] -= deplacement

        return positions_corrigees

    @staticmethod
    def valider_coherence_physique(
        masses: NDArray[np.float64],
        positions: NDArray[np.float64],
        vecteurs: NDArray[np.float64],
    ) -> Tuple[bool, List[str]]:
        """
        Valide la cohérence physique d'un ensemble d'entités.

        Returns:
            Tuple[bool, List[str]]: (Validité, Liste des erreurs)
        """
        erreurs = []

        # Vérification des arrays
        if not (len(masses) == len(positions) == len(vecteurs)):
            erreurs.append("Tailles d'arrays incohérentes")

        # Vérification valeurs physiques
        if np.any(masses <= 0):
            erreurs.append("Masses négatives ou nulles détectées")

        if np.any(~np.isfinite(positions)):
            erreurs.append("Positions invalides (NaN/Inf) détectées")

        if np.any(~np.isfinite(vecteurs)):
            erreurs.append("Vecteurs invalides (NaN/Inf) détectés")

        # Vérification conservation d'énergie approximative
        energie_totale = np.sum(0.5 * masses * np.sum(vecteurs**2, axis=1))
        if not np.isfinite(energie_totale):
            erreurs.append("Énergie totale invalide")

        return len(erreurs) == 0, erreurs


# ========================================================================
# GÉNÉRATEURS DE DISTRIBUTIONS
# ========================================================================


class GenerateurDistributions:
    """Générateur de distributions spatiales et de masses optimisé."""

    @staticmethod
    def generer_masses_realistes(
        nombre: int, params: ParametresCosmologiques
    ) -> NDArray[np.float64]:
        """
        Génère une distribution de masses réaliste et validée.

        Args:
            nombre: Nombre de masses à générer
            params: Paramètres cosmologiques

        Returns:
            Array numpy des masses validées
        """
        if nombre <= 0:
            return np.array([])

        # Distribution stratifiée réaliste
        nb_primaires = int(nombre * 0.75)  # Particules normales
        nb_lourdes = int(nombre * 0.20)  # Futures graines stellaires
        nb_legeres = nombre - nb_primaires - nb_lourdes  # Rayonnement

        # Génération par strates
        masses_primaires = np.random.lognormal(
            mean=params.masse_log_mean, sigma=params.masse_log_sigma, size=nb_primaires
        )

        masses_lourdes = np.random.lognormal(
            mean=params.masse_log_mean + 1.5,
            sigma=params.masse_log_sigma * 0.8,
            size=nb_lourdes,
        )

        masses_legeres = np.random.exponential(
            scale=params.masse_min * 10, size=nb_legeres
        )

        # Combinaison et validation
        masses_combinees = np.concatenate(
            [masses_primaires, masses_lourdes, masses_legeres]
        )

        # Application des limites physiques
        masses_validees = np.clip(masses_combinees, params.masse_min, params.masse_max)

        # Mélange aléatoire
        np.random.shuffle(masses_validees)

        logger.debug(
            f"Masses générées - Moyenne: {np.mean(masses_validees):.3f}, "
            f"Écart-type: {np.std(masses_validees):.3f}, "
            f"Min: {np.min(masses_validees):.3f}, Max: {np.max(masses_validees):.3f}"
        )

        return masses_validees

    @staticmethod
    def generer_positions_avancees(
        nombre: int,
        rayon: float,
        distribution: TypeDistribution,
        eviter_positions: Optional[NDArray[np.float64]] = None,
    ) -> NDArray[np.float64]:
        """
        Génère des positions selon différents modèles avec anti-collision.

        Args:
            nombre: Nombre de positions
            rayon: Rayon de la région
            distribution: Type de distribution spatiale
            eviter_positions: Positions à éviter (optionnel)

        Returns:
            Array numpy des positions 3D validées
        """
        if nombre <= 0:
            return np.array([]).reshape(0, 3)

        if distribution == TypeDistribution.UNIFORME:
            positions = GenerateurDistributions._positions_uniformes(nombre, rayon)
        elif distribution == TypeDistribution.GAUSSIENNE:
            positions = GenerateurDistributions._positions_gaussiennes(nombre, rayon)
        elif distribution == TypeDistribution.COQUILLE:
            positions = GenerateurDistributions._positions_coquille(nombre, rayon)
        elif distribution == TypeDistribution.AMAS:
            positions = GenerateurDistributions._positions_amas(nombre, rayon)
        elif distribution == TypeDistribution.SPIRALE:
            positions = GenerateurDistributions._positions_spirale(nombre, rayon)
        else:
            logger.warning(
                f"Distribution inconnue {distribution}, utilisation uniforme"
            )
            positions = GenerateurDistributions._positions_uniformes(nombre, rayon)

        # Anti-collision avec positions existantes
        if eviter_positions is not None and len(eviter_positions) > 0:
            positions = GenerateurDistributions._eviter_collisions(
                positions, eviter_positions, rayon * 0.1
            )

        return positions

    @staticmethod
    def _positions_uniformes(nombre: int, rayon: float) -> NDArray[np.float64]:
        """Distribution uniforme dans une sphère."""
        positions = np.random.randn(nombre, 3)
        normes = np.linalg.norm(positions, axis=1, keepdims=True)
        normes[normes == 0] = 1
        rayons_aleatoires = np.power(np.random.rand(nombre, 1), 1 / 3)
        return positions / normes * rayons_aleatoires * rayon

    @staticmethod
    def _positions_gaussiennes(nombre: int, rayon: float) -> NDArray[np.float64]:
        """Distribution gaussienne concentrée au centre."""
        return np.random.normal(0, rayon / 3, (nombre, 3))

    @staticmethod
    def _positions_coquille(nombre: int, rayon: float) -> NDArray[np.float64]:
        """Distribution sur une coquille sphérique."""
        positions = np.random.randn(nombre, 3)
        normes = np.linalg.norm(positions, axis=1, keepdims=True)
        normes[normes == 0] = 1
        return positions / normes * rayon

    @staticmethod
    def _positions_amas(nombre: int, rayon: float) -> NDArray[np.float64]:
        """Distribution en amas multiples."""
        nb_amas = min(nombre // 50, 10)  # 1 amas pour 50 entités, max 10
        positions_finales = []

        for _ in range(nb_amas):
            centre_amas = np.random.uniform(-rayon, rayon, 3)
            rayon_amas = rayon / (nb_amas * 2)
            nb_dans_amas = nombre // nb_amas

            positions_amas = np.random.normal(0, rayon_amas, (nb_dans_amas, 3))
            positions_amas += centre_amas
            positions_finales.append(positions_amas)

        # Ajouter entités restantes
        restantes = nombre - sum(len(p) for p in positions_finales)
        if restantes > 0:
            positions_extra = np.random.uniform(-rayon, rayon, (restantes, 3))
            positions_finales.append(positions_extra)

        return np.vstack(positions_finales)

    @staticmethod
    def _positions_spirale(nombre: int, rayon: float) -> NDArray[np.float64]:
        """Distribution en spirale pour structures galactiques précoces."""
        positions = []

        for i in range(nombre):
            # Angle et rayon en spirale
            angle = i * 0.1  # Pas angulaire
            r = (i / nombre) * rayon

            # Coordonnées spirale + variation z
            x = r * np.cos(angle) + np.random.normal(0, rayon * 0.05)
            y = r * np.sin(angle) + np.random.normal(0, rayon * 0.05)
            z = np.random.normal(0, rayon * 0.1)

            positions.append([x, y, z])

        return np.array(positions)

    @staticmethod
    def _eviter_collisions(
        nouvelles_positions: NDArray[np.float64],
        positions_existantes: NDArray[np.float64],
        distance_min: float,
    ) -> NDArray[np.float64]:
        """Évite les collisions avec des positions existantes."""
        positions_corrigees = nouvelles_positions.copy()

        for i, pos in enumerate(positions_corrigees):
            distances = np.linalg.norm(positions_existantes - pos, axis=1)

            if np.any(distances < distance_min):
                # Déplacer vers une zone libre
                tentatives = 0
                while tentatives < 10:  # Limite les tentatives
                    direction_aleatoire = np.random.randn(3)
                    direction_aleatoire /= np.linalg.norm(direction_aleatoire)

                    nouvelle_pos = pos + direction_aleatoire * distance_min * 2
                    nouvelles_distances = np.linalg.norm(
                        positions_existantes - nouvelle_pos, axis=1
                    )

                    if np.all(nouvelles_distances >= distance_min):
                        positions_corrigees[i] = nouvelle_pos
                        break

                    tentatives += 1

        return positions_corrigees


# ========================================================================
# TEMPLATES D'UNIVERS
# ========================================================================


class TemplatesUnivers:
    """Templates prédéfinis pour différents types d'univers."""

    @staticmethod
    def obtenir_template(type_univers: TypeUnivers) -> ParametresCosmologiques:
        """
        Retourne les paramètres prédéfinis pour un type d'univers.

        Args:
            type_univers: Type d'univers désiré

        Returns:
            Paramètres cosmologiques configurés
        """
        params = ParametresCosmologiques()

        if type_univers == TypeUnivers.BIG_BANG_CLASSIQUE:
            # Configuration standard équilibrée
            params.nombre_particules = 10000
            params.rayon_initial = 10.0
            params.energie_cinetique_base = 0.1
            params.chaos_initial = 0.5

        elif type_univers == TypeUnivers.UNIVERS_MATURE:
            # Univers avec structures préexistantes
            params.nombre_particules = 8000
            params.nombre_atomes = 1000
            params.nombre_etoiles_initiales = 5
            params.rayon_initial = 15.0
            params.energie_cinetique_base = 0.08

        elif type_univers == TypeUnivers.LABORATOIRE_STELLAIRE:
            # Optimisé pour formation stellaire rapide
            params.nombre_particules = 3000
            params.nombre_atomes = 2000
            params.nombre_etoiles_initiales = 10
            params.rayon_initial = 12.0
            params.distribution_spatiale = TypeDistribution.AMAS

        elif type_univers == TypeUnivers.CHAOS_PRIMORDIAL:
            # Chaos énergétique maximal
            params.nombre_particules = 15000
            params.energie_cinetique_base = 0.3
            params.chaos_initial = 2.0
            params.rayon_initial = 8.0

        elif type_univers == TypeUnivers.UNIVERS_BIOPRET:
            # Prêt pour émergence de la vie
            params.nombre_particules = 5000
            params.nombre_atomes = 1500
            params.nombre_etoiles_initiales = 8
            params.nombre_planetes_initiales = 3
            params.rayon_initial = 25.0
            params.distribution_spatiale = TypeDistribution.AMAS

        elif type_univers == TypeUnivers.LABORATOIRE_DENSE:
            # Pour plus d'interactions
            params.nombre_particules = 25000
            params.nombre_atomes = 3000
            params.rayon_initial = 8.0  # Plus compact = plus d'interactions
            params.energie_cinetique_base = 0.15
            params.distribution_spatiale = TypeDistribution.AMAS

        elif type_univers == TypeUnivers.UNIVERS_VIDE:
            # Pour tests et développement
            params.nombre_particules = 100
            params.rayon_initial = 5.0
            params.energie_cinetique_base = 0.05

        logger.info(
            f"Template '{type_univers.value}' configuré : {params.nombre_particules} particules"
        )
        return params


# ========================================================================
# GÉNÉRATEURS D'ENTITÉS SPÉCIALISÉS
# ========================================================================


class GenerateurEntites:
    """Générateur d'entités spécialisé avec validation automatique."""

    @staticmethod
    def creer_particules(
        nombre: int,
        positions: NDArray[np.float64],
        masses: NDArray[np.float64],
        vecteurs: NDArray[np.float64],
    ) -> List[Particule]:
        """
        Crée une liste de particules avec validation complète.

        Args:
            nombre: Nombre de particules à créer
            positions: Positions validées
            masses: Masses validées
            vecteurs: Vecteurs de vitesse validés

        Returns:
            Liste des particules créées
        """
        # Validation préalable
        coherent, erreurs = ValidateurCosmologique.valider_coherence_physique(
            masses, positions, vecteurs
        )

        if not coherent:
            logger.error(f"Création particules abandonnée : {erreurs}")
            return []

        particules = []
        for i in range(min(nombre, len(positions))):
            try:
                particule = Particule(
                    masse=float(masses[i]),
                    position=positions[i].copy(),
                    vecteur=vecteurs[i].copy(),
                )
                particules.append(particule)
            except Exception as e:
                logger.warning(f"Échec création particule {i}: {e}")

        logger.info(f"{len(particules)} particules créées avec succès")
        return particules

    @staticmethod
    def creer_atomes_preformes(
        nombre: int,
        rayon_zone: float,
        positions_evitees: Optional[NDArray[np.float64]] = None,
    ) -> List[Atome]:
        """
        Crée des atomes préformés pour univers avancés.

        Args:
            nombre: Nombre d'atomes à créer
            rayon_zone: Rayon de la zone de création
            positions_evitees: Positions à éviter

        Returns:
            Liste des atomes créés
        """
        if nombre <= 0:
            return []

        # Types d'atomes avec probabilités réalistes
        types_atomes = ["hydrogene", "helium", "carbone", "oxygene", "fer", "silicium"]
        probabilites = [0.4, 0.3, 0.1, 0.1, 0.05, 0.05]

        positions_atomes = GenerateurDistributions.generer_positions_avancees(
            nombre, rayon_zone, TypeDistribution.GAUSSIENNE, positions_evitees
        )

        # Masses selon type d'atome
        atomes = []
        for i in range(nombre):
            type_atome = np.random.choice(types_atomes, p=probabilites)

            # Masse caractéristique selon le type
            masse_base = {
                "hydrogene": 1.0,
                "helium": 4.0,
                "carbone": 12.0,
                "oxygene": 16.0,
                "fer": 56.0,
                "silicium": 28.0,
            }.get(type_atome, 1.0)

            masse_atome = masse_base * np.random.lognormal(0, 0.2)
            vecteur_atome = np.random.normal(0, 0.02, 3)  # Mouvement lent

            try:
                atome = Atome(
                    type=type_atome,
                    masse=masse_atome,
                    position=positions_atomes[i].copy(),
                    vecteur=vecteur_atome,
                )
                atomes.append(atome)
            except Exception as e:
                logger.warning(f"Échec création atome {i}: {e}")

        logger.info(f"{len(atomes)} atomes préformés créés")
        return atomes

    @staticmethod
    def creer_etoiles_initiales(
        nombre: int,
        rayon_zone: float,
        positions_evitees: Optional[NDArray[np.float64]] = None,
    ) -> List[Etoile]:
        """
        Crée des étoiles initiales pour univers matures.

        Args:
            nombre: Nombre d'étoiles à créer
            rayon_zone: Rayon de la zone de création
            positions_evitees: Positions à éviter

        Returns:
            Liste des étoiles créées
        """
        if nombre <= 0:
            return []

        positions_etoiles = GenerateurDistributions.generer_positions_avancees(
            nombre, rayon_zone, TypeDistribution.COQUILLE, positions_evitees
        )

        etoiles = []
        for i in range(nombre):
            # Propriétés stellaires réalistes
            masse_etoile = np.random.lognormal(mean=4.0, sigma=1.0)

            # Température selon masse (relation masse-température simplifiée)
            temperature_base = 3000 + masse_etoile * 20
            temperature = max(2000, temperature_base + np.random.normal(0, 500))

            # Luminosité selon relation masse-luminosité
            luminosite = (masse_etoile / 100) ** 3.5
            luminosite = max(0.1, min(luminosite, 1000))

            # Classification automatique par masse
            if masse_etoile > 500:
                type_etoile = "supergeante"
            elif masse_etoile > 200:
                type_etoile = "geante"
            elif masse_etoile > 50:
                type_etoile = "etoile_moyenne"
            else:
                type_etoile = "naine"

            # Mouvement orbital léger
            vecteur_orbital = np.random.normal(0, 0.05, 3)

            try:
                etoile = Etoile(
                    type=type_etoile,
                    masse=masse_etoile,
                    position=positions_etoiles[i].copy(),
                    vecteur=vecteur_orbital,
                    temperature=temperature,
                    luminosite=luminosite,
                )

                # Initialisation composition stellaire réaliste
                etoile.inventaire_elements = {
                    "hydrogene": masse_etoile * 0.73,
                    "helium": masse_etoile * 0.25,
                    "elements_lourds": masse_etoile * 0.02,
                }

                etoiles.append(etoile)

            except Exception as e:
                logger.warning(f"Échec création étoile {i}: {e}")

        logger.info(f"{len(etoiles)} étoiles initiales créées")
        return etoiles


# ========================================================================
# GÉNÉRATEUR PRINCIPAL
# ========================================================================


class ForgeCosmologique:
    """Générateur principal d'univers avec architecture modulaire."""

    def __init__(self, params: Optional[ParametresCosmologiques] = None):
        """Initialise la forge avec paramètres validés."""
        self.params = params or ParametresCosmologiques()
        self.statistiques_generation = {
            "entites_creees": 0,
            "erreurs_creation": 0,
            "temps_generation": 0.0,
        }

    def generer_univers(self, type_univers: TypeUnivers) -> EtatMonde:
        """
        Génère un univers complet selon le type spécifié.

        Args:
            type_univers: Type d'univers à créer

        Returns:
            EtatMonde: Univers nouvellement créé
        """
        import time

        temps_debut = time.time()

        logger.info(f"Forge cosmologique : génération '{type_univers.value}'")

        # Configuration des paramètres selon template
        self.params = TemplatesUnivers.obtenir_template(type_univers)

        # Initialisation graine aléatoire si spécifiée
        if self.params.seed_aleatoire is not None:
            np.random.seed(self.params.seed_aleatoire)
            random.seed(self.params.seed_aleatoire)
            logger.info(f"Graine aléatoire fixée : {self.params.seed_aleatoire}")

        # Création de l'univers vide
        nouveau_monde = EtatMonde()

        # Phase 1 : Génération des particules fondamentales
        if self.params.nombre_particules > 0:
            self._generer_particules_primordiales(nouveau_monde)

        # Phase 2 : Génération d'atomes préformés
        if self.params.nombre_atomes > 0:
            self._generer_atomes_preformes(nouveau_monde)

        # Phase 3 : Génération d'étoiles initiales
        if self.params.nombre_etoiles_initiales > 0:
            self._generer_etoiles_initiales(nouveau_monde)

        # Phase 4 : Génération de planètes initiales
        if self.params.nombre_planetes_initiales > 0:
            self._generer_planetes_initiales(nouveau_monde)

        # Configuration finale
        self._configurer_univers_final(nouveau_monde, type_univers)

        # Métriques finales
        temps_generation = time.time() - temps_debut
        self.statistiques_generation["temps_generation"] = temps_generation

        total_entites = sum(len(cat) for cat in nouveau_monde.entites.values())
        logger.info(
            f"Univers '{type_univers.value}' généré en {temps_generation:.2f}s : "
            f"{total_entites} entités créées"
        )

        return nouveau_monde

    def _generer_particules_primordiales(self, monde: EtatMonde) -> None:
        """Génère les particules fondamentales de l'univers."""
        logger.info(
            f"Génération de {self.params.nombre_particules} particules primordiales"
        )

        # Génération des propriétés physiques
        positions = GenerateurDistributions.generer_positions_avancees(
            self.params.nombre_particules,
            self.params.rayon_initial,
            self.params.distribution_spatiale,
        )

        masses = GenerateurDistributions.generer_masses_realistes(
            self.params.nombre_particules, self.params
        )

        # Vecteurs avec expansion + chaos
        vecteurs_expansion = positions * self.params.energie_cinetique_base
        vecteurs_chaos = np.random.randn(self.params.nombre_particules, 3) * (
            self.params.chaos_initial * self.params.energie_cinetique_base
        )
        vecteurs = vecteurs_expansion + vecteurs_chaos

        # Validation anti-collision
        positions = ValidateurCosmologique.valider_positions_non_collisions(positions)

        # Création des entités
        particules = GenerateurEntites.creer_particules(
            self.params.nombre_particules, positions, masses, vecteurs
        )

        monde.entites["particules"] = particules
        self.statistiques_generation["entites_creees"] += len(particules)

    def _generer_atomes_preformes(self, monde: EtatMonde) -> None:
        """Génère des atomes préformés pour univers avancés."""
        logger.info(f"Génération de {self.params.nombre_atomes} atomes préformés")

        # Éviter collisions avec particules existantes
        positions_existantes = None
        if monde.entites["particules"]:
            positions_existantes = np.array(
                [p.position for p in monde.entites["particules"]]
            )

        atomes = GenerateurEntites.creer_atomes_preformes(
            self.params.nombre_atomes,
            self.params.rayon_initial * 1.2,
            positions_existantes,
        )

        monde.entites["atomes"] = atomes
        self.statistiques_generation["entites_creees"] += len(atomes)

    def _generer_etoiles_initiales(self, monde: EtatMonde) -> None:
        """Génère des étoiles initiales pour univers matures."""
        logger.info(
            f"Génération de {self.params.nombre_etoiles_initiales} étoiles initiales"
        )

        # Éviter collisions avec entités existantes
        positions_existantes = []
        for categorie in ["particules", "atomes"]:
            if monde.entites[categorie]:
                positions_existantes.extend(
                    [e.position for e in monde.entites[categorie]]
                )

        positions_existantes_array = (
            np.array(positions_existantes) if positions_existantes else None
        )

        etoiles = GenerateurEntites.creer_etoiles_initiales(
            self.params.nombre_etoiles_initiales,
            self.params.rayon_initial * 1.5,
            positions_existantes_array,
        )

        monde.entites["etoiles"] = etoiles
        self.statistiques_generation["entites_creees"] += len(etoiles)

    def _generer_planetes_initiales(self, monde: EtatMonde) -> None:
        """Génère des planètes initiales pour univers bio-prêts."""
        logger.info(
            f"Génération de {self.params.nombre_planetes_initiales} planètes initiales"
        )

        etoiles_disponibles = monde.entites.get("etoiles", [])
        if not etoiles_disponibles:
            logger.warning("Impossible de créer des planètes sans étoiles parentes")
            return

        planetes = []
        nombre_max = min(
            self.params.nombre_planetes_initiales, len(etoiles_disponibles)
        )

        for i in range(nombre_max):
            etoile_parente = etoiles_disponibles[i]

            try:
                planete = self._creer_planete_orbitale(etoile_parente)
                planetes.append(planete)
            except Exception as e:
                logger.warning(f"Échec création planète {i}: {e}")

        monde.entites["planetes"] = planetes
        self.statistiques_generation["entites_creees"] += len(planetes)

    def _creer_planete_orbitale(self, etoile_parente: Etoile) -> Planete:
        """Crée une planète en orbite stable autour d'une étoile."""
        # Paramètres orbitaux réalistes
        distance_orbitale = np.random.uniform(8, 25)
        angle_orbital = np.random.uniform(0, 2 * np.pi)
        inclinaison = np.random.uniform(-0.2, 0.2)  # Légère inclinaison

        # Position orbitale 3D
        position_planete = etoile_parente.position + np.array(
            [
                distance_orbitale * np.cos(angle_orbital),
                distance_orbitale * np.sin(angle_orbital),
                distance_orbitale * inclinaison,
            ]
        )

        # Vitesse orbitale stable (approximation circulaire)
        vitesse_orbitale = np.sqrt(etoile_parente.masse * 0.001 / distance_orbitale)
        vecteur_orbital = (
            np.array(
                [
                    -vitesse_orbitale * np.sin(angle_orbital),
                    vitesse_orbitale * np.cos(angle_orbital),
                    0,
                ]
            )
            + etoile_parente.vecteur
        )

        # Propriétés planétaires
        masse_planete = np.random.uniform(20, 200)

        # Composition chimique réaliste
        composition = {
            "oxygene": np.random.uniform(15, 35),
            "silicium": np.random.uniform(10, 25),
            "fer": np.random.uniform(15, 40),
            "carbone": np.random.uniform(1, 15),
            "hydrogene": np.random.uniform(5, 20),
        }

        # Température d'équilibre thermique
        temperature = max(
            50, min(1000, etoile_parente.luminosite * 150 / (distance_orbitale**1.5))
        )

        # Classification selon composition
        fer_ratio = composition["fer"] / sum(composition.values())
        type_planete = "tellurique" if fer_ratio > 0.3 else "composite"

        return Planete(
            type=type_planete,
            masse=masse_planete,
            position=position_planete,
            vecteur=vecteur_orbital,
            composition=composition,
            temperature=temperature,
            etoile_parente_id=str(etoile_parente.id),
        )

    def _configurer_univers_final(
        self, monde: EtatMonde, type_univers: TypeUnivers
    ) -> None:
        """Configuration finale de l'univers généré."""
        # Constantes physiques depuis ConstantesPhysiques
        from etatmonde import ConstantesPhysiques

        monde.constantes.update(
            {
                "gravite": ConstantesPhysiques.GRAVITE,
                "expansion": self.params.facteur_expansion,
                "vitesse_lumiere": ConstantesPhysiques.VITESSE_LUMIERE,
                "constante_planck": ConstantesPhysiques.CONSTANTE_PLANCK,
                "energie_sombre": ConstantesPhysiques.ENERGIE_SOMBRE,
                "matiere_noire": ConstantesPhysiques.MATIERE_NOIRE,
            }
        )

        # Palier initial
        palier_initial = f"[Temps: 0] - {type_univers.value.replace('_', ' ').title()}"
        monde.paliers.append(palier_initial)

        # Statistiques de génération
        monde.statistiques.update(
            {
                "type_univers_initial": type_univers.value,
                "parametres_generation": {
                    "rayon_initial": self.params.rayon_initial,
                    "nombre_particules": self.params.nombre_particules,
                    "nombre_atomes": self.params.nombre_atomes,
                    "nombre_etoiles": self.params.nombre_etoiles_initiales,
                    "distribution": self.params.distribution_spatiale.value,
                },
                "statistiques_creation": self.statistiques_generation.copy(),
            }
        )

        # Détection paliers initiaux
        nouveaux_paliers = monde.detecter_paliers_emergents()
        if nouveaux_paliers:
            logger.info(f"Paliers initiaux détectés : {nouveaux_paliers}")


# ========================================================================
# API PUBLIQUE SIMPLIFIÉE
# ========================================================================


def creerbigbang(
    type_univers: TypeUnivers = TypeUnivers.BIG_BANG_CLASSIQUE,
    params_custom: Optional[ParametresCosmologiques] = None,
) -> EtatMonde:
    """
    Interface principale pour générer un univers.

    Args:
        type_univers: Type d'univers à générer
        params_custom: Paramètres personnalisés (optionnel)

    Returns:
        EtatMonde: Univers nouvellement créé
    """
    forge = ForgeCosmologique(params_custom)
    return forge.generer_univers(type_univers)


def creer_univers_personnalise(config: Dict[str, Any]) -> EtatMonde:
    """
    Crée un univers avec configuration entièrement personnalisée.

    Args:
        config: Configuration personnalisée

    Returns:
        EtatMonde: Univers personnalisé
    """
    # Conversion config dict vers ParametresCosmologiques
    params = ParametresCosmologiques()

    # Mapping des paramètres
    mapping = {
        "nombre_particules": "nombre_particules",
        "nombre_atomes": "nombre_atomes",
        "nombre_etoiles": "nombre_etoiles_initiales",
        "rayon_initial": "rayon_initial",
        "energie_initiale": "energie_cinetique_base",
        "seed": "seed_aleatoire",
    }

    for config_key, param_key in mapping.items():
        if config_key in config:
            setattr(params, param_key, config[config_key])

    forge = ForgeCosmologique(params)

    # Utiliser le template dense si beaucoup d'entités
    total_entites = (
        params.nombre_particules
        + params.nombre_atomes
        + params.nombre_etoiles_initiales
    )

    if total_entites > 20000:
        type_univers = TypeUnivers.LABORATOIRE_DENSE
    else:
        type_univers = TypeUnivers.BIG_BANG_CLASSIQUE

    return forge.generer_univers(type_univers)


# ========================================================================
# FONCTIONS DE CONVENANCE
# ========================================================================


def creer_univers_dense(multiplicateur: int = 3) -> EtatMonde:
    """Crée un univers dense pour plus d'interactions."""
    params = ParametresCosmologiques()
    params.nombre_particules = 10000 * multiplicateur
    params.nombre_atomes = 1000 * multiplicateur
    params.rayon_initial = 8.0  # Plus compact
    params.distribution_spatiale = TypeDistribution.AMAS

    forge = ForgeCosmologique(params)
    return forge.generer_univers(TypeUnivers.LABORATOIRE_DENSE)


def creer_univers_mature() -> EtatMonde:
    """Crée un univers avec quelques étoiles déjà formées."""
    return creerbigbang(TypeUnivers.UNIVERS_MATURE)


def creer_laboratoire_stellaire() -> EtatMonde:
    """Crée un univers optimisé pour l'étude des processus stellaires."""
    return creerbigbang(TypeUnivers.LABORATOIRE_STELLAIRE)


def creer_univers_biopret() -> EtatMonde:
    """Crée un univers avec conditions optimales pour l'émergence de la vie."""
    return creerbigbang(TypeUnivers.UNIVERS_BIOPRET)


# Fonction legacy pour compatibilité
def creerbigbang_simple() -> EtatMonde:
    """Version simple maintenue pour compatibilité."""
    return creerbigbang(TypeUnivers.BIG_BANG_CLASSIQUE)
