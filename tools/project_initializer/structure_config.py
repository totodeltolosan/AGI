#!/usr/bin/env python3
"""
Structure Config - Configuration et Templates pour Arborescence AGI
==================================================================

CHEMIN: tools/project_initializer/structure_config.py

Rôle Fondamental :
- Configuration des structures de domaines AGI
- Templates d'arborescence par domaine
- Paramètres de création de répertoires
- Règles de validation d'arborescence

Conformité Architecturale :
- Module config délégué depuis structure_generator.py
- Limite stricte < 200 lignes ✅
- Données statiques et configuration

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
"""

from typing import Dict, List, Any, Optional


class StructureConfig:
    """Configuration pour génération d'arborescence de projet AGI."""

    def __init__(self):
        self.domain_structures = self._initialize_domain_structures()
        self.base_directories = self._initialize_base_directories()
        self.creation_rules = self._initialize_creation_rules()

    def get_domain_structure(self, domain: str) -> Dict[str, Any]:
        """Récupère la structure d'un domaine spécifique."""
        return self.domain_structures.get(domain, self._get_default_domain_structure())

    def get_base_directories(self) -> List[str]:
        """Récupère la liste des répertoires de base."""
        return self.base_directories.copy()

    def get_creation_rules(self) -> Dict[str, Any]:
        """Récupère les règles de création."""
        return self.creation_rules.copy()

    def get_all_domain_names(self) -> List[str]:
        """Retourne tous les noms de domaines configurés."""
        return list(self.domain_structures.keys())

    def validate_domain_name(self, domain: str) -> bool:
        """Valide qu'un nom de domaine est reconnu."""
        return domain in self.domain_structures

    def get_domain_description(self, domain: str) -> str:
        """Récupère la description d'un domaine."""
        structure = self.get_domain_structure(domain)
        return structure.get("description", f"Domaine {domain}")

    def _initialize_domain_structures(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les structures de domaines AGI."""
        return {
            "compliance": {
                "description": "Conformité et validation des règles AGI",
                "rules": {"create_init": True, "mandatory": True},
                "validators": {"create_init": True, "mandatory": True},
                "reports": {"create_init": False, "mandatory": False},
                "policies": {"create_init": False, "mandatory": False},
            },
            "core": {
                "description": "Composants centraux du système AGI",
                "orchestrator": {"create_init": True, "mandatory": True},
                "interfaces": {"create_init": True, "mandatory": True},
                "abstractions": {"create_init": True, "mandatory": False},
                "base_classes": {"create_init": True, "mandatory": False},
            },
            "generators": {
                "description": "Générateurs de code et contenu",
                "code": {"create_init": True, "mandatory": True},
                "templates": {"create_init": False, "mandatory": True},
                "parsers": {"create_init": True, "mandatory": False},
                "utils": {"create_init": True, "mandatory": False},
            },
            "data_processing": {
                "description": "Traitement et analyse de données",
                "processors": {"create_init": True, "mandatory": True},
                "analyzers": {"create_init": True, "mandatory": True},
                "transformers": {"create_init": True, "mandatory": False},
                "pipelines": {"create_init": True, "mandatory": False},
            },
            "knowledge_management": {
                "description": "Gestion des connaissances et apprentissage",
                "knowledge_base": {"create_init": True, "mandatory": True},
                "learning": {"create_init": True, "mandatory": True},
                "memory": {"create_init": True, "mandatory": False},
                "reasoning": {"create_init": True, "mandatory": False},
            },
            "decision_making": {
                "description": "Prise de décision et planification",
                "decision_engine": {"create_init": True, "mandatory": True},
                "planning": {"create_init": True, "mandatory": True},
                "strategies": {"create_init": True, "mandatory": False},
                "optimization": {"create_init": True, "mandatory": False},
            },
            "natural_language": {
                "description": "Traitement du langage naturel",
                "processing": {"create_init": True, "mandatory": True},
                "understanding": {"create_init": True, "mandatory": True},
                "generation": {"create_init": True, "mandatory": True},
                "dialogue": {"create_init": True, "mandatory": False},
            },
            "perception": {
                "description": "Perception et analyse sensorielle",
                "vision": {"create_init": True, "mandatory": False},
                "audio": {"create_init": True, "mandatory": False},
                "sensors": {"create_init": True, "mandatory": True},
                "fusion": {"create_init": True, "mandatory": False},
            },
            "action_execution": {
                "description": "Exécution d'actions et contrôle",
                "executors": {"create_init": True, "mandatory": True},
                "controllers": {"create_init": True, "mandatory": True},
                "actuators": {"create_init": True, "mandatory": False},
                "feedback": {"create_init": True, "mandatory": False},
            },
            "integration": {
                "description": "Intégration et orchestration système",
                "apis": {"create_init": True, "mandatory": True},
                "connectors": {"create_init": True, "mandatory": True},
                "adapters": {"create_init": True, "mandatory": False},
                "middleware": {"create_init": True, "mandatory": False},
            },
            "meta_cognition": {
                "description": "Métacognition et auto-amélioration",
                "self_monitoring": {"create_init": True, "mandatory": True},
                "self_modification": {"create_init": True, "mandatory": True},
                "introspection": {"create_init": True, "mandatory": False},
                "evolution": {"create_init": True, "mandatory": False},
            },
            "safety_security": {
                "description": "Sécurité et protection du système",
                "safety_monitors": {"create_init": True, "mandatory": True},
                "security": {"create_init": True, "mandatory": True},
                "fail_safes": {"create_init": True, "mandatory": True},
                "audit": {"create_init": True, "mandatory": False},
            },
            "human_interaction": {
                "description": "Interaction avec les utilisateurs humains",
                "interfaces": {"create_init": True, "mandatory": True},
                "collaboration": {"create_init": True, "mandatory": True},
                "communication": {"create_init": True, "mandatory": True},
                "adaptation": {"create_init": True, "mandatory": False},
            },
            "learning_adaptation": {
                "description": "Apprentissage et adaptation continue",
                "online_learning": {"create_init": True, "mandatory": True},
                "transfer_learning": {"create_init": True, "mandatory": True},
                "meta_learning": {"create_init": True, "mandatory": False},
                "continual_learning": {"create_init": True, "mandatory": False},
            },
            "resource_management": {
                "description": "Gestion des ressources système",
                "compute": {"create_init": True, "mandatory": True},
                "memory": {"create_init": True, "mandatory": True},
                "storage": {"create_init": True, "mandatory": True},
                "network": {"create_init": True, "mandatory": False},
            },
            "monitoring_logging": {
                "description": "Surveillance et journalisation",
                "monitors": {"create_init": True, "mandatory": True},
                "loggers": {"create_init": True, "mandatory": True},
                "metrics": {"create_init": True, "mandatory": True},
                "alerts": {"create_init": True, "mandatory": False},
            },
            "testing_validation": {
                "description": "Tests et validation du système",
                "unit_tests": {"create_init": True, "mandatory": True},
                "integration_tests": {"create_init": True, "mandatory": True},
                "validation": {"create_init": True, "mandatory": True},
                "benchmarks": {"create_init": True, "mandatory": False},
            },
            "development_governance": {
                "description": "Gouvernance du développement",
                "standards": {"create_init": False, "mandatory": True},
                "guidelines": {"create_init": False, "mandatory": True},
                "processes": {"create_init": False, "mandatory": True},
                "tools": {"create_init": True, "mandatory": False},
            },
            "deployment_operations": {
                "description": "Déploiement et opérations",
                "deployment": {"create_init": True, "mandatory": True},
                "operations": {"create_init": True, "mandatory": True},
                "maintenance": {"create_init": True, "mandatory": True},
                "scaling": {"create_init": True, "mandatory": False},
            },
            "supervisor": {
                "description": "Supervision et coordination globale",
                "coordination": {"create_init": True, "mandatory": True},
                "oversight": {"create_init": True, "mandatory": True},
                "control": {"create_init": True, "mandatory": True},
                "reporting": {"create_init": True, "mandatory": False},
            },
        }

    def _initialize_base_directories(self) -> List[str]:
        """Initialise les répertoires de base du projet."""
        return [
            "docs",  # Documentation
            "tests",  # Tests globaux
            "scripts",  # Scripts utilitaires
            "configs",  # Configurations
            "tools",  # Outils de développement
            "examples",  # Exemples d'usage
            "benchmarks",  # Benchmarks et performances
            "assets",  # Ressources statiques
        ]

    def _initialize_creation_rules(self) -> Dict[str, Any]:
        """Initialise les règles de création d'arborescence."""
        return {
            "max_depth": 5,  # Profondeur maximale
            "create_init_by_default": True,  # Créer __init__.py par défaut
            "validate_permissions": True,  # Valider les permissions
            "cleanup_on_error": True,  # Nettoyer en cas d'erreur
            "skip_existing": True,  # Ignorer les répertoires existants
            "preserve_content": True,  # Préserver le contenu existant
            "atomic_creation": False,  # Création atomique (tout ou rien)
            "parallel_creation": False,  # Création parallèle
            "backup_existing": False,  # Sauvegarder l'existant
            "symlink_support": False,  # Support des liens symboliques
        }

    def _get_default_domain_structure(self) -> Dict[str, Any]:
        """Structure de domaine par défaut."""
        return {
            "description": "Domaine générique",
            "core": {"create_init": True, "mandatory": True},
            "utils": {"create_init": True, "mandatory": False},
            "config": {"create_init": False, "mandatory": False},
        }

    def get_mandatory_subdirectories(self, domain: str) -> List[str]:
        """Récupère les sous-répertoires obligatoires d'un domaine."""
        structure = self.get_domain_structure(domain)
        mandatory = []

        for subdir, config in structure.items():
            if isinstance(config, dict) and config.get("mandatory", False):
                mandatory.append(subdir)

        return mandatory

    def get_optional_subdirectories(self, domain: str) -> List[str]:
        """Récupère les sous-répertoires optionnels d'un domaine."""
        structure = self.get_domain_structure(domain)
        optional = []

        for subdir, config in structure.items():
            if isinstance(config, dict) and not config.get("mandatory", True):
                optional.append(subdir)

        return optional

    def should_create_init(self, domain: str, subdirectory: str) -> bool:
        """Détermine si un __init__.py doit être créé."""
        structure = self.get_domain_structure(domain)
        subdir_config = structure.get(subdirectory, {})

        if isinstance(subdir_config, dict):
            return subdir_config.get(
                "create_init", self.creation_rules["create_init_by_default"]
            )

        return self.creation_rules["create_init_by_default"]

    def get_domain_priority(self, domain: str) -> int:
        """Récupère la priorité de création d'un domaine."""
        priorities = {
            "core": 1,
            "compliance": 2,
            "safety_security": 3,
            "supervisor": 4,
            "generators": 5,
            "integration": 6,
        }
        return priorities.get(domain, 10)  # Priorité par défaut: 10

    def get_domains_by_priority(self, domains: List[str]) -> List[str]:
        """Trie les domaines par ordre de priorité."""
        return sorted(domains, key=self.get_domain_priority)

    def validate_structure_completeness(
        self, created_domains: List[str]
    ) -> Dict[str, Any]:
        """Valide la complétude d'une structure créée."""
        result = {
            "complete": True,
            "missing_mandatory": [],
            "missing_optional": [],
            "coverage": 0.0,
        }

        all_domains = self.get_all_domain_names()
        mandatory_domains = ["core", "compliance", "supervisor"]

        # Vérification domaines obligatoires
        for domain in mandatory_domains:
            if domain not in created_domains:
                result["missing_mandatory"].append(domain)
                result["complete"] = False

        # Calcul couverture
        if all_domains:
            result["coverage"] = len(created_domains) / len(all_domains) * 100

        return result
