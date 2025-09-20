#!/usr/bin/env python3
"""
GitHub Issue Creator - Transforme les Violations en Tâches Traçables
=====================================================================

Rôle Fondamental (Conforme iaGOD.json) :
- Lire le rapport d'audit structuré (violations.json).
- Se connecter à l'API GitHub via le CLI `gh`.
- Créer une issue GitHub pour chaque violation CRITIQUE.
- Assurer la traçabilité complète de la dette de conformité.
"""

import json
import subprocess
import shlex
import time
from pathlib import Path

VIOLATIONS_FILE = Path("violations.json")
# Ciblez votre dépôt au format "PROPRIETAIRE/NOM_DU_DEPOT"
REPO = "totodeltolosan/AGI"

def run_command(command: str):
    """Exécute une commande shell et retourne le résultat."""
    try:
        process = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de la commande : {command}")
        print(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"❌ Commande 'gh' introuvable. Assurez-vous que GitHub CLI est installé et dans votre PATH.")
        return None

def create_github_issue(repo: str, title: str, body: str, labels: str):
    """Crée une issue sur le dépôt GitHub spécifié."""
    print(f"Création de l'issue : {title}")
    # Utilisation de shlex.quote pour gérer les caractères spéciaux dans le titre et le corps
    safe_title = shlex.quote(title)
    safe_body = shlex.quote(body)
    safe_labels = shlex.quote(labels)

    command = f'gh issue create --repo "{repo}" --title {safe_title} --body {safe_body} --label {safe_labels}'

    # Exécuter la commande via le shell pour gérer correctement les quotes complexes
    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création de l'issue : {title}")
        print(f"Stderr: {e.stderr}")
        return None

def main():
    """Point d'entrée principal du script."""
    if not VIOLATIONS_FILE.exists():
        print(f"❌ Le fichier '{VIOLATIONS_FILE}' est introuvable. Veuillez d'abord générer le rapport d'audit.")
        return

    with VIOLATIONS_FILE.open('r', encoding='utf-8') as f:
        data = json.load(f)

    critical_violations = [v for v in data.get("violations", []) if v["severity"] == "CRITICAL"]

    if not critical_violations:
        print("✅ Aucune violation critique à signaler. Excellent travail !")
        return

    print(f"🚀 Traitement de {len(critical_violations)} violations critiques pour le dépôt {REPO}...")
    print("ℹ️  Une pause de 2 secondes sera respectée entre chaque création pour ne pas surcharger l'API GitHub.")

    for i, violation in enumerate(critical_violations):
        law_id = violation['law_id']
        file_path = violation['file_path']
        line = violation['line_number']
        message = violation['message']

        # Tronquer le titre s'il est trop long pour GitHub
        title = f"[AUDIT][{law_id}] Violation Critique dans {file_path}"
        if len(title) > 250:
            title = title[:247] + "..."

        body = (f"**Violation Constitutionnelle Détectée**\n\n"
                f"- **Loi :** `{violation['law_name']}` ({law_id})\n"
                f"- **Fichier :** `{file_path}`\n"
                f"- **Ligne :** `{line}`\n"
                f"- **Message :** {message}\n\n"
                f"**Suggestion :**\n> {violation.get('suggestion', 'Aucune suggestion automatique.')}\n\n"
                f"*Cette issue a été créée automatiquement par l'auditeur constitutionnel AGI.*")

        labels = "audit,critical-violation,needs-triage"

        issue_url = create_github_issue(REPO, title, body, labels)
        if issue_url:
            print(f"   -> ✅ Issue créée : {issue_url}")
        else:
            print(f"   -> ❌ Échec de la création de l'issue pour {file_path}")

        # Pause pour respecter les limites de l'API GitHub
        time.sleep(2)

    print("\n🎉 Terminé. Toutes les violations critiques sont maintenant tracées comme des issues sur GitHub.")

if __name__ == "__main__":
    main()
