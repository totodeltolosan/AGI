#!/usr/bin/env python3
"""
Project Initializer - CLI Principal du Générateur de Squelette AGI
===================================================================

Rôle Fondamental (Conforme AGI.md - tools/project_initializer/) :
- Générer l'intégralité de la structure de répertoires du projet conforme à AGI.md
- Générer chaque fichier Python (.py) et données (.json, .md) avec contenu minimaliste
- Inclure des stubs de code (imports, classes, fonctions, docstrings, annotations)
- Assurer la conformité à la directive des 200 lignes de code maximum par fichier
- CLI avec options pour initier le projet, spécifier chemins, inclure/exclure modules
- S'appuyer sur AGI.md comme source unique de vérité pour la génération
- Traçabilité complète via logging multi-niveaux (INFO, VERBOSE, DEBUG)

Conformité Architecturale :
- Limite stricte < 200 lignes via délégation modulaire
- Sécurité by Design : validation des chemins, résistance aux injections
- Modularité et Découplage : délégation à report_parser.py, structure_generator.py
- Observabilité Complète : logging granulaire avec options --verbose, --debug

Version : 1.0
Date : 17 Septembre 2025
Référence : Rapport de Directives AGI.md - Section tools/project_initializer/
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import os
import traceback


# === CONFIGURATION LOGGING MULTI-NIVEAUX ===
class AGILogger:
    """Logger dédié au project_initializer avec niveaux hiérarchiques."""

    LEVELS = {
        "ERROR": logging.ERROR,  # Erreurs uniquement
        "INFO": logging.INFO,  # Informations de base (défaut)
        "VERBOSE": 15,  # --verbose : détails de génération
        "DEBUG": logging.DEBUG,  # --debug : granularité maximale
    }

    def __init__(self, level: str = "INFO", log_file: Optional[str] = None):
        """Initialise le logger avec niveau et fichier optionnel."""
        logging.addLevelName(15, "VERBOSE")
        self.logger = logging.getLogger("project_initializer")
        self.logger.setLevel(self.LEVELS[level])

        # Format détaillé pour traçabilité
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )

        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler fichier si spécifié
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def verbose(self, msg: str):
        self.logger.log(15, msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def error(self, msg: str):
        self.logger.error(msg)


# === GÉNÉRATEUR PRINCIPAL ===
class ProjectInitializer:
    """
    Orchestrateur principal de génération du squelette AGI.

    Délègue la complexité à des modules spécialisés pour respecter
    la limite de 200 lignes et les principes de modularité d'AGI.md.
    """

    def __init__(self, logger: AGILogger):
        self.logger = logger
        self.base_path = Path(__file__).parent

    def generate_project(
        self,
        output_dir: str,
        exclude_modules: List[str] = None,
        include_modules: List[str] = None,
    ) -> bool:
        """
        Génère le squelette complet du projet AGI.

        Args:
            output_dir: Répertoire de sortie pour le projet
            exclude_modules: Modules à exclure de la génération
            include_modules: Modules spécifiques à inclure uniquement

        Returns:
            bool: True si génération réussie, False sinon
        """
        try:
            self.logger.info(f"🚀 Démarrage génération squelette AGI")
            self.logger.verbose(f"Répertoire de sortie: {output_dir}")

            # Étape 1: Validation des paramètres
            if not self._validate_output_path(output_dir):
                return False

            # Étape 2: Parse du rapport AGI.md
            self.logger.verbose("📖 Parsing du Rapport de Directives AGI.md")
            project_spec = self._parse_agi_report()
            if not project_spec:
                return False

            # Étape 3: Génération de la structure
            self.logger.verbose("🏗️  Génération de l'arborescence de répertoires")
            if not self._generate_directory_structure(output_dir, project_spec):
                return False

            # Étape 4: Génération des fichiers par domaine (ordre de priorité AGI.md)
            domains_order = [
                "compliance",
                "development_governance",
                "config",
                "supervisor",
                "plugins",
                "core",
                "data",
                "runtime_compliance",
                "ecosystem",
                "ui",
                "ai_compliance",
            ]

            for domain in domains_order:
                if self._should_include_domain(
                    domain, include_modules, exclude_modules
                ):
                    self.logger.verbose(f"⚙️  Génération domaine: {domain}/")
                    if not self._generate_domain_files(
                        output_dir, domain, project_spec
                    ):
                        return False

            # Étape 5: Génération du main.py (orchestrateur principal)
            self.logger.verbose("🎯 Génération du main.py (orchestrateur)")
            if not self._generate_main_file(output_dir, project_spec):
                return False

            self.logger.info(f"✅ Squelette AGI généré avec succès dans: {output_dir}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur critique lors de la génération: {str(e)}")
            self.logger.debug(f"Traceback complet:\n{traceback.format_exc()}")
            return False

    def _validate_output_path(self, output_dir: str) -> bool:
        """Valide et sécurise le chemin de sortie."""
        try:
            path = Path(output_dir).resolve()
            # Sécurité: éviter les chemins système critiques
            forbidden_paths = [Path("/"), Path("/bin"), Path("/etc"), Path("/usr")]
            if any(str(path).startswith(str(fp)) for fp in forbidden_paths):
                self.logger.error(f"❌ Chemin de sortie non autorisé: {path}")
                return False
            self.logger.debug(f"✅ Chemin de sortie validé: {path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur validation chemin: {e}")
            return False

    def _parse_agi_report(self) -> Optional[Dict[str, Any]]:
        """Délègue le parsing du rapport AGI.md à report_parser.py."""
        try:
            # Import dynamique pour délégation modulaire
            from .report_parser import AGIReportParser

            parser = AGIReportParser(self.logger)
            return parser.parse_report()
        except ImportError as e:
            self.logger.error(f"❌ Module report_parser.py introuvable: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Erreur parsing rapport AGI.md: {e}")
            return None

    def _generate_directory_structure(
        self, output_dir: str, spec: Dict[str, Any]
    ) -> bool:
        """Délègue la génération de structure à structure_generator.py."""
        try:
            from .structure_generator import StructureGenerator

            generator = StructureGenerator(self.logger)
            return generator.create_directories(output_dir, spec)
        except ImportError as e:
            self.logger.error(f"❌ Module structure_generator.py introuvable: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erreur génération structure: {e}")
            return False

    def _generate_domain_files(
        self, output_dir: str, domain: str, spec: Dict[str, Any]
    ) -> bool:
        """Délègue la génération de fichiers aux générateurs spécialisés."""
        try:
            from .file_generators.python_generator import PythonGenerator
            from .file_generators.json_generator import JsonGenerator
            from .file_generators.markdown_generator import MarkdownGenerator

            generators = {
                "py": PythonGenerator(self.logger),
                "json": JsonGenerator(self.logger),
                "md": MarkdownGenerator(self.logger),
            }

            # Génération par type de fichier
            for file_type, generator in generators.items():
                if not generator.generate_domain_files(output_dir, domain, spec):
                    return False
            return True
        except ImportError as e:
            self.logger.error(f"❌ Modules générateurs introuvables: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erreur génération fichiers domaine {domain}: {e}")
            return False

    def _generate_main_file(self, output_dir: str, spec: Dict[str, Any]) -> bool:
        """Génère le main.py selon les directives AGI.md."""
        try:
            from .file_generators.python_generator import PythonGenerator

            generator = PythonGenerator(self.logger)
            return generator.generate_main_file(output_dir, spec)
        except Exception as e:
            self.logger.error(f"❌ Erreur génération main.py: {e}")
            return False

    def _should_include_domain(
        self, domain: str, include: List[str], exclude: List[str]
    ) -> bool:
        """Détermine si un domaine doit être inclus selon les filtres."""
        if exclude and domain in exclude:
            return False
        if include and domain not in include:
            return False
        return True


# === CLI PRINCIPAL ===
def main():
    """Point d'entrée CLI avec options de debugging multi-niveaux."""
    parser = argparse.ArgumentParser(
        description="Générateur de Squelette AGI - Conforme aux Directives AGI.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s --output ./mon_projet_agi
  %(prog)s -v --output ./mon_projet_agi
  %(prog)s --debug --log-file ./generation.log --output ./test_agi
  %(prog)s --exclude plugins/ --output ./agi_minimal
        """,
    )

    # Options principales
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Répertoire de sortie pour le squelette AGI",
    )

    # Options de debugging (directive utilisateur)
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Affichage détaillé du processus de génération",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Niveau de détail maximal pour diagnostic"
    )
    parser.add_argument(
        "--log-file", type=str, help="Redirection des logs vers un fichier"
    )

    # Options de filtrage
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Modules à exclure de la génération",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Modules spécifiques à inclure uniquement",
    )

    args = parser.parse_args()

    # Configuration du logger selon les options
    log_level = "DEBUG" if args.debug else ("VERBOSE" if args.verbose else "INFO")
    logger = AGILogger(level=log_level, log_file=args.log_file)

    # Génération du projet
    initializer = ProjectInitializer(logger)
    success = initializer.generate_project(
        output_dir=args.output,
        exclude_modules=args.exclude,
        include_modules=args.include if args.include else None,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
