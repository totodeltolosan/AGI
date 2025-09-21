#!/usr/bin/env python3
"""
Delegates Config - Configuration et Données pour Délégation d'Opérations
=========================================================================

CHEMIN: tools/project_initializer/core/delegates_config.py

Rôle Fondamental :
- Configuration des opérations de délégation AGI
- Règles et paramètres pour orchestration
- Mapping domaines vers fichiers et opérations
- Plans d'exécution et fallbacks

Conformité Architecturale :
- Module config délégué depuis project_delegates.py
- Limite stricte < 200 lignes ✅
- Données statiques et configuration

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
"""

from typing import Dict, List, Any, Optional


class DelegatesConfig:
    """Configuration pour délégation d'opérations de projet AGI."""

    def __init__(self):
        """TODO: Add docstring."""
        self.domain_configurations = self._initialize_domain_configurations()
        self.generation_rules = self._initialize_generation_rules()
        self.validation_rules = self._initialize_validation_rules()
        self.orchestration_templates = self._initialize_orchestration_templates()
        self.fallback_configs = self._initialize_fallback_configs()

    def get_domain_configuration(self, domain: str) -> Dict[str, Any]:
        """Récupère la configuration d'un domaine spécifique."""
        return self.domain_configurations.get(domain, self._get_default_domain_config())

    def get_generation_rules(self) -> Dict[str, Any]:
        """Récupère les règles de génération."""
        return self.generation_rules.copy()

    def get_default_validation_rules(self) -> Dict[str, Any]:
        """Récupère les règles de validation par défaut."""
        return self.validation_rules.copy()

    def get_files_for_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Récupère les spécifications de fichiers pour un domaine."""
        domain_config = self.get_domain_configuration(domain)
        return domain_config.get('files', [])

    def get_default_files_for_domain(self, domain: str) -> List[str]:
        """Récupère les fichiers par défaut pour un domaine."""
        return [f'{domain}_manager.py', f'{domain}_config.py', '__init__.py']

    def apply_file_filters(self, domain: str, files: List[str]) -> List[str]:
        """Applique les filtres de fichiers pour un domaine."""
        domain_config = self.get_domain_configuration(domain)
        filters = domain_config.get('file_filters', [])
        
        filtered_files = files.copy()
        
        for filter_rule in filters:
            if filter_rule['type'] == 'exclude':
                filtered_files = [f for f in filtered_files if f not in filter_rule['patterns']]
            elif filter_rule['type'] == 'include_only':
                filtered_files = [f for f in filtered_files if f in filter_rule['patterns']]
        
        return filtered_files

    def get_orchestration_plan(
        self, output_dir: str, project_spec: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Génère un plan d'orchestration."""
        plan = {}
        
        # Phase 1: Création structure
        plan['structure_creation'] = {
            'type': 'structure_creation',
            'critical': True,
            'config': {
                'output_dir': output_dir,
                'domains': project_spec.get('domains', []),
                'create_base_dirs': True
            }
        }
        
        # Phase 2: Génération fichiers
        plan['file_generation'] = {
            'type': 'file_generation',
            'critical': True,
            'config': {
                'output_dir': output_dir,
                'project_spec': project_spec,
                'generation_mode': options.get('mode', 'standard')
            }
        }
        
        # Phase 3: Validation
        plan['validation'] = {
            'type': 'validation',
            'critical': False,
            'config': {
                'strict_mode': options.get('strict', False),
                'validation_rules': self.get_default_validation_rules()
            }
        }
        
        # Phase 4: Finalisation
        plan['finalization'] = {
            'type': 'finalization',
            'critical': False,
            'config': {
                'cleanup': options.get('cleanup', True),
                'generate_summary': True
            }
        }
        
        return plan

    def get_fallback_generation_results(self) -> Dict[str, Any]:
        """Résultats de fallback pour génération."""
        return self.fallback_configs['generation_results']

    def get_fallback_domain_results(self, domain: str) -> Dict[str, Any]:
        """Résultats de fallback pour un domaine."""
        return {
            'success': False,
            'domain': domain,
            'files_created': [],
            'error': 'Fallback result - operation failed'
        }

    def get_fallback_orchestration_results(self) -> Dict[str, Any]:
        """Résultats de fallback pour orchestration."""
        return self.fallback_configs['orchestration_results']

    def validate_config_integrity(self) -> bool:
        """Valide l'intégrité de la configuration."""
        try:
            # Vérifications de base
            required_configs = [
                'domain_configurations',
                'generation_rules',
                'validation_rules',
                'orchestration_templates'
            ]
            
            for config_name in required_configs:
                if not hasattr(self, config_name):
                    return False
            
            # Vérification cohérence domaines
            for domain, config in self.domain_configurations.items():
                if not isinstance(config, dict):
                    return False
                
                required_keys = ['priority', 'files']
                if not all(key in config for key in required_keys):
                    return False
            
            return True
            
        except Exception:
            return False

    def _initialize_domain_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les configurations par domaine."""
        return {
            'core': {
                'priority': 1,
                'critical': True,
                'files': [
                    {'name': '__init__.py', 'type': 'init', 'required': True},
                    {'name': 'orchestrator.py', 'type': 'manager', 'required': True},
                    {'name': 'interfaces.py', 'type': 'interface', 'required': True},
                    {'name': 'base_classes.py', 'type': 'base', 'required': False}
                ],
                'file_filters': [],
                'dependencies': []
            },
            
            'compliance': {
                'priority': 2,
                'critical': True,
                'files': [
                    {'name': '__init__.py', 'type': 'init', 'required': True},
                    {'name': 'validator.py', 'type': 'validator', 'required': True},
                    {'name': 'rules_engine.py', 'type': 'engine', 'required': True},
                    {'name': 'reporter.py', 'type': 'reporter', 'required': False}
                ],
                'file_filters': [],
                'dependencies': ['core']
            },
            
            'generators': {
                'priority': 5,
                'critical': False,
                'files': [
                    {'name': '__init__.py', 'type': 'init', 'required': True},
                    {'name': 'code_generator.py', 'type': 'generator', 'required': True},
                    {'name': 'template_engine.py', 'type': 'engine', 'required': True},
                    {'name': 'parser.py', 'type': 'parser', 'required': False}
                ],
                'file_filters': [],
                'dependencies': ['core']
            },
            
            'supervisor': {
                'priority': 3,
                'critical': True,
                'files': [
                    {'name': '__init__.py', 'type': 'init', 'required': True},
                    {'name': 'monitor.py', 'type': 'monitor', 'required': True},
                    {'name': 'controller.py', 'type': 'controller', 'required': True},
                    {'name': 'coordinator.py', 'type': 'coordinator', 'required': False}
                ],
                'file_filters': [],
                'dependencies': ['core', 'compliance']
            },
            
            'integration': {
                'priority': 6,
                'critical': False,
                'files': [
                    {'name': '__init__.py', 'type': 'init', 'required': True},
                    {'name': 'api_client.py', 'type': 'client', 'required': True},
                    {'name': 'connector.py', 'type': 'connector', 'required': True},
                    {'name': 'adapter.py', 'type': 'adapter', 'required': False}
                ],
                'file_filters': [],
                'dependencies': ['core']
            }
        }

    def _initialize_generation_rules(self) -> Dict[str, Any]:
        """Initialise les règles de génération."""
        return {
            'max_lines_per_file': 200,
            'encoding': 'utf-8',
            'add_type_hints': True,
            'add_docstrings': True,
            'add_logging': True,
            'create_init_files': True,
            'validate_syntax': True,
            'auto_format': True,
            'backup_existing': False,
            'overwrite_policy': 'ask',
            'template_style': 'agi_standard',
            'import_style': 'relative',
            'error_handling': 'comprehensive'
        }

    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialise les règles de validation."""
        return {
            'max_lines': 200,
            'require_docstrings': True,
            'require_type_hints': True,
            'check_syntax': True,
            'check_imports': True,
            'check_encoding': True,
            'allowed_extensions': ['.py'],
            'forbidden_patterns': ['eval(', 'exec(', '__import__'],
            'required_headers': ['#!/usr/bin/env python3', '"""'],
            'strict_mode': False,
            'auto_fix': False
        }

    def _initialize_orchestration_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les templates d'orchestration."""
        return {
            'standard': {
                'phases': ['structure_creation', 'file_generation', 'validation', 'finalization'],
                'parallel_execution': False,
                'continue_on_error': False,
                'timeout_minutes': 30
            },
            
            'fast': {
                'phases': ['structure_creation', 'file_generation'],
                'parallel_execution': True,
                'continue_on_error': True,
                'timeout_minutes': 10
            },
            
            'comprehensive': {
                'phases': [
                    'structure_creation', 
                    'file_generation', 
                    'validation', 
                    'testing', 
                    'documentation',
                    'finalization'
                ],
                'parallel_execution': False,
                'continue_on_error': False,
                'timeout_minutes': 60
            }
        }

    def _initialize_fallback_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les configurations de fallback."""
        return {
            'generation_results': {
                'success': False,
                'domains_processed': 0,
                'files_generated': 0,
                'errors': ['Fallback: Operation failed'],
                'domain_results': {}
            },
            
            'orchestration_results': {
                'overall_success': False,
                'total_phases': 0,
                'successful_phases': 0,
                'failed_phases': 0,
                'error': 'Fallback: Orchestration failed'
            }
        }

    def _get_default_domain_config(self) -> Dict[str, Any]:
        """Configuration de domaine par défaut."""
        return {
            'priority': 10,
            'critical': False,
            'files': [
                {'name': '__init__.py', 'type': 'init', 'required': True},
                {'name': 'manager.py', 'type': 'manager', 'required': True}
            ],
            'file_filters': [],
            'dependencies': ['core']
        }

    def get_domain_priorities(self) -> Dict[str, int]:
        """Récupère les priorités des domaines."""
        priorities = {}
        for domain, config in self.domain_configurations.items():
            priorities[domain] = config.get('priority', 10)
        return priorities

    def get_critical_domains(self) -> List[str]:
        """Récupère la liste des domaines critiques."""
        critical_domains = []
        for domain, config in self.domain_configurations.items():
            if config.get('critical', False):
                critical_domains.append(domain)
        return critical_domains

    def get_domain_dependencies(self, domain: str) -> List[str]:
        """Récupère les dépendances d'un domaine."""
        domain_config = self.get_domain_configuration(domain)
        return domain_config.get('dependencies', [])

    def get_execution_order(self, domains: List[str]) -> List[str]:
        """Détermine l'ordre d'exécution des domaines."""
        priorities = self.get_domain_priorities()
        
        # Tri par priorité (plus petit = plus prioritaire)
        sorted_domains = sorted(domains, key=lambda d: priorities.get(d, 10))
        
        return sorted_domains

    def get_orchestration_template(self, template_name: str) -> Dict[str, Any]:
        """Récupère un template d'orchestration."""
        return self.orchestration_templates.get(template_name, self.orchestration_templates['standard'])

    def get_supported_file_types(self) -> List[str]:
        """Récupère les types de fichiers supportés."""
        return ['init', 'manager', 'validator', 'generator', 'parser', 'config', 'interface', 'base']

    def get_file_type_template(self, file_type: str) -> Dict[str, Any]:
        """Récupère le template pour un type de fichier."""
        templates = {
            'init': {'has_content': False, 'imports_required': False},
            'manager': {'has_content': True, 'imports_required': True, 'base_class': 'BaseManager'},
            'validator': {'has_content': True, 'imports_required': True, 'base_class': 'BaseValidator'},
            'generator': {'has_content': True, 'imports_required': True, 'base_class': 'BaseGenerator'},
            'parser': {'has_content': True, 'imports_required': True, 'base_class': 'BaseParser'},
            'config': {'has_content': True, 'imports_required': False},
            'interface': {'has_content': True, 'imports_required': True, 'base_class': 'ABC'},
            'base': {'has_content': True, 'imports_required': True, 'base_class': 'ABC'}
        }
        
        return templates.get(file_type, templates['manager'])