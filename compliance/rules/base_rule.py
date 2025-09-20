#!/usr/bin/env python3
"""
Base Rule Interface - Contrat pour Toutes les Règles d'Audit (Corrigé)
======================================================================

CHEMIN: compliance/rules/base_rule.py

Rôle Fondamental (Conforme iaGOD.json) :
- Définir l'interface abstraite (le contrat) que toutes les règles d'audit
  doivent implémenter.
- Garantir un comportement uniforme et prédictible pour chaque règle.
- Promouvoir le découplage entre l'orchestrateur et les règles spécifiques.
- Respecter la directive < 200 lignes.
"""

from abc import ABC, abstractmethod
from pathlib import Path

# Import des contrats de données via un import relatif explicite
# C'est la correction clé pour résoudre l'ImportError
from ..models import AuditContext, ConstitutionalLaw


class BaseRule(ABC):
    """
    Interface abstraite pour une règle de validation constitutionnelle.

    Chaque règle concrète doit hériter de cette classe et implémenter
    la méthode `apply`.
    """

    def __init__(self, law: ConstitutionalLaw):
        """
        Initialise la règle avec la loi constitutionnelle qu'elle représente.

        Args:
            law: L'objet ConstitutionalLaw associé à cette règle.
        """
        self.law = law

    @abstractmethod
    def apply(self, file_path: Path, context: AuditContext):
        """
        Applique la logique de validation de la règle à un fichier donné.

        Si une violation est détectée, cette méthode doit l'ajouter au contexte
        en utilisant `context.add_violation()`.

        Args:
            file_path: Le chemin du fichier à auditer.
            context: Le contexte global de l'audit, contenant les résultats.
        """
        raise NotImplementedError("Chaque règle doit implémenter la méthode 'apply'.")

    def __repr__(self) -> str:
        """TODO: Add docstring."""
        return f"<{self.__class__.__name__}(law_id='{self.law.id}')>"