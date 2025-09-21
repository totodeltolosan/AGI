#!/usr/bin/env python3
"""
Project Initializer - Point d'Entrée CLI du Générateur AGI (Refactorisé)
=======================================================================

Rôle Fondamental (Conforme AGI.md) :
- Point d'entrée CLI minimaliste pour le générateur de squelette AGI.
- Orchestre les appels aux modules de gestion de la CLI et de génération.
- Respecte la directive des 200 lignes.

Version : 2.0 (Refactorisé)
Date : 18 Septembre 2025
"""

import sys
from pathlib import Path

# Configuration du chemin système pour les imports locaux
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from core.orchestrator import ProjectOrchestrator
    from core.cli_handler import (
        create_argument_parser,
        configure_logger,
        validate_arguments,
    )
except ImportError as e:
    print(
        f"❌ Erreur critique d'importation : {e}\nAssurez-vous que tous les modules sont présents."
    )
    sys.exit(1)


def main() -> None:
    """
    Point d'entrée principal qui orchestre le processus de génération.
    1. Parse les arguments de la CLI.
    2. Configure le logger.
    3. Valide les arguments.
    4. Lance la génération.
    """
    try:
        # Délégation de la gestion de la CLI
        parser = create_argument_parser()
        args = parser.parse_args()

        logger = configure_logger(args)

        if not validate_arguments(args, logger):
            sys.exit(1)

        # Correction de la Priorité #1 : Rendre le chemin vers AGI.md relatif et robuste
        try:
            # Le chemin est relatif au répertoire parent du répertoire 'tools'
            agi_md_path = current_dir.parent.parent / "AGI.md"
            if not agi_md_path.exists():
                logger.error(
                    f"Fichier constitutionnel 'AGI.md' introuvable au chemin attendu : {agi_md_path.resolve()}"
                )
                sys.exit(1)
        except Exception:
            logger.error("Impossible de déterminer le chemin vers AGI.md.")
            sys.exit(1)

        # Délégation de la génération
        orchestrator = ProjectOrchestrator(logger)
        success = orchestrator.generate_project(
            output_dir=args.output,
            agi_md_path=str(agi_md_path.resolve()),
            excluded_domains=args.exclude,
            included_domains=args.include,
        )

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\nOpération interrompue par l'utilisateur.")
        sys.exit(130)
    except Exception as e:
        # Capture les erreurs qui pourraient survenir avant que le logger ne soit initialisé
        print(f"❌ Une erreur critique et inattendue est survenue : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
