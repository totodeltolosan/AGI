#!/usr/bin/env python3
"""
Markdown Config - Templates et Configuration pour Génération Markdown
====================================================================

CHEMIN: tools/project_initializer/file_generators/markdown_config.py

Rôle Fondamental :
- Stockage des templates Markdown statiques
- Configuration des paramètres de génération
- Templates de fallback pour cas d'erreur
- Constantes et paramètres Markdown

Conformité Architecturale :
- Module config délégué depuis markdown_templates.py
- Limite stricte < 200 lignes ✅
- Données statiques et configuration

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
"""

from typing import Dict, Any


class MarkdownConfig:
    """Configuration et templates statiques pour génération Markdown."""

    def __init__(self):
        self.templates = self._initialize_templates()
        self.fallbacks = self._initialize_fallbacks()
        self.config = self._initialize_config()

    def get_contribution_template(self) -> str:
        """Template pour guidelines de contribution."""
        return self.templates["contribution_guidelines"]

    def get_readme_template(self) -> str:
        """Template pour README principal."""
        return self.templates["main_readme"]

    def get_architecture_template(self) -> str:
        """Template pour documentation d'architecture."""
        return self.templates["architecture"]

    def get_domain_readme_template(self) -> str:
        """Template pour README de domaine."""
        return self.templates["domain_readme"]

    def get_api_template(self) -> str:
        """Template pour documentation API."""
        return self.templates["api_documentation"]

    def get_user_guide_template(self) -> str:
        """Template pour guide utilisateur."""
        return self.templates["user_guide"]

    def get_fallback_guidelines(self) -> str:
        """Fallback pour guidelines."""
        return self.fallbacks["guidelines"]

    def get_fallback_readme(self) -> str:
        """Fallback pour README."""
        return self.fallbacks["readme"]

    def get_fallback_architecture(self) -> str:
        """Fallback pour architecture."""
        return self.fallbacks["architecture"]

    def get_fallback_domain_readme(self, domain: str) -> str:
        """Fallback pour README de domaine."""
        return self.fallbacks["domain_readme"].format(domain=domain)

    def get_fallback_api_doc(self) -> str:
        """Fallback pour doc API."""
        return self.fallbacks["api_doc"]

    def get_fallback_user_guide(self) -> str:
        """Fallback pour guide utilisateur."""
        return self.fallbacks["user_guide"]

    def _initialize_templates(self) -> Dict[str, str]:
        """Initialise les templates Markdown."""
        return {
            "contribution_guidelines": """# Guidelines de Contribution - {project_name}

**Version :** {version}
**Date :** {date}

## Processus de Contribution

### 1. Préparation
- Fork du repository
- Création de branche feature
- Respect des conventions de code

### 2. Développement
- Limite stricte 200 lignes par fichier
- Tests unitaires obligatoires
- Documentation inline

### 3. Validation
- Tests d'intégration
- Revue de code
- Validation conformité AGI.md

### 4. Intégration
- Pull request documentée
- Validation par l'équipe
- Merge après approbation

## Standards de Code

### Python
- PEP 8 obligatoire
- Type hints requis
- Docstrings complètes

### Documentation
- Markdown pour docs
- Diagrammes si nécessaire
- Exemples d'usage

## Contact

Pour questions : équipe de développement {project_name}
""",
            "main_readme": """# {project_name}

**Version :** {version}
**Date :** {date}
**Auteur :** {author}

## Description

{description}

## Architecture

Type d'architecture : {architecture}
Nombre de domaines : {domains_count}

## Fonctionnalités

{features}

## Installation

### Prérequis

{requirements}

### Installation

```bash
git clone <repository>
cd {project_name}
pip install -r requirements.txt
```

## Usage

```python
from main import AGIProject

project = AGIProject()
project.run()
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Guide Utilisateur](docs/USER_GUIDE.md)
- [API Documentation](docs/API.md)
- [Guidelines](development_governance/contribution_guidelines.md)

## Licence

Projet {project_name} - {date}
""",
            "architecture": """# Architecture - {project_name}

**Date :** {date}
**Type :** {architecture_type}

## Vue d'Ensemble

Le projet {project_name} implémente une architecture {architecture_type} avec {domains_count} domaines principaux.

## Domaines

{domains_list}

## Patterns Architecturaux

{patterns}

## Principes de Design

{principles}

## Structure des Fichiers

```
{project_name}/
├── main.py                 # Point d'entrée principal
├── compliance/             # Règles et validation
├── core/                  # Composants centraux
├── generators/            # Générateurs de code
└── docs/                  # Documentation
```

## Diagrammes

### Architecture Globale

```
[Core] ←→ [Generators] ←→ [Compliance]
  ↓           ↓              ↓
[Utils]   [Templates]   [Validators]
```

## Évolution

L'architecture est conçue pour évoluer et s'adapter aux besoins futurs du projet AGI.
""",
            "domain_readme": """# Domaine {domain_title}

**Module :** {domain_name}
**Date :** {date}

## Description

{description}

## Responsabilités

{responsibilities}

## Composants

{components}

## Interfaces

{interfaces}

## Usage

```python
from {domain_name} import {domain_name}Interface

interface = {domain_name}Interface()
result = interface.process()
```

## Configuration

Voir configuration spécifique dans `config/{domain_name}_config.py`
""",
            "api_documentation": """# API Documentation - {project_name}

**Version API :** {api_version}
**Date :** {date}

## Endpoints

{endpoints}

## Authentification

Méthode : {authentication}

## Limitations

Rate limiting : {rate_limits}

## Exemples

### Statut du système

```bash
curl -X GET /status
```

### Traitement principal

```bash
curl -X POST /process -d '{"data": "exemple"}'
```

## Codes d'Erreur

- 200: Succès
- 400: Requête invalide
- 401: Non autorisé
- 500: Erreur serveur
""",
            "user_guide": """# Guide Utilisateur - {project_name}

**Date :** {date}

## Installation

{installation_steps}

## Configuration

{configuration}

## Exemples d'Usage

{usage_examples}

## Dépannage

{troubleshooting}

## Support

Pour aide supplémentaire, consultez la documentation technique ou contactez l'équipe de développement.
""",
        }

    def _initialize_fallbacks(self) -> Dict[str, str]:
        """Initialise les templates de fallback."""
        return {
            "guidelines": "# Guidelines de Contribution\n\nGuidelines de base pour contribution au projet.",
            "readme": "# Projet AGI\n\nProjet d'Intelligence Artificielle Générale.",
            "architecture": "# Architecture\n\nDocumentation de l'architecture du projet.",
            "domain_readme": "# Domaine {domain}\n\nDocumentation du domaine {domain}.",
            "api_doc": "# API Documentation\n\nDocumentation de l'API du projet.",
            "user_guide": "# Guide Utilisateur\n\nGuide d'utilisation du projet.",
        }

    def _initialize_config(self) -> Dict[str, Any]:
        """Initialise la configuration Markdown."""
        return {
            "max_line_length": 120,
            "header_levels": {"main": 1, "section": 2, "subsection": 3, "detail": 4},
            "code_block_language": "python",
            "table_alignment": "left",
            "list_style": "-",
            "emphasis_style": "**",
            "link_style": "inline",
            "image_style": "inline",
        }

    def get_config(self, key: str = None) -> Any:
        """Récupère un élément de configuration."""
        if key:
            return self.config.get(key)
        return self.config

    def get_all_templates(self) -> Dict[str, str]:
        """Retourne tous les templates."""
        return self.templates.copy()

    def validate_template_name(self, name: str) -> bool:
        """Valide qu'un nom de template existe."""
        return name in self.templates

    def get_template_names(self) -> list:
        """Retourne la liste des noms de templates disponibles."""
        return list(self.templates.keys())
