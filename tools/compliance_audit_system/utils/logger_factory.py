#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_audit_system/utils/logger_factory.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""
Fabrique de Loggers - Système d'Audit AGI
Responsabilité unique : Création et configuration des loggers pour traçabilité
Respecte strictement la directive des 200 lignes
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime


class AGILogger:
    """Logger spécialisé pour le système d'audit AGI"""

    def __init__(
        """TODO: Add docstring."""
        self,
        name: str,
        level: int = logging.INFO,
        log_file: Optional[Path] = None,
        verbose: bool = False,
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Éviter la duplication des handlers
        if not self.logger.handlers:
            self._setup_handlers(log_file, verbose)

    def _setup_handlers(self, log_file: Optional[Path], verbose: bool):
        """Configure les handlers de logging"""

        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_level = logging.DEBUG if verbose else logging.INFO
        console_handler.setLevel(console_level)

        # Format console (coloré si possible)
        if self._supports_color():
            console_formatter = ColoredFormatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        else:
            console_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%H:%M:%S",
            )

        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Handler fichier (si spécifié)
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)  # Toujours debug dans le fichier

            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)8s | %(name)20s | %(funcName)15s:%(lineno)4d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def _supports_color(self) -> bool:
        """Vérifie si le terminal supporte les couleurs"""
        return (
            hasattr(sys.stdout, "isatty")
            and sys.stdout.isatty()
            and ("TERM" in os.environ or sys.platform == "win32")
        )

    def info(self, message: str, **kwargs):
        """Log niveau info avec contexte AGI"""
        self.logger.info(f"🔍 {message}", **kwargs)

    def success(self, message: str, **kwargs):
        """Log pour succès (niveau info avec émoji)"""
        self.logger.info(f"✅ {message}", **kwargs)

    def warning(self, message: str, **kwargs):
        """Log niveau warning avec contexte AGI"""
        self.logger.warning(f"⚠️ {message}", **kwargs)

    def error(self, message: str, **kwargs):
        """Log niveau error avec contexte AGI"""
        self.logger.error(f"❌ {message}", **kwargs)

    def debug(self, message: str, **kwargs):
        """Log niveau debug avec contexte AGI"""
        self.logger.debug(f"🔧 {message}", **kwargs)

    def audit_event(self, event_type: str, details: str, **kwargs):
        """Log spécialisé pour les événements d'audit"""
        self.logger.info(f"🏛️ [{event_type}] {details}", **kwargs)


