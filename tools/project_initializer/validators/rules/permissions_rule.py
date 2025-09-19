#!/usr/bin/env python3
"""
Permissions Rule - Règle de Validation des Permissions de Fichiers
===================================================================

Rôle Fondamental (Conforme AGI.md) :
- Vérifier les permissions de lecture et d'écriture sur le système de fichiers.
- Gérer les cas où les chemins ou leurs répertoires parents n'existent pas encore.
- Isoler les interactions avec le module `os` pour une meilleure testabilité.

Version : 1.0
Date : 18 Septembre 2025
"""

import os
from pathlib import Path
from typing import Union


def validate_write_permissions(path_input: Union[str, Path], logger) -> bool:
    """
    Valide que le processus a les permissions d'écriture pour un chemin donné.

    Si le chemin n'existe pas, la fonction remonte l'arborescence pour
    vérifier les permissions sur le premier parent existant.

    Args:
        path_input (Union[str, Path]): Le chemin (fichier ou répertoire) à vérifier.
        logger: L'instance du logger AGI pour rapporter les erreurs.

    Returns:
        bool: True si les permissions d'écriture sont suffisantes, False sinon.
    """
    try:
        path = Path(path_input)

        # Si le chemin existe, on vérifie directement ses permissions.
        if path.exists():
            if not os.access(path, os.W_OK):
                logger.error(
                    f"❌ Permissions d'écriture insuffisantes sur le chemin existant : {path}"
                )
                return False
            return True

        # Si le chemin n'existe pas, on vérifie le parent le plus proche.
        parent = path.parent
        while not parent.exists() and parent != parent.parent:
            parent = parent.parent

        if not parent.exists():
            logger.error(
                f"❌ Aucun répertoire parent accessible n'a été trouvé pour le chemin : {path}"
            )
            return False

        if not os.access(parent, os.W_OK):
            logger.error(
                f"❌ Permissions d'écriture insuffisantes sur le répertoire parent : {parent}"
            )
            return False

        logger.debug(
            f"Permissions d'écriture validées pour le chemin (via parent) : {path}"
        )
        return True

    except Exception as e:
        logger.error(
            f"❌ Erreur inattendue lors de la validation des permissions d'écriture pour '{path_input}': {e}"
        )
        return False


def validate_read_permissions(path_input: Union[str, Path], logger) -> bool:
    """
    Valide que le processus a les permissions de lecture pour un chemin donné.

    Si le chemin n'existe pas, la validation est considérée comme réussie
    car il n'y a rien à lire.

    Args:
        path_input (Union[str, Path]): Le chemin (fichier ou répertoire) à vérifier.
        logger: L'instance du logger AGI pour rapporter les erreurs.

    Returns:
        bool: True si les permissions de lecture sont suffisantes ou si le fichier
              n'existe pas, False sinon.
    """
    try:
        path = Path(path_input)

        if not path.exists():
            logger.debug(
                f"Chemin inexistant, la validation de lecture passe par défaut : {path}"
            )
            return True  # On ne peut pas échouer à lire un fichier qui n'existe pas.

        if not os.access(path, os.R_OK):
            logger.error(
                f"❌ Permissions de lecture insuffisantes sur le chemin : {path}"
            )
            return False

        logger.debug(f"Permissions de lecture validées pour le chemin : {path}")
        return True

    except Exception as e:
        logger.error(
            f"❌ Erreur inattendue lors de la validation des permissions de lecture pour '{path_input}': {e}"
        )
        return False
