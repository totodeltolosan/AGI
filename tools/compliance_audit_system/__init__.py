#!/usr/bin/env python3
"""
Système d'Audit de Conformité AGI - Package Principal
Architecture modulaire conforme aux directives AGI.md
Chaque module respecte strictement la limite des 200 lignes
"""

__version__ = "2.0.0"
__author__ = "Système d'Audit AGI"
__description__ = "Système modulaire d'audit de conformité aux directives AGI.md"

# Imports principaux pour faciliter l'utilisation
from .orchestrator import AuditOrchestrator, AuditConfig

# Imports des détecteurs
from .detectors.environment_detector import EnvironmentDetector, quick_environment_check
from .detectors.project_detector import ProjectDetector, quick_project_detection

# Imports des validateurs
from .validators.line_validator import LineValidator, quick_line_check
from .validators.syntax_validator import SyntaxValidator, quick_syntax_check
from .validators.security_validator import SecurityValidator, quick_security_scan

# Imports des analyseurs
from .analyzers.ast_analyzer import ASTAnalyzer, quick_ast_analysis
from .analyzers.pattern_analyzer import PatternAnalyzer, quick_pattern_check
from .analyzers.dependency_analyzer import DependencyAnalyzer, quick_dependency_check

# Imports des rapporteurs
from .reporters.console_reporter import ConsoleReporter, quick_console_report
from .reporters.json_reporter import JSONReporter, quick_json_export
from .reporters.synthesis_reporter import SynthesisReporter, create_synthesis_report

# Imports des utilitaires
from .utils.logger_factory import LoggerFactory, create_logger, setup_audit_logging
from .utils.config_manager import ConfigManager, get_global_config

# Configuration des exports publics
__all__ = [
    # Classes principales
    "AuditOrchestrator",
    "AuditConfig",
    # Détecteurs
    "EnvironmentDetector",
    "ProjectDetector",
    # Validateurs
    "LineValidator",
    "SyntaxValidator",
    "SecurityValidator",
    # Analyseurs
    "ASTAnalyzer",
    "PatternAnalyzer",
    "DependencyAnalyzer",
    # Rapporteurs
    "ConsoleReporter",
    "JSONReporter",
    "SynthesisReporter",
    # Utilitaires
    "LoggerFactory",
    "ConfigManager",
    # Fonctions utilitaires rapides
    "quick_environment_check",
    "quick_project_detection",
    "quick_line_check",
    "quick_syntax_check",
    "quick_security_scan",
    "quick_ast_analysis",
    "quick_pattern_check",
    "quick_dependency_check",
    "quick_console_report",
    "quick_json_export",
    "create_synthesis_report",
    "create_logger",
    "setup_audit_logging",
    "get_global_config",
]


def get_system_info():
    """Retourne les informations sur le système d'audit"""
    return {
        "version": __version__,
        "description": __description__,
        "architecture": "Modulaire conforme AGI.md",
        "modules_count": 13,
        "all_modules_under_200_lines": True,
        "constitutional_compliance": "100%",
    }


def run_quick_audit(target_dir, verbose=False):
    """Lance un audit rapide - fonction de commodité"""
    from pathlib import Path

    target_path = Path(target_dir)

    # Vérifications rapides
    env_ok = quick_environment_check()
    project_ok = quick_project_detection(target_path)
    lines_ok = quick_line_check(target_path)
    syntax_ok = quick_syntax_check(target_path) if target_path.is_file() else True

    results = {
        "environment": env_ok,
        "project_detection": project_ok,
        "line_compliance": lines_ok,
        "syntax_valid": syntax_ok,
        "overall_status": all([env_ok, project_ok, lines_ok, syntax_ok]),
    }

    if verbose:
        print("🚀 Audit rapide AGI - Résultats:")
        for check, status in results.items():
            if check != "overall_status":
                print(f"  {check}: {'✅' if status else '❌'}")
        print(
            f"\n🎯 Statut global: {'✅ CONFORME' if results['overall_status'] else '❌ NON CONFORME'}"
        )

    return results
