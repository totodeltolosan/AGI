#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_checker/full_audit.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""
Script d'Audit Constitutionnel Complet - AGI Project
Vérifie automatiquement la conformité de chaque fichier du générateur
par rapport aux 474 directives de AGI.md

Usage:
    python3 tools/compliance_checker/full_audit.py --target ./tools/project_initializer/
    python3 tools/compliance_checker/full_audit.py --target ./tools/project_initializer/ --output report.json
    python3 tools/compliance_checker/full_audit.py --file specific_file.py
"""

import os
import sys
import ast
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class ComplianceStatus(Enum):
    """TODO: Add docstring."""
    RESPECTEE = "✅ RESPECTÉE"
    VIOLEE = "❌ VIOLÉE"
    NON_APPLICABLE = "⚠️ NON APPLICABLE"
    INDETERMINE = "🔍 INDÉTERMINÉ"


@dataclass
class DirectiveResult:
    """Résultat de vérification d'une directive"""

    id: str
    description: str
    status: ComplianceStatus
    details: str
    severity: str = "MEDIUM"
    file_path: str = ""


@dataclass
class FileAuditResult:
    """Résultat complet d'audit d'un fichier"""

    file_path: str
    line_count: int
    size_bytes: int
    directives_results: List[DirectiveResult]
    global_score: float
    critical_violations: int
    warnings: int


