#!/usr/bin/env python3
"""
Détecteur de Projet AGI - Système d'Audit de Conformité
Responsabilité unique : Détection et validation de la structure projet AGI
Respecte strictement la directive des 200 lignes
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
import re


class ProjectDetector:
    """Détecteur de structure et caractéristiques projet AGI"""

    def __init__(self):
        self.agi_markers = {
            "constitution": ["AGI.md", "agi.md"],
            "documentation": ["AGI2.md", "AGI3.md", "AGI4.md", "AGI5.md", "AGIHELP.md"],
            "generator": ["tools/project_initializer", "project_initializer"],
            "compliance": ["tools/compliance_checker", "compliance_checker"],
        }

    def detect_agi_project(self, target_dir: Path) -> Dict:
        """Détecte si le répertoire contient un projet AGI valide"""
        detection_results = {
            "valid": False,
            "root_path": None,
            "agi_files": [],
            "project_type": "unknown",
            "structure_score": 0,
        }

        # Recherche de la racine du projet AGI
        project_root = self._find_project_root(target_dir)
        if not project_root:
            return detection_results

        detection_results["root_path"] = project_root

        # Analyse des fichiers AGI présents
        agi_files = self._scan_agi_files(project_root)
        detection_results["agi_files"] = agi_files

        # Détermination du type de projet
        project_type = self._determine_project_type(agi_files, project_root)
        detection_results["project_type"] = project_type

        # Calcul du score de structure
        structure_score = self._calculate_structure_score(agi_files, project_root)
        detection_results["structure_score"] = structure_score

        # Validation finale
        detection_results["valid"] = (
            structure_score >= 3
        )  # Au moins 3 éléments AGI détectés

        return detection_results

    def analyze_project_health(self, project_root: Path) -> Dict:
        """Analyse la santé générale du projet AGI"""
        health_metrics = {
            "documentation_completeness": 0,
            "generator_presence": False,
            "tools_structure": False,
            "constitution_present": False,
            "estimated_conformity": "unknown",
        }

        # Vérification de la documentation
        doc_files = self._find_documentation_files(project_root)
        health_metrics["documentation_completeness"] = len(doc_files)

        # Vérification du générateur
        generator_path = project_root / "tools" / "project_initializer"
        health_metrics["generator_presence"] = generator_path.exists()

        # Vérification de la structure des outils
        tools_path = project_root / "tools"
        health_metrics["tools_structure"] = tools_path.exists()

        # Vérification de la constitution
        constitution_files = self._find_constitution_files(project_root)
        health_metrics["constitution_present"] = len(constitution_files) > 0

        # Estimation de la conformité
        health_metrics["estimated_conformity"] = self._estimate_conformity(
            health_metrics
        )

        return health_metrics

    def _find_project_root(self, start_path: Path) -> Optional[Path]:
        """Trouve la racine du projet AGI en remontant l'arborescence"""
        current_path = start_path.resolve()

        # Recherche dans le répertoire courant et parents
        search_paths = [current_path] + list(current_path.parents)

        for path in search_paths:
            # Vérification des marqueurs AGI
            if self._has_agi_markers(path):
                return path

        return None

    def _has_agi_markers(self, path: Path) -> bool:
        """Vérifie si un répertoire contient des marqueurs AGI"""
        # Recherche de AGI.md (marqueur principal)
        for constitution_file in self.agi_markers["constitution"]:
            if (path / constitution_file).exists():
                return True

        # Recherche de la structure tools/project_initializer
        for generator_path in self.agi_markers["generator"]:
            if (path / generator_path).exists():
                return True

        return False

    def _scan_agi_files(self, project_root: Path) -> List[str]:
        """Scanne tous les fichiers AGI dans le projet"""
        agi_files = []

        # Scan de tous les types de fichiers AGI
        for category, file_patterns in self.agi_markers.items():
            for pattern in file_patterns:
                file_path = project_root / pattern
                if file_path.exists():
                    agi_files.append(str(file_path.relative_to(project_root)))

        # Recherche de fichiers AGI additionnels
        additional_files = self._find_additional_agi_files(project_root)
        agi_files.extend(additional_files)

        return sorted(list(set(agi_files)))  # Suppression des doublons et tri

    def _find_additional_agi_files(self, project_root: Path) -> List[str]:
        """Trouve des fichiers AGI additionnels par pattern matching"""
        additional_files = []

        # Patterns de recherche
        agi_patterns = [
            r"AGI\d*\.md",
            r"agi\d*\.md",
            r".*agi.*\.py",
            r".*compliance.*\.py",
            r".*audit.*\.py",
        ]

        # Recherche récursive avec patterns
        for py_file in project_root.rglob("*.py"):
            relative_path = str(py_file.relative_to(project_root))
            for pattern in agi_patterns:
                if re.search(pattern, py_file.name, re.IGNORECASE):
                    additional_files.append(relative_path)
                    break

        # Recherche de fichiers markdown AGI
        for md_file in project_root.rglob("*.md"):
            relative_path = str(md_file.relative_to(project_root))
            if re.search(r"AGI\d*\.md", md_file.name, re.IGNORECASE):
                additional_files.append(relative_path)

        return additional_files

    def _determine_project_type(self, agi_files: List[str], project_root: Path) -> str:
        """Détermine le type de projet AGI basé sur les fichiers présents"""

        # Classification par présence de composants
        has_constitution = any("AGI.md" in f for f in agi_files)
        has_generator = any("project_initializer" in f for f in agi_files)
        has_compliance = any("compliance" in f for f in agi_files)
        has_docs = any(re.search(r"AGI[2-9]\.md", f) for f in agi_files)

        if has_constitution and has_generator and has_compliance:
            return "full_agi_project"
        elif has_constitution and has_generator:
            return "agi_generator_project"
        elif has_constitution and has_docs:
            return "agi_documentation_project"
        elif has_constitution:
            return "agi_basic_project"
        elif has_generator:
            return "generator_only_project"
        else:
            return "agi_fragment"

    def _calculate_structure_score(
        self, agi_files: List[str], project_root: Path
    ) -> int:
        """Calcule un score de structure du projet AGI"""
        score = 0

        # Points pour les composants essentiels
        if any("AGI.md" in f for f in agi_files):
            score += 3  # Constitution = très important

        if any("project_initializer" in f for f in agi_files):
            score += 2  # Générateur = important

        if any("compliance" in f for f in agi_files):
            score += 2  # Outils de conformité = important

        # Points pour la documentation
        doc_count = len([f for f in agi_files if re.search(r"AGI[2-9]\.md", f)])
        score += min(doc_count, 3)  # Max 3 points pour la doc

        # Points pour la structure de répertoires
        if (project_root / "tools").exists():
            score += 1

        return score

    def _find_documentation_files(self, project_root: Path) -> List[str]:
        """Trouve tous les fichiers de documentation AGI"""
        doc_files = []

        for doc_pattern in self.agi_markers["documentation"]:
            doc_file = project_root / doc_pattern
            if doc_file.exists():
                doc_files.append(doc_pattern)

        return doc_files

    def _find_constitution_files(self, project_root: Path) -> List[str]:
        """Trouve les fichiers de constitution AGI"""
        constitution_files = []

        for const_pattern in self.agi_markers["constitution"]:
            const_file = project_root / const_pattern
            if const_file.exists():
                constitution_files.append(const_pattern)

        return constitution_files

    def _estimate_conformity(self, health_metrics: Dict) -> str:
        """Estime le niveau de conformité du projet"""

        # Calcul d'un score de santé
        health_score = 0

        if health_metrics["constitution_present"]:
            health_score += 3
        if health_metrics["generator_presence"]:
            health_score += 2
        if health_metrics["tools_structure"]:
            health_score += 1

        health_score += min(health_metrics["documentation_completeness"], 2)

        # Classification par score
        if health_score >= 7:
            return "high_conformity_expected"
        elif health_score >= 4:
            return "medium_conformity_expected"
        elif health_score >= 2:
            return "low_conformity_expected"
        else:
            return "conformity_unknown"


def quick_project_detection(target_dir: Path) -> bool:
    """Détection rapide - fonction utilitaire"""
    detector = ProjectDetector()
    result = detector.detect_agi_project(target_dir)
    return result["valid"]


def get_project_summary(target_dir: Path) -> Dict:
    """Résumé rapide du projet - fonction utilitaire"""
    detector = ProjectDetector()
    detection = detector.detect_agi_project(target_dir)

    if detection["valid"]:
        health = detector.analyze_project_health(detection["root_path"])
        return {
            "valid": True,
            "type": detection["project_type"],
            "score": detection["structure_score"],
            "health": health["estimated_conformity"],
        }
    else:
        return {"valid": False}


if __name__ == "__main__":
    # Test du détecteur de projet
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    print("🔍 Test du détecteur de projet AGI")
    print("=" * 40)

    detector = ProjectDetector()
    result = detector.detect_agi_project(target)

    print(f"Projet valide : {result['valid']}")
    print(f"Type : {result['project_type']}")
    print(f"Score structure : {result['structure_score']}")
    print(f"Fichiers AGI trouvés : {len(result['agi_files'])}")

    for agi_file in result["agi_files"][:5]:  # Affiche max 5 fichiers
        print(f"  - {agi_file}")
