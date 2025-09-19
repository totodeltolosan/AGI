#!/usr/bin/env python3
"""
Report Extractors - Fonctions d'Extraction pour AGI.md
=======================================================

Rôle Fondamental (Conforme AGI.md) :
- Contenir les fonctions pures et spécialisées pour l'extraction de données
  depuis le texte du rapport AGI.md.
- Isoler la complexité des expressions régulières du parser principal.
- Assurer que chaque fonction a une responsabilité unique d'extraction.

Version : 1.0
Date : 18 Septembre 2025
"""

import re
from typing import Dict, List, Tuple
from models.specs import FileSpec, FileType, MasterLevel, DomainSpec


def extract_sections(content: str, logger) -> Dict[str, str]:
    """Extrait les sections principales du rapport (Principes, Directives, etc.)."""
    sections = {}
    patterns = {
        "architecture_principles": r"PHILOSOPHIE ARCHITECTURALE FONDAMENTALE(.*?)(?=DIRECTIVES DÉTAILLÉES)",
        "detailed_directives": r"DIRECTIVES DÉTAILLÉES PAR DOMAINE ET FICHIER(.*?)(?=CONCLUSION)",
    }
    for name, pattern in patterns.items():
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            sections[name] = match.group(1).strip()
            logger.debug(
                f"Section '{name}' extraite ({len(sections[name])} caractères)."
            )
    return sections


def parse_architecture_principles(section_content: str) -> List[str]:
    """Extrait la liste des principes architecturaux fondamentaux."""
    patterns = [
        r"Modularité et Découplage Strict",
        r"Gouvernance par les Contrats",
        r"Conformité Continue",
        r"Sécurité par Conception",
        r"Traçabilité et Observabilité Complètes",
        r"Simplicité et Maintenabilité Extrêmes",
        r"Contrainte de Taille \(200 Lignes de Code\)",
        r"Évolutivité Contrôlée",
        r"Véracité et Fiabilité Garanties",
        r"Gouvernance du Développement",
    ]
    return [
        p.replace("\\", "")
        for p in patterns
        if re.search(p, section_content, re.IGNORECASE)
    ]


def parse_domains_and_files(
    section_content: str, domains_priority: Dict[str, int], logger
) -> Dict[str, DomainSpec]:
    """Parse tous les domaines et leurs fichiers respectifs à partir de la section des directives."""
    domains = {}
    domain_sections = re.split(r"\n\d+\.\s+Domaine\s*:", section_content)[1:]

    for i, domain_block in enumerate(domain_sections, 2):
        name_match = re.search(r"([a-zA-Z_]+)\/", domain_block)
        if not name_match:
            continue

        domain_name = name_match.group(1)
        master_level = (
            MasterLevel.MASTER_TRIPLE
            if "Maître +++" in domain_block
            else MasterLevel.STANDARD
        )
        files = _extract_domain_files(domain_name, domain_block, logger)

        domains[domain_name] = DomainSpec(
            name=domain_name,
            priority=domains_priority.get(domain_name, 99),
            description=f"Domaine {domain_name}",
            files=files,
            master_level=master_level,
        )
    logger.verbose(f"Domaines parsés : {list(domains.keys())}")
    return domains


def _extract_domain_files(
    domain_name: str, domain_content: str, logger
) -> List[FileSpec]:
    """Extrait les fichiers listés dans le bloc de contenu d'un domaine."""
    files = []
    file_patterns = [
        (rf"{domain_name}/([a-zA-Z_]+\.py)", FileType.PYTHON),
        (rf"{domain_name}/([a-zA-Z_]+\.json)", FileType.JSON),
        (rf"{domain_name}/([a-zA-Z_]+\.md)", FileType.MARKDOWN),
    ]
    for pattern, file_type in file_patterns:
        matches = re.finditer(pattern, domain_content)
        for match in matches:
            filename = match.group(1)
            role, interactions, requirements = _extract_file_details(
                filename, domain_content
            )
            files.append(
                FileSpec(
                    name=filename,
                    type=file_type,
                    role=role,
                    interactions=interactions,
                    requirements=requirements,
                    limits=[],
                )
            )
    return files


def _extract_file_details(
    filename: str, content: str
) -> Tuple[str, List[str], List[str]]:
    """Extrait le rôle, les interactions et les exigences pour un fichier spécifique."""
    file_section_pattern = rf"{filename}.*?(?=\n[a-zA-Z_]+\.py|$)"
    match = re.search(file_section_pattern, content, re.DOTALL)
    if not match:
        return f"Module {filename}", [], []

    section_content = match.group(0)
    role_match = re.search(r"Rôle Fondamental[:\s]*([^.]+)", section_content)
    role = role_match.group(1).strip() if role_match else f"Module {filename}"

    interactions = []
    for pattern in [r"DOIT ([^.]+)", r"UTILISE ([^.]+)", r"APPELLE ([^.]+)"]:
        matches = re.finditer(pattern, section_content)
        interactions.extend([m.group(1).strip() for m in matches])

    requirements = []
    for pattern in [r"DOIT être ([^.]+)", r"EST ([^.]+)"]:
        matches = re.finditer(pattern, section_content)
        requirements.extend([m.group(1).strip() for m in matches])

    return role, interactions[:3], requirements[:3]
