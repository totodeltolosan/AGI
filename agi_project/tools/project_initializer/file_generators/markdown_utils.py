#!/usr/bin/env python3
"""
Markdown Utils - Utilitaires pour génération documentation Markdown AGI
======================================================================

Rôle : Fonctions utilitaires pour formatage et description des éléments
Sépare les utilitaires de la logique principale pour conformité AGI.md <200 lignes

Conformité Architecturale :
- Responsabilité unique : utilitaires et helpers Markdown
- Descriptions basées sur directives AGI.md
- Formatage cohérent et réutilisable
- Aucune logique métier complexe

Version : 1.0
Date : 18 September 2025
Référence : Refactorisation conforme AGI.md
"""

from typing import List, Dict


class MarkdownUtils:
    """
    Utilitaires pour génération et formatage Markdown
    Contient descriptions domaines et helpers de formatage
    """

    def __init__(self):
        """TODO: Add docstring."""
        self.domain_descriptions = self._init_domain_descriptions()
        self.file_descriptions = self._init_file_descriptions()

    def get_domain_description(self, domain_name: str) -> str:
        """Retourne la description d'un domaine selon AGI.md"""
        return self.domain_descriptions.get(
            domain_name, f"Module {domain_name} du projet AGI"
        )

    def format_python_files_list(self, python_files: List[str]) -> str:
        """Formate la liste des fichiers Python en Markdown"""
        if not python_files:
            return "- *Aucun fichier Python*"

        formatted_files = []
        for file in python_files:
            if file != "__init__.py":
                description = self.get_file_description(file)
                formatted_files.append(f"- **`{file}`** - {description}")

        if "__init__.py" in python_files:
            formatted_files.append("- `__init__.py` - Module d'initialisation")

        return "\n".join(formatted_files)

    def get_file_description(self, filename: str) -> str:
        """Retourne une description du fichier basée sur son nom"""
        return self.file_descriptions.get(filename, "Module du domaine")

    def format_domain_hierarchy(self, domains: List[str]) -> str:
        """Génère la hiérarchie des domaines en Markdown"""
        hierarchy = []

        # Maîtres +++
        masters = ["compliance", "development_governance"]
        if any(d in domains for d in masters):
            hierarchy.append("### Maîtres +++ (Contrôle Critique)")
            for domain in masters:
                if domain in domains:
                    hierarchy.append(
                        f"- **{domain}/** - {self.get_domain_description(domain)}"
                    )

        # Haute priorité
        high_priority = ["config", "supervisor"]
        if any(d in domains for d in high_priority):
            hierarchy.append("\n### Haute Priorité")
            for domain in high_priority:
                if domain in domains:
                    hierarchy.append(
                        f"- **{domain}/** - {self.get_domain_description(domain)}"
                    )

        # Priorité standard
        standard = [
            "plugins",
            "core",
            "data",
            "runtime_compliance",
            "ecosystem",
            "ui",
            "ai_compliance",
        ]
        standard_in_domains = [d for d in standard if d in domains]
        if standard_in_domains:
            hierarchy.append("\n### Priorité Standard")
            for domain in standard_in_domains:
                hierarchy.append(
                    f"- **{domain}/** - {self.get_domain_description(domain)}"
                )

        return "\n".join(hierarchy)

    def create_badges(self, project_name: str) -> str:
        """Génère les badges Markdown pour le projet"""
        badges = [
            "[![Conformité AGI](https://img.shields.io/badge/AGI-100%25%20Conforme-green)](./AGI.md)",
            "[![Ligne de Code](https://img.shields.io/badge/Max%20Lignes-200-blue)](#architecture)",
            "[![Tests](https://img.shields.io/badge/Tests-Passing-green)](#tests)",
            "[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)",
        ]
        return "\n".join(badges)

    def _init_domain_descriptions(self) -> Dict[str, str]:
        """Initialize les descriptions des domaines selon AGI.md"""
        return {
            "compliance": "**MAÎTRE +++** - Gouvernance et application des directives AGI.md",
            "development_governance": "**MAÎTRE +++** - Outils et processus pour développeurs",
            "config": "Configuration centralisée et gestion des paramètres",
            "supervisor": "Surveillance, logging et monitoring du système",
            "plugins": "Système d'extensions et modules dynamiques",
            "core": "Moteur cœur et logique métier principale",
            "data": "Gestion, transformation et persistance des données",
            "runtime_compliance": "Contrôle et application des politiques à l'exécution",
            "ecosystem": "Gestion des dépendances et environnements",
            "ui": "Interfaces utilisateur et adaptateurs externes",
            "ai_compliance": "Vérification véracité et détection biais IA",
        }

    def _init_file_descriptions(self) -> Dict[str, str]:
        """Initialize les descriptions des fichiers courants"""
        return {
            # Compliance
            "compliance_reporter.py": "Confirmateur ultime des violations",
            "policy_loader.py": "Chargeur et validateur des politiques",
            "static_auditor.py": "Auditeur statique du code",
            # Config
            "config_manager.py": "Gestionnaire centralisé de configuration",
            "config_loader.py": "Chargeur de configurations",
            "config_validator.py": "Validateur de configurations",
            # Supervisor
            "supervisor.py": "Superviseur global du système",
            "logger.py": "Gestionnaire de journalisation",
            "updater.py": "Gestionnaire de mises à jour",
            # Development Governance
            "dev_workflow_check.py": "Vérificateur workflow développeur",
            # Plugins
            "plugin_loader.py": "Chargeur de plugins",
            "plugin_discoverer.py": "Découvreur de plugins",
            "plugin_interface.py": "Interface de plugins",
            # Core
            "core_engine_base.py": "Base du moteur cœur",
            "core_engine_tasks.py": "Tâches du moteur cœur",
            "core_engine_ai.py": "Services IA du moteur cœur",
            # Data
            "data_storage.py": "Gestionnaire de stockage des données",
            "data_loader.py": "Chargeur de données",
            "data_transformer.py": "Transformateur de données",
            # Runtime Compliance
            "runtime_policy_enforcer.py": "Vérificateur de politiques d'exécution",
            "resource_monitor.py": "Moniteur de ressources",
            "data_integrity_checker.py": "Vérificateur d'intégrité des données",
            # Ecosystem
            "environment_manager.py": "Gestionnaire d'environnement",
            "dependency_resolver.py": "Résolveur de dépendances",
            # UI
            "ui_web.py": "Interface Web principale",
            "ui_cli.py": "Interface en ligne de commande",
            "ui_adapters.py": "Adapteurs d'interface",
            # AI Compliance
            "ai_fact_checker.py": "Vérificateur de faits IA",
            "ai_bias_detector.py": "Détecteur de biais IA",
        }

    def escape_markdown(self, text: str) -> str:
        """Échappe les caractères spéciaux Markdown"""
        special_chars = ["*", "_", "`", "[", "]", "(", ")", "#", "+", "-", ".", "!"]
        escaped_text = text
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f"\\{char}")
        return escaped_text

    def create_table_of_contents(self, headers: List[str]) -> str:
        """Génère une table des matières à partir des headers"""
        toc = ["## Table des Matières\n"]
        for header in headers:
            # Convertir header en lien anchor
            anchor = header.lower().replace(" ", "-").replace(":", "").replace("/", "")
            toc.append(f"- [{header}](#{anchor})")
        return "\n".join(toc)