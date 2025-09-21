#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_checker/full_audit_verification.py
Rôle Fondamental (Conforme iaGOD.json) :
- Vérification évolutivité constitutionnelle AGI
- Validation compatibilité et extensibilité
- Extension de ConstitutionalAuditor
- Taille: <200 lignes MAX
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any

from .full_audit_models import ComplianceStatus, DirectiveResult


class ConstitutionalVerifier:
    """Vérificateur pour directives d'évolutivité"""
    
    def __init__(self, constitution_rules: Dict[str, Any]):
        """Initialise avec les règles constitutionnelles"""
        self.constitution_rules = constitution_rules
    
    def _check_evolution(
        self, file_path: Path, tree: ast.AST, content: str
    ) -> DirectiveResult:
        """Vérifie les directives d'évolutivité"""
        # Recherche de patterns d'extensibilité
        extensibility_patterns = [
            (r"abstract", "Classes abstraites pour extensibilité"),
            (r"Protocol|typing\.Protocol", "Protocols pour interfaces"),
            (r"@.*property", "Properties pour encapsulation"),
            (r"def __.*__", "Méthodes magiques pour flexibilité"),
            (r"yield|generator", "Générateurs pour performance"),
            (r"@.*decorator", "Décorateurs pour extension"),
        ]
        
        score = 0
        for pattern, description in extensibility_patterns:
            if re.search(pattern, content):
                score += 1
        
        # Vérification de la compatibilité (évite les breaking changes)
        breaking_changes = []
        
        # Recherche de suppressions potentielles
        if re.search(r"del\s+\w+", content):
            breaking_changes.append("Suppression de variables/attributs")
        
        # Vérification des NotImplementedError (bon pour extensibilité)
        if re.search(r"raise\s+NotImplementedError", content):
            # C'est en fait positif pour l'extensibilité
            score += 1
        
        # Évaluation finale
        if score >= 2:
            return DirectiveResult(
                id="EVOL-001",
                description="Évolutivité contrôlée",
                status=ComplianceStatus.RESPECTEE,
                details=f"Bonne évolutivité: {score} patterns détectés",
                severity="MEDIUM",
                file_path=str(file_path),
            )
        elif breaking_changes:
            return DirectiveResult(
                id="EVOL-001",
                description="Évolutivité contrôlée",
                status=ComplianceStatus.VIOLEE,
                details=f"Breaking changes détectés: {'; '.join(breaking_changes)}",
                severity="MEDIUM",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="EVOL-001",
                description="Évolutivité contrôlée",
                status=ComplianceStatus.NON_APPLICABLE,
                details=f"Évolutivité limitée: {score} patterns seulement",
                severity="MEDIUM",
                file_path=str(file_path),
            )
