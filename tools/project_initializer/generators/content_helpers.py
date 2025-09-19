#!/usr/bin/env python3
"""
Content Helpers - Fonctions Utilitaires pour Génération de Contenu Python
=========================================================================

CHEMIN: tools/project_initializer/generators/content_helpers.py

Rôle Fondamental :
- Fonctions utilitaires pour génération contenu Python
- Processing de templates avec contexte dynamique
- Validation et optimisation de code Python
- Génération de méthodes et fonctions spécialisées

Conformité Architecturale :
- Module helper délégué depuis content.py
- Limite stricte < 200 lignes ✅
- Fonctions réutilisables et modulaires

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
"""

import ast
import re
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from pathlib import Path


class ContentHelpers:
    """Fonctions utilitaires pour génération de contenu Python."""

    def __init__(self, logger=None):
        self.logger = logger
        self.template_mappings = self._initialize_template_mappings()
        self.domain_contexts = self._initialize_domain_contexts()

    def determine_template_type(self, filename: str) -> str:
        """Détermine le type de template basé sur le nom de fichier."""
        filename_lower = filename.lower()

        for pattern, template_type in self.template_mappings.items():
            if pattern in filename_lower:
                return template_type

        # Fallback basé sur l'extension
        if filename_lower.endswith(".py"):
            return "module"
        return "generic"

    def process_template(self, template: str, context: Dict[str, Any]) -> str:
        """Traite un template avec variables de substitution."""
        try:
            processed = template
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                processed = processed.replace(placeholder, str(value))

            # Nettoyage des placeholders non remplacés
            processed = re.sub(r"\{[^}]+\}", "# TODO: Implémenter", processed)
            return processed

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur processing template: {e}")
            return template

    def validate_python_content(self, content: str, filename: str = None) -> bool:
        """Valide la syntaxe Python du contenu généré."""
        try:
            ast.parse(content)

            # Vérifications supplémentaires
            if not self._has_required_elements(content, filename):
                return False

            # Vérification limite 200 lignes
            if len(content.splitlines()) > 200:
                if self.logger:
                    self.logger.warning(
                        f"⚠️ Contenu dépasse 200 lignes: {len(content.splitlines())}"
                    )
                return False

            return True

        except SyntaxError as e:
            if self.logger:
                self.logger.error(f"❌ Erreur syntaxe Python: {e}")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur validation: {e}")
            return False

    def optimize_content(self, content: str) -> str:
        """Optimise le contenu généré."""
        try:
            # Suppression des lignes vides excessives
            lines = content.split("\n")
            optimized_lines = []
            empty_count = 0

            for line in lines:
                if line.strip() == "":
                    empty_count += 1
                    if empty_count <= 2:  # Max 2 lignes vides consécutives
                        optimized_lines.append(line)
                else:
                    empty_count = 0
                    optimized_lines.append(line)

            # Ajout des imports manquants
            optimized_content = "\n".join(optimized_lines)
            optimized_content = self._add_missing_imports(optimized_content)

            return optimized_content

        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️ Erreur optimisation: {e}")
            return content

    def build_base_context(
        self, domain: str, filename: str, project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Construit le contexte de base pour génération."""
        return {
            "domain": domain,
            "filename": filename,
            "module_name": filename.replace(".py", ""),
            "class_name": self._filename_to_class_name(filename),
            "project_name": project_spec.get("name", "Projet AGI"),
            "date": datetime.now().strftime("%d %B %Y"),
            "author": project_spec.get("author", "Équipe AGI"),
            "version": project_spec.get("version", "1.0"),
            "description": self._generate_module_description(domain, filename),
            "imports": self._generate_imports(domain, filename),
            "docstring": self._generate_docstring(domain, filename),
        }

    def get_domain_specific_context(
        self, domain: str, project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Récupère le contexte spécifique à un domaine."""
        return self.domain_contexts.get(domain, {})

    def build_main_context(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le contexte pour le fichier main.py."""
        domains = project_spec.get("domains", [])
        return {
            "project_name": project_spec.get("name", "Projet AGI"),
            "domains": domains,
            "domains_imports": self._generate_main_imports(domains),
            "main_orchestration": self._generate_main_orchestration(domains),
            "date": datetime.now().strftime("%d %B %Y"),
            "version": project_spec.get("version", "1.0"),
        }

    def build_class_context(
        self, class_name: str, domain: str, project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Construit le contexte pour génération de classe."""
        return {
            "class_name": class_name,
            "domain": domain,
            "base_classes": self._get_base_classes(domain),
            "class_methods": self._generate_class_methods(class_name, domain),
            "class_attributes": self._generate_class_attributes(class_name, domain),
            "class_docstring": f"Classe {class_name} pour domaine {domain}.",
        }

    def build_function_context(
        self, function_name: str, domain: str, project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Construit le contexte pour génération de fonction."""
        return {
            "function_name": function_name,
            "domain": domain,
            "function_params": self._generate_function_params(function_name, domain),
            "function_body": self._generate_function_body(function_name, domain),
            "return_type": self._determine_return_type(function_name),
            "function_docstring": f"Fonction {function_name} pour domaine {domain}.",
        }

    def add_dynamic_imports(self, content: str, project_spec: Dict[str, Any]) -> str:
        """Ajoute les imports dynamiques basés sur les domaines."""
        domains = project_spec.get("domains", [])
        imports_to_add = []

        for domain in domains:
            imports_to_add.append(f"from {domain} import {domain.title()}Manager")

        if imports_to_add:
            import_section = "\n".join(imports_to_add)
            content = content.replace("# DYNAMIC_IMPORTS", import_section)

        return content

    def generate_domain_methods(self, domain: str, class_name: str) -> List[str]:
        """Génère les méthodes spécifiques à un domaine."""
        methods = []

        if domain == "compliance":
            methods.extend(
                [
                    "validate_compliance(self) -> bool",
                    "check_rules(self) -> Dict[str, bool]",
                    "generate_report(self) -> str",
                ]
            )
        elif domain == "core":
            methods.extend(
                [
                    "initialize(self) -> None",
                    "process(self, data: Any) -> Any",
                    "cleanup(self) -> None",
                ]
            )
        elif domain == "generators":
            methods.extend(
                [
                    "generate(self, template: str) -> str",
                    "validate_output(self, content: str) -> bool",
                    "save_output(self, content: str, path: str) -> bool",
                ]
            )

        return methods

    def integrate_methods(self, content: str, methods: List[str]) -> str:
        """Intègre les méthodes dans le contenu de classe."""
        if "# DOMAIN_METHODS" in content:
            methods_code = "\n\n    ".join(
                f'def {method}:\n        """Méthode générée automatiquement."""\n        pass'
                for method in methods
            )
            content = content.replace("# DOMAIN_METHODS", methods_code)

        return content

    def _initialize_template_mappings(self) -> Dict[str, str]:
        """Initialise les mappings nom de fichier -> type de template."""
        return {
            "manager": "manager",
            "validator": "validator",
            "generator": "generator",
            "parser": "parser",
            "config": "config",
            "utils": "utils",
            "logger": "logger",
            "main": "main",
            "__init__": "init",
        }

    def _initialize_domain_contexts(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les contextes spécifiques aux domaines."""
        return {
            "compliance": {
                "base_imports": ["from typing import Dict, List, Any"],
                "common_methods": ["validate", "check_compliance", "report"],
            },
            "core": {
                "base_imports": ["from abc import ABC, abstractmethod"],
                "common_methods": ["initialize", "process", "cleanup"],
            },
            "generators": {
                "base_imports": [
                    "from pathlib import Path",
                    "from typing import Optional",
                ],
                "common_methods": ["generate", "validate", "save"],
            },
        }

    def _has_required_elements(self, content: str, filename: str) -> bool:
        """Vérifie que le contenu a les éléments requis."""
        if not filename:
            return True

        # Vérification docstring module
        if not content.strip().startswith('"""') and not content.strip().startswith(
            "'''"
        ):
            return False

        # Vérification imports pour modules non-init
        if filename != "__init__.py" and "import" not in content:
            return False

        return True

    def _add_missing_imports(self, content: str) -> str:
        """Ajoute les imports manquants."""
        lines = content.split("\n")

        # Vérification typing
        if "Dict" in content or "List" in content or "Any" in content:
            if not any("from typing import" in line for line in lines):
                lines.insert(1, "from typing import Dict, List, Any, Optional")

        return "\n".join(lines)

    def _filename_to_class_name(self, filename: str) -> str:
        """Convertit un nom de fichier en nom de classe."""
        name = filename.replace(".py", "")
        return "".join(word.capitalize() for word in name.split("_"))

    def _generate_module_description(self, domain: str, filename: str) -> str:
        """Génère une description de module."""
        return f"Module {filename} pour domaine {domain} du projet AGI."

    def _generate_imports(self, domain: str, filename: str) -> str:
        """Génère les imports appropriés."""
        base_imports = ["from typing import Dict, List, Any, Optional"]

        if domain in self.domain_contexts:
            base_imports.extend(self.domain_contexts[domain].get("base_imports", []))

        return "\n".join(base_imports)

    def _generate_docstring(self, domain: str, filename: str) -> str:
        """Génère le docstring du module."""
        return f'"""\n{self._generate_module_description(domain, filename)}\n\nVersion : 1.0\nDate : {datetime.now().strftime("%d %B %Y")}\n"""'

    def _generate_main_imports(self, domains: List[str]) -> str:
        """Génère les imports pour main.py."""
        imports = ["import logging", "from pathlib import Path"]
        for domain in domains:
            imports.append(f"from {domain} import {domain.title()}Manager")
        return "\n".join(imports)

    def _generate_main_orchestration(self, domains: List[str]) -> str:
        """Génère l'orchestration principale."""
        orchestration = []
        for domain in domains:
            manager_name = f"{domain}_manager"
            orchestration.append(f"    {manager_name} = {domain.title()}Manager()")
            orchestration.append(f"    {manager_name}.process()")
        return "\n".join(orchestration)

    def _get_base_classes(self, domain: str) -> str:
        """Détermine les classes de base pour un domaine."""
        if domain == "core":
            return "ABC"
        return ""

    def _generate_class_methods(self, class_name: str, domain: str) -> str:
        """Génère les méthodes de classe de base."""
        return 'def __init__(self):\n        """Initialise la classe."""\n        pass'

    def _generate_class_attributes(self, class_name: str, domain: str) -> str:
        """Génère les attributs de classe."""
        return f'    """Classe {class_name} pour domaine {domain}."""'

    def _generate_function_params(self, function_name: str, domain: str) -> str:
        """Génère les paramètres de fonction."""
        return "self, *args, **kwargs"

    def _generate_function_body(self, function_name: str, domain: str) -> str:
        """Génère le corps de fonction."""
        return '    """Fonction générée automatiquement."""\n    pass'

    def _determine_return_type(self, function_name: str) -> str:
        """Détermine le type de retour d'une fonction."""
        if "validate" in function_name or "check" in function_name:
            return "bool"
        elif "get" in function_name or "generate" in function_name:
            return "Any"
        return "None"
