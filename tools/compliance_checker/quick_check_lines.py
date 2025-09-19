#!/usr/bin/env python3
"""
Quick Check Lines - Vérification rapide des violations de la directive 200 lignes
Outil de validation de base pour le projet AGI

Usage:
    python3 tools/compliance_checker/quick_check_lines.py
    python3 tools/compliance_checker/quick_check_lines.py --target ./tools/project_initializer/
    python3 tools/compliance_checker/quick_check_lines.py --csv output.csv
"""

import os
import sys
import csv
import argparse
from pathlib import Path
from typing import List, Tuple, NamedTuple
from datetime import datetime


class FileStatus(NamedTuple):
    """Statut d'un fichier vis-à-vis de la directive 200 lignes"""

    file_path: str
    line_count: int
    status: str  # 'CONFORME' ou 'VIOLATION'
    excess: int  # Nombre de lignes en excès (0 si conforme)


class LineChecker:
    """Vérificateur rapide de la directive 200 lignes"""

    def __init__(self, max_lines: int = 200):
        self.max_lines = max_lines
        self.results: List[FileStatus] = []

    def check_file(self, file_path: Path) -> FileStatus:
        """Vérifie un fichier spécifique"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                line_count = len(lines)

            if line_count <= self.max_lines:
                return FileStatus(
                    file_path=str(file_path),
                    line_count=line_count,
                    status="CONFORME",
                    excess=0,
                )
            else:
                excess = line_count - self.max_lines
                return FileStatus(
                    file_path=str(file_path),
                    line_count=line_count,
                    status="VIOLATION",
                    excess=excess,
                )
        except Exception as e:
            print(f"⚠️  Erreur lecture {file_path}: {e}")
            return FileStatus(
                file_path=str(file_path), line_count=0, status="ERREUR", excess=0
            )

    def check_directory(
        self, target_dir: Path, recursive: bool = True
    ) -> List[FileStatus]:
        """Vérifie tous les fichiers Python d'un répertoire"""
        self.results = []

        if not target_dir.exists():
            print(f"❌ Répertoire non trouvé: {target_dir}")
            return self.results

        # Recherche des fichiers Python
        if recursive:
            python_files = list(target_dir.rglob("*.py"))
        else:
            python_files = list(target_dir.glob("*.py"))

        print(f"🔍 Vérification de {len(python_files)} fichiers Python...")

        for py_file in python_files:
            status = self.check_file(py_file)
            self.results.append(status)

        return self.results

    def print_summary(self, results: List[FileStatus] = None):
        """Affiche un résumé des résultats"""
        if results is None:
            results = self.results

        if not results:
            print("❌ Aucun résultat à afficher")
            return

        violations = [r for r in results if r.status == "VIOLATION"]
        conformes = [r for r in results if r.status == "CONFORME"]
        errors = [r for r in results if r.status == "ERREUR"]

        print("\n" + "=" * 60)
        print(f"📊 RÉSUMÉ - DIRECTIVE 200 LIGNES MAX")
        print("=" * 60)
        print(f"Total fichiers: {len(results)}")
        print(f"✅ Conformes: {len(conformes)}")
        print(f"❌ Violations: {len(violations)}")
        print(f"⚠️  Erreurs: {len(errors)}")

        if violations:
            print(f"\n🚨 VIOLATIONS DÉTECTÉES:")
            print(f"{'Fichier':<50} {'Lignes':<8} {'Excès':<8}")
            print("-" * 66)

            # Tri par excès décroissant
            violations_sorted = sorted(violations, key=lambda x: x.excess, reverse=True)
            for violation in violations_sorted:
                filename = Path(violation.file_path).name
                if len(filename) > 45:
                    filename = "..." + filename[-42:]
                print(f"{filename:<50} {violation.line_count:<8} {violation.excess:<8}")

        # Calcul du pourcentage de conformité
        conformity_rate = len(conformes) / len(results) * 100 if results else 0

        print(f"\n🎯 TAUX DE CONFORMITÉ: {conformity_rate:.1f}%")

        if conformity_rate == 100:
            print(
                "🏆 FÉLICITATIONS! Tous les fichiers respectent la directive 200 lignes!"
            )
        elif conformity_rate >= 80:
            print("📈 Bonne conformité, quelques ajustements nécessaires")
        elif conformity_rate >= 50:
            print("⚡ Refactorisation partielle requise")
        else:
            print("🔥 REFACTORISATION MAJEURE URGENTE")

    def export_csv(self, output_file: Path, results: List[FileStatus] = None):
        """Exporte les résultats en CSV"""
        if results is None:
            results = self.results

        try:
            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Fichier", "Lignes", "Statut", "Excès"])

                for result in results:
                    writer.writerow(
                        [
                            result.file_path,
                            result.line_count,
                            result.status,
                            result.excess,
                        ]
                    )

            print(f"📄 Rapport CSV exporté: {output_file}")

        except Exception as e:
            print(f"❌ Erreur export CSV: {e}")


def find_project_root() -> Path:
    """Trouve la racine du projet AGI"""
    current = Path.cwd()

    # Recherche du répertoire contenant AGI.md
    for parent in [current] + list(current.parents):
        if (parent / "AGI.md").exists():
            return parent
        if (parent / "tools" / "project_initializer").exists():
            return parent

    # Si pas trouvé, utilise le répertoire courant
    return current


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Vérification rapide de la directive 200 lignes max",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--target", type=str, help="Répertoire à vérifier (défaut: auto-détection)"
    )
    parser.add_argument("--csv", type=str, help="Fichier CSV de sortie")
    parser.add_argument(
        "--no-recursive", action="store_true", help="Ne pas parcourir récursivement"
    )
    parser.add_argument(
        "--max-lines", type=int, default=200, help="Limite de lignes (défaut: 200)"
    )

    args = parser.parse_args()

    # Détermination du répertoire cible
    if args.target:
        target_dir = Path(args.target)
    else:
        # Auto-détection
        project_root = find_project_root()
        target_dir = project_root / "tools" / "project_initializer"

        if not target_dir.exists():
            target_dir = project_root

        print(f"🎯 Auto-détection: {target_dir}")

    # Initialisation du vérificateur
    checker = LineChecker(max_lines=args.max_lines)

    # Exécution de la vérification
    results = checker.check_directory(target_dir, recursive=not args.no_recursive)

    # Affichage des résultats
    checker.print_summary(results)

    # Export CSV si demandé
    if args.csv:
        csv_path = Path(args.csv)
        checker.export_csv(csv_path, results)

    # Code de sortie basé sur les violations
    violations = [r for r in results if r.status == "VIOLATION"]
    if violations:
        print(
            f"\n💡 Conseil: Utilisez full_audit.py pour une analyse détaillée des violations"
        )
        sys.exit(1)
    else:
        print(f"\n🎉 Aucune violation détectée!")
        sys.exit(0)


if __name__ == "__main__":
    main()
