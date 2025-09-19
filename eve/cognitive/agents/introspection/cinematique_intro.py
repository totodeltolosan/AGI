# -*- coding: utf-8 -*-
"""
cinematique_intro.py (v1.2.1)

Ajout d'un signal personnalisé 'finished' pour notifier la fin de l'animation.
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Property, QRectF, QPointF, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QPen

class CinematicSplashScreen(QWidget):
    # On déclare un signal personnalisé pour cette classe
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._phase = 0.0

    def get_phase(self): return self._phase
    def set_phase(self, value): self._phase = value; self.update()
    phase = Property(float, get_phase, set_phase)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(18, 18, 18, 240))
        if self._phase >= 1.0:
            opacity = min(1.0, (self._phase - 1.0) * 2)
            font_alma = QFont("Segoe UI", 80, QFont.Weight.Bold)
            painter.setFont(font_alma)
            color_alma = QColor(60, 130, 220, int(255 * opacity))
            painter.setPen(color_alma)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "ALMA")
        if self._phase >= 2.0:
            opacity_icons = min(1.0, (self._phase - 2.0))
            self.draw_capability_icons(painter, opacity_icons)
        if self._phase >= 3.5:
            opacity_final = max(0.0, 1.0 - (self._phase - 3.5) * 2)
            painter.setOpacity(opacity_final)

    def draw_capability_icons(self, painter, opacity):
        center = self.rect().center()
        radius = 120
        icons = ["🧠", "🔊", "📈", "📄", "🌳"]
        painter.setOpacity(opacity)
        font_icon = QFont("Segoe UI Symbol", 24)
        painter.setFont(font_icon)
        for i, icon in enumerate(icons):
            angle = (i / len(icons)) * 2 * math.pi - (math.pi / 2)
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)
            pen = QPen(QColor(200, 200, 200, int(100 * opacity)), 1)
            painter.setPen(pen)
            painter.drawLine(center, QPointF(x, y))
            pen_icon = QPen(QColor(200, 200, 200, int(255 * opacity)))
            painter.setPen(pen_icon)
            painter.drawText(QRectF(x - 20, y - 20, 40, 40), Qt.AlignmentFlag.AlignCenter, icon)

    def start(self):
        """Démarre la séquence d'animation interne."""
        self.anim_phase = QPropertyAnimation(self, b"phase")
        self.anim_phase.setDuration(10000)
        self.anim_phase.setStartValue(0.0)
        self.anim_phase.setEndValue(4.0)
        self.anim_phase.setEasingCurve(QEasingCurve.Type.Linear)

        # On émet notre propre signal quand l'animation interne est finie
        self.anim_phase.finished.connect(self.finished.emit)
        # On se ferme aussi
        self.anim_phase.finished.connect(self.close)

        self.anim_phase.start()
