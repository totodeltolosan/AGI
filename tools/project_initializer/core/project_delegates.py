#!/usr/bin/env python3
"""
Project Delegates - Interface Principale pour Délégation d'Opérations AGI
==========================================================================

CHEMIN: tools/project_initializer/core/project_delegates.py

Version corrigée avec bonnes méthodes PathValidator
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import traceback

try:
    from .delegates_helpers import DelegatesHelpers
    from .delegates_config import DelegatesConfig
except ImportError as e:
    try:
        from delegates_helpers import DelegatesHelpers
        from delegates_config import DelegatesConfig
    except ImportError:
        raise ImportError(f"❌ Modules delegates refactorisés introuvables: {e}")


class ProjectDelegates:
    """Délégué principal pour opérations complexes de projet AGI."""

    def __init__(self, logger, orchestrator):
        """Initialise le délégué avec logger et référence à l'orchestrateur."""
        self.logger = logger
        self.orchestrator = orchestrator
        self.helpers = DelegatesHelpers(logger)
        self.config = DelegatesConfig()
        self.operation_cache: Dict[str, Any] = {}
        self.delegation_stats = {'operations': 0, 'successes': 0, 'errors': 0}

    def validate_project_inputs(self, output_dir: str, agi_md_path: str) -> bool:
        """Valide les paramètres d'entrée du projet avec PathValidator correct."""
        try:
            self.logger.info(f"🔍 Validation inputs: {output_dir}")
            
            # Utilisation correcte de PathValidator avec les vraies méthodes
            if hasattr(self.orchestrator, 'path_validator') and self.orchestrator.path_validator:
                try:
                    # Utiliser validate_safe_path (méthode qui existe)
                    safe_path_result = self.orchestrator.path_validator.validate_safe_path(output_dir)
                    if not safe_path_result:
                        self.logger.error(f"❌ Chemin non sécurisé: {output_dir}")
                        return False
                    
                    # Utiliser validate_directory_creation (méthode qui existe)
                    dir_creation_result = self.orchestrator.path_validator.validate_directory_creation(output_dir)
                    if not dir_creation_result:
                        self.logger.error(f"❌ Création répertoire impossible: {output_dir}")
                        return False
                    
                    self.logger.info("✅ Validation PathValidator réussie")
                    
                except Exception as validator_error:
                    self.logger.warning(f"⚠️ Erreur PathValidator, fallback: {validator_error}")
                    # Continuer avec validation basique
            
            # Validation basique en fallback ou complément
            output_path = Path(output_dir)
            
            # Créer le répertoire parent si nécessaire
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.error(f"❌ Impossible de créer répertoire parent: {e}")
                return False
            
            # Vérifier permissions
            if not os.access(output_path.parent, os.W_OK):
                self.logger.error(f"❌ Pas de permission d'écriture: {output_path.parent}")
                return False
            
            self.logger.info("✅ Validation inputs réussie")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur validation inputs: {e}")
            return False

    def parse_agi_report(self, agi_md_path: str) -> Dict[str, Any]:
        """Parse le rapport AGI.md via l'orchestrateur."""
        try:
            self.logger.info("📖 Parsing AGI.md")
            
            # Utilisation du parser de l'orchestrateur si disponible
            if hasattr(self.orchestrator, 'agi_parser') and self.orchestrator.agi_parser:
                try:
                    result = self.orchestrator.agi_parser.parse_report()
                    self.logger.info(f"✅ Parsing réussi: {len(result.get('domains', []))} domaines")
                    return result
                except Exception as parser_error:
                    self.logger.warning(f"⚠️ Erreur parser AGI, fallback: {parser_error}")
            
            # Fallback avec domaines par défaut
            fallback_result = {
                'domains': ['core', 'compliance', 'supervisor', 'generators', 'integration'],
                'project_name': 'Projet AGI',
                'version': '1.0',
                'description': 'Projet AGI généré automatiquement',
                'architecture': 'Modulaire'
            }
            
            self.logger.info(f"✅ Parsing fallback: {len(fallback_result['domains'])} domaines")
            return fallback_result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur parsing AGI.md: {e}")
            return {
                'domains': ['core', 'compliance'],
                'project_name': 'AGI Fallback',
                'version': '1.0'
            }

    def generate_all_files(
        self, output_dir: str, project_spec: Dict[str, Any], 
        excluded_domains: List[str], included_domains: List[str]
    ) -> bool:
        """Génère tous les fichiers du projet."""
        try:
            self.logger.info("🚀 Démarrage génération complète")
            
            # Filtrage des domaines
            all_domains = project_spec.get('domains', ['core', 'compliance'])
            domains = self._filter_domains(all_domains, excluded_domains, included_domains)
            
            self.logger.info(f"📁 Domaines à générer: {domains}")
            
            # Génération Python via orchestrateur
            python_success = self._generate_python_files(output_dir, domains, project_spec)
            
            # Génération des autres fichiers (non-bloquant)
            json_success = self._generate_json_files(output_dir, project_spec)
            markdown_success = self._generate_markdown_files(output_dir, project_spec)
            
            # Le succès est basé principalement sur Python
            overall_success = python_success
            
            if overall_success:
                self.logger.info("✅ Génération complète réussie")
            else:
                self.logger.warning("⚠️ Génération avec erreurs")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération complète: {e}")
            return False

    def get_python_files_for_domain(self, domain: str) -> List[str]:
        """Récupère la liste des fichiers Python pour un domaine."""
        try:
            files = self.helpers.get_domain_python_files(domain)
            return files
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération fichiers {domain}: {e}")
            return ['__init__.py', f'{domain}_manager.py']

    def _filter_domains(
        self, all_domains: List[str], excluded: List[str], included: List[str]
    ) -> List[str]:
        """Filtre les domaines selon les critères."""
        if included:
            filtered = [d for d in all_domains if d in included]
            self.logger.info(f"🔍 Filtrage par inclusion: {filtered}")
            return filtered
        if excluded:
            filtered = [d for d in all_domains if d not in excluded]
            self.logger.info(f"🔍 Filtrage par exclusion: {filtered}")
            return filtered
        return all_domains

    def _generate_python_files(self, output_dir: str, domains: List[str], project_spec: Dict[str, Any]) -> bool:
        """Génère les fichiers Python."""
        try:
            success_count = 0
            
            if hasattr(self.orchestrator, 'python_generator') and self.orchestrator.python_generator:
                # Génération par domaine
                for domain in domains:
                    try:
                        if self.orchestrator.python_generator.generate_domain_files(output_dir, domain, project_spec):
                            success_count += 1
                            self.logger.info(f"✅ Domaine {domain}: fichiers générés")
                        else:
                            self.logger.warning(f"⚠️ Domaine {domain}: échec génération")
                    except Exception as domain_error:
                        self.logger.error(f"❌ Erreur domaine {domain}: {domain_error}")
                
                # Génération du main.py
                try:
                    main_success = self.orchestrator.python_generator.generate_main_file(output_dir, project_spec)
                    if main_success:
                        self.logger.info("✅ main.py généré")
                    else:
                        self.logger.warning("⚠️ main.py échec")
                except Exception as main_error:
                    self.logger.error(f"❌ Erreur main.py: {main_error}")
                    main_success = False
                
                total_success = success_count > 0 or main_success
                self.logger.info(f"🐍 Python: {success_count}/{len(domains)} domaines, main.py: {main_success}")
                return total_success
            
            self.logger.error("❌ Pas de générateur Python disponible")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération Python: {e}")
            return False

    def _generate_json_files(self, output_dir: str, project_spec: Dict[str, Any]) -> bool:
        """Génère les fichiers JSON si disponible."""
        try:
            if hasattr(self.orchestrator, 'json_generator') and self.orchestrator.json_generator:
                success = self.orchestrator.json_generator.generate_rules_json(Path(output_dir))
                self.logger.info(f"📄 JSON: {'✅ réussi' if success else '⚠️ échec'}")
                return success
            
            self.logger.info("📄 JSON: générateur non disponible (non-bloquant)")
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur génération JSON (non-bloquant): {e}")
            return True

    def _generate_markdown_files(self, output_dir: str, project_spec: Dict[str, Any]) -> bool:
        """Génère les fichiers Markdown si disponible."""
        try:
            if hasattr(self.orchestrator, 'markdown_generator') and self.orchestrator.markdown_generator:
                success = self.orchestrator.markdown_generator.generate_main_readme(Path(output_dir))
                self.logger.info(f"📝 Markdown: {'✅ réussi' if success else '⚠️ échec'}")
                return success
            
            self.logger.info("📝 Markdown: générateur non disponible (non-bloquant)")
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur génération Markdown (non-bloquant): {e}")
            return True

    def get_delegation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de délégation."""
        return self.delegation_stats.copy()

    def __str__(self) -> str:
        """TODO: Add docstring."""
        return f"ProjectDelegates(operations={self.delegation_stats['operations']})"

    """TODO: Add docstring."""
    def __repr__(self) -> str:
        return f"ProjectDelegates(helpers={self.helpers}, config={self.config})"