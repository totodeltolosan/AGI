#!/usr/bin/env python3
"""
CHEMIN: tools/project_initializer/config/utils/config_helpers.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module utilitaire avec fonctions de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""Config Helpers - Fonctions Utilitaires pour Configuration AGI"""

from typing import Dict, List, Any
try:
    from ..data.python_files_data import DOMAIN_FILES, DEFAULT_IMPORTS, CLASS_PATTERNS, FILE_ROLES
    from ..data.domain_data import DOMAIN_STRUCTURE
except ImportError:
    DOMAIN_FILES = {
        "core": ["orchestrator.py", "interfaces.py", "__init__.py"],
        "compliance": ["validator.py", "rules_engine.py", "__init__.py"],
        "supervisor": ["monitor.py", "controller.py", "__init__.py"]
    }
    DOMAIN_STRUCTURE = {
        "core": {"priority": 1, "master_level": "+++"},
        "compliance": {"priority": 2, "master_level": "+++"},
        "supervisor": {"priority": 3, "master_level": "+++"}
    }
    DEFAULT_IMPORTS = {"base": ["from typing import Dict, List, Any, Optional"]}
    CLASS_PATTERNS = {"manager": {"pattern": ["manager"], "base_class": "BaseManager"}}
    FILE_ROLES = {"__init__.py": "Module d'initialisation"}

def get_files_for_domain(domain: str) -> List[str]:
    """Récupère la liste des fichiers Python pour un domaine."""
    return DOMAIN_FILES.get(domain, [f"{domain}_manager.py", "__init__.py"])

def get_all_python_files() -> Dict[str, List[str]]:
    """Retourne tous les fichiers Python organisés par domaine."""
    return DOMAIN_FILES.copy()

def get_default_imports_for_file(filename: str) -> List[str]:
    """Récupère les imports par défaut pour un fichier."""
    return DEFAULT_IMPORTS.get("base", []).copy()

def get_class_pattern_for_file(filename: str) -> Dict[str, Any]:
    """Détermine le pattern de classe pour un fichier."""
    return {"pattern": ["generic"], "base_class": "object"}

def get_role_for_file(filename: str) -> str:
    """Retourne le rôle d'un fichier."""
    return FILE_ROLES.get(filename, f'Module {filename.replace(".py", "")}')

def get_domains_by_priority() -> List[str]:
    """Retourne les domaines triés par priorité."""
    domains_with_priority = [(config.get("priority", 10), domain) for domain, config in DOMAIN_STRUCTURE.items()]
    domains_with_priority.sort(key=lambda x: x[0])
    return [domain for _, domain in domains_with_priority]

def get_master_domains() -> List[str]:
    """Retourne les domaines maître."""
    return [domain for domain, config in DOMAIN_STRUCTURE.items() if config.get("master_level") == "+++"]

def get_domain_config(domain_name: str) -> Dict[str, Any]:
    """Retourne la configuration d'un domaine."""
    return DOMAIN_STRUCTURE.get(domain_name, {"priority": 10, "master_level": ""})

def validate_domain_structure() -> bool:
    """Valide la structure des domaines."""
    return len(DOMAIN_STRUCTURE) > 0

def validate_python_files_config() -> bool:
    """Valide la configuration des fichiers Python."""
    return len(DOMAIN_FILES) > 0

def get_domain_creation_order() -> List[str]:
    """Retourne l'ordre de création des domaines."""
    return get_domains_by_priority()
