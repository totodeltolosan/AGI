#!/usr/bin/env python3
"""
CHEMIN: tools/project_initializer/structure_config.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de configuration statique.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""Structure Config - Configuration Templates AGI"""

STRUCTURE_TEMPLATES = {
    "base_structure": ["core", "docs", "tests", "scripts", "config"],
    "web": {
        "directories": ["templates", "static", "api", "views", "models"],
        "files": [{"name": "app.py", "template": "# Application principale\n"}]
    },
    "api": {
        "directories": ["endpoints", "middleware", "schemas", "utils"],
        "files": [{"name": "main.py", "template": "# API principale\n"}]
    }
}

DEFAULT_CONFIG = {
    "create_init_files": True,
    "create_readme": True,
    "validate_names": True
}
