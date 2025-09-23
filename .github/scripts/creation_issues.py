#!/usr/bin/env python3
"""
🎫 Contremaître Création Issues (Niveau 3)
==========================================

Orchestre la création d'issues GitHub à partir des violations critiques.
Pipeline : Collecteur → Validation → Rédacteur → Validation → Poster GitHub

Auteur: Gouvernance AGI
Version: 1.0.0
"""

import argparse
import json
import sys
import subprocess
import os
from pathlib import Path


def appeler_workflow(workflow_path: str, inputs: dict) -> bool:
    """
    Appelle un workflow GitHub Actions en utilisant workflow_dispatch.
    
    Args:
        workflow_path: Chemin vers le workflow
        inputs: Dictionnaire des inputs à passer
        
    Returns:
        True si succès, False sinon
    """
    try:
        # Construction de la commande gh workflow run
        cmd = ["gh", "workflow", "run", workflow_path]
        
        # Ajout des inputs
        for key, value in inputs.items():
            cmd.extend(["-f", f"{key}={value}"])
        
        # Exécution de la commande
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Workflow {workflow_path} lancé avec succès")
            return True
        else:
            print(f"❌ Erreur lors du lancement de {workflow_path}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception lors de l'appel de {workflow_path}: {e}")
        return False


def orchestrer_creation_issues(noms_artefacts: list) -> bool:
    """
    Orchestre la création d'issues à partir des rapports d'audit.
    
    Args:
        noms_artefacts: Liste des noms d'artefacts de rapport à analyser
        
    Returns:
        True si succès complet, False sinon
    """
    print("🎫 === CONTREMAÎTRE CRÉATION ISSUES ===")
    print(f"Artefacts à analyser: {noms_artefacts}")
    print()
    
    try:
        # Étape 1: Collecteur de violations critiques (Niveau 4)
        print("📥 Étape 1: Collecte des violations critiques...")
        collecteur_inputs = {
            "noms_artefacts": json.dumps(noms_artefacts)
        }
        
        if not appeler_workflow("04-01-issues-collecteur.yml", collecteur_inputs):
            return False
        
        # Étape 2: Validation Collecteur (Niveau 5)
        print("✅ Étape 2: Validation des violations collectées...")
        validation_collecteur_inputs = {
            "violations-critiques": "violations-critiques"
        }
        
        if not appeler_workflow("05-01-issues-valid-collecteur.yml", validation_collecteur_inputs):
            return False
        
        # Étape 3: Rédacteur d'issue (Niveau 4)
        print("✍️ Étape 3: Rédaction du contenu de l'issue...")
        redacteur_inputs = {
            "violations-critiques": "violations-critiques"
        }
        
        if not appeler_workflow("04-02-issues-redacteur.yml", redacteur_inputs):
            return False
        
        # Étape 4: Validation Rédacteur (Niveau 5)
        print("✅ Étape 4: Validation du contenu rédigé...")
        validation_redacteur_inputs = {
            "titre_issue": "titre_issue",
            "corps_issue": "corps_issue"
        }
        
        if not appeler_workflow("05-02-issues-valid-redacteur.yml", validation_redacteur_inputs):
            return False
        
        # Étape 5: Poster l'issue sur GitHub (Niveau 6)
        print("📝 Étape 5: Publication de l'issue sur GitHub...")
        poster_inputs = {
            "titre": "titre_issue",
            "corps": "corps_issue",
            "labels": json.dumps(["gouvernance", "violation-critique", "audit"]),
            "assignes": json.dumps([])
        }
        
        if not appeler_workflow("06-04-github-poster.yml", poster_inputs):
            return False
        
        print("🎉 === CRÉATION ISSUES TERMINÉE AVEC SUCCÈS ===")
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique lors de l'orchestration: {e}")
        return False


def main():
    """Fonction principale du Contremaître."""
    parser = argparse.ArgumentParser(
        description="🎫 Contremaître Création Issues",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--artefacts',
        required=True,
        help='Liste des noms d\'artefacts de rapport au format JSON'
    )
    
    args = parser.parse_args()
    
    try:
        noms_artefacts = json.loads(args.artefacts)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON pour les artefacts: {e}")
        sys.exit(1)
    
    # Orchestration de la création d'issues
    success = orchestrer_creation_issues(noms_artefacts)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
