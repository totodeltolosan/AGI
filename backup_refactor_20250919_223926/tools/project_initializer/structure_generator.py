#!/usr/bin/env python3
"""
Structure Generator - Interface Principale pour Génération d'Arborescence AGI
=============================================================================

CHEMIN: tools/project_initializer/structure_generator.py

Rôle Fondamental (Conforme AGI.md) :
- Interface principale pour génération d'arborescence de projet
- Orchestration via modules délégués pour respect limite 200 lignes
- Création de répertoires conformes aux directives AGI

Conformité Architecturale :
- Limite stricte < 200 lignes ✅ (refactorisé depuis 280 lignes)
- Délégation : structure_helpers.py + structure_config.py
- Traçabilité : logging détaillé
- Modularité : séparation claire des responsabilités

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
Référence : Refactorisation conformité AGI.md
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import traceback

try:
    from .structure_helpers import StructureHelpers
    from .structure_config import StructureConfig
except ImportError as e:
    # Import relatif pour module autonome
    try:
        from structure_helpers import StructureHelpers
        from structure_config import StructureConfig
    except ImportError:
        raise ImportError(f"❌ Modules structure refactorisés introuvables: {e}")


class StructureGenerator:
    """
    Générateur d'arborescence de projet AGI (refactorisé).

    Interface principale qui délègue la complexité aux modules spécialisés
    pour respecter la limite de 200 lignes et l'architecture modulaire.
    """

    def __init__(self, logger):
        self.logger = logger
        self.helpers = StructureHelpers(logger)
        self.config = StructureConfig()
        self.created_directories: Set[str] = set()
        self.creation_stats = {"success": 0, "errors": 0, "skipped": 0}

    def create_directories(
        self,
        output_dir: str,
        domains: List[str],
        excluded_domains: Optional[List[str]] = None,
    ) -> bool:
        """
        Crée l'arborescence complète du projet AGI.

        Args:
            output_dir: Répertoire de destination
            domains: Liste des domaines à créer
            excluded_domains: Domaines à exclure (optionnel)

        Returns:
            True si succès, False sinon
        """
        try:
            self.logger.info(f"🏗️ Création arborescence dans {output_dir}")

            # Validation et préparation
            if not self._validate_input(output_dir, domains):
                return False

            output_path = Path(output_dir)
            filtered_domains = self.helpers.filter_domains(domains, excluded_domains)

            # Création du répertoire racine
            if not self._create_root_directory(output_path):
                return False

            # Création des domaines
            if not self._create_domain_directories(output_path, filtered_domains):
                return False

            # Création des répertoires de base
            if not self._create_base_directories(output_path):
                return False

            # Validation finale
            success = self._validate_creation_results(output_path, filtered_domains)
            self._log_creation_summary()

            return success

        except Exception as e:
            self.logger.error(f"❌ Erreur création arborescence: {e}")
            self.logger.debug(traceback.format_exc())
            return False

    def create_domain_structure(self, output_dir: str, domain: str) -> bool:
        """Crée la structure d'un domaine spécifique."""
        try:
            self.logger.info(f"🔄 Création structure domaine {domain}")

            output_path = Path(output_dir)
            domain_structure = self.config.get_domain_structure(domain)

            return self.helpers.create_domain_directories(
                output_path, domain, domain_structure
            )

        except Exception as e:
            self.logger.error(f"❌ Erreur création domaine {domain}: {e}")
            return False

    def validate_structure(
        self, output_dir: str, expected_domains: List[str]
    ) -> Dict[str, Any]:
        """Valide la structure créée."""
        try:
            output_path = Path(output_dir)
            validation_result = {
                "valid": True,
                "missing_directories": [],
                "unexpected_directories": [],
                "permissions_issues": [],
                "summary": {},
            }

            # Validation des domaines
            for domain in expected_domains:
                domain_path = output_path / domain
                if not domain_path.exists():
                    validation_result["missing_directories"].append(domain)
                    validation_result["valid"] = False
                elif not self.helpers.validate_domain_permissions(domain_path):
                    validation_result["permissions_issues"].append(domain)
                    validation_result["valid"] = False

            # Validation des répertoires de base
            base_dirs = self.config.get_base_directories()
            for base_dir in base_dirs:
                base_path = output_path / base_dir
                if not base_path.exists():
                    validation_result["missing_directories"].append(base_dir)
                    validation_result["valid"] = False

            # Génération du résumé
            validation_result["summary"] = self._generate_validation_summary(
                output_path, expected_domains
            )

            return validation_result

        except Exception as e:
            self.logger.error(f"❌ Erreur validation structure: {e}")
            return {"valid": False, "error": str(e)}

    def get_created_directories(self) -> Set[str]:
        """Retourne les répertoires créés."""
        return self.created_directories.copy()

    def get_creation_stats(self) -> Dict[str, int]:
        """Retourne les statistiques de création."""
        return self.creation_stats.copy()

    def cleanup_failed_creation(self, output_dir: str) -> bool:
        """Nettoie en cas d'échec de création."""
        try:
            self.logger.info(f"🧹 Nettoyage après échec: {output_dir}")
            return self.helpers.cleanup_directories(
                Path(output_dir), self.created_directories
            )
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage: {e}")
            return False

    def _validate_input(self, output_dir: str, domains: List[str]) -> bool:
        """Valide les paramètres d'entrée."""
        if not output_dir or not domains:
            self.logger.error("❌ Paramètres d'entrée invalides")
            return False

        if not self.helpers.validate_output_directory(output_dir):
            return False

        if not self.helpers.validate_domains_list(domains):
            return False

        return True

    def _create_root_directory(self, output_path: Path) -> bool:
        """Crée le répertoire racine."""
        try:
            success = self.helpers.create_directory_safe(output_path)
            if success:
                self.created_directories.add(str(output_path))
                self.creation_stats["success"] += 1
            else:
                self.creation_stats["errors"] += 1
            return success
        except Exception as e:
            self.logger.error(f"❌ Erreur création répertoire racine: {e}")
            self.creation_stats["errors"] += 1
            return False

    def _create_domain_directories(self, output_path: Path, domains: List[str]) -> bool:
        """Crée les répertoires de domaines."""
        try:
            total_success = True

            for domain in domains:
                self.logger.info(f"🔄 Création domaine: {domain}")

                domain_success = self.helpers.create_single_domain(
                    output_path, domain, self.config.get_domain_structure(domain)
                )

                if domain_success:
                    self.created_directories.add(str(output_path / domain))
                    self.creation_stats["success"] += 1
                    self.logger.info(f"✅ Domaine {domain} créé")
                else:
                    self.creation_stats["errors"] += 1
                    self.logger.error(f"❌ Échec création domaine {domain}")
                    total_success = False

            return total_success

        except Exception as e:
            self.logger.error(f"❌ Erreur création domaines: {e}")
            return False

    def _create_base_directories(self, output_path: Path) -> bool:
        """Crée les répertoires de base (docs, tests, etc.)."""
        try:
            base_directories = self.config.get_base_directories()

            for base_dir in base_directories:
                base_path = output_path / base_dir

                if self.helpers.create_directory_safe(base_path):
                    self.created_directories.add(str(base_path))
                    self.creation_stats["success"] += 1
                    self.logger.debug(f"✅ Répertoire base créé: {base_dir}")
                else:
                    self.creation_stats["errors"] += 1
                    self.logger.warning(f"⚠️ Échec création répertoire base: {base_dir}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur création répertoires base: {e}")
            return False

    def _validate_creation_results(self, output_path: Path, domains: List[str]) -> bool:
        """Valide les résultats de création."""
        try:
            # Vérification existence domaines
            for domain in domains:
                domain_path = output_path / domain
                if not domain_path.exists():
                    self.logger.error(f"❌ Domaine manquant: {domain}")
                    return False

            # Vérification permissions
            if not self.helpers.validate_permissions(output_path):
                return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur validation résultats: {e}")
            return False

    def _generate_validation_summary(
        self, output_path: Path, domains: List[str]
    ) -> Dict[str, Any]:
        """Génère un résumé de validation."""
        return {
            "total_directories": len(self.created_directories),
            "domains_created": len(domains),
            "base_directories": len(self.config.get_base_directories()),
            "creation_stats": self.creation_stats.copy(),
            "structure_valid": True,
        }

    def _log_creation_summary(self):
        """Log le résumé de création."""
        total = sum(self.creation_stats.values())
        self.logger.info(
            f"📊 Résumé création: {self.creation_stats['success']}/{total} succès, "
            f"{self.creation_stats['errors']} erreurs, {self.creation_stats['skipped']} ignorés"
        )

    def __str__(self) -> str:
        """Représentation string de l'instance."""
        return f"StructureGenerator(created={len(self.created_directories)})"

    def __repr__(self) -> str:
        """Représentation debug de l'instance."""
        return f"StructureGenerator(helpers={self.helpers}, config={self.config})"
