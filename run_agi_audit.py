#!/usr/bin/env python3
"""
Script Principal d'Audit AGI - v2.1 (Architecture Conforme et Corrigée)
=======================================================================

CHEMIN: run_agi_audit.py

Rôle Fondamental (Conforme iaGOD.json) :
- Interface utilisateur CLI pour l'audit constitutionnel.
- Délégation à l'architecture modulaire et conforme du package `compliance`.
- Orchestrer le chargement, l'audit et le reporting.
- Respecter la directive < 200 lignes.
"""

import sys
import argparse
import logging
from pathlib import Path

# Import direct des modules spécifiques pour éviter les dépendances circulaires
from compliance.loader import ConstitutionLoader
from compliance.orchestrator import AuditOrchestrator
from compliance.reporter import AuditReporter


def setup_logging(verbose: bool = False):
    """Configure le système de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    """Point d'entrée principal orchestrant l'audit."""
    parser = argparse.ArgumentParser(
        description="🏛️ Audit AGI - Système Constitutionnel v2.1 (Conforme)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--target",
        type=str,
        default=".",
        help="Répertoire à auditer (défaut: répertoire courant)",
    )
    parser.add_argument(
        "--output", type=str, help="Fichier de sortie pour le rapport détaillé"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mode verbeux avec détails d'exécution",
    )

    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # 1. Charger la constitution
        logger.info("📜 Chargement de la constitution iaGOD.json...")
        loader = ConstitutionLoader()
        if not loader.load():
            logger.error("❌ Échec critique : impossible de charger la constitution.")
            return 1

        # 2. Initialiser l'orchestrateur avec les lois chargées
        logger.info("🔍 Initialisation de l'orchestrateur d'audit...")
        orchestrator = AuditOrchestrator(constitution=loader.get_all_laws())

        # 3. Exécuter l'audit
        target_path = Path(args.target)
        if not target_path.exists() or not target_path.is_dir():
            logger.error(f"❌ Répertoire cible invalide : {target_path}")
            return 1

        audit_context = orchestrator.run_audit(target_path)

        # 4. Générer et afficher les rapports
        reporter = AuditReporter()
        console_report = reporter.generate_console_report(audit_context)
        print(console_report)

        if args.output:
            reporter.save_report_to_file(audit_context, Path(args.output))

        # 5. Déterminer le code de sortie en fonction des violations
        if not audit_context.violations:
            return 0  # Succès

        if any(v.severity == "CRITICAL" for v in audit_context.violations):
            return 1  # Échec critique

        return 0  # Succès avec avertissements

    except Exception as e:
        logger.error(f"💥 Erreur fatale inattendue durant l'audit : {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 2


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Audit interrompu par l'utilisateur.")
        sys.exit(130)
