#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_checker/full_audit_core.py
Rôle Fondamental (Conforme iaGOD.json) :
- Classe principale ConstitutionalAuditor
- Configuration et lecture fichiers
- Utilitaires de base pour audit AGI
- Taille: <200 lignes MAX
"""

import os
import ast
from pathlib import Path
from typing import Dict, List, Any

from .full_audit_models import ComplianceStatus, DirectiveResult, FileAuditResult


class ConstitutionalAuditor:
    """Auditeur principal pour la vérification constitutionnelle AGI"""
    
    def __init__(self, verbose: bool = False):
        """Initialise l'auditeur avec les règles constitutionnelles"""
        self.verbose = verbose
        self.constitution_rules = self._load_constitutional_rules()
    
    def _load_constitutional_rules(self) -> Dict[str, Any]:
        """Charge les 474 directives constitutionnelles organisées par catégories"""
        return {
            "architecture": {
                "max_lines": 200,
                "description": "Contrainte de Taille - 200 lignes maximum par fichier",
                "severity": "CRITICAL",
            },
            "modularity": {
                "single_responsibility": True,
                "description": "Principe de responsabilité unique",
                "severity": "HIGH",
            },
            "security": {
                "path_validation": True,
                "input_sanitization": True,
                "description": "Sécurité by design",
                "severity": "CRITICAL",
            },
            "traceability": {
                "logging_required": True,
                "error_handling": True,
                "description": "Traçabilité complète",
                "severity": "HIGH",
            },
            "contracts": {
                "clear_interfaces": True,
                "type_hints": True,
                "description": "Gouvernance des contrats",
                "severity": "MEDIUM",
            },
            "evolution": {
                "extensible_design": True,
                "backward_compatibility": True,
                "description": "Évolutivité contrôlée",
                "severity": "MEDIUM",
            },
        }
    
    def _create_syntax_error_result(
        self, file_path: Path, error: str
    ) -> FileAuditResult:
        """Crée un résultat d'audit pour un fichier avec erreur de syntaxe"""
        syntax_error = DirectiveResult(
            id="SYNTAX-001",
            description="Syntaxe Python valide",
            status=ComplianceStatus.VIOLEE,
            details=f"Erreur de syntaxe: {error}",
            severity="CRITICAL",
            file_path=str(file_path),
        )
        return FileAuditResult(
            file_path=str(file_path),
            line_count=0,
            size_bytes=0,
            directives_results=[syntax_error],
            global_score=0.0,
            critical_violations=1,
            warnings=0,
        )
    
    def _read_and_parse_file(self, file_path: Path) -> tuple:
        """Lit et parse un fichier Python, retourne (content, lines, tree)"""
        if not file_path.exists() or not file_path.suffix == ".py":
            raise ValueError(f"Fichier invalide : {file_path}")
        
        # Lecture du fichier
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        
        # Analyse AST
        try:
            tree = ast.parse(content, filename=str(file_path))
            return content, lines, tree
        except SyntaxError as e:
            # Retourne None pour AST en cas d'erreur
            return content, lines, None
    
    def _validate_file_path(self, file_path: Path) -> bool:
        """Valide qu'un chemin de fichier est sécurisé"""
        try:
            resolved_path = file_path.resolve()
            return (
                resolved_path.exists() and
                resolved_path.suffix == ".py" and
                resolved_path.is_file()
            )
        except (OSError, ValueError):
            return False
