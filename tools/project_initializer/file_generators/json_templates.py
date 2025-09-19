#!/usr/bin/env python3
"""
JSON Templates - Données Statiques pour les Fichiers JSON
=========================================================

Rôle Fondamental (Conforme AGI.md) :
- Contenir les structures de données statiques pour la génération des fichiers JSON.
- Agir comme une source de vérité unique pour le contenu des configurations.
- Assurer la séparation entre les données (ce module) et la logique (JSONGenerator).

Version : 1.0
Date : 18 Septembre 2025
"""

from datetime import datetime
from typing import Dict, Any


def get_rules_data() -> Dict[str, Any]:
    """Retourne la structure de données complète pour le fichier rules.json."""
    return {
        "schema_version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "description": "Constitution des règles de gouvernance AGI.md",
        "global_rules": {
            "code_quality": {
                "max_lines_per_file": {
                    "value": 200,
                    "severity": "CRITICAL",
                    "enforcement": "BLOCK",
                    "description": "Limite stricte 200 lignes par fichier Python",
                },
                "complexity_limit": {
                    "value": 5,
                    "severity": "WARNING",
                    "enforcement": "WARN",
                    "description": "Complexité cyclomatique maximale",
                },
            },
            "architecture": {
                "modularity_required": {
                    "value": True,
                    "severity": "CRITICAL",
                    "enforcement": "BLOCK",
                },
                "single_responsibility": {
                    "value": True,
                    "severity": "HIGH",
                    "enforcement": "WARN",
                },
            },
            "security": {
                "path_validation": {
                    "value": True,
                    "severity": "CRITICAL",
                    "enforcement": "BLOCK",
                },
                "input_sanitization": {
                    "value": True,
                    "severity": "HIGH",
                    "enforcement": "WARN",
                },
            },
        },
        "domain_priorities": [
            {"name": "compliance", "level": "MASTER_PLUS_PLUS_PLUS", "order": 1},
            {
                "name": "development_governance",
                "level": "MASTER_PLUS_PLUS_PLUS",
                "order": 2,
            },
            {"name": "config", "level": "HIGH", "order": 3},
            {"name": "supervisor", "level": "HIGH", "order": 4},
            {"name": "plugins", "level": "HIGH", "order": 5},
            {"name": "core", "level": "HIGH", "order": 6},
            {"name": "data", "level": "MEDIUM", "order": 7},
            {"name": "runtime_compliance", "level": "MEDIUM", "order": 8},
            {"name": "ecosystem", "level": "MEDIUM", "order": 9},
            {"name": "ui", "level": "LOW", "order": 10},
            {"name": "ai_compliance", "level": "SPECIALIZED", "order": 11},
        ],
    }


def get_policy_context_rules_data() -> Dict[str, Any]:
    """Retourne la structure de données pour le fichier policy_context_rules.json."""
    return {
        "schema_version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "description": "Règles contextuelles par environnement",
        "context_rules": {
            "development": {
                "code_quality.max_lines_per_file": {
                    "override_value": 250,
                    "reason": "Tolérance pour prototypage",
                },
                "logging_level": "DEBUG",
            },
            "production": {
                "code_quality.max_lines_per_file": {
                    "override_value": 200,
                    "reason": "Application stricte en production",
                },
                "logging_level": "INFO",
                "security.path_validation": {"enforcement": "BLOCK_STRICT"},
            },
            "testing": {
                "code_quality.complexity_limit": {
                    "override_value": 8,
                    "reason": "Tests peuvent être plus complexes",
                },
                "logging_level": "VERBOSE",
            },
        },
    }
