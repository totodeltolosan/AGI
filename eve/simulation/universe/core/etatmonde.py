# Fichier : etatmonde.py
# Version 9.0 ("Architecture Robuste") - Structures de données validées et optimisées.

"""
Définit la structure de données centrale de la simulation, l'Objet-Univers.
Ce fichier est la seule source de vérité concernant l'état de l'univers à un instant t.
Il utilise des dataclasses avec héritage, validation stricte et optimisations performance.
Version améliorée avec validation robuste, types précis et méthodes utilitaires.
"""

import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Any, ClassVar, Optional, Union, Tuple
from enum import Enum

import numpy as np
from numpy.typing import NDArray

# Utilisation du logger configuré dans lancement.py
logger = logging.getLogger(__name__)

# ========================================================================
# CONSTANTES ET ÉNUMÉRATIONS
# ========================================================================


class TypeEtoile(Enum):
    """Types d'étoiles reconnus par la simulation."""

    NAINE = "naine"
    ETOILE_MOYENNE = "etoile_moyenne"
    ETOILE_JEUNE = "etoile_jeune"
    GEANTE = "geante"
    SUPERGEANTE = "supergeante"


class TypePlanete(Enum):
    """Types de planètes reconnus par la simulation."""

    TELLURIQUE = "tellurique"
    GAZEUSE = "gazeuse"
    RICHE_CARBONE = "riche_carbone"
    RICHE_OXYGENE = "riche_oxygene"
    COMPOSITE = "composite"


class TypeGalaxie(Enum):
    """Types morphologiques de galaxies."""

    SPIRALE = "spirale"
    ELLIPTIQUE = "elliptique"
    IRREGULIERE = "irreguliere"


class ConstantesPhysiques:
    """Constantes physiques centralisées avec documentation."""

    # Constantes fondamentales
    GRAVITE: float = 6.67430e-11  # Constante gravitationnelle (m³/kg/s²)
    VITESSE_LUMIERE: float = 3e8  # Vitesse de la lumière (m/s)
    CONSTANTE_PLANCK: float = 6.626e-34  # Constante de Planck (J⋅s)

    # Constantes cosmologiques
    EXPANSION_BASE: float = 1e-5  # Taux d'expansion de l'univers
    ENERGIE_SOMBRE: float = 0.68  # Fraction d'énergie sombre
    MATIERE_NOIRE: float = 0.27  # Fraction de matière noire

    # Limites physiques pour validation
    MASSE_MIN: float = 1e-10  # Masse minimale valide
    MASSE_MAX: float = 1e10  # Masse maximale valide
    VITESSE_MAX: float = 1e3  # Vitesse maximale autorisée
    TEMPERATURE_MIN: float = 0.0  # Température minimale absolue
    TEMPERATURE_MAX: float = 1e8  # Température maximale stellaire


# ========================================================================
# UTILITAIRES DE VALIDATION
# ========================================================================


