#!/usr/bin/env python3
"""
Rapporteur JSON - Système d'Audit AGI
Responsabilité unique : Génération de rapports JSON structurés pour traitement automatisé
Respecte strictement la directive des 200 lignes
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


class JSONReporter:
    """Générateur de rapports JSON pour l'audit AGI"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_report(self, audit_results: Dict) -> str:
        """Exporte le rapport d'audit complet en JSON"""

        # Structure du rapport JSON
        json_report = {
            "metadata": self._create_metadata(),
            "summary": self._create_summary(audit_results),
            "detailed_results": self._structure_detailed_results(audit_results),
            "metrics": self._extract_metrics(audit_results),
            "recommendations": self._generate_recommendations(audit_results),
            "compliance_matrix": self._create_compliance_matrix(audit_results),
        }

        # Génération du nom de fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agi_audit_report_{timestamp}.json"
        output_file = self.output_dir / filename

        # Écriture du fichier JSON
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    json_report,
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=self._json_serializer,
                )

            return str(output_file)

        except Exception as e:
            raise Exception(f"Erreur lors de l'export JSON: {e}")

    def export_summary_json(self, audit_results: Dict) -> str:
        """Exporte un résumé JSON compact"""

        summary_report = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": self._create_summary(audit_results),
            "key_metrics": self._extract_key_metrics(audit_results),
            "compliance_status": self._determine_compliance_status(audit_results),
        }

        # Fichier de résumé
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agi_audit_summary_{timestamp}.json"
        output_file = self.output_dir / filename

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                summary_report,
                f,
                indent=2,
                ensure_ascii=False,
                default=self._json_serializer,
            )

        return str(output_file)

    def _create_metadata(self) -> Dict:
        """Crée les métadonnées du rapport"""
        return {
            "report_id": str(uuid.uuid4()),
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            "audit_system_version": "2.0.0",
            "schema_version": "1.0",
            "generator": "AGI Compliance Audit System - Modular Architecture",
            "conformity_standard": "AGI.md Constitutional Directives",
        }

    def _create_summary(self, audit_results: Dict) -> Dict:
        """Crée le résumé exécutif"""
        total_files = self._count_total_files(audit_results)
        total_violations = self._count_total_violations(audit_results)
        compliance_rate = self._calculate_compliance_rate(audit_results)

        return {
            "total_files_analyzed": total_files,
            "total_violations_detected": total_violations,
            "overall_compliance_rate": round(compliance_rate, 2),
            "critical_issues_count": self._count_critical_issues(audit_results),
            "audit_completion_status": "completed",
            "primary_verdict": self._determine_primary_verdict(
                compliance_rate, total_violations
            ),
        }

    def _structure_detailed_results(self, audit_results: Dict) -> Dict:
        """Structure les résultats détaillés"""
        detailed = {}

        # Résultats de conformité des lignes
        if "line_compliance" in audit_results:
            detailed["line_compliance"] = self._format_line_compliance(
                audit_results["line_compliance"]
            )

        # Résultats de validation syntaxique
        if "syntax_check" in audit_results:
            detailed["syntax_validation"] = self._format_syntax_results(
                audit_results["syntax_check"]
            )

        # Résultats de sécurité
        if "security_scan" in audit_results:
            detailed["security_analysis"] = self._format_security_results(
                audit_results["security_scan"]
            )

        # Résultats d'analyse AST
        if "ast_analysis" in audit_results:
            detailed["ast_analysis"] = self._format_ast_results(
                audit_results["ast_analysis"]
            )

        # Résultats d'analyse des patterns
        if "pattern_analysis" in audit_results:
            detailed["pattern_analysis"] = self._format_pattern_results(
                audit_results["pattern_analysis"]
            )

        return detailed

    def _extract_metrics(self, audit_results: Dict) -> Dict:
        """Extrait toutes les métriques quantifiables"""
        metrics = {
            "file_metrics": {},
            "quality_metrics": {},
            "compliance_metrics": {},
            "complexity_metrics": {},
        }

        # Métriques de fichiers
        if "line_compliance" in audit_results:
            line_results = audit_results["line_compliance"]
            if "results" in line_results:
                violations = [
                    r for r in line_results["results"] if r.get("status") == "VIOLATION"
                ]
                metrics["file_metrics"]["line_violations"] = len(violations)
                metrics["file_metrics"]["average_excess_lines"] = (
                    self._calculate_average_excess(violations)
                )

        # Métriques de qualité
        if "syntax_check" in audit_results:
            syntax_results = audit_results["syntax_check"]
            metrics["quality_metrics"]["syntax_error_count"] = len(
                syntax_results.get("syntax_errors", [])
            )
            metrics["quality_metrics"]["syntax_validation_rate"] = syntax_results.get(
                "validation_rate", 0
            )

        return metrics

    def _generate_recommendations(self, audit_results: Dict) -> List[Dict]:
        """Génère des recommandations structurées"""
        recommendations = []

        # Recommandations basées sur les violations de lignes
        if "line_compliance" in audit_results:
            line_recs = self._generate_line_recommendations(
                audit_results["line_compliance"]
            )
            recommendations.extend(line_recs)

        # Recommandations syntaxiques
        if "syntax_check" in audit_results:
            syntax_recs = self._generate_syntax_recommendations(
                audit_results["syntax_check"]
            )
            recommendations.extend(syntax_recs)

        # Recommandations de sécurité
        if "security_scan" in audit_results:
            security_recs = self._generate_security_recommendations(
                audit_results["security_scan"]
            )
            recommendations.extend(security_recs)

        return recommendations

    def _create_compliance_matrix(self, audit_results: Dict) -> Dict:
        """Crée une matrice de conformité aux directives AGI"""
        matrix = {
            "line_limit_directive": {
                "directive_id": "ARCH-001",
                "description": "200 lines maximum per file",
                "compliance_status": "unknown",
                "violation_count": 0,
            },
            "modularity_directive": {
                "directive_id": "MOD-001",
                "description": "Single responsibility principle",
                "compliance_status": "unknown",
                "violation_count": 0,
            },
            "security_directive": {
                "directive_id": "SEC-001",
                "description": "Security by design",
                "compliance_status": "unknown",
                "violation_count": 0,
            },
        }

        # Mise à jour basée sur les résultats
        if "line_compliance" in audit_results:
            line_results = audit_results["line_compliance"]
            if "results" in line_results:
                violations = [
                    r for r in line_results["results"] if r.get("status") == "VIOLATION"
                ]
                matrix["line_limit_directive"]["violation_count"] = len(violations)
                matrix["line_limit_directive"]["compliance_status"] = (
                    "compliant" if len(violations) == 0 else "non_compliant"
                )

        return matrix

    def _format_line_compliance(self, line_results: Dict) -> Dict:
        """Formate les résultats de conformité des lignes"""
        if "results" not in line_results:
            return {}

        violations = [
            r for r in line_results["results"] if r.get("status") == "VIOLATION"
        ]
        conformant = [
            r for r in line_results["results"] if r.get("status") == "CONFORME"
        ]

        return {
            "total_files": len(line_results["results"]),
            "compliant_files": len(conformant),
            "violation_files": len(violations),
            "worst_violation": (
                max(violations, key=lambda x: x.get("excess", 0))
                if violations
                else None
            ),
            "violations_details": violations[:10],  # Limite à 10 pour JSON
        }

    def _format_syntax_results(self, syntax_results: Dict) -> Dict:
        """Formate les résultats syntaxiques"""
        return {
            "total_files": syntax_results.get("total_files", 0),
            "valid_files": syntax_results.get("valid_files", 0),
            "validation_rate": syntax_results.get("validation_rate", 0),
            "syntax_errors": syntax_results.get("syntax_errors", [])[
                :5
            ],  # Top 5 erreurs
            "quality_issues_count": len(syntax_results.get("quality_issues", [])),
        }

    def _count_total_files(self, audit_results: Dict) -> int:
        """Compte le nombre total de fichiers"""
        max_count = 0

        if (
            "line_compliance" in audit_results
            and "results" in audit_results["line_compliance"]
        ):
            max_count = max(max_count, len(audit_results["line_compliance"]["results"]))

        if "syntax_check" in audit_results:
            max_count = max(
                max_count, audit_results["syntax_check"].get("total_files", 0)
            )

        return max_count

    def _count_total_violations(self, audit_results: Dict) -> int:
        """Compte le nombre total de violations"""
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

        return violations

    def _calculate_compliance_rate(self, audit_results: Dict) -> float:
        """Calcule le taux de conformité global"""
        total_files = self._count_total_files(audit_results)
        total_violations = self._count_total_violations(audit_results)

        if total_files == 0:
            return 100.0

        # Approximation du taux de conformité
        affected_files = min(total_violations, total_files)
        compliant_files = total_files - affected_files

        return (compliant_files / total_files) * 100

    def _count_critical_issues(self, audit_results: Dict) -> int:
        """Compte les problèmes critiques"""
        critical_count = 0

        if "security_scan" in audit_results:
            security_issues = audit_results["security_scan"].get("security_issues", [])
            critical_count += len(
                [i for i in security_issues if i.get("severity") == "CRITICAL"]
            )

        return critical_count

    def _determine_primary_verdict(
        self, compliance_rate: float, total_violations: int
    ) -> str:
        """Détermine le verdict principal"""
        if compliance_rate >= 95 and total_violations == 0:
            return "EXCELLENT_COMPLIANCE"
        elif compliance_rate >= 80:
            return "ACCEPTABLE_COMPLIANCE"
        elif compliance_rate >= 60:
            return "PARTIAL_COMPLIANCE"
        else:
            return "CRITICAL_NON_COMPLIANCE"

    def _json_serializer(self, obj):
        """Sérialiseur JSON personnalisé pour les objets non-standard"""
        if isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, "isoformat"):
            return obj.isoformat()
        else:
            return str(obj)


# Fonctions utilitaires
def quick_json_export(audit_results: Dict, output_dir: Path) -> str:
    """Export JSON rapide - fonction utilitaire"""
    reporter = JSONReporter(output_dir)
    return reporter.export_report(audit_results)


def export_summary_only(audit_results: Dict, output_dir: Path) -> str:
    """Export résumé uniquement - fonction utilitaire"""
    reporter = JSONReporter(output_dir)
    return reporter.export_summary_json(audit_results)


if __name__ == "__main__":
    # Test du rapporteur JSON
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
            "validation_rate": 50.0,
            "syntax_errors": [],
        },
    }

    # Test avec répertoire temporaire
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        reporter = JSONReporter(output_dir)
        json_file = reporter.export_report(test_results)
        print(f"Rapport JSON généré: {json_file}")
