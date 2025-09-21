#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_audit_system/reporters/__init__.py

Rôle Fondamental (Conforme iaGOD.json) :
- Package d'initialisation pour le module 'reporters'.
- Ce fichier respecte la constitution AGI.
"""

# tools/compliance_audit_system/reporters/__init__.py
"""Rapporteurs pour audit AGI"""
from .console_reporter import ConsoleReporter, quick_console_report
from .json_reporter import JSONReporter, quick_json_export
from .synthesis_reporter import SynthesisReporter, create_synthesis_report

__all__ = [
    "ConsoleReporter",
    "JSONReporter",
    "SynthesisReporter",
    "quick_console_report",
    "quick_json_export",
    "create_synthesis_report",
]
