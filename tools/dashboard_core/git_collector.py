#!/usr/bin/env python3
"""
GIT DATA COLLECTOR - Module délégué conforme AGI
Collecte des données Git (status, commits, hotspots)
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class GitDataCollector:
    """Collecteur spécialisé pour les données Git."""
    
    def __init__(self, project_root: Path):
        """Initialise le collecteur avec le répertoire racine."""
        self.project_root = project_root
    
    def collect_git_status(self) -> Dict[str, Any]:
        """Collecte l'état du travail local via Git."""
        try:
            import git
            repo = git.Repo(self.project_root)
            
            # État des modifications
            modified_files = len(repo.index.diff(None))
            untracked_files = len(repo.untracked_files)
            has_changes = modified_files > 0 or untracked_files > 0
            
            status_text = "⚠️ Modifications locales" if has_changes else "✅ À jour"
            
            return {
                "status_text": status_text,
                "modified_files": modified_files,
                "untracked_files": untracked_files,
                "has_changes": has_changes
            }
            
        except Exception as e:
            logger.error(f"Erreur Git status: {e}")
            return self._get_error_fallback(f"Erreur Git: {str(e)}")
    
    def collect_hot_spots(self) -> List[Tuple[str, int]]:
        """Collecte les points chauds (fichiers les plus modifiés) des 7 derniers jours."""
        try:
            import git
            repo = git.Repo(self.project_root)
            
            # Date limite (7 jours)
            since_date = datetime.now() - timedelta(days=7)
            
            # Comptage des modifications par fichier
            file_changes = {}
            
            for commit in repo.iter_commits(since=since_date):
                for file_path in commit.stats.files:
                    if file_path.endswith('.py'):  # Focus sur les fichiers Python
                        file_changes[file_path] = file_changes.get(file_path, 0) + 1
            
            # Top 3 des fichiers les plus modifiés
            hot_spots = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return hot_spots if hot_spots else [("Aucun fichier modifié", 0)]
            
        except Exception as e:
            logger.error(f"Erreur calcul hot spots: {e}")
            return [("Erreur Git", 0)]
    
    def collect_recent_activity(self) -> List[Dict[str, Any]]:
        """Collecte les 5 derniers commits."""
        try:
            import git
            repo = git.Repo(self.project_root)
            
            recent_commits = []
            
            for commit in list(repo.iter_commits(max_count=5)):
                commit_info = {
                    "hash": commit.hexsha[:8],
                    "author": commit.author.name,
                    "message": commit.message.split('\n')[0][:60],  # Première ligne, max 60 chars
                    "date": commit.committed_datetime.strftime("%d/%m %H:%M"),
                    "is_auto_corrector": "Constitutional Auto-Corrector" in commit.message
                }
                recent_commits.append(commit_info)
            
            return recent_commits if recent_commits else self._get_empty_commits()
            
        except Exception as e:
            logger.error(f"Erreur activité récente: {e}")
            return [self._get_error_commit(str(e))]
    
    def _get_error_fallback(self, error_message: str) -> Dict[str, Any]:
        """Retourne une structure d'erreur pour le status Git."""
        return {
            "error": error_message,
            "status_text": "❌ Erreur Git",
            "modified_files": 0,
            "untracked_files": 0,
            "has_changes": False
        }
    
    def _get_empty_commits(self) -> List[Dict[str, Any]]:
        """Retourne une liste de commits vide."""
        return [{"hash": "N/A", "author": "System", "message": "Aucun commit trouvé", "date": "N/A", "is_auto_corrector": False}]
    
    def _get_error_commit(self, error_msg: str) -> Dict[str, Any]:
        """Retourne un commit d'erreur."""
        return {"hash": "ERROR", "author": "System", "message": f"Erreur Git: {error_msg}", "date": "N/A", "is_auto_corrector": False}
