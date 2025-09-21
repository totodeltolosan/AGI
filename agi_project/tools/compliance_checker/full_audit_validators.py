#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_checker/full_audit_validators.py
Rôle Fondamental (Conforme iaGOD.json) :
- Validation conformité constitutionnelle AGI
- Vérification traçabilité et contrats
- Extension de ConstitutionalAuditor
- Taille: <200 lignes MAX
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any

from .full_audit_models import ComplianceStatus, DirectiveResult


class ConstitutionalValidator:
    """Validateur pour directives de traçabilité et contrats"""
    
    def __init__(self, constitution_rules: Dict[str, Any]):
        """Initialise avec les règles constitutionnelles"""
        self.constitution_rules = constitution_rules
    
    def _check_traceability(
        self, file_path: Path, tree: ast.AST, content: str
    ) -> DirectiveResult:
        """Vérifie les directives de traçabilité"""
        # Recherche de logging
        has_logging = bool(re.search(r"logging|logger|log\.", content, re.I))
        
        # Recherche de gestion d'erreurs
        try_except_blocks = [
            node for node in ast.walk(tree) if isinstance(node, ast.Try)
        ]
        
        # Vérification des docstrings
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        documented_functions = 0
        for func in functions:
            if (func.body and isinstance(func.body[0], ast.Expr) and 
                isinstance(func.body[0].value, ast.Constant)):
                documented_functions += 1
        
        documented_classes = 0
        for cls in classes:
            if (cls.body and isinstance(cls.body[0], ast.Expr) and 
                isinstance(cls.body[0].value, ast.Constant)):
                documented_classes += 1
        
        # Calcul des scores
        total_functions = len(functions)
        total_classes = len(classes)
        
        issues = []
        if not has_logging and total_functions > 5:
            issues.append("Absence de logging dans un module complexe")
        
        if len(try_except_blocks) == 0 and total_functions > 3:
            issues.append("Aucune gestion d'erreur détectée")
        
        doc_ratio_func = documented_functions / total_functions if total_functions > 0 else 1
        doc_ratio_class = documented_classes / total_classes if total_classes > 0 else 1
        
        if doc_ratio_func < 0.5:
            issues.append(f"Documentation insuffisante des fonctions ({doc_ratio_func:.1%})")
        
        if doc_ratio_class < 0.5 and total_classes > 0:
            issues.append(f"Documentation insuffisante des classes ({doc_ratio_class:.1%})")
        
        if not issues:
            return DirectiveResult(
                id="TRACE-001",
                description="Traçabilité complète",
                status=ComplianceStatus.RESPECTEE,
                details=f"Traçabilité OK: logging={has_logging}, {len(try_except_blocks)} try/except",
                severity="HIGH",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="TRACE-001",
                description="Traçabilité complète",
                status=ComplianceStatus.VIOLEE,
                details=f"Problèmes traçabilité: {'; '.join(issues)}",
                severity="HIGH",
                file_path=str(file_path),
            )
    
    def _check_contracts(self, file_path: Path, tree: ast.AST) -> DirectiveResult:
        """Vérifie les directives de gouvernance des contrats"""
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Vérification des type hints
        functions_with_hints = 0
        for func in functions:
            has_return_annotation = func.returns is not None
            has_arg_annotations = any(arg.annotation is not None for arg in func.args.args)
            if has_return_annotation or has_arg_annotations:
                functions_with_hints += 1
        
        # Vérification des interfaces claires
        functions_with_docstrings = 0
        for func in functions:
            if (func.body and isinstance(func.body[0], ast.Expr) and 
                isinstance(func.body[0].value, ast.Constant)):
                functions_with_docstrings += 1
        
        # Métriques
        total_functions = len(functions)
        hint_ratio = functions_with_hints / total_functions if total_functions > 0 else 1
        doc_ratio = functions_with_docstrings / total_functions if total_functions > 0 else 1
        
        issues = []
        if hint_ratio < 0.3 and total_functions > 2:
            issues.append(f"Type hints insuffisants ({hint_ratio:.1%})")
        
        if doc_ratio < 0.5 and total_functions > 2:
            issues.append(f"Docstrings insuffisantes ({doc_ratio:.1%})")
        
        # Vérifier la présence de __init__ dans les classes
        for cls in classes:
            has_init = any(
                isinstance(node, ast.FunctionDef) and node.name == "__init__"
                for node in cls.body
            )
            if not has_init:
                issues.append(f"Classe {cls.name} sans __init__")
        
        if not issues:
            return DirectiveResult(
                id="CONTRACT-001",
                description="Gouvernance des contrats",
                status=ComplianceStatus.RESPECTEE,
                details=f"Contrats OK: {hint_ratio:.1%} hints, {doc_ratio:.1%} docs",
                severity="MEDIUM",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="CONTRACT-001",
                description="Gouvernance des contrats",
                status=ComplianceStatus.VIOLEE,
                details=f"Problèmes contrats: {'; '.join(issues)}",
                severity="MEDIUM",
                file_path=str(file_path),
            )
