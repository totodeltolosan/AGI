#!/usr/bin/env python3
"""
Compliance Module - Système d'Audit Constitutionnel AGI
=======================================================

CHEMIN: compliance/__init__.py

Rôle Fondamental (Conforme iaGOD.json) :
- Point d'entrée du module d'audit constitutionnel
- Export des classes principales selon architecture AGI
- Interface unifiée pour l'audit des lois iaGOD.json
- Respecter directive < 200 lignes

Module conforme aux directives constitutionnelles:
- COMP-CST-001: Constitution Exécutable iaGOD.json
- COMP-CPL-001: Chargeur de Constitution Dynamique  
- COMP-CGR-001: Analyseur de Cause Racine et Propagation
"""

from .constitution_loader import ConstitutionLoader, ConstitutionalLaw
from .basic_auditor import BasicAuditor, ViolationReport
from .reporter import ConstitutionalReporter

__version__ = "1.0.0"
__author__ = "AGI Development Team"

# Exports principaux du module
__all__ = [
    "ConstitutionLoader",
    "ConstitutionalLaw", 
    "BasicAuditor",
    "ViolationReport",
    "ConstitutionalReporter"
]
