# Fichier : agents_physiques.py
# Version 11.0 ("Physique Robuste") - Agents de base optimisés et modulaires

"""
Module des agents de base - Physique fondamentale et stellaire.
Architecture refactorisée avec gestionnaires spécialisés, validation stricte
et optimisations adaptatives selon les ressources système.
"""

import logging
import pickle
import os
import threading
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING, List, Tuple, Optional, Dict, Any, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from etatmonde import EtatMonde, Particule, Atome, Etoile

# Import conditionnel sécurisé
try:
    from scipy.spatial import cKDTree

    SCIPY_DISPONIBLE = True
except ImportError:
    cKDTree = None
    SCIPY_DISPONIBLE = False

logger = logging.getLogger(__name__)

# ========================================================================
# CONFIGURATION ET ÉNUMÉRATIONS
# ========================================================================


class ModeCalcul(Enum):
    """Modes de calcul disponibles pour les forces gravitationnelles."""

    SEQUENTIEL = "sequentiel"
    PARALLELE = "parallele"
    ADAPTATIF = "adaptatif"


class NiveauPerformance(Enum):
    """Niveaux de performance selon les ressources."""

    HAUTE = "haute"
    MOYENNE = "moyenne"
    ECONOMIQUE = "economique"
    SURVIVAL = "survival"


@dataclass
class ConfigurationPhysique:
    """Configuration des paramètres physiques."""

    # Paramètres gravitationnels
    mode_calcul: ModeCalcul = ModeCalcul.ADAPTATIF
    seuil_parallelisation: int = 500
    max_processus: int = 4
    limite_entites_performance: int = 20000

    # Paramètres nucléosynthèse
    seuil_fusion: float = 0.25
    rayon_exclusion_stellaire: float = 12.0
    efficacite_fusion: float = 0.95

    # Paramètres temporels
    pas_temps_integration: float = 0.01
    vitesse_max_entites: float = 100.0

    # Paramètres de cache
    taille_cache_max: int = 10000
    cycles_invalidation_cache: int = 100


