#!/usr/bin/env python3
"""
CLI Handler - Gestionnaire de la Ligne de Commande pour le Générateur AGI
=========================================================================

Rôle Fondamental (Conforme AGI.md) :
- Isoler la logique de gestion de l'interface en ligne de commande (CLI).
- Fournir des fonctions pour créer le parser d'arguments, configurer le logger
  et valider les entrées utilisateur.
- Permettre au point d'entrée principal de rester simple et focalisé.

Version : 1.0
Date : 18 Septembre 2025
"""

import argparse
from utils.agi_logger import AGILogger


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Crée et configure le parser d'arguments pour la CLI du générateur.
    """
    parser = argparse.ArgumentParser(
        description="Générateur de Squelette AGI - Conforme aux Directives AGI.md",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s --output ./mon_projet_agi
  %(prog)s -v --output ./mon_projet_agi --include compliance
  %(prog)s --debug --log-file ./gen.log --output ./test_agi --exclude plugins
""",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Répertoire de sortie pour le squelette AGI.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Active le logging détaillé."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Active le logging de débogage (très verbeux).",
    )
    parser.add_argument(
        "--log-file", type=str, help="Chemin du fichier où enregistrer les logs."
    )

    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument(
        "--exclude",
        nargs="+",
        default=[],
        help="Domaine(s) à exclure de la génération.",
    )
    filter_group.add_argument(
        "--include",
        nargs="+",
        default=[],
        help="N'inclure que le(s) domaine(s) spécifié(s).",
    )

    return parser


def configure_logger(args: argparse.Namespace) -> AGILogger:
    """
    Configure et retourne une instance de AGILogger basée sur les arguments de la CLI.
    """
    log_level = "DEBUG" if args.debug else ("VERBOSE" if args.verbose else "INFO")
    return AGILogger(level=log_level, log_file=args.log_file)


def validate_arguments(args: argparse.Namespace, logger: AGILogger) -> bool:
    """
    Valide la logique des arguments fournis. Actuellement, ne fait rien car
    argparse gère les contraintes (required, mutually_exclusive_group).
    """
    # La validation de base (required=True, add_mutually_exclusive_group) est gérée par argparse.
    # Des validations plus complexes pourraient être ajoutées ici.
    logger.debug("Arguments de la CLI parsés avec succès.")
    return True
