#!/usr/bin/env python3
"""
Analyse des Interconnexions - Écosystème EVE
============================================

Analyse les projets pour identifier les points de fusion avec AGI
"""

import os
import re
from pathlib import Path

def analyze_project_connections():
    """Analyse les connexions entre projets"""
    
    projects = [
        "/home/toni/Documents/gaia",
        "/home/toni/Documents/EVE", 
        "/home/toni/Documents/ALMA",
        "/home/toni/Documents/Monde",
        "/home/toni/Documents/EVE GENESIS",
        "/home/toni/Documents/Test Eve",
        "/home/toni/Documents/Projet simulateur",
        "/home/toni/Documents/ALMA_Space_Cerveau_Demo"
    ]
    
    print("🔗 ANALYSE INTERCONNEXIONS ÉCOSYSTÈME EVE")
    print("=========================================")
    
    all_imports = {}
    all_classes = {}
    all_functions = {}
    
    for project_path in projects:
        if os.path.exists(project_path):
            project_name = os.path.basename(project_path)
            print(f"\n📁 PROJET: {project_name}")
            
            # Analyser les fichiers Python
            python_files = list(Path(project_path).rglob("*.py"))
            print(f"   Fichiers Python: {len(python_files)}")
            
            imports = set()
            classes = set()
            functions = set()
            
            for py_file in python_files[:10]:  # Limiter pour performance
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extraire imports
                    import_matches = re.findall(r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content)
                    imports.update(import_matches)
                    
                    # Extraire classes
                    class_matches = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                    classes.update(class_matches)
                    
                    # Extraire fonctions principales
                    func_matches = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                    functions.update(func_matches)
                    
                except Exception as e:
                    continue
            
            all_imports[project_name] = imports
            all_classes[project_name] = classes
            all_functions[project_name] = functions
            
            print(f"   Imports uniques: {len(imports)}")
            print(f"   Classes: {len(classes)}")
            print(f"   Fonctions: {len(functions)}")
            
            # Afficher quelques éléments clés
            if classes:
                print(f"   Classes principales: {list(classes)[:3]}")
            if functions:
                print(f"   Fonctions principales: {list(functions)[:3]}")
    
    # Analyser les recoupements
    print("\n🔍 ANALYSE DES RECOUPEMENTS")
    print("---------------------------")
    
    all_projects = list(all_imports.keys())
    
    for i, proj1 in enumerate(all_projects):
        for proj2 in all_projects[i+1:]:
            if proj1 in all_imports and proj2 in all_imports:
                common_imports = all_imports[proj1] & all_imports[proj2]
                if common_imports:
                    print(f"\n🔗 {proj1} ↔ {proj2}")
                    print(f"   Imports communs: {len(common_imports)}")
                    if len(common_imports) > 5:
                        print(f"   Technologies partagées: {list(common_imports)[:5]}")

if __name__ == "__main__":
    analyze_project_connections()
