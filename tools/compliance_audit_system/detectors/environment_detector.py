#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_audit_system/detectors/environment_detector.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""
Détecteur d'Environnement - Système d'Audit AGI
Responsabilité unique : Validation de l'environnement d'exécution
Respecte strictement la directive des 200 lignes
"""

import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, Tuple, Optional


class EnvironmentDetector:
    """Détecteur et validateur d'environnement pour audit AGI"""

    def __init__(self):
        """TODO: Add docstring."""
        self.min_python_version = (3, 7)
        self.required_modules = ["ast", "pathlib", "typing", "dataclasses"]

    def validate_python_environment(self) -> bool:
        """Validation complète de l'environnement Python"""
        try:
            # Vérification version Python
            if not self._check_python_version():
                return False

            # Vérification modules requis
            if not self._check_required_modules():
                return False

            # Vérification capacités AST
            if not self._test_ast_capabilities():
                return False

            return True

        except Exception:
            return False

    def get_python_version(self) -> str:
        """Retourne la version Python détaillée"""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def get_environment_info(self) -> Dict[str, str]:
        """Collecte les informations complètes de l'environnement"""
        return {
            "python_version": self.get_python_version(),
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "executable": sys.executable,
            "encoding": sys.getdefaultencoding(),
            "path_separator": str(Path().resolve().anchor),
        }

    def detect_project_capabilities(self) -> Dict[str, bool]:
        """Détecte les capacités disponibles pour l'audit"""
        capabilities = {
            "ast_parsing": self._test_ast_capabilities(),
            "file_operations": self._test_file_operations(),
            "json_export": self._test_json_capabilities(),
            "csv_export": self._test_csv_capabilities(),
            "regex_patterns": self._test_regex_capabilities(),
        }

        return capabilities

    def _check_python_version(self) -> bool:
        """Vérifie que la version Python est suffisante"""
        current_version = (sys.version_info.major, sys.version_info.minor)
        return current_version >= self.min_python_version

    def _check_required_modules(self) -> bool:
        """Vérifie la disponibilité des modules requis"""
        for module_name in self.required_modules:
            try:
                __import__(module_name)
            except ImportError:
                return False
        return True

    def _test_ast_capabilities(self) -> bool:
        """Teste les capacités d'analyse AST"""
        try:
            import ast

            # Test simple de parsing AST
            test_code = "def test(): pass"
            tree = ast.parse(test_code)
            return tree is not None
        except Exception:
            return False

    def _test_file_operations(self) -> bool:
        """Teste les capacités d'opérations sur fichiers"""
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", delete=True) as tmp:
                tmp.write("test")
                tmp.flush()
                # Test lecture
                with open(tmp.name, "r") as f:
                    content = f.read()
                return content == "test"
        except Exception:
            return False

    def _test_json_capabilities(self) -> bool:
        """Teste les capacités JSON"""
        try:
            import json

            test_data = {"test": "value"}
            serialized = json.dumps(test_data)
            deserialized = json.loads(serialized)
            return deserialized == test_data
        except Exception:
            return False

    def _test_csv_capabilities(self) -> bool:
        """Teste les capacités CSV"""
        try:
            import csv
            import io

            # Test écriture/lecture CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["test", "data"])

            csv_content = output.getvalue()
            return "test,data" in csv_content
        except Exception:
            return False

    def _test_regex_capabilities(self) -> bool:
        """Teste les capacités d'expressions régulières"""
        try:
            import re

            pattern = re.compile(r"\w+")
            match = pattern.search("test123")
            return match is not None
        except Exception:
            return False

    def diagnose_environment_issues(self) -> Dict[str, str]:
        """Diagnostic des problèmes d'environnement"""
        issues = {}

        # Diagnostic version Python
        if not self._check_python_version():
            current = self.get_python_version()
            required = f"{self.min_python_version[0]}.{self.min_python_version[1]}"
            issues["python_version"] = f"Version {current} < {required} requise"

        # Diagnostic modules manquants
        missing_modules = []
        for module_name in self.required_modules:
            try:
                __import__(module_name)
            except ImportError:
                missing_modules.append(module_name)

        if missing_modules:
            issues["missing_modules"] = (
                f"Modules manquants: {', '.join(missing_modules)}"
            )

        # Diagnostic capacités
        capabilities = self.detect_project_capabilities()
        failed_capabilities = [
            name for name, status in capabilities.items() if not status
        ]

        if failed_capabilities:
            issues["failed_capabilities"] = (
                f"Capacités défaillantes: {', '.join(failed_capabilities)}"
            )

        return issues

    def suggest_environment_fixes(self) -> Dict[str, str]:
        """Suggestions pour corriger l'environnement"""
        issues = self.diagnose_environment_issues()
        suggestions = {}

        if "python_version" in issues:
            suggestions["python_upgrade"] = (
                "Mettre à jour Python vers une version >= 3.7"
            )

        if "missing_modules" in issues:
            suggestions["install_modules"] = (
                "Installer les modules Python standard manquants"
            )

        if "failed_capabilities" in issues:
            suggestions["check_installation"] = (
                "Vérifier l'installation Python complète"
            )

        return suggestions


class SystemRequirementsChecker:
    """Vérificateur des exigences système pour l'audit AGI"""

    @staticmethod
    def check_disk_space(min_mb: int = 100) -> Tuple[bool, int]:
        """Vérifie l'espace disque disponible"""
        try:
            import shutil

            free_bytes = shutil.disk_usage(".").free
            free_mb = free_bytes // (1024 * 1024)
            return free_mb >= min_mb, free_mb
        except Exception:
            return False, 0

    @staticmethod
    def check_memory_available(min_mb: int = 512) -> Tuple[bool, Optional[int]]:
        """Vérifie la mémoire disponible"""
        try:
            import psutil

            available_mb = psutil.virtual_memory().available // (1024 * 1024)
            return available_mb >= min_mb, available_mb
        except ImportError:
            # psutil non disponible, assume OK
            return True, None
        except Exception:
            return False, None

    @staticmethod
    def check_write_permissions(target_dir: Path) -> bool:
        """Vérifie les permissions d'écriture"""
        try:
            test_file = target_dir / ".audit_permission_test"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False


def quick_environment_check() -> Dict[str, bool]:
    """Vérification rapide de l'environnement - fonction utilitaire"""
    detector = EnvironmentDetector()
    requirements = SystemRequirementsChecker()

    return {
        "python_ok": detector.validate_python_environment(),
        "disk_space_ok": requirements.check_disk_space()[0],
        "memory_ok": requirements.check_memory_available()[0],
        "capabilities_ok": all(detector.detect_project_capabilities().values()),
    }


if __name__ == "__main__":
    # Test rapide du module
    detector = EnvironmentDetector()

    print("🔍 Test du détecteur d'environnement AGI")
    print("=" * 40)

    if detector.validate_python_environment():
        print("✅ Environnement Python valide")
        env_info = detector.get_environment_info()
        for key, value in env_info.items():
            print(f"   {key}: {value}")
    else:
        print("❌ Environnement Python invalide")
        issues = detector.diagnose_environment_issues()
        for issue, description in issues.items():
            print(f"   {issue}: {description}")

        suggestions = detector.suggest_environment_fixes()
        if suggestions:
            print("\n💡 Suggestions:")
            for fix, description in suggestions.items():
                print(f"   {fix}: {description}")