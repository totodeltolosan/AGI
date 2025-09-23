#!/usr/bin/env python3
"""
🛡️ Contremaître Audit Sécurité (Niveau 3)
==========================================

Orchestre l'audit complet de la Division "Loi Sécurité".
Pipeline : Scanner → Chercheur → Validation → Trieur → Validation → Formateur Markdown

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


def orchestrer_audit_securite(regles_securite: list) -> bool:
    """
    Orchestre l'audit complet de la division Loi Sécurité.
    
    Args:
        regles_securite: Liste des règles de sécurité à appliquer
        
    Returns:
        True si succès complet, False sinon
    """
    print("🛡️ === CONTREMAÎTRE AUDIT SÉCURITÉ ===")
    print(f"Règles de sécurité: {len(regles_securite)} règle(s)")
    print()
    
    try:
        # Étape 1: Scanner les fichiers Python (Niveau 6)
        print("🔍 Étape 1: Scan des fichiers Python...")
        scanner_inputs = {
            "pattern": "*.py",
            "chemin_racine": ".",
            "exclusions": json.dumps([".git/*", "__pycache__/*", "*.pyc"])
        }
        
        if not appeler_workflow("06-01-scanner-fichiers.yml", scanner_inputs):
            return False
        
        # Attendre la fin du scan (simulation)
        print("⏳ Attente de la fin du scan...")
        
        # Étape 2: Chercheur de violations (Niveau 4)
        print("🔍 Étape 2: Recherche des violations de sécurité...")
        chercheur_inputs = {
            "liste-fichiers": "liste-fichiers",
            "regles_securite": json.dumps(regles_securite)
        }
        
        if not appeler_workflow("04-01-securite-chercheur.yml", chercheur_inputs):
            return False
        
        # Étape 3: Validation Chercheur (Niveau 5)
        print("✅ Étape 3: Validation des violations trouvées...")
        validation_chercheur_inputs = {
            "violations-brutes": "violations-brutes"
        }
        
        if not appeler_workflow("05-01-securite-valid-chercheur.yml", validation_chercheur_inputs):
            return False
        
        # Étape 4: Trieur par sévérité (Niveau 4)
        print("🗂️ Étape 4: Tri des violations par sévérité...")
        trieur_inputs = {
            "violations-brutes": "violations-brutes"
        }
        
        if not appeler_workflow("04-02-securite-trieur.yml", trieur_inputs):
            return False
        
        # Étape 5: Validation Trieur (Niveau 5)
        print("✅ Étape 5: Validation du tri...")
        validation_trieur_inputs = {
            "violations-triees": "violations-triees"
        }
        
        if not appeler_workflow("05-02-securite-valid-trieur.yml", validation_trieur_inputs):
            return False
        
        # Étape 6: Formateur Markdown final (Niveau 7)
        print("📝 Étape 6: Génération du rapport de sécurité...")
        formateur_inputs = {
            "artefact_entree_json": "violations-triees",
            "template_markdown": "## 🛡️ Rapport de Sécurité\\n\\n### Violations par Sévérité\\n"
        }
        
        if not appeler_workflow("07-02-formateur-markdown.yml", formateur_inputs):
            return False
        
        print("🎉 === AUDIT SÉCURITÉ TERMINÉ AVEC SUCCÈS ===")
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique lors de l'orchestration: {e}")
        return False


def main():
    """Fonction principale du Contremaître."""
    parser = argparse.ArgumentParser(
        description="🛡️ Contremaître Audit Sécurité",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--regles',
        required=True,
        help='Règles de sécurité au format JSON'
    )
    
    args = parser.parse_args()
    
    try:
        regles_securite = json.loads(args.regles)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON pour les règles: {e}")
        sys.exit(1)
    
    # Orchestration de l'audit
    success = orchestrer_audit_securite(regles_securite)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
