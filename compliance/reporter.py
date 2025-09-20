#!/usr/bin/env python3
"""
Audit Reporter - Générateur de Rapports d'Audit Constitutionnel (v2.1 avec JSON)
================================================================================

CHEMIN: compliance/reporter.py

Rôle Fondamental (Conforme iaGOD.json) :
- Générer des rapports d'audit lisibles (console) et exploitables (JSON).
- Formater les sorties selon les standards AGI.
- Isoler complètement la logique de présentation de la logique d'audit.
- Respecter la directive < 200 lignes.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Import des contrats de données
from .models import AuditContext, Violation


class AuditReporter:
    """
    Génère des rapports formatés (texte et JSON) à partir des résultats d'un audit.
    """

    def __init__(self):
        """Initialise le reporter."""
        self.logger = logging.getLogger(__name__)

    def generate_console_report(self, context: AuditContext) -> str:
        """Génère un rapport textuel formaté pour la console."""
        if not context.violations:
            return self._generate_success_report()

        violations = context.violations
        report_lines = [
            "🚨 RAPPORT D'AUDIT CONSTITUTIONNEL AGI",
            "=" * 50,
            "",
            "📊 STATISTIQUES:",
            f"   • Violations totales: {len(violations)}",
            self._format_stats_by_severity(violations),
            "",
            "🔍 DÉTAIL DES VIOLATIONS:",
            "-" * 30,
        ]

        for severity, name in [
            ("CRITICAL", "CRITIQUES"),
            ("MEDIUM", "MOYENNES"),
            ("LOW", "MINEURES"),
        ]:
            severity_violations = [v for v in violations if v.severity == severity]
            if severity_violations:
                report_lines.extend(
                    self._format_violations_group(name, severity_violations)
                )

        report_lines.extend(self._get_footer())
        return "\n".join(report_lines)

    def save_report_to_file(self, context: AuditContext, output_path: Path):
        """Sauvegarde le rapport textuel dans un fichier."""
        try:
            report_content = self.generate_console_report(context)
            output_path.write_text(report_content, encoding="utf-8")
            self.logger.info(f"Rapport d'audit sauvegardé dans : {output_path}")
        except Exception as e:
            self.logger.error(
                f"Impossible de sauvegarder le rapport dans {output_path}: {e}"
            )

    def generate_json_report(self, context: AuditContext) -> Dict[str, Any]:
        """Génère un rapport structuré en JSON."""
        violations_data = [
            {
                "law_id": v.law.id,
                "law_name": v.law.name,
                "severity": v.severity,
                "file_path": str(v.file_path),
                "line_number": v.line_number,
                "message": v.message,
                "suggestion": v.suggestion,
            }
            for v in context.violations
        ]

        return {
            "summary": {
                "total_violations": len(context.violations),
                "critical": len(
                    [v for v in context.violations if v.severity == "CRITICAL"]
                ),
                "medium": len(
                    [v for v in context.violations if v.severity == "MEDIUM"]
                ),
                "low": len([v for v in context.violations if v.severity == "LOW"]),
            },
            "violations": violations_data,
        }

    def save_json_report(self, context: AuditContext, output_path: Path):
        """Sauvegarde le rapport JSON dans un fichier."""
        try:
            report_data = self.generate_json_report(context)
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
            self.logger.info(f"Rapport JSON sauvegardé dans : {output_path}")
        except Exception as e:
            self.logger.error(
                f"Impossible de sauvegarder le rapport JSON dans {output_path}: {e}"
            )

    def _format_stats_by_severity(self, violations: List[Violation]) -> str:
        """Formate la ligne de statistiques par sévérité."""
        criticals = len([v for v in violations if v.severity == "CRITICAL"])
        mediums = len([v for v in violations if v.severity == "MEDIUM"])
        lows = len([v for v in violations if v.severity == "LOW"])
        return (
            f"   • Détail: {criticals} critiques, {mediums} moyennes, {lows} mineures."
        )

    def _format_violations_group(
        self, group_name: str, violations: List[Violation]
    ) -> List[str]:
        """Formate une section du rapport pour un groupe de violations."""
        lines = [f"\n❌ VIOLATIONS {group_name} ({len(violations)}):"]
        for i, v in enumerate(violations, 1):
            lines.extend(
                [
                    f"\n   {i}. {v.law.name} (ID: {v.law.id})",
                    f"      📁 Fichier: {v.file_path}",
                    f"      📍 Ligne: {v.line_number}",
                    f"      📝 Message: {v.message}",
                ]
            )
            if v.suggestion:
                lines.append(f"      💡 Suggestion: {v.suggestion}")
        return lines

    def _generate_success_report(self) -> str:
        """Génère un message de succès en cas d'absence de violations."""
        return (
            "\n✅ AUDIT CONSTITUTIONNEL RÉUSSI\n"
            "===================================\n"
            "🏛️  CONFORMITÉ TOTALE À iaGOD.json\n"
            "   Aucune violation constitutionnelle détectée.\n"
        )

    def _get_footer(self) -> List[str]:
        """Retourne le pied de page standard pour les rapports."""
        return [
            "\n💡 RECOMMANDATIONS:",
            "-" * 20,
            "1. Corriger les violations CRITIQUES en priorité.",
            "2. Consulter iaGOD.json pour les directives complètes.",
            "\n📚 RESSOURCES:",
            "   • Constitution: iaGOD.json",
            "   • Aide: python run_agi_audit.py --help",
        ]
