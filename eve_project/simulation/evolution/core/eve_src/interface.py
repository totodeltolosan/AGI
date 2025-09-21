# eve_src/interface.py
"""
Gère toute l'interface graphique en Qt6.
Intègre le Centre de Contrôle Interactif avec ses outils, le graphique
de population en temps réel et l'inspecteur d'entité.
"""
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QButtonGroup,
)
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import QTimer, QRectF, Qt
import pyqtgraph as pg

from eve_src.archetypes.archetype_animal import Animal
from eve_src.archetypes.archetype_vegetal import Vegetal
from eve_src.archetypes.archetype_insecte import Insecte


class SimulationCanvas(QWidget):
    """Widget qui dessine la simulation et gère les interactions souris."""

    def __init__(self, main_window, simulation):
        """TODO: Add docstring."""
        super().__init__()
        self.main_window = main_window
        self.simulation = simulation
        self.selected_unit = None
        self.setMinimumSize(800, 800)
        self.setMouseTracking(True)

    def select_unit(self, unit):
        """Met en surbrillance une unité sélectionnée."""
        self.selected_unit = unit
        self.update()

    def handle_mouse_interaction(self, event):
        """Logique centrale pour l'interaction de la souris avec les outils."""
        if self.simulation.monde.taille > 0:
            cell_size = self.width() / self.simulation.monde.taille
            grid_x = int(event.position().x() / cell_size)
            grid_y = int(event.position().y() / cell_size)

            tool = self.main_window.current_tool
            # Le clic droit est toujours assigné à l'outil "tuer"
            if event.buttons() & Qt.MouseButton.RightButton:
                tool = "tuer"

            if tool == "inspecter":
                if (
                    event.type() == event.Type.MouseButtonPress
                ):  # L'inspection ne se fait qu'au clic simple
                    unit = self.simulation.get_unit_at(grid_x, grid_y)
                    self.main_window.display_unit_info(unit)
            elif tool == "ajouter_vegetal":
                self.simulation.ajouter_entite("vegetal", grid_x, grid_y)
            elif tool == "ajouter_insecte":
                self.simulation.ajouter_entite("insecte", grid_x, grid_y)
            elif tool == "ajouter_animal":
                self.simulation.ajouter_entite("animal", grid_x, grid_y)
            elif tool == "ajouter_obstacle":
                self.simulation.modifier_obstacle(grid_x, grid_y, action="ajouter")
            elif tool == "tuer":
                self.simulation.tuer_entites(grid_x, grid_y, rayon=0)

    # pylint: disable=invalid-name
    def mousePressEvent(self, event):
        """Gère un clic simple."""
        self.handle_mouse_interaction(event)

    # pylint: disable=invalid-name
    def mouseMoveEvent(self, event):
        """Gère le mouvement de la souris avec un bouton pressé pour "peindre"."""
        self.handle_mouse_interaction(event)

    # pylint: disable=invalid-name
    def paintEvent(self, _event):
        """Dessine tous les éléments de la simulation."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("black"))
        taille_monde = self.simulation.monde.taille
        if taille_monde == 0:
            return
        cell_size = self.width() / taille_monde

        # Dessin du terrain
        for y in range(taille_monde):
            for x in range(taille_monde):
                if self.simulation.monde.terrain[y][x] > 1.0:
                    painter.fillRect(
                        int(x * cell_size),
                        int(y * cell_size),
                        int(cell_size) + 2,
                        int(cell_size) + 2,
                        QColor(30, 40, 50),
                    )

        # Dessins des obstacles, cadavres, etc.
        painter.setBrush(QColor("dimgray"))
        for x, y in self.simulation.monde.obstacles:
            painter.drawRect(
                int(x * cell_size),
                int(y * cell_size),
                int(cell_size) + 1,
                int(cell_size) + 1,
            )
        painter.setBrush(QColor("darkkhaki"))
        for x, y in self.simulation.monde.cadavres:
            painter.drawRect(
                int(x * cell_size),
                int(y * cell_size),
                int(cell_size) + 1,
                int(cell_size) + 1,
            )

        # Dessin de la population
        for unite in self.simulation.population:
            painter.setBrush(unite.couleur)
            rect = QRectF(
                unite.x * cell_size, unite.y * cell_size, cell_size, cell_size
            )
            if isinstance(unite, Animal):
                # Utilise le phénotype pour la taille
                taille_unite = cell_size * unite.phenotype.get("physique", {}).get(
                    "taille", 1.0
                )
                animal_rect = QRectF(
                    unite.x * cell_size, unite.y * cell_size, taille_unite, taille_unite
                )
                painter.drawEllipse(animal_rect)
                if unite.phenotype.get("alimentation", {}).get("type") == "carnivore":
                    painter.setBrush(QColor("white"))
                    painter.drawEllipse(
                        animal_rect.center(), taille_unite * 0.2, taille_unite * 0.2
                    )
            elif isinstance(unite, Insecte):
                painter.drawRect(int(rect.x()), int(rect.y()), 3, 3)
            elif isinstance(unite, Vegetal):
                painter.fillRect(int(rect.x()), int(rect.y()), 2, 2, unite.couleur)

        # Dessin du cercle de sélection
        if self.selected_unit:
            pen = QPen(QColor("yellow"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            select_rect = QRectF(
                self.selected_unit.x * cell_size - cell_size * 0.5,
                self.selected_unit.y * cell_size - cell_size * 0.5,
                cell_size * 2,
                cell_size * 2,
            )
            painter.drawEllipse(select_rect)


class MainApp(QMainWindow):
    """Fenêtre principale qui orchestre l'application et la simulation."""

    """TODO: Add docstring."""
    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.setWindowTitle("EVE v8.2 - Centre de Contrôle Interactif")
        (
            self.time_data,
            self.animal_pop_data,
            self.insect_pop_data,
            self.vegetal_pop_data,
        ) = ([], [], [], [])
        self.current_tool = "inspecter"
        self.setup_ui()
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_gui)
        self.timer.start()

    def setup_ui(self):
        """Construit l'interface utilisateur évoluée."""
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        dashboard_container = QWidget()
        dashboard_layout = QVBoxLayout()
        font_title = QFont()
        font_title.setPointSize(12)
        font_title.setBold(True)
        font_normal = QFont()
        font_normal.setPointSize(11)
            """TODO: Add docstring."""

        def create_label(text, is_title=False):
            label = QLabel(text)
            label.setFont(font_title if is_title else font_normal)
            if is_title:
                label.setStyleSheet(
                    "margin-top: 10px; margin-bottom: 2px; border-bottom: 1px solid gray;"
                )
            return label

        # --- Section Contrôle ---
        dashboard_layout.addWidget(create_label("CONTRÔLE", is_title=True))
        self.play_pause_button = QPushButton("Pause")
        self.play_pause_button.clicked.connect(self.toggle_pause)
        dashboard_layout.addWidget(self.play_pause_button)
        speed_layout = QHBoxLayout()
        self.speed_buttons = {
            "x0.5": QPushButton("x0.5"),
            "x1": QPushButton("x1"),
            "x2": QPushButton("x2"),
            "x5": QPushButton("x5"),
        }
        for btn in self.speed_buttons.values():
            speed_layout.addWidget(btn)
        self.speed_buttons["x0.5"].clicked.connect(lambda: self.change_speed(100))
        self.speed_buttons["x1"].clicked.connect(lambda: self.change_speed(50))
        self.speed_buttons["x2"].clicked.connect(lambda: self.change_speed(25))
        self.speed_buttons["x5"].clicked.connect(lambda: self.change_speed(10))
        dashboard_layout.addLayout(speed_layout)

        # --- Section Boîte à Outils ---
        dashboard_layout.addWidget(create_label("BOÎTE À OUTILS", is_title=True))
        self.tool_buttons = QButtonGroup(self)
        self.tool_buttons.setExclusive(True)
        tools = {
            "Inspecter (Clic G)": "inspecter",
            "Ajouter Végétal": "ajouter_vegetal",
            "Ajouter Insecte": "ajouter_insecte",
            "Ajouter Animal": "ajouter_animal",
            "Ajouter Obstacle": "ajouter_obstacle",
            "Tuer (Clic D)": "tuer",
        }
        for i, (text, tool_name) in enumerate(tools.items()):
            btn = QPushButton(text)
            btn.setCheckable(True)
            if tool_name == "inspecter":
                btn.setChecked(True)
            self.tool_buttons.addButton(btn)
            btn.clicked.connect(lambda _, t=tool_name: self.select_tool(t))
            dashboard_layout.addWidget(btn)

        # --- Section Stats & Inspecteur ---
        dashboard_layout.addWidget(create_label("STATS MONDE", is_title=True))
        self.labels = {
            "age": create_label("Âge: 0"),
            "saison": create_label("Saison: Été"),
            "event": create_label("Événement: RAS"),
            "pop_total": create_label("Pop. Totale: 0"),
            "pop_vegetal": create_label("Végétaux: 0"),
            "pop_insecte": create_label("Insectes: 0"),
            "pop_animal": create_label("Animaux: 0"),
        }
        for label in self.labels.values():
            dashboard_layout.addWidget(label)
        self.labels["event"].setStyleSheet("color: yellow;")
        dashboard_layout.addWidget(create_label("INSPECTEUR", is_title=True))
        self.inspect_labels = {
            "type": create_label("Archétype: N/A"),
            "tribu": create_label("Tribu ID: N/A"),
            "energie": create_label("Énergie: N/A"),
            "age": create_label("Âge: N/A"),
            "etat": create_label("État: N/A"),
        }
        for label in self.inspect_labels.values():
            dashboard_layout.addWidget(label)
        dashboard_layout.addStretch()
        dashboard_container.setLayout(dashboard_layout)

        # --- Panneau principal (droite) ---
        main_panel_layout = QVBoxLayout()
        self.canvas = SimulationCanvas(self, self.simulation)
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("k")
        self.graph_widget.addLegend()
        self.animal_curve = self.graph_widget.plot(pen="c", name="Animaux")
        self.insect_curve = self.graph_widget.plot(pen="y", name="Insectes")
        self.vegetal_curve = self.graph_widget.plot(pen="g", name="Végétaux")
        splitter_main = QSplitter(Qt.Orientation.Vertical)
        splitter_main.addWidget(self.canvas)
        splitter_main.addWidget(self.graph_widget)
        splitter_main.setSizes([700, 200])
        main_panel_layout.addWidget(splitter_main)

        main_panel_layout_container = QWidget()
        main_panel_layout_container.setLayout(main_panel_layout)
        splitter.addWidget(dashboard_container)
        splitter.addWidget(main_panel_layout_container)
        splitter.setSizes([280, 800])
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def select_tool(self, tool_name):
        """Change l'outil actif de l'utilisateur."""
        self.current_tool = tool_name

    def toggle_pause(self):
        """Met en pause ou reprend la simulation."""
        self.simulation.is_paused = not self.simulation.is_paused
        self.play_pause_button.setText("Play" if self.simulation.is_paused else "Pause")

    def change_speed(self, interval):
        """Change la vitesse de la simulation."""
        self.timer.setInterval(interval)

    def display_unit_info(self, unit):
        """Affiche les informations de l'unité sélectionnée dans l'inspecteur."""
        self.canvas.select_unit(unit)
        if unit and isinstance(unit, Animal):
            phenotype = unit.phenotype
            self.inspect_labels["type"].setText(
                f"Archétype: Animal ({phenotype.get('alimentation', {}).get('type', 'N/A')})"
            )
            self.inspect_labels["tribu"].setText(
                f"Tribu ID: {phenotype.get('social', {}).get('id_tribu', [0])[0]:.2f}"
            )
            self.inspect_labels["energie"].setText(f"Énergie: {unit.energie:.1f}")
            self.inspect_labels["age"].setText(f"Âge: {unit.age}")
            self.inspect_labels["etat"].setText(f"État: {unit.etat}")
        else:
            for key in self.inspect_labels:
                self.inspect_labels[key].setText(
                    self.inspect_labels[key].text().split(":")[0] + ": N/A"
                )

    def update_gui(self):
        """Met à jour l'intégralité de l'interface."""
        self.simulation.update()
        stats = self.simulation.get_stats()

        if stats["pop_total"] == 0 and self.simulation.age_simulation > 1:
            self.labels["pop_total"].setText("EXTINCTION GLOBALE")
            self.timer.stop()
        else:
            self.labels["age"].setText(f"Âge: {stats['age']}")
            self.labels["saison"].setText(f"Saison: {stats['saison']}")
            self.labels["event"].setText(f"Événement: {stats['dernier_event']}")
            self.labels["pop_total"].setText(f"Pop. Totale: {stats['pop_total']}")
            self.labels["pop_vegetal"].setText(f"Végétaux: {stats['pop_vegetal']}")
            self.labels["pop_insecte"].setText(f"Insectes: {stats['pop_insecte']}")
            self.labels["pop_animal"].setText(f"Animaux: {stats['pop_animal']}")

            if stats["age"] % 10 == 0:
                self.time_data.append(stats["age"])
                self.animal_pop_data.append(stats["pop_animal"])
                self.insect_pop_data.append(stats["pop_insecte"])
                self.vegetal_pop_data.append(stats["pop_vegetal"])
                self.animal_curve.setData(self.time_data, self.animal_pop_data)
                self.insect_curve.setData(self.time_data, self.insect_pop_data)
                self.vegetal_curve.setData(self.time_data, self.vegetal_pop_data)

        if self.canvas.selected_unit and self.canvas.selected_unit.est_mort:
            self.display_unit_info(None)

        self.canvas.update()