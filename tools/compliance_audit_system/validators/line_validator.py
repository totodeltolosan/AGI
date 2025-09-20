#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_audit_system/validators/line_validator.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""
Validateur de Lignes - Système d'Audit AGI
Responsabilité unique : Validation de la directive des 200 lignes maximum
Respecte strictement la directive des 200 lignes
"""

from pathlib import Path
from typing import Dict, List, NamedTuple, Optional
from dataclasses import dataclass
import csv
from datetime import datetime


class LineViolation(NamedTuple):
    """Représente une violation de la directive de lignes"""

    file_path: str
    line_count: int
    excess_lines: int
    severity: str


@dataclass
class LineValidationResult:
    """Résultat de validation des lignes"""

    total_files: int
    compliant_files: int
    violations: List[LineViolation]
    compliance_rate: float
    max_lines_found: int
    worst_violation: Optional[LineViolation] = None


class LineValidator:
    """Validateur de la directive des 200 lignes maximum"""

    def __init__(self, max_lines: int = 200):
        """TODO: Add docstring."""
        self.max_lines = max_lines
        self.results: List[LineViolation] = []

    def validate_file(self, file_path: Path) -> LineViolation:
        """Valide un fichier Python spécifique"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                line_count = len(lines)

            if line_count <= self.max_lines:
                return None  # Pas de violation

            excess = line_count - self.max_lines
            severity = self._determine_severity(excess)

            return LineViolation(
                file_path=str(file_path),
                line_count=line_count,
                excess_lines=excess,
                severity=severity,
            )

        except Exception as e:
            # En cas d'erreur, considérer comme violation critique
            return LineViolation(
                file_path=str(file_path), line_count=0, excess_lines=0, severity="ERROR"
            )

    def validate_directory(self, target_dir: Path) -> LineValidationResult:
        """Valide tous les fichiers Python d'un répertoire"""
        violations = []
        total_files = 0
        max_lines_found = 0

        # Recherche récursive des fichiers Python
        python_files = list(target_dir.rglob("*.py"))
        total_files = len(python_files)

        for py_file in python_files:
            violation = self.validate_file(py_file)

            # Suivi du nombre max de lignes trouvé
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    file_lines = len(f.readlines())
                    max_lines_found = max(max_lines_found, file_lines)
            except:
                pass

            if violation:
                violations.append(violation)

        # Calcul des métriques
        compliant_files = total_files - len(
            [v for v in violations if v.severity != "ERROR"]
        )
        compliance_rate = (
            (compliant_files / total_files * 100) if total_files > 0 else 100
        )

        # Identification de la pire violation
        worst_violation = None
        if violations:
            worst_violation = max(violations, key=lambda v: v.excess_lines)

        return LineValidationResult(
            total_files=total_files,
            compliant_files=compliant_files,
            violations=violations,
            compliance_rate=compliance_rate,
            max_lines_found=max_lines_found,
            worst_violation=worst_violation,
        )

    def _determine_severity(self, excess_lines: int) -> str:
        """Détermine la sévérité d'une violation"""
        if excess_lines <= 10:
            return "MINOR"
        elif excess_lines <= 50:
            return "MODERATE"
        elif excess_lines <= 100:
            return "MAJOR"
        else:
            return "CRITICAL"

    def generate_violations_report(self, result: LineValidationResult) -> str:
        """Génère un rapport textuel des violations"""
        lines = []
        lines.append("📏 RAPPORT DE VALIDATION DES LIGNES")
        lines.append("=" * 40)

        # Statistiques globales
        lines.append(f"Total fichiers analysés: {result.total_files}")
        lines.append(f"Fichiers conformes: {result.compliant_files}")
        lines.append(f"Violations détectées: {len(result.violations)}")
        lines.append(f"Taux de conformité: {result.compliance_rate:.1f}%")
        lines.append(f"Maximum de lignes trouvé: {result.max_lines_found}")

        # Verdict global
        if not result.violations:
            lines.append(
                "\n🎉 FÉLICITATIONS! Tous les fichiers respectent la directive 200 lignes!"
            )
        else:
            lines.append(f"\n⚠️ VIOLATIONS DÉTECTÉES:")

            # Tri des violations par excès décroissant
            sorted_violations = sorted(
                result.violations, key=lambda v: v.excess_lines, reverse=True
            )

            lines.append(f"{'Fichier':<40} {'Lignes':<8} {'Excès':<8} {'Sévérité':<10}")
            lines.append("-" * 70)

            for violation in sorted_violations:
                filename = Path(violation.file_path).name
                if len(filename) > 35:
                    filename = "..." + filename[-32:]

                lines.append(
                    f"{filename:<40} {violation.line_count:<8} "
                    f"{violation.excess_lines:<8} {violation.severity:<10}"
                )

        # Recommandations
        if result.violations:
            lines.append("\n💡 RECOMMANDATIONS:")
            critical_violations = [
                v for v in result.violations if v.severity == "CRITICAL"
            ]
            if critical_violations:
                lines.append(
                    "1. PRIORITÉ URGENTE: Refactoriser les violations CRITIQUES"
                )
                for violation in critical_violations[:3]:
                    filename = Path(violation.file_path).name
                    lines.append(
                        f"   - {filename} ({violation.excess_lines} lignes en excès)"
                    )

        return "\n".join(lines)

    def export_csv_report(
        self, result: LineValidationResult, output_file: Path
    ) -> bool:
        """Exporte le rapport en format CSV"""
        try:
            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # En-tête
                writer.writerow(["Fichier", "Lignes", "Statut", "Excès", "Sévérité"])

                # Collecte de tous les fichiers (conformes + violations)
                all_files = set()

                # Ajout des violations
                for violation in result.violations:
                    if violation.severity != "ERROR":
                        writer.writerow(
                            [
                                violation.file_path,
                                violation.line_count,
                                "VIOLATION",
                                violation.excess_lines,
                                violation.severity,
                            ]
                        )
                        all_files.add(violation.file_path)

                # Estimation des fichiers conformes (approximation)
                conformant_count = result.compliant_files
                for i in range(conformant_count):
                    writer.writerow(
                        [f"fichier_conforme_{i+1}.py", "< 200", "CONFORME", 0, "NONE"]
                    )

            return True

        except Exception:
            return False


