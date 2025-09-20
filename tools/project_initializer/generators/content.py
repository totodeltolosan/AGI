#!/usr/bin/env python3
"""
Content Generator - Interface Principale pour Génération de Contenu AGI
=======================================================================

CHEMIN: tools/project_initializer/generators/content.py

Rôle Fondamental (Conforme AGI.md) :
- Interface principale pour génération de contenu Python
- Orchestration via modules délégués pour respect limite 200 lignes
- Génération de fichiers Python conformes aux directives AGI

Conformité Architecturale :
- Limite stricte < 200 lignes ✅ (refactorisé depuis 299 lignes)
- Délégation : content_helpers.py + content_templates.py
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
    from .content_helpers import ContentHelpers
    from .content_templates import ContentTemplates
except ImportError as e:
    # Import relatif pour module autonome
    try:
        from content_helpers import ContentHelpers
        from content_templates import ContentTemplates
    except ImportError:
        raise ImportError(f"❌ Modules content refactorisés introuvables: {e}")


class PythonContentGenerator:
    """
    Générateur de contenu Python pour projet AGI (refactorisé).

    Interface principale qui délègue la complexité aux modules spécialisés
    pour respecter la limite de 200 lignes et l'architecture modulaire.
    """

    def __init__(self, logger):
        """TODO: Add docstring."""
        self.logger = logger
        self.helpers = ContentHelpers(logger)
        self.templates = ContentTemplates()
        self.generated_files: Set[str] = set()
        self.context_cache: Dict[str, Any] = {}

    def generate_file_content(
        self, domain: str, filename: str, project_spec: Dict[str, Any]
    ) -> str:
        """
        Génère le contenu d'un fichier Python pour un domaine spécifique.

        Args:
            domain: Nom du domaine (ex: 'compliance', 'core')
            filename: Nom du fichier (ex: 'validator.py')
            project_spec: Spécifications du projet

        Returns:
            Contenu Python généré
        """
        try:
            self.logger.info(f"🔄 Génération contenu {domain}/{filename}")

            # Préparation du contexte
            context = self._prepare_context(domain, filename, project_spec)

            # Sélection du template approprié
            template_type = self.helpers.determine_template_type(filename)
            template = self.templates.get_template(template_type)

            # Génération du contenu
            content = self.helpers.process_template(template, context)

            # Validation et optimisation
            if self.helpers.validate_python_content(content):
                optimized_content = self.helpers.optimize_content(content)
                self.generated_files.add(f"{domain}/{filename}")
                return optimized_content
            else:
                self.logger.warning(f"⚠️ Contenu généré invalide pour {filename}")
                return self.templates.get_fallback_template(template_type, context)

        except Exception as e:
            self.logger.error(f"❌ Erreur génération {domain}/{filename}: {e}")
            return self._generate_emergency_content(domain, filename)

    def generate_main_file_content(self, project_spec: Dict[str, Any]) -> str:
        """Génère le contenu du fichier main.py principal."""
        try:
            context = self._prepare_main_context(project_spec)
            template = self.templates.get_main_template()
            content = self.helpers.process_template(template, context)

            # Ajout des imports dynamiques
            content = self.helpers.add_dynamic_imports(content, project_spec)

            return self.helpers.optimize_content(content)

        except Exception as e:
            self.logger.error(f"❌ Erreur génération main.py: {e}")
            return self.templates.get_emergency_main_template()

    def generate_init_content(self, domain: str) -> str:
        """Génère le contenu d'un fichier __init__.py."""
        try:
            context = {"domain": domain, "domain_title": domain.title()}
            template = self.templates.get_init_template()
            return self.helpers.process_template(template, context)

        except Exception as e:
            self.logger.error(f"❌ Erreur génération __init__.py pour {domain}: {e}")
            return self.templates.get_minimal_init()

    def generate_class_content(
        self, class_name: str, domain: str, project_spec: Dict[str, Any]
    ) -> str:
        """Génère le contenu d'une classe spécifique."""
        try:
            context = self._prepare_class_context(class_name, domain, project_spec)
            template = self.templates.get_class_template()
            content = self.helpers.process_template(template, context)

            # Ajout des méthodes spécifiques au domaine
            methods = self.helpers.generate_domain_methods(domain, class_name)
            content = self.helpers.integrate_methods(content, methods)

            return self.helpers.optimize_content(content)

        except Exception as e:
            self.logger.error(f"❌ Erreur génération classe {class_name}: {e}")
            return self.templates.get_minimal_class(class_name)

    def generate_function_content(
        self, function_name: str, domain: str, project_spec: Dict[str, Any]
    ) -> str:
        """Génère le contenu d'une fonction spécifique."""
        try:
            context = self._prepare_function_context(
                function_name, domain, project_spec
            )
            template = self.templates.get_function_template()
            return self.helpers.process_template(template, context)

        except Exception as e:
            self.logger.error(f"❌ Erreur génération fonction {function_name}: {e}")
            return self.templates.get_minimal_function(function_name)

    def validate_generated_content(self, content: str, filename: str) -> bool:
        """Valide le contenu généré."""
        return self.helpers.validate_python_content(content, filename)

    def get_generation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de génération."""
        return {
            "files_generated": len(self.generated_files),
            "generated_files": list(self.generated_files),
            "cache_entries": len(self.context_cache),
            "templates_available": len(self.templates.get_all_templates()),
        }

    def _prepare_context(
        self, domain: str, filename: str, project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prépare le contexte pour génération."""
        cache_key = f"{domain}_{filename}"
        if cache_key in self.context_cache:
            return self.context_cache[cache_key]

        context = self.helpers.build_base_context(domain, filename, project_spec)
        context.update(self.helpers.get_domain_specific_context(domain, project_spec))

        self.context_cache[cache_key] = context
        return context

    def _prepare_main_context(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare le contexte pour le fichier main.py."""
        return self.helpers.build_main_context(project_spec)

    def _prepare_class_context(
        self, class_name: str, domain: str, project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prépare le contexte pour génération de classe."""
        return self.helpers.build_class_context(class_name, domain, project_spec)

    def _prepare_function_context(
        self, function_name: str, domain: str, project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prépare le contexte pour génération de fonction."""
        return self.helpers.build_function_context(function_name, domain, project_spec)

    def _generate_emergency_content(self, domain: str, filename: str) -> str:
        """Génère un contenu d'urgence en cas d'erreur."""
        return self.templates.get_emergency_template(domain, filename)

    def clear_cache(self):
        """Vide le cache de contexte."""
        self.context_cache.clear()

    def get_generated_files(self) -> Set[str]:
        """Retourne les fichiers générés."""
        return self.generated_files.copy()

    def __str__(self) -> str:
        """Représentation string de l'instance."""
        return f"PythonContentGenerator(files={len(self.generated_files)})"

    def __repr__(self) -> str:
        """Représentation debug de l'instance."""
        return f"PythonContentGenerator(helpers={self.helpers}, templates={self.templates})"