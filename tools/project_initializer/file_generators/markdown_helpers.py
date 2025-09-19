#!/usr/bin/env python3
"""
Markdown Helpers - Fonctions Utilitaires pour Templates Markdown
===============================================================

CHEMIN: tools/project_initializer/file_generators/markdown_helpers.py

Rôle Fondamental :
- Fonctions utilitaires pour traitement templates Markdown
- Processing de templates avec variables de substitution
- Validation et formatage de contenu Markdown
- Support pour contexte de génération

Conformité Architecturale :
- Module helper délégué depuis markdown_templates.py
- Limite stricte < 200 lignes ✅
- Fonctions réutilisables et modulaires

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class MarkdownHelpers:
    """Fonctions utilitaires pour génération de templates Markdown."""

    def __init__(self, logger=None):
        self.logger = logger

    def process_template(self, template: str, context: Dict[str, Any]) -> str:
        """Traite un template avec variables de substitution."""
        try:
            processed = template
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                processed = processed.replace(placeholder, str(value))

            # Nettoyage des placeholders non remplacés
            processed = re.sub(r"\{[^}]+\}", "[NON_DÉFINI]", processed)
            return processed

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur processing template: {e}")
            return template

    def build_readme_context(self, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Construit le contexte pour template README principal."""
        return {
            "project_name": project_spec.get("name", "Projet AGI"),
            "description": project_spec.get(
                "description", "Projet d'Intelligence Artificielle Générale"
            ),
            "version": project_spec.get("version", "1.0"),
            "date": self.get_current_date(),
            "author": project_spec.get("author", "Équipe AGI"),
            "domains_count": str(len(project_spec.get("domains", []))),
            "architecture": project_spec.get("architecture", "Modulaire et évolutive"),
            "features": self._format_features_list(project_spec.get("features", [])),
            "requirements": self._format_requirements(
                project_spec.get("requirements", [])
            ),
        }

    def build_architecture_context(
        self, project_spec: Dict[str, Any]
    ) -> Dict[str, str]:
        """Construit le contexte pour documentation d'architecture."""
        domains = project_spec.get("domains", [])
        return {
            "project_name": project_spec.get("name", "Projet AGI"),
            "domains_list": self._format_domains_list(domains),
            "domains_count": str(len(domains)),
            "architecture_type": project_spec.get("architecture", "Modulaire"),
            "patterns": self._format_architecture_patterns(project_spec),
            "date": self.get_current_date(),
            "principles": self._format_design_principles(project_spec),
        }

    def build_domain_context(
        self, domain: str, project_spec: Dict[str, Any]
    ) -> Dict[str, str]:
        """Construit le contexte pour README de domaine spécifique."""
        domain_info = self._get_domain_info(domain, project_spec)
        return {
            "domain_name": domain,
            "domain_title": domain.title().replace("_", " "),
            "description": domain_info.get("description", f"Module {domain}"),
            "responsibilities": self._format_responsibilities(
                domain_info.get("responsibilities", [])
            ),
            "components": self._format_components(domain_info.get("components", [])),
            "interfaces": self._format_interfaces(domain_info.get("interfaces", [])),
            "date": self.get_current_date(),
        }

    def build_api_context(self, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Construit le contexte pour documentation API."""
        return {
            "project_name": project_spec.get("name", "Projet AGI"),
            "api_version": project_spec.get("api_version", "1.0"),
            "endpoints": self._format_api_endpoints(project_spec.get("endpoints", [])),
            "authentication": project_spec.get("auth_method", "Token-based"),
            "rate_limits": project_spec.get("rate_limits", "Standard"),
            "date": self.get_current_date(),
        }

    def build_user_guide_context(self, project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Construit le contexte pour guide utilisateur."""
        return {
            "project_name": project_spec.get("name", "Projet AGI"),
            "installation_steps": self._format_installation_steps(project_spec),
            "usage_examples": self._format_usage_examples(project_spec),
            "configuration": self._format_configuration_options(project_spec),
            "troubleshooting": self._format_troubleshooting(project_spec),
            "date": self.get_current_date(),
        }

    def validate_markdown_content(self, template_name: str, content: str) -> bool:
        """Valide la structure d'un contenu Markdown."""
        try:
            # Vérifications basiques
            if not content or len(content.strip()) < 10:
                return False

            # Vérification des headers
            if not re.search(r"^#\s+", content, re.MULTILINE):
                return False

            # Vérification de la structure minimale
            required_patterns = {
                "readme": [r"#.*README", r"##.*Installation|Usage|Description"],
                "guidelines": [r"#.*Guidelines|Contribution", r"##.*Process|Rules"],
                "architecture": [r"#.*Architecture", r"##.*Components|Modules"],
            }

            patterns = required_patterns.get(template_name.lower(), [])
            for pattern in patterns:
                if not re.search(pattern, content, re.IGNORECASE):
                    return False

            return True

        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️ Erreur validation {template_name}: {e}")
            return False

    def get_current_date(self) -> str:
        """Retourne la date actuelle formatée."""
        return datetime.now().strftime("%d %B %Y")

    def _format_features_list(self, features: List[str]) -> str:
        """Formate une liste de fonctionnalités en Markdown."""
        if not features:
            return "- Architecture modulaire\n- Extensibilité\n- Conformité AGI.md"
        return "\n".join(f"- {feature}" for feature in features)

    def _format_requirements(self, requirements: List[str]) -> str:
        """Formate les prérequis en Markdown."""
        if not requirements:
            return "- Python 3.8+\n- Modules standard Python"
        return "\n".join(f"- {req}" for req in requirements)

    def _format_domains_list(self, domains: List[str]) -> str:
        """Formate la liste des domaines."""
        if not domains:
            return "- core\n- compliance\n- generators"
        return "\n".join(
            f"- **{domain}**: Module {domain.replace('_', ' ')}" for domain in domains
        )

    def _format_architecture_patterns(self, project_spec: Dict[str, Any]) -> str:
        """Formate les patterns architecturaux."""
        patterns = project_spec.get(
            "patterns", ["Modular Design", "Delegation Pattern", "Factory Pattern"]
        )
        return "\n".join(f"- **{pattern}**" for pattern in patterns)

    def _format_design_principles(self, project_spec: Dict[str, Any]) -> str:
        """Formate les principes de design."""
        principles = project_spec.get(
            "principles",
            [
                "Limite 200 lignes par fichier",
                "Séparation des responsabilités",
                "Modularité et réutilisabilité",
            ],
        )
        return "\n".join(f"- {principle}" for principle in principles)

    def _get_domain_info(
        self, domain: str, project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Récupère les informations d'un domaine spécifique."""
        domains = project_spec.get("domains", {})
        return domains.get(
            domain,
            {
                "description": f"Module {domain} du projet AGI",
                "responsibilities": [f"Gestion des fonctionnalités {domain}"],
                "components": [f"{domain}_manager.py", f"{domain}_config.py"],
                "interfaces": [f"{domain}Interface"],
            },
        )

    def _format_responsibilities(self, responsibilities: List[str]) -> str:
        """Formate les responsabilités d'un domaine."""
        return "\n".join(f"- {resp}" for resp in responsibilities)

    def _format_components(self, components: List[str]) -> str:
        """Formate les composants d'un domaine."""
        return "\n".join(f"- `{comp}`" for comp in components)

    def _format_interfaces(self, interfaces: List[str]) -> str:
        """Formate les interfaces d'un domaine."""
        return "\n".join(f"- `{interface}`" for interface in interfaces)

    def _format_api_endpoints(self, endpoints: List[Dict]) -> str:
        """Formate les endpoints API."""
        if not endpoints:
            return "- `GET /status` - Statut du système\n- `POST /process` - Traitement principal"
        return "\n".join(
            f"- `{ep.get('method', 'GET')} {ep.get('path', '/')}` - {ep.get('description', 'Endpoint')}"
            for ep in endpoints
        )

    def _format_installation_steps(self, project_spec: Dict[str, Any]) -> str:
        """Formate les étapes d'installation."""
        steps = project_spec.get(
            "installation_steps",
            [
                "Cloner le repository",
                "Installer les dépendances: `pip install -r requirements.txt`",
                "Configurer l'environnement",
                "Lancer l'application: `python main.py`",
            ],
        )
        return "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))

    def _format_usage_examples(self, project_spec: Dict[str, Any]) -> str:
        """Formate les exemples d'usage."""
        examples = project_spec.get(
            "usage_examples",
            [
                "```python\nfrom main import AGIProject\nproject = AGIProject()\nproject.run()\n```"
            ],
        )
        return "\n\n".join(examples)

    def _format_configuration_options(self, project_spec: Dict[str, Any]) -> str:
        """Formate les options de configuration."""
        config = project_spec.get(
            "configuration",
            {
                "debug": "Mode debug (True/False)",
                "log_level": "Niveau de log (INFO, DEBUG, ERROR)",
                "output_dir": "Répertoire de sortie",
            },
        )
        return "\n".join(f"- **{key}**: {desc}" for key, desc in config.items())

    def _format_troubleshooting(self, project_spec: Dict[str, Any]) -> str:
        """Formate la section dépannage."""
        troubleshooting = project_spec.get(
            "troubleshooting",
            {
                "Import Error": "Vérifier l'installation des dépendances",
                "Permission Denied": "Vérifier les droits d'écriture",
                "Configuration Error": "Valider le fichier de configuration",
            },
        )
        return "\n".join(
            f"**{problem}**: {solution}"
            for problem, solution in troubleshooting.items()
        )
