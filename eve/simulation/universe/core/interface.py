# Fichier : interface.py
# Version 11.0 ("Architecture MVC Robuste") - Interface refactorisée et optimisée

"""
Module interface graphique du Projet Monde.
Fournit l'interface utilisateur pour visualiser et contrôler la simulation.
Architecture MVC avec séparation des responsabilités et gestion d'erreurs robuste.
"""

import json
import logging
from typing import Optional, Dict, Any, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray

from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPainter,
    QCursor,
    QWheelEvent,
    QMouseEvent,
    QRadialGradient,
    QFont,
)
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QSplitter,
    QPushButton,
    QComboBox,
    QLineEdit,
    QStatusBar,
    QProgressBar,
    QGroupBox,
)

logger = logging.getLogger(__name__)

# ========================================================================
# CONFIGURATION ET CONSTANTES
# ========================================================================


class CategorieEntite(Enum):
    """Énumération des catégories d'entités reconnues."""

    PARTICULES = "particules"
    ATOMES = "atomes"
    ETOILES = "etoiles"
    PLANETES = "planetes"
    CELLULES_SIMPLES = "cellules_simples"
    ORGANISMES_COMPLEXES = "organismes_complexes"
    CIVILISATIONS = "civilisations"
    GALAXIES = "galaxies"
    TROUS_NOIRS = "trous_noirs"


@dataclass
class ConfigRendu:
    """Configuration du rendu visuel d'une catégorie d'entité."""

    nom_affiche: str
    couleur_principale: QColor
    taille_base: float
    taille_min: float = 2.0
    taille_max: float = 25.0
    utilise_temperature: bool = False
    utilise_masse: bool = False
    contour_couleur: Optional[QColor] = None
    contour_epaisseur: float = 0.0


class ConfigurationRendu:
    """Configuration centralisée du rendu visuel."""

    CONFIGURATIONS: Dict[CategorieEntite, ConfigRendu] = {
        CategorieEntite.PARTICULES: ConfigRendu(
            nom_affiche="Particules",
            couleur_principale=QColor(200, 200, 200, 180),
            taille_base=2.0,
            taille_min=1.0,
            taille_max=3.0,
        ),
        CategorieEntite.ATOMES: ConfigRendu(
            nom_affiche="Atomes",
            couleur_principale=QColor("cyan"),
            taille_base=3.0,
            taille_min=2.0,
            taille_max=5.0,
        ),
        CategorieEntite.ETOILES: ConfigRendu(
            nom_affiche="Étoiles",
            couleur_principale=QColor("yellow"),
            taille_base=8.0,
            taille_min=4.0,
            taille_max=15.0,
            utilise_temperature=True,
            utilise_masse=True,
        ),
        CategorieEntite.PLANETES: ConfigRendu(
            nom_affiche="Planètes",
            couleur_principale=QColor("orange"),
            taille_base=5.0,
            taille_min=3.0,
            taille_max=8.0,
        ),
        CategorieEntite.CELLULES_SIMPLES: ConfigRendu(
            nom_affiche="Cellules",
            couleur_principale=QColor("lime"),
            taille_base=2.5,
            taille_min=1.5,
            taille_max=4.0,
        ),
        CategorieEntite.ORGANISMES_COMPLEXES: ConfigRendu(
            nom_affiche="Organismes",
            couleur_principale=QColor("green"),
            taille_base=4.0,
            taille_min=2.5,
            taille_max=6.0,
        ),
        CategorieEntite.CIVILISATIONS: ConfigRendu(
            nom_affiche="Civilisations",
            couleur_principale=QColor("gold"),
            taille_base=8.0,
            taille_min=5.0,
            taille_max=12.0,
        ),
        CategorieEntite.GALAXIES: ConfigRendu(
            nom_affiche="Galaxies",
            couleur_principale=QColor("purple"),
            taille_base=20.0,
            taille_min=15.0,
            taille_max=30.0,
        ),
        CategorieEntite.TROUS_NOIRS: ConfigRendu(
            nom_affiche="Trous Noirs",
            couleur_principale=QColor("black"),
            taille_base=10.0,
            taille_min=6.0,
            taille_max=15.0,
            contour_couleur=QColor("red"),
            contour_epaisseur=2.0,
        ),
    }


class ConstantesInterface:
    """Constantes pour l'interface utilisateur."""

    # Géométrie
    FENETRE_LARGEUR_DEFAUT = 1600
    FENETRE_HAUTEUR_DEFAUT = 900
    PANNEAU_DROIT_LARGEUR = 400

    # Rendu
    ZOOM_FACTEUR = 1.15
    MARGE_RECENTRAGE_FACTEUR = 1.2
    SEUIL_EXTENSION_UNIVERS = 15.0
    TAILLE_SCENE_MINIMALE = 100.0

    # Performance
    MAX_ENTITES_DEBUG = 50000
    INTERVALLE_STATS_MS = 1000

    # Couleurs thème
    COULEUR_FOND = QColor(5, 5, 15)
    COULEUR_SELECTION = QColor("lime")
    COULEUR_STATUT_SUCCES = "lightgreen"
    COULEUR_STATUT_ERREUR = "red"