class ValidateurPhysique:
    """Classe utilitaire pour valider les propriétés physiques."""

    @staticmethod
    def valider_masse(masse: float, nom_entite: str = "") -> float:
        """Valide et corrige une valeur de masse."""
        if not isinstance(masse, (int, float)) or not np.isfinite(masse):
            logger.warning(
                f"Masse invalide pour {nom_entite}: {masse}, correction à 1.0"
            )
            return 1.0

        if masse < ConstantesPhysiques.MASSE_MIN:
            logger.debug(
                f"Masse trop faible pour {nom_entite}: {masse}, correction à minimum"
            )
            return ConstantesPhysiques.MASSE_MIN

        if masse > ConstantesPhysiques.MASSE_MAX:
            logger.warning(
                f"Masse excessive pour {nom_entite}: {masse}, limitation appliquée"
            )
            return ConstantesPhysiques.MASSE_MAX

        return float(masse)

    @staticmethod
    def valider_position(position: Union[list, tuple, NDArray]) -> NDArray[np.float64]:
        """Valide et normalise une position 3D."""
        try:
            pos_array = np.asarray(position, dtype=np.float64)
            if pos_array.shape != (3,):
                logger.error(
                    f"Position invalide (forme {pos_array.shape}), correction à [0,0,0]"
                )
                return np.zeros(3, dtype=np.float64)

            if not np.all(np.isfinite(pos_array)):
                logger.warning("Position contient NaN/Inf, correction à [0,0,0]")
                return np.zeros(3, dtype=np.float64)

            return pos_array
        except (ValueError, TypeError) as e:
            logger.error(f"Erreur validation position: {e}, correction à [0,0,0]")
            return np.zeros(3, dtype=np.float64)

    @staticmethod
    def valider_vecteur(vecteur: Union[list, tuple, NDArray]) -> NDArray[np.float64]:
        """Valide et limite un vecteur de vitesse."""
        try:
            vec_array = np.asarray(vecteur, dtype=np.float64)
            if vec_array.shape != (3,):
                logger.error(
                    f"Vecteur invalide (forme {vec_array.shape}), correction à [0,0,0]"
                )
                return np.zeros(3, dtype=np.float64)

            if not np.all(np.isfinite(vec_array)):
                logger.warning("Vecteur contient NaN/Inf, correction à [0,0,0]")
                return np.zeros(3, dtype=np.float64)

            # Limitation de vitesse pour stabilité numérique
            vitesse = np.linalg.norm(vec_array)
            if vitesse > ConstantesPhysiques.VITESSE_MAX:
                facteur = ConstantesPhysiques.VITESSE_MAX / vitesse
                vec_array *= facteur
                logger.debug(f"Vitesse excessive ({vitesse:.2f}), limitation appliquée")

            return vec_array
        except (ValueError, TypeError) as e:
            logger.error(f"Erreur validation vecteur: {e}, correction à [0,0,0]")
            return np.zeros(3, dtype=np.float64)


# ========================================================================
# CLASSE DE BASE POUR TOUTES LES ENTITÉS
# ========================================================================


@dataclass
class EntiteCosmique:
    """
    Classe de base pour toutes les entités de l'univers.
    Définit les attributs communs et un système d'identification unique (UUID).
    Version améliorée avec validation stricte et méthodes utilitaires.
    """

    masse: float
    position: Union[list, tuple, NDArray]
    id: uuid.UUID = field(default_factory=uuid.uuid4, init=False, repr=False)
    categorie: ClassVar[str] = "inconnu"

    # Métadonnées de création et debug
    temps_creation: int = field(default=0, init=False)
    derniere_mise_a_jour: int = field(default=0, init=False)

    def __post_init__(self):
        """Validation stricte des propriétés physiques."""
        # Validation et correction de la masse
        self.masse = ValidateurPhysique.valider_masse(
            self.masse, f"{self.__class__.__name__}({str(self.id)[:8]})"
        )

        # Validation et correction de la position
        self.position = ValidateurPhysique.valider_position(self.position)

        logger.debug(
            f"Entité {self.__class__.__name__} créée avec masse={self.masse:.3f}"
        )

    def distance_vers(self, autre: "EntiteCosmique") -> float:
        """Calcule la distance euclidienne vers une autre entité."""
        return float(np.linalg.norm(self.position - autre.position))

    def est_proche_de(self, autre: "EntiteCosmique", seuil: float) -> bool:
        """Vérifie si cette entité est proche d'une autre."""
        return self.distance_vers(autre) <= seuil

    def deplacer_vers(self, nouvelle_position: Union[list, tuple, NDArray]) -> None:
        """Déplace l'entité vers une nouvelle position validée."""
        self.position = ValidateurPhysique.valider_position(nouvelle_position)

    def obtenir_info_debug(self) -> Dict[str, Any]:
        """Retourne les informations de debug de l'entité."""
        return {
            "id": str(self.id),
            "type": self.__class__.__name__,
            "categorie": self.categorie,
            "masse": self.masse,
            "position": self.position.tolist(),
            "temps_creation": self.temps_creation,
        }


# ========================================================================
# DÉFINITION DES SCHÉMAS D'ENTITÉS SPÉCIFIQUES (HÉRITAGE)
# ========================================================================


