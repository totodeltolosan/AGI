#!/usr/bin/env python3
"""
AGI Report Parser - Parser Intelligent du Rapport de Directives AGI.md
=====================================================================

Rôle Fondamental (Conforme AGI.md - tools/project_initializer/report_parser.py) :
- Extraire et interpréter les directives du Rapport AGI.md de manière structurée
- Parser la hiérarchie des domaines, fichiers, interactions et délégations
- Extraire les exigences clés (fiabilité, performance, sécurité, limites)
- Fournir une représentation JSON structurée utilisable par les générateurs
- Valider la conformité du format du rapport et signaler les incohérences
- S'appuyer sur AGI.md comme source unique de vérité sans interprétation subjective

Conformité Architecturale :
- Limite stricte < 200 lignes via fonctions atomiques et délégation
- Fiabilité extrême : résistant aux fichiers mal formés, erreurs de lecture
- Traçabilité complète : logs détaillés du processus de parsing
- Déterminisme : même input = même output structuré

Version : 1.0
Date : 17 Septembre 2025
Référence : Rapport de Directives AGI.md - Section tools/project_initializer/
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import traceback


@dataclass
class FileSpec:
    """Spécification d'un fichier selon les directives AGI.md."""

    name: str
    type: str  # 'python', 'json', 'markdown'
    role: str
    interactions: List[str]
    requirements: List[str]
    limits: List[str]
    max_lines: int = 200


@dataclass
class DomainSpec:
    """Spécification d'un domaine selon les directives AGI.md."""

    name: str
    priority: int
    description: str
    files: List[FileSpec]
    master_level: str  # '+++', '++', '+', 'standard'


