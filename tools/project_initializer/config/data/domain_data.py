#!/usr/bin/env python3
"""Domain Data - Données Statiques pour Configuration des Domaines AGI"""

DOMAIN_STRUCTURE = {
    "compliance": {"priority": 1, "master_level": "+++", "critical": True},
    "core": {"priority": 2, "master_level": "+++", "critical": True},
    "supervisor": {"priority": 3, "master_level": "+++", "critical": True},
    "generators": {"priority": 4, "master_level": "++", "critical": False},
    "integration": {"priority": 5, "master_level": "+", "critical": False}
}

DOMAIN_METADATA = {"total_domains": len(DOMAIN_STRUCTURE), "version": "1.0"}
MASTER_LEVELS = {"+++": "Critique", "++": "Important", "+": "Standard"}