class ColoredFormatter(logging.Formatter):
    """Formateur de logs coloré pour terminal"""

    """TODO: Add docstring."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[37m",  # Blanc
            "WARNING": "\033[33m",  # Jaune
            "ERROR": "\033[31m",  # Rouge
            "CRITICAL": "\033[35m",  # Magenta
            "RESET": "\033[0m",  # Reset
        }
            """TODO: Add docstring."""

    def format(self, record):
        # Coloration du niveau de log
        level_color = self.colors.get(record.levelname, self.colors["RESET"])
        record.levelname = f"{level_color}{record.levelname}{self.colors['RESET']}"

        # Coloration du nom du logger
        record.name = f"\033[34m{record.name}\033[0m"  # Bleu

        return super().format(record)


class LoggerFactory:
    """Fabrique centralisée de loggers AGI"""

    _instances: Dict[str, AGILogger] = {}
    _global_config = {
        "default_level": logging.INFO,
        "log_directory": None,
        "enable_file_logging": False,
        "verbose_mode": False,
    }

    @classmethod
    def configure_global(
        cls,
        level: int = logging.INFO,
        log_directory: Optional[Path] = None,
        enable_file_logging: bool = False,
        verbose_mode: bool = False,
    ):
        """Configure les paramètres globaux de logging"""
        cls._global_config.update(
            {
                "default_level": level,
                "log_directory": log_directory,
                "enable_file_logging": enable_file_logging,
                "verbose_mode": verbose_mode,
            }
        )

        # Création du répertoire de logs si nécessaire
        if log_directory and enable_file_logging:
            log_directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def create_logger(cls, name: str, verbose: Optional[bool] = None) -> AGILogger:
        """Crée ou récupère un logger AGI"""

        # Utilisation de la configuration globale si verbose non spécifié
        if verbose is None:
            verbose = cls._global_config["verbose_mode"]

        # Réutilisation d'instance existante
        cache_key = f"{name}_{verbose}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]

        # Détermination du fichier de log
        log_file = None
        if (
            cls._global_config["enable_file_logging"]
            and cls._global_config["log_directory"]
        ):
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = (
                cls._global_config["log_directory"]
                / f"agi_audit_{name}_{timestamp}.log"
            )

        # Création du logger
        logger = AGILogger(
            name=name,
            level=cls._global_config["default_level"],
            log_file=log_file,
            verbose=verbose,
        )

        # Cache de l'instance
        cls._instances[cache_key] = logger

        return logger

    @classmethod
    def get_audit_logger(cls, component_name: str, verbose: bool = False) -> AGILogger:
        """Raccourci pour créer un logger d'audit spécialisé"""
        return cls.create_logger(f"audit.{component_name}", verbose)

    @classmethod
    def get_validator_logger(
        cls, validator_name: str, verbose: bool = False
    ) -> AGILogger:
        """Raccourci pour créer un logger de validateur"""
        return cls.create_logger(f"validator.{validator_name}", verbose)

    @classmethod
    def get_analyzer_logger(
        cls, analyzer_name: str, verbose: bool = False
    ) -> AGILogger:
        """Raccourci pour créer un logger d'analyseur"""
        return cls.create_logger(f"analyzer.{analyzer_name}", verbose)

    @classmethod
    def clear_cache(cls):
        """Vide le cache des loggers (utile pour les tests)"""
        cls._instances.clear()


# Import nécessaire pour les couleurs
import os


# Fonctions utilitaires
def create_logger(name: str, verbose: bool = False) -> AGILogger:
    """Fonction utilitaire pour créer un logger"""
    return LoggerFactory.create_logger(name, verbose)


def setup_audit_logging(
    log_directory: Optional[Path] = None,
    verbose: bool = False,
    level: int = logging.INFO,
):
    """Configuration rapide du système de logging d'audit"""
    LoggerFactory.configure_global(
        level=level,
        log_directory=log_directory,
        enable_file_logging=log_directory is not None,
        verbose_mode=verbose,
    )


def get_component_logger(
    component_type: str, component_name: str, verbose: bool = False
) -> AGILogger:
    """Obtient un logger pour un composant spécifique"""

    logger_getters = {
        "audit": LoggerFactory.get_audit_logger,
        "validator": LoggerFactory.get_validator_logger,
        "analyzer": LoggerFactory.get_analyzer_logger,
    }

    if component_type in logger_getters:
        return logger_getters[component_type](component_name, verbose)
    else:
        return LoggerFactory.create_logger(
            f"{component_type}.{component_name}", verbose
        )


if __name__ == "__main__":
    # Test du système de logging
    import tempfile

    print("🧪 Test du système de logging AGI")
    print("=" * 40)

    # Configuration pour les tests
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir)
        setup_audit_logging(log_dir, verbose=True)

        # Test des différents types de loggers
        audit_logger = LoggerFactory.get_audit_logger("test_component", verbose=True)
        validator_logger = LoggerFactory.get_validator_logger("line_validator")
        analyzer_logger = LoggerFactory.get_analyzer_logger("ast_analyzer")

        # Test des différents niveaux
        audit_logger.info("Début de l'audit de test")
        audit_logger.success("Composant validé avec succès")
        audit_logger.warning("Violation détectée")
        audit_logger.error("Erreur lors de l'analyse")
        audit_logger.debug("Information de débogage")
        audit_logger.audit_event("VALIDATION", "Fichier test.py analysé")

        validator_logger.info("Validation des lignes en cours")
        analyzer_logger.info("Analyse AST terminée")

        print(f"Logs sauvegardés dans: {log_dir}")

        # Affichage des fichiers créés
        log_files = list(log_dir.glob("*.log"))
        print(f"Fichiers de log créés: {len(log_files)}")
        for log_file in log_files:
            print(f"  - {log_file.name}")