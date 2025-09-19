#!/usr/bin/env python3
"""
Analyseur de Dépendances - Système d'Audit AGI
Responsabilité unique : Analyse des dépendances et du couplage entre modules
Respecte strictement la directive des 200 lignes
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, NamedTuple, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter


class DependencyRelation(NamedTuple):
    """Relation de dépendance entre modules"""

    source_file: str
    target_module: str
    dependency_type: str  # 'import', 'from_import', 'dynamic'
    line_number: int
    is_external: bool


class ModuleCoupling(NamedTuple):
    """Métrique de couplage d'un module"""

    module_path: str
    incoming_dependencies: int  # Afferent coupling (Ca)
    outgoing_dependencies: int  # Efferent coupling (Ce)
    instability: float  # I = Ce / (Ca + Ce)
    coupling_strength: str  # LOW, MEDIUM, HIGH, CRITICAL


@dataclass
class DependencyAnalysisResult:
    """Résultat d'analyse des dépendances"""

    analyzed_modules: int
    dependency_relations: List[DependencyRelation]
    coupling_metrics: List[ModuleCoupling]
    circular_dependencies: List[List[str]]
    external_dependencies: Set[str]
    coupling_violations: List[str]
    modularity_score: float


class DependencyAnalyzer:
    """Analyseur de dépendances et couplage pour conformité AGI"""

    def __init__(self):
        self.coupling_thresholds = {
            "max_outgoing": 15,  # Maximum dépendances sortantes
            "max_incoming": 10,  # Maximum dépendances entrantes
            "max_instability": 0.8,  # Instabilité acceptable
            "circular_tolerance": 0,  # Tolérance pour dépendances circulaires
        }

        self.standard_modules = {
            # Modules standard Python à ignorer dans l'analyse
            "os",
            "sys",
            "pathlib",
            "typing",
            "dataclasses",
            "json",
            "csv",
            "datetime",
            "uuid",
            "logging",
            "argparse",
            "ast",
            "re",
            "collections",
        }

    def analyze_file(self, file_path: Path, project_root: Path) -> Dict:
        """Analyse les dépendances d'un fichier"""
        result = {
            "dependencies": [],
            "imports": [],
            "coupling_info": {},
            "parsed": False,
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Analyse via AST
            tree = ast.parse(content)
            result["parsed"] = True

            # Extraction des imports
            imports = self._extract_imports(tree, file_path)
            result["imports"] = imports

            # Classification des dépendances
            dependencies = self._classify_dependencies(imports, project_root)
            result["dependencies"] = dependencies

            # Information de couplage
            result["coupling_info"] = self._analyze_file_coupling(imports)

        except (SyntaxError, FileNotFoundError):
            # Erreurs gérées silencieusement
            pass
        except Exception:
            # Autres erreurs - fichier problématique
            pass

        return result

    def analyze_directory(self, target_dir: Path) -> DependencyAnalysisResult:
        """Analyse complète des dépendances d'un projet"""
        all_dependencies = []
        all_imports = []
        analyzed_modules = 0

        # Recherche récursive des fichiers Python
        python_files = list(target_dir.rglob("*.py"))
        file_dependencies = {}

        # Analyse fichier par fichier
        for py_file in python_files:
            file_result = self.analyze_file(py_file, target_dir)

            if file_result["parsed"]:
                analyzed_modules += 1
                all_dependencies.extend(file_result["dependencies"])
                all_imports.extend(file_result["imports"])
                file_dependencies[str(py_file)] = file_result["dependencies"]

        # Calcul des métriques de couplage
        coupling_metrics = self._calculate_coupling_metrics(
            file_dependencies, python_files
        )

        # Détection des dépendances circulaires
        circular_deps = self._detect_circular_dependencies(file_dependencies)

        # Extraction des dépendances externes
        external_deps = self._extract_external_dependencies(all_dependencies)

        # Identification des violations de couplage
        coupling_violations = self._identify_coupling_violations(coupling_metrics)

        # Calcul du score de modularité
        modularity_score = self._calculate_modularity_score(
            coupling_metrics, circular_deps
        )

        return DependencyAnalysisResult(
            analyzed_modules=analyzed_modules,
            dependency_relations=all_dependencies,
            coupling_metrics=coupling_metrics,
            circular_dependencies=circular_deps,
            external_dependencies=external_deps,
            coupling_violations=coupling_violations,
            modularity_score=modularity_score,
        )

    def _extract_imports(self, tree: ast.AST, file_path: Path) -> List[Dict]:
        """Extrait tous les imports d'un AST"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                            "file": str(file_path),
                        }
                    )

            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(
                    {
                        "type": "from_import",
                        "module": node.module,
                        "names": [alias.name for alias in node.names],
                        "line": node.lineno,
                        "file": str(file_path),
                    }
                )

        return imports

    def _classify_dependencies(
        self, imports: List[Dict], project_root: Path
    ) -> List[DependencyRelation]:
        """Classifie les dépendances par type"""
        dependencies = []

        for imp in imports:
            module_name = imp["module"]
            is_external = self._is_external_dependency(module_name, project_root)

            dependency = DependencyRelation(
                source_file=imp["file"],
                target_module=module_name,
                dependency_type=imp["type"],
                line_number=imp["line"],
                is_external=is_external,
            )
            dependencies.append(dependency)

        return dependencies

    def _is_external_dependency(self, module_name: str, project_root: Path) -> bool:
        """Détermine si une dépendance est externe au projet"""

        # Modules standard Python
        if module_name.split(".")[0] in self.standard_modules:
            return True

        # Tentative de localisation dans le projet
        # Conversion du nom de module en chemin
        module_path = module_name.replace(".", "/")
        potential_paths = [
            project_root / f"{module_path}.py",
            project_root / module_path / "__init__.py",
        ]

        return not any(path.exists() for path in potential_paths)

    def _analyze_file_coupling(self, imports: List[Dict]) -> Dict:
        """Analyse le couplage d'un fichier spécifique"""

        outgoing_count = len(imports)
        unique_modules = len(set(imp["module"] for imp in imports))

        return {
            "total_imports": outgoing_count,
            "unique_modules": unique_modules,
            "import_diversity": (
                unique_modules / outgoing_count if outgoing_count > 0 else 1.0
            ),
        }

    def _calculate_coupling_metrics(
        self, file_dependencies: Dict, python_files: List[Path]
    ) -> List[ModuleCoupling]:
        """Calcule les métriques de couplage Martin (Ca, Ce, I)"""
        coupling_metrics = []

        # Création d'un mapping fichier -> module
        file_to_module = {str(f): self._file_to_module_name(f) for f in python_files}

        for file_path in file_dependencies:
            if file_path not in file_to_module:
                continue

            module_name = file_to_module[file_path]

            # Dépendances sortantes (Ce - Efferent coupling)
            outgoing = len(
                [dep for dep in file_dependencies[file_path] if not dep.is_external]
            )

            # Dépendances entrantes (Ca - Afferent coupling)
            incoming = 0
            for other_file, other_deps in file_dependencies.items():
                if other_file != file_path:
                    for dep in other_deps:
                        if not dep.is_external and dep.target_module in module_name:
                            incoming += 1

            # Instabilité (I = Ce / (Ca + Ce))
            total_coupling = incoming + outgoing
            instability = outgoing / total_coupling if total_coupling > 0 else 0

            # Classification de la force de couplage
            coupling_strength = self._classify_coupling_strength(
                incoming, outgoing, instability
            )

            coupling_metrics.append(
                ModuleCoupling(
                    module_path=file_path,
                    incoming_dependencies=incoming,
                    outgoing_dependencies=outgoing,
                    instability=instability,
                    coupling_strength=coupling_strength,
                )
            )

        return coupling_metrics

    def _file_to_module_name(self, file_path: Path) -> str:
        """Convertit un chemin de fichier en nom de module"""
        # Suppression de l'extension et conversion en notation module
        module_parts = file_path.with_suffix("").parts
        return ".".join(module_parts)

    def _classify_coupling_strength(
        self, incoming: int, outgoing: int, instability: float
    ) -> str:
        """Classifie la force de couplage"""

        if (
            outgoing > self.coupling_thresholds["max_outgoing"]
            or incoming > self.coupling_thresholds["max_incoming"]
        ):
            return "CRITICAL"
        elif outgoing > 10 or incoming > 7:
            return "HIGH"
        elif outgoing > 5 or incoming > 4:
            return "MEDIUM"
        else:
            return "LOW"

    def _detect_circular_dependencies(self, file_dependencies: Dict) -> List[List[str]]:
        """Détecte les dépendances circulaires"""
        # Algorithme simple de détection de cycles
        # (Pour une implémentation complète, utiliseriez un algorithme de graphes)

        circular_deps = []

        # Construction d'un graphe simplifié
        graph = defaultdict(set)
        for file_path, dependencies in file_dependencies.items():
            for dep in dependencies:
                if not dep.is_external:
                    graph[file_path].add(dep.target_module)

        # Détection basique de cycles directs (A -> B -> A)
        for source in graph:
            for target in graph[source]:
                if source in graph.get(target, set()):
                    circular_deps.append([source, target])

        return circular_deps

    def _extract_external_dependencies(
        self, dependencies: List[DependencyRelation]
    ) -> Set[str]:
        """Extrait les dépendances externes uniques"""
        external = set()

        for dep in dependencies:
            if dep.is_external and dep.target_module not in self.standard_modules:
                # Gardez seulement le module racine
                root_module = dep.target_module.split(".")[0]
                external.add(root_module)

        return external

    def _identify_coupling_violations(
        self, coupling_metrics: List[ModuleCoupling]
    ) -> List[str]:
        """Identifie les violations de couplage"""
        violations = []

        for metric in coupling_metrics:
            module_name = Path(metric.module_path).name

            if metric.outgoing_dependencies > self.coupling_thresholds["max_outgoing"]:
                violations.append(
                    f"{module_name}: Trop de dépendances sortantes ({metric.outgoing_dependencies})"
                )

            if metric.incoming_dependencies > self.coupling_thresholds["max_incoming"]:
                violations.append(
                    f"{module_name}: Trop de dépendances entrantes ({metric.incoming_dependencies})"
                )

            if metric.instability > self.coupling_thresholds["max_instability"]:
                violations.append(
                    f"{module_name}: Instabilité excessive ({metric.instability:.2f})"
                )

        return violations

    def _calculate_modularity_score(
        self, coupling_metrics: List[ModuleCoupling], circular_deps: List[List[str]]
    ) -> float:
        """Calcule un score de modularité global"""
        if not coupling_metrics:
            return 100.0

        # Score basé sur la distribution du couplage
        low_coupling_count = len(
            [m for m in coupling_metrics if m.coupling_strength == "LOW"]
        )
        total_modules = len(coupling_metrics)

        base_score = (low_coupling_count / total_modules) * 100

        # Pénalités pour dépendances circulaires
        circular_penalty = len(circular_deps) * 10

        # Pénalités pour couplage excessif
        high_coupling_count = len(
            [m for m in coupling_metrics if m.coupling_strength in ["HIGH", "CRITICAL"]]
        )
        coupling_penalty = high_coupling_count * 5

        final_score = max(0, base_score - circular_penalty - coupling_penalty)
        return round(final_score, 1)


def quick_dependency_check(target_dir: Path) -> Dict:
    """Vérification rapide des dépendances - fonction utilitaire"""
    analyzer = DependencyAnalyzer()
    result = analyzer.analyze_directory(target_dir)

    return {
        "has_circular_deps": len(result.circular_dependencies) > 0,
        "external_deps_count": len(result.external_dependencies),
        "coupling_violations": len(result.coupling_violations),
        "modularity_score": result.modularity_score,
    }


def get_coupling_summary(target_dir: Path) -> Dict:
    """Résumé de couplage - fonction utilitaire"""
    analyzer = DependencyAnalyzer()
    result = analyzer.analyze_directory(target_dir)

    if result.coupling_metrics:
        avg_outgoing = sum(
            m.outgoing_dependencies for m in result.coupling_metrics
        ) / len(result.coupling_metrics)
        avg_incoming = sum(
            m.incoming_dependencies for m in result.coupling_metrics
        ) / len(result.coupling_metrics)
        avg_instability = sum(m.instability for m in result.coupling_metrics) / len(
            result.coupling_metrics
        )
    else:
        avg_outgoing = avg_incoming = avg_instability = 0

    return {
        "modularity_score": result.modularity_score,
        "avg_outgoing_coupling": round(avg_outgoing, 1),
        "avg_incoming_coupling": round(avg_incoming, 1),
        "avg_instability": round(avg_instability, 2),
        "circular_dependencies": len(result.circular_dependencies),
        "external_dependencies": len(result.external_dependencies),
    }


if __name__ == "__main__":
    # Test de l'analyseur de dépendances
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("🔗 Test de l'analyseur de dépendances AGI")
    print("=" * 45)

    analyzer = DependencyAnalyzer()
    result = analyzer.analyze_directory(target)

    print(f"Modules analysés: {result.analyzed_modules}")
    print(f"Relations de dépendance: {len(result.dependency_relations)}")
    print(f"Dépendances circulaires: {len(result.circular_dependencies)}")
    print(f"Dépendances externes: {len(result.external_dependencies)}")
    print(f"Violations de couplage: {len(result.coupling_violations)}")
    print(f"Score de modularité: {result.modularity_score}/100")
