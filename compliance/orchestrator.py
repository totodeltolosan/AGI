#!/usr/bin/env python3
"""
Audit Orchestrator - Chef d'Orchestre de l'Audit Constitutionnel (v2.2 Registre)
================================================================================

CHEMIN: compliance/orchestrator.py

Rôle Fondamental (Conforme iaGOD.json) :
- Orchestrer l'exécution des règles d'audit sur les fichiers du projet.
- Utiliser le registre de règles pour charger dynamiquement les validations.
- Agréger les violations dans un AuditContext.
- Respecter la directive < 200 lignes.
"""

import logging
from pathlib import Path
from typing import List, Dict

# Import des contrats, de l'interface de base, et du nouveau registre
from .models import AuditContext, ConstitutionalLaw
from .rules.base_rule import BaseRule
from .rule_registry import get_rule_registry


class AuditOrchestrator:
    """
    Orchestre l'audit en utilisant un registre central pour charger les règles
    correspondant aux lois définies dans la constitution.
    """

    def __init__(self, constitution: Dict[str, ConstitutionalLaw]):
        """TODO: Add docstring."""
        self.logger = logging.getLogger(__name__)
        self.constitution = constitution
        self.rules: List[BaseRule] = self._initialize_rules_from_registry()
        self.excluded_dirs = {
            ".venv",
            "venv",
            "env",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".git",
            ".github",
            "node_modules",
            "build",
            "dist",
            "backup_old_files",
        }

    def _initialize_rules_from_registry(self) -> List[BaseRule]:
        """
        Charge les règles en croisant la constitution chargée avec le registre.
        """
        initialized_rules = []
        rule_registry = get_rule_registry()

        for law_id, rule_class in rule_registry.items():
            if law_id in self.constitution:
                law = self.constitution[law_id]
                initialized_rules.append(rule_class(law))
                self.logger.debug(
                    f"Règle '{rule_class.__name__}' activée pour la loi '{law_id}'."
                )
            else:
                self.logger.debug(
                    f"Loi '{law_id}' non trouvée dans la constitution, règle ignorée."
                )

        if not initialized_rules:
            self.logger.warning(
                "Aucune règle d'audit n'a été activée. Vérifiez les ID dans 'rule_registry.py' et 'iaGOD.json'."
            )

        return initialized_rules

    def run_audit(self, target_path: Path) -> AuditContext:
        """Exécute l'audit complet sur le répertoire cible."""
        context = AuditContext(target_path=target_path, constitution=self.constitution)
        self.logger.info(f"🚀 Démarrage de l'audit constitutionnel sur : {target_path}")

        python_files = self._collect_project_files(target_path)
        self.logger.info(
            f"🔍 Audit de {len(python_files)} fichiers Python du projet (après exclusions)."
        )

        if not self.rules:
            self.logger.warning(
                "Aucune règle d'audit n'est active. L'audit ne vérifiera rien."
            )
            return context

        for file_path in python_files:
            self._audit_file(file_path, context)

        self.logger.info(
            f"Audit terminé. {len(context.violations)} violation(s) trouvée(s)."
        )
        return context

    def _collect_project_files(self, target_path: Path) -> List[Path]:
        """Collecte les fichiers Python du projet en excluant les répertoires non pertinents."""
        project_files = []
        for py_file in target_path.rglob("*.py"):
            is_excluded = any(
                excluded in py_file.parts for excluded in self.excluded_dirs
            )
            if not is_excluded:
                project_files.append(py_file)
        return project_files

    def _audit_file(self, file_path: Path, context: AuditContext):
        """Applique toutes les règles initialisées à un seul fichier."""
        self.logger.debug(f"Audit du fichier : {file_path}")
        for rule in self.rules:
            try:
                rule.apply(file_path, context)
            except Exception as e:
                self.logger.error(
                    f"Erreur en appliquant la règle '{rule.law.id}' sur {file_path}: {e}"
                )