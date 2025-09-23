#!/usr/bin/env python3
"""
🗄️ Contremaître Sauvegarde Rapports (Niveau 3)
===============================================

Orchestre la sauvegarde et l'archivage de tous les rapports d'audit.
Pipeline : Collecteur → Validation → Archiveur ZIP

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


def orchestrer_sauvegarde_rapports(noms_artefacts: list, nom_archive: str) -> bool:
    """
    Orchestre la sauvegarde complète de tous les rapports d'audit.
    
    Args:
        noms_artefacts: Liste des noms d'artefacts à sauvegarder
        nom_archive: Nom de l'archive finale à créer
        
    Returns:
        True si succès complet, False sinon
    """
    print("🗄️ === CONTREMAÎTRE SAUVEGARDE RAPPORTS ===")
    print(f"Artefacts à sauvegarder: {noms_artefacts}")
    print(f"Archive finale: {nom_archive}")
    print()
    
    try:
        # Étape 1: Collecteur de rapports (Niveau 4)
        print("📥 Étape 1: Collecte de tous les rapports...")
        collecteur_inputs = {
            "noms_artefacts": json.dumps(noms_artefacts)
        }
        
        if not appeler_workflow("04-01-sauvegarde-collecteur.yml", collecteur_inputs):
            return False
        
        # Étape 2: Validation Collecteur (Niveau 5)
        print("✅ Étape 2: Validation des fichiers collectés...")
        # Génération de la liste des fichiers attendus
        fichiers_attendus = []
        for artefact in noms_artefacts:
            # Mapping des noms d'artefacts vers les noms de fichiers
            if artefact == "rapport-lignes":
                fichiers_attendus.append("rapport-lignes.csv")
            elif artefact == "violations-triees":
                fichiers_attendus.append("violations-triees.json")
            elif artefact == "statistiques-documentation":
                fichiers_attendus.append("statistiques-documentation.json")
            else:
                fichiers_attendus.append(f"{artefact}.json")
        
        validation_collecteur_inputs = {
            "noms_fichiers_attendus": json.dumps(fichiers_attendus)
        }
        
        if not appeler_workflow("05-01-sauvegarde-valid-collecteur.yml", validation_collecteur_inputs):
            return False
        
        # Étape 3: Archiveur ZIP (Niveau 6)
        print("📦 Étape 3: Création de l'archive ZIP...")
        archiveur_inputs = {
            "nom_archive": nom_archive,
            "fichiers_a_zipper": json.dumps(fichiers_attendus)
        }
        
        if not appeler_workflow("06-05-archiveur-zip.yml", archiveur_inputs):
            return False
        
        print("🎉 === SAUVEGARDE RAPPORTS TERMINÉE AVEC SUCCÈS ===")
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique lors de l'orchestration: {e}")
        return False


def main():
    """Fonction principale du Contremaître."""
    parser = argparse.ArgumentParser(
        description="🗄️ Contremaître Sauvegarde Rapports",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--artefacts',
        required=True,
        help='Liste des noms d\'artefacts à sauvegarder au format JSON'
    )
    
    parser.add_argument(
        '--nom-archive',
        required=True,
        help='Nom de l\'archive finale à créer'
    )
    
    args = parser.parse_args()
    
    try:
        noms_artefacts = json.loads(args.artefacts)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON pour les artefacts: {e}")
        sys.exit(1)
    
    # Orchestration de la sauvegarde
    success = orchestrer_sauvegarde_rapports(noms_artefacts, args.nom_archive)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
