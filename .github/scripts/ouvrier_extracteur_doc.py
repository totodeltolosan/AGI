#!/usr/bin/env python3
"""
Handler Ouvrier Extracteur Documentation
Extrait les faits sur la documentation depuis une liste de fichiers
"""

import json
import argparse
import sys
import os
from pathlib import Path

def extract_documentation_facts(file_list):
    """Extrait les faits de documentation depuis une liste de fichiers."""
    facts = {
        "total_files": 0,
        "doc_files": 0,
        "readme_files": 0,
        "code_comments": 0,
        "missing_docs": [],
        "well_documented": []
    }

    try:
        for file_path in file_list:
            if not os.path.exists(file_path):
                continue

            facts["total_files"] += 1
            file_lower = file_path.lower()

            # Identifier les fichiers de documentation
            if any(ext in file_lower for ext in ['.md', '.rst', '.txt', 'readme']):
                facts["doc_files"] += 1
                if 'readme' in file_lower:
                    facts["readme_files"] += 1

            # Analyser les fichiers Python pour les commentaires
            elif file_path.endswith('.py'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')

                    comment_lines = sum(1 for line in lines if line.strip().startswith('#') or '"""' in line or "'''" in line)
                    total_lines = len(lines)

                    if total_lines > 0:
                        comment_ratio = comment_lines / total_lines
                        if comment_ratio > 0.1:  # Plus de 10% de commentaires
                            facts["well_documented"].append({
                                "file": file_path,
                                "comment_ratio": round(comment_ratio, 2)
                            })
                        else:
                            facts["missing_docs"].append(file_path)

                    facts["code_comments"] += comment_lines

                except Exception as e:
                    print(f"Erreur lecture {file_path}: {e}")

    except Exception as e:
        print(f"Erreur extraction documentation: {e}")
        return None

    return facts

def main():
    parser = argparse.ArgumentParser(description="Extracteur de faits documentation")
    parser.add_argument("--liste-fichiers", required=True,
                       help="Fichier JSON contenant la liste des fichiers")

    args = parser.parse_args()

    try:
        # Charger la liste des fichiers
        with open(args.liste_fichiers, 'r') as f:
            file_data = json.load(f)

        file_list = file_data.get('files', [])
        if not file_list:
            print("Aucun fichier trouvé dans la liste")
            sys.exit(1)

        # Extraire les faits de documentation
        facts = extract_documentation_facts(file_list)
        if facts is None:
            sys.exit(1)

        # Sauvegarder les résultats
        output_file = "faits-documentation.json"
        with open(output_file, 'w') as f:
            json.dump(facts, f, indent=2)

        print(f"Faits documentation extraits: {facts['total_files']} fichiers analysés")
        print(f"Documentation trouvée: {facts['doc_files']} fichiers")
        print(f"Fichiers bien documentés: {len(facts['well_documented'])}")
        print(f"Artefact sauvé: {output_file}")

    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
