#!/usr/bin/env python3
"""
Line Limit Rule - Règle de Validation pour la Limite de Lignes
===============================================================

CHEMIN: compliance/rules/line_limit_rule.py

Rôle Fondamental (Conforme iaGOD.json) :
- Implémenter la logique de validation pour la loi AGI-LIMIT-001.
- Vérifier si un fichier dépasse la limite de 200 lignes.
- Être un module spécialisé, autonome et conforme.
- Respecter la directive < 200 lignes.
"""

import logging
from pathlib import Path

# Import des contrats et de l'interface de base
from compliance.models import AuditContext, Violation
from .base_rule import BaseRule


class LineLimitRule(BaseRule):
    """
    Implémente la règle constitutionnelle sur la limite de lignes par fichier.
    """

    def apply(self, file_path: Path, context: AuditContext):
        """
        Vérifie si le fichier dépasse la limite de 200 lignes.

        Args:
            file_path: Le chemin du fichier à auditer.
            context: Le contexte global de l'audit pour ajouter les violations.
        """
        try:
            with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                line_count = sum(1 for _ in f)

            # La limite est codée en dur car c'est une loi fondamentale
            limit = 200
            if line_count > limit:
                violation = Violation(
                    law=self.law,
                    file_path=file_path,
                    line_number=line_count,
                    severity="CRITICAL",
                    message=f"Le fichier dépasse la limite de {limit} lignes ({line_count} lignes trouvées).",
                    suggestion="Refactoriser en modules plus petits et spécialisés.",
                )
                context.add_violation(violation)

        except Exception as e:
            logging.getLogger(__name__).error(
                f"Erreur lors de l'application de LineLimitRule sur {file_path}: {e}"
            )
