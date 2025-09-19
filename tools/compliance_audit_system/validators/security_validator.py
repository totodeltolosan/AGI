#!/usr/bin/env python3
"""
Validateur de Sécurité - Système d'Audit AGI
Responsabilité unique : Détection des problèmes de sécurité dans le code Python
Respecte strictement la directive des 200 lignes
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, NamedTuple, Set
from dataclasses import dataclass


class SecurityIssue(NamedTuple):
    """Représente un problème de sécurité détecté"""

    file_path: str
    issue_type: str
    description: str
    severity: str
    line_number: int
    pattern: str


@dataclass
class SecurityScanResult:
    """Résultat du scan de sécurité"""

    scanned_files: int
    security_issues: List[SecurityIssue]
    high_risk_files: List[str]
    security_score: float


class SecurityValidator:
    """Validateur de sécurité pour code Python"""

    def __init__(self):
        self.dangerous_patterns = {
            # Exécution de code dangereux
            "code_execution": [
                (
                    r"eval\s*\(",
                    "Usage d'eval() - exécution de code arbitraire",
                    "CRITICAL",
                ),
                (
                    r"exec\s*\(",
                    "Usage d'exec() - exécution de code arbitraire",
                    "CRITICAL",
                ),
                (r"compile\s*\(", "Compilation dynamique de code", "HIGH"),
                (r"__import__\s*\(", "Import dynamique non sécurisé", "MEDIUM"),
            ],
            # Manipulation de fichiers dangereuse
            "file_operations": [
                (
                    r"open\s*\([^)]*['\"]w",
                    "Écriture de fichier sans validation",
                    "MEDIUM",
                ),
                (r"os\.system\s*\(", "Exécution de commandes système", "CRITICAL"),
                (r"subprocess\.call", "Appel subprocess sans validation", "HIGH"),
                (r"os\.popen\s*\(", "Ouverture de processus système", "HIGH"),
            ],
            # Gestion des chemins non sécurisée
            "path_traversal": [
                (r"\.\.\/", "Traversée de répertoire potentielle", "MEDIUM"),
                (r"os\.path\.join.*\.\.", "Path traversal dans os.path.join", "MEDIUM"),
                (
                    r"open\s*\([^)]*\/\.\.",
                    "Ouverture de fichier avec traversée",
                    "HIGH",
                ),
            ],
            # Injection potentielle
            "injection_risks": [
                (
                    r"\.format\s*\(.*input",
                    "Format string avec input utilisateur",
                    "MEDIUM",
                ),
                (r"% .*input", "String formatting avec input", "MEDIUM"),
                (r"sql.*\+.*input", "Concaténation SQL potentielle", "HIGH"),
            ],
        }

        self.secure_patterns = {
            "pathlib_usage": r"from pathlib import|import pathlib",
            "input_validation": r"validate|sanitize|clean",
            "secure_random": r"secrets\.|os\.urandom",
            "logging_security": r"logging\.|logger\.",
        }

    def scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """Scanne un fichier pour détecter les problèmes de sécurité"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # Scan par patterns de regex
            issues.extend(self._scan_dangerous_patterns(file_path, content, lines))

            # Analyse AST si possible
            try:
                tree = ast.parse(content)
                issues.extend(self._analyze_ast_security(file_path, tree))
            except SyntaxError:
                # Ignore les erreurs de syntaxe, gérées par le validateur syntaxique
                pass

        except Exception:
            # Problème de lecture du fichier
            issues.append(
                SecurityIssue(
                    file_path=str(file_path),
                    issue_type="file_access_error",
                    description="Impossible de lire le fichier pour scan sécurité",
                    severity="LOW",
                    line_number=0,
                    pattern="file_error",
                )
            )

        return issues

    def scan_directory(self, target_dir: Path) -> SecurityScanResult:
        """Scanne un répertoire complet"""
        all_issues = []
        scanned_files = 0
        high_risk_files = []

        # Recherche récursive des fichiers Python
        python_files = list(target_dir.rglob("*.py"))

        for py_file in python_files:
            file_issues = self.scan_file(py_file)
            all_issues.extend(file_issues)
            scanned_files += 1

            # Identification des fichiers à haut risque
            critical_issues = [i for i in file_issues if i.severity == "CRITICAL"]
            high_issues = [i for i in file_issues if i.severity == "HIGH"]

            if critical_issues or len(high_issues) >= 2:
                high_risk_files.append(str(py_file))

        # Calcul du score de sécurité
        security_score = self._calculate_security_score(all_issues, scanned_files)

        return SecurityScanResult(
            scanned_files=scanned_files,
            security_issues=all_issues,
            high_risk_files=high_risk_files,
            security_score=security_score,
        )

    def _scan_dangerous_patterns(
        self, file_path: Path, content: str, lines: List[str]
    ) -> List[SecurityIssue]:
        """Scanne les patterns dangereux via regex"""
        issues = []

        for category, patterns in self.dangerous_patterns.items():
            for pattern, description, severity in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        issues.append(
                            SecurityIssue(
                                file_path=str(file_path),
                                issue_type=category,
                                description=description,
                                severity=severity,
                                line_number=line_num,
                                pattern=pattern,
                            )
                        )

        return issues

    def _analyze_ast_security(
        self, file_path: Path, tree: ast.AST
    ) -> List[SecurityIssue]:
        """Analyse de sécurité via AST"""
        issues = []

        for node in ast.walk(tree):
            # Détection d'appels de fonctions dangereuses
            if isinstance(node, ast.Call):
                issues.extend(self._check_dangerous_calls(file_path, node))

            # Détection de manipulations de chaînes dangereuses
            if isinstance(node, ast.BinOp):
                issues.extend(self._check_string_operations(file_path, node))

        return issues

    def _check_dangerous_calls(
        self, file_path: Path, call_node: ast.Call
    ) -> List[SecurityIssue]:
        """Vérifie les appels de fonctions dangereux"""
        issues = []

        # Extraction du nom de la fonction appelée
        func_name = ""
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            func_name = call_node.func.attr

        # Vérification des fonctions dangereuses
        dangerous_functions = {
            "eval": ("Appel eval() détecté via AST", "CRITICAL"),
            "exec": ("Appel exec() détecté via AST", "CRITICAL"),
            "compile": ("Compilation dynamique détectée", "HIGH"),
            "system": ("Appel système détecté", "CRITICAL"),
        }

        if func_name in dangerous_functions:
            description, severity = dangerous_functions[func_name]
            issues.append(
                SecurityIssue(
                    file_path=str(file_path),
                    issue_type="dangerous_call",
                    description=description,
                    severity=severity,
                    line_number=call_node.lineno,
                    pattern=f"ast_call_{func_name}",
                )
            )

        return issues

    def _check_string_operations(
        self, file_path: Path, binop_node: ast.BinOp
    ) -> List[SecurityIssue]:
        """Vérifie les opérations sur chaînes potentiellement dangereuses"""
        issues = []

        # Détection de concaténation avec des variables suspectes
        if isinstance(binop_node.op, ast.Add):
            # Recherche de variables nommées "input", "user_input", etc.
            for node in ast.walk(binop_node):
                if isinstance(node, ast.Name) and node.id in [
                    "input",
                    "user_input",
                    "request",
                ]:
                    issues.append(
                        SecurityIssue(
                            file_path=str(file_path),
                            issue_type="string_injection",
                            description="Concaténation avec input utilisateur",
                            severity="MEDIUM",
                            line_number=binop_node.lineno,
                            pattern="ast_string_concat",
                        )
                    )
                    break

        return issues

    def _calculate_security_score(
        self, issues: List[SecurityIssue], total_files: int
    ) -> float:
        """Calcule un score de sécurité (0-100, 100 = excellent)"""
        if total_files == 0:
            return 100.0

        # Pondération par sévérité
        severity_weights = {"CRITICAL": 10, "HIGH": 5, "MEDIUM": 2, "LOW": 1}

        # Calcul du score de risque
        risk_score = 0
        for issue in issues:
            risk_score += severity_weights.get(issue.severity, 1)

        # Normalisation (plus il y a de risques, plus le score baisse)
        max_possible_risk = total_files * 5  # Estimation du risque maximum
        normalized_risk = (
            min(risk_score / max_possible_risk, 1.0) if max_possible_risk > 0 else 0
        )

        # Score de sécurité (inversé)
        security_score = (1 - normalized_risk) * 100

        return round(security_score, 1)

    def generate_security_report(self, result: SecurityScanResult) -> str:
        """Génère un rapport de sécurité textuel"""
        lines = []
        lines.append("🛡️ RAPPORT DE SÉCURITÉ")
        lines.append("=" * 30)

        # Statistiques globales
        lines.append(f"Fichiers scannés: {result.scanned_files}")
        lines.append(f"Problèmes détectés: {len(result.security_issues)}")
        lines.append(f"Score de sécurité: {result.security_score}/100")
        lines.append(f"Fichiers à haut risque: {len(result.high_risk_files)}")

        # Analyse par sévérité
        if result.security_issues:
            by_severity = {}
            for issue in result.security_issues:
                severity = issue.severity
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(issue)

            lines.append("\n🚨 PROBLÈMES PAR SÉVÉRITÉ:")
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if severity in by_severity:
                    count = len(by_severity[severity])
                    lines.append(f"  {severity}: {count} problème(s)")

                    # Affichage des premiers problèmes
                    for issue in by_severity[severity][:3]:
                        filename = Path(issue.file_path).name
                        lines.append(
                            f"    {filename}:{issue.line_number} - {issue.description}"
                        )

        # Verdict de sécurité
        if result.security_score >= 90:
            lines.append("\n✅ EXCELLENT NIVEAU DE SÉCURITÉ")
        elif result.security_score >= 70:
            lines.append("\n⚠️ NIVEAU DE SÉCURITÉ ACCEPTABLE")
        else:
            lines.append("\n❌ NIVEAU DE SÉCURITÉ INSUFFISANT")

        return "\n".join(lines)


def quick_security_scan(target_dir: Path) -> bool:
    """Scan rapide de sécurité - fonction utilitaire"""
    validator = SecurityValidator()
    result = validator.scan_directory(target_dir)

    # Considère comme "sûr" si pas de problèmes critiques
    critical_issues = [i for i in result.security_issues if i.severity == "CRITICAL"]
    return len(critical_issues) == 0


def get_security_summary(target_dir: Path) -> Dict:
    """Résumé de sécurité - fonction utilitaire"""
    validator = SecurityValidator()
    result = validator.scan_directory(target_dir)

    critical_count = len(
        [i for i in result.security_issues if i.severity == "CRITICAL"]
    )
    high_count = len([i for i in result.security_issues if i.severity == "HIGH"])

    return {
        "secure": critical_count == 0 and high_count <= 1,
        "critical_issues": critical_count,
        "high_issues": high_count,
        "security_score": result.security_score,
        "high_risk_files": len(result.high_risk_files),
    }


if __name__ == "__main__":
    # Test du validateur de sécurité
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("🛡️ Test du validateur de sécurité AGI")
    print("=" * 40)

    validator = SecurityValidator()
    result = validator.scan_directory(target)

    print(validator.generate_security_report(result))
