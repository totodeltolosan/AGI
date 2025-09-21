#!/usr/bin/env python3
"""
AGI Specification Models - Modèles de Données du Projet AGI
==========================================================

Rôle Fondamental (Conforme AGI.md - models/specs.py) :
- Définir les structures de données pour les spécifications extraites d'AGI.md
- Modèles pour fichiers, domaines, interactions et exigences
- Support de la sérialisation JSON pour les générateurs
- Types de données strictement typés selon les directives

Conformité Architecturale :
- Limite stricte < 200 lignes (extrait de report_parser.py)
- Types stricts : annotations complètes avec typing
- Sérialisation : support dataclasses avec asdict()

Version : 1.0
Date : 17 Septembre 2025
Référence : Rapport de Directives AGI.md - Section tools/project_initializer/
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class FileType(Enum):
    """Types de fichiers supportés dans le projet AGI."""

    PYTHON = "python"
    JSON = "json"
    MARKDOWN = "markdown"


class MasterLevel(Enum):
    """Niveaux maître des domaines selon AGI.md."""

    MASTER_TRIPLE = "+++"  # compliance, development_governance
    MASTER_DOUBLE = "++"  # (non utilisé actuellement)
    MASTER_SINGLE = "+"  # (non utilisé actuellement)
    STANDARD = "standard"  # domaines normaux


@dataclass
class FileSpec:
    """
    Spécification d'un fichier selon les directives AGI.md.

    Contient toutes les informations nécessaires pour générer
    un fichier conforme aux interactions et exigences définies.
    """

    name: str
    type: FileType
    role: str
    interactions: List[str]
    requirements: List[str]
    limits: List[str]
    max_lines: int = 200

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la spécification en dictionnaire."""
        data = asdict(self)
        data["type"] = self.type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileSpec":
        """Crée une FileSpec depuis un dictionnaire."""
        data["type"] = FileType(data["type"])
        return cls(**data)


@dataclass
class DomainSpec:
    """
    Spécification d'un domaine selon les directives AGI.md.

    Représente un domaine complet avec sa priorité, son niveau maître,
    ses fichiers et sa description selon la hiérarchie AGI.md.
    """

    name: str
    priority: int
    description: str
    files: List[FileSpec]
    master_level: MasterLevel
    subdirs: List[str] = None

    def __post_init__(self):
        """Initialise les sous-répertoires par défaut."""
        if self.subdirs is None:
            self.subdirs = []

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la spécification en dictionnaire."""
        data = asdict(self)
        data["master_level"] = self.master_level.value
        data["files"] = [file_spec.to_dict() for file_spec in self.files]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainSpec":
        """Crée une DomainSpec depuis un dictionnaire."""
        data["master_level"] = MasterLevel(data["master_level"])
        data["files"] = [FileSpec.from_dict(f) for f in data["files"]]
        return cls(**data)


@dataclass
class ProjectSpec:
    """
    Spécification complète du projet AGI.

    Structure principale contenant tous les domaines, principes
    architecturaux et directives globales extraites d'AGI.md.
    """

    architecture_principles: List[str]
    domains: Dict[str, DomainSpec]
    main_py_spec: Dict[str, Any]
    global_directives: Dict[str, Any]
    metadata: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la spécification complète en dictionnaire."""
        return {
            "architecture_principles": self.architecture_principles,
            "domains": {
                name: domain.to_dict() for name, domain in self.domains.items()
            },
            "main_py_spec": self.main_py_spec,
            "global_directives": self.global_directives,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectSpec":
        """Crée une ProjectSpec depuis un dictionnaire."""
        domains = {
            name: DomainSpec.from_dict(domain_data)
            for name, domain_data in data["domains"].items()
        }

        return cls(
            architecture_principles=data["architecture_principles"],
            domains=domains,
            main_py_spec=data["main_py_spec"],
            global_directives=data["global_directives"],
            metadata=data["metadata"],
        )

    def get_domains_by_priority(self) -> List[DomainSpec]:
        """Retourne les domaines triés par priorité (compliance en premier)."""
        return sorted(self.domains.values(), key=lambda d: d.priority)

    def get_master_domains(self) -> List[DomainSpec]:
        """Retourne seulement les domaines maître (niveau +++)."""
        return [
            domain
            for domain in self.domains.values()
            if domain.master_level == MasterLevel.MASTER_TRIPLE
        ]
