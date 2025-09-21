#!/usr/bin/env python3
"""
CHEMIN: tools/project_initializer/config/data/__init__.py

Rôle Fondamental (Conforme iaGOD.json) :
- Package d'initialisation pour le module 'data'.
- Ce fichier respecte la constitution AGI.
"""

"""Config Data Package - Données de Configuration AGI"""
from .domain_data import DOMAIN_STRUCTURE, DOMAIN_METADATA, MASTER_LEVELS
from .python_files_data import DOMAIN_FILES, DEFAULT_IMPORTS, CLASS_PATTERNS, FILE_ROLES

__all__ = [
    "DOMAIN_STRUCTURE", "DOMAIN_METADATA", "MASTER_LEVELS",
    "DOMAIN_FILES", "DEFAULT_IMPORTS", "CLASS_PATTERNS", "FILE_ROLES"
]
