#!/usr/bin/env python3
"""
🧹 Le Concierge - Correcteur Syntaxique Automatique
Directive SYNTAX-CORRECTOR-v1.0

Mission: Corriger automatiquement les erreurs de syntaxe et formatage
Auteur: Le Concierge (AGI Architecture Bot)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Import modules concierge
from concierge_modules import (
    FileProcessor,
    SyntaxValidator,
    GitManager,
    CorrectionLogger
)

@dataclass
class CorrectionResult:
    """Résultat d'une correction de fichier"""
    file_path: str
    corrections_applied: List[str]
    syntax_valid: bool
    error_message: Optional[str] = None


class ConciergeOrchestrator:
    """🎯 Orchestrateur principal Le Concierge"""

    def __init__(self, branch: str, verbose: bool = False):
        self.branch = branch
        self.verbose = verbose
        self.corrections_made = []
        self.failed_files = []

        # Initialiser les modules
        self.file_processor = FileProcessor(verbose)
        self.syntax_validator = SyntaxValidator(verbose)
        self.git_manager = GitManager(branch, verbose)
        self.logger = CorrectionLogger(verbose)

    def log(self, message: str, level: str = "INFO") -> None:
        """Logging conditionnel"""
        if self.verbose or level == "ERROR":
            prefix = {"INFO": "🔍", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
            print(f"{prefix.get(level, '📝')} {message}")

    def correct_file(self, file_path: str) -> CorrectionResult:
        """Corriger un fichier Python"""
        self.log(f"Correction de {file_path}")

        if not Path(file_path).exists():
            return CorrectionResult(
                file_path=file_path,
                corrections_applied=[],
                syntax_valid=False,
                error_message=f"Fichier non trouvé: {file_path}"
            )

        # Étape 1: Vérification syntaxe initiale
        initial_valid = self.syntax_validator.validate_file(file_path)

        # Étape 2: Application des corrections
        corrections = []

        try:
            # Autoflake - suppression imports inutiles
            if self.file_processor.apply_autoflake(file_path):
                corrections.append("autoflake")
                self.log(f"  ✅ Autoflake appliqué sur {file_path}")

            # Isort - tri des imports
            if self.file_processor.apply_isort(file_path):
                corrections.append("isort")
                self.log(f"  ✅ Isort appliqué sur {file_path}")

            # Black - formatage standard
            if self.file_processor.apply_black(file_path):
                corrections.append("black")
                self.log(f"  ✅ Black appliqué sur {file_path}")

            # Autopep8 - corrections PEP8 supplémentaires
            if self.file_processor.apply_autopep8(file_path):
                corrections.append("autopep8")
                self.log(f"  ✅ Autopep8 appliqué sur {file_path}")

        except Exception as e:
            return CorrectionResult(
                file_path=file_path,
                corrections_applied=corrections,
                syntax_valid=False,
                error_message=f"Erreur lors de la correction: {e}"
            )

        # Étape 3: Vérification syntaxe finale
        final_valid = self.syntax_validator.validate_file(file_path)

        result = CorrectionResult(
            file_path=file_path,
            corrections_applied=corrections,
            syntax_valid=final_valid
        )

        if not final_valid:
            error_details = self.syntax_validator.get_syntax_error_details(file_path)
            result.error_message = error_details

        return result

    def process_files(self, file_list: List[str]) -> Dict[str, CorrectionResult]:
        """Traiter une liste de fichiers"""
        results = {}

        self.log(f"Traitement de {len(file_list)} fichiers", "INFO")

        for file_path in file_list:
            if not file_path.strip() or not file_path.endswith('.py'):
                continue

            result = self.correct_file(file_path.strip())
            results[file_path] = result

            if result.corrections_applied:
                self.corrections_made.append(file_path)

            if not result.syntax_valid:
                self.failed_files.append(file_path)

        return results

    def commit_corrections(self, results: Dict[str, CorrectionResult]) -> bool:
        """Committer les corrections si nécessaire"""
        files_with_corrections = [
            path for path, result in results.items()
            if result.corrections_applied
        ]

        if not files_with_corrections:
            self.log("Aucune correction à committer", "INFO")
            return True

        # Créer message de commit détaillé
        commit_message = self.create_commit_message(results)

        # Committer les changements
        success = self.git_manager.commit_changes(
            files_with_corrections,
            commit_message
        )

        if success:
            self.log(f"✅ Corrections committées: {len(files_with_corrections)} fichiers", "SUCCESS")
        else:
            self.log("❌ Échec du commit des corrections", "ERROR")

        return success

    def create_commit_message(self, results: Dict[str, CorrectionResult]) -> str:
        """Créer un message de commit détaillé"""
        corrections_summary = {}
        total_files = 0

        for result in results.values():
            if result.corrections_applied:
                total_files += 1
                for correction in result.corrections_applied:
                    corrections_summary[correction] = corrections_summary.get(correction, 0) + 1

        # Message principal
        commit_msg = "style(auto): Application du formatage constitutionnel\n\n"

        # Détails des corrections
        commit_msg += f"🧹 Le Concierge - {total_files} fichier(s) corrigé(s)\n\n"

        for tool, count in corrections_summary.items():
            commit_msg += f"• {tool}: {count} fichier(s)\n"

        commit_msg += f"\nDirective: SYNTAX-CORRECTOR-v1.0"

        return commit_msg

    def generate_summary_report(self, results: Dict[str, CorrectionResult]) -> str:
        """Générer un résumé des corrections"""
        total_files = len(results)
        corrected_files = len([r for r in results.values() if r.corrections_applied])
        failed_files = len([r for r in results.values() if not r.syntax_valid])

        report = f"""## 🧹 Rapport de Correction Automatique

### 📊 Résumé
- **Fichiers traités**: {total_files}
- **Fichiers corrigés**: {corrected_files}
- **Erreurs persistantes**: {failed_files}

### 🎯 Détails par Fichier
"""

        for file_path, result in results.items():
            status = "✅" if result.syntax_valid else "❌"
            corrections = ", ".join(result.corrections_applied) if result.corrections_applied else "Aucune"

            report += f"\n**{status} `{file_path}`**\n"
            report += f"- Corrections: {corrections}\n"

            if result.error_message:
                report += f"- ⚠️ Erreur: {result.error_message}\n"

        return report


def parse_arguments() -> argparse.Namespace:
    """Parser les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="🧹 Le Concierge - Correcteur Syntaxique Automatique"
    )

    parser.add_argument(
        '--files',
        type=str,
        required=True,
        help='Liste des fichiers à corriger (séparés par des nouvelles lignes)'
    )

    parser.add_argument(
        '--branch',
        type=str,
        required=True,
        help='Nom de la branche de travail'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbose pour debugging'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulation sans commit effectif'
    )

    return parser.parse_args()


def main():
    """Point d'entrée principal"""
    args = parse_arguments()

    # Traiter la liste des fichiers
    file_list = [f.strip() for f in args.files.split('\n') if f.strip()]

    if not file_list:
        print("🔍 Aucun fichier à traiter")
        return 0

    # Initialiser Le Concierge
    concierge = ConciergeOrchestrator(args.branch, args.verbose)

    print(f"🧹 Le Concierge - Début de la correction automatique")
    print(f"📁 Branche: {args.branch}")
    print(f"📝 Fichiers: {len(file_list)}")

    # Traiter les fichiers
    results = concierge.process_files(file_list)

    # Générer le rapport
    report = concierge.generate_summary_report(results)
    print(report)

    # Sauvegarder le rapport
    with open('correction_report.md', 'w') as f:
        f.write(report)

    # Committer si nécessaire et pas en dry-run
    if not args.dry_run:
        commit_success = concierge.commit_corrections(results)

        # Déterminer le code de sortie
        if concierge.failed_files:
            print(f"\n❌ {len(concierge.failed_files)} fichier(s) avec erreurs persistantes")
            for failed_file in concierge.failed_files:
                print(f"   • {failed_file}")
            return 1
        elif not commit_success and concierge.corrections_made:
            print(f"\n⚠️ Erreur lors du commit des corrections")
            return 1

    print(f"\n✅ Mission accomplie - Le Concierge")
    return 0


if __name__ == "__main__":
    sys.exit(main())
