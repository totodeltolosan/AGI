#!/usr/bin/env python3
"""
Python Generator - Générateur de Fichiers Python AGI (Corrigé)
===============================================================

CHEMIN: tools/project_initializer/file_generators/python_generator.py

Rôle Fondamental (Conforme AGI.md) :
- Interface principale pour génération de fichiers Python
- Utilisation des modules config refactorisés
- Respect strict limite 200 lignes
- Intégration avec l'architecture modulaire existante

Conformité Architecturale :
- Limite stricte < 200 lignes ✅
- Imports corrigés vers config.utils.config_helpers
- Délégation aux templates et content generators
- Logging détaillé et gestion d'erreurs

Version : 1.0 (Corrigé)
Date : 18 Septembre 2025
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import traceback

# Imports corrigés pour utiliser l'architecture refactorisée
try:
    from config.utils.config_helpers import get_files_for_domain, get_all_python_files
    from templates.python_tpl import PythonTemplates
except ImportError as e:
    raise ImportError(f"❌ Modules config refactorisés introuvables: {e}")


class PythonGenerator:
    """
    Générateur spécialisé pour les fichiers Python du projet AGI.

    Utilise l'architecture modulaire refactorisée avec les nouveaux
    modules config.utils et config.data pour respecter les directives AGI.
    """

    def __init__(self, logger):
        self.logger = logger
        self.templates = PythonTemplates()
        self.generated_files: Set[str] = set()

    def generate_domain_files(
        self, output_dir: str, domain: str, project_spec: Dict[str, Any]
    ) -> bool:
        """
        Génère tous les fichiers Python d'un domaine spécifique.

        Args:
            output_dir: Répertoire de destination
            domain: Nom du domaine
            project_spec: Spécifications du projet

        Returns:
            True si génération réussie, False sinon
        """
        try:
            self.logger.info(f"🔄 Génération fichiers Python pour domaine: {domain}")

            # Récupération des fichiers via config refactorisé
            files_to_generate = get_files_for_domain(domain)

            if not files_to_generate:
                self.logger.warning(f"⚠️ Aucun fichier défini pour domaine {domain}")
                return False

            domain_path = Path(output_dir) / domain
            domain_path.mkdir(parents=True, exist_ok=True)

            success_count = 0
            total_files = len(files_to_generate)

            for filename in files_to_generate:
                if self._generate_single_file(
                    domain_path, filename, domain, project_spec
                ):
                    success_count += 1
                    self.logger.debug(f"✅ Fichier généré: {filename}")
                else:
                    self.logger.error(f"❌ Échec génération: {filename}")

            success_rate = success_count / total_files if total_files > 0 else 0
            self.logger.info(
                f"📊 Domaine {domain}: {success_count}/{total_files} fichiers générés "
                f"({success_rate:.1%})"
            )

            return success_count > 0

        except Exception as e:
            self.logger.error(f"❌ Erreur génération domaine {domain}: {e}")
            self.logger.debug(traceback.format_exc())
            return False

    def generate_main_file(self, output_dir: str, project_spec: Dict[str, Any]) -> bool:
        """Génère le fichier main.py principal."""
        try:
            self.logger.info("🔄 Génération fichier main.py")

            main_path = Path(output_dir) / "main.py"
            main_content = self.templates.get_main_template(project_spec)

            main_path.write_text(main_content, encoding="utf-8")
            self.generated_files.add(str(main_path))

            self.logger.info(f"✅ main.py généré: {len(main_content)} caractères")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur génération main.py: {e}")
            return False

    def validate_generated_files(
        self, files_to_validate: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Valide les fichiers générés."""
        try:
            files = files_to_validate or list(self.generated_files)
            validation_results = {
                "total_files": len(files),
                "valid_files": 0,
                "invalid_files": 0,
                "errors": [],
            }

            for file_path in files:
                try:
                    path = Path(file_path)
                    if not path.exists():
                        validation_results["errors"].append(
                            f"Fichier manquant: {file_path}"
                        )
                        validation_results["invalid_files"] += 1
                        continue

                    # Validation syntaxe Python
                    if path.suffix == ".py":
                        import ast

                        content = path.read_text(encoding="utf-8")
                        ast.parse(content)  # Lève SyntaxError si syntaxe incorrecte

                        # Vérification limite 200 lignes
                        line_count = len(content.splitlines())
                        if line_count > 200:
                            validation_results["errors"].append(
                                f"Fichier dépasse 200 lignes: {file_path} ({line_count} lignes)"
                            )
                            validation_results["invalid_files"] += 1
                            continue

                    validation_results["valid_files"] += 1

                except SyntaxError as e:
                    validation_results["errors"].append(
                        f"Erreur syntaxe {file_path}: {e}"
                    )
                    validation_results["invalid_files"] += 1
                except Exception as e:
                    validation_results["errors"].append(
                        f"Erreur validation {file_path}: {e}"
                    )
                    validation_results["invalid_files"] += 1

            self.logger.info(
                f"🔍 Validation: {validation_results['valid_files']}/{validation_results['total_files']} "
                f"fichiers valides"
            )

            return validation_results

        except Exception as e:
            self.logger.error(f"❌ Erreur validation fichiers: {e}")
            return {
                "total_files": 0,
                "valid_files": 0,
                "invalid_files": 0,
                "errors": [str(e)],
            }

    def get_generation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de génération."""
        return {
            "files_generated": len(self.generated_files),
            "generated_files": list(self.generated_files),
            "domains_processed": len(
                {
                    Path(f).parent.name
                    for f in self.generated_files
                    if Path(f).parent.name != Path(f).parent.parent.name
                }
            ),
        }

    def cleanup_generated_files(self) -> bool:
        """Supprime les fichiers générés (utile pour nettoyage)."""
        try:
            cleanup_count = 0
            for file_path in self.generated_files:
                try:
                    path = Path(file_path)
                    if path.exists():
                        path.unlink()
                        cleanup_count += 1
                except Exception as e:
                    self.logger.warning(f"⚠️ Échec suppression {file_path}: {e}")

            self.logger.info(f"🧹 {cleanup_count} fichiers supprimés")
            self.generated_files.clear()
            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage: {e}")
            return False

    def _generate_single_file(
        self,
        domain_path: Path,
        filename: str,
        domain: str,
        project_spec: Dict[str, Any],
    ) -> bool:
        """Génère un fichier Python individuel."""
        try:
            file_path = domain_path / filename

            if filename == "__init__.py":
                content = self.templates.get_init_template(domain)
            else:
                content = self.templates.get_file_template(
                    filename, domain, project_spec
                )

            file_path.write_text(content, encoding="utf-8")
            self.generated_files.add(str(file_path))

            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur génération {filename}: {e}")
            return False

    def get_generated_files(self) -> Set[str]:
        """Retourne l'ensemble des fichiers générés."""
        return self.generated_files.copy()

    def __str__(self) -> str:
        """Représentation string de l'instance."""
        return f"PythonGenerator(files_generated={len(self.generated_files)})"

    def __repr__(self) -> str:
        """Représentation debug de l'instance."""
        return f"PythonGenerator(templates={self.templates}, files={len(self.generated_files)})"
