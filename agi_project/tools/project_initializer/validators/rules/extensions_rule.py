#!/usr/bin/env python3
"""
Extensions Rule - Règle de Validation des Extensions de Fichiers
=================================================================

Rôle Fondamental (Conforme AGI.md) :
- Empêcher la génération de fichiers avec des extensions potentiellement dangereuses.
- Maintenir une liste claire et modifiable de ces extensions.
- Isoler cette règle de sécurité pour une meilleure auditabilité.

Version : 1.0
Date : 18 Septembre 2025
"""

from pathlib import Path
from typing import Set

# Ensemble des extensions de fichiers considérées comme dangereuses ou non souhaitées
# pour la génération de squelette. Utiliser un Set pour une recherche en O(1).
DANGEROUS_EXTENSIONS: Set[str] = {
    ".exe",
    ".bat",
    ".cmd",
    ".sh",
    ".bash",
    ".ps1",
    ".vbs",
    ".scr",
    ".com",
    ".pif",
    ".jar",
    ".dll",
}


def check_dangerous_extensions(path: Path, logger) -> bool:
    """
    Vérifie que l'extension du fichier n'est pas dans la liste des extensions dangereuses.

    La vérification est insensible à la casse.

    Args:
        path (Path): Le chemin du fichier à vérifier.
        logger: L'instance du logger AGI pour rapporter les erreurs.

    Returns:
        bool: True si l'extension est sûre, False sinon.
    """
    try:
        # Obtenir le suffixe (extension) du fichier en minuscules
        suffix = path.suffix.lower()

        if suffix in DANGEROUS_EXTENSIONS:
            logger.error(
                f"❌ Extension dangereuse détectée : '{suffix}' dans le chemin '{path}'"
            )
            return False

        return True

    except Exception as e:
        logger.error(
            f"❌ Erreur inattendue lors de la vérification de l'extension pour '{path}': {e}"
        )
        return False
