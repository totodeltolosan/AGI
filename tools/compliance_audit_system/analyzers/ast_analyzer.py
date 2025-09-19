#!/usr/bin/env python3
"""
Analyseur AST - Système d'Audit AGI
Responsabilité unique : Analyse approfondie de l'arbre syntaxique abstrait
Respecte strictement la directive des 200 lignes
"""

import ast
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional
from dataclasses import dataclass
from collections import defaultdict


class ASTMetric(NamedTuple):
    """Métrique extraite de l'AST"""

    file_path: str
    metric_name: str
    value: int
    threshold: Optional[int] = None
    compliant: Optional[bool] = None


class CodeComplexity(NamedTuple):
    """Mesure de complexité du code"""

    file_path: str
    cyclomatic_complexity: int
    cognitive_complexity: int
    nesting_depth: int
    function_count: int
    class_count: int


@dataclass
class ASTAnalysisResult:
    """Résultat d'analyse AST"""

    analyzed_files: int
    total_metrics: List[ASTMetric]
    complexity_metrics: List[CodeComplexity]
    quality_score: float
    architectural_violations: List[str]


class ASTAnalyzer:
    """Analyseur d'arbre syntaxique abstrait pour conformité AGI"""

    def __init__(self):
        self.complexity_thresholds = {
            "cyclomatic_complexity": 10,
            "cognitive_complexity": 15,
            "nesting_depth": 4,
            "function_count_per_file": 15,
            "class_count_per_file": 3,
        }

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyse AST complète d'un fichier"""
        result = {
            "parsed": False,
            "metrics": [],
            "complexity": None,
            "violations": [],
            "ast_tree": None,
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parsing AST
            tree = ast.parse(content, filename=str(file_path))
            result["ast_tree"] = tree
            result["parsed"] = True

            # Extraction des métriques
            result["metrics"] = self._extract_metrics(file_path, tree)

            # Calcul de la complexité
            result["complexity"] = self._calculate_complexity(file_path, tree)

            # Détection des violations architecturales
            result["violations"] = self._detect_architectural_violations(
                file_path, tree
            )

        except SyntaxError:
            # Erreur de syntaxe - pas d'analyse possible
            pass
        except Exception:
            # Autres erreurs - fichier problématique
            result["violations"].append("Erreur lors de l'analyse AST")

        return result

    def analyze_directory(self, target_dir: Path) -> ASTAnalysisResult:
        """Analyse AST d'un répertoire complet"""
        all_metrics = []
        all_complexity = []
        all_violations = []
        analyzed_files = 0

        # Recherche récursive des fichiers Python
        python_files = list(target_dir.rglob("*.py"))

        for py_file in python_files:
            file_result = self.analyze_file(py_file)

            if file_result["parsed"]:
                analyzed_files += 1
                all_metrics.extend(file_result["metrics"])

                if file_result["complexity"]:
                    all_complexity.append(file_result["complexity"])

                all_violations.extend(file_result["violations"])

        # Calcul du score de qualité global
        quality_score = self._calculate_quality_score(all_metrics, all_complexity)

        return ASTAnalysisResult(
            analyzed_files=analyzed_files,
            total_metrics=all_metrics,
            complexity_metrics=all_complexity,
            quality_score=quality_score,
            architectural_violations=all_violations,
        )

    def _extract_metrics(self, file_path: Path, tree: ast.AST) -> List[ASTMetric]:
        """Extrait les métriques de base de l'AST"""
        metrics = []

        # Comptage des éléments
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]

        # Métriques de base
        metrics.append(
            ASTMetric(
                str(file_path),
                "function_count",
                len(functions),
                self.complexity_thresholds["function_count_per_file"],
                len(functions) <= self.complexity_thresholds["function_count_per_file"],
            )
        )

        metrics.append(
            ASTMetric(
                str(file_path),
                "class_count",
                len(classes),
                self.complexity_thresholds["class_count_per_file"],
                len(classes) <= self.complexity_thresholds["class_count_per_file"],
            )
        )

        metrics.append(
            ASTMetric(
                str(file_path),
                "import_count",
                len(imports),
                20,  # Seuil d'imports
                len(imports) <= 20,
            )
        )

        # Métriques de qualité de code
        metrics.extend(
            self._extract_quality_metrics(file_path, tree, functions, classes)
        )

        return metrics

    def _extract_quality_metrics(
        self, file_path: Path, tree: ast.AST, functions: List, classes: List
    ) -> List[ASTMetric]:
        """Extrait les métriques de qualité"""
        metrics = []

        # Fonctions avec docstring
        functions_with_docstring = sum(
            1 for func in functions if ast.get_docstring(func)
        )
        docstring_rate = (
            (functions_with_docstring / len(functions) * 100) if functions else 100
        )

        metrics.append(
            ASTMetric(
                str(file_path),
                "docstring_coverage",
                int(docstring_rate),
                70,  # 70% minimum
                docstring_rate >= 70,
            )
        )

        # Classes avec docstring
        classes_with_docstring = sum(1 for cls in classes if ast.get_docstring(cls))
        class_docstring_rate = (
            (classes_with_docstring / len(classes) * 100) if classes else 100
        )

        metrics.append(
            ASTMetric(
                str(file_path),
                "class_docstring_coverage",
                int(class_docstring_rate),
                80,  # 80% minimum pour les classes
                class_docstring_rate >= 80,
            )
        )

        # Fonctions avec type hints
        typed_functions = 0
        for func in functions:
            has_return_hint = func.returns is not None
            has_arg_hints = any(arg.annotation is not None for arg in func.args.args)
            if has_return_hint or has_arg_hints:
                typed_functions += 1

        type_hint_rate = (typed_functions / len(functions) * 100) if functions else 100

        metrics.append(
            ASTMetric(
                str(file_path),
                "type_hint_coverage",
                int(type_hint_rate),
                50,  # 50% minimum
                type_hint_rate >= 50,
            )
        )

        return metrics

    def _calculate_complexity(self, file_path: Path, tree: ast.AST) -> CodeComplexity:
        """Calcule les métriques de complexité"""

        # Complexité cyclomatique simplifiée
        cyclomatic = self._calculate_cyclomatic_complexity(tree)

        # Complexité cognitive (approximation)
        cognitive = self._calculate_cognitive_complexity(tree)

        # Profondeur d'imbrication
        nesting_depth = self._calculate_nesting_depth(tree)

        # Comptages
        functions = len(
            [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        )
        classes = len(
            [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        )

        return CodeComplexity(
            file_path=str(file_path),
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            nesting_depth=nesting_depth,
            function_count=functions,
            class_count=classes,
        )

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calcule la complexité cyclomatique (approximation)"""
        complexity = 1  # Base

        # Nœuds qui ajoutent de la complexité
        complexity_nodes = (
            ast.If,
            ast.While,
            ast.For,
            ast.Try,
            ast.With,
            ast.ExceptHandler,
            ast.And,
            ast.Or,
        )

        for node in ast.walk(tree):
            if isinstance(node, complexity_nodes):
                complexity += 1

        return complexity

    def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """Calcule la complexité cognitive (approximation)"""
        cognitive = 0
        nesting_level = 0

        def calculate_recursive(node, level=0):
            nonlocal cognitive

            # Structures qui augmentent la complexité cognitive
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                cognitive += 1 + level  # +1 base + niveau d'imbrication
                level += 1
            elif isinstance(node, (ast.And, ast.Or)):
                cognitive += 1

            # Parcours récursif
            for child in ast.iter_child_nodes(node):
                calculate_recursive(child, level)

        calculate_recursive(tree)
        return cognitive

    def _calculate_nesting_depth(self, tree: ast.AST) -> int:
        """Calcule la profondeur d'imbrication maximale"""
        max_depth = 0

        def calculate_depth(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)

            # Nœuds qui augmentent la profondeur
            nesting_nodes = (
                ast.If,
                ast.For,
                ast.While,
                ast.With,
                ast.Try,
                ast.FunctionDef,
                ast.ClassDef,
            )

            for child in ast.iter_child_nodes(node):
                if isinstance(child, nesting_nodes):
                    calculate_depth(child, current_depth + 1)
                else:
                    calculate_depth(child, current_depth)

        calculate_depth(tree)
        return max_depth

    def _detect_architectural_violations(
        self, file_path: Path, tree: ast.AST
    ) -> List[str]:
        """Détecte les violations architecturales"""
        violations = []

        # Fonctions trop longues (heuristique basée sur l'AST)
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        for func in functions:
            if hasattr(func, "end_lineno") and func.end_lineno:
                func_length = func.end_lineno - func.lineno
                if func_length > 50:  # Plus de 50 lignes
                    violations.append(
                        f"Fonction '{func.name}' trop longue ({func_length} lignes)"
                    )

        # Classes avec trop de méthodes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        for cls in classes:
            methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
            if len(methods) > 15:
                violations.append(
                    f"Classe '{cls.name}' avec trop de méthodes ({len(methods)})"
                )

        # Trop d'imports (couplage fort)
        imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        if len(imports) > 20:
            violations.append(
                f"Trop d'imports ({len(imports)}) - couplage fort possible"
            )

        return violations

    def _calculate_quality_score(
        self, metrics: List[ASTMetric], complexity_metrics: List[CodeComplexity]
    ) -> float:
        """Calcule un score de qualité global"""
        if not metrics:
            return 100.0

        # Score basé sur la conformité des métriques
        compliant_metrics = [m for m in metrics if m.compliant is True]
        total_metrics = [m for m in metrics if m.compliant is not None]

        metric_score = (
            (len(compliant_metrics) / len(total_metrics) * 100)
            if total_metrics
            else 100
        )

        # Pénalités pour complexité excessive
        complexity_penalty = 0
        for complexity in complexity_metrics:
            if (
                complexity.cyclomatic_complexity
                > self.complexity_thresholds["cyclomatic_complexity"]
            ):
                complexity_penalty += 5
            if (
                complexity.cognitive_complexity
                > self.complexity_thresholds["cognitive_complexity"]
            ):
                complexity_penalty += 5
            if complexity.nesting_depth > self.complexity_thresholds["nesting_depth"]:
                complexity_penalty += 10

        # Score final
        final_score = max(0, metric_score - complexity_penalty)
        return round(final_score, 1)


def quick_ast_analysis(file_path: Path) -> bool:
    """Analyse AST rapide - fonction utilitaire"""
    analyzer = ASTAnalyzer()
    result = analyzer.analyze_file(file_path)
    return result["parsed"] and len(result["violations"]) == 0


def get_complexity_summary(target_dir: Path) -> Dict:
    """Résumé de complexité - fonction utilitaire"""
    analyzer = ASTAnalyzer()
    result = analyzer.analyze_directory(target_dir)

    avg_cyclomatic = 0
    avg_cognitive = 0
    max_nesting = 0

    if result.complexity_metrics:
        avg_cyclomatic = sum(
            c.cyclomatic_complexity for c in result.complexity_metrics
        ) / len(result.complexity_metrics)
        avg_cognitive = sum(
            c.cognitive_complexity for c in result.complexity_metrics
        ) / len(result.complexity_metrics)
        max_nesting = max(c.nesting_depth for c in result.complexity_metrics)

    return {
        "quality_score": result.quality_score,
        "avg_cyclomatic_complexity": round(avg_cyclomatic, 1),
        "avg_cognitive_complexity": round(avg_cognitive, 1),
        "max_nesting_depth": max_nesting,
        "architectural_violations": len(result.architectural_violations),
    }


if __name__ == "__main__":
    # Test de l'analyseur AST
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("🌳 Test de l'analyseur AST AGI")
    print("=" * 40)

    analyzer = ASTAnalyzer()
    result = analyzer.analyze_directory(target)

    print(f"Fichiers analysés: {result.analyzed_files}")
    print(f"Métriques extraites: {len(result.total_metrics)}")
    print(f"Score de qualité: {result.quality_score}/100")
    print(f"Violations architecturales: {len(result.architectural_violations)}")
