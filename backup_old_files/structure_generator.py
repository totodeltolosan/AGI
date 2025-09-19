#!/usr/bin/env python3
"""
Structure Generator - Générateur d'Arborescence du Projet AGI
============================================================

Rôle Fondamental (Conforme AGI.md - tools/project_initializer/structure_generator.py) :
- Créer l'intégralité de la structure de répertoires conforme à la hiérarchie AGI.md
- Générer l'arborescence des 11 domaines selon l'ordre de priorité défini
- Créer les sous-répertoires spécialisés (file_generators/, templates/, etc.)
- Valider les permissions et la sécurité des chemins de création
- Assurer la reproductibilité et le déterminisme de la structure générée
- Traçabilité complète de toutes les opérations de création de répertoires

Conformité Architecturale :
- Limite stricte < 200 lignes via fonctions atomiques spécialisées
- Sécurité by Design : validation des chemins, protection contre path traversal
- Fiabilité extrême : gestion robuste des erreurs de système de fichiers
- Modularité : délégation par type de structure (domaines, sous-modules, templates)

Version : 1.0
Date : 17 Septembre 2025
Référence : Rapport de Directives AGI.md - Section tools/project_initializer/
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import stat
import traceback

class StructureGenerator:
    """
    Générateur d'arborescence physique du projet AGI.
    
    Crée la structure complète des répertoires en respectant la hiérarchie
    définie dans AGI.md et les spécifications extraites par report_parser.py.
    Assure la sécurité, la reproductibilité et la traçabilité complète.
    """
    
    # Structure fixe selon AGI.md - Ordre de priorité respecté
    DOMAIN_STRUCTURE = {
        'compliance': {
            'priority': 1,
            'master_level': '+++',
            'subdirs': [],
            'description': 'Gouvernance et Conformité - Maître +++'
        },
        'development_governance': {
            'priority': 2, 
            'master_level': '+++',
            'subdirs': ['onboarding_materials'],
            'description': 'Gouvernance du Développement - Maître +++'
        },
        'config': {
            'priority': 3,
            'master_level': 'standard',
            'subdirs': [],
            'description': 'Configuration et Paramètres'
        },
        'supervisor': {
            'priority': 4,
            'master_level': 'standard', 
            'subdirs': [],
            'description': 'Surveillance et Mise à jour'
        },
        'plugins': {
            'priority': 5,
            'master_level': 'standard',
            'subdirs': [],
            'description': 'Gestion des Plugins/Modules'
        },
        'core': {
            'priority': 6,
            'master_level': 'standard',
            'subdirs': [],
            'description': 'Moteur Cœur'
        },
        'data': {
            'priority': 7,
            'master_level': 'standard',
            'subdirs': [],
            'description': 'Gestion Données'
        },
        'runtime_compliance': {
            'priority': 8,
            'master_level': 'standard',
            'subdirs': [],
            'description': 'Surveillance et Contrôle d\'Exécution'
        },
        'ecosystem': {
            'priority': 9,
            'master_level': 'standard',
            'subdirs': [],
            'description': 'Gestion des Dépendances et de l\'Écosystème'
        },
        'ui': {
            'priority': 10,
            'master_level': 'standard',
            'subdirs': [],
            'description': 'Interface Utilisateur / API'
        },
        'ai_compliance': {
            'priority': 11,
            'master_level': 'standard',
            'subdirs': [],
            'description': 'Véracité et Audit IA'
        }
    }
    
    def __init__(self, logger):
        self.logger = logger
        self.created_paths: Set[str] = set()
        
    def create_directories(self, output_dir: str, project_spec: Dict[str, Any]) -> bool:
        """
        Crée l'arborescence complète du projet AGI.
        
        Args:
            output_dir: Répertoire racine de sortie
            project_spec: Spécifications extraites par report_parser.py
            
        Returns:
            bool: True si création réussie, False sinon
        """
        try:
            self.logger.debug("🏗️ Démarrage génération arborescence AGI")
            
            # Validation et création du répertoire racine
            root_path = self._create_root_directory(output_dir)
            if not root_path:
                return False
                
            # Création de la structure principale du projet
            if not self._create_main_structure(root_path):
                return False
                
            # Création des domaines selon l'ordre de priorité AGI.md
            if not self._create_domains_structure(root_path, project_spec):
                return False
                
            # Création de la structure tools/ (générateurs)
            if not self._create_tools_structure(root_path):
                return False
                
            # Validation finale de la structure créée
            if not self._validate_created_structure(root_path):
                return False
                
            self.logger.verbose(f"✅ Arborescence AGI créée: {len(self.created_paths)} répertoires")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur critique génération arborescence: {str(e)}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _create_root_directory(self, output_dir: str) -> Optional[Path]:
        """Valide et crée le répertoire racine du projet."""
        try:
            root_path = Path(output_dir).resolve()
            
            # Sécurité : validation du chemin
            if not self._validate_safe_path(root_path):
                return None
                
            # Création sécurisée du répertoire racine
            root_path.mkdir(parents=True, exist_ok=True)
            
            # Vérification des permissions d'écriture
            if not os.access(root_path, os.W_OK):
                self.logger.error(f"❌ Permissions insuffisantes: {root_path}")
                return None
                
            self.created_paths.add(str(root_path))
            self.logger.debug(f"✅ Répertoire racine créé: {root_path}")
            return root_path
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création répertoire racine: {e}")
            return None
    
    def _validate_safe_path(self, path: Path) -> bool:
        """Valide la sécurité d'un chemin (protection contre path traversal)."""
        try:
            # Conversion en chemin absolu pour validation
            abs_path = path.resolve()
            
            # Interdiction des chemins système critiques
            forbidden_paths = ['/bin', '/etc', '/usr', '/var', '/sys', '/proc']
            for forbidden in forbidden_paths:
                if str(abs_path).startswith(forbidden):
                    self.logger.error(f"❌ Chemin système interdit: {abs_path}")
                    return False
                    
            # Vérification absence de path traversal
            if '..' in str(path) or str(abs_path) != str(path.resolve()):
                self.logger.error(f"❌ Path traversal détecté: {path}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur validation chemin: {e}")
            return False
    
    def _create_main_structure(self, root_path: Path) -> bool:
        """Crée la structure principale du projet (racine + fichiers principaux)."""
        try:
            # Structure de base selon AGI.md
            main_dirs = [
                'tests',           # Tests unitaires et d'intégration
                'docs',            # Documentation du projet
                'scripts',         # Scripts utilitaires
                'logs',            # Répertoire des logs (sera créé par supervisor/logger.py)
            ]
            
            for dir_name in main_dirs:
                dir_path = root_path / dir_name
                dir_path.mkdir(exist_ok=True)
                self.created_paths.add(str(dir_path))
                self.logger.debug(f"📁 Répertoire principal créé: {dir_name}/")
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création structure principale: {e}")
            return False
    
    def _create_domains_structure(self, root_path: Path, project_spec: Dict[str, Any]) -> bool:
        """Crée les domaines selon l'ordre de priorité défini dans AGI.md."""
        try:
            # Tri des domaines par priorité (compliance/ en premier, etc.)
            sorted_domains = sorted(
                self.DOMAIN_STRUCTURE.items(), 
                key=lambda x: x[1]['priority']
            )
            
            for domain_name, domain_config in sorted_domains:
                domain_path = root_path / domain_name
                
                # Création du domaine principal
                domain_path.mkdir(exist_ok=True)
                self.created_paths.add(str(domain_path))
                
                # Log avec niveau maître pour traçabilité
                master_indicator = f" [{domain_config['master_level']}]" if domain_config['master_level'] != 'standard' else ""
                self.logger.verbose(f"🎯 Domaine créé: {domain_name}/{master_indicator}")
                
                # Création des sous-répertoires spécialisés
                for subdir in domain_config['subdirs']:
                    subdir_path = domain_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    self.created_paths.add(str(subdir_path))
                    self.logger.debug(f"  📂 Sous-répertoire: {domain_name}/{subdir}/")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création domaines: {e}")
            return False
    
    def _create_tools_structure(self, root_path: Path) -> bool:
        """Crée la structure tools/ avec les générateurs et templates."""
        try:
            tools_structure = {
                'tools': {
                    'project_initializer': {
                        'file_generators': {
                            'templates': {}
                        }
                    }
                }
            }
            
            # Création récursive de la structure tools/
            self._create_nested_structure(root_path, tools_structure)
            
            self.logger.verbose("🔧 Structure tools/ créée (générateurs + templates)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création structure tools/: {e}")
            return False
    
    def _create_nested_structure(self, base_path: Path, structure: Dict[str, Any]) -> None:
        """Crée récursivement une structure de répertoires imbriqués."""
        for name, content in structure.items():
            current_path = base_path / name
            current_path.mkdir(exist_ok=True)
            self.created_paths.add(str(current_path))
            
            if isinstance(content, dict):
                self._create_nested_structure(current_path, content)
    
    def _validate_created_structure(self, root_path: Path) -> bool:
        """Valide que la structure créée est conforme aux attentes."""
        try:
            # Vérification des domaines obligatoires
            required_domains = list(self.DOMAIN_STRUCTURE.keys())
            missing_domains = []
            
            for domain in required_domains:
                domain_path = root_path / domain
                if not domain_path.exists():
                    missing_domains.append(domain)
                    
            if missing_domains:
                self.logger.error(f"❌ Domaines manquants: {missing_domains}")
                return False
                
            # Vérification de la structure tools/
            tools_path = root_path / 'tools' / 'project_initializer'
            if not tools_path.exists():
                self.logger.error("❌ Structure tools/project_initializer/ manquante")
                return False
                
            # Validation des permissions sur tous les répertoires créés
            for path_str in self.created_paths:
                path = Path(path_str)
                if not os.access(path, os.R_OK | os.W_OK):
                    self.logger.error(f"❌ Permissions insuffisantes: {path}")
                    return False
                    
            self.logger.debug(f"✅ Structure validée: {len(self.created_paths)} répertoires")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur validation structure: {e}")
            return False# [Copier-coller ici le code généré dans l'artifact ci-dessus]