@dataclass
class EntiteMobile(EntiteCosmique):
    """
    Classe intermédiaire pour toutes les entités possédant leur propre vecteur de mouvement.
    Version améliorée avec validation des vitesses et méthodes cinématiques.
    """

    vecteur: Union[list, tuple, NDArray]

    def __post_init__(self):
        """Validation stricte de la position et du vecteur."""
        super().__post_init__()
        self.vecteur = ValidateurPhysique.valider_vecteur(self.vecteur)

    def vitesse(self) -> float:
        """Retourne la magnitude de la vitesse."""
        return float(np.linalg.norm(self.vecteur))

    def energie_cinetique(self) -> float:
        """Calcule l'énergie cinétique (1/2 * m * v²)."""
        return 0.5 * self.masse * (self.vitesse() ** 2)

    def accelerer(self, acceleration: Union[list, tuple, NDArray]) -> None:
        """Applique une accélération au vecteur de vitesse."""
        acc_validee = ValidateurPhysique.valider_vecteur(acceleration)
        nouveau_vecteur = self.vecteur + acc_validee
        self.vecteur = ValidateurPhysique.valider_vecteur(nouveau_vecteur)

    def obtenir_info_debug(self) -> Dict[str, Any]:
        """Étend les infos debug avec les propriétés cinématiques."""
        info = super().obtenir_info_debug()
        info.update(
            {
                "vecteur": self.vecteur.tolist(),
                "vitesse": self.vitesse(),
                "energie_cinetique": self.energie_cinetique(),
            }
        )
        return info


# ========================================================================
# ENTITÉS PHYSIQUES FONDAMENTALES
# ========================================================================


@dataclass
class Particule(EntiteMobile):
    """Entité fondamentale avec un vecteur de mouvement."""

    categorie: ClassVar[str] = "particules"

    def __post_init__(self):
        """Validation spécifique aux particules."""
        super().__post_init__()
        # Les particules ont typiquement des masses faibles
        if self.masse > 10.0:
            logger.warning(f"Particule avec masse élevée détectée: {self.masse}")


