#!/usr/bin/env python3
"""
Path Validator - Orchestrateur de Validation de Chemins (Refactorisé)
======================================================================

Rôle Fondamental (Conforme AGI.md) :
- Orchestrer l'application séquentielle des règles de validation de chemins.
- Déléguer la logique de validation à des modules spécialisés et conformes.
- Fournir une interface de validation unifiée pour le reste du générateur.
- Respecter la directive des 200 lignes.

Version : 2.0 (Refactorisé)
Date : 18 Septembre 2025
"""

from pathlib import Path
from typing import Set, Union

# Import des règles de validation spécialisées
from .rules.traversal_rule import check_path_traversal
from .rules.system_paths_rule import check_critical_system_paths
from .rules.extensions_rule import check_dangerous_extensions
from .rules.permissions_rule import (
    validate_write_permissions,
    validate_read_permissions,
)


class PathValidator:
    """
    Orchestrateur de validation qui applique un ensemble de règles de sécurité
    sur les chemins de fichiers, conformément à la constitution AGI.md.
    """

    def __init__(self, logger):
        """TODO: Add docstring."""
        self.logger = logger
        self.validated_paths: Set[str] = set()

    def _ensure_path_object(self, path_input: Union[str, Path]) -> Path:
        """Convertit l'entrée en objet Path pour une manipulation cohérente."""
        if isinstance(path_input, str):
            return Path(path_input)
        if isinstance(path_input, Path):
            return path_input
        raise TypeError(f"Type non supporté pour le chemin : {type(path_input)}")

    def validate_safe_path(self, path_input: Union[str, Path]) -> bool:
        """
        Valide la sécurité d'un chemin en appliquant toutes les règles déléguées.

        Args:
            path_input: Le chemin (str ou Path) à valider.

        Returns:
            True si toutes les règles de sécurité passent, False sinon.
        """
        try:
            path = self._ensure_path_object(path_input)
            abs_path = path.resolve()
            path_str = str(abs_path)

            if path_str in self.validated_paths:
                return True

            # Application séquentielle des règles importées
            if not check_path_traversal(path, self.logger):
                return False
            if not check_critical_system_paths(abs_path, self.logger):
                return False
            if not check_dangerous_extensions(path, self.logger):
                return False
            # Note: La vérification des caractères suspects reste simple et interne.
            if not self._check_suspicious_characters(path_str):
                return False

            self.validated_paths.add(path_str)
            self.logger.debug(f"Chemin validé par toutes les règles : {abs_path}")
            return True

        except Exception as e:
            self.logger.error(
                f"❌ Erreur inattendue lors de la validation du chemin '{path_input}': {e}"
            )
            return False

    def _check_suspicious_characters(self, path_str: str) -> bool:
        """Vérifie la présence de caractères potentiellement dangereux."""
        suspicious_chars = ["`", ";", "|", "&"]
        for char in suspicious_chars:
            if char in path_str:
                self.logger.error(
                    f"❌ Caractère suspect '{char}' détecté dans le chemin : {path_str}"
                )
                return False
        return True

    def validate_directory_creation(
        self, directory_path_input: Union[str, Path]
    ) -> bool:
        """
        Valide qu'un répertoire peut être créé de manière sécurisée.

        Args:
            directory_path_input: Le chemin du répertoire à créer.

        Returns:
            True si la création est possible et sécurisée, False sinon.
        """
        try:
            directory_path = self._ensure_path_object(directory_path_input)

            if not self.validate_safe_path(directory_path):
                return False

            # Délégation à la règle de permission
            if not validate_write_permissions(directory_path, self.logger):
                return False

            if directory_path.exists() and not directory_path.is_dir():
                self.logger.error(
                    f"❌ Un fichier existe déjà à l'emplacement du répertoire : {directory_path}"
                )
                return False

            self.logger.debug(
                f"Validation de création de répertoire réussie pour : {directory_path}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"❌ Erreur inattendue lors de la validation de création de répertoire '{directory_path_input}': {e}"
            )
            return False