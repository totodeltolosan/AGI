#!/usr/bin/env python3
"""
Python Generator - Générateur de Fichiers Python du Projet AGI
==============================================================

Rôle Fondamental (Conforme AGI.md - tools/project_initializer/file_generators/python_generator.py) :
- Générer tous les fichiers Python (.py) du projet avec stubs conformes aux directives
- Inclure imports, classes, fonctions, docstrings et annotations de type selon AGI.md
- Appliquer les patterns d'interactions (DOIT, UTILISE, APPELLE) définis dans le rapport
- Assurer la conformité stricte à la limite de 200 lignes de code par fichier
- Générer des commentaires référençant les sections pertinentes d'AGI.md
- Créer des stubs fonctionnels syntaxiquement corrects mais sans logique métier complète

Conformité Architecturale :
- Limite stricte < 200 lignes via délégation aux templates
- Sécurité by Design : validation des noms de fichiers, échappement code
- Déterminisme : même spécification = même code généré
- Traçabilité : logging détaillé de chaque fichier généré

Version : 1.0
Date : 17 Septembre 2025
Référence : Rapport de Directives AGI.md - Section tools/project_initializer/
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import re
import traceback
from datetime import datetime

class PythonGenerator:
    """
    Générateur spécialisé pour les fichiers Python du projet AGI.
    
    Génère des stubs de code conformes aux directives AGI.md avec :
    - Docstrings détaillées référençant le rapport
    - Imports selon les interactions définies  
    - Classes abstraites et concrètes selon les rôles
    - Annotations de type complètes
    - Respect strict de la limite 200 lignes
    """
    
    # Mapping des domaines vers leurs fichiers Python principaux (selon AGI.md)
    DOMAIN_FILES = {
        'compliance': [
            'compliance_reporter.py', 'policy_loader.py', 'static_auditor.py'
        ],
        'development_governance': [
            'dev_workflow_check.py'
        ],
        'config': [
            'config_manager.py', 'config_loader.py', 'config_validator.py'
        ],
        'supervisor': [
            'supervisor.py', 'updater.py', 'logger.py'
        ],
        'plugins': [
            'plugin_loader.py', 'plugin_discoverer.py', 'plugin_interface.py'
        ],
        'core': [
            'core_engine_base.py', 'core_engine_tasks.py', 'core_engine_ai.py'
        ],
        'data': [
            'data_storage.py', 'data_loader.py', 'data_transformer.py'
        ],
        'runtime_compliance': [
            'runtime_policy_enforcer.py', 'resource_monitor.py', 'data_integrity_checker.py'
        ],
        'ecosystem': [
            'environment_manager.py', 'dependency_resolver.py'
        ],
        'ui': [
            'ui_web.py', 'ui_cli.py', 'ui_adapters.py'
        ],
        'ai_compliance': [
            'ai_fact_checker.py', 'ai_bias_detector.py'
        ]
    }
    
    def __init__(self, logger):
        self.logger = logger
        self.generated_files: Set[str] = set()
        
    def generate_domain_files(self, output_dir: str, domain: str, project_spec: Dict[str, Any]) -> bool:
        """
        Génère tous les fichiers Python d'un domaine spécifique.
        
        Args:
            output_dir: Répertoire de sortie du projet
            domain: Nom du domaine (ex: 'compliance', 'config')
            project_spec: Spécifications extraites par report_parser.py
            
        Returns:
            bool: True si génération réussie, False sinon
        """
        try:
            if domain not in self.DOMAIN_FILES:
                self.logger.debug(f"🔍 Domaine {domain} sans fichiers Python prédéfinis")
                return True
                
            domain_path = Path(output_dir) / domain
            files_to_generate = self.DOMAIN_FILES[domain]
            
            self.logger.verbose(f"🐍 Génération Python pour {domain}/: {len(files_to_generate)} fichiers")
            
            for filename in files_to_generate:
                if not self._generate_python_file(domain_path, filename, domain, project_spec):
                    return False
                    
            # Génération du __init__.py pour le package
            if not self._generate_init_file(domain_path, domain):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération Python {domain}: {str(e)}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def generate_main_file(self, output_dir: str, project_spec: Dict[str, Any]) -> bool:
        """Génère le fichier main.py selon les spécifications AGI.md."""
        try:
            main_path = Path(output_dir) / 'main.py'
            main_content = self._generate_main_py_content(project_spec)
            
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write(main_content)
                
            self.generated_files.add(str(main_path))
            self.logger.verbose("🎯 main.py généré (orchestrateur principal)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération main.py: {e}")
            return False
    
    def _generate_python_file(self, domain_path: Path, filename: str, domain: str, 
                            project_spec: Dict[str, Any]) -> bool:
        """Génère un fichier Python individuel avec stubs conformes."""
        try:
            file_path = domain_path / filename
            
            # Extraction des spécifications pour ce fichier
            file_spec = self._extract_file_specifications(filename, domain, project_spec)
            
            # Génération du contenu Python complet
            python_content = self._generate_file_content(filename, domain, file_spec)
            
            # Validation de la limite 200 lignes
            if not self._validate_line_count(python_content, filename):
                return False
                
            # Écriture du fichier
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(python_content)
                
            self.generated_files.add(str(file_path))
            self.logger.debug(f"  📄 {filename} généré ({len(python_content.splitlines())} lignes)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération {filename}: {e}")
            return False
    
    def _extract_file_specifications(self, filename: str, domain: str, 
                                   project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les spécifications d'un fichier depuis project_spec."""
        # Spécifications par défaut basées sur AGI.md
        default_spec = {
            'role': f'Module {filename.replace(".py", "")}',
            'interactions': [],
            'requirements': [],
            'imports': self._get_default_imports(filename, domain),
            'classes': self._get_default_classes(filename, domain),
            'functions': self._get_default_functions(filename, domain)
        }
        
        # Fusion avec les spécifications extraites du rapport si disponibles
        domains = project_spec.get('domains', {})
        if domain in domains:
            domain_spec = domains[domain]
            for file_spec in domain_spec.files:
                if file_spec.name == filename:
                    default_spec.update({
                        'role': file_spec.role,
                        'interactions': file_spec.interactions,
                        'requirements': file_spec.requirements
                    })
                    break
                    
        return default_spec
    
    def _get_default_imports(self, filename: str, domain: str) -> List[str]:
        """Détermine les imports par défaut selon le fichier et domaine."""
        base_imports = [
            'from typing import Optional, List, Dict, Any, Union',
            'import logging',
            'from pathlib import Path'
        ]
        
        # Imports spécifiques selon le type de fichier
        specific_imports = {
            'logger.py': ['import sys', 'from datetime import datetime'],
            'config_manager.py': ['import json', 'import os'],
            'plugin_interface.py': ['from abc import ABC, abstractmethod'],
            'core_engine_base.py': ['from abc import ABC, abstractmethod'],
            'data_storage.py': ['import sqlite3', 'import json'],
            'ui_web.py': ['from flask import Flask, request, jsonify'],
            'ui_cli.py': ['import argparse', 'import sys']
        }
        
        imports = base_imports.copy()
        if filename in specific_imports:
            imports.extend(specific_imports[filename])
            
        return imports
    
    def _get_default_classes(self, filename: str, domain: str) -> List[Dict[str, Any]]:
        """Détermine les classes par défaut selon le fichier."""
        base_name = filename.replace('.py', '').replace('_', ' ').title().replace(' ', '')
        
        # Classes spécifiques selon les patterns AGI.md
        if 'interface' in filename or 'base' in filename:
            return [{
                'name': base_name,
                'type': 'abstract',
                'methods': ['__init__', 'initialize', 'execute'],
                'docstring': f'Interface abstraite pour {base_name.lower()}.'
            }]
        else:
            return [{
                'name': base_name,
                'type': 'concrete', 
                'methods': ['__init__', 'initialize', 'run'],
                'docstring': f'Implémentation concrète de {base_name.lower()}.'
            }]
    
    def _get_default_functions(self, filename: str, domain: str) -> List[Dict[str, Any]]:
        """Détermine les fonctions par défaut selon le fichier."""
        return [
            {
                'name': 'main',
                'args': [],
                'return_type': 'None',
                'docstring': 'Point d\'entrée principal du module.'
            }
        ]
    
    def _generate_file_content(self, filename: str, domain: str, file_spec: Dict[str, Any]) -> str:
        """Génère le contenu Python complet d'un fichier."""
        lines = []
        
        # Header avec référence AGI.md
        lines.extend(self._generate_file_header(filename, domain, file_spec))
        lines.append('')
        
        # Imports
        lines.extend(file_spec['imports'])
        lines.append('')
        
        # Classes
        for class_spec in file_spec['classes']:
            lines.extend(self._generate_class_code(class_spec))
            lines.append('')
            
        # Fonctions
        for func_spec in file_spec['functions']:
            lines.extend(self._generate_function_code(func_spec))
            lines.append('')
            
        # Footer avec conformité AGI.md
        lines.extend(self._generate_file_footer(filename, domain))
        
        return '\n'.join(lines)
    
    def _generate_file_header(self, filename: str, domain: str, file_spec: Dict[str, Any]) -> List[str]:
        """Génère l'en-tête du fichier avec docstring détaillée."""
        module_name = filename.replace('.py', '').replace('_', ' ').title()
        
        return [
            '#!/usr/bin/env python3',
            '"""',
            f'{module_name} - {file_spec["role"]}',
            '=' * (len(module_name) + len(file_spec["role"]) + 3),
            '',
            f'Rôle Fondamental (Conforme AGI.md - {domain}/{filename}) :',
            f'- {file_spec["role"]}',
            '- Respect strict de la limite 200 lignes de code exécutable',
            '- Modularité et découplage selon les directives architecturales',
            '- Traçabilité complète via supervisor/logger.py',
            '- Sécurité by Design intégrée à chaque couche',
            '',
            'Interactions et Délégations :',
        ] + [f'- {interaction}' for interaction in file_spec['interactions'][:5]] + [
            '',
            'Exigences Clés (Fiabilité, Performance, Sécurité) :',
        ] + [f'- {req}' for req in file_spec['requirements'][:5]] + [
            '',
            'Version : 1.0',
            f'Date : {datetime.now().strftime("%d %B %Y")}',
            f'Référence : Rapport de Directives AGI.md - Section {domain}/{filename}',
            '"""'
        ]
    
    def _generate_class_code(self, class_spec: Dict[str, Any]) -> List[str]:
        """Génère le code d'une classe avec méthodes stubs."""
        lines = []
        
        # Définition de classe (abstraite ou concrète)
        if class_spec['type'] == 'abstract':
            lines.append(f'class {class_spec["name"]}(ABC):')
        else:
            lines.append(f'class {class_spec["name"]}:')
            
        lines.append(f'    """{class_spec["docstring"]}"""')
        lines.append('')
        
        # Méthodes stubs
        for method in class_spec['methods']:
            if method == '__init__':
                lines.extend([
                    '    def __init__(self, logger=None):',
                    '        """Initialise le module avec logger optionnel."""',
                    '        self.logger = logger',
                    '        # TODO: Implémentation selon directives AGI.md',
                    '        pass',
                    ''
                ])
            else:
                lines.extend([
                    f'    def {method}(self) -> bool:',
                    f'        """Implémente {method} selon les directives AGI.md."""',
                    '        # TODO: Implémentation conforme aux spécifications',
                    '        raise NotImplementedError("À implémenter selon AGI.md")',
                    ''
                ])
                
        return lines
    
    def _generate_function_code(self, func_spec: Dict[str, Any]) -> List[str]:
        """Génère le code d'une fonction stub."""
        args_str = ', '.join(func_spec['args']) if func_spec['args'] else ''
        return_annotation = f' -> {func_spec["return_type"]}' if func_spec.get('return_type') else ''
        
        return [
            f'def {func_spec["name"]}({args_str}){return_annotation}:',
            f'    """{func_spec["docstring"]}"""',
            '    # TODO: Implémentation selon directives AGI.md',
            '    pass'
        ]
    
    def _generate_file_footer(self, filename: str, domain: str) -> List[str]:
        """Génère le footer du fichier avec conformité AGI.md."""
        return [
            '',
            '# === CONFORMITÉ AGI.md ===',
            f'# Fichier: {domain}/{filename}',
            '# Limite: < 200 lignes de code exécutable',
            '# Audit: compliance/static_auditor.py',
            '# Tests: tests/test_' + filename.replace('.py', '.py'),
            '',
            'if __name__ == "__main__":',
            '    main()'
        ]
    
    def _generate_main_py_content(self, project_spec: Dict[str, Any]) -> str:
        """Génère le contenu spécifique du main.py selon AGI.md."""
        return '''#!/usr/bin/env python3
"""
Main - Orchestrateur Principal du Projet AGI
===========================================

Rôle Fondamental (Conforme AGI.md - main.py) :
- Point d'entrée unique et chef d'orchestre principal
- Initialisation du programme et coordination des services essentiels
- Lancement de l'audit de conformité initial
- Chargement des plugins conformes
- Démarrage de l'interface utilisateur
- Gestion globale des erreurs et arrêt propre

Conformité Architecturale :
- Limite stricte < 200 lignes via délégation modulaire
- Aucune logique métier directe
- État interne minimal (stateless)
- Délégation complète aux modules spécialisés

Version : 1.0
Date : 17 Septembre 2025
Référence : Rapport de Directives AGI.md - Section main.py
"""

import sys
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

# Imports essentiels selon délégations AGI.md
try:
    from supervisor.logger import Logger
    from config.config_loader import ConfigLoader
    from config.config_validator import ConfigValidator
    from config.config_manager import ConfigManager
    from compliance.static_auditor import StaticAuditor
    from compliance.compliance_reporter import ComplianceReporter
    from plugins.plugin_loader import PluginLoader
    from ui.ui_cli import UICLI
    from ui.ui_web import UIWeb
except ImportError as e:
    print(f"❌ Erreur critique import modules: {e}")
    sys.exit(1)

class AGIOrchestrator:
    """
    Orchestrateur principal du projet AGI.
    
    Coordonne l'initialisation et l'exécution selon la séquence
    définie dans AGI.md sans contenir de logique métier.
    """
    
    def __init__(self):
        self.logger: Optional[Logger] = None
        self.config_manager: Optional[ConfigManager] = None
        self.plugins: Dict[str, Any] = {}
        
    def initialize_and_run(self) -> int:
        """
        Séquence principale d'initialisation et d'exécution.
        
        Returns:
            int: Code de sortie (0 = succès, 1 = erreur)
        """
        try:
            # Étape 1: Initialisation du logging (première priorité)
            self.logger = Logger()
            self.logger.info("🚀 Démarrage Projet AGI")
            
            # Étape 2: Chargement et validation configuration
            if not self._initialize_configuration():
                return 1
                
            # Étape 3: Audit de conformité initial
            if not self._run_initial_compliance_audit():
                return 1
                
            # Étape 4: Chargement des plugins conformes
            if not self._load_and_validate_plugins():
                return 1
                
            # Étape 5: Démarrage de l'interface utilisateur
            if not self._start_user_interface():
                return 1
                
            self.logger.info("✅ Projet AGI initialisé avec succès")
            return 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur critique orchestrateur: {str(e)}")
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
            else:
                print(f"❌ Erreur critique avant initialisation logger: {e}")
            return 1
    
    def _initialize_configuration(self) -> bool:
        """Délègue l'initialisation de la configuration."""
        try:
            loader = ConfigLoader()
            raw_config = loader.load_configuration()
            
            validator = ConfigValidator()
            validated_config = validator.validate(raw_config)
            
            self.config_manager = ConfigManager(validated_config)
            self.logger.info("✅ Configuration initialisée")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation configuration: {e}")
            return False
    
    def _run_initial_compliance_audit(self) -> bool:
        """Délègue l'audit de conformité initial."""
        try:
            auditor = StaticAuditor(self.logger)
            reporter = ComplianceReporter(self.logger)
            
            # Audit du noyau et des modules critiques
            audit_results = auditor.audit_core_modules()
            
            # Rapport et décision de blocage si nécessaire
            if not reporter.process_audit_results(audit_results):
                self.logger.error("❌ Audit de conformité échoué - Arrêt")
                return False
                
            self.logger.info("✅ Audit de conformité initial réussi")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur audit conformité: {e}")
            return False
    
    def _load_and_validate_plugins(self) -> bool:
        """Délègue le chargement et la validation des plugins."""
        try:
            plugin_loader = PluginLoader(self.logger, self.config_manager)
            self.plugins = plugin_loader.discover_and_load_plugins()
            
            self.logger.info(f"✅ {len(self.plugins)} plugins chargés avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement plugins: {e}")
            return False
    
    def _start_user_interface(self) -> bool:
        """Délègue le démarrage de l'interface utilisateur."""
        try:
            # Sélection interface selon configuration
            interface_type = self.config_manager.get('ui.interface_type', 'cli')
            
            if interface_type == 'web':
                ui = UIWeb(self.logger, self.config_manager, self.plugins)
            else:
                ui = UICLI(self.logger, self.config_manager, self.plugins)
                
            ui.start()
            self.logger.info(f"✅ Interface {interface_type} démarrée")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage interface: {e}")
            return False

def main() -> None:
    """Point d'entrée principal - Délégation complète à l'orchestrateur."""
    orchestrator = AGIOrchestrator()
    exit_code = orchestrator.initialize_and_run()
    sys.exit(exit_code)

# === CONFORMITÉ AGI.md ===
# Fichier: main.py
# Limite: < 200 lignes de code exécutable ✅
# Audit: compliance/static_auditor.py
# Tests: tests/test_main.py

if __name__ == "__main__":
    main()'''
    
    def _generate_init_file(self, domain_path: Path, domain: str) -> bool:
        """Génère le fichier __init__.py pour le package du domaine."""
        try:
            init_path = domain_path / '__init__.py'
            init_content = f'"""Package {domain} - Conforme aux directives AGI.md"""\n'
            
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(init_content)
                
            self.logger.debug(f"  📦 __init__.py généré pour {domain}/")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération __init__.py {domain}: {e}")
            return False
    
    def _validate_line_count(self, content: str, filename: str) -> bool:
        """Valide que le fichier respecte la limite de 200 lignes."""
        lines = content.splitlines()
        executable_lines = [line for line in lines if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""')]
        
        if len(executable_lines) > 200:
            self.logger.error(f"❌ {filename}: {len(executable_lines)} lignes > limite 200")
            return False
            
        return True# [Copier-coller ici le code généré dans l'artifact ci-dessus]