# ========================================================================
# WIDGETS PERSONNALISÉS OPTIMISÉS
# ========================================================================


class EntiteGraphique(QGraphicsEllipseItem):
    """Item graphique optimisé représentant une entité cosmique."""

    def __init__(
        self, entite_id: str, parent_fenetre: QObject, categorie: str = "inconnu"
    ):
        super().__init__()
        self.entite_id = entite_id
        self.parent_fenetre = parent_fenetre
        self.categorie = categorie
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)

    def hoverEnterEvent(self, event: Any) -> None:
        """Gère l'entrée du curseur sur l'entité."""
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: Any) -> None:
        """Gère la sortie du curseur de l'entité."""
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Gère le clic sur l'entité avec validation."""
        try:
            if hasattr(self.parent_fenetre, "selectionner_entite"):
                self.parent_fenetre.selectionner_entite(self.entite_id)
        except Exception as e:
            logger.error(f"Erreur lors de la sélection d'entité {self.entite_id}: {e}")
        super().mousePressEvent(event)


class VueInteractive(QGraphicsView):
    """Vue personnalisée avec navigation optimisée et gestion d'erreurs."""

    clicVide = pyqtSignal()

    def __init__(
        self,
        scene: QGraphicsScene,
        parent_fenetre: QObject,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(scene, parent)
        self.parent_fenetre = parent_fenetre
        self._configurer_rendu()
        self._derniere_position_centre: Optional[Tuple[float, float]] = None

    def _configurer_rendu(self) -> None:
        """Configure les options de rendu pour performance optimale."""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setBackgroundBrush(ConstantesInterface.COULEUR_FOND)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Gère le zoom avec validation des limites."""
        try:
            zoom_facteur = ConstantesInterface.ZOOM_FACTEUR
            angle_delta = event.angleDelta().y()

            if angle_delta > 0:
                self.scale(zoom_facteur, zoom_facteur)
            else:
                self.scale(1.0 / zoom_facteur, 1.0 / zoom_facteur)

        except Exception as e:
            logger.error(f"Erreur lors du zoom: {e}")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Gère les clics avec détection de clic dans le vide."""
        try:
            item = self.itemAt(event.pos())
            if item is None:
                self.clicVide.emit()
                if hasattr(self.parent_fenetre, "deselectionner_entite"):
                    self.parent_fenetre.deselectionner_entite()
        except Exception as e:
            logger.error(f"Erreur lors du clic souris: {e}")

        super().mousePressEvent(event)


# ========================================================================
# GESTIONNAIRES SPÉCIALISÉS
# ========================================================================


class GestionnaireRendu:
    """Gestionnaire centralisé du rendu des entités avec optimisations."""

    def __init__(self):
        self.cache_couleurs: Dict[str, QColor] = {}
        self.cache_configurations: Dict[str, ConfigRendu] = {}

    def obtenir_couleur_temperature(self, temperature: float) -> QColor:
        """Retourne une couleur basée sur la température stellaire (corps noir)."""
        # Cache pour éviter recalculs
        temp_key = f"temp_{int(temperature/100)*100}"
        if temp_key in self.cache_couleurs:
            return self.cache_couleurs[temp_key]

        if temperature > 15000:
            couleur = QColor("#a2c8ff")  # Bleu blanc (très chaud)
        elif temperature > 10000:
            couleur = QColor("#ffffff")  # Blanc
        elif temperature > 7000:
            couleur = QColor("#fff4e8")  # Blanc jaunâtre
        elif temperature > 5000:
            couleur = QColor("#ffe8c5")  # Jaune
        elif temperature > 3500:
            couleur = QColor("#ffc575")  # Orange
        else:
            couleur = QColor("#ff9d45")  # Rouge orangé (froid)

        self.cache_couleurs[temp_key] = couleur
        return couleur

    def obtenir_couleur_planete(self, type_planete: str) -> QColor:
        """Retourne la couleur d'une planète selon son type."""
        couleurs_planetes = {
            "tellurique": QColor("brown"),
            "gazeuse": QColor("lightblue"),
            "riche_carbone": QColor("darkgray"),
            "riche_oxygene": QColor("lightcoral"),
            "composite": QColor("orange"),
        }
        return couleurs_planetes.get(type_planete, QColor("orange"))

    def calculer_taille_entite(self, categorie: str, data: Dict[str, Any]) -> float:
        """Calcule la taille d'affichage d'une entité selon ses propriétés."""
        try:
            # Vérifier si la catégorie existe
            categorie_enum = None
            for cat in CategorieEntite:
                if cat.value == categorie:
                    categorie_enum = cat
                    break

            if not categorie_enum:
                return 3.0  # Taille par défaut

            config = ConfigurationRendu.CONFIGURATIONS[categorie_enum]
            taille = config.taille_base

            # Ajustement selon masse si applicable
            if config.utilise_masse and "masse" in data:
                masse = data["masse"]
                facteur_masse = np.log10(max(masse, 0.1)) / 2
                taille = config.taille_base + facteur_masse

            return max(config.taille_min, min(taille, config.taille_max))

        except Exception as e:
            logger.warning(f"Erreur calcul taille pour {categorie}: {e}")
            return 3.0


class ValidateurDonnees:
    """Validateur des données JSON reçues de la simulation."""

    @staticmethod
    def valider_donnees_entite(data: Dict[str, Any]) -> bool:
        """Valide les données d'une entité."""
        # Champs requis
        champs_requis = ["id", "categorie", "position", "masse"]

        for champ in champs_requis:
            if champ not in data:
                logger.warning(f"Champ requis manquant: {champ}")
                return False

        # Validation position
        position = data.get("position", [])
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            logger.warning(f"Position invalide: {position}")
            return False

        # Validation masse
        masse = data.get("masse", 0)
        if not isinstance(masse, (int, float)) or masse <= 0:
            logger.warning(f"Masse invalide: {masse}")
            return False

        return True

    @staticmethod
    def valider_json_simulation(etat_json: str) -> Optional[Dict[str, Any]]:
        """Valide et parse le JSON de simulation."""
        try:
            donnees = json.loads(etat_json)

            # Vérification structure minimale
            champs_requis = ["temps", "statistiques", "paliers", "entites"]
            for champ in champs_requis:
                if champ not in donnees:
                    logger.error(f"Structure JSON invalide: champ '{champ}' manquant")
                    return None

            return donnees

        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur validation JSON: {e}")
            return None


# ========================================================================
# GESTIONNAIRE DE SCÈNE OPTIMISÉ
# ========================================================================


class GestionnaireScene:
    """Gestionnaire optimisé de la scène graphique avec cache et performances."""

    def __init__(self, scene: QGraphicsScene, vue: VueInteractive):
        self.scene = scene
        self.vue = vue
        self.gestionnaire_rendu = GestionnaireRendu()
        self.items_graphiques: Dict[str, EntiteGraphique] = {}
        self.premiere_mise_a_jour = True
        self.derniere_position_centre: Optional[NDArray] = None
        self.derniere_taille_univers = 0.0

    def mettre_a_jour_scene(self, donnees_entites: Dict[str, Any]) -> None:
        """Met à jour la scène graphique de manière optimisée."""
        try:
            # Phase 1: Collecte et validation
            donnees_valides = self._collecter_donnees_valides(donnees_entites)
            if not donnees_valides:
                return

            ids_recus, toutes_positions = donnees_valides

            # Phase 2: Mise à jour des items graphiques
            self._mettre_a_jour_items_graphiques(donnees_entites, ids_recus)

            # Phase 3: Gestion du viewport
            self._gerer_viewport(toutes_positions)

            # Phase 4: Nettoyage
            self._nettoyer_items_obsoletes(ids_recus)

        except Exception as e:
            logger.error(f"Erreur critique mise à jour scène: {e}")

    def _collecter_donnees_valides(
        self, donnees_entites: Dict[str, Any]
    ) -> Optional[Tuple[Set[str], List[List[float]]]]:
        """Collecte et valide les données d'entités."""
        ids_recus: Set[str] = set()
        toutes_positions: List[List[float]] = []
        nombre_entites_total = 0
        entites_invalides = 0

        for nom_categorie, entites_data in donnees_entites.items():
            if not isinstance(entites_data, list):
                continue

            nombre_entites_total += len(entites_data)

            for data in entites_data:
                if not ValidateurDonnees.valider_donnees_entite(data):
                    entites_invalides += 1
                    continue

                ids_recus.add(data["id"])
                position = data.get("position", [])
                if len(position) >= 2:
                    toutes_positions.append(position)

        # Logging des statistiques
        if nombre_entites_total > 0:
            logger.debug(
                f"Scène: {nombre_entites_total} entités, "
                f"{len(toutes_positions)} positions valides, "
                f"{entites_invalides} invalides"
            )

        return (ids_recus, toutes_positions) if ids_recus else None

    def _mettre_a_jour_items_graphiques(
        self, donnees_entites: Dict[str, Any], ids_recus: Set[str]
    ) -> None:
        """Met à jour les items graphiques de manière optimisée."""
        for nom_categorie, entites_data in donnees_entites.items():
            if not isinstance(entites_data, list):
                continue

            for data in entites_data:
                if not ValidateurDonnees.valider_donnees_entite(data):
                    continue

                entite_id = data["id"]

                # Créer ou récupérer item
                if entite_id in self.items_graphiques:
                    item = self.items_graphiques[entite_id]
                else:
                    item = EntiteGraphique(
                        entite_id, self.vue.parent_fenetre, nom_categorie
                    )
                    self.items_graphiques[entite_id] = item
                    self.scene.addItem(item)

                # Mise à jour position
                position = data["position"]
                item.setPos(float(position[0]), float(position[1]))

                # Mise à jour apparence
                self._appliquer_style_entite(item, data, nom_categorie)

    def _appliquer_style_entite(
        self, item: EntiteGraphique, data: Dict[str, Any], categorie: str
    ) -> None:
        """Applique le style à une entité selon sa catégorie."""
        try:
            # Obtenir configuration
            categorie_enum = None
            for cat in CategorieEntite:
                if cat.value == categorie:
                    categorie_enum = cat
                    break

            if not categorie_enum:
                # Entité inconnue
                self._appliquer_style_inconnu(
                    item, categorie, data.get("position", [0, 0])
                )
                return

            config = ConfigurationRendu.CONFIGURATIONS[categorie_enum]

            # Calcul de la couleur
            couleur = self._calculer_couleur_entite(config, data, categorie)

            # Calcul de la taille
            taille = self.gestionnaire_rendu.calculer_taille_entite(categorie, data)

            # Application du style
            pinceau = QBrush(couleur)
            item.setBrush(pinceau)
            item.setRect(-taille / 2, -taille / 2, taille, taille)

            # Contour si spécifié
            if config.contour_couleur and config.contour_epaisseur > 0:
                item.setPen(QPen(config.contour_couleur, config.contour_epaisseur))
            else:
                item.setPen(QPen(Qt.PenStyle.NoPen))

        except Exception as e:
            logger.error(f"Erreur style entité {item.entite_id}: {e}")

    def _calculer_couleur_entite(
        self, config: ConfigRendu, data: Dict[str, Any], categorie: str
    ) -> QColor:
        """Calcule la couleur d'une entité selon ses propriétés."""
        # Couleur basée sur température pour étoiles
        if config.utilise_temperature and "temperature" in data:
            return self.gestionnaire_rendu.obtenir_couleur_temperature(
                data["temperature"]
            )

        # Couleur basée sur type pour planètes
        if categorie == "planetes" and "type" in data:
            return self.gestionnaire_rendu.obtenir_couleur_planete(data["type"])

        return config.couleur_principale

    def _appliquer_style_inconnu(
        self, item: EntiteGraphique, categorie: str, position: List[float]
    ) -> None:
        """Applique un style pour les entités de catégorie inconnue."""
        item.setBrush(QBrush(QColor("magenta")))
        item.setRect(-2.0, -2.0, 4.0, 4.0)
        logger.debug(f"Entité inconnue '{categorie}' à {position[:2]}")

    def _gerer_viewport(self, toutes_positions: List[List[float]]) -> None:
        """Gère le viewport avec recentrage intelligent."""
        if not toutes_positions or len(self.items_graphiques) == 0:
            return

        try:
            positions_np = np.array(toutes_positions)
            centre = np.mean(positions_np, axis=0)
            rayon_max = np.max(np.linalg.norm(positions_np - centre, axis=1))

            if self.premiere_mise_a_jour:
                self._recentrage_initial(centre, rayon_max)
            elif rayon_max > ConstantesInterface.SEUIL_EXTENSION_UNIVERS:
                self._ajuster_scene_expansion(centre, rayon_max)

        except Exception as e:
            logger.error(f"Erreur gestion viewport: {e}")

    def _recentrage_initial(self, centre: NDArray, rayon_max: float) -> None:
        """Effectue le recentrage initial de la vue."""
        marge = max(
            rayon_max * ConstantesInterface.MARGE_RECENTRAGE_FACTEUR,
            ConstantesInterface.TAILLE_SCENE_MINIMALE,
        )

        self.scene.setSceneRect(
            centre[0] - marge, centre[1] - marge, marge * 2, marge * 2
        )

        self.vue.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        self.premiere_mise_a_jour = False
        self.derniere_position_centre = centre[:2]
        self.derniere_taille_univers = rayon_max

        logger.debug(f"Recentrage initial: centre={centre[:2]}, rayon={rayon_max:.1f}")

    def _ajuster_scene_expansion(self, centre: NDArray, rayon_max: float) -> None:
        """Ajuste la scène lors de l'expansion de l'univers."""
        marge = rayon_max * ConstantesInterface.MARGE_RECENTRAGE_FACTEUR

        self.scene.setSceneRect(
            centre[0] - marge, centre[1] - marge, marge * 2, marge * 2
        )

        self.derniere_taille_univers = rayon_max
        logger.debug(f"Scène ajustée pour expansion: nouveau rayon={marge:.1f}")

    def _nettoyer_items_obsoletes(self, ids_recus: Set[str]) -> None:
        """Supprime les items graphiques obsolètes."""
        ids_a_supprimer = set(self.items_graphiques.keys()) - ids_recus

        if ids_a_supprimer:
            logger.debug(f"Nettoyage: {len(ids_a_supprimer)} entités obsolètes")

            for entite_id in ids_a_supprimer:
                item = self.items_graphiques.pop(entite_id, None)
                if item:
                    self.scene.removeItem(item)


# ========================================================================
# GESTIONNAIRE D'AFFICHAGE DES DONNÉES
# ========================================================================


class GestionnaireAffichage:
    """Gestionnaire de l'affichage des statistiques et informations."""

    def __init__(self):
        self.cache_html: Dict[str, str] = {}

    def generer_html_statistiques(self, donnees: Dict[str, Any]) -> str:
        """Génère le HTML des statistiques avec mise en cache."""
        stats = donnees.get("statistiques", {})
        temps = donnees.get("temps", 0)

        # Cache key basé sur le temps et nombre d'entités
        cache_key = f"stats_{temps}_{hash(str(sorted(stats.items())))}"
        if cache_key in self.cache_html:
            return self.cache_html[cache_key]

        html = f"<b>Temps de Simulation :</b> {temps:,} cycles<hr>"
        html += "<b><u>Inventaire de l'Univers</u></b><br>"

        # Statistiques par catégorie avec couleurs
        for categorie_enum in CategorieEntite:
            config = ConfigurationRendu.CONFIGURATIONS[categorie_enum]
            nombre = stats.get(f"nombre{categorie_enum.value}", 0)

            if nombre > 0:
                couleur = config.couleur_principale.name()
                html += (
                    f"<b style='color: {couleur}'>{config.nom_affiche} :</b> "
                    f"{nombre:,}<br>"
                )

        # Métriques physiques
        html += "<br><b><u>Métriques Physiques</u></b><br>"

        if "tailleunivers" in stats:
            taille = stats["tailleunivers"]
            html += f"<b>Diamètre Univers :</b> {taille:,.1f} unités<br>"

        # Statistiques avancées conditionnelles
        stats_avancees = [
            ("temperature_moyenne_etoiles", "Temp. Stellaire Moy.", ":.0f", "K"),
            ("population_totale_civilisations", "Population Intelligente", ":,.0f", ""),
            ("niveau_technologique_max", "Niveau Tech. Max", "", "/10"),
        ]

        for cle, nom, format_spec, unite in stats_avancees:
            if cle in stats and stats[cle] > 0:
                valeur = stats[cle]
                html += f"<b>{nom} :</b> {valeur:{format_spec}}{unite}<br>"

        # Performance
        if "dureecycle" in stats:
            duree_ms = stats["dureecycle"] * 1000
            html += f"<hr><b><u>Performance</u></b><br>"
            html += f"<b>Durée moy. Cycle :</b> {duree_ms:.2f} ms<br>"

        self.cache_html[cache_key] = html
        return html

    def generer_html_entite(self, entite_data: Dict[str, Any]) -> str:
        """Génère le HTML détaillé d'une entité sélectionnée."""
        try:
            html = f"<b>ID :</b> {entite_data['id'][:8]}...<br>"
            html += f"<b>Catégorie :</b> {entite_data.get('categorie', 'N/A').replace('_', ' ').title()}<br>"

            # Position
            pos = entite_data.get("position", [0, 0, 0])
            html += f"<b>Position :</b> [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]<br>"

            # Propriétés communes
            if "type" in entite_data:
                html += f"<b>Type :</b> {entite_data['type']}<br>"
            html += f"<b>Masse :</b> {entite_data.get('masse', 0):.2f}<br>"

            # Propriétés spécifiques selon catégorie
            categorie = entite_data.get("categorie", "")
            html += self._generer_html_specifique_categorie(entite_data, categorie)

            return html

        except Exception as e:
            logger.error(f"Erreur génération HTML entité: {e}")
            return "<b>Erreur d'affichage</b>"

    def _generer_html_specifique_categorie(
        self, data: Dict[str, Any], categorie: str
    ) -> str:
        """Génère le HTML spécifique à une catégorie d'entité."""
        html = ""

        try:
            if categorie == "etoiles":
                html += f"<b>Température :</b> {data.get('temperature', 0):.0f} K<br>"
                html += f"<b>Luminosité :</b> {data.get('luminosite', 0):.2f} L☉<br>"

                if "inventaire_elements" in data:
                    html += "<b>Éléments :</b><br>"
                    for element, quantite in data["inventaire_elements"].items():
                        if quantite > 0.1:
                            html += f"  • {element.title()}: {quantite:.1f}<br>"

            elif categorie == "planetes":
                html += f"<b>Température :</b> {data.get('temperature', 0):.1f} K<br>"
                etoile_id = data.get("etoile_parente_id", "N/A")
                html += f"<b>Étoile Parente :</b> {etoile_id[:8]}...<br>"

                if "composition" in data:
                    html += "<b>Composition :</b><br>"
                    for element, quantite in data["composition"].items():
                        if quantite > 0.1:
                            html += f"  • {element.title()}: {quantite:.1f}<br>"

            elif categorie == "cellules_simples":
                planete_id = data.get("planete_hote_id", "N/A")
                html += f"<b>Planète Hôte :</b> {planete_id[:8]}...<br>"
                html += f"<b>Longueur ADN :</b> {len(data.get('adn', ''))} bases<br>"
                if "age" in data:
                    html += f"<b>Âge :</b> {data['age']} cycles<br>"

            elif categorie == "civilisations":
                planete_id = data.get("planete_mere_id", "N/A")
                html += f"<b>Planète Mère :</b> {planete_id[:8]}...<br>"
                html += f"<b>Population :</b> {data.get('population', 0):,.0f}<br>"
                html += (
                    f"<b>Niveau Tech :</b> {data.get('niveau_technologique', 0)}/10<br>"
                )

        except Exception as e:
            logger.warning(f"Erreur HTML catégorie {categorie}: {e}")

        return html


# ========================================================================
# FENÊTRE PRINCIPALE REFACTORISÉE
# ========================================================================


class FenetrePrincipale(QMainWindow):
    """Fenêtre principale avec architecture MVC et gestion d'erreurs robuste."""

    # Signaux
    pause_demandee = pyqtSignal()
    reprise_demandee = pyqtSignal()
    vitesse_changee = pyqtSignal(str)
    sauvegarde_demandee = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._initialiser_fenetre()
        self._creer_composants()
        self._connecter_signaux()

        # Gestionnaires spécialisés
        self.gestionnaire_scene: Optional[GestionnaireScene] = None
        self.gestionnaire_affichage = GestionnaireAffichage()

        # État interne
        self.donnees_actuelles: Dict[str, Any] = {}
        self.id_selection_actuelle: Optional[str] = None

        # Timer pour performance
        self.timer_stats = QTimer()
        self.timer_stats.timeout.connect(self._mettre_a_jour_performance)
        self.timer_stats.start(ConstantesInterface.INTERVALLE_STATS_MS)

    def _initialiser_fenetre(self) -> None:
        """Initialise les propriétés de base de la fenêtre."""
        self.setWindowTitle("Projet Monde - Chronoscope v11.0 (Architecture MVC)")
        self.setGeometry(
            100,
            100,
            ConstantesInterface.FENETRE_LARGEUR_DEFAUT,
            ConstantesInterface.FENETRE_HAUTEUR_DEFAUT,
        )

        # Barre de statut avec barre de progression
        self.barre_statut = QStatusBar()
        self.barre_progression = QProgressBar()
        self.barre_progression.setVisible(False)
        self.barre_statut.addPermanentWidget(self.barre_progression)
        self.setStatusBar(self.barre_statut)

    def _creer_composants(self) -> None:
        """Crée tous les composants de l'interface."""
        # Scène et vue principale
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-200, -200, 400, 400)

        self.vue = VueInteractive(self.scene, self)
        self.gestionnaire_scene = GestionnaireScene(self.scene, self.vue)

        # Panneau de droite
        dashboard_widget = self._creer_panneau_droit()

        # Layout principal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.vue)
        main_splitter.addWidget(dashboard_widget)
        main_splitter.setSizes([1200, ConstantesInterface.PANNEAU_DROIT_LARGEUR])

        self.setCentralWidget(main_splitter)

    def _creer_panneau_droit(self) -> QWidget:
        """Crée le panneau de droite avec sections organisées."""
        conteneur = QWidget()
        layout = QVBoxLayout(conteneur)
        layout.setContentsMargins(5, 5, 5, 5)

        # Sections d'affichage
        self.affichage_stats = self._creer_section_stats()
        self.journal_historique = self._creer_section_journal()
        self.panneau_selection = self._creer_section_selection()

        # Panneau de contrôle
        controle_widget = self._creer_panneau_controle()

        # Assembly avec splitter vertical
        splitter_vertical = QSplitter(Qt.Orientation.Vertical)
        splitter_vertical.addWidget(self.affichage_stats)
        splitter_vertical.addWidget(self.journal_historique)
        splitter_vertical.addWidget(self.panneau_selection)
        splitter_vertical.setSizes([300, 200, 150])

        layout.addWidget(splitter_vertical)
        layout.addWidget(controle_widget)

        return conteneur

    def _creer_section_stats(self) -> QGroupBox:
        """Crée la section des statistiques."""
        group = QGroupBox("📊 TABLEAU DE BORD COSMIQUE")
        layout = QVBoxLayout(group)

        self.text_stats = QTextEdit()
        self.text_stats.setReadOnly(True)
        self.text_stats.setFont(QFont("Consolas", 10))

        layout.addWidget(self.text_stats)
        return group

    def _creer_section_journal(self) -> QGroupBox:
        """Crée la section du journal historique."""
        group = QGroupBox("📜 JOURNAL HISTORIQUE")
        layout = QVBoxLayout(group)

        self.text_journal = QTextEdit()
        self.text_journal.setReadOnly(True)
        self.text_journal.setFont(QFont("Consolas", 9))

        layout.addWidget(self.text_journal)
        return group

    def _creer_section_selection(self) -> QGroupBox:
        """Crée la section de sélection d'entité."""
        self.group_selection = QGroupBox("🎯 ENTITÉ SÉLECTIONNÉE")
        layout = QVBoxLayout(self.group_selection)

        self.text_selection = QTextEdit()
        self.text_selection.setReadOnly(True)
        self.text_selection.setFont(QFont("Consolas", 9))

        layout.addWidget(self.text_selection)
        self.group_selection.setVisible(False)
        return self.group_selection

    def _creer_panneau_controle(self) -> QGroupBox:
        """Crée le panneau de contrôle de la simulation."""
        group = QGroupBox("⚙️ CONTRÔLE SIMULATION")
        layout = QVBoxLayout(group)

        # Boutons de contrôle
        boutons_layout = QHBoxLayout()
        self.bouton_pause = QPushButton("⏸ Pause")
        self.bouton_reprise = QPushButton("▶ Reprise")
        self.bouton_reprise.setEnabled(False)

        boutons_layout.addWidget(self.bouton_pause)
        boutons_layout.addWidget(self.bouton_reprise)

        # Contrôle de vitesse
        vitesse_layout = QHBoxLayout()
        self.combo_vitesse = QComboBox()
        self.combo_vitesse.addItems(
            ["x1", "x10", "x100", "x1000", "x10000", "Personnalisé"]
        )

        self.input_vitesse = QLineEdit("1")
        self.input_vitesse.setFixedWidth(80)
        self.input_vitesse.setVisible(False)

        vitesse_layout.addWidget(QLabel("Vitesse :"))
        vitesse_layout.addWidget(self.combo_vitesse)
        vitesse_layout.addWidget(self.input_vitesse)

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButton("💾 Sauvegarder")

        # Assembly
        layout.addLayout(boutons_layout)
        layout.addLayout(vitesse_layout)
        layout.addWidget(self.bouton_sauvegarde)

        return group

    def _connecter_signaux(self) -> None:
        """Connecte tous les signaux de l'interface."""
        try:
            # Signaux de contrôle (seront connectés après création des widgets)
            pass
        except Exception as e:
            logger.error(f"Erreur connexion signaux: {e}")

    def _connecter_signaux_controle(self) -> None:
        """Connecte les signaux de contrôle après création des widgets."""
        self.bouton_pause.clicked.connect(self._on_pause)
        self.bouton_reprise.clicked.connect(self._on_reprise)
        self.combo_vitesse.currentIndexChanged.connect(self._on_vitesse_combo_changee)
        self.input_vitesse.returnPressed.connect(self._on_vitesse_input_changee)
        self.bouton_sauvegarde.clicked.connect(self.sauvegarde_demandee.emit)

        # Signal de clic dans le vide
        if self.vue:
            self.vue.clicVide.connect(self.deselectionner_entite)

    # ========================================================================
    # MÉTHODES PUBLIQUES PRINCIPALES
    # ========================================================================

    def mise_a_jour(self, etat_json: str) -> None:
        """Point d'entrée principal pour mise à jour de l'interface."""
        try:
            # Validation des données
            donnees_valides = ValidateurDonnees.valider_json_simulation(etat_json)
            if not donnees_valides:
                return

            self.donnees_actuelles = donnees_valides

            # Mise à jour des composants
            self._mettre_a_jour_dashboard(donnees_valides)

            if self.gestionnaire_scene:
                entites_data = donnees_valides.get("entites", {})
                self.gestionnaire_scene.mettre_a_jour_scene(entites_data)

            # Maintenir sélection si applicable
            if self.id_selection_actuelle:
                self.selectionner_entite(self.id_selection_actuelle)

        except Exception as e:
            logger.error(f"Erreur mise à jour interface: {e}")
            self.afficher_notification_sauvegarde(
                False, f"Erreur mise à jour: {str(e)[:50]}..."
            )

    def selectionner_entite(self, entite_id: str) -> None:
        """Sélectionne une entité et affiche ses détails."""
        try:
            # Retirer sélection précédente
            self._retirer_selection_precedente()

            # Chercher l'entité
            entite_trouvee = self._rechercher_entite_par_id(entite_id)

            if entite_trouvee:
                self._afficher_details_entite(entite_trouvee, entite_id)
                self._mettre_en_evidence_entite(entite_id)
                self.id_selection_actuelle = entite_id
            else:
                logger.warning(f"Entité {entite_id} introuvable pour sélection")
                self.deselectionner_entite()

        except Exception as e:
            logger.error(f"Erreur sélection entité {entite_id}: {e}")
            self.deselectionner_entite()

    def deselectionner_entite(self) -> None:
        """Désélectionne l'entité actuelle."""
        try:
            if self.id_selection_actuelle and self.gestionnaire_scene:
                items = self.gestionnaire_scene.items_graphiques
                if self.id_selection_actuelle in items:
                    items[self.id_selection_actuelle].setPen(QPen(Qt.PenStyle.NoPen))

            self.id_selection_actuelle = None
            self.group_selection.setVisible(False)

        except Exception as e:
            logger.error(f"Erreur désélection: {e}")

    def afficher_notification_sauvegarde(self, succes: bool, message: str) -> None:
        """Affiche une notification de sauvegarde dans la barre de statut."""
        couleur = (
            ConstantesInterface.COULEUR_STATUT_SUCCES
            if succes
            else ConstantesInterface.COULEUR_STATUT_ERREUR
        )
        self.barre_statut.setStyleSheet(f"color: {couleur};")
        self.barre_statut.showMessage(message, 5000)

    # ========================================================================
    # MÉTHODES PRIVÉES
    # ========================================================================

    def _mettre_a_jour_dashboard(self, donnees: Dict[str, Any]) -> None:
        """Met à jour le tableau de bord avec les nouvelles données."""
        try:
            # Statistiques principales
            html_stats = self.gestionnaire_affichage.generer_html_statistiques(donnees)
            self.text_stats.setHtml(html_stats)

            # Journal des paliers
            paliers = donnees.get("paliers", [])
            texte_journal = "\n".join(paliers[-20:])  # Derniers 20 paliers
            self.text_journal.setPlainText(texte_journal)

        except Exception as e:
            logger.error(f"Erreur mise à jour dashboard: {e}")

    def _rechercher_entite_par_id(self, entite_id: str) -> Optional[Dict[str, Any]]:
        """Recherche une entité par ID dans toutes les catégories."""
        for entites_categorie in self.donnees_actuelles.get("entites", {}).values():
            for entite_data in entites_categorie:
                if entite_data.get("id") == entite_id:
                    return entite_data
        return None

    def _afficher_details_entite(
        self, entite_data: Dict[str, Any], entite_id: str
    ) -> None:
        """Affiche les détails d'une entité sélectionnée."""
        html_details = self.gestionnaire_affichage.generer_html_entite(entite_data)
        self.text_selection.setHtml(html_details)
        self.group_selection.setVisible(True)

    def _mettre_en_evidence_entite(self, entite_id: str) -> None:
        """Met en évidence graphiquement l'entité sélectionnée."""
        if not self.gestionnaire_scene:
            return

        items = self.gestionnaire_scene.items_graphiques
        if entite_id in items:
            pen_selection = QPen(ConstantesInterface.COULEUR_SELECTION, 2)
            items[entite_id].setPen(pen_selection)

    def _retirer_selection_precedente(self) -> None:
        """Retire la sélection visuelle précédente."""
        if not self.id_selection_actuelle or not self.gestionnaire_scene:
            return

        items = self.gestionnaire_scene.items_graphiques
        if self.id_selection_actuelle in items:
            items[self.id_selection_actuelle].setPen(QPen(Qt.PenStyle.NoPen))

    def _mettre_a_jour_performance(self) -> None:
        """Met à jour les métriques de performance d'affichage."""
        try:
            if not self.gestionnaire_scene:
                return

            nb_items = len(self.gestionnaire_scene.items_graphiques)
            if nb_items > ConstantesInterface.MAX_ENTITES_DEBUG:
                self.barre_progression.setVisible(True)
                self.barre_progression.setValue(
                    min(
                        100, int(nb_items / ConstantesInterface.MAX_ENTITES_DEBUG * 100)
                    )
                )
            else:
                self.barre_progression.setVisible(False)

        except Exception as e:
            logger.debug(f"Erreur mise à jour performance: {e}")

    # ========================================================================
    # GESTIONNAIRES D'ÉVÉNEMENTS
    # ========================================================================

    def _on_pause(self) -> None:
        """Gestionnaire du bouton pause."""
        self.pause_demandee.emit()
        self.bouton_pause.setEnabled(False)
        self.bouton_reprise.setEnabled(True)
        logger.info("Interface: Pause demandée")

    def _on_reprise(self) -> None:
        """Gestionnaire du bouton reprise."""
        self.reprise_demandee.emit()
        self.bouton_pause.setEnabled(True)
        self.bouton_reprise.setEnabled(False)
        logger.info("Interface: Reprise demandée")

    def _on_vitesse_combo_changee(self, index: int) -> None:
        """Gestionnaire du changement de vitesse via combo."""
        try:
            texte = self.combo_vitesse.itemText(index)
            personnalise = texte == "Personnalisé"

            self.input_vitesse.setVisible(personnalise)
            if personnalise:
                self.input_vitesse.setFocus()

            valeur = (
                self.input_vitesse.text() if personnalise else texte.replace("x", "")
            )

            self.vitesse_changee.emit(valeur)
            logger.info(f"Interface: Vitesse changée à {valeur}")

        except Exception as e:
            logger.error(f"Erreur changement vitesse: {e}")

    def _on_vitesse_input_changee(self) -> None:
        """Gestionnaire du changement de vitesse via input."""
        try:
            valeur = self.input_vitesse.text()
            # Validation basique
            int(valeur)  # Vérification que c'est un nombre
            self.vitesse_changee.emit(valeur)
            logger.info(f"Interface: Vitesse personnalisée à {valeur}")
        except ValueError:
            logger.warning(f"Valeur de vitesse invalide: {self.input_vitesse.text()}")

    def showEvent(self, event: Any) -> None:
        """Événement d'affichage de la fenêtre."""
        super().showEvent(event)
        # Connecter les signaux après que tous les widgets soient créés
        if hasattr(self, "bouton_pause"):
            self._connecter_signaux_controle()

    def closeEvent(self, event: Any) -> None:
        """Gère la fermeture de la fenêtre proprement."""
        try:
            logger.info("Fermeture de l'interface principale")
            self.timer_stats.stop()
            super().closeEvent(event)
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture: {e}")


# ========================================================================
# POINT D'ENTRÉE DE COMPATIBILITÉ
# ========================================================================


# Alias pour compatibilité avec l'ancienne API
def miseajour(self, etat_json: str) -> None:
    """Méthode de compatibilité (deprecated)."""
    logger.warning("Utilisation de l'ancienne API miseajour(), utilisez mise_a_jour()")
    self.mise_a_jour(etat_json)


# Injection de la méthode pour compatibilité
FenetrePrincipale.miseajour = miseajour
