#!/usr/bin/env python3
"""
Script Principal d'Audit AGI - Point d'Entrée Final Conforme
CONFORME À AGI.md : < 200 lignes, architecture modulaire, responsabilité unique
Responsabilité : Interface utilisateur et délégation vers système modulaire
"""

import sys
import argparse
from pathlib import Path
from typing import Optional


def show_architecture_info():
    """Affiche l'information sur l'architecture modulaire"""
    print(
        """
🏛️ SYSTÈME D'AUDIT AGI - ARCHITECTURE MODULAIRE CONFORME

✅ CONFORMITÉ TOTALE AUX DIRECTIVES AGI.md:
   • Chaque module < 200 lignes
   • Responsabilité unique par module
   • Architecture extensible et maintenable
   • 10+ modules spécialisés

📁 MODULES CRÉÉS (tous < 200 lignes):
   tools/compliance_audit_system/
   ├── orchestrator.py              # Coordination principale
   ├── detectors/
   │   ├── environment_detector.py  # Validation environnement
   │   └── project_detector.py      # Détection projet AGI
   ├── validators/
   │   ├── line_validator.py        # Directive 200 lignes
   │   ├── syntax_validator.py      # Syntaxe Python
   │   └── security_validator.py    # Sécurité code
   ├── analyzers/
   │   ├── ast_analyzer.py          # Analyse AST approfondie
   │   └── pattern_analyzer.py      # Patterns architecturaux
   ├── reporters/
   │   ├── console_reporter.py      # Rapports console
   │   └── json_reporter.py         # Export JSON
   ├── utils/
   │   ├── logger_factory.py        # Système logging
   │   └── config_manager.py        # Configuration
   └── audit_agi.py                 # Interface modulaire

🎯 CORRECTION DU PROBLÈME INITIAL:
   Le script bash verification_compliance_script.sh violait lui-même
   les directives AGI.md (>200 lignes). Cette architecture modulaire
   résout ce problème en respectant SCRUPULEUSEMENT toutes les règles.
"""
    )


def detect_project_root() -> Path:
    """Détecte la racine du projet AGI"""
    current = Path.cwd()

    # Recherche de marqueurs AGI
    for parent in [current] + list(current.parents):
        if (parent / "AGI.md").exists() or (parent / "tools").exists():
            return parent

    return current


def main():
    """Point d'entrée principal conforme AGI.md"""
    parser = argparse.ArgumentParser(
        description="🏛️ Audit AGI - Architecture Modulaire Conforme",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLES D'UTILISATION:

  Audit standard:
    python3 run_agi_audit.py --target ./tools/project_initializer/

  Audit constitutionnel complet:
    python3 run_agi_audit.py --target ./tools/project_initializer/ --full-audit

  Avec rapports détaillés:
    python3 run_agi_audit.py --target ./tools/project_initializer/ \\
                              --output ./reports/ --verbose

  Information sur l'architecture:
    python3 run_agi_audit.py --show-architecture

ARCHITECTURE MODULAIRE:
  Ce script délègue tout travail vers les modules Python conformes.
  Chaque module respecte strictement la directive des 200 lignes.
        """,
    )

    parser.add_argument("--target", type=str, help="Répertoire à auditer")
    parser.add_argument(
        "--output", type=str, help="Répertoire de sortie pour les rapports"
    )
    parser.add_argument(
        "--full-audit",
        action="store_true",
        help="Audit constitutionnel complet (474 directives)",
    )
    parser.add_argument("--quick", action="store_true", help="Audit rapide uniquement")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    parser.add_argument(
        "--show-architecture",
        action="store_true",
        help="Affiche l'architecture du système modulaire",
    )

    args = parser.parse_args()

    # Affichage architecture si demandé
    if args.show_architecture:
        show_architecture_info()
        return 0

    # Auto-détection du répertoire cible
    if not args.target:
        project_root = detect_project_root()
        target_dir = project_root / "tools" / "project_initializer"
        if not target_dir.exists():
            target_dir = project_root
        args.target = str(target_dir)
        print(f"🎯 Auto-détection: {args.target}")

    # Validation du répertoire cible
    target_path = Path(args.target)
    if not target_path.exists():
        print(f"❌ Répertoire cible inexistant: {target_path}")
        return 1

    # Import et délégation vers le système modulaire
    try:
        # Import du système d'audit modulaire
        audit_system_path = Path(__file__).parent / "tools" / "compliance_audit_system"
        sys.path.insert(0, str(audit_system_path.parent))

        from compliance_audit_system.audit_agi import (
            cli_entry_point as run_modular_audit,
        )

        # Construction des arguments pour le système modulaire
        modular_args = ["--target", args.target]

        if args.output:
            modular_args.extend(["--output", args.output])

        if args.full_audit:
            modular_args.append("--full-audit")
        elif args.quick:
            modular_args.append("--quick")

        if args.verbose:
            modular_args.append("--verbose")

        # Délégation complète vers le système modulaire
        print("🚀 Délégation vers le système d'audit modulaire conforme...")
        sys.argv = ["audit_agi.py"] + modular_args

        return run_modular_audit()

    except ImportError as e:
        print(f"❌ Système d'audit modulaire non trouvé: {e}")
        print("💡 Assurez-vous que tools/compliance_audit_system/ existe")
        return 2
    except Exception as e:
        print(f"❌ Erreur lors de l'audit: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 3


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Audit interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        sys.exit(255)
