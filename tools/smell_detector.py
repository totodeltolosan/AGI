#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Smell Detector (Le Débroussailleur) - v2.0
===============================================
Rôle Constitutionnel :
- Détecter les "mauvaises odeurs" architecturales et logiques.
- Signaler les violations de complexité, de longueur et de documentation.
- Agit comme un conseiller qualité non-bloquant.
"""
import json
import sys
import ast
from pathlib import Path
from datetime import datetime, timezone
import subprocess
from radon.visitors import ComplexityVisitor
from radon.metrics import mi_visit

def get_tracked_python_files(root_path: Path):
    """Utilise 'git ls-files' pour lister les fichiers Python du projet."""
    try:
        command = ["git", "ls-files", "*.py"]
        result = subprocess.run(command, cwd=root_path, capture_output=True, text=True, check=True)
        return [root_path / f for f in result.stdout.strip().splitlines()]
    except Exception:
        return []

def analyze_file(file_path: Path, root_path: Path):
    """Analyse un seul fichier pour plusieurs types de "code smells"."""
    smells = []
    try:
        with file_path.open('r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)

        # 1. Analyse de complexité et de longueur avec Radon
        visitor = ComplexityVisitor.from_code(content)
        for func in visitor.functions:
            if func.complexity > 10:
                smells.append({
                    "file_path": str(file_path.relative_to(root_path)),
                    "line_number": func.lineno,
                    "smell_type": "COMPLEXITE_ELEVEE",
                    "message": f"La fonction '{func.name}' a une complexité de {func.complexity} (>10).",
                    "suggestion": "Refactoriser en fonctions plus petites."
                })
            if func.endline - func.lineno > 50:
                 smells.append({
                    "file_path": str(file_path.relative_to(root_path)),
                    "line_number": func.lineno,
                    "smell_type": "FONCTION_TROP_LONGUE",
                    "message": f"La fonction '{func.name}' fait {func.endline - func.lineno} lignes (>50).",
                    "suggestion": "Extraire la logique dans des fonctions filles."
                })

        # 2. Analyse des docstrings manquantes avec AST
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('_'):
                    continue # Ignore les fonctions privées
                if not ast.get_docstring(node):
                    name = getattr(node, 'name', 'Module')
                    smells.append({
                        "file_path": str(file_path.relative_to(root_path)),
                        "line_number": node.lineno,
                        "smell_type": "DOCSTRING_MANQUANTE",
                        "message": f"Docstring manquante pour la {'fonction' if isinstance(node, ast.FunctionDef) else 'classe'} '{name}'.",
                        "suggestion": "Ajouter une docstring expliquant le rôle de cet élément."
                    })
    except Exception as e:
        # Ignore les fichiers avec des erreurs de syntaxe, ce n'est pas sa mission
        pass
    return smells

def main():
    """Point d'entrée du script."""
    root_path = Path('.')
    output_file = Path("code_smells_report.json")
    
    project_files = get_tracked_python_files(root_path)
    all_smells = []

    print(f"🕵️  Analyse de {len(project_files)} fichiers pour les 'Code Smells'...")

    for file in project_files:
        all_smells.extend(analyze_file(file, root_path))

    report = {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_files_scanned": len(project_files),
            "total_smells_found": len(all_smells)
        },
        "smells": all_smells
    }

    with output_file.open('w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)

    print(f"✅ Rapport de 'Code Smells' sauvegardé dans '{output_file}'.")
    print(f"📊 {len(all_smells)} 'mauvaises odeurs' détectées.")

if __name__ == "__main__":
    main()
