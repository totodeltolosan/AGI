"""
Constantes lanceur projet Le Simulateur (Directive 60).
Configuration centralisée valeurs système.
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
CONFIG_PATH = BASE_DIR / "config" / "config.json"
LOGS_DIR = BASE_DIR / "logs"
TIMEOUT_INIT = 30
TIMEOUT_QUEUES = 2.0
GUI_UPDATE_INTERVAL = 100
MAX_RESTART_ATTEMPTS = 3
PROCESS_CHECK_INTERVAL = 1.0