@dataclass
class MetriquesPhysiques:
    """Métriques de performance des calculs physiques."""

    cycles_total: int = 0
    temps_calcul_total: float = 0.0
    entites_traitees_total: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    erreurs_numeriques: int = 0

    def temps_moyen_par_cycle(self) -> float:
        """Calcule le temps moyen par cycle."""
        return self.temps_calcul_total / max(1, self.cycles_total)

    def taux_cache_hit(self) -> float:
        """Calcule le taux de succès du cache."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / max(1, total)


# ========================================================================
# UTILITAIRES PHYSIQUES
# ========================================================================


class ValidateurPhysique:
    """Validateur pour les calculs physiques."""

    @staticmethod
    def valider_arrays_physiques(
        positions: NDArray[np.float64],
        masses: NDArray[np.float64],
        vecteurs: Optional[NDArray[np.float64]] = None,
    ) -> Tuple[bool, List[str]]:
        """Valide les arrays physiques pour éviter erreurs numériques."""
        erreurs = []

        # Validation positions
        if not np.all(np.isfinite(positions)):
            erreurs.append("Positions contiennent NaN/Inf")

        # Validation masses
        if not np.all(masses > 0):
            erreurs.append("Masses négatives ou nulles détectées")

        if not np.all(np.isfinite(masses)):
            erreurs.append("Masses contiennent NaN/Inf")

        # Validation vecteurs si fournis
        if vecteurs is not None:
            if not np.all(np.isfinite(vecteurs)):
                erreurs.append("Vecteurs contiennent NaN/Inf")

        # Validation cohérence des tailles
        if vecteurs is not None and len(positions) != len(vecteurs):
            erreurs.append("Tailles incohérentes positions/vecteurs")

        if len(positions) != len(masses):
            erreurs.append("Tailles incohérentes positions/masses")

        return len(erreurs) == 0, erreurs

    @staticmethod
    def corriger_arrays_physiques(
        positions: NDArray[np.float64],
        masses: NDArray[np.float64],
        vecteurs: Optional[NDArray[np.float64]] = None,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64], Optional[NDArray[np.float64]]]:
        """Corrige automatiquement les arrays physiques invalides."""

        # Correction positions
        positions_corrigees = np.where(np.isfinite(positions), positions, 0.0)

        # Correction masses
        masses_corrigees = np.where(masses > 0, masses, 1e-6)
        masses_corrigees = np.where(
            np.isfinite(masses_corrigees), masses_corrigees, 1.0
        )

        # Correction vecteurs
        vecteurs_corriges = None
        if vecteurs is not None:
            vecteurs_corriges = np.where(np.isfinite(vecteurs), vecteurs, 0.0)

        return positions_corrigees, masses_corrigees, vecteurs_corriges


class CalculateurForcesGravitationnelles:
    """Calculateur spécialisé pour les forces gravitationnelles."""

    def __init__(self, config: ConfigurationPhysique):
        self.config = config
        self.metriques = MetriquesPhysiques()

    @staticmethod
    def calculer_forces_lot(
        indices_lot: NDArray[np.int64],
        positions_completes: NDArray[np.float64],
        masses_completes: NDArray[np.float64],
        constante_g: float,
    ) -> NDArray[np.float64]:
        """Calcule les forces gravitationnelles pour un lot d'entités (optimisé)."""
        n_lot = len(indices_lot)
        forces_lot = np.zeros((n_lot, 3), dtype=np.float64)

        # Validation préalable
        if n_lot == 0 or len(positions_completes) == 0:
            return forces_lot

        try:
            for i, index_global in enumerate(indices_lot):
                pos_actuelle = positions_completes[index_global]
                masse_actuelle = masses_completes[index_global]

                # Calcul vectorisé des différences
                diff = positions_completes - pos_actuelle
                dist_sq = np.sum(diff**2, axis=1)

                # Éviter auto-interaction et singularités
                dist_sq[index_global] = np.inf
                dist_sq = np.maximum(dist_sq, 1e-12)  # Distance minimale

                # Calcul forces avec gestion erreurs numériques
                with np.errstate(all="ignore"):
                    force_magnitudes = (
                        constante_g * masses_completes * masse_actuelle / dist_sq
                    )

                    # Limitation physique des forces
                    force_max = masse_actuelle * 1000
                    force_magnitudes = np.clip(force_magnitudes, 0, force_max)

                    # Remplacement des valeurs non-finies
                    force_magnitudes = np.where(
                        np.isfinite(force_magnitudes), force_magnitudes, 0.0
                    )

                # Sommation vectorielle
                force_resultante = np.sum(
                    diff * force_magnitudes[:, np.newaxis], axis=0
                )
                forces_lot[i] = force_resultante

        except Exception as e:
            logger.error(f"Erreur calcul forces lot: {e}")

        return forces_lot

    def calculer_forces_systeme_complet(
        self,
        entites_massives: List["Particule"],
        constante_g: float,
        mode_force: ModeCalcul = ModeCalcul.ADAPTATIF,
    ) -> NDArray[np.float64]:
        """Calcule les forces pour tout le système avec stratégie adaptative."""
        n_entites = len(entites_massives)

        # Extraction et validation des propriétés
        positions = np.array([e.position for e in entites_massives], dtype=np.float64)
        masses = np.array([e.masse for e in entites_massives], dtype=np.float64)

        # Validation stricte
        valide, erreurs = ValidateurPhysique.valider_arrays_physiques(positions, masses)
        if not valide:
            logger.warning(
                f"Arrays physiques invalides: {erreurs}, correction automatique"
            )
            positions, masses, _ = ValidateurPhysique.corriger_arrays_physiques(
                positions, masses
            )
            self.metriques.erreurs_numeriques += len(erreurs)

        # Choix stratégie de calcul
        if mode_force == ModeCalcul.ADAPTATIF:
            if n_entites > self.config.seuil_parallelisation and cpu_count() > 2:
                mode_effectif = ModeCalcul.PARALLELE
            else:
                mode_effectif = ModeCalcul.SEQUENTIEL
        else:
            mode_effectif = mode_force

        # Calcul selon la stratégie
        if mode_effectif == ModeCalcul.PARALLELE:
            return self._calculer_forces_parallele(positions, masses, constante_g)
        else:
            return self._calculer_forces_sequentiel(positions, masses, constante_g)

    def _calculer_forces_sequentiel(
        self,
        positions: NDArray[np.float64],
        masses: NDArray[np.float64],
        constante_g: float,
    ) -> NDArray[np.float64]:
        """Calcul séquentiel optimisé."""
        indices = np.arange(len(positions))
        return self.calculer_forces_lot(indices, positions, masses, constante_g)

    def _calculer_forces_parallele(
        self,
        positions: NDArray[np.float64],
        masses: NDArray[np.float64],
        constante_g: float,
    ) -> NDArray[np.float64]:
        """Calcul parallèle avec gestion d'erreurs."""
        try:
            with GestionnairePoolProcessus(self.config.max_processus) as pool:
                indices = np.arange(len(positions))
                lots_indices = np.array_split(indices, self.config.max_processus)

                # Filtrer les lots vides
                lots_valides = [lot for lot in lots_indices if lot.size > 0]

                donnees_pour_pool = [
                    (lot, positions, masses, constante_g) for lot in lots_valides
                ]

                resultats_lots = pool.map(
                    self.calculer_forces_lot_statique, donnees_pour_pool
                )

                return np.vstack(resultats_lots)

        except Exception as e:
            logger.warning(f"Échec calcul parallèle: {e}, basculement séquentiel")
            return self._calculer_forces_sequentiel(positions, masses, constante_g)

    @staticmethod
    def calculer_forces_lot_statique(donnees_lot: Tuple) -> NDArray[np.float64]:
        """Version statique pour multiprocessing."""
        indices_lot, positions_completes, masses_completes, constante_g = donnees_lot
        return CalculateurForcesGravitationnelles.calculer_forces_lot(
            indices_lot, positions_completes, masses_completes, constante_g
        )


