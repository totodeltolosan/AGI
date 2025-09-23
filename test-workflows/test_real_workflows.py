#!/usr/bin/env python3
"""
🎯 AGI Real Workflows Tester - Tests RÉELS GitHub Actions
========================================================
Déclenche et surveille de vrais workflows GitHub Actions
"""

import subprocess
import json
import time
from rich.console import Console

console = Console()

class RealWorkflowTester:
    def __init__(self):
        self.repo = self._get_repo_info()
    
    def _get_repo_info(self):
        """Récupère les infos du repo GitHub"""
        try:
            result = subprocess.run(['gh', 'repo', 'view', '--json', 'owner,name'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                console.print("❌ [red]GitHub CLI non configuré ou erreur repo[/red]")
                return None
        except FileNotFoundError:
            console.print("❌ [red]GitHub CLI (gh) non installé[/red]")
            return None
    
    def trigger_workflow(self, workflow_file: str, inputs: dict = None):
        """Déclenche un workflow réel via GitHub API"""
        if not self.repo:
            return False
            
        console.print(f"🚀 [blue]Déclenchement: {workflow_file}[/blue]")
        
        cmd = ['gh', 'workflow', 'run', workflow_file]
        
        if inputs:
            for key, value in inputs.items():
                cmd.extend(['-f', f'{key}={value}'])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                console.print("✅ [green]Workflow déclenché[/green]")
                return True
            else:
                console.print(f"❌ [red]Erreur: {result.stderr}[/red]")
                return False
        except Exception as e:
            console.print(f"❌ [red]Exception: {e}[/red]")
            return False
    
    def test_simple_workflow(self):
        """Test d'un workflow simple comme démo"""
        # Tester le scanner de fichiers (simple et sûr)
        success = self.trigger_workflow('06-01-scanner-fichiers.yml', {
            'pattern': '*.py',
            'chemin_racine': '.',
            'exclusions': '[]'
        })
        
        if success:
            console.print("🕐 [yellow]Attendez 30s puis vérifiez GitHub Actions...[/yellow]")
            time.sleep(30)
            
            # Vérifier les runs récents
            self.check_recent_runs()
    
    def check_recent_runs(self):
        """Vérifier les exécutions récentes"""
        try:
            result = subprocess.run(['gh', 'run', 'list', '--limit', '5'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                console.print("📊 [blue]Exécutions récentes:[/blue]")
                console.print(result.stdout)
            else:
                console.print("❌ Impossible de récupérer les runs")
        except Exception as e:
            console.print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    tester = RealWorkflowTester()
    if tester.repo:
        console.print(f"🏠 Repository: {tester.repo['owner']['login']}/{tester.repo['name']}")
        tester.test_simple_workflow()
    else:
        console.print("❌ Configuration GitHub CLI requise")
