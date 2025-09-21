#!/usr/bin/env python3
"""
System Paths Rule - Règle de Validation des Chemins Système Critiques
======================================================================

Rôle Fondamental (Conforme AGI.md) :
- Protéger les répertoires système critiques contre toute écriture accidentelle.
- Maintenir une liste explicite de chemins autorisés et interdits.
- Isoler cette logique de validation pour garantir la sécurité du système hôte.

Version : 1.0
Date : 18 Septembre 2025
"""

from pathlib import Path
from typing import List

# Chemins système CRITIQUES dont l'accès en écriture est strictement interdit
FORBIDDEN_SYSTEM_PATHS: List[str] = [
    "/bin",
    "/sbin",
    "/usr/bin",
    "/usr/sbin",
    "/etc",
    "/sys",
    "/proc",
    "/dev",
    "/root",
    "/boot",
    "/lib",
    "/lib64",
]

# Chemins utilisateur dont l'accès est explicitement autorisé pour la génération
ALLOWED_USER_PATTERNS: List[str] = [
    "/home/",  # Répertoires utilisateur Linux
    "/Users/",  # Répertoires utilisateur macOS
    "/tmp/",  # Répertoire temporaire standard
    "/opt/",  # Applications optionnelles
    "/var/tmp/",  # Autre répertoire temporaire
]


def check_critical_system_paths(abs_path: Path, logger) -> bool:
    """
    Vérifie que le chemin n'accède pas à un répertoire système critique.

    La logique est la suivante :
    1. Si le chemin est dans une zone explicitement autorisée, il est validé.
    2. Sinon, si le chemin est dans une zone explicitement interdite, il est rejeté.
    3. Si le chemin n'est dans aucune de ces zones (ex: /mnt/data), il est autorisé
       par défaut pour plus de flexibilité.

    Args:
        abs_path (Path): Le chemin absolu et résolu à vérifier.
        logger: L'instance du logger AGI pour rapporter les erreurs.

    Returns:
        bool: True si le chemin est sûr, False sinon.
    """
    try:
        path_str = str(abs_path)

        # Vérification prioritaire des chemins autorisés
        for allowed_pattern in ALLOWED_USER_PATTERNS:
            if path_str.startswith(allowed_pattern):
                logger.debug(f"Chemin autorisé par la règle utilisateur : {path_str}")
                return True

        # Vérification des chemins interdits
        for forbidden in FORBIDDEN_SYSTEM_PATHS:
            if path_str.startswith(forbidden):
                logger.error(
                    f"❌ Accès interdit au chemin système critique : {abs_path}"
                )
                return False

        # Si le chemin n'est ni explicitement autorisé ni interdit, on le considère sûr.
        logger.debug(f"Chemin non critique autorisé par défaut : {path_str}")
        return True

    except Exception as e:
        logger.error(
            f"❌ Erreur inattendue lors de la vérification des chemins système pour '{abs_path}': {e}"
        )
        return False
