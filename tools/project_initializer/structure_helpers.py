#!/usr/bin/env python3
"""
Structure Helpers - Utilitaires Structure Projet AGI
==================================================

CHEMIN: tools/project_initializer/structure_helpers.py
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
        """TODO: Add docstring."""
        self.logger = logging.getLogger(__name__)
        self.validator = StructureValidator()
        self.templates = STRUCTURE_TEMPLATES
        
    def create_project_structure(self, output_dir: Path, domains: List[str]) -> bool:
        """Créer structure projet conforme aux directives AGI"""
        try:
            self.logger.info(f"🏗️ Création structure: {output_dir}")
            
            if not self.validator.validate_output_directory(output_dir):
                return False
                
            self._create_base_directories(output_dir)
            
            for domain in domains:
                self._create_domain_structure(output_dir, domain)
                
            return self.validator.validate_created_structure(output_dir)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création structure: {e}")
            return False
    
    def _create_base_directories(self, output_dir: Path):
        """Créer répertoires de base du projet"""
        base_dirs = self.templates["base_structure"]
        
        for dir_name in base_dirs:
            dir_path = output_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"📁 Créé: {dir_path}")
    
    def _create_domain_structure(self, output_dir: Path, domain: str):
        """Créer structure spécifique d'un domaine"""
        if domain not in self.templates:
            self.logger.warning(f"⚠️ Domaine inconnu: {domain}")
            return
            
        domain_config = self.templates[domain]
        domain_path = output_dir / domain
        
        for subdir in domain_config.get("directories", []):
            subdir_path = domain_path / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            
        for file_config in domain_config.get("files", []):
            self._create_domain_file(domain_path, file_config)
    
    def _create_domain_file(self, domain_path: Path, file_config: Dict[str, Any]):
        """Créer fichier spécifique d'un domaine"""
        file_path = domain_path / file_config["name"]
        
        if file_path.exists() and not file_config.get("overwrite", False):
            return
            
        content = file_config.get("template", "")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.logger.debug(f"📄 Créé: {file_path}")
    
    def validate_project_compliance(self, project_dir: Path) -> Dict[str, Any]:
        """Valider conformité projet aux directives AGI"""
        return self.validator.full_compliance_check(project_dir)
    
    def get_structure_templates(self) -> Dict[str, Any]:
        """Retourner templates de structure disponibles"""
        return self.templates.copy()