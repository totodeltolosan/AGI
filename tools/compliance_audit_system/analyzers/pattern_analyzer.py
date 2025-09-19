#!/usr/bin/env python3
"""
Analyseur de Patterns - Système d'Audit AGI
Responsabilité unique : Détection des patterns architecturaux et anti-patterns
Respecte strictement la directive des 200 lignes
"""

import re
from pathlib import Path
from typing import Dict, List, NamedTuple, Set
from dataclasses import dataclass
from collections import Counter


class DesignPattern(NamedTuple):
    """Pattern de conception détecté"""

    file_path: str
    pattern_name: str
    pattern_type: str  # 'good_pattern' ou 'anti_pattern'
    confidence: float
    description: str
    line_number: int


class ArchitecturalMetric(NamedTuple):
    """Métrique architecturale"""

    metric_name: str
    value: float
    threshold: float
    compliant: bool
    description: str


@dataclass
class PatternAnalysisResult:
    """Résultat d'analyse des patterns"""

    analyzed_files: int
    good_patterns: List[DesignPattern]
    anti_patterns: List[DesignPattern]
    architectural_metrics: List[ArchitecturalMetric]
    modularity_score: float
    design_quality_score: float


class PatternAnalyzer:
    """Analyseur de patterns architecturaux pour conformité AGI"""

    def __init__(self):
        self.good_patterns = {
            # Patterns de responsabilité unique
            "single_responsibility": [
                (r"class\s+\w+Validator\s*:", "Validator pattern", 0.8),
                (r"class\s+\w+Factory\s*:", "Factory pattern", 0.7),
                (r"class\s+\w+Builder\s*:", "Builder pattern", 0.7),
                (r"class\s+\w+Observer\s*:", "Observer pattern", 0.6),
                (r"class\s+\w+Strategy\s*:", "Strategy pattern", 0.7),
            ],
            # Patterns de configuration
            "configuration": [
                (r"@dataclass", "Dataclass pour configuration", 0.8),
                (r"NamedTuple", "NamedTuple pour structure", 0.7),
                (r"class\s+\w+Config\s*:", "Configuration class", 0.8),
            ],
            # Patterns d'extensibilité
            "extensibility": [
                (r"@abstractmethod", "Abstract method pour extension", 0.9),
                (r"Protocol", "Protocol pour interfaces", 0.8),
                (r"raise\s+NotImplementedError", "Extension point", 0.6),
            ],
            # Patterns de sécurité
            "security": [
                (r"from pathlib import Path", "Pathlib pour sécurité", 0.7),
                (r"validate|sanitize", "Validation input", 0.8),
                (r"try:\s*.*\s*except\s+\w+Error:", "Gestion d'erreur spécifique", 0.6),
            ],
        }

        self.anti_patterns = {
            # Anti-patterns de responsabilité
            "responsibility_violation": [
                (
                    r"class\s+\w*(Manager|Handler|Controller|Service)\s*:",
                    "God class potential",
                    0.6,
                ),
                (r"def\s+\w*(process|handle|manage)_everything", "God method", 0.8),
            ],
            # Anti-patterns de couplage
            "tight_coupling": [
                (r"import\s+.*\..*\..*\.", "Deep import hierarchy", 0.5),
                (r"global\s+\w+", "Global variable", 0.7),
                (r"from\s+\w+\s+import\s+\*", "Wildcard import", 0.8),
            ],
            # Anti-patterns de sécurité
            "security_anti_patterns": [
                (r"eval\s*\(", "Eval usage", 0.9),
                (r"exec\s*\(", "Exec usage", 0.9),
                (r"os\.system", "System call", 0.8),
                (r"subprocess\.shell=True", "Shell injection risk", 0.7),
            ],
        }

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyse les patterns d'un fichier"""
        result = {
            "good_patterns": [],
            "anti_patterns": [],
            "modularity_indicators": {},
            "file_metrics": {},
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Détection des patterns positifs
            result["good_patterns"] = self._detect_good_patterns(
                file_path, content, lines
            )

            # Détection des anti-patterns
            result["anti_patterns"] = self._detect_anti_patterns(
                file_path, content, lines
            )

            # Analyse de la modularité
            result["modularity_indicators"] = self._analyze_modularity(content)

            # Métriques du fichier
            result["file_metrics"] = self._calculate_file_metrics(content, lines)

        except Exception:
            # Erreur de lecture - fichier problématique
            pass

        return result

    def analyze_directory(self, target_dir: Path) -> PatternAnalysisResult:
        """Analyse les patterns d'un répertoire"""
        all_good_patterns = []
        all_anti_patterns = []
        analyzed_files = 0

        # Collecte des métriques par fichier
        file_metrics = []
        modularity_indicators = []

        # Recherche récursive des fichiers Python
        python_files = list(target_dir.rglob("*.py"))

        for py_file in python_files:
            file_result = self.analyze_file(py_file)
            analyzed_files += 1

            all_good_patterns.extend(file_result["good_patterns"])
            all_anti_patterns.extend(file_result["anti_patterns"])

            if file_result["file_metrics"]:
                file_metrics.append(file_result["file_metrics"])

            if file_result["modularity_indicators"]:
                modularity_indicators.append(file_result["modularity_indicators"])

        # Calcul des métriques architecturales globales
        architectural_metrics = self._calculate_architectural_metrics(
            file_metrics, modularity_indicators, target_dir
        )

        # Calcul des scores de qualité
        modularity_score = self._calculate_modularity_score(modularity_indicators)
        design_quality_score = self._calculate_design_quality_score(
            all_good_patterns, all_anti_patterns, analyzed_files
        )

        return PatternAnalysisResult(
            analyzed_files=analyzed_files,
            good_patterns=all_good_patterns,
            anti_patterns=all_anti_patterns,
            architectural_metrics=architectural_metrics,
            modularity_score=modularity_score,
            design_quality_score=design_quality_score,
        )

    def _detect_good_patterns(
        self, file_path: Path, content: str, lines: List[str]
    ) -> List[DesignPattern]:
        """Détecte les patterns positifs"""
        patterns = []

        for category, pattern_list in self.good_patterns.items():
            for pattern, description, confidence in pattern_list:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        patterns.append(
                            DesignPattern(
                                file_path=str(file_path),
                                pattern_name=category,
                                pattern_type="good_pattern",
                                confidence=confidence,
                                description=description,
                                line_number=line_num,
                            )
                        )

        return patterns

    def _detect_anti_patterns(
        self, file_path: Path, content: str, lines: List[str]
    ) -> List[DesignPattern]:
        """Détecte les anti-patterns"""
        patterns = []

        for category, pattern_list in self.anti_patterns.items():
            for pattern, description, confidence in pattern_list:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        patterns.append(
                            DesignPattern(
                                file_path=str(file_path),
                                pattern_name=category,
                                pattern_type="anti_pattern",
                                confidence=confidence,
                                description=description,
                                line_number=line_num,
                            )
                        )

        return patterns

    def _analyze_modularity(self, content: str) -> Dict:
        """Analyse les indicateurs de modularité"""
        indicators = {}

        # Comptage des imports
        import_count = len(re.findall(r"^(import|from)\s+", content, re.MULTILINE))
        indicators["import_count"] = import_count

        # Ratio classes/fonctions
        class_count = len(re.findall(r"^class\s+\w+", content, re.MULTILINE))
        function_count = len(re.findall(r"^def\s+\w+", content, re.MULTILINE))
        indicators["class_count"] = class_count
        indicators["function_count"] = function_count

        # Indicateurs de responsabilité unique
        if class_count > 0:
            methods_per_class = function_count / class_count
            indicators["methods_per_class"] = methods_per_class

        # Présence de docstrings
        docstring_count = len(re.findall(r'"""[\s\S]*?"""', content))
        indicators["docstring_count"] = docstring_count

        # Type hints (approximation)
        type_hint_count = len(re.findall(r":\s*\w+", content))
        indicators["type_hint_count"] = type_hint_count

        return indicators

    def _calculate_file_metrics(self, content: str, lines: List[str]) -> Dict:
        """Calcule les métriques de fichier"""
        metrics = {}

        # Métriques de base
        metrics["line_count"] = len(lines)
        metrics["non_empty_lines"] = len([line for line in lines if line.strip()])
        metrics["comment_lines"] = len(
            [line for line in lines if line.strip().startswith("#")]
        )

        # Ratio de commentaires
        if metrics["non_empty_lines"] > 0:
            metrics["comment_ratio"] = (
                metrics["comment_lines"] / metrics["non_empty_lines"]
            )

        # Complexité lexicale (approximation)
        unique_tokens = len(set(re.findall(r"\w+", content.lower())))
        total_tokens = len(re.findall(r"\w+", content))
        metrics["lexical_diversity"] = (
            unique_tokens / total_tokens if total_tokens > 0 else 0
        )

        return metrics

    def _calculate_architectural_metrics(
        self,
        file_metrics: List[Dict],
        modularity_indicators: List[Dict],
        target_dir: Path,
    ) -> List[ArchitecturalMetric]:
        """Calcule les métriques architecturales globales"""
        metrics = []

        if not file_metrics:
            return metrics

        # Métrique de cohésion
        avg_imports = sum(
            m.get("import_count", 0) for m in modularity_indicators
        ) / len(modularity_indicators)
        cohesion_metric = ArchitecturalMetric(
            metric_name="module_cohesion",
            value=min(20, avg_imports),  # Normalisé sur 20
            threshold=15.0,
            compliant=avg_imports <= 15,
            description="Cohésion des modules (imports moyens)",
        )
        metrics.append(cohesion_metric)

        # Métrique de responsabilité unique
        avg_functions_per_file = sum(
            f.get("function_count", 0) for f in file_metrics
        ) / len(file_metrics)
        responsibility_metric = ArchitecturalMetric(
            metric_name="single_responsibility",
            value=avg_functions_per_file,
            threshold=15.0,
            compliant=avg_functions_per_file <= 15,
            description="Responsabilité unique (fonctions par fichier)",
        )
        metrics.append(responsibility_metric)

        # Métrique de documentation
        total_docstrings = sum(
            m.get("docstring_count", 0) for m in modularity_indicators
        )
        total_functions = sum(m.get("function_count", 0) for m in modularity_indicators)
        doc_ratio = (
            (total_docstrings / total_functions * 100) if total_functions > 0 else 100
        )

        documentation_metric = ArchitecturalMetric(
            metric_name="documentation_coverage",
            value=doc_ratio,
            threshold=50.0,
            compliant=doc_ratio >= 50,
            description="Couverture documentation (%)",
        )
        metrics.append(documentation_metric)

        return metrics

    def _calculate_modularity_score(self, modularity_indicators: List[Dict]) -> float:
        """Calcule un score de modularité"""
        if not modularity_indicators:
            return 100.0

        score = 100.0

        # Pénalités pour mauvaise modularité
        for indicators in modularity_indicators:
            # Trop d'imports = couplage fort
            imports = indicators.get("import_count", 0)
            if imports > 20:
                score -= min(20, (imports - 20) * 2)

            # Trop de fonctions = responsabilité multiple
            functions = indicators.get("function_count", 0)
            if functions > 15:
                score -= min(15, (functions - 15) * 1.5)

            # Ratio méthodes/classes déséquilibré
            methods_per_class = indicators.get("methods_per_class", 0)
            if methods_per_class > 10:  # Classes trop grosses
                score -= min(10, (methods_per_class - 10) * 1)

        return max(0, round(score, 1))

    def _calculate_design_quality_score(
        self,
        good_patterns: List[DesignPattern],
        anti_patterns: List[DesignPattern],
        total_files: int,
    ) -> float:
        """Calcule un score de qualité de design"""
        if total_files == 0:
            return 100.0

        # Points pour les bons patterns
        good_score = sum(pattern.confidence for pattern in good_patterns)

        # Pénalités pour les anti-patterns
        anti_penalty = sum(pattern.confidence * 10 for pattern in anti_patterns)

        # Normalisation par nombre de fichiers
        normalized_good = good_score / total_files
        normalized_penalty = anti_penalty / total_files

        # Score final (0-100)
        raw_score = normalized_good * 10 - normalized_penalty
        final_score = max(0, min(100, raw_score))

        return round(final_score, 1)


def quick_pattern_check(file_path: Path) -> Dict:
    """Vérification rapide des patterns - fonction utilitaire"""
    analyzer = PatternAnalyzer()
    result = analyzer.analyze_file(file_path)

    good_count = len(result["good_patterns"])
    anti_count = len(result["anti_patterns"])

    return {
        "has_good_patterns": good_count > 0,
        "has_anti_patterns": anti_count > 0,
        "pattern_balance": good_count - anti_count,
    }


def get_design_summary(target_dir: Path) -> Dict:
    """Résumé de design - fonction utilitaire"""
    analyzer = PatternAnalyzer()
    result = analyzer.analyze_directory(target_dir)

    return {
        "modularity_score": result.modularity_score,
        "design_quality_score": result.design_quality_score,
        "good_patterns_count": len(result.good_patterns),
        "anti_patterns_count": len(result.anti_patterns),
        "files_analyzed": result.analyzed_files,
    }


if __name__ == "__main__":
    # Test de l'analyseur de patterns
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("🎨 Test de l'analyseur de patterns AGI")
    print("=" * 40)

    analyzer = PatternAnalyzer()
    result = analyzer.analyze_directory(target)

    print(f"Fichiers analysés: {result.analyzed_files}")
    print(f"Bons patterns: {len(result.good_patterns)}")
    print(f"Anti-patterns: {len(result.anti_patterns)}")
    print(f"Score modularité: {result.modularity_score}/100")
    print(f"Score qualité design: {result.design_quality_score}/100")
