#!/usr/bin/env python3
"""
Travailleur : GitHub Poster
Brique d'interaction avec l'API GitHub pour créer des issues automatiquement.
"""

import argparse
import json
import os
import sys
import subprocess
import requests
from datetime import datetime


class GitHubPoster:
    def __init__(self):
        """Initialise le poster GitHub avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Crée une issue GitHub via API')
        parser.add_argument('--titre', required=True,
                          help='Titre de l\'issue à créer')
        parser.add_argument('--corps', required=True,
                          help='Corps du message de l\'issue (Markdown supporté)')
        parser.add_argument('--labels', required=False, default='[]',
                          help='JSON array des labels à appliquer')
        parser.add_argument('--assignes', required=False, default='[]',
                          help='JSON array des utilisateurs à assigner')
        parser.add_argument('--milestone', required=False,
                          help='ID ou nom du milestone à associer')
        
        self.args = parser.parse_args()
        
        # Validation et parsing des paramètres JSON
        try:
            self.labels = json.loads(self.args.labels)
            self.assignes = json.loads(self.args.assignes)
            
            if not isinstance(self.labels, list):
                raise ValueError("Labels doivent être une liste JSON")
            if not isinstance(self.assignes, list):
                raise ValueError("Assignés doivent être une liste JSON")
                
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR: Format JSON invalide - {e}", file=sys.stderr)
            sys.exit(1)
        
        # Récupération des variables d'environnement GitHub
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPOSITORY')
        
        if not all([self.github_token, self.github_repo]):
            print("❌ ERREUR: Variables d'environnement GitHub manquantes", file=sys.stderr)
            print("Requis: GITHUB_TOKEN, GITHUB_REPOSITORY", file=sys.stderr)
            sys.exit(1)
    
    def run(self):
        """
        Logique principale : crée une issue GitHub avec les paramètres fournis.
        Utilise l'API GitHub REST en priorité, avec GitHub CLI en fallback.
        """
        try:
            print(f"🎫 Création d'issue GitHub")
            print(f"📋 Titre: {self.args.titre}")
            print(f"🏷️  Labels: {self.labels}")
            print(f"👥 Assignés: {self.assignes}")
            
            # Tentative avec l'API GitHub (méthode préférée)
            issue_url = self._create_issue_via_api()
            
            if not issue_url:
                print("⚠️  API GitHub indisponible, utilisation de GitHub CLI")
                issue_url = self._create_issue_via_cli()
            
            if issue_url:
                print(f"✅ Issue créée avec succès")
                print(f"🔗 URL: {issue_url}")
                
                # Écriture de l'URL dans les outputs GitHub Actions
                self._write_github_outputs(issue_url)
            else:
                print("❌ Échec de création de l'issue par tous les moyens")
                sys.exit(1)
            
        except Exception as e:
            print(f"❌ ERREUR lors de la création d'issue : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _create_issue_via_api(self):
        """
        Crée une issue via l'API GitHub REST (méthode recommandée).
        """
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/issues"
            
            payload = {
                "title": self.args.titre,
                "body": self.args.corps,
                "labels": self.labels,
                "assignees": self.assignes
            }
            
            # Ajout du milestone si spécifié
            if self.args.milestone:
                # Si c'est un nombre, l'utiliser directement comme ID
                try:
                    milestone_id = int(self.args.milestone)
                    payload["milestone"] = milestone_id
                except ValueError:
                    # Sinon, rechercher le milestone par nom
                    milestone_id = self._find_milestone_by_name(self.args.milestone)
                    if milestone_id:
                        payload["milestone"] = milestone_id
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 201:
                issue_data = response.json()
                print(f"🆔 Issue créée avec numéro: #{issue_data['number']}")
                print(f"📅 Créée le: {issue_data['created_at']}")
                return issue_data['html_url']
            else:
                print(f"⚠️  Réponse API: {response.status_code}")
                if response.text:
                    print(f"Détails: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Erreur réseau API GitHub: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Erreur création issue API: {e}")
            return None
    
    def _create_issue_via_cli(self):
        """
        Crée une issue via GitHub CLI en fallback.
        """
        try:
            cmd = [
                "gh", "issue", "create",
                "--title", self.args.titre,
                "--body", self.args.corps
            ]
            
            # Ajout des labels
            if self.labels:
                cmd.extend(["--label", ",".join(self.labels)])
            
            # Ajout des assignés
            if self.assignes:
                cmd.extend(["--assignee", ",".join(self.assignes)])
            
            # Ajout du milestone
            if self.args.milestone:
                cmd.extend(["--milestone", self.args.milestone])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # L'URL de l'issue est dans stdout
                issue_url = result.stdout.strip()
                print(f"🔄 Issue créée via GitHub CLI")
                return issue_url
            else:
                print(f"⚠️  Erreur GitHub CLI: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout GitHub CLI")
            return None
        except FileNotFoundError:
            print("⚠️  GitHub CLI non disponible")
            return None
        except Exception as e:
            print(f"⚠️  Erreur GitHub CLI: {e}")
            return None
    
    def _find_milestone_by_name(self, milestone_name):
        """
        Trouve l'ID d'un milestone par son nom.
        """
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/milestones"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                milestones = response.json()
                for milestone in milestones:
                    if milestone['title'].lower() == milestone_name.lower():
                        print(f"📌 Milestone trouvé: {milestone['title']} (ID: {milestone['number']})")
                        return milestone['number']
                
                print(f"⚠️  Milestone '{milestone_name}' non trouvé")
                return None
            else:
                print(f"⚠️  Erreur récupération milestones: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️  Erreur recherche milestone: {e}")
            return None
    
    def _write_github_outputs(self, issue_url):
        """
        Écrit l'URL de l'issue dans les outputs GitHub Actions.
        """
        try:
            # Extraction du numéro d'issue depuis l'URL
            issue_number = issue_url.split('/')[-1]
            
            # Écriture dans GITHUB_OUTPUT
            if 'GITHUB_OUTPUT' in os.environ:
                with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
                    f.write(f"issue_url={issue_url}\n")
                    f.write(f"issue_number={issue_number}\n")
                    f.write(f"creation_timestamp={datetime.now().isoformat()}\n")
                print("📤 Outputs GitHub Actions mis à jour")
            
            # Écriture dans GITHUB_STEP_SUMMARY
            if 'GITHUB_STEP_SUMMARY' in os.environ:
                summary_content = f"""
## 🎫 Issue GitHub Créée

**Titre:** {self.args.titre}

**URL:** [{issue_url}]({issue_url})

**Labels:** {', '.join(self.labels) if self.labels else 'Aucun'}

**Assignés:** {', '.join(self.assignes) if self.assignes else 'Aucun'}

**Créée le:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
                    f.write(summary_content)
                print("📄 Résumé ajouté à GitHub Actions")
                
        except Exception as e:
            print(f"⚠️  Erreur écriture outputs: {e}")


if __name__ == "__main__":
    poster = GitHubPoster()
    poster.run()
