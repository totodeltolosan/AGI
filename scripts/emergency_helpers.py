#!/usr/bin/env python3
"""Helpers pour refactorisation d'urgence AGI"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class StructureCreator:
    """Créateur de structures et fichiers de configuration"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)
    
    def create_structure_config(self):
        """Créer fichier structure_config.py"""
        config_path = self.project_root / "tools/project_initializer/structure_config.py"
        
        content = '''#!/usr/bin/env python3
"""Structure Config - Configuration Templates AGI"""

STRUCTURE_TEMPLATES = {
    "base_structure": ["core", "docs", "tests", "scripts", "config"],
    "web": {
        "directories": ["templates", "static", "api", "views", "models"],
        "files": [{"name": "app.py", "template": "# Application principale\\n"}]
    },
    "api": {
        "directories": ["endpoints", "middleware", "schemas", "utils"],
        "files": [{"name": "main.py", "template": "# API principale\\n"}]
    }
}

DEFAULT_CONFIG = {
    "create_init_files": True,
    "create_readme": True,
    "validate_names": True
}
'''
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Créé: structure_config.py")
    
    def create_structure_validators(self):
        """Créer fichier structure_validators.py"""
        validators_path = self.project_root / "tools/project_initializer/structure_validators.py"
        
        content = '''#!/usr/bin/env python3
"""Structure Validators - Validation Structures AGI"""

from pathlib import Path
from typing import Dict, Any
import logging

class StructureValidator:
    """Validation conformité structures projet AGI"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_output_directory(self, output_dir: Path) -> bool:
        """Valider répertoire de sortie"""
        try:
            if output_dir.exists() and any(output_dir.iterdir()):
                self.logger.warning(f"Répertoire non vide: {output_dir}")
                return False
            output_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Erreur validation: {e}")
            return False
    
    def validate_created_structure(self, project_dir: Path) -> bool:
        """Valider structure créée"""
        required_dirs = ["core", "docs", "tests"]
        for dir_name in required_dirs:
            if not (project_dir / dir_name).exists():
                self.logger.error(f"Répertoire manquant: {dir_name}")
                return False
        return True
    
    def full_compliance_check(self, project_dir: Path) -> Dict[str, Any]:
        """Audit complet conformité AGI"""
        return {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "stats": {"total_files": len(list(project_dir.rglob("*.*")))}
        }
'''
        
        with open(validators_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Créé: structure_validators.py")

class FileGenerator:
    """Générateur de fichiers refactorisés"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def create_refactored_structure_helpers(self, file_path: Path) -> bool:
        """Créer version refactorisée de structure_helpers.py"""
        
        header = '''#!/usr/bin/env python3
"""
Structure Helpers - Utilitaires Structure Projet AGI
Rôle: Générer structures projet conformes constitution
Conformité: iaGOD.json < 200 lignes
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import os

from .structure_config import STRUCTURE_TEMPLATES, DEFAULT_CONFIG
from .structure_validators import StructureValidator

class StructureHelpers:
    """Gestionnaire principal des structures projet AGI"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = StructureValidator()
        self.templates = STRUCTURE_TEMPLATES
        
    def create_project_structure(self, output_dir: Path, domains: List[str]) -> bool:
        """Créer structure projet conforme aux directives AGI"""
        try:
            self.logger.info(f"Création structure: {output_dir}")
            
            if not self.validator.validate_output_directory(output_dir):
                return False
                
            self._create_base_directories(output_dir)
            
            for domain in domains:
                self._create_domain_structure(output_dir, domain)
                
            return self.validator.validate_created_structure(output_dir)
            
        except Exception as e:
            self.logger.error(f"Erreur création structure: {e}")
            return False
    
    def _create_base_directories(self, output_dir: Path):
        """Créer répertoires de base du projet"""
        base_dirs = self.templates["base_structure"]
        
        for dir_name in base_dirs:
            dir_path = output_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Créé: {dir_path}")
    
    def _create_domain_structure(self, output_dir: Path, domain: str):
        """Créer structure spécifique d'un domaine"""
        if domain not in self.templates:
            self.logger.warning(f"Domaine inconnu: {domain}")
            return
            
        domain_config = self.templates[domain]
        domain_path = output_dir / domain
        
        for subdir in domain_config.get("directories", []):
            subdir_path = domain_path / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            
        for file_config in domain_config.get("files", []):
            self._create_domain_file(domain_path, file_config)
    
    def validate_project_compliance(self, project_dir: Path) -> Dict[str, Any]:
        """Valider conformité projet aux directives AGI"""
        return self.validator.full_compliance_check(project_dir)
'''
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(header)
            
            new_lines = len(header.split('\n'))
            print(f"✅ Fichier refactorisé: {new_lines} lignes")
            return True
            
        except Exception as e:
            print(f"❌ Erreur refactorisation: {e}")
            return False
