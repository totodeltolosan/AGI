#!/usr/bin/env python3
"""
🔍 Contremaître Auditeur de Solution (Niveau 3)
===============================================

Orchestre l'audit complet d'une proposition de solution.
Pipeline : Schema → Validation → Sécurité → Validation → Simulation → Validation → 
          Coût → Validation → Plan Final → Validation

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


def orchestrer_auditeur_solution(proposition_solution: dict, metriques_actuelles: dict) -> bool:
    """
    Orchestre l'audit complet d'une proposition de solution.
    
    Args:
        proposition_solution: Proposition de solution à auditer
        metriques_actuelles: Métriques actuelles du système
        
    Returns:
        True si succès complet, False sinon
    """
    print("🔍 === CONTREMAÎTRE AUDITEUR DE SOLUTION ===")
    print(f"Type de solution: {proposition_solution.get('type', 'unknown')}")
    print()
    
    try:
        # Schéma de validation attendu (exemple)
        schema_attendu = {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "description": {"type": "string"},
                "implementation": {"type": "object"},
                "impacts": {"type": "array"}
            },
            "required": ["type", "description"]
        }
        
        # Étape 1: Validation du schéma (Niveau 4)
        print("📋 Étape 1: Validation du schéma de la solution...")
        auditeur_schema_inputs = {
            "proposition_solution": json.dumps(proposition_solution),
            "schema_attendu": json.dumps(schema_attendu)
        }
        
        if not appeler_workflow("04-01-auditeur-schema.yml", auditeur_schema_inputs):
            return False
        
        # Validation du rapport de schéma
        print("✅ Étape 1b: Validation du rapport de schéma...")
        if not appeler_workflow("05-01-auditeur-valid-schema.yml", {"validation-schema": "validation-schema"}):
            return False
        
        # Étape 2: Audit de sécurité (Niveau 4)
        print("🛡️ Étape 2: Audit de sécurité de la solution...")
        auditeur_securite_inputs = {
            "proposition_solution": json.dumps(proposition_solution)
        }
        
        if not appeler_workflow("04-02-auditeur-securite.yml", auditeur_securite_inputs):
            return False
        
        # Validation du rapport de sécurité
        print("✅ Étape 2b: Validation du rapport de sécurité...")
        if not appeler_workflow("05-02-auditeur-valid-securite.yml", {"rapport-securite-solution": "rapport-securite-solution"}):
            return False
        
        # Étape 3: Simulation en bac à sable (Niveau 4)
        print("🧪 Étape 3: Simulation de la solution...")
        auditeur_simulation_inputs = {
            "proposition_solution": json.dumps(proposition_solution),
            "environnement_test": "sandbox"
        }
        
        if not appeler_workflow("04-03-auditeur-simulation.yml", auditeur_simulation_inputs):
            return False
        
        # Validation du rapport de simulation
        print("✅ Étape 3b: Validation du rapport de simulation...")
        if not appeler_workflow("05-03-auditeur-valid-simulation.yml", {"resultat-simulation-audit": "resultat-simulation-audit"}):
            return False
        
        # Étape 4: Analyse coût/bénéfice (Niveau 4)
        print("💰 Étape 4: Analyse coût/bénéfice...")
        auditeur_cout_inputs = {
            "proposition_solution": json.dumps(proposition_solution),
            "metriques_actuelles": json.dumps(metriques_actuelles)
        }
        
        if not appeler_workflow("04-04-auditeur-cout.yml", auditeur_cout_inputs):
            return False
        
        # Validation du rapport coût/bénéfice
        print("✅ Étape 4b: Validation du rapport coût/bénéfice...")
        if not appeler_workflow("05-04-auditeur-valid-cout.yml", {"analyse-cout-benefice": "analyse-cout-benefice"}):
            return False
        
        # Étape 5: Génération du plan d'implémentation (Niveau 4)
        print("📋 Étape 5: Génération du plan d'implémentation...")
        auditeur_plan_inputs = {
            "validation-schema": "validation-schema",
            "rapport-securite-solution": "rapport-securite-solution",
            "resultat-simulation-audit": "resultat-simulation-audit",
            "analyse-cout-benefice": "analyse-cout-benefice"
        }
        
        if not appeler_workflow("04-05-auditeur-plan.yml", auditeur_plan_inputs):
            return False
        
        # Validation du plan d'implémentation
        print("✅ Étape 5b: Validation du plan d'implémentation...")
        if not appeler_workflow("05-05-auditeur-valid-plan.yml", {"plan-implementation": "plan-implementation"}):
            return False
        
        print("🎉 === AUDITEUR DE SOLUTION TERMINÉ AVEC SUCCÈS ===")
        print("📋 Plan d'implémentation disponible dans l'artefact 'plan-implementation'")
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique lors de l'orchestration: {e}")
        return False


def main():
    """Fonction principale du Contremaître."""
    parser = argparse.ArgumentParser(
        description="🔍 Contremaître Auditeur de Solution",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--proposition',
        required=True,
        help='Proposition de solution à auditer au format JSON'
    )
    
    parser.add_argument(
        '--metriques',
        required=True,
        help='Métriques actuelles du système au format JSON'
    )
    
    args = parser.parse_args()
    
    try:
        proposition_solution = json.loads(args.proposition)
        metriques_actuelles = json.loads(args.metriques)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        sys.exit(1)
    
    # Orchestration de l'audit de solution
    success = orchestrer_auditeur_solution(proposition_solution, metriques_actuelles)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
