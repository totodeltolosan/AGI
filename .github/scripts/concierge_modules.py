#!/usr/bin/env python3
"""
🧹 Modules Le Concierge - Composants Modulaires
Directive SYNTAX-CORRECTOR-v1.0

Mission: Modules réutilisables pour la correction automatique
Auteur: Le Concierge (AGI Architecture Bot)
"""

import os
import subprocess
import tempfile
import ast
from pathlib import Path
from typing import List, Optional, Tuple
import json


class FileProcessor:
    """📝 Processeur de fichiers - Application des corrections"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"  📝 {message}")

    def apply_autoflake(self, file_path: str) -> bool:
        """Appliquer autoflake pour supprimer imports inutiles"""
        try:
            cmd = [
                'autoflake',
                '--in-place',
                '--remove-all-unused-imports',
                '--remove-unused-variables',
                '--ignore-init-module-imports',
                file_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log(f"Autoflake réussi sur {file_path}")
                return True
            else:
                self.log(f"Autoflake échoué: {result.stderr}")
                return False

        except Exception as e:
            self.log(f"Erreur autoflake: {e}")
            return False

    def apply_isort(self, file_path: str) -> bool:
        """Appliquer isort pour trier les imports"""
        try:
            cmd = [
                'isort',
                '--force-single-line',
                '--line-length=88',
                file_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log(f"Isort réussi sur {file_path}")
                return True
            else:
                self.log(f"Isort échoué: {result.stderr}")
                return False

        except Exception as e:
            self.log(f"Erreur isort: {e}")
            return False

    def apply_black(self, file_path: str) -> bool:
        """Appliquer black pour formatage standard"""
        try:
            cmd = [
                'black',
                '--line-length=88',
                '--target-version=py311',
                file_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log(f"Black réussi sur {file_path}")
                return True
            else:
                self.log(f"Black échoué: {result.stderr}")
                return False

        except Exception as e:
            self.log(f"Erreur black: {e}")
            return False

    def apply_autopep8(self, file_path: str) -> bool:
        """Appliquer autopep8 pour corrections PEP8"""
        try:
            cmd = [
                'autopep8',
                '--in-place',
                '--aggressive',
                '--aggressive',
                '--max-line-length=88',
                file_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log(f"Autopep8 réussi sur {file_path}")
                return True
            else:
                self.log(f"Autopep8 échoué: {result.stderr}")
                return False

        except Exception as e:
            self.log(f"Erreur autopep8: {e}")
            return False


class SyntaxValidator:
    """✅ Validateur de syntaxe Python"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"  ✅ {message}")

    def validate_file(self, file_path: str) -> bool:
        """Valider la syntaxe d'un fichier Python"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Compiler le code pour vérifier la syntaxe
            compile(content, file_path, 'exec')
            self.log(f"Syntaxe valide: {file_path}")
            return True

        except SyntaxError as e:
            self.log(f"Erreur de syntaxe dans {file_path}: {e}")
            return False
        except Exception as e:
            self.log(f"Erreur lors de la validation {file_path}: {e}")
            return False

    def get_syntax_error_details(self, file_path: str) -> str:
        """Obtenir les détails d'une erreur de syntaxe"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            compile(content, file_path, 'exec')
            return "Aucune erreur détectée"

        except SyntaxError as e:
            return f"Ligne {e.lineno}: {e.msg}"
        except Exception as e:
            return f"Erreur: {str(e)}"

    def validate_with_py_compile(self, file_path: str) -> Tuple[bool, str]:
        """Validation avec py_compile pour plus de précision"""
        try:
            cmd = ['python', '-m', 'py_compile', file_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, "Syntaxe valide"
            else:
                return False, result.stderr.strip()

        except Exception as e:
            return False, str(e)


class GitManager:
    """🔄 Gestionnaire Git pour commits automatiques"""

    def __init__(self, branch: str, verbose: bool = False):
        self.branch = branch
        self.verbose = verbose

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"  🔄 {message}")

    def configure_git(self) -> bool:
        """Configurer Git pour les commits automatiques"""
        try:
            # Configuration utilisateur pour commits automatiques
            subprocess.run([
                'git', 'config', 'user.name', 'Le Concierge Bot'
            ], check=True)

            subprocess.run([
                'git', 'config', 'user.email', 'concierge@agi-project.dev'
            ], check=True)

            self.log("Configuration Git réussie")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"Erreur configuration Git: {e}")
            return False

    def has_changes(self, files: List[str]) -> bool:
        """Vérifier s'il y a des changements dans les fichiers"""
        try:
            for file_path in files:
                result = subprocess.run([
                    'git', 'diff', '--name-only', file_path
                ], capture_output=True, text=True)

                if result.stdout.strip():
                    return True

            return False

        except Exception as e:
            self.log(f"Erreur vérification changements: {e}")
            return False

    def commit_changes(self, files: List[str], message: str) -> bool:
        """Committer les changements"""
        try:
            # Configurer Git
            if not self.configure_git():
                return False

            # Vérifier s'il y a des changements
            if not self.has_changes(files):
                self.log("Aucun changement à committer")
                return True

            # Ajouter les fichiers modifiés
            for file_path in files:
                subprocess.run(['git', 'add', file_path], check=True)
                self.log(f"Ajouté: {file_path}")

            # Créer le commit
            subprocess.run([
                'git', 'commit', '-m', message
            ], check=True)

            self.log(f"Commit créé: {message[:50]}...")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"Erreur lors du commit: {e}")
            return False
        except Exception as e:
            self.log(f"Erreur Git: {e}")
            return False


