#!/usr/bin/env python3
"""
Header Check Rule - Règle de Validation pour l'En-tête Constitutionnel
=======================================================================

CHEMIN: compliance/rules/header_check_rule.py

Rôle Fondamental (Conforme iaGOD.json) :
- Implémenter la logique de validation pour la loi AGI-HEADER-001.
- Vérifier la présence d'un en-tête constitutionnel dans les fichiers.
- Être un module spécialisé, autonome et conforme.
- Respecter la directive < 200 lignes.
"""

import logging
from pathlib import Path

# Import des contrats et de l'interface de base
from compliance.models import AuditContext, Violation
from .base_rule import BaseRule


class HeaderCheckRule(BaseRule):
    """
    Implémente la règle sur la présence d'un en-tête constitutionnel.
    """

    def apply(self, file_path: Path, context: AuditContext):
        """
        Vérifie la présence de marqueurs d'en-tête constitutionnel.

        Args:
            file_path: Le chemin du fichier à auditer.
            context: Le contexte global de l'audit pour ajouter les violations.
        """
        try:
            with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                # Lire les 500 premiers caractères est suffisant et performant
                header_content = f.read(500)

            markers = [
                "Rôle Fondamental",
                "Conforme AGI.md",
                "CHEMIN:",
                "Conformité Architecturale",
                "Conforme iaGOD.json",
            ]

            if not any(marker in header_content for marker in markers):
                violation = Violation(
                    law=self.law,
                    file_path=file_path,
                    line_number=1,
                    severity="MEDIUM",
                    message="L'en-tête constitutionnel AGI est manquant ou non conforme.",
                    suggestion="Ajouter un en-tête décrivant le rôle et la conformité du fichier.",
                )
                context.add_violation(violation)

        except Exception as e:
            logging.getLogger(__name__).error(
                f"Erreur lors de l'application de HeaderCheckRule sur {file_path}: {e}"
            )
