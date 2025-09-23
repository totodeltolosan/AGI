#!/usr/bin/env python3
"""
📏 Contremaître Audit Lignes (Niveau 3)
=========================================

Orchestre l'audit complet de la Division "Loi Lignes".
Pipeline : Scanner → Compteur → Validation → Juge → Validation →
          Statisticien → Validation → Rapporteur → Validation →
          Conseiller → Validation → Formateur CSV

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


def orchestrer_audit_lignes(limite_lignes: int, exclusions: list) -> bool:
    """
    Orchestre l'audit complet de la division Loi Lignes.

    Args:
        limite_lignes: Limite maximale de lignes autorisée
        exclusions: Liste des patterns de fichiers à exclure

    Returns:
        True si succès complet, False sinon
    """
    print("📏 === CONTREMAÎTRE AUDIT LIGNES ===")
    print(f"Limite de lignes: {limite_lignes}")
    print(f"Exclusions: {exclusions}")
    print()

    try:
        # Étape 1: Scanner les fichiers (Niveau 6)
        print("🔍 Étape 1: Scan des fichiers Python...")
        scanner_inputs = {
            "pattern": "*.py",
            "chemin_racine": ".",
            "exclusions": json.dumps(exclusions),
        }

        if not appeler_workflow("06-01-scanner-fichiers.yml", scanner_inputs):
            return False

        # Attendre la fin du scan (simulation)
        print("⏳ Attente de la fin du scan...")

        # Étape 2: Compteur de lignes (Niveau 4)
        print("📊 Étape 2: Comptage des lignes...")
        compteur_inputs = {"liste-fichiers": "liste-fichiers"}

        if not appeler_workflow("04-01-lignes-compteur.yml", compteur_inputs):
            return False

        # Étape 3: Validation Compteur (Niveau 5)
        print("✅ Étape 3: Validation du comptage...")
        validation_inputs = {"resultats-bruts-compteur": "resultats-bruts-compteur"}

        if not appeler_workflow("05-01-lignes-valid-compteur.yml", validation_inputs):
            return False

        # Étape 4: Juge (Niveau 4)
        print("⚖️ Étape 4: Jugement conformité...")
        juge_inputs = {
            "resultats-bruts-compteur": "resultats-bruts-compteur",
            "limite_lignes": str(limite_lignes),
        }

        if not appeler_workflow("04-02-lignes-juge.yml", juge_inputs):
            return False

        # Étape 5: Validation Juge (Niveau 5)
        print("✅ Étape 5: Validation du jugement...")
        validation_juge_inputs = {"resultats-juges": "resultats-juges"}

        if not appeler_workflow("05-02-lignes-valid-juge.yml", validation_juge_inputs):
            return False

        # Étape 6: Statisticien (Niveau 4)
        print("📈 Étape 6: Calcul des statistiques...")
        statisticien_inputs = {"resultats-juges": "resultats-juges"}

        if not appeler_workflow("04-03-lignes-statisticien.yml", statisticien_inputs):
            return False

        # Étape 7: Validation Statisticien (Niveau 5)
        print("✅ Étape 7: Validation des statistiques...")
        validation_stats_inputs = {"statistiques": "statistiques"}

        if not appeler_workflow(
            "05-03-lignes-valid-statisticien.yml", validation_stats_inputs
        ):
            return False

        # Étape 8: Rapporteur (Niveau 4)
        print("📝 Étape 8: Génération du rapport...")
        rapporteur_inputs = {
            "resultats-juges": "resultats-juges",
            "statistiques": "statistiques",
        }

        if not appeler_workflow("04-04-lignes-rapporteur.yml", rapporteur_inputs):
            return False

        # Étape 9: Validation Rapporteur (Niveau 5)
        print("✅ Étape 9: Validation du rapport...")
        validation_rapport_inputs = {"rapport-lignes": "rapport-lignes"}

        if not appeler_workflow(
            "05-04-lignes-valid-rapporteur.yml", validation_rapport_inputs
        ):
            return False

        # Étape 10: Conseiller (Niveau 4)
        print("💡 Étape 10: Génération des recommandations...")
        conseiller_inputs = {"statistiques": "statistiques"}

        if not appeler_workflow("04-05-lignes-conseiller.yml", conseiller_inputs):
            return False

        # Étape 11: Validation Conseiller (Niveau 5)
        print("✅ Étape 11: Validation des recommandations...")
        validation_conseiller_inputs = {"recommandations": "recommandations"}

        if not appeler_workflow(
            "05-05-lignes-valid-conseiller.yml", validation_conseiller_inputs
        ):
            return False

        # Étape 12: Formateur CSV final (Niveau 7)
        print("📊 Étape 12: Formatage CSV final...")
        formateur_inputs = {
            "artefact_entree_json": "statistiques",
            "nom_fichier_sortie_csv": "rapport-lignes-final.csv",
            "colonnes": json.dumps(["fichier", "lignes", "conforme", "recommandation"]),
        }

        if not appeler_workflow("07-01-formateur-csv.yml", formateur_inputs):
            return False

        print("🎉 === AUDIT LIGNES TERMINÉ AVEC SUCCÈS ===")
        return True

    except Exception as e:
        print(f"❌ Erreur critique lors de l'orchestration: {e}")
        return False


def main():
    """Fonction principale du Contremaître."""
    parser = argparse.ArgumentParser(
        description="📏 Contremaître Audit Lignes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--limite-lignes",
        type=int,
        required=True,
        help="Limite maximale de lignes autorisée par fichier",
    )

    parser.add_argument(
        "--exclusions",
        required=True,
        help="Liste des patterns de fichiers à exclure (JSON)",
    )
    parser.add_argument(
        "--audit-id",
        required=False,
        default="default",
        help="Identifiant unique de l'audit",
    )

    args = parser.parse_args()

    try:
        exclusions = json.loads(args.exclusions)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON pour les exclusions: {e}")
        sys.exit(1)

    # Orchestration de l'audit
    success = orchestrer_audit_lignes(args.limite_lignes, exclusions)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
