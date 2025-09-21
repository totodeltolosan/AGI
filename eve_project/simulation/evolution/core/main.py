# main.py
"""
Point d'entrée principal de l'application EVE.
"""
import sys
from PyQt6.QtWidgets import QApplication
from eve_src.simulation import AdvancedSimulation as Simulation

from eve_src.interface import MainApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    eve_simulation = Simulation()
    window = MainApp(eve_simulation)
    window.showMaximized()
    sys.exit(app.exec())
