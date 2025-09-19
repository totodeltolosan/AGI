# tools/compliance_audit_system/detectors/__init__.py
"""Détecteurs d'environnement et de projet AGI"""
from .environment_detector import EnvironmentDetector, quick_environment_check
from .project_detector import ProjectDetector, quick_project_detection

__all__ = [
    "EnvironmentDetector",
    "ProjectDetector",
    "quick_environment_check",
    "quick_project_detection",
]
