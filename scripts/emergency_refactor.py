#!/usr/bin/env python3
"""REFACTORISATION D'URGENCE AGI - CORRECTION VIOLATIONS CRITIQUES"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from .emergency_helpers import StructureCreator, FileGenerator

class EmergencyRefactor:
    """Gestionnaire principal refactorisation d'urgence AGI"""
    
    def __init__(self, project_root="/home/toni/Documents/Projet AGI"):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / f"backup_refactor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Fichiers critiques à refactoriser
        self.critical_files = [
            "tools/project_initializer/structure_helpers.py",
            "tools/project_initializer/file_generators/markdown_templates.py",
            "tools/project_initializer/generators/content.py",
            "tools/project_initializer/structure_generator.py",
            "tools/project_initializer/report_parser.py"
        ]
        
        self.structure_creator = StructureCreator(self.project_root)
        self.file_generator = FileGenerator(self.project_root)
        
    def create_backup(self):
        """Créer sauvegarde avant refactorisation"""
        print("💾 CRÉATION SAUVEGARDE REFACTORISATION")
        self.backup_dir.mkdir(exist_ok=True)
        
        for file_path in self.critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(full_path, backup_path)
                print(f"✅ Sauvegardé: {file_path}")
        
        print(f"📁 Sauvegarde: {self.backup_dir}")
        
    def refactor_structure_helpers(self):
        """Refactoriser structure_helpers.py principal"""
        print("\n🔧 REFACTORISATION: structure_helpers.py")
        
        file_path = self.project_root / "tools/project_initializer/structure_helpers.py"
        if not file_path.exists():
            print("❌ Fichier introuvable")
            return False
            
        # Générer version refactorisée
        success = self.file_generator.create_refactored_structure_helpers(file_path)
        
        if success:
            # Créer fichiers de support
            self.structure_creator.create_structure_config()
            self.structure_creator.create_structure_validators()
            print("✅ Structure helpers refactorisé avec succès")
            
        return success
    
    def run_emergency_refactor(self):
        """Exécuter refactorisation d'urgence complète"""
        print("🚨 DÉMARRAGE REFACTORISATION D'URGENCE AGI")
        
        self.create_backup()
        
        success_count = 0
        if self.refactor_structure_helpers():
            success_count += 1
            
        print(f"\n✅ REFACTORISATION TERMINÉE")
        print(f"Fichiers refactorisés: {success_count}")
        print(f"Sauvegarde: {self.backup_dir}")
        
        return success_count > 0

if __name__ == "__main__":
    refactor = EmergencyRefactor()
    success = refactor.run_emergency_refactor()
    exit(0 if success else 1)
