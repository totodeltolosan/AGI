#!/usr/bin/env python3
"""
JSON Generator - Générateur de Fichiers JSON pour AGI (Refactorisé)
===================================================================

Rôle Fondamental (Conforme AGI.md) :
- Orchestrer la génération des fichiers JSON critiques du projet AGI.
- Déléguer la récupération des structures de données au module de templates.
- Assurer la conformité à la limite des 200 lignes.

Version : 2.0 (Refactorisé)
Date : 18 Septembre 2025
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Import du nouveau module de templates
from . import json_templates


class JSONGenerator:
    """
    Génère les fichiers JSON conformes aux directives AGI.md en utilisant
    des templates de données externalisés.
    """

    def __init__(self, logger):
        self.logger = logger
        self.generated_files: List[str] = []

    def generate_rules_json(self, output_dir: Path) -> bool:
        """Génère compliance/rules.json en utilisant un template de données."""
        try:
            # Délégation de la récupération des données
            rules_data = json_templates.get_rules_data()

            rules_path = output_dir / "compliance" / "rules.json"
            self._write_json_file(rules_path, rules_data)
            self.logger.verbose(f"✅ Fichier 'rules.json' généré avec succès.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la génération de 'rules.json': {e}")
            return False

    def generate_policy_context_rules(self, output_dir: Path) -> bool:
        """Génère compliance/policy_context_rules.json en utilisant un template."""
        try:
            # Délégation de la récupération des données
            context_rules = json_templates.get_policy_context_rules_data()

            context_path = output_dir / "compliance" / "policy_context_rules.json"
            self._write_json_file(context_path, context_rules)
            self.logger.verbose(f"✅ Fichier 'policy_context_rules.json' généré.")
            return True
        except Exception as e:
            self.logger.error(
                f"❌ Erreur lors de la génération de 'policy_context_rules.json': {e}"
            )
            return False

    def generate_module_manifest(
        self, domain_name: str, output_dir: Path, python_files: List[str]
    ) -> bool:
        """Génère le fichier module_manifest.json pour un domaine."""
        try:
            # La logique de création du manifest reste ici car elle est dynamique
            manifest_data = {
                "schema_version": "1.0",
                "metadata": {
                    "name": domain_name,
                    "version": "1.0.0",
                    "description": f"Module {domain_name} du projet AGI",
                    "created": datetime.now().isoformat(),
                },
                "files": {"python_modules": python_files},
                "resource_requirements": {"max_memory_mb": 100, "max_cpu_percent": 10},
            }
            manifest_path = output_dir / domain_name / "module_manifest.json"
            self._write_json_file(manifest_path, manifest_data)
            self.logger.verbose(
                f"✅ Fichier 'module_manifest.json' généré pour le domaine '{domain_name}'."
            )
            return True
        except Exception as e:
            self.logger.error(
                f"❌ Erreur lors de la génération du manifest pour '{domain_name}': {e}"
            )
            return False

    def _write_json_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Écrit un dictionnaire dans un fichier JSON formaté."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.generated_files.append(str(file_path))