# ========================================================================
# GESTIONNAIRE DE POOL DE PROCESSUS
# ========================================================================


@contextmanager
def GestionnairePoolProcessus(max_processus: int = 4):
    """Gestionnaire de contexte pour pool de processus sécurisé."""
    pool = None
    try:
        num_processus_effectif = max(1, min(cpu_count() - 1, max_processus))
        pool = Pool(processes=num_processus_effectif)
        logger.debug(f"Pool créé avec {num_processus_effectif} processus")
        yield pool
    except Exception as e:
        logger.error(f"Erreur gestion pool: {e}")
        yield None
    finally:
        if pool:
            try:
                pool.close()
                pool.join(timeout=3)
            except Exception as e:
                logger.warning(f"Erreur fermeture pool: {e}")
                try:
                    pool.terminate()
                    pool.join(timeout=1)
                except:
                    pass


# ========================================================================
# AGENTS PHYSIQUES REFACTORISÉS
# ========================================================================


class MaitreTemps:
    """Agent temporel - Métronome cosmique avec métriques."""

    def __init__(self, config: Optional[ConfigurationPhysique] = None):
        """Initialise le gestionnaire temporel."""
        self.config = config or ConfigurationPhysique()
        self.cycles_elapsed: int = 0
        self.derniere_vitesse: int = 1
        self.temps_debut_simulation: float = 0.0

    def maitretemps(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Avance le temps de simulation d'un cycle avec validation."""
        try:
            etatmonde.temps += 1
            self.cycles_elapsed += 1

            # Mise à jour métadonnées temporelles
            if hasattr(etatmonde, "derniere_mise_a_jour_temps"):
                etatmonde.derniere_mise_a_jour_temps = etatmonde.temps

            # Log périodique adaptatif
            intervalle_log = self._calculer_intervalle_log(etatmonde.temps)
            if etatmonde.temps % intervalle_log == 0:
                logger.info(
                    f"Progression temporelle: {etatmonde.temps:,} cycles "
                    f"({self.cycles_elapsed:,} cycles depuis démarrage)"
                )

            return etatmonde

        except Exception as e:
            logger.error(f"Erreur MaitreTemps au cycle {etatmonde.temps}: {e}")
            return etatmonde

    def _calculer_intervalle_log(self, temps_actuel: int) -> int:
        """Calcule l'intervalle de log adaptatif selon le temps."""
        if temps_actuel < 1000:
            return 100
        elif temps_actuel < 10000:
            return 1000
        elif temps_actuel < 100000:
            return 10000
        else:
            return 50000


class CalculateurLois:
    """Agent physique - Dynamique gravitationnelle optimisée."""

    def __init__(self, config: Optional[ConfigurationPhysique] = None):
        """Initialise le calculateur avec configuration flexible."""
        self.config = config or ConfigurationPhysique()
        self.calculateur_forces = CalculateurForcesGravitationnelles(self.config)
        self.metriques = MetriquesPhysiques()
        self.cache_forces: Dict[str, NDArray[np.float64]] = {}
        self.derniere_invalidation = 0
        self._lock = threading.Lock()

    def calculateurlois(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Applique les lois physiques avec stratégie adaptative."""
        import time

        temps_debut = time.time()

        try:
            # Collecte des entités massives
            entites_massives = self._collecter_entites_massives(etatmonde)
            n_entites = len(entites_massives)

            if n_entites < 2:
                return etatmonde

            # Optimisation adaptative pour gros systèmes
            entites_traitees = self._optimiser_entites_selon_performance(
                entites_massives, n_entites
            )

            # Calcul des forces gravitationnelles
            forces = self.calculateur_forces.calculer_forces_systeme_complet(
                entites_traitees,
                etatmonde.constantes["gravite"],
                self.config.mode_calcul,
            )

            # Application de la dynamique
            self._appliquer_dynamique(entites_traitees, forces, etatmonde)

            # Mise à jour métriques
            temps_calcul = time.time() - temps_debut
            self._mettre_a_jour_metriques(temps_calcul, len(entites_traitees))

            return etatmonde

        except Exception as e:
            logger.error(f"Erreur CalculateurLois: {e}")
            return etatmonde

    def _collecter_entites_massives(self, etatmonde: "EtatMonde") -> List:
        """Collecte toutes les entités ayant une masse significative."""
        entites_massives = []

        categories_massives = [
            "particules",
            "atomes",
            "etoiles",
            "planetes",
            "trous_noirs",
        ]

        for categorie in categories_massives:
            entites_categorie = etatmonde.entites.get(categorie, [])
            # Filtrer les entités avec masse significative
            entites_valides = [e for e in entites_categorie if e.masse > 1e-9]
            entites_massives.extend(entites_valides)

        return entites_massives

    def _optimiser_entites_selon_performance(
        self, entites_massives: List, n_entites: int
    ) -> List:
        """Optimise le nombre d'entités selon les performances."""
        if n_entites <= self.config.limite_entites_performance:
            return entites_massives

        # Stratégie d'échantillonnage intelligent
        logger.info(f"Optimisation performance: {n_entites} entités -> échantillonnage")

        # Tri par masse décroissante
        entites_triees = sorted(entites_massives, key=lambda e: e.masse, reverse=True)

        # Garder les plus massives + échantillon représentatif
        limite_importantes = min(5000, self.config.limite_entites_performance // 4)
        entites_importantes = entites_triees[:limite_importantes]

        # Échantillonnage du reste
        entites_restantes = entites_triees[limite_importantes:]
        pas_echantillonnage = max(
            1,
            len(entites_restantes)
            // (self.config.limite_entites_performance - limite_importantes),
        )
        entites_echantillon = entites_restantes[::pas_echantillonnage]

        entites_finales = entites_importantes + entites_echantillon

        logger.debug(
            f"Échantillonnage: {len(entites_importantes)} importantes + "
            f"{len(entites_echantillon)} échantillonnées = {len(entites_finales)} total"
        )

        return entites_finales

    def _appliquer_dynamique(
        self, entites: List, forces: NDArray[np.float64], etatmonde: "EtatMonde"
    ) -> None:
        """Applique la dynamique newtonienne avec intégration stable."""
        # Extraction des propriétés cinématiques
        est_mobile = np.array([hasattr(e, "vecteur") for e in entites])

        if not np.any(est_mobile):
            return

        # Arrays pour calculs
        positions = np.array([e.position for e in entites])
        masses = np.array([e.masse for e in entites])
        vecteurs = np.array(
            [e.vecteur if hasattr(e, "vecteur") else np.zeros(3) for e in entites]
        )

        # Calcul accélérations (a = F/m)
        acceleration = np.zeros_like(positions)
        masses_mobiles = masses[est_mobile, np.newaxis]
        masses_mobiles = np.maximum(masses_mobiles, 1e-12)  # Éviter division par zéro
        acceleration[est_mobile] = forces[est_mobile] / masses_mobiles

        # Intégration de Verlet pour stabilité
        dt = self.config.pas_temps_integration
        nouveaux_vecteurs = vecteurs + acceleration * dt
        nouvelles_positions = positions + nouveaux_vecteurs * dt

        # Application expansion cosmologique
        facteur_expansion = 1 + etatmonde.constantes.get("expansion", 0)
        nouvelles_positions *= facteur_expansion

        # Limitation des vitesses
        vitesses = np.linalg.norm(nouveaux_vecteurs, axis=1)
        indices_rapides = vitesses > self.config.vitesse_max_entites

        if np.any(indices_rapides):
            facteur_limitation = (
                self.config.vitesse_max_entites / vitesses[indices_rapides, np.newaxis]
            )
            nouveaux_vecteurs[indices_rapides] *= facteur_limitation

        # Mise à jour des entités
        for i, entite in enumerate(entites):
            entite.position = nouvelles_positions[i]
            if est_mobile[i]:
                entite.vecteur = nouveaux_vecteurs[i]

    def _mettre_a_jour_metriques(self, temps_calcul: float, nb_entites: int) -> None:
        """Met à jour les métriques de performance."""
        with self._lock:
            self.metriques.cycles_total += 1
            self.metriques.temps_calcul_total += temps_calcul
            self.metriques.entites_traitees_total += nb_entites

    def obtenir_rapport_performance(self) -> Dict[str, Any]:
        """Génère un rapport de performance."""
        return {
            "cycles_total": self.metriques.cycles_total,
            "temps_moyen_cycle": self.metriques.temps_moyen_par_cycle(),
            "entites_traitees": self.metriques.entites_traitees_total,
            "erreurs_numeriques": self.metriques.erreurs_numeriques,
            "mode_calcul": self.config.mode_calcul.value,
        }


class Alchimiste:
    """Agent nucléaire - Nucléosynthèse primordiale optimisée."""

    def __init__(self, config: Optional[ConfigurationPhysique] = None):
        """Initialise les paramètres de nucléosynthèse."""
        self.config = config or ConfigurationPhysique()
        self.types_atomes_produits = ["hydrogene", "helium", "deuterium", "lithium"]
        self.compteur_fusions = 0

    def alchimiste(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Protocole de nucléosynthèse avec gestion intelligente."""
        from etatmonde import Particule, Atome, Etoile

        particules: List[Particule] = etatmonde.entites.get("particules", [])
        if len(particules) < 2:
            return etatmonde

        # Choix de l'algorithme selon disponibilité scipy
        if SCIPY_DISPONIBLE and cKDTree and len(particules) > 100:
            return self._alchimiste_optimise(etatmonde, particules)
        else:
            return self._alchimiste_simple(etatmonde, particules)

    def _alchimiste_optimise(
        self, etatmonde: "EtatMonde", particules: List["Particule"]
    ) -> "EtatMonde":
        """Version optimisée avec scipy et filtrage stellaire."""
        from etatmonde import Atome

        positions_particules = np.array([p.position for p in particules])

        # Filtrage : éviter fusion près des étoiles
        particules_eligibles = self._filtrer_particules_loin_etoiles(
            etatmonde, particules, positions_particules
        )

        if len(particules_eligibles) < 2:
            return etatmonde

        # Construction arbre spatial
        positions_eligibles = np.array([p.position for p in particules_eligibles])
        arbre_positions = cKDTree(positions_eligibles)

        # Recherche de paires pour fusion
        paires = arbre_positions.query_pairs(r=self.config.seuil_fusion)
        if not paires:
            return etatmonde

        # Traitement des fusions
        nouveaux_atomes, indices_consommes = self._traiter_fusions(
            particules_eligibles, paires
        )

        # Mise à jour état du monde
        if nouveaux_atomes:
            self._appliquer_resultats_fusion(
                etatmonde,
                particules,
                particules_eligibles,
                nouveaux_atomes,
                indices_consommes,
            )

        return etatmonde

    def _filtrer_particules_loin_etoiles(
        self,
        etatmonde: "EtatMonde",
        particules: List["Particule"],
        positions_particules: NDArray[np.float64],
    ) -> List["Particule"]:
        """Filtre les particules éloignées des étoiles."""
        etoiles = etatmonde.entites.get("etoiles", [])

        if not etoiles:
            return particules

        positions_etoiles = np.array([e.position for e in etoiles])
        arbre_etoiles = cKDTree(positions_etoiles)

        distances_etoiles = arbre_etoiles.query(positions_particules, k=1)[0]
        indices_isolees = distances_etoiles > self.config.rayon_exclusion_stellaire

        return [p for i, p in enumerate(particules) if indices_isolees[i]]

    def _traiter_fusions(
        self, particules_eligibles: List["Particule"], paires: set
    ) -> Tuple[List["Atome"], NDArray[np.bool_]]:
        """Traite les fusions de particules en atomes."""
        from etatmonde import Atome

        indices_consommes = np.zeros(len(particules_eligibles), dtype=bool)
        nouveaux_atomes: List[Atome] = []

        for i, j in paires:
            if indices_consommes[i] or indices_consommes[j]:
                continue

            p1, p2 = particules_eligibles[i], particules_eligibles[j]

            # Calcul propriétés fusion
            masse_totale = (p1.masse + p2.masse) * self.config.efficacite_fusion
            position_fusion = (p1.position + p2.position) / 2

            # Conservation momentum
            vecteur_fusion = (p1.vecteur * p1.masse + p2.vecteur * p2.masse) / (
                p1.masse + p2.masse
            )

            # Détermination type d'atome (probabiliste)
            type_atome = self._determiner_type_atome(masse_totale)

            # Ajout énergie de liaison si nécessaire
            if type_atome in ["helium", "lithium"]:
                energie_liaison = np.random.normal(0, 0.03, 3)
                vecteur_fusion += energie_liaison

            nouvel_atome = Atome(
                type=type_atome,
                masse=masse_totale,
                position=position_fusion,
                vecteur=vecteur_fusion,
            )
            nouveaux_atomes.append(nouvel_atome)

            indices_consommes[i] = True
            indices_consommes[j] = True
            self.compteur_fusions += 1

        return nouveaux_atomes, indices_consommes

    def _determiner_type_atome(self, masse_totale: float) -> str:
        """Détermine le type d'atome selon la masse avec probabilités réalistes."""
        if masse_totale < 0.5:
            return "hydrogene"
        elif masse_totale < 1.5:
            return np.random.choice(["hydrogene", "deuterium"], p=[0.85, 0.15])
        elif masse_totale < 3.0:
            return np.random.choice(["helium", "hydrogene"], p=[0.75, 0.25])
        else:
            return np.random.choice(
                ["helium", "lithium", "hydrogene"], p=[0.6, 0.15, 0.25]
            )

    def _appliquer_resultats_fusion(
        self,
        etatmonde: "EtatMonde",
        particules_originales: List["Particule"],
        particules_eligibles: List["Particule"],
        nouveaux_atomes: List["Atome"],
        indices_consommes: NDArray[np.bool_],
    ) -> None:
        """Applique les résultats de fusion à l'état du monde."""

        # Log des résultats
        compteurs = {}
        for atome in nouveaux_atomes:
            compteurs[atome.type] = compteurs.get(atome.type, 0) + 1

        logger.info(
            f"Nucléosynthèse Temps {etatmonde.temps}: "
            f"{len(nouveaux_atomes)} atomes formés "
            f"({', '.join(f'{count} {type_}' for type_, count in compteurs.items())})"
        )

        # Suppression des particules consommées
        ids_consommes = {
            particules_eligibles[i].id
            for i, consomme in enumerate(indices_consommes)
            if consomme
        }

        etatmonde.entites["particules"] = [
            p for p in particules_originales if p.id not in ids_consommes
        ]

        # Ajout des nouveaux atomes
        etatmonde.entites["atomes"].extend(nouveaux_atomes)

        # Enregistrement du palier
        if not any("PremiereNucleosynthese" in p for p in etatmonde.paliers):
            etatmonde.paliers.append(
                f"[Temps: {etatmonde.temps}] - PremiereNucleosynthese"
            )

    def _alchimiste_simple(
        self, etatmonde: "EtatMonde", particules: List["Particule"]
    ) -> "EtatMonde":
        """Version simple sans scipy, optimisée pour petits systèmes."""
        from etatmonde import Atome

        nouveaux_atomes: List[Atome] = []
        particules_a_supprimer: List["Particule"] = []

        # Algorithme O(n²) avec early exit pour performance
        for i, p1 in enumerate(particules):
            if p1 in particules_a_supprimer:
                continue

            for p2 in particules[i + 1 :]:
                if p2 in particules_a_supprimer:
                    continue

                distance = np.linalg.norm(p1.position - p2.position)
                if distance < self.config.seuil_fusion:
                    # Fusion simplifiée
                    masse_totale = (p1.masse + p2.masse) * self.config.efficacite_fusion
                    position_fusion = (p1.position + p2.position) / 2
                    vecteur_fusion = (p1.vecteur + p2.vecteur) / 2

                    nouvel_atome = Atome(
                        type=self._determiner_type_atome(masse_totale),
                        masse=masse_totale,
                        position=position_fusion,
                        vecteur=vecteur_fusion,
                    )
                    nouveaux_atomes.append(nouvel_atome)
                    particules_a_supprimer.extend([p1, p2])
                    break

        # Application des résultats
        if nouveaux_atomes:
            ids_a_supprimer = {p.id for p in particules_a_supprimer}
            etatmonde.entites["particules"] = [
                p for p in particules if p.id not in ids_a_supprimer
            ]
            etatmonde.entites["atomes"].extend(nouveaux_atomes)

        return etatmonde


# ========================================================================
# GESTIONNAIRE DE SAUVEGARDE AVANCÉ
# ========================================================================


class GestionnaireSauvegarde:
    """Gestionnaire spécialisé pour les opérations de sauvegarde."""

    def __init__(self, repertoire: Union[str, Path] = "sauvegardes"):
        self.repertoire = Path(repertoire)
        self.repertoire.mkdir(exist_ok=True)
        self.format_timestamp = "%Y%m%d_%H%M%S"
        self.max_backups = 10

    def sauvegarder_avec_backup(
        self, etatmonde: "EtatMonde", nom_fichier: str = "memoire.monde"
    ) -> bool:
        """Sauvegarde avec backup automatique et validation."""
        if not etatmonde:
            logger.error("Tentative de sauvegarde d'un univers None")
            return False

        try:
            # Validation préalable
            if not self._valider_univers_sauvegardable(etatmonde):
                return False

            # Sauvegarde principale avec sauvegarde atomique
            fichier_temp = f"{nom_fichier}.tmp"

            with open(fichier_temp, "wb") as f:
                pickle.dump(etatmonde, f, protocol=pickle.HIGHEST_PROTOCOL)

            # Renommage atomique
            os.rename(fichier_temp, nom_fichier)

            # Création backup horodaté
            self._creer_backup_horodate(etatmonde)

            # Nettoyage anciens backups
            self._nettoyer_anciens_backups()

            logger.info(
                f"Sauvegarde réussie - Temps: {etatmonde.temps}, "
                f"Entités: {sum(len(cat) for cat in etatmonde.entites.values())}"
            )
            return True

        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
            # Nettoyage fichier temporaire si erreur
            if os.path.exists(fichier_temp):
                try:
                    os.remove(fichier_temp)
                except:
                    pass
            return False

    def _valider_univers_sauvegardable(self, etatmonde: "EtatMonde") -> bool:
        """Valide qu'un univers peut être sauvegardé."""
        try:
            # Vérifications de base
            if not hasattr(etatmonde, "temps") or not hasattr(etatmonde, "entites"):
                logger.error("Structure EtatMonde invalide")
                return False

            # Test de sérialisation
            test_pickle = pickle.dumps(etatmonde, protocol=pickle.HIGHEST_PROTOCOL)
            if len(test_pickle) == 0:
                logger.error("Échec test sérialisation")
                return False

            return True

        except Exception as e:
            logger.error(f"Validation univers échouée: {e}")
            return False

    def _creer_backup_horodate(self, etatmonde: "EtatMonde") -> None:
        """Crée un backup avec horodatage."""
        timestamp = datetime.now().strftime(self.format_timestamp)
        nom_backup = self.repertoire / f"univers_backup_{timestamp}.monde"

        with open(nom_backup, "wb") as f:
            pickle.dump(etatmonde, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _nettoyer_anciens_backups(self) -> None:
        """Supprime les backups anciens selon la politique de rétention."""
        backups = sorted(
            self.repertoire.glob("univers_backup_*.monde"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if len(backups) > self.max_backups:
            for backup in backups[self.max_backups :]:
                try:
                    backup.unlink()
                    logger.debug(f"Backup ancien supprimé: {backup.name}")
                except Exception as e:
                    logger.warning(f"Erreur suppression backup {backup.name}: {e}")


class Archiviste:
    """Agent archiviste - Interface de sauvegarde avec fallback robuste."""

    def __init__(self):
        """Initialise l'archiviste avec gestionnaire de sauvegarde."""
        self.gestionnaire = GestionnaireSauvegarde()

    def archiviste(
        self, etatmonde: Optional["EtatMonde"] = None, instruction: str = "charger"
    ) -> Union[Optional["EtatMonde"], bool, List[Dict[str, Any]]]:
        """Interface principale de l'archiviste."""
        try:
            if instruction == "sauvegarder":
                return self.gestionnaire.sauvegarder_avec_backup(etatmonde)
            elif instruction == "charger":
                return self._charger_avec_fallback()
            elif instruction == "lister_sauvegardes":
                return self._lister_sauvegardes()
            else:
                logger.error(f"Instruction inconnue: {instruction}")
                return None

        except Exception as e:
            logger.error(f"Erreur Archiviste instruction '{instruction}': {e}")
            return None

    def _charger_avec_fallback(self) -> Optional["EtatMonde"]:
        """Charge un univers avec système de fallback robuste."""
        fichier_principal = "memoire.monde"

        # Tentative fichier principal
        monde_charge = self._tenter_chargement_fichier(fichier_principal)
        if monde_charge:
            return monde_charge

        logger.warning("Fichier principal inaccessible, tentative backups...")

        # Fallback sur backups par ordre chronologique
        backups = sorted(
            self.gestionnaire.repertoire.glob("univers_backup_*.monde"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for backup_path in backups:
            monde_charge = self._tenter_chargement_fichier(str(backup_path))
            if monde_charge:
                logger.info(f"Univers récupéré depuis {backup_path.name}")
                return monde_charge

        logger.info("Aucun univers récupérable trouvé")
        return None

    def _tenter_chargement_fichier(self, nom_fichier: str) -> Optional["EtatMonde"]:
        """Tente de charger un fichier avec validation."""
        try:
            if not os.path.exists(nom_fichier):
                return None

            with open(nom_fichier, "rb") as f:
                monde_charge = pickle.load(f)

            # Validation post-chargement
            if self._valider_univers_charge(monde_charge):
                logger.info(f"Chargement réussi: {nom_fichier}")
                return monde_charge
            else:
                logger.warning(f"Univers chargé invalide: {nom_fichier}")
                return None

        except Exception as e:
            logger.warning(f"Échec chargement {nom_fichier}: {e}")
            return None

    def _valider_univers_charge(self, etatmonde: "EtatMonde") -> bool:
        """Valide un univers après chargement."""
        try:
            # Vérifications de base
            if not hasattr(etatmonde, "temps") or etatmonde.temps < 0:
                return False

            if not hasattr(etatmonde, "entites") or not isinstance(
                etatmonde.entites, dict
            ):
                return False

            # Validation entités
            total_entites = sum(len(cat) for cat in etatmonde.entites.values())
            if total_entites > 1000000:  # Limite raisonnable
                logger.warning(f"Univers très volumineux: {total_entites} entités")

            return True

        except Exception:
            return False

    def _lister_sauvegardes(self) -> List[Dict[str, Any]]:
        """Liste toutes les sauvegardes avec métadonnées."""
        sauvegardes = []

        # Fichier principal
        fichier_principal = "memoire.monde"
        if os.path.exists(fichier_principal):
            stat = os.stat(fichier_principal)
            sauvegardes.append(
                {
                    "nom": fichier_principal,
                    "type": "principal",
                    "taille_mb": stat.st_size / (1024 * 1024),
                    "date_modification": datetime.fromtimestamp(stat.st_mtime),
                }
            )

        # Backups
        for backup_path in self.gestionnaire.repertoire.glob("univers_backup_*.monde"):
            stat = backup_path.stat()
            sauvegardes.append(
                {
                    "nom": backup_path.name,
                    "type": "backup",
                    "taille_mb": stat.st_size / (1024 * 1024),
                    "date_modification": datetime.fromtimestamp(stat.st_mtime),
                }
            )

        return sorted(sauvegardes, key=lambda s: s["date_modification"], reverse=True)


# ========================================================================
# OPTIMISATEUR DE PERFORMANCE AVANCÉ
# ========================================================================


class OptimisateurPerformance:
    """Optimisateur intelligent selon les ressources système."""

    @staticmethod
    def analyser_performance_systeme(etatmonde: "EtatMonde") -> Dict[str, Any]:
        """Analyse complète des performances avec recommandations."""
        total_entites = sum(len(cat) for cat in etatmonde.entites.values())

        # Classification du niveau de performance
        niveau = OptimisateurPerformance._determiner_niveau_performance(total_entites)

        # Recommandations adaptatives
        recommandations = OptimisateurPerformance._generer_recommandations(
            niveau, total_entites
        )

        # Paramètres suggérés
        parametres_optimaux = OptimisateurPerformance._calculer_parametres_optimaux(
            niveau, total_entites
        )

        return {
            "total_entites": total_entites,
            "niveau_performance": niveau.value,
            "recommandations": recommandations,
            "parametres_optimaux": parametres_optimaux,
            "timestamp_analyse": datetime.now().isoformat(),
        }

    @staticmethod
    def _determiner_niveau_performance(total_entites: int) -> NiveauPerformance:
        """Détermine le niveau de performance selon le nombre d'entités."""
        if total_entites < 1000:
            return NiveauPerformance.HAUTE
        elif total_entites < 5000:
            return NiveauPerformance.MOYENNE
        elif total_entites < 15000:
            return NiveauPerformance.ECONOMIQUE
        else:
            return NiveauPerformance.SURVIVAL

    @staticmethod
    def _generer_recommandations(
        niveau: NiveauPerformance, total_entites: int
    ) -> List[str]:
        """Génère des recommandations selon le niveau de performance."""
        recommandations = []

        if niveau == NiveauPerformance.HAUTE:
            recommandations.append("Performance optimale - Tous calculs activés")

        elif niveau == NiveauPerformance.MOYENNE:
            recommandations.append("Performance correcte - Surveillance recommandée")
            recommandations.append("Considérez réduire fréquence agents lourds")

        elif niveau == NiveauPerformance.ECONOMIQUE:
            recommandations.append("Performance limitée - Optimisations nécessaires")
            recommandations.append("Réduisez la parallélisation")
            recommandations.append("Augmentez fréquence calculs lourds")

        else:  # SURVIVAL
            recommandations.append("Performance critique - Action immédiate requise")
            recommandations.append(
                f"Réduisez drastiquement le nombre d'entités ({total_entites})"
            )
            recommandations.append("Désactivez agents non-essentiels")
            recommandations.append("Considérez redémarrer avec univers plus petit")

        return recommandations

    @staticmethod
    def _calculer_parametres_optimaux(
        niveau: NiveauPerformance, total_entites: int
    ) -> Dict[str, Any]:
        """Calcule les paramètres optimaux selon le niveau."""
        params = {
            NiveauPerformance.HAUTE: {
                "frequence_calculs_lourds": 1,
                "mode_calcul": ModeCalcul.PARALLELE.value,
                "limite_entites": 25000,
                "fps_interface_max": 60,
            },
            NiveauPerformance.MOYENNE: {
                "frequence_calculs_lourds": 2,
                "mode_calcul": ModeCalcul.ADAPTATIF.value,
                "limite_entites": 15000,
                "fps_interface_max": 45,
            },
            NiveauPerformance.ECONOMIQUE: {
                "frequence_calculs_lourds": 5,
                "mode_calcul": ModeCalcul.SEQUENTIEL.value,
                "limite_entites": 10000,
                "fps_interface_max": 30,
            },
            NiveauPerformance.SURVIVAL: {
                "frequence_calculs_lourds": 10,
                "mode_calcul": ModeCalcul.SEQUENTIEL.value,
                "limite_entites": 5000,
                "fps_interface_max": 15,
            },
        }

        return params[niveau]
