#!/usr/bin/env python3
"""
Markdown Templates - Interface Principale pour Templates Markdown AGI
====================================================================

CHEMIN: tools/project_initializer/file_generators/markdown_templates.py

Rôle Fondamental (Conforme AGI.md) :
- Interface principale pour génération de templates Markdown
- Orchestration des templates via modules délégués
- Respect strict limite 200 lignes par refactorisation modulaire

Conformité Architecturale :
- Limite stricte < 200 lignes ✅ (refactorisé depuis 312 lignes)
- Délégation : markdown_helpers.py + markdown_config.py
- Traçabilité : logging détaillé
- Modularité : séparation claire des responsabilités

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
Référence : Refactorisation conformité AGI.md
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from .markdown_helpers import MarkdownHelpers
    from .markdown_config import MarkdownConfig
except ImportError as e:
    # Import relatif pour module autonome
    try:
        from markdown_helpers import MarkdownHelpers
        from markdown_config import MarkdownConfig
    except ImportError:
        raise ImportError(f"❌ Modules markdown refactorisés introuvables: {e}")


class MarkdownTemplates:
    """
    Générateur de templates Markdown pour projet AGI (refactorisé).

    Interface principale qui délègue la complexité aux modules spécialisés
    pour respecter la limite de 200 lignes et l'architecture modulaire.
    """

    def __init__(self, logger=None):
        self.logger = logger or self._create_default_logger()
        self.helpers = MarkdownHelpers(self.logger)
        self.config = MarkdownConfig()
        self.generated_files = []

    def build_contribution_guidelines(self) -> str:
        """Génère le contenu des guidelines de contribution."""
        try:
            template = self.config.get_contribution_template()
            return self.helpers.process_template(
                template,
                {
                    "project_name": "Projet AGI",
                    "date": self.helpers.get_current_date(),
                    "version": "1.0",
                },
            )
        except Exception as e:
            self.logger.error(f"❌ Erreur génération guidelines: {e}")
            return self.config.get_fallback_guidelines()

    def build_main_readme(self, project_spec: Dict[str, Any]) -> str:
        """Génère le README.md principal du projet."""
        try:
            template = self.config.get_readme_template()
            context = self.helpers.build_readme_context(project_spec)
            return self.helpers.process_template(template, context)
        except Exception as e:
            self.logger.error(f"❌ Erreur génération README: {e}")
            return self.config.get_fallback_readme()

    def build_architecture_doc(self, project_spec: Dict[str, Any]) -> str:
        """Génère la documentation d'architecture."""
        try:
            template = self.config.get_architecture_template()
            context = self.helpers.build_architecture_context(project_spec)
            return self.helpers.process_template(template, context)
        except Exception as e:
            self.logger.error(f"❌ Erreur génération architecture: {e}")
            return self.config.get_fallback_architecture()

    def build_domain_readme(self, domain: str, project_spec: Dict[str, Any]) -> str:
        """Génère un README spécifique à un domaine."""
        try:
            template = self.config.get_domain_readme_template()
            context = self.helpers.build_domain_context(domain, project_spec)
            return self.helpers.process_template(template, context)
        except Exception as e:
            self.logger.error(f"❌ Erreur génération README domaine {domain}: {e}")
            return self.config.get_fallback_domain_readme(domain)

    def build_api_documentation(self, project_spec: Dict[str, Any]) -> str:
        """Génère la documentation API."""
        try:
            template = self.config.get_api_template()
            context = self.helpers.build_api_context(project_spec)
            return self.helpers.process_template(template, context)
        except Exception as e:
            self.logger.error(f"❌ Erreur génération doc API: {e}")
            return self.config.get_fallback_api_doc()

    def build_user_guide(self, project_spec: Dict[str, Any]) -> str:
        """Génère le guide utilisateur."""
        try:
            template = self.config.get_user_guide_template()
            context = self.helpers.build_user_guide_context(project_spec)
            return self.helpers.process_template(template, context)
        except Exception as e:
            self.logger.error(f"❌ Erreur génération guide utilisateur: {e}")
            return self.config.get_fallback_user_guide()

    def get_all_templates(self) -> Dict[str, str]:
        """Retourne tous les templates disponibles."""
        return {
            "contribution_guidelines": self.build_contribution_guidelines(),
            "main_readme": self.build_main_readme({}),
            "architecture": self.build_architecture_doc({}),
            "api_documentation": self.build_api_documentation({}),
            "user_guide": self.build_user_guide({}),
        }

    def validate_template(self, template_name: str, content: str) -> bool:
        """Valide un template généré."""
        return self.helpers.validate_markdown_content(template_name, content)

    def get_generated_files(self) -> List[str]:
        """Retourne la liste des fichiers générés."""
        return self.generated_files.copy()

    def _create_default_logger(self):
        """Crée un logger par défaut si non fourni."""
        import logging

        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def __str__(self) -> str:
        """Représentation string de l'instance."""
        return f"MarkdownTemplates(templates={len(self.get_all_templates())})"

    def __repr__(self) -> str:
        """Représentation debug de l'instance."""
        return f"MarkdownTemplates(helpers={self.helpers}, config={self.config})"
