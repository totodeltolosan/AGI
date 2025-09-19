#!/usr/bin/env python3
"""
Structure Helpers - Fonctions Utilitaires pour Génération d'Arborescence
========================================================================

CHEMIN: tools/project_initializer/structure_helpers.py

Rôle Fondamental :
- Fonctions utilitaires pour création d'arborescence
- Validation de permissions et chemins
- Gestion d'erreurs et nettoyage
- Opérations atomiques sur répertoires

Conformité Architecturale :
- Module helper délégué depuis structure_generator.py
- Limite stricte < 200 lignes ✅
- Fonctions réutilisables et robustes

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import stat


class StructureHelpers:
    """Fonctions utilitaires pour génération d'arborescence."""

    def __init__(self, logger=None):
        self.logger = logger

    def filter_domains(
        self, domains: List[str], excluded_domains: Optional[List[str]] = None
    ) -> List[str]:
        """Filtre les domaines en excluant ceux spécifiés."""
        if not excluded_domains:
            return domains.copy()

        filtered = [domain for domain in domains if domain not in excluded_domains]

        if self.logger and excluded_domains:
            self.logger.info(f"🔍 Domaines exclus: {excluded_domains}")
            self.logger.info(f"🔍 Domaines retenus: {filtered}")

        return filtered

    def validate_output_directory(self, output_dir: str) -> bool:
        """Valide le répertoire de sortie."""
        try:
            output_path = Path(output_dir)

            # Vérification répertoire parent
            parent = output_path.parent
            if not parent.exists():
                if self.logger:
                    self.logger.error(f"❌ Répertoire parent inexistant: {parent}")
                return False

            # Vérification permissions d'écriture
            if not os.access(parent, os.W_OK):
                if self.logger:
                    self.logger.error(f"❌ Pas de permission d'écriture: {parent}")
                return False

            # Vérification existence du répertoire cible
            if output_path.exists() and not output_path.is_dir():
                if self.logger:
                    self.logger.error(
                        f"❌ Chemin existe mais n'est pas un répertoire: {output_path}"
                    )
                return False

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur validation répertoire: {e}")
            return False

    def validate_domains_list(self, domains: List[str]) -> bool:
        """Valide la liste des domaines."""
        if not domains:
            if self.logger:
                self.logger.error("❌ Liste de domaines vide")
            return False

        invalid_domains = []
        for domain in domains:
            if not self._is_valid_domain_name(domain):
                invalid_domains.append(domain)

        if invalid_domains:
            if self.logger:
                self.logger.error(f"❌ Noms de domaines invalides: {invalid_domains}")
            return False

        return True

    def create_directory_safe(self, directory_path: Path) -> bool:
        """Crée un répertoire de façon sécurisée."""
        try:
            if directory_path.exists():
                if directory_path.is_dir():
                    if self.logger:
                        self.logger.debug(
                            f"📁 Répertoire existe déjà: {directory_path}"
                        )
                    return True
                else:
                    if self.logger:
                        self.logger.error(
                            f"❌ Chemin existe mais n'est pas un répertoire: {directory_path}"
                        )
                    return False

            # Création du répertoire
            directory_path.mkdir(parents=True, exist_ok=True)

            # Vérification création
            if directory_path.exists() and directory_path.is_dir():
                if self.logger:
                    self.logger.debug(f"✅ Répertoire créé: {directory_path}")
                return True
            else:
                if self.logger:
                    self.logger.error(f"❌ Échec création répertoire: {directory_path}")
                return False

        except PermissionError as e:
            if self.logger:
                self.logger.error(f"❌ Permission refusée: {directory_path} - {e}")
            return False
        except OSError as e:
            if self.logger:
                self.logger.error(f"❌ Erreur système: {directory_path} - {e}")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur inattendue: {directory_path} - {e}")
            return False

    def create_domain_directories(
        self, output_path: Path, domain: str, structure: Dict[str, Any]
    ) -> bool:
        """Crée les répertoires d'un domaine avec sa structure."""
        try:
            domain_path = output_path / domain

            # Création du répertoire principal du domaine
            if not self.create_directory_safe(domain_path):
                return False

            # Création des sous-répertoires
            for subdir_name, subdir_config in structure.items():
                subdir_path = domain_path / subdir_name

                if not self.create_directory_safe(subdir_path):
                    if self.logger:
                        self.logger.warning(
                            f"⚠️ Échec création sous-répertoire: {subdir_path}"
                        )
                    # Continue malgré l'échec d'un sous-répertoire

                # Création des fichiers __init__.py si nécessaire
                if subdir_config.get("create_init", False):
                    self._create_init_file(subdir_path)

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur création structure domaine {domain}: {e}")
            return False

    def create_single_domain(
        self, output_path: Path, domain: str, structure: Dict[str, Any]
    ) -> bool:
        """Crée un domaine unique avec sa structure."""
        return self.create_domain_directories(output_path, domain, structure)

    def validate_domain_permissions(self, domain_path: Path) -> bool:
        """Valide les permissions d'un domaine."""
        try:
            if not domain_path.exists():
                return False

            # Vérification lecture
            if not os.access(domain_path, os.R_OK):
                if self.logger:
                    self.logger.warning(
                        f"⚠️ Pas de permission de lecture: {domain_path}"
                    )
                return False

            # Vérification écriture
            if not os.access(domain_path, os.W_OK):
                if self.logger:
                    self.logger.warning(
                        f"⚠️ Pas de permission d'écriture: {domain_path}"
                    )
                return False

            # Vérification exécution
            if not os.access(domain_path, os.X_OK):
                if self.logger:
                    self.logger.warning(
                        f"⚠️ Pas de permission d'exécution: {domain_path}"
                    )
                return False

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"❌ Erreur validation permissions {domain_path}: {e}"
                )
            return False

    def validate_permissions(self, base_path: Path) -> bool:
        """Valide les permissions de l'arborescence complète."""
        try:
            # Validation répertoire racine
            if not self.validate_domain_permissions(base_path):
                return False

            # Validation récursive des sous-répertoires
            for item in base_path.iterdir():
                if item.is_dir():
                    if not self.validate_domain_permissions(item):
                        if self.logger:
                            self.logger.warning(f"⚠️ Permissions incorrectes: {item}")
                        # Continue la validation malgré les erreurs

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur validation permissions globales: {e}")
            return False

    def cleanup_directories(self, base_path: Path, created_dirs: Set[str]) -> bool:
        """Nettoie les répertoires créés en cas d'échec."""
        try:
            if self.logger:
                self.logger.info(f"🧹 Nettoyage de {len(created_dirs)} répertoires")

            cleanup_success = True

            # Tri des répertoires par profondeur (plus profonds d'abord)
            sorted_dirs = sorted(
                created_dirs, key=lambda x: x.count(os.sep), reverse=True
            )

            for dir_path in sorted_dirs:
                try:
                    path = Path(dir_path)
                    if path.exists() and path.is_dir():
                        if path.is_symlink():
                            path.unlink()
                        else:
                            shutil.rmtree(path)

                        if self.logger:
                            self.logger.debug(f"🗑️ Supprimé: {dir_path}")

                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"⚠️ Échec suppression {dir_path}: {e}")
                    cleanup_success = False

            return cleanup_success

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur nettoyage global: {e}")
            return False

    def _is_valid_domain_name(self, domain: str) -> bool:
        """Valide qu'un nom de domaine est acceptable."""
        if not domain or not isinstance(domain, str):
            return False

        # Vérification caractères autorisés
        if not domain.replace("_", "").replace("-", "").isalnum():
            return False

        # Vérification longueur
        if len(domain) < 2 or len(domain) > 50:
            return False

        # Vérification début/fin
        if domain.startswith("_") or domain.endswith("_"):
            return False

        # Vérification mots réservés
        reserved_words = {"con", "aux", "prn", "nul", "com1", "com2", "lpt1", "lpt2"}
        if domain.lower() in reserved_words:
            return False

        return True

    def _create_init_file(self, directory_path: Path) -> bool:
        """Crée un fichier __init__.py dans un répertoire."""
        try:
            init_file = directory_path / "__init__.py"

            if not init_file.exists():
                init_content = f'"""Module {directory_path.name}."""\n'
                init_file.write_text(init_content, encoding="utf-8")

                if self.logger:
                    self.logger.debug(f"📄 Fichier __init__.py créé: {init_file}")

            return True

        except Exception as e:
            if self.logger:
                self.logger.warning(
                    f"⚠️ Échec création __init__.py dans {directory_path}: {e}"
                )
            return False

    def get_directory_stats(self, base_path: Path) -> Dict[str, Any]:
        """Récupère les statistiques d'un répertoire."""
        try:
            if not base_path.exists():
                return {"exists": False}

            stats = {
                "exists": True,
                "is_directory": base_path.is_dir(),
                "total_items": 0,
                "directories": 0,
                "files": 0,
                "size_bytes": 0,
            }

            if stats["is_directory"]:
                for item in base_path.rglob("*"):
                    stats["total_items"] += 1
                    if item.is_dir():
                        stats["directories"] += 1
                    elif item.is_file():
                        stats["files"] += 1
                        stats["size_bytes"] += item.stat().st_size

            return stats

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur calcul statistiques {base_path}: {e}")
            return {"exists": False, "error": str(e)}

    def compare_structures(self, path1: Path, path2: Path) -> Dict[str, Any]:
        """Compare deux structures de répertoires."""
        try:
            stats1 = self.get_directory_stats(path1)
            stats2 = self.get_directory_stats(path2)

            return {
                "path1_stats": stats1,
                "path2_stats": stats2,
                "structures_match": (
                    stats1.get("directories", 0) == stats2.get("directories", 0)
                    and stats1.get("total_items", 0) == stats2.get("total_items", 0)
                ),
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur comparaison structures: {e}")
            return {"error": str(e)}
