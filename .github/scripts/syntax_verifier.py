#!/usr/bin/env python3
"""
✅ Le Concierge - Vérificateur de Syntaxe Final
Directive SYNTAX-CORRECTOR-v1.0

Mission: Vérification finale de la syntaxe après corrections
Auteur: Le Concierge Verifier (AGI Architecture Bot)
"""

import os
import sys
import ast
import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SyntaxCheck:
    """Résultat d'une vérification de syntaxe"""
    file_path: str
    is_valid: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None


class SyntaxVerifier:
    """✅ Vérificateur de syntaxe Python avancé"""

    def __init__(self, strict: bool = False, verbose: bool = False):
        self.strict = strict
        self.verbose = verbose
        self.checks_performed = []
        self.errors_found = []
        self.warnings_found = []

    def log(self, message: str, level: str = "INFO") -> None:
        """Logging conditionnel"""
        if self.verbose or level == "ERROR":
            prefix = {"INFO": "🔍", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
            print(f"{prefix.get(level, '📝')} {message}")

    def check_file_syntax(self, file_path: str) -> SyntaxCheck:
        """Vérifier la syntaxe d'un fichier Python"""
        if not Path(file_path).exists():
            return SyntaxCheck(
                file_path=file_path,
                is_valid=False,
                error_type="FileNotFound",
                error_message=f"Fichier non trouvé: {file_path}"
            )

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Méthode 1: Compilation AST
            try:
                ast.parse(content, filename=file_path)
                self.log(f"Syntaxe AST valide: {file_path}", "SUCCESS")

                # Méthode 2: Compilation bytecode (plus stricte)
                compile(content, file_path, 'exec')
                self.log(f"Compilation bytecode réussie: {file_path}", "SUCCESS")

                return SyntaxCheck(
                    file_path=file_path,
                    is_valid=True
                )

            except SyntaxError as e:
                self.log(f"Erreur de syntaxe dans {file_path}: {e}", "ERROR")
                return SyntaxCheck(
                    file_path=file_path,
                    is_valid=False,
                    error_type="SyntaxError",
                    error_message=str(e.msg) if e.msg else str(e),
                    line_number=e.lineno,
                    column_number=e.offset
                )

        except UnicodeDecodeError as e:
            self.log(f"Erreur d'encodage dans {file_path}: {e}", "ERROR")
            return SyntaxCheck(
                file_path=file_path,
                is_valid=False,
                error_type="UnicodeDecodeError",
                error_message=str(e)
            )
        except Exception as e:
            self.log(f"Erreur inattendue lors de la vérification {file_path}: {e}", "ERROR")
            return SyntaxCheck(
                file_path=file_path,
                is_valid=False,
                error_type="UnexpectedError",
                error_message=str(e)
            )

    def check_with_py_compile(self, file_path: str) -> SyntaxCheck:
        """Vérification avec py_compile (plus robuste)"""
        try:
            cmd = ['python', '-m', 'py_compile', file_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log(f"py_compile réussi: {file_path}", "SUCCESS")
                return SyntaxCheck(
                    file_path=file_path,
                    is_valid=True
                )
            else:
                error_output = result.stderr.strip()
                self.log(f"py_compile échoué pour {file_path}: {error_output}", "ERROR")

                # Parser l'erreur pour extraire ligne et message
                line_num = None
                error_msg = error_output

                # Format typique: "File "path", line X, ..."
                if 'line ' in error_output:
                    try:
                        line_part = error_output.split('line ')[1]
                        line_num = int(line_part.split(',')[0])
                    except:
                        pass

                return SyntaxCheck(
                    file_path=file_path,
                    is_valid=False,
                    error_type="CompilationError",
                    error_message=error_msg,
                    line_number=line_num
                )

        except subprocess.TimeoutExpired:
            return SyntaxCheck(
                file_path=file_path,
                is_valid=False,
                error_type="TimeoutError",
                error_message="Timeout lors de la compilation"
            )
        except Exception as e:
            return SyntaxCheck(
                file_path=file_path,
                is_valid=False,
                error_type="ProcessError",
                error_message=str(e)
            )

    def verify_python_files(self, file_paths: List[str]) -> List[SyntaxCheck]:
        """Vérifier une liste de fichiers Python"""
        results = []

        self.log(f"Vérification de {len(file_paths)} fichiers Python")

        for file_path in file_paths:
            if not file_path.strip() or not file_path.endswith('.py'):
                continue

            file_path = file_path.strip()
            self.log(f"Vérification: {file_path}")

            # Vérification principale
            check_result = self.check_file_syntax(file_path)

            # Vérification secondaire avec py_compile si strict mode
            if self.strict and check_result.is_valid:
                py_compile_result = self.check_with_py_compile(file_path)
                if not py_compile_result.is_valid:
                    check_result = py_compile_result

            results.append(check_result)

            if check_result.is_valid:
                self.log(f"✅ {file_path} - Syntaxe valide")
            else:
                self.errors_found.append(check_result)
                self.log(f"❌ {file_path} - {check_result.error_message}", "ERROR")

        return results

    def scan_directory_for_python_files(self, directory: str = ".") -> List[str]:
        """Scanner un répertoire pour trouver tous les fichiers Python"""
        python_files = []

        try:
            for path in Path(directory).rglob("*.py"):
                if path.is_file():
                    python_files.append(str(path))

            self.log(f"Trouvé {len(python_files)} fichiers Python dans {directory}")
            return python_files

        except Exception as e:
            self.log(f"Erreur lors du scan du répertoire {directory}: {e}", "ERROR")
            return []

    def generate_verification_report(self, results: List[SyntaxCheck]) -> Dict:
        """Générer un rapport de vérification"""
        total_files = len(results)
        valid_files = len([r for r in results if r.is_valid])
        invalid_files = total_files - valid_files

        # Grouper les erreurs par type
        error_types = {}
        for result in results:
            if not result.is_valid and result.error_type:
                error_types[result.error_type] = error_types.get(result.error_type, 0) + 1

        # Détails des erreurs
        error_details = []
        for result in results:
            if not result.is_valid:
                error_details.append({
                    "file": result.file_path,
                    "type": result.error_type,
                    "message": result.error_message,
                    "line": result.line_number,
                    "column": result.column_number
                })

        report = {
            "timestamp": datetime.now().isoformat(),
            "directive": "SYNTAX-CORRECTOR-v1.0",
            "verification_mode": "strict" if self.strict else "standard",
            "summary": {
                "total_files": total_files,
                "valid_files": valid_files,
                "invalid_files": invalid_files,
                "success_rate": (valid_files / total_files * 100) if total_files > 0 else 0
            },
            "error_statistics": error_types,
            "syntax_errors": invalid_files,
            "warnings": len(self.warnings_found),
            "error_details": error_details,
            "status": "success" if invalid_files == 0 else "failure"
        }

        return report

    def save_report(self, report: Dict, output_file: str) -> None:
        """Sauvegarder le rapport de vérification"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.log(f"Rapport sauvegardé: {output_file}", "SUCCESS")

        except Exception as e:
            self.log(f"Erreur sauvegarde rapport: {e}", "ERROR")


def parse_arguments() -> argparse.Namespace:
    """Parser les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="✅ Le Concierge Verifier - Vérification Syntaxe Python"
    )

    parser.add_argument(
        '--files',
        type=str,
        help='Liste des fichiers à vérifier (séparés par des nouvelles lignes)'
    )

    parser.add_argument(
        '--directory',
        type=str,
        default='.',
        help='Répertoire à scanner pour les fichiers Python'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Mode strict avec py_compile'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbose'
    )

    parser.add_argument(
        '--report-file',
        type=str,
        default='syntax_verification.json',
        help='Fichier de sortie pour le rapport JSON'
    )

    return parser.parse_args()


def main():
    """Point d'entrée principal"""
    args = parse_arguments()

    print("✅ Le Concierge Verifier - Vérification finale de syntaxe")

    verifier = SyntaxVerifier(args.strict, args.verbose)

    # Déterminer les fichiers à vérifier
    files_to_check = []

    if args.files:
        # Fichiers spécifiés explicitement
        files_to_check = [f.strip() for f in args.files.split('\n') if f.strip()]
        verifier.log(f"Fichiers spécifiés: {len(files_to_check)}")
    else:
        # Scanner le répertoire
        files_to_check = verifier.scan_directory_for_python_files(args.directory)
        verifier.log(f"Fichiers trouvés dans {args.directory}: {len(files_to_check)}")

    if not files_to_check:
        print("🔍 Aucun fichier Python à vérifier")
        return 0

    # Effectuer la vérification
    results = verifier.verify_python_files(files_to_check)

    # Générer le rapport
    report = verifier.generate_verification_report(results)

    # Sauvegarder le rapport
    verifier.save_report(report, args.report_file)

    # Afficher le résumé
    summary = report['summary']
    print(f"\n📊 Résumé de Vérification:")
    print(f"   Total fichiers: {summary['total_files']}")
    print(f"   Fichiers valides: {summary['valid_files']}")
    print(f"   Fichiers invalides: {summary['invalid_files']}")
    print(f"   Taux de réussite: {summary['success_rate']:.1f}%")

    # Déterminer le code de sortie
    if summary['invalid_files'] > 0:
        print(f"\n❌ {summary['invalid_files']} fichier(s) avec erreurs de syntaxe")
        return 1
    else:
        print(f"\n✅ Tous les fichiers ont une syntaxe valide")
        return 0


if __name__ == "__main__":
    sys.exit(main())
