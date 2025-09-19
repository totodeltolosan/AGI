#!/usr/bin/env python3
"""
Parser Helpers - Fonctions Utilitaires pour Parsing AGI.md
==========================================================

CHEMIN: tools/project_initializer/parser_helpers.py

Rôle Fondamental :
- Fonctions utilitaires pour parsing de contenu Markdown
- Extraction de sections et métadonnées
- Validation et normalisation de données
- Patterns de reconnaissance de contenu AGI

Conformité Architecturale :
- Module helper délégué depuis report_parser.py
- Limite stricte < 200 lignes ✅
- Fonctions réutilisables et robustes

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
"""

import re
from typing import Dict, List, Any, Optional, Tuple


class ParserHelpers:
    """Fonctions utilitaires pour parsing de fichiers AGI.md."""

    def __init__(self, logger=None):
        self.logger = logger
        self.section_patterns = self._initialize_section_patterns()
        self.domain_patterns = self._initialize_domain_patterns()

    def extract_sections(self, content: str) -> Dict[str, str]:
        """Extrait les sections principales du contenu Markdown."""
        try:
            sections = {}
            current_section = None
            current_content = []

            lines = content.split("\n")

            for line in lines:
                # Détection d'un header de section
                header_match = re.match(r"^#+\s+(.+)", line.strip())
                if header_match:
                    # Sauvegarde de la section précédente
                    if current_section:
                        sections[current_section] = "\n".join(current_content)

                    # Nouvelle section
                    current_section = header_match.group(1).strip()
                    current_content = [line]
                else:
                    if current_section:
                        current_content.append(line)

            # Sauvegarde de la dernière section
            if current_section:
                sections[current_section] = "\n".join(current_content)

            if self.logger:
                self.logger.debug(f"🔍 Sections extraites: {list(sections.keys())}")

            return sections

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur extraction sections: {e}")
            return {}

    def extract_domains_from_content(self, content: str) -> List[str]:
        """Extrait les domaines mentionnés dans le contenu."""
        try:
            domains = set()

            # Patterns de recherche pour domaines
            for pattern in self.domain_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        domains.update(match)
                    else:
                        domains.add(match)

            # Nettoyage et validation des domaines
            cleaned_domains = []
            for domain in domains:
                cleaned = self._clean_domain_name(domain)
                if cleaned and self._is_valid_domain(cleaned):
                    cleaned_domains.append(cleaned)

            # Suppression des doublons et tri
            unique_domains = sorted(list(set(cleaned_domains)))

            if self.logger:
                self.logger.debug(f"🏗️ Domaines trouvés: {unique_domains}")

            return unique_domains

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur extraction domaines: {e}")
            return []

    def parse_metadata_section(self, content: str) -> Dict[str, Any]:
        """Parse les métadonnées du projet depuis le contenu."""
        try:
            metadata = {}

            # Patterns pour métadonnées
            patterns = {
                "project_name": [
                    r"#\s+(.+?)\s*\n",
                    r"Projet\s*:\s*(.+)",
                    r"Name\s*:\s*(.+)",
                ],
                "version": [r"Version\s*:?\s*([0-9\.]+)", r"v([0-9\.]+)"],
                "date": [r"Date\s*:?\s*([0-9\-\/\s\w]+)", r"(\d{1,2}\s+\w+\s+\d{4})"],
                "author": [
                    r"Auteur\s*:?\s*(.+)",
                    r"Author\s*:?\s*(.+)",
                    r"Équipe\s*:?\s*(.+)",
                ],
                "description": [
                    r"Description\s*:?\s*(.+)",
                    r"##\s*Description\s*\n(.+?)(?=\n#|$)",
                ],
            }

            for key, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                    if match:
                        metadata[key] = match.group(1).strip()
                        break

            return metadata

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur parsing métadonnées: {e}")
            return {}

    def parse_architecture_section(self, content: str) -> Dict[str, Any]:
        """Parse les informations d'architecture."""
        try:
            architecture = {}

            # Recherche section architecture
            arch_section = self._find_section_content(
                content, ["Architecture", "ARCHITECTURE"]
            )

            if arch_section:
                # Type d'architecture
                type_match = re.search(r"Type\s*:?\s*(.+)", arch_section, re.IGNORECASE)
                if type_match:
                    architecture["architecture_type"] = type_match.group(1).strip()

                # Patterns architecturaux
                patterns = re.findall(
                    r"Pattern\s*:?\s*(.+)", arch_section, re.IGNORECASE
                )
                if patterns:
                    architecture["patterns"] = [p.strip() for p in patterns]

                # Principes
                principles = re.findall(
                    r"Principe\s*:?\s*(.+)", arch_section, re.IGNORECASE
                )
                if principles:
                    architecture["principles"] = [p.strip() for p in principles]

            return architecture

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur parsing architecture: {e}")
            return {}

    def parse_rules_section(self, content: str) -> Dict[str, Any]:
        """Parse les règles et contraintes."""
        try:
            rules = {}

            # Recherche des règles
            rules_patterns = [
                r"Règle\s*:?\s*(.+)",
                r"Rule\s*:?\s*(.+)",
                r"Contrainte\s*:?\s*(.+)",
                r"Constraint\s*:?\s*(.+)",
            ]

            found_rules = []
            for pattern in rules_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                found_rules.extend(matches)

            if found_rules:
                rules["rules"] = [rule.strip() for rule in found_rules]

            # Limite de lignes (spécifique AGI)
            line_limit_match = re.search(
                r"(\d+)\s*lignes?\s*maximum", content, re.IGNORECASE
            )
            if line_limit_match:
                rules["line_limit"] = int(line_limit_match.group(1))

            return rules

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur parsing règles: {e}")
            return {}

    def validate_agi_format(self, content: str) -> Dict[str, Any]:
        """Valide le format du fichier AGI.md."""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "score": 100,
            }

            # Vérifications de base
            if len(content.strip()) < 100:
                validation_result["errors"].append("Contenu trop court")
                validation_result["valid"] = False
                validation_result["score"] -= 30

            # Vérification headers
            if not re.search(r"^#\s+", content, re.MULTILINE):
                validation_result["errors"].append("Aucun header principal trouvé")
                validation_result["valid"] = False
                validation_result["score"] -= 20

            # Vérification structure minimale
            required_sections = ["domaines?", "architecture", "règles?"]
            for section in required_sections:
                if not re.search(section, content, re.IGNORECASE):
                    validation_result["warnings"].append(
                        f"Section '{section}' manquante"
                    )
                    validation_result["score"] -= 10

            # Vérification format Markdown
            if not re.search(r"```|`[^`]+`|\*\*|\*|_", content):
                validation_result["warnings"].append("Format Markdown minimal")
                validation_result["score"] -= 5

            return validation_result

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur validation format: {e}")
            return {"valid": False, "errors": [str(e)], "score": 0}

    def validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les données parsées."""
        try:
            validated = data.copy()

            # Validation domaines
            if "domains" in validated:
                valid_domains = []
                for domain in validated["domains"]:
                    if self._is_valid_domain(domain):
                        valid_domains.append(domain)
                validated["domains"] = valid_domains

            # Validation métadonnées
            if "project_name" not in validated or not validated["project_name"]:
                validated["project_name"] = "Projet AGI"

            if "version" not in validated or not validated["version"]:
                validated["version"] = "1.0"

            return validated

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur validation données: {e}")
            return data

    def enrich_with_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les données avec des valeurs par défaut."""
        try:
            enriched = data.copy()

            # Domaines par défaut si vide
            if not enriched.get("domains"):
                enriched["domains"] = ["core", "compliance", "supervisor"]

            # Architecture par défaut
            if not enriched.get("architecture_type"):
                enriched["architecture_type"] = "Modulaire"

            # Patterns par défaut
            if not enriched.get("patterns"):
                enriched["patterns"] = ["Modular Design", "Delegation Pattern"]

            # Règles par défaut
            if not enriched.get("rules"):
                enriched["rules"] = ["Limite 200 lignes par fichier"]

            return enriched

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur enrichissement: {e}")
            return data

    def _initialize_section_patterns(self) -> List[str]:
        """Initialise les patterns de reconnaissance de sections."""
        return [
            r"^#+\s+(.+)$",  # Headers Markdown
            r"=+\s*(.+)\s*=+",  # Headers avec =
            r"-+\s*(.+)\s*-+",  # Headers avec -
            r"\*+\s*(.+)\s*\*+",  # Headers avec *
        ]

    def _initialize_domain_patterns(self) -> List[str]:
        """Initialise les patterns de reconnaissance de domaines."""
        return [
            r"domaine[s]?\s*:?\s*([a-z_]+)",
            r"domain[s]?\s*:?\s*([a-z_]+)",
            r"module[s]?\s*:?\s*([a-z_]+)",
            r"composant[s]?\s*:?\s*([a-z_]+)",
            r"([a-z_]+)_(?:manager|module|component)",
            r"([a-z_]+)(?:/|\\)([a-z_]+)",
            r"`([a-z_]+)`",
            r"\b([a-z]+_[a-z]+(?:_[a-z]+)*)\b",
        ]

    def _clean_domain_name(self, domain: str) -> str:
        """Nettoie un nom de domaine."""
        if not domain:
            return ""

        # Suppression caractères spéciaux
        cleaned = re.sub(r"[^a-zA-Z0-9_]", "", domain.strip())

        # Conversion en minuscules
        cleaned = cleaned.lower()

        # Suppression underscores multiples
        cleaned = re.sub(r"_+", "_", cleaned)

        # Suppression underscores début/fin
        cleaned = cleaned.strip("_")

        return cleaned

    def _is_valid_domain(self, domain: str) -> bool:
        """Valide qu'un domaine est acceptable."""
        if not domain or len(domain) < 2:
            return False

        # Vérification caractères autorisés
        if not re.match(r"^[a-z][a-z0-9_]*[a-z0-9]$", domain):
            return False

        # Exclusion de mots réservés
        reserved = {"test", "tmp", "temp", "old", "new", "main", "init"}
        if domain in reserved:
            return False

        return True

    def _find_section_content(self, content: str, section_names: List[str]) -> str:
        """Trouve le contenu d'une section spécifique."""
        for name in section_names:
            pattern = rf"^#+\s*{re.escape(name)}\s*\n(.*?)(?=\n#+|$)"
            match = re.search(
                pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL
            )
            if match:
                return match.group(1).strip()

        return ""
