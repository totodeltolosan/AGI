#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_audit_system/reporters/console_reporter.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""
Rapporteur Console - Système d'Audit AGI
Responsabilité unique : Génération de rapports console formatés et lisibles
Respecte strictement la directive des 200 lignes
"""

from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime


class ConsoleReporter:
    """Générateur de rapports console pour l'audit AGI"""

    def __init__(self):
        """TODO: Add docstring."""
        self.colors = {
            "RED": "\033[0;31m",
            "GREEN": "\033[0;32m",
            "YELLOW": "\033[1;33m",
            "BLUE": "\033[0;34m",
            "PURPLE": "\033[0;35m",
            "CYAN": "\033[0;36m",
            "WHITE": "\033[1;37m",
            "RESET": "\033[0m",
        }

    def generate_report(self, audit_results: Dict) -> str:
        """Génère le rapport console complet"""
        sections = []

        # En-tête principal
        sections.append(self._generate_header())

        # Synthèse exécutive
        sections.append(self._generate_executive_summary(audit_results))

        # Résultats par catégorie
        if "line_compliance" in audit_results:
            sections.append(
                self._generate_line_compliance_section(audit_results["line_compliance"])
            )

        if "syntax_check" in audit_results:
            sections.append(
                self._generate_syntax_section(audit_results["syntax_check"])
            )

        if "security_scan" in audit_results:
            sections.append(
                self._generate_security_section(audit_results["security_scan"])
            )

        # Recommandations
        sections.append(self._generate_recommendations(audit_results))

        # Pied de page
        sections.append(self._generate_footer())

        return "\n\n".join(sections)

    def _generate_header(self) -> str:
        """Génère l'en-tête du rapport"""
        lines = []
        lines.append("=" * 80)
        lines.append(
            f"{self._colorize('🏛️  RAPPORT D\'AUDIT CONSTITUTIONNEL AGI', 'PURPLE')}"
        )
        lines.append("=" * 80)
        lines.append(f"📅 Date: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
        lines.append(f"🎯 Mission: Validation de conformité aux directives AGI.md")

        return "\n".join(lines)

    def _generate_executive_summary(self, audit_results: Dict) -> str:
        """Génère la synthèse exécutive"""
        lines = []
        lines.append(f"{self._colorize('📊 SYNTHÈSE EXÉCUTIVE', 'BLUE')}")
        lines.append("-" * 40)

        # Calcul des métriques globales
        total_files = self._get_total_files(audit_results)
        total_violations = self._get_total_violations(audit_results)
        compliance_rate = self._calculate_global_compliance(audit_results)

        lines.append(f"📁 Fichiers analysés: {total_files}")
        lines.append(f"⚖️ Violations détectées: {total_violations}")
        lines.append(f"📈 Taux de conformité global: {compliance_rate:.1f}%")

        # Verdict global
        verdict = self._determine_global_verdict(compliance_rate, total_violations)
        lines.append(f"🎯 Verdict: {verdict}")

        return "\n".join(lines)

    def _generate_line_compliance_section(self, line_results: Dict) -> str:
        """Génère la section conformité des lignes"""
        lines = []
        lines.append(f"{self._colorize('📏 CONFORMITÉ DES LIGNES (200 max)', 'CYAN')}")
        lines.append("-" * 50)

        if "results" in line_results:
            violations = [
                r for r in line_results["results"] if r.get("status") == "VIOLATION"
            ]
            conformes = [
                r for r in line_results["results"] if r.get("status") == "CONFORME"
            ]

            lines.append(f"✅ Fichiers conformes: {len(conformes)}")
            lines.append(f"❌ Violations: {len(violations)}")

            if violations:
                lines.append("\n🚨 TOP VIOLATIONS:")
                # Tri par excès décroissant
                sorted_violations = sorted(
                    violations, key=lambda x: x.get("excess", 0), reverse=True
                )

                for violation in sorted_violations[:5]:  # Top 5
                    filename = Path(violation["file_path"]).name
                    excess = violation.get("excess", 0)
                    lines.append(f"   {filename}: +{excess} lignes")

        return "\n".join(lines)

    def _generate_syntax_section(self, syntax_results: Dict) -> str:
        """Génère la section validation syntaxique"""
        lines = []
        lines.append(f"{self._colorize('🐍 VALIDATION SYNTAXIQUE', 'GREEN')}")
        lines.append("-" * 40)

        valid_files = syntax_results.get("valid_files", 0)
        total_files = syntax_results.get("total_files", 0)
        errors = syntax_results.get("syntax_errors", [])

        lines.append(f"✅ Fichiers valides: {valid_files}/{total_files}")
        lines.append(f"❌ Erreurs de syntaxe: {len(errors)}")

        if errors:
            lines.append("\n🚨 ERREURS DÉTECTÉES:")
            for error in errors[:3]:  # Top 3 erreurs
                filename = Path(error.file_path).name
                lines.append(
                    f"   {filename}:{error.line_number} - {error.error_message}"
                )

        return "\n".join(lines)

    def _generate_security_section(self, security_results: Dict) -> str:
        """Génère la section sécurité"""
        lines = []
        lines.append(f"{self._colorize('🛡️ ANALYSE DE SÉCURITÉ', 'YELLOW')}")
        lines.append("-" * 40)

        issues = security_results.get("security_issues", [])
        scanned_files = security_results.get("scanned_files", 0)

        lines.append(f"🔍 Fichiers scannés: {scanned_files}")
        lines.append(f"⚠️ Problèmes détectés: {len(issues)}")

        if issues:
            lines.append("\n🔒 PROBLÈMES DE SÉCURITÉ:")
            for issue in issues[:3]:  # Top 3 problèmes
                filename = Path(issue["file_path"]).name
                lines.append(f"   {filename}: {issue['description']}")

        return "\n".join(lines)

    def _generate_recommendations(self, audit_results: Dict) -> str:
        """Génère les recommandations"""
        lines = []
        lines.append(f"{self._colorize('💡 RECOMMANDATIONS PRIORITAIRES', 'WHITE')}")
        lines.append("-" * 50)

        recommendations = self._calculate_recommendations(audit_results)

        if not recommendations:
            lines.append("🎉 Aucune action corrective requise!")
        else:
            for i, recommendation in enumerate(recommendations[:5], 1):
                lines.append(f"{i}. {recommendation}")

        return "\n".join(lines)

    def _generate_footer(self) -> str:
        """Génère le pied de page"""
        lines = []
        lines.append("=" * 80)
        lines.append(
            f"{self._colorize('🔧 SYSTÈME D\'AUDIT AGI - VERSION MODULAIRE', 'PURPLE')}"
        )
        lines.append(f"📖 Conforme aux directives AGI.md - Tous modules < 200 lignes")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _colorize(self, text: str, color: str) -> str:
        """Ajoute la couleur au texte"""
        if color in self.colors:
            return f"{self.colors[color]}{text}{self.colors['RESET']}"
        return text

    def _get_total_files(self, audit_results: Dict) -> int:
        """Calcule le nombre total de fichiers analysés"""
        total = 0

        if (
            "line_compliance" in audit_results
            and "results" in audit_results["line_compliance"]
        ):
            total = max(total, len(audit_results["line_compliance"]["results"]))

        if "syntax_check" in audit_results:
            total = max(total, audit_results["syntax_check"].get("total_files", 0))

        return total

    def _get_total_violations(self, audit_results: Dict) -> int:
        """Calcule le nombre total de violations"""
        violations = 0

        # Violations de lignes
        if (
            "line_compliance" in audit_results
            and "results" in audit_results["line_compliance"]
        ):
            line_violations = [
                r
                for r in audit_results["line_compliance"]["results"]
                if r.get("status") == "VIOLATION"
            ]
            violations += len(line_violations)

        # Erreurs de syntaxe
        if "syntax_check" in audit_results:
            syntax_errors = audit_results["syntax_check"].get("syntax_errors", [])
            violations += len(syntax_errors)

        # Problèmes de sécurité
        if "security_scan" in audit_results:
            security_issues = audit_results["security_scan"].get("security_issues", [])
            violations += len(security_issues)

        return violations

    def _calculate_global_compliance(self, audit_results: Dict) -> float:
        """Calcule le taux de conformité global"""
        total_files = self._get_total_files(audit_results)
        total_violations = self._get_total_violations(audit_results)

        if total_files == 0:
            return 100.0

        # Approximation: chaque violation affecte un fichier
        affected_files = min(total_violations, total_files)
        compliant_files = total_files - affected_files

        return (compliant_files / total_files) * 100

    def _determine_global_verdict(
        self, compliance_rate: float, total_violations: int
    ) -> str:
        """Détermine le verdict global"""
        if compliance_rate >= 95 and total_violations == 0:
            return self._colorize("✅ EXCELLENTE CONFORMITÉ", "GREEN")
        elif compliance_rate >= 80:
            return self._colorize("⚠️ CONFORMITÉ ACCEPTABLE", "YELLOW")
        elif compliance_rate >= 60:
            return self._colorize("🔶 CONFORMITÉ PARTIELLE", "YELLOW")
        else:
            return self._colorize("❌ NON-CONFORMITÉ CRITIQUE", "RED")

    def _calculate_recommendations(self, audit_results: Dict) -> List[str]:
        """Calcule les recommandations prioritaires"""
        recommendations = []

        # Recommandations basées sur les violations de lignes
        if (
            "line_compliance" in audit_results
            and "results" in audit_results["line_compliance"]
        ):
            violations = [
                r
                for r in audit_results["line_compliance"]["results"]
                if r.get("status") == "VIOLATION"
            ]
            if violations:
                worst_violation = max(violations, key=lambda x: x.get("excess", 0))
                filename = Path(worst_violation["file_path"]).name
                recommendations.append(
                    f"URGENT: Refactoriser {filename} ({worst_violation.get('excess', 0)} lignes excès)"
                )

        # Recommandations syntaxiques
        if "syntax_check" in audit_results:
            errors = audit_results["syntax_check"].get("syntax_errors", [])
            if errors:
                recommendations.append(f"Corriger {len(errors)} erreur(s) de syntaxe")

        # Recommandations sécurité
        if "security_scan" in audit_results:
            issues = audit_results["security_scan"].get("security_issues", [])
            if issues:
                recommendations.append(f"Traiter {len(issues)} problème(s) de sécurité")

        return recommendations


# Fonction utilitaire pour génération rapide
def quick_console_report(audit_results: Dict) -> str:
    """Génération rapide de rapport console"""
    reporter = ConsoleReporter()
    return reporter.generate_report(audit_results)


if __name__ == "__main__":
    # Test du rapporteur console
    test_results = {
        "line_compliance": {
            "results": [
                {"file_path": "test1.py", "status": "VIOLATION", "excess": 50},
                {"file_path": "test2.py", "status": "CONFORME", "excess": 0},
            ]
        },
        "syntax_check": {
            "total_files": 2,
            "valid_files": 1,
            "syntax_errors": [
                {
                    "file_path": "test1.py",
                    "line_number": 10,
                    "error_message": "Test error",
                }
            ],
        },
    }

    reporter = ConsoleReporter()
    print(reporter.generate_report(test_results))