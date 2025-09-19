#!/usr/bin/env python3
"""
Gestionnaire de Configuration - Système d'Audit AGI
Responsabilité unique : Gestion centralisée de la configuration d'audit
Respecte strictement la directive des 200 lignes
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AuditThresholds:
    """Seuils de conformité pour l'audit AGI"""

    max_lines_per_file: int = 200
    max_functions_per_file: int = 15
    max_classes_per_file: int = 3
    max_imports_per_file: int = 20
    max_cyclomatic_complexity: int = 10
    max_cognitive_complexity: int = 15
    max_nesting_depth: int = 4
    min_docstring_coverage: float = 70.0
    min_type_hint_coverage: float = 50.0
    security_score_threshold: float = 80.0


@dataclass
class ReportingConfig:
    """Configuration des rapports"""

    console_colors: bool = True
    verbose_mode: bool = False
    generate_json: bool = True
    generate_html: bool = False
    generate_csv: bool = True
    max_violations_displayed: int = 10
    include_compliance_matrix: bool = True


@dataclass
class AuditConfig:
    """Configuration complète d'audit"""

    thresholds: AuditThresholds
    reporting: ReportingConfig
    enabled_validators: list
    enabled_analyzers: list
    output_formats: list
    log_level: str = "INFO"


class ConfigManager:
    """Gestionnaire centralisé de configuration AGI"""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file
        self.config = self._load_default_config()

        if config_file and config_file.exists():
            self._load_from_file()

    def _load_default_config(self) -> AuditConfig:
        """Charge la configuration par défaut"""
        default_thresholds = AuditThresholds()
        default_reporting = ReportingConfig()

        return AuditConfig(
            thresholds=default_thresholds,
            reporting=default_reporting,
            enabled_validators=[
                "line_validator",
                "syntax_validator",
                "security_validator",
            ],
            enabled_analyzers=[
                "ast_analyzer",
                "pattern_analyzer",
                "dependency_analyzer",
            ],
            output_formats=["console", "json"],
            log_level="INFO",
        )

    def _load_from_file(self):
        """Charge la configuration depuis un fichier JSON"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            self._merge_config(config_data)

        except Exception as e:
            raise ConfigurationError(
                f"Erreur lors du chargement de la configuration: {e}"
            )

    def _merge_config(self, config_data: Dict[str, Any]):
        """Fusionne la configuration chargée avec les valeurs par défaut"""

        # Mise à jour des seuils
        if "thresholds" in config_data:
            threshold_data = config_data["thresholds"]
            for key, value in threshold_data.items():
                if hasattr(self.config.thresholds, key):
                    setattr(self.config.thresholds, key, value)

        # Mise à jour de la configuration de rapport
        if "reporting" in config_data:
            reporting_data = config_data["reporting"]
            for key, value in reporting_data.items():
                if hasattr(self.config.reporting, key):
                    setattr(self.config.reporting, key, value)

        # Mise à jour des listes
        for list_key in ["enabled_validators", "enabled_analyzers", "output_formats"]:
            if list_key in config_data:
                setattr(self.config, list_key, config_data[list_key])

        # Mise à jour du niveau de log
        if "log_level" in config_data:
            self.config.log_level = config_data["log_level"]

    def save_to_file(self, output_file: Path):
        """Sauvegarde la configuration dans un fichier"""
        config_dict = asdict(self.config)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise ConfigurationError(f"Erreur lors de la sauvegarde: {e}")

    def get_threshold(self, threshold_name: str) -> Union[int, float]:
        """Récupère un seuil spécifique"""
        if hasattr(self.config.thresholds, threshold_name):
            return getattr(self.config.thresholds, threshold_name)
        else:
            raise ConfigurationError(f"Seuil inconnu: {threshold_name}")

    def set_threshold(self, threshold_name: str, value: Union[int, float]):
        """Définit un seuil spécifique"""
        if hasattr(self.config.thresholds, threshold_name):
            setattr(self.config.thresholds, threshold_name, value)
        else:
            raise ConfigurationError(f"Seuil inconnu: {threshold_name}")

    def is_validator_enabled(self, validator_name: str) -> bool:
        """Vérifie si un validateur est activé"""
        return validator_name in self.config.enabled_validators

    def is_analyzer_enabled(self, analyzer_name: str) -> bool:
        """Vérifie si un analyseur est activé"""
        return analyzer_name in self.config.enabled_analyzers

    def get_output_formats(self) -> list:
        """Récupère les formats de sortie activés"""
        return self.config.output_formats.copy()

    def validate_config(self) -> Dict[str, Any]:
        """Valide la configuration et retourne un rapport"""
        validation_result = {"valid": True, "warnings": [], "errors": []}

        # Validation des seuils
        thresholds = self.config.thresholds

        if thresholds.max_lines_per_file < 50:
            validation_result["warnings"].append("Seuil de lignes très bas (<50)")
        elif thresholds.max_lines_per_file > 500:
            validation_result["warnings"].append("Seuil de lignes très élevé (>500)")

        if thresholds.min_docstring_coverage > 100:
            validation_result["errors"].append("Couverture docstring > 100%")
            validation_result["valid"] = False

        if thresholds.security_score_threshold > 100:
            validation_result["errors"].append("Seuil sécurité > 100")
            validation_result["valid"] = False

        # Validation des composants activés
        if not self.config.enabled_validators:
            validation_result["warnings"].append("Aucun validateur activé")

        if not self.config.output_formats:
            validation_result["errors"].append("Aucun format de sortie activé")
            validation_result["valid"] = False

        return validation_result

    def create_validator_config(self, validator_name: str) -> Dict[str, Any]:
        """Crée une configuration spécifique pour un validateur"""
        base_config = {
            "enabled": self.is_validator_enabled(validator_name),
            "log_level": self.config.log_level,
            "verbose": self.config.reporting.verbose_mode,
        }

        # Configuration spécifique par validateur
        if validator_name == "line_validator":
            base_config.update({"max_lines": self.config.thresholds.max_lines_per_file})
        elif validator_name == "security_validator":
            base_config.update(
                {"score_threshold": self.config.thresholds.security_score_threshold}
            )

        return base_config

    def create_analyzer_config(self, analyzer_name: str) -> Dict[str, Any]:
        """Crée une configuration spécifique pour un analyseur"""
        base_config = {
            "enabled": self.is_analyzer_enabled(analyzer_name),
            "log_level": self.config.log_level,
            "verbose": self.config.reporting.verbose_mode,
        }

        # Configuration spécifique par analyseur
        if analyzer_name == "ast_analyzer":
            base_config.update(
                {
                    "max_cyclomatic_complexity": self.config.thresholds.max_cyclomatic_complexity,
                    "max_cognitive_complexity": self.config.thresholds.max_cognitive_complexity,
                    "max_nesting_depth": self.config.thresholds.max_nesting_depth,
                }
            )

        return base_config

    def get_reporting_config(self) -> Dict[str, Any]:
        """Récupère la configuration de rapport"""
        return asdict(self.config.reporting)


class ConfigurationError(Exception):
    """Exception pour les erreurs de configuration"""

    pass


# Gestionnaire global de configuration
_global_config_manager: Optional[ConfigManager] = None


def get_global_config() -> ConfigManager:
    """Récupère le gestionnaire de configuration global"""
    global _global_config_manager

    if _global_config_manager is None:
        _global_config_manager = ConfigManager()

    return _global_config_manager


def load_config_from_file(config_file: Path) -> ConfigManager:
    """Charge la configuration depuis un fichier"""
    global _global_config_manager
    _global_config_manager = ConfigManager(config_file)
    return _global_config_manager


def reset_config():
    """Remet à zéro la configuration globale"""
    global _global_config_manager
    _global_config_manager = None


def create_default_config_file(output_file: Path):
    """Crée un fichier de configuration par défaut"""
    default_manager = ConfigManager()
    default_manager.save_to_file(output_file)


# Fonction utilitaire pour accès rapide aux seuils
def get_threshold(name: str) -> Union[int, float]:
    """Accès rapide à un seuil de configuration"""
    return get_global_config().get_threshold(name)


if __name__ == "__main__":
    # Test du gestionnaire de configuration
    import tempfile

    print("⚙️ Test du gestionnaire de configuration AGI")
    print("=" * 50)

    # Test configuration par défaut
    config_manager = ConfigManager()
    print(
        f"Seuil lignes par défaut: {config_manager.get_threshold('max_lines_per_file')}"
    )
    print(f"Validateurs activés: {config_manager.config.enabled_validators}")

    # Test validation
    validation = config_manager.validate_config()
    print(f"Configuration valide: {validation['valid']}")
    if validation["warnings"]:
        print(f"Avertissements: {validation['warnings']}")

    # Test sauvegarde/chargement
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.json"

        # Modification et sauvegarde
        config_manager.set_threshold("max_lines_per_file", 150)
        config_manager.save_to_file(config_file)

        # Rechargement
        new_config = ConfigManager(config_file)
        print(f"Seuil rechargé: {new_config.get_threshold('max_lines_per_file')}")

        print(f"Configuration sauvegardée dans: {config_file}")
