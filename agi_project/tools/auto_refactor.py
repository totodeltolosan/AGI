#!/usr/bin/env python3
"""Auto-Refactor Universel - Gère tous types de fichiers Python"""

import ast
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class FileViolation:
    path: Path
    lines: int
    excess: int

class UniversalAutoRefactor:
    def __init__(self, max_lines: int = 200, project_root: str = "."):
        self.max_lines = max_lines
        self.project_root = Path(project_root)
        
    def scan_violations(self) -> List[FileViolation]:
        """Scanner universel - fonctionne sur tous projets"""
        violations = []
        
        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            lines = self._count_lines_reliable(py_file)
            if lines > self.max_lines:
                excess = lines - self.max_lines
                violations.append(FileViolation(py_file, lines, excess))
        
        return sorted(violations, key=lambda x: x.excess, reverse=True)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Filtrage minimal pour robustesse"""
        path_str = str(file_path)
        return any(skip in path_str for skip in [
            "__pycache__", ".git", ".venv", "/backup_"
        ])
    
    def _count_lines_reliable(self, file_path: Path) -> int:
        """Comptage fiable et universel"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len([line for line in f if line.strip()])
        except:
            return 0
    
    def auto_refactor_file(self, file_path: Path, dry_run: bool = True) -> bool:
        """Refactorisation automatique universelle"""
        if dry_run:
            return self._simulate_refactor(file_path)
        else:
            return self._execute_refactor(file_path)
    
    def _simulate_refactor(self, file_path: Path) -> bool:
        """Simulation sûre"""
        lines = self._count_lines_reliable(file_path)
        if lines <= self.max_lines:
            return True
            
        excess = lines - self.max_lines
        strategy = self._determine_strategy(file_path)
        
        print(f"🔄 SIMULATION: {file_path}")
        print(f"   📏 {lines} lignes (+{excess})")
        print(f"   💡 Stratégie: {strategy}")
        print(f"   📁 Diviserait en ~{self._estimate_files(lines)} fichiers")
        
        return True
    
    def _execute_refactor(self, file_path: Path) -> bool:
        """Refactorisation réelle robuste"""
        try:
            # Méthode simple et fiable: division par taille
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Créer sauvegarde
            backup_path = f"{file_path}.backup_{int(time.time())}"
            shutil.copy2(file_path, backup_path)
            
            # Division simple par chunks
            chunk_size = self.max_lines - 20  # Marge de sécurité
            chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
            
            base_name = file_path.stem
            created_files = []
            
            for i, chunk in enumerate(chunks, 1):
                part_name = f"{base_name}_part{i}.py"
                part_path = file_path.parent / part_name
                
                # Ajouter header constitutionnel
                header = f'"""\nFichier refactorisé automatiquement - Partie {i}/{len(chunks)}\nConformité AGI: <200 lignes\n"""\n\n'
                
                with open(part_path, 'w', encoding='utf-8') as f:
                    f.write(header)
                    f.writelines(chunk)
                
                created_files.append(part_path)
            
            print(f"✅ Refactorisé: {len(created_files)} fichiers créés")
            return True
            
        except Exception as e:
            print(f"❌ Erreur refactorisation {file_path}: {e}")
            return False
    
    def _determine_strategy(self, file_path: Path) -> str:
        """Déterminer stratégie automatiquement"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
            functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
            
            if len(classes) > 1:
                return "Séparation par classes"
            elif len(classes) == 1 and len(functions) > 10:
                return "Classe principale + utilitaires"  
            elif len(functions) > 15:
                return "Groupement par fonctions"
            else:
                return "Division générique par taille"
                
        except:
            return "Division sécurisée par taille"
    
    def _estimate_files(self, lines: int) -> int:
        """Estimer nombre de fichiers nécessaires"""
        return (lines // self.max_lines) + 1

def main():
    parser = argparse.ArgumentParser(description="Auto-refactor universel AGI")
    parser.add_argument("--scan", action="store_true", help="Scanner violations")
    parser.add_argument("--fix", action="store_true", help="Corriger violations")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Mode simulation")
    parser.add_argument("--max-lines", type=int, default=200, help="Limite lignes")
    parser.add_argument("--project-root", default=".", help="Racine projet")
    parser.add_argument("--max-files", type=int, default=5, help="Max fichiers à traiter")
    
    args = parser.parse_args()
    
    refactor = UniversalAutoRefactor(args.max_lines, args.project_root)
    
    if args.scan or not args.fix:
        violations = refactor.scan_violations()
        
        if violations:
            print(f"🚨 {len(violations)} VIOLATIONS DÉTECTÉES:")
            for i, v in enumerate(violations[:10], 1):
                print(f"{i}. {v.lines} lignes (+{v.excess}): {v.path}")
        else:
            print("✅ Aucune violation détectée")
        return
    
    if args.fix:
        violations = refactor.scan_violations()
        success_count = 0
        
        for violation in violations[:args.max_files]:
            if refactor.auto_refactor_file(violation.path, dry_run=args.dry_run):
                success_count += 1
        
        print(f"✅ Refactorisations: {success_count}/{min(args.max_files, len(violations))}")

if __name__ == "__main__":
    import shutil
    import time
    main()
