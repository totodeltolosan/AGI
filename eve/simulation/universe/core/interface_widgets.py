# Fichier : interface_widgets.py
# Version 8.4 ("Rendu Robuste")

"""
Contient les widgets personnalisés pour l'interface du Chronoscope,
y compris les items graphiques intelligents et les effets visuels.
"""

import random
from typing import Optional, Dict, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QRadialGradient, QCursor
from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QWidget,
)

# --- Effets Visuels ---


class EffetLueur(QGraphicsEllipseItem):
    """Un item graphique qui crée un effet de lueur (bloom) autour d'un autre item."""

    def __init__(self, parent: QGraphicsItem):
        super().__init__(parent)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setZValue(parent.zValue() - 1)

    def update_lueur(self, taille: float, couleur: QColor):
        """Met à jour la taille et la couleur du gradient de lueur."""
        gradient = QRadialGradient(0, 0, taille / 2)
        start_color = QColor(couleur)
        start_color.setAlpha(150)
        end_color = QColor(couleur)
        end_color.setAlpha(0)
        gradient.setColorAt(0.2, start_color)
        gradient.setColorAt(1.0, end_color)
        self.setBrush(gradient)
        self.setRect(-taille / 2, -taille / 2, taille, taille)


# --- Items Graphiques Intelligents ---


class EntiteGraphique(QGraphicsEllipseItem):
    """Un item graphique qui représente une entité, gère son apparence et les clics."""

    itemClique = pyqtSignal(str)

    def __init__(self, entite_id: str, data: Dict[str, Any]):
        super().__init__()
        self.entite_id = entite_id
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setAcceptHoverEvents(True)
        self.lueur: Optional[EffetLueur] = None
        self.categorie = data.get("categorie", "inconnu")

    def hoverEnterEvent(self, event):
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.itemClique.emit(self.entite_id)
        super().mousePressEvent(event)

    def update_visuals(self, data: Dict[str, Any], config: Dict[str, Any]):
        """Met à jour la position, la taille et l'apparence de l'item."""
        pos = data["position"]
        taille = config.get(
            "taille",
            random.uniform(config.get("taille_min", 1), config.get("taille_max", 2)),
        )

        self.setPos(pos[0], pos[1])
        self.setRect(-taille / 2, -taille / 2, taille, taille)

        pinceau = QBrush()
        if self.categorie == "etoiles":
            couleur_etoile = self._get_couleur_temperature(
                data.get("temperature", 5000)
            )
            pinceau.setColor(couleur_etoile)
            self._update_lueur(taille, couleur_etoile)
        elif self.categorie == "particules":
            gris = random.randint(150, 255)
            opacite = random.uniform(0.5, 1.0)
            couleur = QColor(gris, gris, gris)
            couleur.setAlphaF(opacite)
            pinceau.setColor(couleur)
        elif self.categorie == "atomes":
            pinceau.setColor(QColor("cyan"))
        else:
            # AMÉLIORATION : Cas par défaut pour rendre les entités de catégorie
            # inconnue visibles pour faciliter le débogage.
            pinceau.setColor(QColor("magenta"))

        self.setBrush(pinceau)

    def _get_couleur_temperature(self, temp: float) -> QColor:
        """Retourne une couleur basée sur la température d'une étoile (corps noir)."""
        if temp > 15000:
            return QColor("#a2c8ff")
        if temp > 9000:
            return QColor("#ffffff")
        if temp > 6500:
            return QColor("#fff4e8")
        if temp > 5000:
            return QColor("#ffe8c5")
        if temp > 3500:
            return QColor("#ffc575")
        return QColor("#ff9d45")

    def _update_lueur(self, taille_etoile: float, couleur: QColor):
        """Crée ou met à jour l'effet de lueur."""
        if self.lueur is None:
            self.lueur = EffetLueur(self)
        self.lueur.update_lueur(taille_etoile * 5, couleur)


# --- Vue Principale ---


class VueInteractive(QGraphicsView):
    """Une QGraphicsView personnalisée qui gère le zoom, le déplacement et les clics sur le fond."""

    sceneCliquee = pyqtSignal()

    def __init__(self, scene: QGraphicsScene, parent: Optional[QWidget] = None) -> None:
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setBackgroundBrush(QColor(5, 5, 15))

    def wheelEvent(self, event):
        zoom_facteur = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_facteur, zoom_facteur)
        else:
            self.scale(1.0 / zoom_facteur, 1.0 / zoom_facteur)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item is None or not isinstance(item, (EntiteGraphique, EffetLueur)):
            self.sceneCliquee.emit()
        super().mousePressEvent(event)
