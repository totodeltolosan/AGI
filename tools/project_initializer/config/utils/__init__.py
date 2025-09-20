#!/usr/bin/env python3
"""
CHEMIN: tools/project_initializer/config/utils/__init__.py

Rôle Fondamental (Conforme iaGOD.json) :
- Package d'initialisation pour le module 'utils'.
- Ce fichier respecte la constitution AGI.
"""

"""Config Utils Package - Utilitaires de Configuration AGI"""
from .config_helpers import (
    get_files_for_domain, get_all_python_files, get_default_imports_for_file,
    get_class_pattern_for_file, get_role_for_file, get_domains_by_priority,
    get_master_domains, get_domain_config, validate_domain_structure,
    validate_python_files_config, get_domain_creation_order
)

__all__ = [
    "get_files_for_domain", "get_all_python_files", "get_default_imports_for_file",
    "get_class_pattern_for_file", "get_role_for_file", "get_domains_by_priority",
    "get_master_domains", "get_domain_config", "validate_domain_structure",
    "validate_python_files_config", "get_domain_creation_order"
]
