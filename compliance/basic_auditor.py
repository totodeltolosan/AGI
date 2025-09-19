#!/usr/bin/env python3
"""
Basic Auditor - Auditeur Basique Conforme COMP-CGR-001 (Version Corrigée)
=======================================================

CHEMIN: compliance/basic_auditor.py

Rôle Fondamental (Conforme iaGOD.json COMP-CGR-001) :
- Auditer UNIQUEMENT le code du projet (exclure .venv/, __pycache__, etc.)
- Respecter directive < 200 lignes
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .constitution_loader import ConstitutionLoader, ConstitutionalLaw

@dataclass
class ViolationReport:
    """Rapport de violation constitutionnelle"""
    law_id: str
    law_name: str
    file_path: str
    line_number: int
    severity: str
    description: str
    suggested_fix: Optional[str] = None

class BasicAuditor:
    """Auditeur Basique AGI - Conforme COMP-CGR-001"""
    
    def __init__(self, constitution_loader: ConstitutionLoader):
        self.logger = logging.getLogger(__name__)
        self.constitution = constitution_loader
        self.violations: List[ViolationReport] = []
        
        # Répertoires à exclure (dépendances externes)
        self.excluded_dirs = {
            ".venv", "__pycache__", ".git", "node_modules", 
            ".pytest_cache", ".mypy_cache", "backup_old_files"
        }
        
    def audit_directory(self, target_path: Path) -> List[ViolationReport]:
        """Audite UNIQUEMENT les fichiers du projet"""
        self.violations.clear()
        
        if not self.constitution.is_loaded():
            self.logger.error("Constitution non chargée")
            return []
            
        # Fichiers Python du projet uniquement
        python_files = []
        for py_file in target_path.rglob("*.py"):
            if not any(excluded in py_file.parts for excluded in self.excluded_dirs):
                python_files.append(py_file)
        
        self.logger.info(f"Audit de {len(python_files)} fichiers Python (projet uniquement)")
        
        for py_file in python_files:
            self._audit_file(py_file)
            
        self.logger.info(f"Audit terminé: {len(self.violations)} violations")
        return self.violations
    
    def _audit_file(self, file_path: Path):
        """Audite un fichier Python spécifique"""
        try:
            self._check_line_limit(file_path)
            self._check_python_syntax(file_path)
            self._check_constitutional_practices(file_path)
        except Exception as e:
            self.logger.error(f"Erreur audit {file_path}: {e}")
    
    def _check_line_limit(self, file_path: Path):
        """Vérifie limite 200 lignes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            line_count = len(lines)
            
            if line_count > 200:
                self.violations.append(ViolationReport(
                    law_id="AGI-LIMIT-001",
                    law_name="Contrainte de Taille (200 Lignes)",
                    file_path=str(file_path),
                    line_number=line_count,
                    severity="CRITICAL",
                    description=f"Fichier dépasse la limite: {line_count} lignes (max: 200)",
                    suggested_fix="Refactoriser en modules plus petits selon architecture AGI"
                ))
        except Exception as e:
            self.logger.error(f"Erreur vérification lignes {file_path}: {e}")
    
    def _check_python_syntax(self, file_path: Path):
        """Vérifie syntaxe Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            ast.parse(source_code)
        except SyntaxError as e:
            self.violations.append(ViolationReport(
                law_id="PYTHON-SYNTAX-001",
                law_name="Syntaxe Python Valide",
                file_path=str(file_path),
                line_number=e.lineno or 0,
                severity="CRITICAL",
                description=f"Erreur syntaxe: {e.msg}",
                suggested_fix="Corriger l'erreur de syntaxe Python"
            ))
        except Exception as e:
            self.logger.error(f"Erreur vérification syntaxe {file_path}: {e}")
    
    def _check_constitutional_practices(self, file_path: Path):
        """Vérifie bonnes pratiques constitutionnelles"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not self._has_constitutional_header(content):
                self.violations.append(ViolationReport(
                    law_id="AGI-HEADER-001",
                    law_name="En-tête Constitutionnel AGI",
                    file_path=str(file_path),
                    line_number=1,
                    severity="MEDIUM",
                    description="Fichier manque l'en-tête constitutionnel AGI",
                    suggested_fix="Ajouter en-tête avec rôle et conformité AGI.md"
                ))
        except Exception as e:
            self.logger.error(f"Erreur vérification pratiques {file_path}: {e}")
    
    def _has_constitutional_header(self, content: str) -> bool:
        """Vérifie en-tête conforme"""
        markers = ["Rôle Fondamental", "Conforme AGI.md", "CHEMIN:", "Conformité Architecturale"]
        return any(marker in content[:500] for marker in markers)
    
    def get_violations_by_severity(self, severity: str) -> List[ViolationReport]:
        """Récupère violations par sévérité"""
        return [v for v in self.violations if v.severity == severity]
    
    def get_critical_violations(self) -> List[ViolationReport]:
        """Récupère violations critiques"""
        return self.get_violations_by_severity("CRITICAL")
    
    def has_violations(self) -> bool:
        """Vérifie s'il y a des violations"""
        return len(self.violations) > 0
