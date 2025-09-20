#!/usr/bin/env python3
"""
Intégration GitHub API pour le projet AGI
Crée automatiquement des issues pour les violations constitutionnelles
"""

import os
import sys
import requests
import csv
from datetime import datetime

class GitHubIntegration:
    def __init__(self, repo_owner, repo_name, token):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_violation_issue(self, violation):
        """Créer une issue pour une violation constitutionnelle"""
        title = f"[VIOLATION] {violation['Fichier']} dépasse la limite constitutionnelle"
        
        body = f"""## 🏛️ Violation Constitutionnelle Détectée

**Fichier:** `{violation['Fichier']}`
**Lignes:** {violation['Lignes']} (excès: +{violation['Excès']})
**Date de détection:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Action Requise
Ce fichier dépasse la limite constitutionnelle de 200 lignes et doit être refactorisé.

### Suggestion de Correction
- Décomposer en {max(2, violation['Excès'] // 100)} modules plus petits
- Appliquer les principes de responsabilité unique
- Maintenir la cohésion fonctionnelle

### Impact sur la Conformité
Cette violation contribue à réduire notre taux de conformité constitutionnelle général.

---
*Issue générée automatiquement par le système d'audit constitutionnel AGI*
"""

        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": ["constitutional-violation", "technical-debt", "automated"]
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 201

    def process_conformity_report(self, csv_file):
        """Traiter un rapport de conformité CSV et créer des issues"""
        violations_created = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Statut'] == 'VIOLATION':
                        if self.create_violation_issue(row):
                            violations_created += 1
                            print(f"✅ Issue créée pour {row['Fichier']}")
                        else:
                            print(f"❌ Échec création issue pour {row['Fichier']}")
        
        except FileNotFoundError:
            print(f"❌ Fichier {csv_file} non trouvé")
            return 0
        
        return violations_created

if __name__ == "__main__":
    # Configuration
    REPO_OWNER = "totodeltolosan"
    REPO_NAME = "AGI"
    
    # Token GitHub (à configurer en secret)
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN non configuré")
        sys.exit(1)
    
    # Traitement
    github = GitHubIntegration(REPO_OWNER, REPO_NAME, token)
    
    # Chercher le dernier rapport de conformité
    import glob
    reports = glob.glob("conformite_*.csv")
    if reports:
        latest_report = max(reports)
        print(f"📊 Traitement du rapport: {latest_report}")
        violations = github.process_conformity_report(latest_report)
        print(f"✅ {violations} violations converties en issues")
    else:
        print("❌ Aucun rapport de conformité trouvé")