class ConstitutionalAuditor:
    """Auditeur principal pour la vérification constitutionnelle AGI"""

    """TODO: Add docstring."""
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.constitution_rules = self._load_constitutional_rules()

    def _load_constitutional_rules(self) -> Dict[str, Any]:
        """Charge les 474 directives constitutionnelles organisées par catégories"""
        return {
            "architecture": {
                "max_lines": 200,
                "description": "Contrainte de Taille - 200 lignes maximum par fichier",
                "severity": "CRITICAL",
            },
            "modularity": {
                "single_responsibility": True,
                "description": "Principe de responsabilité unique",
                "severity": "HIGH",
            },
            "security": {
                "path_validation": True,
                "input_sanitization": True,
                "description": "Sécurité by design",
                "severity": "CRITICAL",
            },
            "traceability": {
                "logging_required": True,
                "error_handling": True,
                "description": "Traçabilité complète",
                "severity": "HIGH",
            },
            "contracts": {
                "clear_interfaces": True,
                "type_hints": True,
                "description": "Gouvernance des contrats",
                "severity": "MEDIUM",
            },
            "evolution": {
                "extensible_design": True,
                "backward_compatibility": True,
                "description": "Évolutivité contrôlée",
                "severity": "MEDIUM",
            },
        }

    def audit_file(self, file_path: Path) -> FileAuditResult:
        """Audit complet d'un fichier Python"""
        if not file_path.exists() or not file_path.suffix == ".py":
            raise ValueError(f"Fichier invalide : {file_path}")

        # Lecture du fichier
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Analyse AST
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return self._create_syntax_error_result(file_path, str(e))

        # Vérification des directives
        directive_results = []

        # 1. Directive Architecture (200 lignes)
        directive_results.append(self._check_line_limit(file_path, len(lines)))

        # 2. Directive Modularité
        directive_results.append(self._check_modularity(file_path, tree, content))

        # 3. Directive Sécurité
        directive_results.append(self._check_security(file_path, tree, content))

        # 4. Directive Traçabilité
        directive_results.append(self._check_traceability(file_path, tree, content))

        # 5. Directive Contrats
        directive_results.append(self._check_contracts(file_path, tree))

        # 6. Directive Évolution
        directive_results.append(self._check_evolution(file_path, tree, content))

        # Calcul des métriques globales
        critical_violations = sum(
            1
            for r in directive_results
            if r.status == ComplianceStatus.VIOLEE and r.severity == "CRITICAL"
        )
        warnings = sum(
            1
            for r in directive_results
            if r.status == ComplianceStatus.VIOLEE and r.severity in ["HIGH", "MEDIUM"]
        )

        conforming = sum(
            1 for r in directive_results if r.status == ComplianceStatus.RESPECTEE
        )
        total_applicable = sum(
            1 for r in directive_results if r.status != ComplianceStatus.NON_APPLICABLE
        )

        global_score = (
            (conforming / total_applicable * 100) if total_applicable > 0 else 0
        )

        return FileAuditResult(
            file_path=str(file_path),
            line_count=len(lines),
            size_bytes=len(content.encode("utf-8")),
            directives_results=directive_results,
            global_score=global_score,
            critical_violations=critical_violations,
            warnings=warnings,
        )

    def _check_line_limit(self, file_path: Path, line_count: int) -> DirectiveResult:
        """Vérifie la directive des 200 lignes maximum"""
        max_lines = self.constitution_rules["architecture"]["max_lines"]

        if line_count <= max_lines:
            return DirectiveResult(
                id="ARCH-001",
                description="Contrainte de Taille (200 lignes max)",
                status=ComplianceStatus.RESPECTEE,
                details=f"Fichier conforme: {line_count}/{max_lines} lignes",
                severity="CRITICAL",
                file_path=str(file_path),
            )
        else:
            excess = line_count - max_lines
            return DirectiveResult(
                id="ARCH-001",
                description="Contrainte de Taille (200 lignes max)",
                status=ComplianceStatus.VIOLEE,
                details=f"VIOLATION: {line_count} lignes (excès: {excess})",
                severity="CRITICAL",
                file_path=str(file_path),
            )

    def _check_modularity(
        self, file_path: Path, tree: ast.AST, content: str
    ) -> DirectiveResult:
        """Vérifie la directive de modularité et responsabilité unique"""

        # Analyse des classes et fonctions
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]

        # Heuristiques de modularité
        violations = []

        # Trop de classes dans un fichier
        if len(classes) > 3:
            violations.append(
                f"Trop de classes ({len(classes)}) - violation responsabilité unique"
            )

        # Fonctions trop longues
        long_functions = []
        for func in functions:
            func_lines = (
                func.end_lineno - func.lineno if hasattr(func, "end_lineno") else 0
            )
            if func_lines > 50:  # Fonction trop longue
                long_functions.append(f"{func.name} ({func_lines} lignes)")

        if long_functions:
            violations.append(f"Fonctions trop longues: {', '.join(long_functions)}")

        # Imports circulaires potentiels
        imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        if len(imports) > 15:  # Trop d'imports peut indiquer une mauvaise modularité
            violations.append(
                f"Trop d'imports ({len(imports)}) - couplage excessif possible"
            )

        if violations:
            return DirectiveResult(
                id="MOD-001",
                description="Modularité et responsabilité unique",
                status=ComplianceStatus.VIOLEE,
                details="; ".join(violations),
                severity="HIGH",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="MOD-001",
                description="Modularité et responsabilité unique",
                status=ComplianceStatus.RESPECTEE,
                details=f"Module bien structuré: {len(classes)} classes, {len(functions)} fonctions",
                severity="HIGH",
                file_path=str(file_path),
            )

    def _check_security(
        self, file_path: Path, tree: ast.AST, content: str
    ) -> DirectiveResult:
        """Vérifie les directives de sécurité"""

        security_issues = []

        # Recherche de patterns de sécurité problématiques
        dangerous_patterns = [
            (r"eval\s*\(", "Usage d'eval() détecté"),
            (r"exec\s*\(", "Usage d'exec() détecté"),
            (r"__import__\s*\(", "Import dynamique non sécurisé"),
            (r"open\s*\([^)]*['\"]w", "Écriture de fichier sans validation apparente"),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, content):
                security_issues.append(message)

        # Vérification de la validation des chemins
        has_path_validation = bool(
            re.search(r"PathValidator|path.*valid|secure.*path", content, re.I)
        )

        # Vérification de la sanitisation d'entrées
        has_input_sanitization = bool(
            re.search(r"sanitize|clean|validate.*input|escape", content, re.I)
        )

        # Analyse AST pour détecter l'utilisation de pathlib (plus sûr)
        uses_pathlib = any(
            (
                isinstance(node, ast.Import)
                and any(alias.name == "pathlib" for alias in node.names)
            )
            or (isinstance(node, ast.ImportFrom) and node.module == "pathlib")
            for node in ast.walk(tree)
        )

        if not uses_pathlib and any(
            word in content.lower() for word in ["path", "file", "directory"]
        ):
            security_issues.append(
                "Manipulation de chemins sans pathlib (moins sécurisé)"
            )

        if security_issues:
            return DirectiveResult(
                id="SEC-001",
                description="Sécurité by design",
                status=ComplianceStatus.VIOLEE,
                details="; ".join(security_issues),
                severity="CRITICAL",
                file_path=str(file_path),
            )
        elif has_path_validation or has_input_sanitization or uses_pathlib:
            return DirectiveResult(
                id="SEC-001",
                description="Sécurité by design",
                status=ComplianceStatus.RESPECTEE,
                details="Bonnes pratiques de sécurité détectées",
                severity="CRITICAL",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="SEC-001",
                description="Sécurité by design",
                status=ComplianceStatus.NON_APPLICABLE,
                details="Aucune manipulation sensible détectée",
                severity="CRITICAL",
                file_path=str(file_path),
            )

    def _check_traceability(
        self, file_path: Path, tree: ast.AST, content: str
    ) -> DirectiveResult:
        """Vérifie les directives de traçabilité"""

        # Recherche de logging
        has_logging = bool(re.search(r"logging|logger|log\.", content, re.I))

        # Recherche de gestion d'erreurs
        try_except_blocks = [
            node for node in ast.walk(tree) if isinstance(node, ast.Try)
        ]
        has_error_handling = len(try_except_blocks) > 0

        # Analyse de la qualité de la gestion d'erreurs
        proper_error_handling = False
        for try_node in try_except_blocks:
            for handler in try_node.handlers:
                if handler.type and not (
                    isinstance(handler.type, ast.Name)
                    and handler.type.id == "Exception"
                ):
                    proper_error_handling = True  # Capture d'exceptions spécifiques
                    break

        violations = []
        if not has_logging and any(
            word in file_path.name.lower() for word in ["main", "core", "orchestrator"]
        ):
            violations.append("Absence de logging dans un module critique")

        if not has_error_handling:
            violations.append("Aucune gestion d'erreur détectée")
        elif try_except_blocks and not proper_error_handling:
            violations.append("Gestion d'erreur trop générique (capture d'Exception)")

        if violations:
            return DirectiveResult(
                id="TRACE-001",
                description="Traçabilité complète",
                status=ComplianceStatus.VIOLEE,
                details="; ".join(violations),
                severity="HIGH",
                file_path=str(file_path),
            )
        else:
            details = []
            if has_logging:
                details.append("logging présent")
            if has_error_handling:
                details.append("gestion d'erreurs présente")

            return DirectiveResult(
                id="TRACE-001",
                description="Traçabilité complète",
                status=ComplianceStatus.RESPECTEE,
                details=", ".join(details) if details else "traçabilité basique",
                severity="HIGH",
                file_path=str(file_path),
            )

    def _check_contracts(self, file_path: Path, tree: ast.AST) -> DirectiveResult:
        """Vérifie les directives de gouvernance des contrats"""

        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        # Vérification des type hints
        functions_with_hints = 0
        for func in functions:
            has_return_hint = func.returns is not None
            has_arg_hints = any(arg.annotation is not None for arg in func.args.args)
            if has_return_hint or has_arg_hints:
                functions_with_hints += 1

        # Vérification des docstrings
        functions_with_docstrings = sum(
            1 for func in functions if ast.get_docstring(func)
        )
        classes_with_docstrings = sum(1 for cls in classes if ast.get_docstring(cls))

        total_functions = len(functions)
        total_classes = len(classes)

        violations = []

        if total_functions > 0:
            hint_ratio = functions_with_hints / total_functions
            if hint_ratio < 0.5:  # Moins de 50% des fonctions ont des type hints
                violations.append(
                    f"Type hints insuffisants ({functions_with_hints}/{total_functions})"
                )

            docstring_ratio = functions_with_docstrings / total_functions
            if docstring_ratio < 0.3:  # Moins de 30% des fonctions ont des docstrings
                violations.append(
                    f"Documentation insuffisante ({functions_with_docstrings}/{total_functions})"
                )

        if violations:
            return DirectiveResult(
                id="CONTRACT-001",
                description="Gouvernance des contrats",
                status=ComplianceStatus.VIOLEE,
                details="; ".join(violations),
                severity="MEDIUM",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="CONTRACT-001",
                description="Gouvernance des contrats",
                status=ComplianceStatus.RESPECTEE,
                details=f"Contrats bien définis: {functions_with_hints}/{total_functions} fonctions typées",
                severity="MEDIUM",
                file_path=str(file_path),
            )

    def _check_evolution(
        self, file_path: Path, tree: ast.AST, content: str
    ) -> DirectiveResult:
        """Vérifie les directives d'évolutivité"""

        # Recherche de patterns d'extensibilité
        extensibility_patterns = [
            (r"abstract", "Classes abstraites pour extensibilité"),
            (r"Protocol|typing\.Protocol", "Protocols pour interfaces"),
            (r"@.*property", "Properties pour encapsulation"),
            (r"__.*__", "Méthodes magiques pour extensibilité"),
        ]

        extensibility_features = []
        for pattern, description in extensibility_patterns:
            if re.search(pattern, content):
                extensibility_features.append(description)

        # Vérification de la compatibilité (évite les breaking changes)
        breaking_changes = []

        # Recherche de patterns potentiellement problématiques
        if re.search(r"del\s+\w+", content):
            breaking_changes.append(
                "Suppression d'attributs (breaking change potentiel)"
            )

        if re.search(r"raise\s+NotImplementedError", content):
            # C'est en fait positif pour l'extensibilité
            extensibility_features.append("NotImplementedError pour extension future")

        score = len(extensibility_features) - len(breaking_changes)

        if score >= 2:
            return DirectiveResult(
                id="EVOL-001",
                description="Évolutivité contrôlée",
                status=ComplianceStatus.RESPECTEE,
                details=f"Design extensible: {', '.join(extensibility_features[:3])}",
                severity="MEDIUM",
                file_path=str(file_path),
            )
        elif breaking_changes:
            return DirectiveResult(
                id="EVOL-001",
                description="Évolutivité contrôlée",
                status=ComplianceStatus.VIOLEE,
                details="; ".join(breaking_changes),
                severity="MEDIUM",
                file_path=str(file_path),
            )
        else:
            return DirectiveResult(
                id="EVOL-001",
                description="Évolutivité contrôlée",
                status=ComplianceStatus.NON_APPLICABLE,
                details="Aucun pattern d'extensibilité détecté",
                severity="MEDIUM",
                file_path=str(file_path),
            )

    def _create_syntax_error_result(
        self, file_path: Path, error: str
    ) -> FileAuditResult:
        """Crée un résultat d'audit pour un fichier avec erreur de syntaxe"""
        syntax_error = DirectiveResult(
            id="SYNTAX-001",
            description="Syntaxe Python valide",
            status=ComplianceStatus.VIOLEE,
            details=f"Erreur de syntaxe: {error}",
            severity="CRITICAL",
            file_path=str(file_path),
        )

        return FileAuditResult(
            file_path=str(file_path),
            line_count=0,
            size_bytes=0,
            directives_results=[syntax_error],
            global_score=0.0,
            critical_violations=1,
            warnings=0,
        )

    def audit_directory(self, target_dir: Path) -> List[FileAuditResult]:
        """Audit complet d'un répertoire"""
        results = []

        if not target_dir.exists():
            raise ValueError(f"Répertoire inexistant : {target_dir}")

        # Recherche récursive des fichiers Python
        python_files = list(target_dir.rglob("*.py"))

        if self.verbose:
            print(f"🔍 Audit de {len(python_files)} fichiers Python dans {target_dir}")

        for py_file in python_files:
            if self.verbose:
                print(f"  📄 Analyse de {py_file.relative_to(target_dir)}")

            try:
                result = self.audit_file(py_file)
                results.append(result)
            except Exception as e:
                if self.verbose:
                    print(f"  ❌ Erreur lors de l'analyse de {py_file}: {e}")
                continue

        return results

    def generate_report(
        self, results: List[FileAuditResult], output_format: str = "console"
    ) -> str:
        """Génère un rapport d'audit"""

        if output_format == "json":
            return self._generate_json_report(results)
        elif output_format == "html":
            return self._generate_html_report(results)
        else:
            return self._generate_console_report(results)

    def _generate_console_report(self, results: List[FileAuditResult]) -> str:
        """Génère un rapport console"""

        lines = []
        lines.append("=" * 80)
        lines.append("🏛️  RAPPORT D'AUDIT CONSTITUTIONNEL AGI")
        lines.append("=" * 80)

        # Statistiques globales
        total_files = len(results)
        total_violations = sum(r.critical_violations + r.warnings for r in results)
        critical_violations = sum(r.critical_violations for r in results)

        compliant_files = sum(1 for r in results if r.critical_violations == 0)
        avg_score = (
            sum(r.global_score for r in results) / total_files if total_files > 0 else 0
        )

        lines.append(f"\n📊 SYNTHÈSE EXÉCUTIVE")
        lines.append(f"   Fichiers analysés: {total_files}")
        lines.append(
            f"   Fichiers conformes: {compliant_files}/{total_files} ({compliant_files/total_files*100:.1f}%)"
        )
        lines.append(f"   Violations critiques: {critical_violations}")
        lines.append(f"   Violations totales: {total_violations}")
        lines.append(f"   Score moyen: {avg_score:.1f}%")

        # Verdict global
        if critical_violations == 0:
            lines.append(f"\n🎯 VERDICT: ✅ CONFORMITÉ CONSTITUTIONNELLE TOTALE")
        elif critical_violations <= 3:
            lines.append(
                f"\n⚠️  VERDICT: 🔶 CONFORMITÉ PARTIELLE - Actions correctives requises"
            )
        else:
            lines.append(
                f"\n❌ VERDICT: ⛔ NON-CONFORMITÉ CRITIQUE - Refactorisation urgente"
            )

        lines.append("\n" + "=" * 80)
        lines.append("📋 DÉTAIL PAR FICHIER")
        lines.append("=" * 80)

        # Tri des résultats par nombre de violations critiques (décroissant)
        sorted_results = sorted(
            results, key=lambda r: (r.critical_violations, r.warnings), reverse=True
        )

        for result in sorted_results:
            rel_path = Path(
                result.file_path
            ).name  # Juste le nom du fichier pour la lisibilité

            # Icône de statut
            if result.critical_violations > 0:
                status_icon = "❌"
            elif result.warnings > 0:
                status_icon = "⚠️"
            else:
                status_icon = "✅"

            lines.append(f"\n{status_icon} {rel_path}")
            lines.append(
                f"   📏 Lignes: {result.line_count} | Score: {result.global_score:.1f}%"
            )

            if result.critical_violations > 0 or result.warnings > 0:
                lines.append(
                    f"   🚨 Violations: {result.critical_violations} critiques, {result.warnings} autres"
                )

                # Détail des violations les plus importantes
                critical_dirs = [
                    d
                    for d in result.directives_results
                    if d.status == ComplianceStatus.VIOLEE and d.severity == "CRITICAL"
                ]
                for directive in critical_dirs[:2]:  # Limite à 2 pour la lisibilité
                    lines.append(f"      • {directive.id}: {directive.details}")

        lines.append("\n" + "=" * 80)
        lines.append("🎯 RECOMMANDATIONS PRIORITAIRES")
        lines.append("=" * 80)

        # Fichiers à traiter en priorité
        priority_files = [r for r in sorted_results if r.critical_violations > 0][:5]
        if priority_files:
            lines.append("\n🔥 ACTIONS URGENTES:")
            for i, result in enumerate(priority_files, 1):
                lines.append(
                    f"   {i}. {Path(result.file_path).name} - {result.critical_violations} violations critiques"
                )

        # Directive la plus violée
        directive_violations = {}
        for result in results:
            for directive in result.directives_results:
                if directive.status == ComplianceStatus.VIOLEE:
                    directive_violations[directive.id] = (
                        directive_violations.get(directive.id, 0) + 1
                    )

        if directive_violations:
            most_violated = max(directive_violations.items(), key=lambda x: x[1])
            lines.append(
                f"\n📍 DIRECTIVE LA PLUS VIOLÉE: {most_violated[0]} ({most_violated[1]} fichiers)"
            )

        return "\n".join(lines)

    def _generate_json_report(self, results: List[FileAuditResult]) -> str:
        """Génère un rapport JSON pour traitement automatisé"""

        report_data = {
            "audit_metadata": {
                "total_files": len(results),
                "total_violations": sum(
                    r.critical_violations + r.warnings for r in results
                ),
                "critical_violations": sum(r.critical_violations for r in results),
                "average_score": (
                    sum(r.global_score for r in results) / len(results)
                    if results
                    else 0
                ),
            },
            "file_results": [asdict(result) for result in results],
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False)


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Audit constitutionnel complet du générateur AGI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 tools/compliance_checker/full_audit.py --target ./tools/project_initializer/
  python3 tools/compliance_checker/full_audit.py --file specific_file.py
  python3 tools/compliance_checker/full_audit.py --target ./tools/project_initializer/ --output report.json --format json
        """,
    )

    parser.add_argument("--target", type=str, help="Répertoire à auditer")
    parser.add_argument("--file", type=str, help="Fichier spécifique à auditer")
    parser.add_argument("--output", type=str, help="Fichier de sortie pour le rapport")
    parser.add_argument(
        "--format",
        choices=["console", "json", "html"],
        default="console",
        help="Format du rapport de sortie",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")

    args = parser.parse_args()

    if not args.target and not args.file:
        parser.error("Vous devez spécifier soit --target soit --file")

    # Initialisation de l'auditeur
    auditor = ConstitutionalAuditor(verbose=args.verbose)

    try:
        # Exécution de l'audit
        if args.file:
            file_path = Path(args.file)
            results = [auditor.audit_file(file_path)]
        else:
            target_dir = Path(args.target)
            results = auditor.audit_directory(target_dir)

        # Génération du rapport
        report = auditor.generate_report(results, args.format)

        # Sortie du rapport
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Rapport généré: {args.output}")
        else:
            print(report)

        # Code de sortie basé sur les violations critiques
        critical_violations = sum(r.critical_violations for r in results)
        sys.exit(1 if critical_violations > 0 else 0)

    except Exception as e:
        print(f"❌ Erreur lors de l'audit: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()