@dataclass
class Atome(EntiteMobile):
    """Première structure composite avec un type chimique validé."""

    type: str
    categorie: ClassVar[str] = "atomes"

    # Types d'atomes reconnus
    TYPES_VALIDES: ClassVar[List[str]] = [
        "hydrogene",
        "helium",
        "deuterium",
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

    def __post_init__(self):
        """Validation du type d'atome."""
        super().__post_init__()
        if self.type not in self.TYPES_VALIDES:
            logger.warning(
                f"Type d'atome inconnu: {self.type}, correction à 'hydrogene'"
            )
            self.type = "hydrogene"


@dataclass
class Etoile(EntiteMobile):
    """Objet massif en fusion nucléaire avec évolution chimique."""

    type: str
    temperature: float
    luminosite: float
    inventaire_elements: Dict[str, float] = field(default_factory=dict)
    categorie: ClassVar[str] = "etoiles"

    def __post_init__(self):
        """Validation étendue des propriétés stellaires."""
        super().__post_init__()

        # Validation du type d'étoile
        types_valides = [t.value for t in TypeEtoile]
        if self.type not in types_valides:
            logger.warning(
                f"Type d'étoile inconnu: {self.type}, correction à 'etoile_jeune'"
            )
            self.type = TypeEtoile.ETOILE_JEUNE.value

        # Validation température
        self.temperature = max(
            ConstantesPhysiques.TEMPERATURE_MIN,
            min(self.temperature, ConstantesPhysiques.TEMPERATURE_MAX),
        )

        # Validation luminosité
        self.luminosite = max(0.0, self.luminosite)

        # Initialisation inventaire si nécessaire
        if not self.inventaire_elements:
            self.inventaire_elements = {"hydrogene": self.masse * 0.73}

    def obtenir_element(self, element: str) -> float:
        """Retourne la quantité d'un élément dans l'étoile."""
        return self.inventaire_elements.get(element, 0.0)

    def consommer_element(self, element: str, quantite: float) -> float:
        """Consomme une quantité d'élément et retourne ce qui a été effectivement consommé."""
        disponible = self.obtenir_element(element)
        consomme = min(quantite, disponible)
        self.inventaire_elements[element] = disponible - consomme
        return consomme

    def ajouter_element(self, element: str, quantite: float) -> None:
        """Ajoute un élément à l'inventaire."""
        if quantite > 0:
            self.inventaire_elements[element] = self.obtenir_element(element) + quantite


# ========================================================================
# ENTITÉS PLANÉTAIRES
# ========================================================================


@dataclass
class Planete(EntiteMobile):
    """Monde rocheux ou gazeux orbitant autour d'une étoile."""

    type: str
    composition: Dict[str, float]
    temperature: float
    etoile_parente_id: str
    categorie: ClassVar[str] = "planetes"

    def __post_init__(self):
        """Validation étendue des propriétés planétaires."""
        super().__post_init__()

        # Validation du type de planète
        types_valides = [t.value for t in TypePlanete]
        if self.type not in types_valides:
            logger.warning(
                f"Type de planète inconnu: {self.type}, correction à 'composite'"
            )
            self.type = TypePlanete.COMPOSITE.value

        # Validation température
        self.temperature = max(0.0, min(self.temperature, 5000.0))

        # Validation composition
        if not self.composition:
            self.composition = {}

        # Normalisation de la composition (optionnel)
        total_composition = sum(self.composition.values())
        if total_composition > self.masse * 1.1:  # Tolérance 10%
            logger.warning(
                f"Composition planétaire incohérente (total: {total_composition}, masse: {self.masse})"
            )

    def est_habitable(self) -> bool:
        """Détermine si la planète est potentiellement habitable."""
        temp_ok = 200.0 <= self.temperature <= 400.0
        a_eau = (
            self.composition.get("oxygene", 0) > 0
            and self.composition.get("hydrogene", 0) > 0
        )
        masse_ok = self.masse > 30.0
        return temp_ok and a_eau and masse_ok

    def obtenir_element(self, element: str) -> float:
        """Retourne la quantité d'un élément dans la composition."""
        return self.composition.get(element, 0.0)


# ========================================================================
# ENTITÉS BIOLOGIQUES
# ========================================================================


@dataclass
class CelluleSimple(EntiteCosmique):
    """Première forme de vie : cellule primitive avec matériel génétique."""

    planete_hote_id: str
    adn: str
    age: int = field(default=0)
    categorie: ClassVar[str] = "cellules_simples"

    def __post_init__(self):
        """Validation de l'ADN et des propriétés biologiques."""
        super().__post_init__()

        # Validation ADN
        bases_valides = set("ATGC")
        if not all(base in bases_valides for base in self.adn):
            logger.warning(f"ADN invalide détecté : {self.adn[:20]}..., nettoyage")
            self.adn = "".join(c for c in self.adn if c in bases_valides)

        # Validation âge
        self.age = max(0, self.age)

        # Masse très faible pour cellules
        if self.masse > 1.0:
            logger.warning(f"Cellule avec masse élevée: {self.masse}, correction")
            self.masse = 0.001

    def complexite_genetique(self) -> float:
        """Calcule la complexité génétique basée sur la longueur et diversité ADN."""
        if not self.adn:
            return 0.0
        longueur = len(self.adn)
        diversite = len(set(self.adn))
        return longueur * diversite * 0.1


@dataclass
class OrganismeComplexe(EntiteCosmique):
    """Forme de vie évoluée avec complexité génétique mesurable."""

    planete_hote_id: str
    complexite_genetique: float
    espece: str = field(default="organisme_primitif")
    categorie: ClassVar[str] = "organismes_complexes"

    def __post_init__(self):
        """Validation des propriétés biologiques complexes."""
        super().__post_init__()
        self.complexite_genetique = max(0.0, self.complexite_genetique)


# ========================================================================
# ENTITÉS CIVILISATIONNELLES
# ========================================================================


@dataclass
class Civilisation(EntiteCosmique):
    """Société intelligente capable de développement technologique et d'expansion."""

    planete_mere_id: str
    niveau_technologique: int
    population: float
    expansion: float
    nom_espece: str = field(default="Inconnu")
    age_civilisation: int = field(default=0)
    categorie: ClassVar[str] = "civilisations"

    def __post_init__(self):
        """Validation des paramètres civilisationnels."""
        super().__post_init__()
        self.niveau_technologique = max(1, min(10, int(self.niveau_technologique)))
        self.expansion = max(0.0, min(1.0, float(self.expansion)))
        self.population = max(0.0, float(self.population))
        self.age_civilisation = max(0, int(self.age_civilisation))

    def peut_explorer_espace(self) -> bool:
        """Détermine si la civilisation peut explorer l'espace."""
        return self.niveau_technologique >= 6 and self.expansion > 0.3


# ========================================================================
# STRUCTURES COSMIQUES À GRANDE ÉCHELLE
# ========================================================================


@dataclass
class Galaxie(EntiteCosmique):
    """Structure gravitationnelle regroupant de nombreuses étoiles."""

    centre_de_masse: Union[list, tuple, NDArray]
    nombre_etoiles: int
    rayon: float
    type_galaxie: str = field(default="spirale")
    categorie: ClassVar[str] = "galaxies"

    def __post_init__(self):
        """Validation des propriétés galactiques."""
        super().__post_init__()
        self.centre_de_masse = ValidateurPhysique.valider_position(self.centre_de_masse)
        self.nombre_etoiles = max(0, int(self.nombre_etoiles))
        self.rayon = max(0.0, float(self.rayon))

        # Validation type galaxie
        types_valides = [t.value for t in TypeGalaxie]
        if self.type_galaxie not in types_valides:
            logger.warning(
                f"Type de galaxie inconnu: {self.type_galaxie}, correction à 'spirale'"
            )
            self.type_galaxie = TypeGalaxie.SPIRALE.value


@dataclass
class TrouNoir(EntiteCosmique):
    """Singularité gravitationnelle résultant d'un effondrement stellaire."""

    rayon_schwarzschild: float
    masse_accretee: float = field(default=0.0)
    activite: float = field(default=0.0)
    categorie: ClassVar[str] = "trous_noirs"

    def __post_init__(self):
        """Validation des paramètres du trou noir."""
        super().__post_init__()
        self.rayon_schwarzschild = max(0.0, float(self.rayon_schwarzschild))
        self.masse_accretee = max(0.0, float(self.masse_accretee))
        self.activite = max(0.0, min(1.0, float(self.activite)))

    def masse_totale(self) -> float:
        """Retourne la masse totale (masse + masse accrétée)."""
        return self.masse + self.masse_accretee


# ========================================================================
# GESTIONNAIRE PRINCIPAL DE L'UNIVERS
# ========================================================================


class EtatMonde:
    """
    L'Objet-Univers. Une structure de données contenant l'intégralité de l'état
    de la simulation. Version améliorée avec validation, performance et méthodes utilitaires.
    """

    def __init__(self):
        """Initialise un univers vide au temps zéro avec toutes les catégories d'entités."""
        logger.info("Instanciation d'un nouvel objet EtatMonde robuste...")

        # Temps et constantes physiques
        self.temps: int = 0
        self.constantes: Dict[str, float] = {
            "gravite": ConstantesPhysiques.GRAVITE,
            "expansion": ConstantesPhysiques.EXPANSION_BASE,
            "vitesse_lumiere": ConstantesPhysiques.VITESSE_LUMIERE,
            "constante_planck": ConstantesPhysiques.CONSTANTE_PLANCK,
            "energie_sombre": ConstantesPhysiques.ENERGIE_SOMBRE,
            "matiere_noire": ConstantesPhysiques.MATIERE_NOIRE,
        }

        # Dictionnaire d'entités avec initialisation explicite
        self.entites: Dict[str, List[EntiteCosmique]] = {}

        # Initialisation de toutes les catégories
        categories_entites = [
            "particules",
            "atomes",
            "etoiles",
            "planetes",
            "cellules_simples",
            "organismes_complexes",
            "civilisations",
            "galaxies",
            "trous_noirs",
        ]

        for categorie in categories_entites:
            self.entites[categorie] = []

        # Statistiques et métriques
        self.statistiques: Dict[str, Any] = defaultdict(float)

        # Journal des événements majeurs
        self.paliers: List[str] = []

        # Index pour recherche rapide par ID
        self._index_entites: Dict[str, EntiteCosmique] = {}

        logger.info("Nouvel univers robuste initialisé.")

    def ajouter_entite(self, entite: EntiteCosmique) -> bool:
        """
        Ajoute une entité à l'univers avec validation complète.

        Args:
            entite: L'entité à ajouter

        Returns:
            bool: True si ajout réussi, False sinon
        """
        if not isinstance(entite, EntiteCosmique):
            logger.error(f"Tentative d'ajout d'entité non-cosmique: {type(entite)}")
            return False

        categorie = entite.categorie
        if categorie not in self.entites:
            logger.warning(f"Catégorie inconnue '{categorie}', création automatique")
            self.entites[categorie] = []

        # Vérifier que l'ID n'existe pas déjà
        entite_id = str(entite.id)
        if entite_id in self._index_entites:
            logger.warning(f"Entité avec ID {entite_id[:8]}... déjà existante, ignorée")
            return False

        # Ajout avec mise à jour des métadonnées
        entite.temps_creation = self.temps
        entite.derniere_mise_a_jour = self.temps

        self.entites[categorie].append(entite)
        self._index_entites[entite_id] = entite

        logger.debug(f"Entité {type(entite).__name__} ajoutée à '{categorie}'")
        return True

    def supprimer_entite(self, entite: EntiteCosmique) -> bool:
        """
        Supprime une entité de l'univers avec nettoyage de l'index.

        Args:
            entite: L'entité à supprimer

        Returns:
            bool: True si suppression réussie, False sinon
        """
        categorie = entite.categorie
        entite_id = str(entite.id)

        if categorie in self.entites and entite in self.entites[categorie]:
            self.entites[categorie].remove(entite)
            self._index_entites.pop(entite_id, None)
            logger.debug(f"Entité {type(entite).__name__} supprimée de '{categorie}'")
            return True

        logger.warning(
            f"Tentative de suppression d'entité inexistante: {entite_id[:8]}..."
        )
        return False

    def obtenir_entite_par_id(self, entite_id: str) -> Optional[EntiteCosmique]:
        """Recherche rapide d'entité par ID."""
        return self._index_entites.get(entite_id)

    def obtenir_entites_par_type(self, type_entite: type) -> List[EntiteCosmique]:
        """
        Retourne toutes les entités d'un type donné de manière optimisée.

        Args:
            type_entite: La classe d'entité recherchée

        Returns:
            List: Liste des entités du type demandé
        """
        entites_trouvees = []
        for categorie_entites in self.entites.values():
            entites_trouvees.extend(
                [e for e in categorie_entites if isinstance(e, type_entite)]
            )
        return entites_trouvees

    def obtenir_entites_dans_rayon(
        self,
        position_centre: NDArray,
        rayon: float,
        categories_filtrees: Optional[List[str]] = None,
    ) -> List[EntiteCosmique]:
        """
        Trouve toutes les entités dans un rayon donné.

        Args:
            position_centre: Position du centre de recherche
            rayon: Rayon de recherche
            categories_filtrees: Liste des catégories à inclure (toutes si None)

        Returns:
            List: Entités trouvées dans le rayon
        """
        entites_proches = []
        categories = categories_filtrees or self.entites.keys()

        for categorie in categories:
            if categorie in self.entites:
                for entite in self.entites[categorie]:
                    distance = np.linalg.norm(entite.position - position_centre)
                    if distance <= rayon:
                        entites_proches.append(entite)

        return entites_proches

    def nettoyer_index(self) -> int:
        """
        Nettoie l'index des entités en supprimant les références obsolètes.

        Returns:
            int: Nombre d'entrées nettoyées
        """
        ids_actuels = set()
        for categorie_entites in self.entites.values():
            ids_actuels.update(str(e.id) for e in categorie_entites)

        ids_obsoletes = set(self._index_entites.keys()) - ids_actuels
        for id_obsolete in ids_obsoletes:
            del self._index_entites[id_obsolete]

        if ids_obsoletes:
            logger.info(
                f"Index nettoyé: {len(ids_obsoletes)} références obsolètes supprimées"
            )

        return len(ids_obsoletes)

    def obtenir_statistiques_avancees(self) -> Dict[str, Any]:
        """
        Calcule des statistiques complètes et optimisées sur l'état de l'univers.

        Returns:
            Dict: Métriques détaillées de l'univers
        """
        stats = {}

        # Comptages par catégorie
        for categorie, entites_list in self.entites.items():
            stats[f"nombre_{categorie}"] = len(entites_list)

        # Calculs physiques globaux
        toutes_entites = [e for cat in self.entites.values() for e in cat]
        if toutes_entites:
            masses = np.array([e.masse for e in toutes_entites])
            positions = np.array([e.position for e in toutes_entites])

            stats["masse_totale_univers"] = float(np.sum(masses))
            stats["centre_masse_univers"] = np.average(
                positions, weights=masses, axis=0
            ).tolist()

            # Dimensions de l'univers
            distances_centre = np.linalg.norm(
                positions - stats["centre_masse_univers"], axis=1
            )
            stats["rayon_univers"] = float(np.max(distances_centre))
            stats["diametre_univers"] = stats["rayon_univers"] * 2

        # Statistiques stellaires
        etoiles = self.entites.get("etoiles", [])
        if etoiles:
            temperatures = np.array([e.temperature for e in etoiles])
            luminosites = np.array([e.luminosite for e in etoiles])

            stats["temperature_stellaire_moyenne"] = float(np.mean(temperatures))
            stats["temperature_stellaire_max"] = float(np.max(temperatures))
            stats["luminosite_totale"] = float(np.sum(luminosites))

        # Statistiques planétaires
        planetes = self.entites.get("planetes", [])
        if planetes:
            temperatures_planetes = np.array([p.temperature for p in planetes])
            stats["temperature_planetaire_moyenne"] = float(
                np.mean(temperatures_planetes)
            )

            planetes_habitables = sum(1 for p in planetes if p.est_habitable())
            stats["planetes_habitables"] = planetes_habitables

        # Statistiques biologiques
        cellules = self.entites.get("cellules_simples", [])
        if cellules:
            complexites = np.array([c.complexite_genetique() for c in cellules])
            stats["complexite_genetique_moyenne"] = float(np.mean(complexites))
            stats["complexite_genetique_max"] = float(np.max(complexites))

        # Statistiques civilisationnelles
        civilisations = self.entites.get("civilisations", [])
        if civilisations:
            population_totale = sum(c.population for c in civilisations)
            niveau_tech_max = max(c.niveau_technologique for c in civilisations)
            civilisations_spatiales = sum(
                1 for c in civilisations if c.peut_explorer_espace()
            )

            stats["population_totale_intelligente"] = population_totale
            stats["niveau_technologique_maximum"] = niveau_tech_max
            stats["civilisations_spatiales"] = civilisations_spatiales

        return stats

    def detecter_paliers_emergents(self) -> List[str]:
        """
        Détecte automatiquement l'atteinte de nouveaux paliers d'évolution.
        Version optimisée avec paliers dynamiques.

        Returns:
            List: Nouveaux paliers détectés
        """
        nouveaux_paliers = []

        # Paliers de base
        paliers_possibles = {
            "PremiereNucleosynthese": lambda: len(self.entites["atomes"]) > 0,
            "PremiereEtoile": lambda: len(self.entites["etoiles"]) > 0,
            "PremierePlanete": lambda: len(self.entites["planetes"]) > 0,
            "PremiereVie": lambda: len(self.entites["cellules_simples"]) > 0,
            "PremierEvolution": lambda: len(self.entites["organismes_complexes"]) > 0,
            "PremiereCivilisation": lambda: len(self.entites["civilisations"]) > 0,
            "PremiereGalaxie": lambda: len(self.entites["galaxies"]) > 0,
            "PremierTrouNoir": lambda: len(self.entites["trous_noirs"]) > 0,
        }

        # Paliers avancés dynamiques
        paliers_avances = {
            "UniversMature": lambda: (
                len(self.entites["etoiles"]) > 50 and len(self.entites["planetes"]) > 10
            ),
            "EreBiologique": lambda: len(self.entites["cellules_simples"]) > 20,
            "EreIntelligente": lambda: len(self.entites["civilisations"]) > 3,
            "EreGalactique": lambda: len(self.entites["galaxies"]) > 5,
            "ErePostSingularite": lambda: len(self.entites["trous_noirs"]) > 10,
        }

        # Paliers de quantité
        paliers_quantite = {
            "BigBangAcheve": lambda: len(self.entites["particules"]) < 1000,
            "NucleosyntheseMassive": lambda: len(self.entites["atomes"]) > 5000,
            "FormationStellaireActive": lambda: len(self.entites["etoiles"]) > 100,
            "SystemesPlanetairesMatures": lambda: len(self.entites["planetes"]) > 50,
        }

        tous_paliers = {**paliers_possibles, **paliers_avances, **paliers_quantite}

        for nom_palier, condition in tous_paliers.items():
            if condition() and not any(nom_palier in p for p in self.paliers):
                nouveau_palier = f"[Temps: {self.temps}] - {nom_palier}"
                nouveaux_paliers.append(nouveau_palier)
                self.paliers.append(nouveau_palier)
                logger.info(f"Nouveau palier atteint: {nom_palier}")

        return nouveaux_paliers

    def valider_coherence(self) -> Dict[str, Any]:
        """
        Valide la cohérence globale de l'univers et retourne un rapport.

        Returns:
            Dict: Rapport de validation avec erreurs et avertissements
        """
        rapport = {
            "erreurs": [],
            "avertissements": [],
            "entites_validees": 0,
            "entites_corrigees": 0,
        }

        for categorie, entites_list in self.entites.items():
            for entite in entites_list:
                rapport["entites_validees"] += 1

                # Vérifications basiques
                if not np.all(np.isfinite(entite.position)):
                    rapport["erreurs"].append(
                        f"Position invalide pour {type(entite).__name__} {str(entite.id)[:8]}..."
                    )

                if entite.masse <= 0:
                    rapport["erreurs"].append(
                        f"Masse invalide pour {type(entite).__name__} {str(entite.id)[:8]}..."
                    )

                # Vérifications spécifiques aux types
                if isinstance(entite, EntiteMobile) and not np.all(
                    np.isfinite(entite.vecteur)
                ):
                    rapport["erreurs"].append(
                        f"Vecteur invalide pour {type(entite).__name__} {str(entite.id)[:8]}..."
                    )

        # Nettoyage de l'index si nécessaire
        entries_nettoyees = self.nettoyer_index()
        if entries_nettoyees > 0:
            rapport["avertissements"].append(
                f"Index nettoyé: {entries_nettoyees} entrées obsolètes"
            )

        return rapport

    def obtenir_resume_univers(self) -> Dict[str, Any]:
        """
        Génère un résumé complet de l'état de l'univers.

        Returns:
            Dict: Résumé structuré de l'univers
        """
        stats = self.obtenir_statistiques_avancees()

        return {
            "temps_simulation": self.temps,
            "inventaire_entites": {
                cat: len(entites) for cat, entites in self.entites.items() if entites
            },
            "metriques_physiques": {
                "masse_totale": stats.get("masse_totale_univers", 0),
                "rayon_univers": stats.get("rayon_univers", 0),
                "centre_masse": stats.get("centre_masse_univers", [0, 0, 0]),
            },
            "paliers_atteints": len(self.paliers),
            "dernier_palier": self.paliers[-1] if self.paliers else "Aucun",
            "entites_totales": sum(len(cat) for cat in self.entites.values()),
            "performance": {
                "entites_indexees": len(self._index_entites),
                "categories_actives": len(
                    [cat for cat, ents in self.entites.items() if ents]
                ),
            },
        }
