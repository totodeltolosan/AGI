#!/usr/bin/env python3
"""
Travailleur : Git Historien
Brique d'interrogation de l'historique Git pour trouver les dates de modification.
"""

import argparse
import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class GitHistorien:
    def __init__(self):
        """Initialise l'historien Git avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Interroge l\'historique Git pour les dates')
        parser.add_argument('--chemin-fichier-ou-dossier', required=True,
                          help='Chemin vers le fichier ou dossier à analyser')
        parser.add_argument('--format-sortie', choices=['timestamp', 'iso', 'human'], 
                          default='iso',
                          help='Format de la date retournée')
        parser.add_argument('--operation', choices=['last_commit', 'first_commit', 'all_commits'], 
                          default='last_commit',
                          help='Type d\'opération à effectuer')
        parser.add_argument('--sortie', default='git-historique.json',
                          help='Nom du fichier JSON de sortie (optionnel)')
        
        self.args = parser.parse_args()
        
        # Validation du chemin
        if not os.path.exists(self.args.chemin_fichier_ou_dossier):
            print(f"❌ ERREUR: Chemin introuvable : {self.args.chemin_fichier_ou_dossier}", file=sys.stderr)
            sys.exit(1)
    
    def run(self):
        """
        Logique principale : interroge l'historique Git pour obtenir les informations
        de versioning du fichier ou dossier spécifié.
        """
        try:
            chemin = self.args.chemin_fichier_ou_dossier
            print(f"🕰️  Analyse Git : {chemin}")
            print(f"📋 Opération : {self.args.operation}")
            
            # Vérification que nous sommes dans un repository Git
            if not self._is_git_repository():
                print("❌ ERREUR: Pas dans un repository Git", file=sys.stderr)
                sys.exit(1)
            
            # Exécution de l'opération demandée
            if self.args.operation == 'last_commit':
                result = self._get_last_commit(chemin)
            elif self.args.operation == 'first_commit':
                result = self._get_first_commit(chemin)
            elif self.args.operation == 'all_commits':
                result = self._get_all_commits(chemin)
            else:
                raise ValueError(f"Opération non supportée : {self.args.operation}")
            
            # Formatage et sortie des résultats
            self._output_results(result, chemin)
            
        except Exception as e:
            print(f"❌ ERREUR lors de l'analyse Git : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _is_git_repository(self):
        """Vérifie si nous sommes dans un repository Git."""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         capture_output=True, check=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _get_last_commit(self, chemin):
        """
        Récupère les informations du dernier commit affectant le chemin.
        """
        try:
            # Commande Git pour obtenir le dernier commit
            cmd = [
                'git', 'log', '-1', 
                '--format=%H|%ci|%an|%s', 
                '--', chemin
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True, timeout=30)
            
            if not result.stdout.strip():
                print(f"⚠️  Aucun commit trouvé pour : {chemin}")
                return None
            
            # Parse de la sortie Git
            parts = result.stdout.strip().split('|', 3)
            if len(parts) != 4:
                raise ValueError("Format de sortie Git inattendu")
            
            commit_hash, date_str, author, message = parts
            
            # Conversion de la date
            commit_date = datetime.fromisoformat(date_str.replace(' ', 'T', 1))
            
            return {
                'type': 'last_commit',
                'commit_hash': commit_hash,
                'date': commit_date,
                'author': author,
                'message': message.strip(),
                'path': chemin
            }
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Erreur commande Git : {e.stderr if e.stderr else 'Inconnue'}")
            return None
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout commande Git")
            return None
        except Exception as e:
            print(f"⚠️  Erreur analyse dernier commit : {e}")
            return None
    
    def _get_first_commit(self, chemin):
        """
        Récupère les informations du premier commit ayant créé le fichier/dossier.
        """
        try:
            # Commande Git pour obtenir le premier commit (ordre reverse)
            cmd = [
                'git', 'log', '--reverse', '-1',
                '--format=%H|%ci|%an|%s', 
                '--', chemin
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True, timeout=30)
            
            if not result.stdout.strip():
                print(f"⚠️  Aucun commit trouvé pour : {chemin}")
                return None
            
            # Parse identique à last_commit
            parts = result.stdout.strip().split('|', 3)
            if len(parts) != 4:
                raise ValueError("Format de sortie Git inattendu")
            
            commit_hash, date_str, author, message = parts
            commit_date = datetime.fromisoformat(date_str.replace(' ', 'T', 1))
            
            return {
                'type': 'first_commit',
                'commit_hash': commit_hash,
                'date': commit_date,
                'author': author,
                'message': message.strip(),
                'path': chemin
            }
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Erreur commande Git : {e.stderr if e.stderr else 'Inconnue'}")
            return None
        except Exception as e:
            print(f"⚠️  Erreur analyse premier commit : {e}")
            return None
    
    def _get_all_commits(self, chemin):
        """
        Récupère l'historique complet des commits pour le chemin.
        """
        try:
            # Limitation à 100 commits pour éviter les sorties trop volumineuses
            cmd = [
                'git', 'log', '--max-count=100',
                '--format=%H|%ci|%an|%s', 
                '--', chemin
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True, timeout=60)
            
            if not result.stdout.strip():
                print(f"⚠️  Aucun commit trouvé pour : {chemin}")
                return None
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split('|', 3)
                if len(parts) != 4:
                    continue
                
                commit_hash, date_str, author, message = parts
                commit_date = datetime.fromisoformat(date_str.replace(' ', 'T', 1))
                
                commits.append({
                    'commit_hash': commit_hash,
                    'date': commit_date,
                    'author': author,
                    'message': message.strip()
                })
            
            return {
                'type': 'all_commits',
                'path': chemin,
                'total_commits': len(commits),
                'commits': commits
            }
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Erreur commande Git : {e.stderr if e.stderr else 'Inconnue'}")
            return None
        except Exception as e:
            print(f"⚠️  Erreur analyse historique complet : {e}")
            return None
    
    def _output_results(self, result, chemin):
        """
        Formate et affiche les résultats selon le format demandé.
        """
        if result is None:
            print(f"📭 Aucun historique Git trouvé pour : {chemin}")
            
            # Créer un fichier de résultats vide
            empty_result = {
                'timestamp': datetime.now().isoformat(),
                'path': chemin,
                'operation': self.args.operation,
                'format_sortie': self.args.format_sortie,
                'git_history': None,
                'formatted_output': None
            }
            
            self._write_json_output(empty_result)
            return
        
        # Formatage de la sortie principale
        if result['type'] in ['last_commit', 'first_commit']:
            date_obj = result['date']
            formatted_date = self._format_date(date_obj)
            
            print(f"📅 Date {result['type'].replace('_', ' ')} : {formatted_date}")
            print(f"👤 Auteur : {result['author']}")
            print(f"🔹 Commit : {result['commit_hash'][:8]}...")
            print(f"💬 Message : {result['message']}")
            
            # Output principal pour les workflows
            main_output = formatted_date
            
        elif result['type'] == 'all_commits':
            print(f"📚 Historique complet : {result['total_commits']} commits")
            
            # Afficher les 3 commits les plus récents
            for i, commit in enumerate(result['commits'][:3]):
                formatted_date = self._format_date(commit['date'])
                print(f"   {i+1}. {formatted_date} - {commit['author']} - {commit['message'][:50]}...")
            
            if result['total_commits'] > 3:
                print(f"   ... et {result['total_commits'] - 3} commits plus anciens")
            
            # Pour all_commits, retourner la date du commit le plus récent
            if result['commits']:
                main_output = self._format_date(result['commits'][0]['date'])
            else:
                main_output = None
        
        # Préparation des résultats complets
        final_result = {
            'timestamp': datetime.now().isoformat(),
            'path': chemin,
            'operation': self.args.operation,
            'format_sortie': self.args.format_sortie,
            'git_history': result,
            'formatted_output': main_output
        }
        
        # Écriture du fichier JSON si demandé
        if self.args.sortie:
            self._write_json_output(final_result)
        
        # Output pour les workflows GitHub Actions (timestamp/date principale)
        if main_output:
            print(f"\n🎯 Output principal : {main_output}")
        
        print(f"✅ Analyse Git terminée")
    
    def _format_date(self, date_obj):
        """
        Formate une date selon le format demandé.
        """
        if self.args.format_sortie == 'timestamp':
            return str(int(date_obj.timestamp()))
        elif self.args.format_sortie == 'iso':
            return date_obj.isoformat()
        elif self.args.format_sortie == 'human':
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return date_obj.isoformat()
    
    def _write_json_output(self, result):
        """
        Écrit les résultats dans un fichier JSON.
        """
        try:
            # Sérialisation custom pour les dates
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.args.sortie, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=json_serializer)
            
            print(f"💾 Résultats sauvegardés : {self.args.sortie}")
            
        except Exception as e:
            print(f"⚠️  Erreur sauvegarde JSON : {e}")


if __name__ == "__main__":
    historien = GitHistorien()
    historien.run()
