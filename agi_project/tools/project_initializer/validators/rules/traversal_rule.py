#!/usr/bin/env python3
"""
Traversal Rule - Règle de Validation Anti-Path Traversal
=========================================================

Rôle Fondamental (Conforme AGI.md) :
- Fournir une fonction unique et spécialisée pour détecter le "path traversal".
- Isoler cette logique de sécurité critique pour la clarté et la maintenabilité.
- Respecter la directive des 200 lignes.

Version : 1.0
Date : 18 Septembre 2025
"""

from pathlib import Path


def check_path_traversal(original_path: Path, logger) -> bool:
    """
    Vérifie l'absence de séquences de path traversal ('..') dans un chemin.

    Cette règle est une fonction pure qui ne dépend d'aucun état externe
    autre que le logger pour la traçabilité des violations.

    Args:
        original_path (Path): Le chemin original fourni par l'utilisateur.
        logger: L'instance du logger AGI pour rapporter les erreurs.

    Returns:
        bool: True si le chemin est sûr, False en cas de traversal détecté.
    """
    try:
        # La détection se fait sur la représentation en chaîne du chemin original,
        # avant toute résolution, pour attraper l'intention de traversal.
        if ".." in str(original_path):
            logger.error(
                f"❌ Path traversal détecté : la séquence '..' est interdite dans le chemin '{original_path}'"
            )
            return False

        return True

    except Exception as e:
        logger.error(
            f"❌ Erreur inattendue lors de la vérification du path traversal pour '{original_path}': {e}"
        )
        return False
