#!/usr/bin/env python3
"""
Markdown Generator - Générateur de Documentation Markdown pour AGI
=================================================================

Rôle Fondamental (Conforme AGI.md - file_generators/markdown_generator.py) :
- Génération documentation Markdown complète du projet AGI
- contribution_guidelines.md (Guide développeurs)
- README.md principal et par domaine
- Documentation architecture et API

Conformité Architecturale :
- Limite stricte < 200 lignes via délégation modulaire
- Templates externalisés vers MarkdownTemplates
- Traçabilité complète via AGILogger
- Contenu généré conforme aux directives AGI.md

Version : 2.0 (Refactorisé)
Date : 18 September 2025
Référence : Rapport de Directives AGI.md - Section file_generators/
"""

from pathlib import Path
from typing import Dict, List, Optional
from .markdown_templates import MarkdownTemplates


class MarkdownGenerator:
    """
    Générateur de documentation Markdown conforme aux directives AGI.md
    Délègue la construction de contenu à MarkdownTemplates pour respect limite 200 lignes
    """

    def __init__(self, logger):
        """TODO: Add docstring."""
        self.logger = logger
        self.generated_files = []
        self.templates = MarkdownTemplates()

    def generate_contribution_guidelines(self, output_dir: Path) -> bool:
        """Génère development_governance/contribution_guidelines.md"""
        try:
            content = self.templates.build_contribution_guidelines()
            guidelines_path = (
                output_dir / "development_governance" / "contribution_guidelines.md"
            )
            self._write_markdown_file(guidelines_path, content)
            self.logger.verbose(
                f"✅ contribution_guidelines.md généré: {guidelines_path}"
            )
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur génération contribution_guidelines.md: {e}")
            return False

    def generate_main_readme(
        self, output_dir: Path, project_name: str = "Projet AGI"
    ) -> bool:
        """Génère README.md principal"""
        try:
            content = self.templates.build_main_readme(project_name)
            readme_path = output_dir / "README.md"
            self._write_markdown_file(readme_path, content)
            self.logger.verbose(f"✅ README.md principal généré: {readme_path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur génération README.md: {e}")
            return False

    def generate_domain_readme(
        self, domain_name: str, output_dir: Path, python_files: List[str]
    ) -> bool:
        """Génère README.md pour un domaine spécifique"""
        try:
            content = self.templates.build_domain_readme(domain_name, python_files)
            domain_readme_path = output_dir / domain_name / "README.md"
            self._write_markdown_file(domain_readme_path, content)
            self.logger.verbose(f"✅ README.md généré pour domaine {domain_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur génération README.md pour {domain_name}: {e}")
            return False

    def generate_architecture_doc(self, output_dir: Path) -> bool:
        """Génère docs/ARCHITECTURE.md"""
        try:
            content = self.templates.build_architecture_doc()
            arch_path = output_dir / "docs" / "ARCHITECTURE.md"
            self._write_markdown_file(arch_path, content)
            self.logger.verbose(f"✅ ARCHITECTURE.md généré: {arch_path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur génération ARCHITECTURE.md: {e}")
            return False

    def generate_all_documentation(
        self,
        output_dir: Path,
        project_name: str = "Projet AGI",
        domains: List[str] = None,
    ) -> bool:
        """Génère toute la documentation en une fois"""
        try:
            success_count = 0
            total_count = 0

            # README principal
            if self.generate_main_readme(output_dir, project_name):
                success_count += 1
            total_count += 1

            # Contribution guidelines
            if self.generate_contribution_guidelines(output_dir):
                success_count += 1
            total_count += 1

            # Architecture doc
            if self.generate_architecture_doc(output_dir):
                success_count += 1
            total_count += 1

            # README par domaine
            if domains:
                for domain in domains:
                    if self.generate_domain_readme(domain, output_dir, []):
                        success_count += 1
                    total_count += 1

            self.logger.info(
                f"📄 Documentation générée: {success_count}/{total_count} fichiers"
            )
            return success_count == total_count

        except Exception as e:
            self.logger.error(f"❌ Erreur génération documentation complète: {e}")
            return False

    def get_generated_files(self) -> List[str]:
        """Retourne la liste des fichiers générés"""
        return self.generated_files.copy()

    def _write_markdown_file(self, file_path: Path, content: str) -> None:
        """Écrit un fichier Markdown avec gestion d'erreurs"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.generated_files.append(str(file_path))

        except PermissionError:
            self.logger.error(f"❌ Permission refusée pour écriture: {file_path}")
            raise
        except OSError as e:
            self.logger.error(f"❌ Erreur système écriture fichier: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Erreur inattendue écriture: {e}")
            raise

    def _validate_output_dir(self, output_dir: Path) -> bool:
        """Valide que le répertoire de sortie est accessible"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir.exists() and output_dir.is_dir()
        except Exception:
            return False