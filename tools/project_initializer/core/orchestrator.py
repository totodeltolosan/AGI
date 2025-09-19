#!/usr/bin/env python3
"""
Orchestrateur Principal du Générateur AGI
Coordonne la création complète du squelette de projet AGI
Conforme à AGI.md - Limite stricte: <200 lignes
"""

import sys
from pathlib import Path
from typing import List, Optional, Union, Dict, Any


class ProjectOrchestrator:
    """
    Orchestrateur principal pour la génération de projets AGI conformes.
    Délègue les opérations complexes aux modules helpers.
    """

    def __init__(self, logger):
        """Initialise l'orchestrateur avec logger et composants requis."""
        self.logger = logger
        self.path_validator = None
        self.agi_parser = None
        self.structure_generator = None
        self.python_generator = None
        self.json_generator = None
        self.markdown_generator = None

        # Délégué pour les opérations complexes
        self.delegate = None

        self._initialize_components()

    def _initialize_components(self):
        """Initialise tous les composants nécessaires avec gestion d'erreurs."""
        try:
            # PathValidator avec logger (correction critique)
            from validators.paths import PathValidator

            self.path_validator = PathValidator(self.logger)

            # Parser AGI
            from parsers.agi_parser import AGIReportParser

            # Générateur structure
            from structure_generator import StructureGenerator

            self.structure_generator = StructureGenerator(self.logger)

            # Générateurs de fichiers
            from file_generators.python_generator import PythonGenerator

            self.python_generator = PythonGenerator(self.logger)

            # Générateurs optionnels
            try:
                from file_generators.json_generator import JSONGenerator

                self.json_generator = JSONGenerator(self.logger)
            except ImportError:
                self.logger.info("JSONGenerator non disponible")

            try:
                from file_generators.markdown_generator import MarkdownGenerator

                self.markdown_generator = MarkdownGenerator(self.logger)
            except ImportError:
                self.logger.info("MarkdownGenerator non disponible")

            # Délégué pour opérations complexes (refactorisation)
            from core.project_delegates import ProjectDelegates

            self.delegate = ProjectDelegates(self.logger, self)

            self.logger.debug("✅ Composants orchestrateur initialisés")

        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation composants: {str(e)}")
            raise

    def generate_project(
        self,
        output_dir: str,
        agi_md_path: str,
        excluded_domains: List[str] = None,
        included_domains: List[str] = None,
    ) -> bool:
        """
        Génère un projet AGI complet selon les directives d'AGI.md.

        Returns:
            bool: True si génération réussie, False sinon
        """
        try:
            self.logger.info("🚀 Démarrage génération projet AGI")

            # Validation via délégué
            if not self.delegate.validate_project_inputs(output_dir, agi_md_path):
                return False

            # Parsing via délégué
            project_spec = self.delegate.parse_agi_report(agi_md_path)
            if not project_spec:
                return False

            # Génération arborescence
            self.logger.info("📁 Génération de l'arborescence de répertoires")
            if not self.structure_generator.create_directories(output_dir, project_spec.get("domains", [])):
                self.logger.error("❌ Échec génération arborescence")
                return False

            # Génération fichiers via délégué
            success = self.delegate.generate_all_files(
                output_dir, project_spec, excluded_domains, included_domains
            )

            if success:
                self.logger.info("✅ Projet AGI généré avec succès")
            else:
                self.logger.error("❌ Génération projet partiellement échouée")

            return success

        except Exception as e:
            self.logger.error(f"❌ Erreur génération projet: {str(e)}")
            return False

    def get_python_files_for_domain(self, domain: str) -> List[str]:
        """Récupère la liste des fichiers Python pour un domaine."""
        try:
            from config.python_files import get_files_for_domain

            return get_files_for_domain(domain)
        except ImportError:
            return [f"{domain}_main.py"]

    def filter_domains(
        self, all_domains: List[str], excluded: List[str], included: List[str]
    ) -> List[str]:
        """Filtre les domaines selon les critères d'inclusion/exclusion."""
        if included:
            return [d for d in all_domains if d in included]
        if excluded:
            return [d for d in all_domains if d not in excluded]
        return all_domains
