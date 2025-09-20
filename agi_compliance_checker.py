#!/usr/bin/env python3
"""
CHEMIN: agi_compliance_checker.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""
AGI Compliance Checker - Vérificateur limite 200 lignes
Conforme à AGI.md - Vérifie que tous les fichiers Python respectent la limite
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


class AGIComplianceChecker:
    """Vérificateur de conformité aux directives AGI.md"""

    def __init__(self, max_lines: int = 200):
        """TODO: Add docstring."""
        self.max_lines = max_lines
        self.violations = []
        self.compliant_files = []
        self.total_files = 0

    def count_lines(self, file_path: Path) -> int:
        """Compte les lignes de code dans un fichier Python"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Filtrer les lignes vides et commentaires purs (optionnel)
                return len(lines)
        except Exception as e:
            print(f"Erreur lecture {file_path}: {e}")
            return 0

    def scan_directory(
        self, directory: str, exclude_patterns: List[str] = None
    ) -> None:
        """Scanne un répertoire pour tous les fichiers Python"""
        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", ".git", "venv", "env", ".pytest_cache"]

        directory_path = Path(directory)
        if not directory_path.exists():
            print(f"Répertoire non trouvé: {directory}")
            return

        # Trouver tous les fichiers Python
        for py_file in directory_path.rglob("*.py"):
            # Vérifier exclusions
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            lines = self.count_lines(py_file)
            self.total_files += 1

            if lines > self.max_lines:
                self.violations.append((py_file, lines))
            else:
                self.compliant_files.append((py_file, lines))

    def generate_report(self, verbose: bool = False) -> str:
        """Génère le rapport de conformité"""
        report = []
        report.append("=" * 60)
        report.append("RAPPORT DE CONFORMITÉ AGI.md - LIMITE 200 LIGNES")
        report.append("=" * 60)

        # Statistiques globales
        violation_count = len(self.violations)
        compliant_count = len(self.compliant_files)
        compliance_rate = (
            (compliant_count / self.total_files * 100) if self.total_files > 0 else 0
        )

        report.append(f"Fichiers analysés: {self.total_files}")
        report.append(f"Conformes (<= {self.max_lines} lignes): {compliant_count}")
        report.append(f"Violations (> {self.max_lines} lignes): {violation_count}")
        report.append(f"Taux de conformité: {compliance_rate:.1f}%")
        report.append("")

        # Violations détaillées
        if self.violations:
            report.append("🚨 VIOLATIONS DÉTECTÉES:")
            report.append("-" * 30)
            for file_path, lines in sorted(
                self.violations, key=lambda x: x[1], reverse=True
            ):
                excess = lines - self.max_lines
                relative_path = self._get_relative_path(file_path)
                report.append(f"❌ {relative_path}: {lines} lignes (+{excess})")
            report.append("")

        # Fichiers conformes (si verbose)
        if verbose and self.compliant_files:
            report.append("✅ FICHIERS CONFORMES:")
            report.append("-" * 20)
            for file_path, lines in sorted(
                self.compliant_files, key=lambda x: x[1], reverse=True
            ):
                relative_path = self._get_relative_path(file_path)
                report.append(f"✅ {relative_path}: {lines} lignes")

        # Recommandations
        if self.violations:
            report.append("")
            report.append("📋 ACTIONS RECOMMANDÉES:")
            report.append("-" * 25)
            report.append("1. Refactoriser les fichiers en violation")
            report.append("2. Déléguer la logique complexe vers des modules séparés")
            report.append("3. Respecter le principe de responsabilité unique")
            report.append("4. Utiliser la délégation plutôt que les monolithes")

        return "\n".join(report)

    def _get_relative_path(self, file_path: Path) -> str:
        """Retourne le chemin relatif pour l'affichage"""
        try:
            return str(file_path.relative_to(Path.cwd()))
        except ValueError:
            return str(file_path)

    def export_csv(self, output_file: str) -> None:
        """Exporte les résultats en CSV"""
        import csv

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Fichier", "Lignes", "Statut", "Excès"])

            # Violations
            for file_path, lines in self.violations:
                relative_path = self._get_relative_path(file_path)
                excess = lines - self.max_lines
                writer.writerow([relative_path, lines, "VIOLATION", excess])

            # Conformes
            for file_path, lines in self.compliant_files:
                relative_path = self._get_relative_path(file_path)
                writer.writerow([relative_path, lines, "CONFORME", 0])


def main():
    """TODO: Add docstring."""
    parser = argparse.ArgumentParser(
        description="Vérificateur de conformité AGI.md (limite 200 lignes)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s .                           # Vérifier le répertoire courant
  %(prog)s /path/to/project --verbose  # Rapport détaillé
  %(prog)s . --max-lines 150          # Limite personnalisée
  %(prog)s . --csv report.csv         # Export CSV
        """,
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Répertoire à analyser (défaut: répertoire courant)",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=200,
        help="Nombre maximum de lignes autorisé (défaut: 200)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Afficher aussi les fichiers conformes",
    )
    parser.add_argument("--csv", metavar="FILE", help="Exporter les résultats en CSV")
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=["__pycache__", ".git", "venv", "env", ".pytest_cache"],
        help="Patterns à exclure de l'analyse",
    )

    args = parser.parse_args()

    # Vérification conformité
    checker = AGIComplianceChecker(max_lines=args.max_lines)
    checker.scan_directory(args.directory, exclude_patterns=args.exclude)

    # Affichage rapport
    report = checker.generate_report(verbose=args.verbose)
    print(report)

    # Export CSV si demandé
    if args.csv:
        checker.export_csv(args.csv)
        print(f"\n📄 Résultats exportés vers: {args.csv}")

    # Code de sortie
    sys.exit(0 if not checker.violations else 1)


if __name__ == "__main__":
    main()