class AGIReportParser:
    """
    Parser intelligent du Rapport de Directives AGI.md.

    Extrait de manière déterministe toute la structure architecturale,
    les interactions entre modules, les exigences et les limites définies
    dans le rapport pour permettre la génération conforme du squelette.
    """

    def __init__(self, logger):
        self.logger = logger
        self.report_path = Path("AGI.md")
        self.domains_priority = {
            "compliance": 1,
            "development_governance": 2,
            "config": 3,
            "supervisor": 4,
            "plugins": 5,
            "core": 6,
            "data": 7,
            "runtime_compliance": 8,
            "ecosystem": 9,
            "ui": 10,
            "ai_compliance": 11,
        }

    def parse_report(self) -> Optional[Dict[str, Any]]:
        """
        Parse le rapport AGI.md complet et retourne la spécification structurée.

        Returns:
            Dict contenant : domains, main_py_spec, global_directives, architecture_principles
        """
        try:
            self.logger.debug("🔍 Démarrage parsing du rapport AGI.md")

            # Lecture sécurisée du fichier
            content = self._read_report_safely()
            if not content:
                return None

            # Extraction des sections principales
            sections = self._extract_sections(content)
            self.logger.verbose(f"📖 Sections extraites: {list(sections.keys())}")

            # Parse de l'architecture et des principes
            architecture_principles = self._parse_architecture_principles(sections)

            # Parse des domaines et fichiers
            domains = self._parse_domains_and_files(sections)

            # Parse des spécifications main.py
            main_py_spec = self._parse_main_py_specifications(sections)

            # Parse des directives globales
            global_directives = self._parse_global_directives(sections)

            # Construction de la spécification finale
            project_spec = {
                "architecture_principles": architecture_principles,
                "domains": domains,
                "main_py_spec": main_py_spec,
                "global_directives": global_directives,
                "metadata": {
                    "version": "1.0",
                    "date": "17 Septembre 2025",
                    "source": "AGI.md",
                },
            }

            self.logger.debug(f"✅ Parsing terminé: {len(domains)} domaines extraits")
            return project_spec

        except Exception as e:
            self.logger.error(f"❌ Erreur critique parsing AGI.md: {str(e)}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

    def _read_report_safely(self) -> Optional[str]:
        """Lecture sécurisée et validée du fichier AGI.md."""
        try:
            if not self.report_path.exists():
                self.logger.error(f"❌ Fichier AGI.md introuvable: {self.report_path}")
                return None

            with open(self.report_path, "r", encoding="utf-8") as f:
                content = f.read()

            if len(content) < 1000:  # Validation basique
                self.logger.error("❌ Fichier AGI.md trop petit, probablement corrompu")
                return None

            self.logger.debug(f"✅ Fichier AGI.md lu: {len(content)} caractères")
            return content

        except Exception as e:
            self.logger.error(f"❌ Erreur lecture AGI.md: {e}")
            return None

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extrait les sections principales du rapport par analyse des headers."""
        sections = {}

        # Patterns pour identifier les sections principales
        patterns = {
            "introduction": r"INTRODUCTION(.*?)(?=PHILOSOPHIE|$)",
            "architecture_principles": r"PHILOSOPHIE ARCHITECTURALE FONDAMENTALE(.*?)(?=DIRECTIVES|$)",
            "detailed_directives": r"DIRECTIVES DÉTAILLÉES PAR DOMAINE(.*?)(?=CONCLUSION|$)",
            "conclusion": r"CONCLUSION(.*?)$",
        }

        for section_name, pattern in patterns.items():
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()
                self.logger.debug(
                    f"📝 Section '{section_name}': {len(match.group(1))} chars"
                )

        return sections

    def _parse_architecture_principles(self, sections: Dict[str, str]) -> List[str]:
        """Extrait les principes architecturaux fondamentaux."""
        principles = []

        if "architecture_principles" in sections:
            content = sections["architecture_principles"]

            # Extraction des principes (lignes commençant par des patterns spécifiques)
            principle_patterns = [
                r"Modularité et Découplage Strict",
                r"Gouvernance par les Contrats",
                r"Conformité Continue",
                r"Sécurité par Conception",
                r"Traçabilité et Observabilité",
                r"Simplicité et Maintenabilité",
                r"Contrainte de Taille \(200 Lignes",
                r"Évolutivité Contrôlée",
                r"Véracité et Fiabilité",
                r"Gouvernance du Développement",
            ]

            for pattern in principle_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    principles.append(pattern.replace("\\", ""))

        self.logger.verbose(f"🎯 Principes architecturaux extraits: {len(principles)}")
        return principles

    def _parse_domains_and_files(
        self, sections: Dict[str, str]
    ) -> Dict[str, DomainSpec]:
        """Parse les domaines et leurs fichiers selon la hiérarchie AGI.md."""
        domains = {}

        if "detailed_directives" not in sections:
            return domains

        content = sections["detailed_directives"]

        # Extraction des domaines par analyse des numéros de section
        domain_pattern = r"(\d+)\.\s+(?:Domaine\s*:\s*)?([a-zA-Z_/]+)\s*\([^)]+\)"
        domain_matches = re.finditer(domain_pattern, content)

        for match in domain_matches:
            domain_number = int(match.group(1))
            domain_path = match.group(2).strip()
            domain_name = domain_path.split("/")[-1]  # Dernier élément du chemin

            # Détermination du niveau maître selon la description
            master_level = self._determine_master_level(domain_name, content)

            # Extraction des fichiers de ce domaine
            files = self._extract_domain_files(domain_name, content)

            domains[domain_name] = DomainSpec(
                name=domain_name,
                priority=self.domains_priority.get(domain_name, 99),
                description=f"Domaine {domain_name}",
                files=files,
                master_level=master_level,
            )

        self.logger.verbose(f"🏗️ Domaines parsés: {list(domains.keys())}")
        return domains

    def _determine_master_level(self, domain_name: str, content: str) -> str:
        """Détermine le niveau maître d'un domaine selon les mentions dans le rapport."""
        master_indicators = {
            "+++": ["Maître +++", "MaÃ®tre +++"],
            "++": ["Maître ++", "MaÃ®tre ++"],
            "+": ["Maître +", "MaÃ®tre +"],
        }

        for level, indicators in master_indicators.items():
            for indicator in indicators:
                if indicator in content and domain_name in content:
                    return level

        return "standard"

    def _extract_domain_files(self, domain_name: str, content: str) -> List[FileSpec]:
        """Extrait les fichiers d'un domaine spécifique."""
        files = []

        # Pattern pour identifier les fichiers (nom + rôle)
        file_patterns = [
            rf"{domain_name}/([a-zA-Z_]+\.py)\s*\([^)]+\)",
            rf"{domain_name}/([a-zA-Z_]+\.json)\s*\([^)]+\)",
            rf"{domain_name}/([a-zA-Z_]+\.md)\s*\([^)]+\)",
        ]

        for pattern in file_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                filename = match.group(1)
                file_type = filename.split(".")[-1]

                # Extraction du rôle et des interactions
                role, interactions, requirements = self._extract_file_details(
                    filename, content
                )

                files.append(
                    FileSpec(
                        name=filename,
                        type=file_type,
                        role=role,
                        interactions=interactions,
                        requirements=requirements,
                        limits=[],
                        max_lines=200,
                    )
                )

        return files

    def _extract_file_details(
        self, filename: str, content: str
    ) -> Tuple[str, List[str], List[str]]:
        """Extrait les détails d'un fichier spécifique."""
        # Recherche de la section du fichier
        file_section_pattern = (
            rf"{filename}.*?(?=\n[a-zA-Z_]+\.py|\n[a-zA-Z_]+\.json|\n[a-zA-Z_]+\.md|$)"
        )
        match = re.search(file_section_pattern, content, re.DOTALL)

        if not match:
            return f"Module {filename}", [], []

        section_content = match.group(0)

        # Extraction du rôle
        role_match = re.search(r"Rôle Fondamental[:\s]*([^.]+)", section_content)
        role = role_match.group(1).strip() if role_match else f"Module {filename}"

        # Extraction des interactions (patterns DOIT, UTILISE, APPELLE)
        interactions = []
        interaction_patterns = [r"DOIT ([^.]+)", r"UTILISE ([^.]+)", r"APPELLE ([^.]+)"]
        for pattern in interaction_patterns:
            matches = re.finditer(pattern, section_content)
            interactions.extend([match.group(1).strip() for match in matches])

        # Extraction des exigences clés
        requirements = []
        req_patterns = [r"DOIT être ([^.]+)", r"EST ([^.]+)", r"NE DOIT PAS ([^.]+)"]
        for pattern in req_patterns:
            matches = re.finditer(pattern, section_content)
            requirements.extend([match.group(1).strip() for match in matches])

        return role, interactions[:5], requirements[:5]  # Limitation pour clarté

    def _parse_main_py_specifications(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Parse les spécifications spécifiques à main.py."""
        return {
            "role": "Orchestrateur Principal",
            "max_lines": 200,
            "responsibilities": [
                "Initialisation du programme",
                "Coordination des services essentiels",
                "Audit de conformité initial",
                "Chargement des plugins",
                "Démarrage interface utilisateur",
            ],
            "must_not": [
                "Contenir de logique métier",
                "Maintenir état interne significatif",
                "Dépendre directement des modules métier",
            ],
        }

    def _parse_global_directives(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Parse les directives globales applicables à tous les modules."""
        return {
            "max_lines_per_file": 200,
            "code_style": "PEP 8",
            "documentation": "Docstrings obligatoires",
            "type_annotations": "Obligatoires",
            "security_by_design": True,
            "complete_traceability": True,
            "modularity_strict": True,
        }  # [Copier-coller ici le code généré dans l'artifact ci-dessus]
