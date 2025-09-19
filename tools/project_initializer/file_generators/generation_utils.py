#!/usr/bin/env python3
"""
Generation Utils - Utilitaires pour le Cycle de Vie de la Génération
=====================================================================

Rôle Fondamental (Conforme AGI.md) :
- Fournir des fonctions de support pour les tâches post-génération.
- Isoler la logique de validation, de nettoyage et de reporting.
- Assurer que les générateurs se concentrent uniquement sur la création de contenu.

Version : 1.0
Date : 18 Septembre 2025
"""

import os
from pathlib import Path
from typing import Set


def validate_python_syntax(file_path: Path, logger) -> bool:
    """Valide la syntaxe Python d'un fichier en utilisant compile()."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        compile(content, str(file_path), "exec")
        return True
    except SyntaxError as e:
        logger.error(f"❌ Erreur de syntaxe Python dans {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(
            f"❌ Erreur inattendue lors de la validation de la syntaxe de {file_path}: {e}"
        )
        return False


def validate_generated_files(generated_files: Set[str], logger) -> bool:
    """
    Valide un ensemble de fichiers générés (existence et syntaxe Python).
    """
    validation_errors = []
    for file_path_str in generated_files:
        file_path = Path(file_path_str)

        if not file_path.exists():
            validation_errors.append(f"Fichier généré manquant : {file_path}")
            continue

        if file_path.suffix == ".py":
            if not validate_python_syntax(file_path, logger):
                validation_errors.append(f"Syntaxe Python invalide : {file_path}")

    if validation_errors:
        logger.error(
            f"❌ {len(validation_errors)} erreur(s) de validation détectée(s)."
        )
        for error in validation_errors:
            logger.error(f"  - {error}")
        return False

    logger.verbose(
        f"✅ Validation post-génération réussie pour {len(generated_files)} fichier(s)."
    )
    return True


def cleanup_generated_files(generated_files: Set[str], logger) -> int:
    """
    Nettoie (supprime) un ensemble de fichiers générés, typiquement après une erreur.
    Retourne le nombre de fichiers nettoyés.
    """
    cleaned_count = 0
    for file_path_str in generated_files:
        try:
            file_path = Path(file_path_str)
            if file_path.exists():
                file_path.unlink()
                cleaned_count += 1
        except Exception as e:
            logger.error(f"❌ Impossible de nettoyer le fichier {file_path_str}: {e}")

    if cleaned_count > 0:
        logger.verbose(
            f"🧹 Nettoyage effectué : {cleaned_count} fichier(s) supprimé(s)."
        )

    return cleaned_count
