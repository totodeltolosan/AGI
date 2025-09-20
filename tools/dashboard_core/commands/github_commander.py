#!/usr/bin/env python3
"""
GITHUB COMMANDER - Module v4.0 conforme AGI
Gestionnaire des commandes GitHub et workflows
Limite: 200 lignes (Délégation fine)
"""

import logging
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class GitHubCommander:
    """Gestionnaire des commandes GitHub et workflows."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.github_commands = {
            'workflow_list': 'gh workflow list',
            'workflow_run': 'gh workflow run',
            'pr_list': 'gh pr list',
            'pr_create': 'gh pr create',
            'issue_list': 'gh issue list', 
            'issue_create': 'gh issue create',
            'repo_status': 'gh repo view',
            'actions_status': 'gh run list'
        }
    
    def execute_github_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Exécute une commande GitHub CLI."""
        try:
            if command not in self.github_commands:
                return {'error': f'Commande non autorisée: {command}'}
            
            # Construction de la commande complète
            base_cmd = self.github_commands[command]
            if args:
                full_cmd = f"{base_cmd} {' '.join(args)}"
            else:
                full_cmd = base_cmd
            
            logger.info(f"Exécution commande GitHub: {full_cmd}")
            
            # Exécution avec timeout
            result = subprocess.run(
                full_cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=self.project_root
            )
            
            return {
                'command': full_cmd,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {'error': 'Timeout - commande interrompue après 30s'}
        except Exception as e:
            logger.error(f"Erreur commande GitHub: {e}")
            return {'error': str(e)}
    
    def list_workflows(self) -> Dict[str, Any]:
        """Liste les workflows GitHub Actions."""
        result = self.execute_github_command('workflow_list')
        
        if result.get('success'):
            workflows = self._parse_workflows(result['stdout'])
            return {'workflows': workflows, 'count': len(workflows)}
        else:
            return {'error': result.get('error', 'Erreur listage workflows')}
    
    def trigger_workflow(self, workflow_name: str, branch: str = 'main') -> Dict[str, Any]:
        """Déclenche un workflow GitHub Actions."""
        args = [workflow_name, '--ref', branch]
        result = self.execute_github_command('workflow_run', args)
        
        if result.get('success'):
            return {'message': f'Workflow {workflow_name} déclenché sur {branch}'}
        else:
            return {'error': f'Échec déclenchement: {result.get("stderr", "Erreur inconnue")}'}
    
    def list_pull_requests(self) -> Dict[str, Any]:
        """Liste les pull requests."""
        result = self.execute_github_command('pr_list', ['--json', 'number,title,state,author'])
        
        if result.get('success'):
            try:
                prs = json.loads(result['stdout'])
                return {'pull_requests': prs, 'count': len(prs)}
            except json.JSONDecodeError:
                return {'error': 'Erreur parsing JSON des PRs'}
        else:
            return {'error': result.get('error', 'Erreur listage PRs')}
    
    def list_issues(self) -> Dict[str, Any]:
        """Liste les issues."""
        result = self.execute_github_command('issue_list', ['--json', 'number,title,state,labels'])
        
        if result.get('success'):
            try:
                issues = json.loads(result['stdout'])
                return {'issues': issues, 'count': len(issues)}
            except json.JSONDecodeError:
                return {'error': 'Erreur parsing JSON des issues'}
        else:
            return {'error': result.get('error', 'Erreur listage issues')}
    
    def create_issue_for_violation(self, file_path: str, violation_details: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une issue pour une violation constitutionnelle."""
        title = f"🚨 Violation constitutionnelle: {file_path}"
        
        body = f"""## Violation Constitutionnelle Détectée

**Fichier:** `{file_path}`
**Lignes:** {violation_details.get('lines', 'N/A')}
**Excès:** +{violation_details.get('excess', 'N/A')} lignes
**Loi violée:** {violation_details.get('law_id', 'COMP-001')}

### Actions Recommandées
- [ ] Refactoriser le fichier en modules plus petits
- [ ] Appliquer le pattern de délégation
- [ ] Respecter la limite constitutionnelle de 200 lignes

### Contexte Automatique
Issue créée automatiquement par le Poste de Commandement AGI v4.0
"""
        
        args = ['--title', f'"{title}"', '--body', f'"{body}"', '--label', 'violation,refactoring']
        result = self.execute_github_command('issue_create', args)
        
        if result.get('success'):
            return {'message': f'Issue créée pour {file_path}'}
        else:
            return {'error': f'Échec création issue: {result.get("stderr", "Erreur")}'}
    
    def get_repository_status(self) -> Dict[str, Any]:
        """Obtient le statut du repository."""
        result = self.execute_github_command('repo_status', ['--json', 'name,description,stargazerCount,forkCount'])
        
        if result.get('success'):
            try:
                repo_info = json.loads(result['stdout'])
                return {'repository': repo_info}
            except json.JSONDecodeError:
                return {'error': 'Erreur parsing info repository'}
        else:
            return {'error': result.get('error', 'Erreur statut repository')}
    
    def get_recent_runs(self) -> Dict[str, Any]:
        """Obtient les runs d'actions récents."""
        result = self.execute_github_command('actions_status', ['--limit', '10', '--json', 'status,conclusion,workflowName,createdAt'])
        
        if result.get('success'):
            try:
                runs = json.loads(result['stdout'])
                return {'runs': runs, 'count': len(runs)}
            except json.JSONDecodeError:
                return {'error': 'Erreur parsing runs'}
        else:
            return {'error': result.get('error', 'Erreur listage runs')}
    
    def _parse_workflows(self, workflow_output: str) -> List[Dict[str, str]]:
        """Parse la sortie des workflows en format structuré."""
        workflows = []
        
        for line in workflow_output.strip().split('\n'):
            if line and '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    workflows.append({
                        'name': parts[0].strip(),
                        'state': parts[1].strip(),
                        'id': parts[2].strip()
                    })
        
        return workflows
    
    def check_github_cli(self) -> bool:
        """Vérifie si GitHub CLI est disponible."""
        try:
            result = subprocess.run(['gh', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def authenticate_github(self) -> Dict[str, Any]:
        """Vérifie l'authentification GitHub."""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, timeout=10)
            return {
                'authenticated': result.returncode == 0,
                'status': result.stdout + result.stderr
            }
        except Exception as e:
            return {'authenticated': False, 'error': str(e)}
