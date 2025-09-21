#!/usr/bin/env python3
"""
CHEMIN: tools/project_initializer/config/data/python_files_data.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""Python Files Data - Données Statiques pour Configuration des Fichiers Python"""

DOMAIN_FILES = {
    "compliance": ["validator.py", "rules_engine.py", "__init__.py"],
    "core": ["orchestrator.py", "interfaces.py", "__init__.py"],
    "supervisor": ["monitor.py", "controller.py", "__init__.py"],
    "generators": ["code_generator.py", "template_engine.py", "__init__.py"],
    "integration": ["api_client.py", "connector.py", "__init__.py"]
}

DEFAULT_IMPORTS = {
    "base": ["from typing import Dict, List, Any, Optional", "from pathlib import Path", "import logging"],
    "__init__.py": []
}

CLASS_PATTERNS = {
    "manager": {"pattern": ["manager", "orchestrator"], "base_class": "BaseManager"},
    "validator": {"pattern": ["validator", "checker"], "base_class": "BaseValidator"}
}

FILE_ROLES = {
    "__init__.py": "Module d'initialisation",
    "orchestrator.py": "Orchestrateur principal",
    "validator.py": "Validateur de conformité"
}
