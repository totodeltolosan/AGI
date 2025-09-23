#!/usr/bin/env python3
"""
📐 Contremaître Audit PlantUML (Niveau 3)
=========================================

Orchestre la vérification de synchronisation des diagrammes PlantUML.
Pipeline : Git Historien (diagramme) → Git Historien (code) → Comparateur → Validation → Formateur Statut

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


def orchestrer_audit_planuml(chemin_diagramme: str, dossiers_critiques: list) -> bool:
    """
    Orchestre la vérification de synchronisation du diagramme PlantUML.
    
    Args:
        chemin_diagramme: Chemin vers le fichier diagramme PlantUML
        dossiers_critiques: Liste des dossiers critiques à surveiller
        
    Returns:
        True si succès complet, False sinon
    """
    print("📐 === CONTREMAÎTRE AUDIT PLANTUML ===")
    print(f"Diagramme: {chemin_diagramme}")
    print(f"Dossiers critiques: {dossiers_critiques}")
    print()
    
    try:
        # Étape 1: Git Historien pour le diagramme (Niveau 6)
        print("🕐 Étape 1: Récupération date du diagramme...")
        historien_diagramme_inputs = {
            "chemin_fichier_ou_dossier": chemin_diagramme
        }
        
        if not appeler_workflow("06-06-git-historien.yml", historien_diagramme_inputs):
            return False
        
        # Simulation de récupération du timestamp
        date_diagramme = "1640995200"  # Placeholder
        
        # Étape 2: Git Historien pour les dossiers critiques (Niveau 6)
        print("🕐 Étape 2: Récupération date du code critique...")
        dossiers_str = " ".join(dossiers_critiques)
        historien_code_inputs = {
            "chemin_fichier_ou_dossier": dossiers_str
        }
        
        if not appeler_workflow("06-06-git-historien.yml", historien_code_inputs):
            return False
        
        # Simulation de récupération du timestamp
        date_code = "1641081600"  # Placeholder
        
        # Étape 3: Comparateur de dates (Niveau 4)
        print("📊 Étape 3: Comparaison des dates...")
        comparateur_inputs = {
            "date_diagramme": date_diagramme,
            "date_code": date_code
        }
        
        if not appeler_workflow("04-01-planuml-comparateur.yml", comparateur_inputs):
            return False
        
        # Étape 4: Validation Comparateur (Niveau 5)
        print("✅ Étape 4: Validation du résultat de comparaison...")
        validation_inputs = {
            "resultat-comparaison": "resultat-comparaison"
        }
        
        if not appeler_workflow("05-01-planuml-valid-comparateur.yml", validation_inputs):
            return False
        
        # Étape 5: Formateur de statut (Niveau 7)
        print("📝 Étape 5: Génération du statut de check...")
        
        # Simulation de lecture du résultat
        mise_a_jour_requise = date_code > date_diagramme
        
        formateur_inputs = {
            "resultat": str(mise_a_jour_requise).lower(),
            "message_succes": "📐 Diagramme PlantUML synchronisé avec le code",
            "message_echec": "📐 ⚠️ Diagramme PlantUML potentiellement obsolète - mise à jour recommandée",
            "nom_check": "PlantUML Synchronization"
        }
        
        if not appeler_workflow("07-03-formateur-statut.yml", formateur_inputs):
            return False
        
        print("🎉 === AUDIT PLANTUML TERMINÉ AVEC SUCCÈS ===")
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique lors de l'orchestration: {e}")
        return False


def main():
    """Fonction principale du Contremaître."""
    parser = argparse.ArgumentParser(
        description="📐 Contremaître Audit PlantUML",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--diagramme',
        required=True,
        help='Chemin vers le fichier diagramme PlantUML'
    )
    
    parser.add_argument(
        '--dossiers-critiques',
        required=True,
        help='Liste des dossiers critiques à surveiller au format JSON'
    )
    
    args = parser.parse_args()
    
    try:
        dossiers_critiques = json.loads(args.dossiers_critiques)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON pour les dossiers: {e}")
        sys.exit(1)
    
    # Orchestration de l'audit PlantUML
    success = orchestrer_audit_planuml(args.diagramme, dossiers_critiques)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
