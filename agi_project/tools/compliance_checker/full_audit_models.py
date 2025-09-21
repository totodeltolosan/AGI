#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_checker/full_audit_models.py
Rôle Fondamental (Conforme iaGOD.json) :
- Classes de données pour l'audit constitutionnel AGI
- Modèles et énumérations conformes constitution
- Taille: <200 lignes MAX
"""

from dataclasses import dataclass
from typing import List
from enum import Enum


class ComplianceStatus(Enum):
    """Statut de conformité d'une directive constitutionnelle"""
    RESPECTEE = "✅ RESPECTÉE"
    VIOLEE = "❌ VIOLÉE"
    NON_APPLICABLE = "⚠ NON APPLICABLE"
    INDETERMINE = "❓ INDÉTERMINÉ"


@dataclass
class DirectiveResult:
    """Résultat de vérification d'une directive constitutionnelle"""
    id: str
    description: str
    status: ComplianceStatus
    details: str
    severity: str = "MEDIUM"
    file_path: str = ""


@dataclass
class FileAuditResult:
    """Résultat complet d'audit constitutionnel d'un fichier"""
    file_path: str
    line_count: int
    size_bytes: int
    directives_results: List[DirectiveResult]
    global_score: float
    critical_violations: int
    warnings: int
    
    def is_compliant(self) -> bool:
        """Vérifie si le fichier est globalement conforme"""
        return self.critical_violations == 0 and self.global_score >= 0.8
    
    def get_violation_count(self) -> int:
        """Retourne le nombre total de violations"""
        return len([r for r in self.directives_results 
                   if r.status == ComplianceStatus.VIOLEE])
