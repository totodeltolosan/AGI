# -*- coding: utf-8 -*-
"""
analyseur_code.py (v1.4.1 - Correction)

Corrige l'oubli de la clé 'chemin_racine' dans le graphe de connaissance.
"""

import os
import ast
from pathlib import Path
from . import modele_langage

try:
    analyseur_nlp = modele_langage.ModeleAnalyseCode()
except Exception as e:
    print(f"[ERREUR CRITIQUE] Impossible d'instancier le modèle NLP : {e}")
    analyseur_nlp = None

DOSSIERS_A_EXCLURE = {'__pycache__', 'venv', '.git', '.vscode', 'introspection', 'assets'}
FICHIERS_A_EXCLURE = {'inspecteur_cerveau.py'}

def scanner_projet(chemin_racine: str) -> list[str]:
    fichiers_py_trouves = []
    for racine, dossiers, fichiers in os.walk(chemin_racine, topdown=True):
        dossiers[:] = [d for d in dossiers if d not in DOSSIERS_A_EXCLURE]
        for nom_fichier in fichiers:
            if nom_fichier.endswith('.py') and nom_fichier not in FICHIERS_A_EXCLURE:
                fichiers_py_trouves.append(str(Path(racine) / nom_fichier))
    return sorted(fichiers_py_trouves)

def analyser_fichier(chemin_fichier: str, tous_les_fichiers_du_projet: list) -> dict:
    print(f"[Analyseur] Analyse de : {Path(chemin_fichier).name}")
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            contenu = f.read()

        arbre = ast.parse(contenu)
        docstring = ast.get_docstring(arbre) or "Aucun docstring trouvé."

        imports_bruts = []
        for node in ast.walk(arbre):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports_bruts.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports_bruts.append(node.module.split('.')[0])

        dependances_internes = []
        dependances_externes = []
        noms_fichiers_projet = {Path(f).stem for f in tous_les_fichiers_du_projet}

        for imp in sorted(list(set(imports_bruts))):
            if imp in noms_fichiers_projet:
                dependances_internes.append(imp)
            else:
                dependances_externes.append(imp)

        fonctions = [node.name for node in ast.walk(arbre) if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(arbre) if isinstance(node, ast.ClassDef)]

        resume_ia = "Module NLP non chargé."
        if analyseur_nlp:
            resume_ia = analyseur_nlp.resumer_code(contenu)

        return {
            "chemin": chemin_fichier,
            "nom": Path(chemin_fichier).stem,
            "taille_lignes": len(contenu.splitlines()),
            "role_docstring": docstring.strip(),
            "resume_ia": resume_ia,
            "classes_definies": classes,
            "fonctions_definies": fonctions,
            "dependances_internes": dependances_internes,
            "dependances_externes": dependances_externes,
            "erreur": None
        }
    except Exception as e:
        return {"chemin": chemin_fichier, "nom": Path(chemin_fichier).stem, "erreur": f"Impossible d'analyser le fichier. Erreur: {e}"}

def analyser_tout_le_projet(chemin_racine: str) -> dict:
    """Construit le graphe de connaissance complet."""
    print("[Analyseur] Lancement de l'analyse complète du projet...")
    fichiers_a_analyser = scanner_projet(chemin_racine)

    # --- DÉBUT DE LA CORRECTION ---
    graphe_connaissance = {
        "chemin_racine": chemin_racine, # On ajoute la clé manquante ici
        "fichiers": []
    }
    # --- FIN DE LA CORRECTION ---

    for fichier in fichiers_a_analyser:
        analyse = analyser_fichier(fichier, fichiers_a_analyser)
        graphe_connaissance["fichiers"].append(analyse)

    print("[Analyseur] Graphe de connaissance du projet construit.")
    return graphe_connaissance
