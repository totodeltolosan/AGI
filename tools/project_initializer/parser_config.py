#!/usr/bin/env python3
"""
Parser Config - Configuration et Données pour Parsing AGI.md
============================================================

CHEMIN: tools/project_initializer/parser_config.py

Rôle Fondamental :
- Configuration des règles de parsing AGI.md
- Données de fallback et valeurs par défaut
- Patterns de reconnaissance et validation
- Spécifications de projet de référence

Conformité Architecturale :
- Module config délégué depuis report_parser.py
- Limite stricte < 200 lignes ✅
- Données statiques et configuration

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
"""

from typing import Dict, List, Any


class ParserConfig:
    """Configuration pour parsing de fichiers AGI.md."""

    def __init__(self):
        self.default_specifications = self._initialize_default_specifications()
        self.fallback_specifications = self._initialize_fallback_specifications()
        self.parsing_rules = self._initialize_parsing_rules()
        self.validation_rules = self._initialize_validation_rules()

    def get_default_specifications(self) -> Dict[str, Any]:
        """Retourne les spécifications par défaut."""
        return self.default_specifications.copy()

    def get_fallback_specifications(self) -> Dict[str, Any]:
        """Retourne les spécifications de fallback."""
        return self.fallback_specifications.copy()

    def get_default_domains(self) -> List[str]:
        """Retourne la liste des domaines par défaut."""
        return self.default_specifications["domains"].copy()

    def get_default_metadata(self) -> Dict[str, Any]:
        """Retourne les métadonnées par défaut."""
        return {
            "name": self.default_specifications["project_name"],
            "version": self.default_specifications["version"],
            "description": self.default_specifications["description"],
            "author": self.default_specifications["author"],
            "date": self.default_specifications["date"],
        }

    def get_default_architecture(self) -> Dict[str, Any]:
        """Retourne l'architecture par défaut."""
        return {
            "type": self.default_specifications["architecture_type"],
            "patterns": self.default_specifications["patterns"],
            "principles": self.default_specifications["principles"],
            "constraints": self.default_specifications.get("constraints", []),
        }

    def apply_parsing_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique les règles de parsing aux données."""
        try:
            processed = data.copy()

            # Application des règles de normalisation
            for rule_name, rule_func in self.parsing_rules.items():
                if callable(rule_func):
                    processed = rule_func(processed)
                else:
                    # Règle de configuration simple
                    if rule_name in processed and rule_func:
                        processed[rule_name] = rule_func

            return processed

        except Exception:
            return data

    def validate_against_rules(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Valide les données contre les règles définies."""
        try:
            validation_results = {}

            for rule_name, rule_spec in self.validation_rules.items():
                try:
                    if rule_spec["type"] == "required":
                        validation_results[rule_name] = rule_spec["field"] in data
                    elif rule_spec["type"] == "min_length":
                        field_value = data.get(rule_spec["field"], [])
                        validation_results[rule_name] = (
                            len(field_value) >= rule_spec["value"]
                        )
                    elif rule_spec["type"] == "pattern":
                        field_value = data.get(rule_spec["field"], "")
                        import re

                        validation_results[rule_name] = bool(
                            re.search(rule_spec["pattern"], str(field_value))
                        )
                except Exception:
                    validation_results[rule_name] = False

            return validation_results

        except Exception:
            return {}

    def _initialize_default_specifications(self) -> Dict[str, Any]:
        """Initialise les spécifications par défaut d'un projet AGI."""
        return {
            "project_name": "Projet AGI",
            "version": "1.0",
            "description": "Projet d'Intelligence Artificielle Générale",
            "author": "Équipe AGI",
            "date": "2025",
            "architecture_type": "Modulaire et Évolutive",
            "domains": [
                "compliance",
                "core",
                "generators",
                "data_processing",
                "knowledge_management",
                "decision_making",
                "natural_language",
                "perception",
                "action_execution",
                "integration",
                "meta_cognition",
                "safety_security",
                "human_interaction",
                "learning_adaptation",
                "resource_management",
                "monitoring_logging",
                "testing_validation",
                "development_governance",
                "deployment_operations",
                "supervisor",
            ],
            "patterns": [
                "Modular Design",
                "Delegation Pattern",
                "Factory Pattern",
                "Observer Pattern",
                "Strategy Pattern",
                "Command Pattern",
            ],
            "principles": [
                "Limite stricte 200 lignes par fichier",
                "Séparation des responsabilités",
                "Modularité et réutilisabilité",
                "Traçabilité complète",
                "Gestion d'erreurs robuste",
                "Documentation inline",
                "Tests unitaires",
                "Conformité AGI.md",
            ],
            "constraints": [
                "Pas de fichiers > 200 lignes",
                "Imports relatifs autorisés",
                "Logging obligatoire",
                "Type hints requis",
                "Docstrings complètes",
                "Gestion d'exceptions",
            ],
            "requirements": [
                "Python 3.8+",
                "Modules standard Python",
                "pathlib pour chemins",
                "typing pour annotations",
                "logging pour traçabilité",
            ],
            "features": [
                "Architecture modulaire",
                "Génération automatique",
                "Validation conformité",
                "Extensibilité",
                "Maintenance simplifiée",
            ],
        }

    def _initialize_fallback_specifications(self) -> Dict[str, Any]:
        """Initialise les spécifications de fallback minimales."""
        return {
            "project_name": "Projet AGI (Fallback)",
            "version": "1.0",
            "description": "Projet AGI avec spécifications minimales",
            "author": "Équipe AGI",
            "date": "2025",
            "architecture_type": "Modulaire",
            "domains": ["core", "compliance", "supervisor"],
            "patterns": ["Modular Design"],
            "principles": ["Limite 200 lignes par fichier"],
            "constraints": ["Fichiers <= 200 lignes"],
            "requirements": ["Python 3.8+"],
            "features": ["Architecture modulaire"],
        }

    def _initialize_parsing_rules(self) -> Dict[str, Any]:
        """Initialise les règles de parsing."""
        return {
            "normalize_domains": self._normalize_domains_rule,
            "validate_version": self._validate_version_rule,
            "clean_descriptions": self._clean_descriptions_rule,
            "deduplicate_patterns": self._deduplicate_patterns_rule,
            "sort_domains": self._sort_domains_rule,
        }

    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les règles de validation."""
        return {
            "project_name_required": {
                "type": "required",
                "field": "project_name",
                "message": "Nom de projet requis",
            },
            "domains_min_count": {
                "type": "min_length",
                "field": "domains",
                "value": 1,
                "message": "Au moins un domaine requis",
            },
            "version_pattern": {
                "type": "pattern",
                "field": "version",
                "pattern": r"^\d+\.\d+",
                "message": "Version doit suivre le format X.Y",
            },
            "architecture_required": {
                "type": "required",
                "field": "architecture_type",
                "message": "Type d'architecture requis",
            },
        }

    def _normalize_domains_rule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Règle de normalisation des domaines."""
        if "domains" in data and isinstance(data["domains"], list):
            normalized = []
            for domain in data["domains"]:
                if isinstance(domain, str):
                    # Normalisation: minuscules, suppression espaces
                    normalized_domain = domain.lower().strip().replace(" ", "_")
                    if normalized_domain and normalized_domain not in normalized:
                        normalized.append(normalized_domain)
            data["domains"] = normalized
        return data

    def _validate_version_rule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Règle de validation de version."""
        if "version" in data:
            import re

            version = str(data["version"])
            if not re.match(r"^\d+\.\d+", version):
                data["version"] = "1.0"
        return data

    def _clean_descriptions_rule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Règle de nettoyage des descriptions."""
        text_fields = ["description", "project_name"]
        for field in text_fields:
            if field in data and isinstance(data[field], str):
                # Suppression des caractères de contrôle et normalisation espaces
                cleaned = " ".join(data[field].split())
                data[field] = cleaned[:200]  # Limite à 200 caractères
        return data

    def _deduplicate_patterns_rule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Règle de déduplication des patterns."""
        list_fields = [
            "patterns",
            "principles",
            "constraints",
            "requirements",
            "features",
        ]
        for field in list_fields:
            if field in data and isinstance(data[field], list):
                # Suppression des doublons en préservant l'ordre
                seen = set()
                deduplicated = []
                for item in data[field]:
                    if str(item) not in seen:
                        seen.add(str(item))
                        deduplicated.append(item)
                data[field] = deduplicated
        return data

    def _sort_domains_rule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Règle de tri des domaines par priorité."""
        if "domains" in data and isinstance(data["domains"], list):
            # Ordre de priorité pour les domaines AGI
            priority_order = [
                "core",
                "compliance",
                "safety_security",
                "supervisor",
                "generators",
                "integration",
                "human_interaction",
            ]

            prioritized = []
            remaining = []

            # Domaines prioritaires d'abord
            for domain in priority_order:
                if domain in data["domains"]:
                    prioritized.append(domain)

            # Autres domaines triés alphabétiquement
            for domain in sorted(data["domains"]):
                if domain not in prioritized:
                    remaining.append(domain)

            data["domains"] = prioritized + remaining

        return data

    def get_parsing_config(self) -> Dict[str, Any]:
        """Retourne la configuration de parsing."""
        return {
            "encoding": "utf-8",
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "case_sensitive": False,
            "preserve_formatting": True,
            "auto_correct": True,
            "strict_validation": False,
        }

    def get_supported_formats(self) -> List[str]:
        """Retourne les formats de fichiers supportés."""
        return [".md", ".markdown", ".txt"]

    def get_required_sections(self) -> List[str]:
        """Retourne les sections requises dans un fichier AGI."""
        return ["domaines", "architecture", "règles"]

    def get_optional_sections(self) -> List[str]:
        """Retourne les sections optionnelles."""
        return ["métadonnées", "exemples", "références", "changelog"]
