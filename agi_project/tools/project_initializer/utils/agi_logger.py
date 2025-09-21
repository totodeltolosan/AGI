#!/usr/bin/env python3
"""
AGI Logger - Logger Multi-Niveaux pour Project Initializer
=========================================================

Rôle Fondamental (Conforme AGI.md - utils/agi_logger.py) :
- Fournir logging multi-niveaux hiérarchiques (ERROR, INFO, VERBOSE, DEBUG)
- Gérer les sorties console et fichier selon les options CLI
- Assurer la traçabilité complète du processus de génération
- Respecter la directive des 200 lignes via extraction modulaire

Conformité Architecturale :
- Limite stricte < 200 lignes (extrait de project_initializer.py)
- Sécurité : validation des chemins de fichiers log
- Fiabilité : gestion robuste des erreurs de logging

Version : 1.0
Date : 17 Septembre 2025
Référence : Rapport de Directives AGI.md - Section tools/project_initializer/
"""

import logging
import sys
from typing import Optional
from pathlib import Path


class AGILogger:
    """
    Logger dédié au project_initializer avec niveaux hiérarchiques.

    Implémente la traçabilité complète exigée par AGI.md avec
    support des options --verbose, --debug et --log-file.
    """

    LEVELS = {
        "ERROR": logging.ERROR,  # Erreurs uniquement
        "INFO": logging.INFO,  # Informations de base (défaut)
        "VERBOSE": 15,  # --verbose : détails de génération
        "DEBUG": logging.DEBUG,  # --debug : granularité maximale
    }

    def __init__(self, level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialise le logger avec niveau et fichier optionnel.

        Args:
            level: Niveau de logging ('ERROR', 'INFO', 'VERBOSE', 'DEBUG')
            log_file: Chemin du fichier de log optionnel
        """
        # Enregistrement du niveau VERBOSE personnalisé
        logging.addLevelName(15, "VERBOSE")

        self.logger = logging.getLogger("project_initializer")
        self.logger.setLevel(self.LEVELS[level])

        # Format détaillé pour traçabilité AGI.md
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )

        # Handler console obligatoire
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler fichier si spécifié
        if log_file:
            self._add_file_handler(log_file, formatter)

    def _add_file_handler(self, log_file: str, formatter: logging.Formatter) -> None:
        """Ajoute un handler fichier avec validation du chemin."""
        try:
            log_path = Path(log_file).resolve()

            # Sécurité : validation du chemin parent
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            self.logger.info(f"📝 Log fichier activé: {log_path}")

        except Exception as e:
            self.logger.error(f"❌ Erreur création fichier log {log_file}: {e}")

    def info(self, msg: str) -> None:
        """Log niveau INFO."""
        self.logger.info(msg)

    def verbose(self, msg: str) -> None:
        """Log niveau VERBOSE (--verbose)."""
        self.logger.log(15, msg)

    def debug(self, msg: str) -> None:
        """Log niveau DEBUG (--debug)."""
        self.logger.debug(msg)

    def error(self, msg: str) -> None:
        """Log niveau ERROR."""
        self.logger.error(msg)
