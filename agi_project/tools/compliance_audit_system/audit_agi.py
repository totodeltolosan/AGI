#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_audit_system/audit_agi.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""
Script Principal d'Audit AGI - Point d'Entrée Unifié
Responsabilité unique : Interface ligne de commande et coordination de haut niveau
Respecte strictement la directive des 200 lignes - CONFORME AGI.md
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Import de l'orchestrateur principal
from .orchestrator import AuditOrchestrator, AuditConfig


def create_argument_parser() -> argparse.ArgumentParser:
    """Crée et configure l'analyseur d'arguments"""
    parser = argparse.ArgumentParser(
        description="🏛️ Système d'Audit Constitutionnel AGI - Version Modulaire",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLES D'UTILISATION:

  Audit de base:
    python3 audit_agi.py --target ./tools/project_initializer/

  Audit constitutionnel complet:
    python3 audit_agi.py --target ./tools/project_initializer/ --full-audit

  Génération de rapports:
    python3 audit_agi.py --target ./tools/project_initializer/ \\
                         --output ./reports/ --full-audit --verbose

  Vérification rapide:
    python3 audit_agi.py --target ./tools/project_initializer/ --quick

ARCHITECTURE MODULAIRE:
  Ce script coordonne 10+ modules spécialisés, chacun respectant
  scrupuleusement la directive des 200 lignes d'AGI.md:

  • detectors/     : Détection environnement et projet
  • validators/    : Validation lignes, syntaxe, sécurité
  • analyzers/     : Analyse AST, patterns, dépendances
  • reporters/     : Rapports console, JSON, synthèse
  • utils/         : Utilitaires logging et configuration

CONFORMITÉ:
  ✅ Chaque module < 200 lignes
  ✅ Responsabilité unique par module
  ✅ Architecture extensible et maintenable
  ✅ Respect total des directives AGI.md
        """,
    )

    # Arguments principaux
    parser.add_argument(
        "--target", type=str, required=True, help="Répertoire à auditer (requis)"
    )

    parser.add_argument(
        "--output", type=str, help="Répertoire de sortie pour les rapports"
    )

    # Modes d'audit
    audit_group = parser.add_mutually_exclusive_group()
    audit_group.add_argument(
        "--quick",
        action="store_true",
        help="Audit rapide (lignes + syntaxe uniquement)",
    )
    audit_group.add_argument(
        "--full-audit",
        action="store_true",
        help="Audit constitutionnel complet (474 directives)",
    )

    # Options de sortie
    parser.add_argument(
        "--format",
        choices=["console", "json", "all"],
        default="console",
        help="Format de rapport",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mode verbeux avec détails d'exécution",
    )

    parser.add_argument(
        "--no-color", action="store_true", help="Désactive les couleurs dans la sortie"
    )

    # Validation et aide
    parser.add_argument(
        "--validate-environment",
        action="store_true",
        help="Valide uniquement l'environnement d'audit",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Système d'Audit AGI v2.0 - Architecture Modulaire",
    )

    return parser


def validate_arguments(args) -> Optional[str]:
    """Valide les arguments et retourne un message d'erreur si nécessaire"""

    # Validation du répertoire cible
    target_path = Path(args.target)
    if not target_path.exists():
        return f"❌ Répertoire cible inexistant: {target_path}"

    if not target_path.is_dir():
        return f"❌ Le chemin cible n'est pas un répertoire: {target_path}"

    # Validation du répertoire de sortie
    if args.output:
        output_path = Path(args.output)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return f"❌ Impossible de créer le répertoire de sortie: {e}"

    # Validation des options combinées
    if args.quick and args.format == "json":
        return "⚠️ L'audit rapide ne génère pas de JSON détaillé"

    return None


def handle_environment_validation() -> int:
    """Gère la validation d'environnement uniquement"""
    print("🔍 Validation de l'environnement d'audit AGI...")

    try:
        from .detectors.environment_detector import EnvironmentDetector

        detector = EnvironmentDetector()

        if detector.validate_python_environment():
            print("✅ Environnement Python valide pour l'audit AGI")

            env_info = detector.get_environment_info()
            print(f"🐍 Python: {env_info['python_version']}")
            print(f"🖥️ Platform: {env_info['platform']}")

            capabilities = detector.detect_project_capabilities()
            print(
                f"⚙️ Capacités: {sum(capabilities.values())}/{len(capabilities)} disponibles"
            )

            return 0
        else:
            print("❌ Environnement invalide pour l'audit AGI")

            issues = detector.diagnose_environment_issues()
            for issue, description in issues.items():
                print(f"   {issue}: {description}")

            return 1

    except Exception as e:
        print(f"❌ Erreur lors de la validation: {e}")
        return 2


def execute_audit(args) -> int:
    """Exécute l'audit principal"""

    # Configuration de l'audit
    config = AuditConfig(
        target_dir=Path(args.target),
        output_dir=Path(args.output) if args.output else None,
        verbose=args.verbose,
        full_audit=args.full_audit or not args.quick,
    )

    if args.verbose:
        print(f"🎯 Configuration d'audit:")
        print(f"   Cible: {config.target_dir}")
        print(f"   Mode: {'Complet' if config.full_audit else 'Standard'}")
        print(f"   Sortie: {config.output_dir or 'Console uniquement'}")

    try:
        # Initialisation et exécution de l'orchestrateur
        orchestrator = AuditOrchestrator(config)
        results = orchestrator.execute_audit_pipeline()

        # Gestion des résultats
        if results.get("status") == "completed":

            # Affichage du rapport console
            if args.format in ["console", "all"] and "reports" in results:
                console_report = results["reports"].get("console", "")
                if console_report:
                    print(console_report)

            # Notification des fichiers générés
            if config.output_dir and "reports" in results:
                reports = results["reports"]
                if "json_file" in reports:
                    print(f"\n📄 Rapport JSON: {reports['json_file']}")
                if "synthesis_file" in reports:
                    print(f"📋 Synthèse: {reports['synthesis_file']}")

            # Code de sortie basé sur la conformité
            synthesis = results.get("synthesis", {})
            status = synthesis.get("status", "NON_CONFORME")

            if status == "CONFORME":
                return 0
            elif status == "PARTIELLEMENT_CONFORME":
                return 1
            else:
                return 2

        else:
            # Erreur lors de l'audit
            error_msg = results.get("error", "Erreur inconnue")
            print(f"❌ Échec de l'audit: {error_msg}")
            return 3

    except Exception as e:
        print(f"❌ Erreur critique lors de l'audit: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 4


def main() -> int:
    """Point d'entrée principal"""

    # Analyse des arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Validation des arguments
    validation_error = validate_arguments(args)
    if validation_error:
        print(validation_error)
        return 1

    # Gestion des modes spéciaux
    if args.validate_environment:
        return handle_environment_validation()

    # Exécution de l'audit principal
    return execute_audit(args)


def cli_entry_point():
    """Point d'entrée pour utilisation en ligne de commande"""
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Audit interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        sys.exit(255)


if __name__ == "__main__":
    cli_entry_point()
