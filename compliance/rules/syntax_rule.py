#!/usr/bin/env python3
"""
Syntax and Structure Rule - Règle d'Analyse Statique Avancée (AST)
====================================================================

CHEMIN: compliance/rules/syntax_rule.py

Rôle Fondamental (Conforme iaGOD.json) :
- Analyser la structure du code via l'Arbre Syntaxique Abstrait (AST).
- Vérifier plusieurs lois constitutionnelles en une seule passe :
  - Complexité du code (simplicité).
  - Présence de documentation (traçabilité).
  - Utilisation de patterns dangereux (sécurité).
- Respecter la directive < 200 lignes.
"""

import ast
import logging
from pathlib import Path

# Import des contrats et de l'interface de base
from compliance.models import AuditContext, Violation
from .base_rule import BaseRule


class SyntaxRule(BaseRule):
    """
    Implémente des vérifications structurelles en parcourant l'AST du fichier.
    """

    def apply(self, file_path: Path, context: AuditContext):
        """
        Analyse le fichier source Python pour y trouver des violations structurelles.
        """
        try:
            source_code = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source_code, filename=str(file_path))

            # Lancer les différentes vérifications basées sur l'AST
            self._check_function_complexity_and_docs(tree, file_path, context)
            self._check_dangerous_imports(tree, file_path, context)

        except SyntaxError as e:
            # Gérer les erreurs de syntaxe qui empêchent l'analyse AST
            violation = Violation(
                law=self.law,  # La loi associée sera celle de la sécurité/fiabilité
                file_path=file_path,
                line_number=e.lineno or 1,
                severity="CRITICAL",
                message=f"Erreur de syntaxe Python : {e.msg}",
                suggestion="Corriger la syntaxe avant de pouvoir réaliser un audit structurel.",
            )
            context.add_violation(violation)
        except Exception as e:
            logging.getLogger(__name__).error(
                f"Erreur lors de l'analyse AST de {file_path}: {e}"
            )

    def _check_function_complexity_and_docs(
        self, tree: ast.AST, file_path: Path, context: AuditContext
    ):
        """Parcourt l'AST pour vérifier la complexité et les docstrings des fonctions."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Vérification de la documentation (loi sur la traçabilité)
                if not ast.get_docstring(node):
                    violation = Violation(
                        law=self.law,
                        file_path=file_path,
                        line_number=node.lineno,
                        severity="LOW",
                        message=f"Documentation (docstring) manquante pour '{node.name}'.",
                        suggestion="Ajouter une docstring expliquant le rôle de la fonction/classe.",
                    )
                    context.add_violation(violation)

                # Calcul simple de la complexité (nombre de points de décision)
                complexity = 0
                for sub_node in ast.walk(node):
                    if isinstance(
                        sub_node,
                        (
                            ast.If,
                            ast.For,
                            ast.While,
                            ast.With,
                            ast.AsyncFor,
                            ast.AsyncWith,
                            ast.ExceptHandler,
                            ast.And,
                            ast.Or,
                        ),
                    ):
                        complexity += 1

                # Loi sur la simplicité
                if complexity > 10:  # Seuil de complexité élevé
                    violation = Violation(
                        law=self.law,
                        file_path=file_path,
                        line_number=node.lineno,
                        severity="MEDIUM",
                        message=f"Complexité élevée ({complexity}) détectée dans '{node.name}'.",
                        suggestion="Refactoriser la fonction/méthode en plus petites unités.",
                    )
                    context.add_violation(violation)

    def _check_dangerous_imports(
        self, tree: ast.AST, file_path: Path, context: AuditContext
    ):
        """Vérifie l'utilisation d'imports potentiellement dangereux."""
        dangerous_imports = {"os", "subprocess"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in dangerous_imports:
                        violation = Violation(
                            law=self.law,
                            file_path=file_path,
                            line_number=node.lineno,
                            severity="MEDIUM",
                            message=f"Import potentiellement dangereux détecté : '{alias.name}'.",
                            suggestion="Assurez-vous que l'utilisation de ce module est absolument nécessaire et sécurisée.",
                        )
                        context.add_violation(violation)
