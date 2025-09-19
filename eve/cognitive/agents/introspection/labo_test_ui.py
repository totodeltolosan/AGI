# -*- coding: utf-8 -*-
"""
labo_test_ui.py (v2.6.4)

Correction finale de tous les imports manquants pour une stabilité totale.
"""

import sys
import os
import webbrowser
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QSplitter, QTreeView,
    QFileSystemModel, QGraphicsOpacityEffect
)
# --- DÉBUT DE LA CORRECTION ---
from PySide6.QtCore import Qt, QDir, QTimer, QPropertyAnimation
from PySide6.QtGui import QPalette, QColor
# --- FIN DE LA CORRECTION ---
from PySide6.QtMultimedia import QSoundEffect
from pathlib import Path

from . import analyseur_code
from . import cinematique_intro
from . import generateur_html

class LaboratoireIntrospection(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alma - Laboratoire d'Introspection du Code")
        self.setGeometry(100, 100, 1200, 800)
        self.chemin_projet = str(Path(__file__).parent.parent)
        self.fichiers_du_projet = []
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setup_ui()
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.central_widget.setGraphicsEffect(self.opacity_effect)
        self.central_widget.hide()
        self.setup_sound()
        self.anim_main_ui_fade_in = None

    def setup_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        titre_label = QLabel("Panneau de Contrôle de l'Analyseur")
        titre_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        titre_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout = QHBoxLayout()
        self.bouton_analyser = QPushButton("Rafraîchir l'Arborescence")
        self.bouton_analyser.setStyleSheet("font-size: 12pt; padding: 10px;")
        self.bouton_generer_html = QPushButton("Générer le Rapport HTML Complet")
        self.bouton_generer_html.setStyleSheet("font-size: 12pt; padding: 10px; background-color: #27ae60; color: white;")
        button_layout.addWidget(self.bouton_analyser)
        button_layout.addWidget(self.bouton_generer_html)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.vue_projet = QTreeView()
        self.modele_systeme_fichiers = QFileSystemModel()
        self.vue_projet.setModel(self.modele_systeme_fichiers)
        self.vue_projet.header().hide()
        for i in range(1, self.modele_systeme_fichiers.columnCount()):
            self.vue_projet.hideColumn(i)
        splitter.addWidget(self.vue_projet)
        self.details_viewer = QTextEdit()
        self.details_viewer.setReadOnly(True)
        self.details_viewer.setPlaceholderText("Sélectionnez un fichier Python dans l'arbre pour lancer son analyse...")
        splitter.addWidget(self.details_viewer)
        splitter.setSizes([300, 900])
        main_layout.addWidget(titre_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(splitter)
        self.bouton_analyser.clicked.connect(self.lancer_analyse_complete)
        self.bouton_generer_html.clicked.connect(self.generer_rapport)
        self.vue_projet.selectionModel().selectionChanged.connect(self.afficher_details_fichier)

    def setup_sound(self):
        self.start_sound = QSoundEffect()
        sound_path = Path(__file__).parent.parent / "assets" / "start_sound.wav"
        if sound_path.exists():
            self.start_sound.setSource(sound_path.as_uri())
            self.start_sound.setVolume(0.5)
        else:
            print("[Alerte] Fichier 'assets/start_sound.wav' non trouvé.")

    def start_cinematic(self):
        self.splash = cinematique_intro.CinematicSplashScreen()
        self.splash.resize(500, 500)
        self.splash.move(self.geometry().center() - self.splash.rect().center())
        self.splash.finished.connect(self.on_splash_finished)
        self.splash.show()
        self.start_sound.play()
        self.splash.start()

    def on_splash_finished(self):
        self.central_widget.show()
        self.anim_main_ui_fade_in = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.anim_main_ui_fade_in.setDuration(800)
        self.anim_main_ui_fade_in.setStartValue(0.0)
        self.anim_main_ui_fade_in.setEndValue(1.0)
        self.anim_main_ui_fade_in.start()
        self.lancer_analyse_complete()

    def lancer_analyse_complete(self):
        self.details_viewer.setText("Scan du projet en cours...")
        QApplication.processEvents()
        try:
            self.fichiers_du_projet = analyseur_code.scanner_projet(self.chemin_projet)
            self.modele_systeme_fichiers.setRootPath(self.chemin_projet)
            self.vue_projet.setRootIndex(self.modele_systeme_fichiers.index(self.chemin_projet))
            self.details_viewer.setText(f"{len(self.fichiers_du_projet)} fichiers trouvés. Prêt pour l'analyse.")
        except Exception as e:
            self.details_viewer.setText(f"\n[ERREUR] : {e}")

    def afficher_details_fichier(self, selection):
        indexes = selection.indexes()
        if not indexes: return
        chemin_fichier = self.modele_systeme_fichiers.filePath(indexes[0])
        if not os.path.isfile(chemin_fichier) or not chemin_fichier.endswith('.py'):
            self.details_viewer.setText(f"Sélectionné : {chemin_fichier}\n\n(Ceci n'est pas un fichier Python analysable.)")
            return
        self.details_viewer.setText(f"<h3>Analyse IA en cours pour : {Path(chemin_fichier).name}</h3><p>Veuillez patienter...</p>")
        QApplication.processEvents()
        resultats_analyse = analyseur_code.analyser_fichier(chemin_fichier, self.fichiers_du_projet)
        if resultats_analyse.get("erreur"):
            html = f"<h3>Analyse de : {Path(chemin_fichier).name}</h3><hr><font color='red'><b>Erreur :</b> {resultats_analyse['erreur']}</font>"
            self.details_viewer.setHtml(html)
            return
        html = f"""
        <body style='font-family: Segoe UI, sans-serif; color: #e0e0e0;'>
        <h3>Analyse de : <code>{Path(chemin_fichier).name}</code></h3>
        <b>Chemin :</b> {resultats_analyse['chemin']}<br>
        <b>Taille :</b> {resultats_analyse['taille_lignes']} lignes<br>
        <hr>
        <h4 style='color: #3498db;'>🧠 Résumé par l'Intelligence Artificielle :</h4>
        <p style='background-color:#1c2833; color: #d5dbdb; padding: 10px; border-radius: 5px; border-left: 3px solid #3498db;'>{resultats_analyse['resume_ia']}</p>
        <hr>
        <b>Rôle (d'après le docstring) :</b>
        <p style='background-color:#2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px; font-style: italic;'>{resultats_analyse['role_docstring'].replace(os.linesep, '<br>')}</p>
        <hr>
        <b>Classes Définies :</b>
        <p>{', '.join(f"<code>{c}</code>" for c in resultats_analyse['classes_definies']) if resultats_analyse['classes_definies'] else 'Aucune'}</p>
        <hr>
        <b>Fonctions Définies :</b>
        <p>{', '.join(f"<code>{f}()</code>" for f in resultats_analyse['fonctions_definies']) if resultats_analyse['fonctions_definies'] else 'Aucune'}</p>
        <hr>
        <b>Dépendances Externes :</b>
        <p>{', '.join(f"<code>{i}</code>" for i in resultats_analyse['dependances_externes']) if resultats_analyse['dependances_externes'] else 'Aucune'}</p>
        </body>
        """
        self.details_viewer.setHtml(html)

    def generer_rapport(self):
        self.details_viewer.setText("Lancement de l'analyse complète du projet...\nCela peut prendre une minute.")
        QApplication.processEvents()
        graphe = analyseur_code.analyser_tout_le_projet(self.chemin_projet)
        self.details_viewer.append("\nAnalyse terminée. Génération du rapport HTML...")
        QApplication.processEvents()
        chemin_rapport = generateur_html.generer_rapport_complet(graphe)
        if chemin_rapport:
            self.details_viewer.append(f"\nRapport généré avec succès !\nChemin : {chemin_rapport}")
            try:
                webbrowser.open(f'file://{os.path.realpath(chemin_rapport)}')
                self.details_viewer.append("\nTentative d'ouverture du rapport dans votre navigateur par défaut.")
            except Exception as e:
                self.details_viewer.append(f"\nImpossible d'ouvrir le navigateur : {e}")
        else:
            self.details_viewer.append("\nLa génération du rapport a échoué.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)

    fenetre = LaboratoireIntrospection()
    fenetre.show()
    QTimer.singleShot(100, fenetre.start_cinematic)
    sys.exit(app.exec())
