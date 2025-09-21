#!/usr/bin/env python3
"""
AGI Parser - Orchestrateur de Parsing du Rapport AGI.md (Refactorisé)
=====================================================================

Rôle Fondamental (Conforme AGI.md) :
- Orchestrer le processus de parsing du rapport AGI.md.
- Déléguer la logique d'extraction complexe à des modules spécialisés.
- Construire l'objet final ProjectSpec à partir des données extraites.

Conformité Architecturale :
- Limite stricte < 200 lignes.
- Responsabilité unique : orchestration du parsing.

Version : 2.0 (Refactorisé)
Date : 18 Septembre 2025
"""

from pathlib import Path
from typing import Optional
from datetime import datetime
import traceback

from models.specs import ProjectSpec
from . import extractors  # Import du nouveau module


class AGIReportParser:
    """
    Orchestre le parsing du rapport AGI.md en déléguant l'extraction
    de données à des fonctions spécialisées.
    """

    def __init__(self, logger):
        """TODO: Add docstring."""
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

    def parse_report(self) -> Optional[ProjectSpec]:
        """
        Parse le rapport AGI.md et retourne la spécification structurée.
        """
        try:
            self.logger.debug("🔍 Démarrage du parsing du rapport AGI.md")
            content = self._read_report_safely()
            if not content:
                return None

            # Délégation de l'extraction des sections
            sections = extractors.extract_sections(content, self.logger)
            if (
                "detailed_directives" not in sections
                or "architecture_principles" not in sections
            ):
                self.logger.error(
                    "❌ Sections critiques 'Directives' ou 'Principes' non trouvées dans AGI.md."
                )
                return None

            # Délégation de l'extraction des principes
            principles = extractors.parse_architecture_principles(
                sections["architecture_principles"]
            )
            self.logger.verbose(
                f"Principes architecturaux extraits : {len(principles)}"
            )

            # Délégation de l'extraction des domaines et fichiers
            domains = extractors.parse_domains_and_files(
                sections["detailed_directives"], self.domains_priority, self.logger
            )

            # Construction de la spécification finale
            project_spec = ProjectSpec(
                architecture_principles=principles,
                domains=domains,
                main_py_spec=self._get_main_py_spec(),
                global_directives=self._get_global_directives(),
                metadata={
                    "version": "1.0",
                    "date": datetime.now().strftime("%d %B %Y"),
                    "source": "AGI.md",
                },
            )

            self.logger.info(
                f"✅ Parsing terminé : {len(project_spec.domains)} domaines extraits."
            )
            return project_spec

        except Exception as e:
            self.logger.error(
                f"❌ Erreur critique lors du parsing de AGI.md : {str(e)}"
            )
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

    def _read_report_safely(self) -> Optional[str]:
        """Lit le fichier AGI.md de manière sécurisée."""
        if not self.report_path.exists():
            self.logger.error(
                f"Fichier AGI.md introuvable à : {self.report_path.resolve()}"
            )
            return None
        try:
            content = self.report_path.read_text(encoding="utf-8")
            if len(content) < 1000:
                self.logger.error(
                    "Fichier AGI.md semble corrompu (taille insuffisante)."
                )
                return None
            self.logger.debug(f"Fichier AGI.md lu ({len(content)} caractères).")
            return content
        except Exception as e:
            self.logger.error(f"Impossible de lire le fichier AGI.md : {e}")
            return None

    def _get_main_py_spec(self) -> dict:
        """Retourne les spécifications statiques pour main.py."""
        return {"role": "Orchestrateur Principal", "max_lines": 200}

    def _get_global_directives(self) -> dict:
        """Retourne les directives globales statiques."""
        return {"max_lines_per_file": 200, "security_by_design": True}