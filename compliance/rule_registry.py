#!/usr/bin/env python3
"""
Rule Registry - Registre Central des Règles d'Audit
=====================================================

CHEMIN: compliance/rule_registry.py

Rôle Fondamental (Conforme iaGOD.json) :
- Fournir un mapping explicite entre les ID des lois constitutionnelles
  et les classes de règles Python qui les implémentent.
- Centraliser la connaissance de l'implémentation des règles.
- Permettre l'extensibilité de l'auditeur sans modifier l'orchestrateur.
- Respecter la directive < 200 lignes.
"""

from typing import Dict, Type

# Import de l'interface de base et de toutes les règles concrètes
from .rules.base_rule import BaseRule
from .rules.line_limit_rule import LineLimitRule
from .rules.header_check_rule import HeaderCheckRule
from .rules.syntax_rule import SyntaxRule  # <-- NOUVEL IMPORT


def get_rule_registry() -> Dict[str, Type[BaseRule]]:
    """
    Retourne le dictionnaire mappant les ID de lois à leurs classes d'implémentation.

    Returns:
        Un dictionnaire où la clé est l'ID de la loi (str) et la valeur
        est la classe de la règle (non instanciée).
    """
    return {
        # Loi sur la limite de lignes
        "COMP-ARC-001": LineLimitRule,
        # Loi sur la documentation/en-tête
        "DEV-DOC-001": HeaderCheckRule,
        # NOUVELLE RÈGLE : Loi sur la sécurité et la fiabilité
        # Cette règle vérifiera la syntaxe, la complexité, les docstrings, etc.
        "COMP-SEC-001": SyntaxRule,
    }