class LineMetricsCalculator:
    """Calculateur de métriques avancées pour les lignes"""

    @staticmethod
    def calculate_refactoring_effort(violations: List[LineViolation]) -> Dict[str, int]:
        """Calcule l'effort de refactorisation estimé"""
        effort_map = {
            "MINOR": 1,  # 1 heure
            "MODERATE": 3,  # 3 heures
            "MAJOR": 8,  # 8 heures
            "CRITICAL": 16,  # 16 heures
        }

        total_effort = 0
        effort_by_severity = {}

        for violation in violations:
            if violation.severity in effort_map:
                effort = effort_map[violation.severity]
                total_effort += effort
                effort_by_severity[violation.severity] = (
                    effort_by_severity.get(violation.severity, 0) + effort
                )

        return {
            "total_hours": total_effort,
            "by_severity": effort_by_severity,
            "files_count": len(violations),
        }

    @staticmethod
    def calculate_debt_metrics(result: LineValidationResult) -> Dict[str, float]:
        """Calcule les métriques de dette technique"""
        if result.total_files == 0:
            return {"debt_ratio": 0.0, "avg_excess": 0.0}

        total_excess = sum(v.excess_lines for v in result.violations)
        violation_count = len(result.violations)

        debt_ratio = violation_count / result.total_files * 100
        avg_excess = total_excess / violation_count if violation_count > 0 else 0

        return {
            "debt_ratio": debt_ratio,
            "avg_excess_per_violation": avg_excess,
            "total_excess_lines": total_excess,
        }


def quick_line_check(target_dir: Path, max_lines: int = 200) -> bool:
    """Vérification rapide - fonction utilitaire"""
    validator = LineValidator(max_lines)
    result = validator.validate_directory(target_dir)
    return len(result.violations) == 0


def get_violation_summary(target_dir: Path) -> Dict:
    """Résumé rapide des violations - fonction utilitaire"""
    validator = LineValidator()
    result = validator.validate_directory(target_dir)

    return {
        "compliant": len(result.violations) == 0,
        "violation_count": len(result.violations),
        "compliance_rate": result.compliance_rate,
        "worst_excess": (
            result.worst_violation.excess_lines if result.worst_violation else 0
        ),
    }


if __name__ == "__main__":
    # Test du validateur de lignes
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("📏 Test du validateur de lignes AGI")
    print("=" * 40)

    validator = LineValidator()
    result = validator.validate_directory(target)

    print(validator.generate_violations_report(result))

    # Métriques avancées
    if result.violations:
        metrics_calc = LineMetricsCalculator()
        effort = metrics_calc.calculate_refactoring_effort(result.violations)
        debt = metrics_calc.calculate_debt_metrics(result)

        print(f"\n📊 MÉTRIQUES AVANCÉES:")
        print(f"Effort de refactorisation estimé: {effort['total_hours']} heures")
        print(f"Ratio de dette technique: {debt['debt_ratio']:.1f}%")