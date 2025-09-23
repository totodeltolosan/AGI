#!/usr/bin/env python3
"""
📚 Contremaître Audit Documentation (Niveau 3)
===============================================

Orchestre l'audit complet de la Division "Loi Documentation".
Pipeline : Scanner → Extracteur → Validation → Calculateur → Validation → Formateur

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


def orchestrer_audit_documentation(seuils_documentation: dict) -> bool:
    """
    Orchestre l'audit complet de la division Loi Documentation.
    
    Args:
        seuils_documentation: Seuils de couverture documentation
        
    Returns:
        True si succès complet, False sinon
    """
    print("📚 === CONTREMAÎTRE AUDIT DOCUMENTATION ===")
    print(f"Seuils de couverture: {seuils_documentation}")
    print()
    
    try:
        # Étape 1: Scanner les fichiers Python (Niveau 6)
        print("🔍 Étape 1: Scan des fichiers Python...")
        scanner_inputs = {
            "pattern": "*.py",
            "chemin_racine": ".",
            "exclusions": json.dumps([".git/*", "__pycache__/*", "*.pyc", "*/tests/*"])
        }
        
        if not appeler_workflow("06-01-scanner-fichiers.yml", scanner_inputs):
            return False
        
        # Attendre la fin du scan (simulation)
        print("⏳ Attente de la fin du scan...")
        
        # Étape 2: Extracteur de faits documentation (Niveau 4)
        print("🔍 Étape 2: Extraction des faits de documentation...")
        extracteur_inputs = {
            "liste-fichiers": "liste-fichiers"
        }
        
        if not appeler_workflow("04-01-doc-extracteur.yml", extracteur_inputs):
            return False
        
        # Étape 3: Validation Extracteur (Niveau 5)
        print("✅ Étape 3: Validation des faits extraits...")
        validation_extracteur_inputs = {
            "faits-documentation": "faits-documentation"
        }
        
        if not appeler_workflow("05-01-doc-valid-extracteur.yml", validation_extracteur_inputs):
            return False
        
        # Étape 4: Calculateur de statistiques (Niveau 4)
        print("📊 Étape 4: Calcul des statistiques de couverture...")
        calculateur_inputs = {
            "faits-documentation": "faits-documentation",
            "seuils_documentation": json.dumps(seuils_documentation)
        }
        
        if not appeler_workflow("04-02-doc-calculateur.yml", calculateur_inputs):
            return False
        
        # Étape 5: Validation Calculateur (Niveau 5)
        print("✅ Étape 5: Validation des statistiques...")
        validation_calculateur_inputs = {
            "statistiques-documentation": "statistiques-documentation"
        }
        
        if not appeler_workflow("05-02-doc-valid-calculateur.yml", validation_calculateur_inputs):
            return False
        
        # Étape 6: Formateur Markdown final (Niveau 7)
        print("📝 Étape 6: Génération du rapport de documentation...")
        formateur_inputs = {
            "artefact_entree_json": "statistiques-documentation",
            "template_markdown": "## 📚 Rapport de Documentation\\n\\n### Couverture par Type\\n"
        }
        
        if not appeler_workflow("07-02-formateur-markdown.yml", formateur_inputs):
            return False
        
        print("🎉 === AUDIT DOCUMENTATION TERMINÉ AVEC SUCCÈS ===")
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique lors de l'orchestration: {e}")
        return False


def main():
    """Fonction principale du Contremaître."""
    parser = argparse.ArgumentParser(
        description="📚 Contremaître Audit Documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--seuils',
        required=True,
        help='Seuils de couverture documentation au format JSON'
    )
    parser.add_argument(
        "--audit-id",
        required=False,
        default="default",
        help="Identifiant unique de l\'audit"
    )
    
    args = parser.parse_args()
    
    try:
        seuils_documentation = json.loads(args.seuils)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON pour les seuils: {e}")
        sys.exit(1)
    
    # Orchestration de l'audit
    success = orchestrer_audit_documentation(seuils_documentation)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
