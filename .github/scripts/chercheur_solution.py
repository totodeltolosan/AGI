#!/usr/bin/env python3
"""
🔍 Contremaître Chercheur de Solution (Niveau 3)
================================================

Orchestre la recherche et communication de solutions.
Pipeline : Analyse (Log/KB/Simu) → Validation → Communication (Artefact/Check/Comment/Dispatch/PR)

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


def orchestrer_chercheur_solution(payload_evenement: dict) -> bool:
    """
    Orchestre la recherche et communication de solutions.
    
    Args:
        payload_evenement: Payload de l'événement repository_dispatch
        
    Returns:
        True si succès complet, False sinon
    """
    print("🔍 === CONTREMAÎTRE CHERCHEUR DE SOLUTION ===")
    print(f"Payload événement: {payload_evenement}")
    print()
    
    try:
        # Extraction des informations de l'événement
        type_probleme = payload_evenement.get('type_probleme', 'unknown')
        details = payload_evenement.get('details', {})
        
        # Phase 1: ANALYSE
        print("🔬 === PHASE ANALYSE ===")
        
        # Étape 1: Analyse des logs si ID run fourni
        if 'id_run' in details:
            print("📊 Étape 1a: Analyse des logs...")
            analyse_log_inputs = {
                "id_run": str(details['id_run'])
            }
            
            if not appeler_workflow("04-06-chercheur-analyse-log.yml", analyse_log_inputs):
                return False
            
            # Validation
            if not appeler_workflow("05-06-chercheur-valid-analyse-log.yml", {"diagnostic-log": "diagnostic-log"}):
                return False
        
        # Étape 2: Recherche dans la base de connaissance
        print("📚 Étape 2: Recherche dans la base de connaissance...")
        mots_cles = details.get('mots_cles', type_probleme)
        analyse_kb_inputs = {
            "mots_cles_probleme": mots_cles
        }
        
        if not appeler_workflow("04-07-chercheur-analyse-kb.yml", analyse_kb_inputs):
            return False
        
        # Validation
        if not appeler_workflow("05-07-chercheur-valid-analyse-kb.yml", {"solutions-potentielles": "solutions-potentielles"}):
            return False
        
        # Étape 3: Simulation de solution si patch fourni
        if 'patch_a_tester' in details:
            print("🧪 Étape 3: Simulation de la solution...")
            analyse_simu_inputs = {
                "donnees_probleme": json.dumps(details),
                "patch_a_tester": json.dumps(details['patch_a_tester'])
            }
            
            if not appeler_workflow("04-08-chercheur-analyse-simu.yml", analyse_simu_inputs):
                return False
            
            # Validation
            if not appeler_workflow("05-08-chercheur-valid-analyse-simu.yml", {"resultat-simulation": "resultat-simulation"}):
                return False
        
        # Phase 2: COMMUNICATION
        print("🗣️ === PHASE COMMUNICATION ===")
        
        # Étape 4: Création d'un artefact de proposition
        print("📝 Étape 4: Création artefact de solution...")
        nom_artefact = f"solution-{type_probleme}-{details.get('timestamp', '0')}"
        solution_content = {
            "type_probleme": type_probleme,
            "solutions_trouvees": "solutions-potentielles",
            "recommandations": ["Voir solutions-potentielles.json"],
            "confiance": 0.8
        }
        
        comm_artefact_inputs = {
            "nom_artefact_cible": nom_artefact,
            "contenu_solution": json.dumps(solution_content)
        }
        
        if not appeler_workflow("04-01-chercheur-comm-artefact.yml", comm_artefact_inputs):
            return False
        
        # Validation
        if not appeler_workflow("05-01-chercheur-valid-comm-artefact.yml", {"nom_artefact_cible": nom_artefact}):
            return False
        
        # Étape 5: Publication d'un check de statut
        print("✅ Étape 5: Publication du check de statut...")
        comm_check_inputs = {
            "nom_check": f"Solution-{type_probleme}",
            "conclusion": "success",
            "details": f"Solution proposée pour {type_probleme}"
        }
        
        if not appeler_workflow("04-02-chercheur-comm-check.yml", comm_check_inputs):
            return False
        
        # Validation
        if not appeler_workflow("05-02-chercheur-valid-comm-check.yml", {"nom_check": f"Solution-{type_probleme}"}):
            return False
        
        # Étape 6: Commentaire sur PR si numéro fourni
        if 'numero_pr' in details:
            print("💬 Étape 6: Commentaire sur la PR...")
            corps_commentaire = f"🔍 **Solution proposée pour {type_probleme}**\n\nConsulter l'artefact `{nom_artefact}` pour les détails."
            
            comm_commentaire_inputs = {
                "numero_pr": str(details['numero_pr']),
                "corps_commentaire": corps_commentaire
            }
            
            if not appeler_workflow("04-03-chercheur-comm-commentaire.yml", comm_commentaire_inputs):
                return False
            
            # Validation
            validation_inputs = {
                "numero_pr": str(details['numero_pr']),
                "id_commentaire_attendu": "auto-generated"
            }
            if not appeler_workflow("05-03-chercheur-valid-comm-commentaire.yml", validation_inputs):
                return False
        
        print("🎉 === CHERCHEUR DE SOLUTION TERMINÉ AVEC SUCCÈS ===")
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique lors de l'orchestration: {e}")
        return False


def main():
    """Fonction principale du Contremaître."""
    parser = argparse.ArgumentParser(
        description="🔍 Contremaître Chercheur de Solution",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--payload',
        required=True,
        help='Payload de l\'événement repository_dispatch au format JSON'
    )
    
    args = parser.parse_args()
    
    try:
        payload_evenement = json.loads(args.payload)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON pour le payload: {e}")
        sys.exit(1)
    
    # Orchestration de la recherche de solution
    success = orchestrer_chercheur_solution(payload_evenement)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
