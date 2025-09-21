#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_checker/full_audit_analysis.py
Rôle Fondamental (Conforme iaGOD.json) :
- Méthodes d'analyse constitutionnelle AGI
- Vérification architecture, modularité, sécurité
- Extension de ConstitutionalAuditor
- Taille: <200 lignes MAX
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any

from .full_audit_models import ComplianceStatus, DirectiveResult


class ConstitutionalAnalyzer:
    """Analyseur pour directives architecturales et sécuritaires"""
    
    def __init__(self, constitution_rules: Dict[str, Any]):
        """Initialise avec les règles constitutionnelles"""
        self.constitution_rules = constitution_rules
    
    def _check_line_limit(self, file_path: Path, line_count: int) -> DirectiveResult:
        """Vérifie la directive des 200 lignes maximum"""
        max_lines = self.constitution_rules["architecture"]["max_lines"]
        if line_count <= max_lines:
            return DirectiveResult(
                id="ARCH-001",
                description="Contrainte de Taille (200 lignes max)",
                status=ComplianceStatus.RESPECTEE,
                details=f"Fichier conforme: {line_count}/{max_lines} lignes",
                severity="CRITICAL",
                file_path=str(file_path),
            )
        else:
            excess = line_count - max_lines
            return DirectiveResult(
                id="ARCH-001",
                description="Contrainte de Taille (200 lignes max)",
                status=ComplianceStatus.VIOLEE,
                details=f"Excès de {excess} lignes ({line_count}/{max_lines})",
                severity="CRITICAL",
                file_path=str(file_path),
            )
    
    def _check_modularity(self, file_path: Path, tree: ast.AST, content: str) -> DirectiveResult:
        """Vérifie le principe de responsabilité unique"""
        # Compter les classes et fonctions
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        # Analyser la complexité
        total_complexity = 0
        for func in functions:
            # Compter les if, for, while, try comme indicateurs de complexité
            complexity = 0
            for node in ast.walk(func):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    complexity += 1
            total_complexity += complexity
        
        # Critères de modularité
        issues = []
        if len(classes) > 3:
            issues.append(f"Trop de classes ({len(classes)} > 3)")
        if len(functions) > 15:
            issues.append(f"Trop de fonctions ({len(functions)} > 15)")
        if total_complexity > 50:
            issues.append(f"Complexité excessive ({total_complexity} > 50)")
        
        # Vérifier les imports pour détecter la surcharge
        import_count = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
        if import_count > 20:
            issues.append(f"Trop d'imports ({import_count} > 20)")
        
        if not issues:
            return DirectiveResult(
                id="MOD-001",
                description="Principe de responsabilité unique",
                status=ComplianceStatus.RESPECTEE,
                details=f"Module bien structuré: {len(classes)} classes, {len(functions)} fonctions",
                severity="HIGH",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="MOD-001",
                description="Principe de responsabilité unique",
                status=ComplianceStatus.VIOLEE,
                details=f"Problèmes détectés: {'; '.join(issues)}",
                severity="HIGH",
                file_path=str(file_path),
            )
    
    def _check_security(self, file_path: Path, tree: ast.AST, content: str) -> DirectiveResult:
        """Vérifie les aspects de sécurité"""
        security_issues = []
        
        # Vérifier les appels dangereux
        dangerous_calls = ["eval", "exec", "compile", "__import__"]
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in dangerous_calls:
                    security_issues.append(f"Appel dangereux: {node.func.id}")
        
        # Vérifier les opérations sur les fichiers
        file_operations = ["open", "file", "input"]
        unsecure_file_ops = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in file_operations:
                    unsecure_file_ops += 1
        
        # Vérifier les imports de modules sensibles
        sensitive_imports = ["os", "subprocess", "sys"]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in sensitive_imports:
                        # Vérifier si utilisé de manière sécurisée
                        if "system" in content or "popen" in content:
                            security_issues.append(f"Usage potentiellement dangereux de {alias.name}")
        
        # Vérifier les chemins de fichiers hardcodés
        if re.search(r'["\'][\/\\](?:home|root|etc|var)["\']', content):
            security_issues.append("Chemins absolus hardcodés détectés")
        
        if not security_issues:
            return DirectiveResult(
                id="SEC-001",
                description="Sécurité by design",
                status=ComplianceStatus.RESPECTEE,
                details="Aucun problème de sécurité détecté",
                severity="CRITICAL",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="SEC-001",
                description="Sécurité by design",
                status=ComplianceStatus.VIOLEE,
                details=f"Problèmes sécurité: {'; '.join(security_issues)}",
                severity="CRITICAL",
                file_path=str(file_path),
            )
