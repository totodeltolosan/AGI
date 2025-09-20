#!/usr/bin/env python3
"""
Report Parser - Interface Principale pour Parsing AGI.md
========================================================

CHEMIN: tools/project_initializer/report_parser.py

Rôle Fondamental (Conforme AGI.md) :
- Interface principale pour parsing du fichier AGI.md
- Orchestration via modules délégués pour respect limite 200 lignes
- Extraction de spécifications projet conformes aux directives

Conformité Architecturale :
- Limite stricte < 200 lignes ✅ (refactorisé depuis 239 lignes)
- Délégation : parser_helpers.py + parser_config.py
- Traçabilité : logging détaillé
- Modularité : séparation claire des responsabilités

Version : 1.0 (Refactorisé)
Date : 18 Septembre 2025
Référence : Refactorisation conformité AGI.md
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import traceback

try:
    from .parser_helpers import ParserHelpers
    from .parser_config import ParserConfig
except ImportError as e:
    # Import relatif pour module autonome
    try:
        from parser_helpers import ParserHelpers
        from parser_config import ParserConfig
    except ImportError:
        raise ImportError(f"❌ Modules parser refactorisés introuvables: {e}")


class AGIReportParser:
    """
    Parser pour fichier de rapport AGI.md (refactorisé).

    Interface principale qui délègue la complexité aux modules spécialisés
    pour respecter la limite de 200 lignes et l'architecture modulaire.
    """

    def __init__(self, logger, agi_md_path: Optional[str] = None):
        """TODO: Add docstring."""
        self.logger = logger
        self.helpers = ParserHelpers(logger)
        self.config = ParserConfig()
        self.agi_md_path = agi_md_path or self._get_default_agi_path()
        self.parsed_content: Optional[Dict[str, Any]] = None
        self.parsing_stats = {"sections_found": 0, "domains_extracted": 0, "errors": 0}

    def parse_report(self) -> Dict[str, Any]:
        """
        Parse le fichier AGI.md complet et retourne les spécifications.

        Returns:
            Dictionnaire contenant toutes les spécifications extraites
        """
        try:
            self.logger.info(f"📖 Parsing du rapport AGI: {self.agi_md_path}")

            # Validation du fichier
            if not self._validate_agi_file():
                return self.config.get_fallback_specifications()

            # Lecture du contenu
            content = self._read_agi_file()
            if not content:
                return self.config.get_fallback_specifications()

            # Parsing des sections principales
            parsed_data = self._parse_main_sections(content)

            # Validation et enrichissement
            validated_data = self._validate_and_enrich(parsed_data)

            # Cache du résultat
            self.parsed_content = validated_data
            self._update_parsing_stats(validated_data)

            self.logger.info(f"✅ Parsing terminé: {self.parsing_stats}")
            return validated_data

        except Exception as e:
            self.logger.error(f"❌ Erreur parsing AGI.md: {e}")
            self.logger.debug(traceback.format_exc())
            self.parsing_stats["errors"] += 1
            return self.config.get_fallback_specifications()

    def extract_domains(self) -> List[str]:
        """Extrait la liste des domaines du rapport."""
        try:
            if not self.parsed_content:
                self.parse_report()

            domains = self.parsed_content.get("domains", [])
            if not domains:
                domains = self.helpers.extract_domains_from_content(
                    self._read_agi_file()
                )

            self.logger.info(f"🔍 Domaines extraits: {len(domains)}")
            return domains

        except Exception as e:
            self.logger.error(f"❌ Erreur extraction domaines: {e}")
            return self.config.get_default_domains()

    def extract_project_metadata(self) -> Dict[str, Any]:
        """Extrait les métadonnées du projet."""
        try:
            if not self.parsed_content:
                self.parse_report()

            metadata = {
                "name": self.parsed_content.get("project_name", "Projet AGI"),
                "version": self.parsed_content.get("version", "1.0"),
                "description": self.parsed_content.get("description", "Projet AGI"),
                "author": self.parsed_content.get("author", "Équipe AGI"),
                "date": self.parsed_content.get("date", "2025"),
            }

            return metadata

        except Exception as e:
            self.logger.error(f"❌ Erreur extraction métadonnées: {e}")
            return self.config.get_default_metadata()

    def extract_architecture_info(self) -> Dict[str, Any]:
        """Extrait les informations d'architecture."""
        try:
            if not self.parsed_content:
                self.parse_report()

            architecture = {
                "type": self.parsed_content.get("architecture_type", "Modulaire"),
                "patterns": self.parsed_content.get("patterns", []),
                "principles": self.parsed_content.get("principles", []),
                "constraints": self.parsed_content.get("constraints", []),
            }

            return architecture

        except Exception as e:
            self.logger.error(f"❌ Erreur extraction architecture: {e}")
            return self.config.get_default_architecture()

    def validate_agi_compliance(self) -> Dict[str, Any]:
        """Valide la conformité du contenu AGI.md."""
        try:
            content = self._read_agi_file()
            return self.helpers.validate_agi_format(content)

        except Exception as e:
            self.logger.error(f"❌ Erreur validation conformité: {e}")
            return {"valid": False, "errors": [str(e)]}

    def get_parsing_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de parsing."""
        return self.parsing_stats.copy()

    def refresh_content(self) -> bool:
        """Recharge le contenu depuis le fichier."""
        try:
            self.parsed_content = None
            self.parsing_stats = {
                "sections_found": 0,
                "domains_extracted": 0,
                "errors": 0,
            }
            result = self.parse_report()
            return bool(result and result.get("domains"))

        except Exception as e:
            self.logger.error(f"❌ Erreur rechargement: {e}")
            return False

    def _validate_agi_file(self) -> bool:
        """Valide l'existence et l'accessibilité du fichier AGI.md."""
        try:
            agi_path = Path(self.agi_md_path)

            if not agi_path.exists():
                self.logger.error(f"❌ Fichier AGI.md introuvable: {self.agi_md_path}")
                return False

            if not agi_path.is_file():
                self.logger.error(f"❌ Chemin n'est pas un fichier: {self.agi_md_path}")
                return False

            if not agi_path.suffix.lower() == ".md":
                self.logger.warning(f"⚠️ Extension non standard: {agi_path.suffix}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur validation fichier AGI: {e}")
            return False

    def _read_agi_file(self) -> str:
        """Lit le contenu du fichier AGI.md."""
        try:
            agi_path = Path(self.agi_md_path)
            content = agi_path.read_text(encoding="utf-8")

            if len(content.strip()) < 100:
                self.logger.warning("⚠️ Fichier AGI.md très court")

            return content

        except UnicodeDecodeError as e:
            self.logger.error(f"❌ Erreur encodage fichier AGI: {e}")
            return ""
        except Exception as e:
            self.logger.error(f"❌ Erreur lecture fichier AGI: {e}")
            return ""

    def _parse_main_sections(self, content: str) -> Dict[str, Any]:
        """Parse les sections principales du contenu."""
        try:
            # Utilisation du helper pour extraction des sections
            sections = self.helpers.extract_sections(content)

            # Parsing spécialisé par section
            parsed_data = {}

            # Métadonnées de base
            parsed_data.update(self.helpers.parse_metadata_section(content))

            # Domaines
            parsed_data["domains"] = self.helpers.extract_domains_from_content(content)

            # Architecture
            parsed_data.update(self.helpers.parse_architecture_section(content))

            # Règles et contraintes
            parsed_data.update(self.helpers.parse_rules_section(content))

            # Statistiques
            self.parsing_stats["sections_found"] = len(sections)
            self.parsing_stats["domains_extracted"] = len(
                parsed_data.get("domains", [])
            )

            return parsed_data

        except Exception as e:
            self.logger.error(f"❌ Erreur parsing sections: {e}")
            return {}

    def _validate_and_enrich(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et enrichit les données parsées."""
        try:
            # Validation de base
            validated_data = self.helpers.validate_parsed_data(parsed_data)

            # Enrichissement avec valeurs par défaut
            enriched_data = self.helpers.enrich_with_defaults(validated_data)

            # Application des règles de configuration
            final_data = self.config.apply_parsing_rules(enriched_data)

            return final_data

        except Exception as e:
            self.logger.error(f"❌ Erreur validation/enrichissement: {e}")
            return parsed_data

    def _update_parsing_stats(self, parsed_data: Dict[str, Any]):
        """Met à jour les statistiques de parsing."""
        try:
            self.parsing_stats.update(
                {
                    "domains_extracted": len(parsed_data.get("domains", [])),
                    "metadata_found": bool(parsed_data.get("project_name")),
                    "architecture_found": bool(parsed_data.get("architecture_type")),
                    "rules_found": bool(parsed_data.get("rules")),
                    "total_content_length": len(str(parsed_data)),
                }
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur mise à jour stats: {e}")

    def _get_default_agi_path(self) -> str:
        """Détermine le chemin par défaut vers AGI.md."""
        # Recherche dans le répertoire courant et parent
        potential_paths = [
            Path.cwd() / "AGI.md",
            Path.cwd().parent / "AGI.md",
            Path(__file__).parent.parent.parent / "AGI.md",
        ]

        for path in potential_paths:
            if path.exists():
                return str(path)

        # Fallback - assume dans le répertoire courant
        return "AGI.md"

    def __str__(self) -> str:
        """Représentation string de l'instance."""
        return f"AGIReportParser(path={self.agi_md_path})"

    def __repr__(self) -> str:
        """Représentation debug de l'instance."""
        return f"AGIReportParser(path={self.agi_md_path}, parsed={bool(self.parsed_content)})"