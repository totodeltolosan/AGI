#!/usr/bin/env python3
"""
Orchestrateur Principal du Système d'Audit de Conformité AGI
Module central respectant scrupuleusement la directive des 200 lignes

Responsabilité unique : Coordination des modules d'audit spécialisés
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Imports des modules d'audit spécialisés
from tools.compliance_audit_system.detectors import environment_detector, project_detector
from tools.compliance_audit_system.validators import line_validator, syntax_validator, security_validator
from tools.compliance_audit_system.analyzers import ast_analyzer, pattern_analyzer, dependency_analyzer
from tools.compliance_audit_system.reporters import console_reporter, json_reporter, synthesis_reporter
from tools.compliance_audit_system.utils import logger_factory, config_manager


@dataclass
class AuditConfig:
    """Configuration d'audit centralisée"""

    target_dir: Path
    output_dir: Optional[Path] = None
    verbose: bool = False
    full_audit: bool = False
    export_formats: List[str] = None


class AuditOrchestrator:
    """Orchestrateur principal - Coordination des audits AGI"""

    def __init__(self, config: AuditConfig):
        self.config = config
        self.logger = logger_factory.create_logger("orchestrator", config.verbose)
        self.results = {}

    def execute_audit_pipeline(self) -> Dict:
        """Pipeline principal d'audit en 5 phases"""
        self.logger.info("🏛️ Début de l'audit constitutionnel AGI")

        # Phase 1: Détection et validation environnement
        env_status = self._detect_environment()
        if not env_status["valid"]:
            return self._create_error_result("Environnement invalide")

        # Phase 2: Validation structurelle de base
        basic_validation = self._execute_basic_validation()

        # Phase 3: Analyse constitutionnelle approfondie (si demandée)
        constitutional_analysis = {}
        if self.config.full_audit:
            constitutional_analysis = self._execute_constitutional_analysis()

        # Phase 4: Génération des rapports
        reports = self._generate_reports(basic_validation, constitutional_analysis)

        # Phase 5: Synthèse et recommandations
        synthesis = self._create_synthesis(basic_validation, constitutional_analysis)

        return {
            "status": "completed",
            "environment": env_status,
            "basic_validation": basic_validation,
            "constitutional_analysis": constitutional_analysis,
            "reports": reports,
            "synthesis": synthesis,
            "timestamp": datetime.now().isoformat(),
        }

    def _detect_environment(self) -> Dict:
        """Détection et validation de l'environnement"""
        self.logger.info("🔍 Détection de l'environnement...")

        # Délégation aux détecteurs spécialisés
        env_detector = environment_detector.EnvironmentDetector()
        project_info = project_detector.ProjectDetector().detect_agi_project(
            self.config.target_dir
        )

        return {
            "valid": env_detector.validate_python_environment()
            and project_info["valid"],
            "python_version": env_detector.get_python_version(),
            "project_root": str(project_info.get("root_path", "")),
            "agi_files_detected": project_info.get("agi_files", []),
        }

    def _execute_basic_validation(self) -> Dict:
        """Validation de base : lignes, syntaxe, sécurité"""
        self.logger.info("📏 Validation structurelle de base...")

        results = {}

        # Validation des 200 lignes
        line_val = line_validator.LineValidator(max_lines=200)
        results["line_compliance"] = line_val.validate_directory(self.config.target_dir)

        # Validation syntaxique
        syntax_val = syntax_validator.SyntaxValidator()
        results["syntax_check"] = syntax_val.validate_directory(self.config.target_dir)

        # Validation sécuritaire de base
        security_val = security_validator.SecurityValidator()
        results["security_scan"] = security_val.scan_directory(self.config.target_dir)

        return results

    def _execute_constitutional_analysis(self) -> Dict:
        """Analyse constitutionnelle approfondie des 474 directives"""
        self.logger.info("🏛️ Analyse constitutionnelle approfondie...")

        results = {}

        # Analyse AST approfondie
        ast_anal = ast_analyzer.ASTAnalyzer()
        results["ast_analysis"] = ast_anal.analyze_directory(self.config.target_dir)

        # Analyse des patterns architecturaux
        pattern_anal = pattern_analyzer.PatternAnalyzer()
        results["pattern_analysis"] = pattern_anal.analyze_directory(
            self.config.target_dir
        )

        # Analyse des dépendances et couplage
        dep_anal = dependency_analyzer.DependencyAnalyzer()
        results["dependency_analysis"] = dep_anal.analyze_directory(
            self.config.target_dir
        )

        return results

    def _generate_reports(
        self, basic_results: Dict, constitutional_results: Dict
    ) -> Dict:
        """Génération des rapports multi-formats"""
        self.logger.info("📊 Génération des rapports...")

        reports = {}
        all_results = {**basic_results, **constitutional_results}

        # Rapport console (toujours généré)
        console_rep = console_reporter.ConsoleReporter()
        reports["console"] = console_rep.generate_report(all_results)

        # Rapport JSON (si output_dir spécifié)
        if self.config.output_dir:
            json_rep = json_reporter.JSONReporter(self.config.output_dir)
            reports["json_file"] = json_rep.export_report(all_results)

            # Rapport de synthèse Markdown
            synth_rep = synthesis_reporter.SynthesisReporter(self.config.output_dir)
            reports["synthesis_file"] = synth_rep.create_synthesis(all_results)

        return reports

    def _create_synthesis(
        self, basic_results: Dict, constitutional_results: Dict
    ) -> Dict:
        """Création de la synthèse et recommandations"""

        # Calcul des métriques globales
        total_files = self._count_total_files(basic_results)
        violations = self._count_violations(basic_results, constitutional_results)

        conformity_rate = (
            ((total_files - violations) / total_files * 100) if total_files > 0 else 0
        )

        # Détermination du verdict
        if violations == 0:
            verdict = "✅ CONFORMITÉ TOTALE"
            status = "CONFORME"
        elif violations <= 3:
            verdict = "⚠️ CONFORMITÉ PARTIELLE"
            status = "PARTIELLEMENT_CONFORME"
        else:
            verdict = "❌ NON-CONFORMITÉ CRITIQUE"
            status = "NON_CONFORME"

        return {
            "verdict": verdict,
            "status": status,
            "conformity_rate": round(conformity_rate, 1),
            "total_files": total_files,
            "violations": violations,
            "priority_actions": self._generate_priority_actions(basic_results),
        }

    def _count_total_files(self, basic_results: Dict) -> int:
        """Compte le nombre total de fichiers analysés"""
        if "line_compliance" in basic_results:
            return len(basic_results["line_compliance"].get("results", []))
        return 0

    def _count_violations(
        self, basic_results: Dict, constitutional_results: Dict
    ) -> int:
        """Compte le nombre total de violations"""
        violations = 0

        # Violations de lignes
        if "line_compliance" in basic_results:
            line_violations = [
                r
                for r in basic_results["line_compliance"].get("results", [])
                if r.get("status") == "VIOLATION"
            ]
            violations += len(line_violations)

        # Violations syntaxiques
        if "syntax_check" in basic_results:
            syntax_errors = basic_results["syntax_check"].get("errors", [])
            violations += len(syntax_errors)

        return violations

    def _generate_priority_actions(self, basic_results: Dict) -> List[str]:
        """Génère la liste des actions prioritaires"""
        actions = []

        # Actions basées sur les violations de lignes
        if "line_compliance" in basic_results:
            line_violations = [
                r
                for r in basic_results["line_compliance"].get("results", [])
                if r.get("status") == "VIOLATION"
            ]
            if line_violations:
                # Tri par excès décroissant
                sorted_violations = sorted(
                    line_violations, key=lambda x: x.get("excess", 0), reverse=True
                )
                for violation in sorted_violations[:3]:  # Top 3
                    filename = Path(violation["file_path"]).name
                    actions.append(
                        f"Refactoriser {filename} ({violation['excess']} lignes en excès)"
                    )

        return actions

    def _create_error_result(self, error_message: str) -> Dict:
        """Crée un résultat d'erreur standardisé"""
        return {
            "status": "error",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Point d'entrée principal - Interface en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Orchestrateur d'Audit Constitutionnel AGI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--target", type=str, required=True, help="Répertoire à auditer"
    )
    parser.add_argument(
        "--output", type=str, help="Répertoire de sortie pour les rapports"
    )
    parser.add_argument(
        "--full-audit",
        action="store_true",
        help="Audit constitutionnel complet (474 directives)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")

    args = parser.parse_args()

    # Configuration de l'audit
    config = AuditConfig(
        target_dir=Path(args.target),
        output_dir=Path(args.output) if args.output else None,
        verbose=args.verbose,
        full_audit=args.full_audit,
    )

    # Validation de la configuration
    if not config.target_dir.exists():
        print(f"❌ Répertoire cible inexistant : {config.target_dir}")
        sys.exit(1)

    if config.output_dir:
        config.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Exécution de l'audit
        orchestrator = AuditOrchestrator(config)
        results = orchestrator.execute_audit_pipeline()

        # Affichage du rapport console
        if "reports" in results and "console" in results["reports"]:
            print(results["reports"]["console"])

        # Code de sortie basé sur le statut de conformité
        if results.get("status") == "completed":
            synthesis = results.get("synthesis", {})
            if synthesis.get("status") == "CONFORME":
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            sys.exit(2)

    except Exception as e:
        print(f"❌ Erreur lors de l'audit : {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
