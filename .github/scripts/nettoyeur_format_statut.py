#!/usr/bin/env python3
"""
Nettoyeur : Formateur Statut
Poste un "check" de statut sur le commit GitHub avec la couleur et le message appropriés.
"""

import argparse
import json
import os
import sys
import subprocess
import requests
from datetime import datetime


class StatutFormatter:
    def __init__(self):
        """Initialise le formateur de statut avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Poste un check de statut sur GitHub')
        parser.add_argument('--resultat', required=True, choices=['true', 'false'],
                          help='Résultat du check (true/false)')
        parser.add_argument('--message-succes', required=True,
                          help='Message à afficher en cas de succès')
        parser.add_argument('--message-echec', required=True,
                          help='Message à afficher en cas d\'échec')
        parser.add_argument('--nom-check', required=True,
                          help='Nom du check à créer (ex: "AGI-Gouvernance/Audit-Lignes")')
        
        self.args = parser.parse_args()
        self.resultat_bool = self.args.resultat.lower() == 'true'
        
        # Récupération des variables d'environnement GitHub
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPOSITORY')
        self.github_sha = os.getenv('GITHUB_SHA')
        
        if not all([self.github_token, self.github_repo, self.github_sha]):
            print("❌ ERREUR: Variables d'environnement GitHub manquantes", file=sys.stderr)
            print("Requis: GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_SHA", file=sys.stderr)
            sys.exit(1)
    
    def run(self):
        """
        Logique principale : détermine le statut à poster selon le résultat
        et utilise l'API GitHub pour créer le check de statut.
        """
        try:
            # Détermination des paramètres du check selon le résultat
            if self.resultat_bool:
                conclusion = "success"
                message = self.args.message_succes
                emoji = "✅"
                title = f"{emoji} Check Réussi"
            else:
                conclusion = "failure"
                message = self.args.message_echec
                emoji = "❌"
                title = f"{emoji} Check Échoué"
            
            print(f"{emoji} Création du check '{self.args.nom_check}' avec conclusion: {conclusion}")
            
            # Tentative avec l'API GitHub (méthode préférée)
            success = self._create_check_via_api(conclusion, title, message)
            
            if not success:
                print("⚠️  API GitHub indisponible, utilisation du commit status en fallback")
                self._create_status_via_cli(conclusion, message)
            
            print(f"✅ Check de statut '{self.args.nom_check}' créé avec succès")
            
        except Exception as e:
            print(f"❌ ERREUR lors de la création du check de statut : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _create_check_via_api(self, conclusion, title, message):
        """
        Crée un check run via l'API GitHub (méthode recommandée).
        """
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/check-runs"
            
            payload = {
                "name": self.args.nom_check,
                "head_sha": self.github_sha,
                "status": "completed",
                "conclusion": conclusion,
                "started_at": datetime.utcnow().isoformat() + "Z",
                "completed_at": datetime.utcnow().isoformat() + "Z",
                "output": {
                    "title": title,
                    "summary": message,
                    "text": f"Check effectué le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{message}"
                }
            }
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 201:
                check_data = response.json()
                print(f"🔗 Check créé avec ID: {check_data.get('id')}")
                print(f"🌐 URL: {check_data.get('html_url', 'N/A')}")
                return True
            else:
                print(f"⚠️  Réponse API: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Erreur réseau API GitHub: {e}")
            return False
        except Exception as e:
            print(f"⚠️  Erreur création check API: {e}")
            return False
    
    def _create_status_via_cli(self, conclusion, message):
        """
        Crée un commit status via GitHub CLI en fallback.
        """
        try:
            # Mapping des conclusions pour commit status
            state_mapping = {
                "success": "success",
                "failure": "failure",
                "error": "error"
            }
            
            state = state_mapping.get(conclusion, "error")
            
            cmd = [
                "gh", "api",
                f"repos/{self.github_repo}/statuses/{self.github_sha}",
                "-f", f"state={state}",
                "-f", f"description={message}",
                "-f", f"context={self.args.nom_check}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("🔄 Commit status créé via GitHub CLI")
                return True
            else:
                print(f"⚠️  Erreur GitHub CLI: {result.stderr}")
                # Essayer une approche encore plus simple
                return self._create_simple_output(conclusion, message)
                
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout GitHub CLI")
            return False
        except Exception as e:
            print(f"⚠️  Erreur GitHub CLI: {e}")
            return False
    
    def _create_simple_output(self, conclusion, message):
        """
        En dernier recours, écrit le statut dans les outputs GitHub Actions.
        """
        try:
            # Écriture dans GITHUB_STEP_SUMMARY pour affichage dans l'interface
            summary_content = f"""
## {self.args.nom_check}

**Résultat:** {"✅ Succès" if conclusion == "success" else "❌ Échec"}

**Message:** {message}

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            if 'GITHUB_STEP_SUMMARY' in os.environ:
                with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
                    f.write(summary_content)
                print("📄 Statut écrit dans GITHUB_STEP_SUMMARY")
            
            # Écriture dans les outputs
            if 'GITHUB_OUTPUT' in os.environ:
                with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
                    f.write(f"check_result={conclusion}\n")
                    f.write(f"check_message={message}\n")
                    f.write(f"check_name={self.args.nom_check}\n")
                print("📤 Statut écrit dans GITHUB_OUTPUT")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Erreur création output simple: {e}")
            return False


if __name__ == "__main__":
    formatter = StatutFormatter()
    formatter.run()
