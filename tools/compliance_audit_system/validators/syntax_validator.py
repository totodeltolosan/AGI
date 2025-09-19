#!/usr/bin/env python3
"""
Validateur de Syntaxe - Système d'Audit AGI
Responsabilité unique : Validation de la syntaxe Python et qualité du code
Respecte strictement la directive des 200 lignes
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional
from dataclasses import dataclass


class SyntaxError(NamedTuple):
    """Représente une erreur de syntaxe"""

    file_path: str
    line_number: int
    error_message: str
    error_type: str


class CodeQualityIssue(NamedTuple):
    """Représente un problème de qualité de code"""

    file_path: str
    issue_type: str
    description: str
    severity: str
    line_number: Optional[int] = None


@dataclass
class SyntaxValidationResult:
    """Résultat de validation syntaxique"""

    total_files: int
    valid_files: int
    syntax_errors: List[SyntaxError]
    quality_issues: List[CodeQualityIssue]
    validation_rate: float


class SyntaxValidator:
    """Validateur de syntaxe Python et qualité de code"""

    def __init__(self):
        self.python_version = sys.version_info[:2]

    def validate_file(self, file_path: Path) -> Dict:
        """Valide la syntaxe d'un fichier Python spécifique"""
        result = {
            "valid": False,
            "syntax_errors": [],
            "quality_issues": [],
            "ast_tree": None,
        }

        try:
            # Lecture du fichier
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Tentative de parsing AST
            try:
                tree = ast.parse(content, filename=str(file_path))
                result["ast_tree"] = tree
                result["valid"] = True

                # Analyse de qualité sur l'AST valide
                quality_issues = self._analyze_code_quality(tree, file_path)
                result["quality_issues"] = quality_issues

            except SyntaxError as e:
                syntax_error = SyntaxError(
                    file_path=str(file_path),
                    line_number=e.lineno or 0,
                    error_message=str(e.msg),
                    error_type="SyntaxError",
                )
                result["syntax_errors"].append(syntax_error)

        except Exception as e:
            # Erreur de lecture de fichier
            syntax_error = SyntaxError(
                file_path=str(file_path),
                line_number=0,
                error_message=f"Erreur de lecture: {str(e)}",
                error_type="FileError",
            )
            result["syntax_errors"].append(syntax_error)

        return result

    def validate_directory(self, target_dir: Path) -> SyntaxValidationResult:
        """Valide tous les fichiers Python d'un répertoire"""
        all_syntax_errors = []
        all_quality_issues = []
        total_files = 0
        valid_files = 0

        # Recherche récursive des fichiers Python
        python_files = list(target_dir.rglob("*.py"))
        total_files = len(python_files)

        for py_file in python_files:
            file_result = self.validate_file(py_file)

            if file_result["valid"]:
                valid_files += 1
                all_quality_issues.extend(file_result["quality_issues"])
            else:
                all_syntax_errors.extend(file_result["syntax_errors"])

        # Calcul du taux de validation
        validation_rate = (valid_files / total_files * 100) if total_files > 0 else 100

        return SyntaxValidationResult(
            total_files=total_files,
            valid_files=valid_files,
            syntax_errors=all_syntax_errors,
            quality_issues=all_quality_issues,
            validation_rate=validation_rate,
        )

    def _analyze_code_quality(
        self, tree: ast.AST, file_path: Path
    ) -> List[CodeQualityIssue]:
        """Analyse la qualité du code via l'AST"""
        issues = []

        # Analyse des fonctions
        issues.extend(self._analyze_functions(tree, file_path))

        # Analyse des classes
        issues.extend(self._analyze_classes(tree, file_path))

        # Analyse des imports
        issues.extend(self._analyze_imports(tree, file_path))

        # Analyse de la complexité
        issues.extend(self._analyze_complexity(tree, file_path))

        return issues

    def _analyze_functions(
        self, tree: ast.AST, file_path: Path
    ) -> List[CodeQualityIssue]:
        """Analyse les fonctions pour détecter les problèmes"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Fonction sans docstring
                if not ast.get_docstring(node):
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            issue_type="missing_docstring",
                            description=f"Fonction '{node.name}' sans docstring",
                            severity="MINOR",
                            line_number=node.lineno,
                        )
                    )

                # Fonction avec trop de paramètres
                arg_count = len(node.args.args)
                if arg_count > 7:  # Plus de 7 paramètres
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            issue_type="too_many_parameters",
                            description=f"Fonction '{node.name}' a {arg_count} paramètres (>7)",
                            severity="MODERATE",
                            line_number=node.lineno,
                        )
                    )

                # Fonction potentiellement trop longue (heuristique)
                if hasattr(node, "end_lineno") and node.end_lineno:
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:  # Plus de 50 lignes
                        issues.append(
                            CodeQualityIssue(
                                file_path=str(file_path),
                                issue_type="long_function",
                                description=f"Fonction '{node.name}' longue ({func_length} lignes)",
                                severity="MAJOR",
                                line_number=node.lineno,
                            )
                        )

        return issues

    def _analyze_classes(
        self, tree: ast.AST, file_path: Path
    ) -> List[CodeQualityIssue]:
        """Analyse les classes pour détecter les problèmes"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Classe sans docstring
                if not ast.get_docstring(node):
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            issue_type="missing_class_docstring",
                            description=f"Classe '{node.name}' sans docstring",
                            severity="MINOR",
                            line_number=node.lineno,
                        )
                    )

                # Classe avec trop de méthodes
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 15:  # Plus de 15 méthodes
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            issue_type="too_many_methods",
                            description=f"Classe '{node.name}' a {len(methods)} méthodes (>15)",
                            severity="MAJOR",
                            line_number=node.lineno,
                        )
                    )

        return issues

    def _analyze_imports(
        self, tree: ast.AST, file_path: Path
    ) -> List[CodeQualityIssue]:
        """Analyse les imports pour détecter les problèmes"""
        issues = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)

        # Trop d'imports (signe de couplage fort)
        if len(imports) > 20:
            issues.append(
                CodeQualityIssue(
                    file_path=str(file_path),
                    issue_type="too_many_imports",
                    description=f"Trop d'imports ({len(imports)}) - couplage possible",
                    severity="MODERATE",
                    line_number=1,
                )
            )

        return issues

    def _analyze_complexity(
        self, tree: ast.AST, file_path: Path
    ) -> List[CodeQualityIssue]:
        """Analyse la complexité du code"""
        issues = []

        # Comptage des niveaux d'imbrication
        max_nesting = self._calculate_max_nesting(tree)
        if max_nesting > 4:  # Plus de 4 niveaux d'imbrication
            issues.append(
                CodeQualityIssue(
                    file_path=str(file_path),
                    issue_type="high_nesting",
                    description=f"Imbrication élevée ({max_nesting} niveaux)",
                    severity="MAJOR",
                    line_number=1,
                )
            )

        return issues

    def _calculate_max_nesting(self, tree: ast.AST) -> int:
        """Calcule le niveau maximum d'imbrication"""
        max_depth = 0

        def calculate_depth(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)

            # Nœuds qui augmentent la profondeur
            nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try)

            for child in ast.iter_child_nodes(node):
                if isinstance(child, nesting_nodes):
                    calculate_depth(child, current_depth + 1)
                else:
                    calculate_depth(child, current_depth)

        calculate_depth(tree)
        return max_depth

    def generate_syntax_report(self, result: SyntaxValidationResult) -> str:
        """Génère un rapport textuel de validation syntaxique"""
        lines = []
        lines.append("🐍 RAPPORT DE VALIDATION SYNTAXIQUE")
        lines.append("=" * 40)

        # Statistiques globales
        lines.append(f"Total fichiers analysés: {result.total_files}")
        lines.append(f"Fichiers syntaxiquement valides: {result.valid_files}")
        lines.append(f"Erreurs de syntaxe: {len(result.syntax_errors)}")
        lines.append(f"Problèmes de qualité: {len(result.quality_issues)}")
        lines.append(f"Taux de validation: {result.validation_rate:.1f}%")

        # Erreurs de syntaxe
        if result.syntax_errors:
            lines.append("\n❌ ERREURS DE SYNTAXE:")
            for error in result.syntax_errors:
                filename = Path(error.file_path).name
                lines.append(
                    f"  {filename}:{error.line_number} - {error.error_message}"
                )

        # Problèmes de qualité
        if result.quality_issues:
            lines.append("\n⚠️ PROBLÈMES DE QUALITÉ:")

            # Groupement par sévérité
            by_severity = {}
            for issue in result.quality_issues:
                severity = issue.severity
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(issue)

            for severity in ["MAJOR", "MODERATE", "MINOR"]:
                if severity in by_severity:
                    lines.append(f"\n  {severity} ({len(by_severity[severity])}):")
                    for issue in by_severity[severity][:5]:  # Max 5 par catégorie
                        filename = Path(issue.file_path).name
                        lines.append(f"    {filename} - {issue.description}")

        # Verdict global
        if not result.syntax_errors and len(result.quality_issues) <= 5:
            lines.append("\n✅ CODE DE BONNE QUALITÉ SYNTAXIQUE")
        elif not result.syntax_errors:
            lines.append("\n⚠️ SYNTAXE VALIDE MAIS AMÉLIORATIONS POSSIBLES")
        else:
            lines.append("\n❌ CORRECTIONS SYNTAXIQUES REQUISES")

        return "\n".join(lines)


def quick_syntax_check(file_path: Path) -> bool:
    """Vérification syntaxique rapide - fonction utilitaire"""
    validator = SyntaxValidator()
    result = validator.validate_file(file_path)
    return result["valid"]


def get_syntax_summary(target_dir: Path) -> Dict:
    """Résumé rapide de la syntaxe - fonction utilitaire"""
    validator = SyntaxValidator()
    result = validator.validate_directory(target_dir)

    return {
        "all_valid": len(result.syntax_errors) == 0,
        "error_count": len(result.syntax_errors),
        "quality_issues": len(result.quality_issues),
        "validation_rate": result.validation_rate,
    }


if __name__ == "__main__":
    # Test du validateur de syntaxe
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("🐍 Test du validateur de syntaxe AGI")
    print("=" * 40)

    validator = SyntaxValidator()
    result = validator.validate_directory(target)

    print(validator.generate_syntax_report(result))
