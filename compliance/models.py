#!/usr/bin/env python3
"""
Compliance Models - Contrats de Données pour l'Audit Constitutionnel
=====================================================================

CHEMIN: compliance/models.py

Rôle Fondamental (Conforme iaGOD.json) :
- Définir les structures de données immuables (contrats) utilisées par l'auditeur.
- Garantir une communication standardisée et découplée entre les modules.
- Respecter la directive < 200 lignes.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional


@dataclass(frozen=True)
class ConstitutionalLaw:
    """
    Représentation d'une loi constitutionnelle.
    Ce contrat est immuable (frozen=True) pour garantir la stabilité.
    """

    id: str
    name: str
    version: str
    description: str
    section_id: int
    specifications: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class Violation:
    """
    Représentation d'une violation constitutionnelle détectée.
    Ce contrat est immuable.
    """

    law: ConstitutionalLaw
    file_path: Path
    line_number: int
    message: str
    severity: str = "MEDIUM"
    suggestion: Optional[str] = None


@dataclass
class AuditContext:
    """
    Contexte d'un audit, contenant l'état et les configurations.
    Mutable pour permettre l'agrégation des résultats.
    """

    target_path: Path
    constitution: Dict[str, ConstitutionalLaw]
    violations: List[Violation] = field(default_factory=list)

    def add_violation(self, violation: Violation):
        """Ajoute une violation au contexte."""
        self.violations.append(violation)