class CorrectionLogger:
    """📊 Logger pour traçabilité des corrections"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.log_data = {
            "corrections": [],
            "errors": [],
            "summary": {}
        }

    def log_correction(self, file_path: str, tool: str, success: bool, details: str = ""):
        """Logger une correction appliquée"""
        correction_entry = {
            "file": file_path,
            "tool": tool,
            "success": success,
            "details": details,
            "timestamp": self._get_timestamp()
        }

        self.log_data["corrections"].append(correction_entry)

        if self.verbose:
            status = "✅" if success else "❌"
            print(f"  📊 {status} {tool} sur {file_path}")

    def log_error(self, file_path: str, error_type: str, message: str):
        """Logger une erreur"""
        error_entry = {
            "file": file_path,
            "type": error_type,
            "message": message,
            "timestamp": self._get_timestamp()
        }

        self.log_data["errors"].append(error_entry)

        if self.verbose:
            print(f"  📊 ❌ Erreur {error_type} dans {file_path}: {message}")

    def generate_summary(self) -> dict:
        """Générer un résumé des corrections"""
        total_corrections = len(self.log_data["corrections"])
        successful_corrections = len([c for c in self.log_data["corrections"] if c["success"]])
        total_errors = len(self.log_data["errors"])

        tools_used = {}
        for correction in self.log_data["corrections"]:
            tool = correction["tool"]
            tools_used[tool] = tools_used.get(tool, 0) + 1

        self.log_data["summary"] = {
            "total_corrections": total_corrections,
            "successful_corrections": successful_corrections,
            "total_errors": total_errors,
            "tools_used": tools_used,
            "success_rate": (successful_corrections / total_corrections * 100) if total_corrections > 0 else 0
        }

        return self.log_data["summary"]

    def save_log(self, output_path: str = "concierge_log.json"):
        """Sauvegarder le log complet"""
        try:
            with open(output_path, 'w') as f:
                json.dump(self.log_data, f, indent=2)

            if self.verbose:
                print(f"  📊 Log sauvegardé: {output_path}")

        except Exception as e:
            if self.verbose:
                print(f"  📊 ❌ Erreur sauvegarde log: {e}")

    def _get_timestamp(self) -> str:
        """Obtenir timestamp actuel"""
        from datetime import datetime
        return datetime.now().isoformat()
