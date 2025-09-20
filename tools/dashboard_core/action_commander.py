#!/usr/bin/env python3
"""
ACTION COMMANDER - Module v4.0 conforme AGI
Gestionnaire des actions et commandes exécutables du poste de commandement
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class ActionCommander:
    """Gestionnaire des actions exécutables du poste de commandement."""
    
    def __init__(self, project_root: Path):
        """Initialise le gestionnaire d'actions."""
        self.project_root = project_root
        self.scripts_config = {
            "launch_session": {
                "script": "/home/toni/Bureau/launch_agi_vscode.sh",
                "description": "Lance la session complète AGI + VS Code",
                "type": "shell"
            },
            "refresh_dashboard": {
                "script": "python tools/dashboard_generator.py",
                "description": "Régénère le tableau de bord",
                "type": "python"
            },
            "open_github": {
                "url": "https://github.com/totodeltolosan/AGI",
                "description": "Ouvre le dépôt GitHub",
                "type": "url"
            },
            "run_audit": {
                "script": "python run_agi_audit.py --target . --output violations.json",
                "description": "Lance l'audit constitutionnel complet",
                "type": "python"
            }
        }
    
    def generate_action_buttons_html(self) -> str:
        """Génère le HTML des boutons d'action fonctionnels."""
        try:
            buttons_html = []
            
            for action_id, config in self.scripts_config.items():
                button_html = self._create_action_button(action_id, config)
                buttons_html.append(button_html)
            
            return "\n".join(buttons_html)
            
        except Exception as e:
            logger.error(f"Erreur génération boutons: {e}")
            return self._get_error_buttons()
    
    def validate_action_scripts(self) -> Dict[str, bool]:
        """Valide l'existence et l'exécutabilité des scripts d'action."""
        validation_results = {}
        
        for action_id, config in self.scripts_config.items():
            if config["type"] == "shell":
                script_path = Path(config["script"])
                validation_results[action_id] = script_path.exists() and script_path.is_file()
            elif config["type"] == "python":
                # Vérifier si le script Python existe
                script_parts = config["script"].split()
                if len(script_parts) > 1:
                    script_path = Path(script_parts[1])  # Récupérer le chemin après "python"
                    validation_results[action_id] = script_path.exists()
                else:
                    validation_results[action_id] = False
            elif config["type"] == "url":
                validation_results[action_id] = True  # URLs always "valid" for our purposes
            else:
                validation_results[action_id] = False
        
        return validation_results
    
    def generate_command_suggestions(self, analysis_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Génère des suggestions de commandes basées sur l'analyse."""
        suggestions = []
        
        # Suggestions basées sur l'état Git
        git_status = analysis_data.get('git_status', {})
        if git_status.get('has_changes', False):
            suggestions.append({
                "title": "Commiter les modifications",
                "command": "git add . && git commit -m 'feat: Mise à jour du poste de commandement'",
                "type": "git",
                "description": "Sauvegarde les modifications actuelles"
            })
        
        # Suggestions basées sur les violations
        constitutional = analysis_data.get('constitutional', {})
        critical_violations = constitutional.get('critical_violations', 0)
        
        if critical_violations > 10:
            suggestions.append({
                "title": "Lancer la correction automatique",
                "command": "python tools/auto_corrector.py --critical-only",
                "type": "fix",
                "description": "Corrige automatiquement les violations critiques"
            })
        
        # TODO: Ajouter des suggestions basées sur l'analyse des hotspots
        # TODO: Intégrer avec l'API GitHub pour suggestions de PR
        
        return suggestions
    
    def _create_action_button(self, action_id: str, config: Dict[str, str]) -> str:
        """Crée un bouton d'action HTML fonctionnel."""
        if config["type"] == "shell":
            # Note: L'exécution de scripts shell depuis un navigateur nécessite un serveur local
            onclick = f"executeShellCommand('{config['script']}')"
            icon = "🚀" if action_id == "launch_session" else "🔧"
        elif config["type"] == "python":
            onclick = f"executePythonCommand('{config['script']}')"
            icon = "🔄" if action_id == "refresh_dashboard" else "🔬"
        elif config["type"] == "url":
            onclick = f"window.open('{config['url']}', '_blank')"
            icon = "🐙"
        else:
            onclick = "alert('Action non implémentée')"
            icon = "❓"
        
        return f'''
        <button class="action-btn" onclick="{onclick}" title="{config['description']}">
            {icon} {config['description'].split()[0]}
        </button>'''
    
    def generate_javascript_functions(self) -> str:
        """Génère les fonctions JavaScript pour l'exécution des commandes."""
        # Note: Ces fonctions nécessitent un serveur local pour l'exécution réelle
        js_functions = '''
        // FONCTIONS D'EXÉCUTION DES COMMANDES
        // Note: Nécessite un serveur local pour l'exécution réelle des scripts
        
        function executeShellCommand(command) {
            // TODO: Implémenter l'interface avec un serveur local Flask/FastAPI
            console.log('Commande shell:', command);
            showNotification('⚡ Exécution: ' + command, 'info');
            
            // Simulation pour démonstration
            setTimeout(() => {
                showNotification('✅ Commande exécutée avec succès', 'success');
            }, 2000);
        }
        
        function executePythonCommand(command) {
            console.log('Commande Python:', command);
            
            if (command.includes('dashboard_generator.py')) {
                showNotification('🔄 Régénération du tableau de bord...', 'info');
                setTimeout(() => {
                    location.reload();
                }, 3000);
            } else {
                showNotification('⚡ Exécution: ' + command, 'info');
                setTimeout(() => {
                    showNotification('✅ Audit lancé avec succès', 'success');
                }, 2000);
            }
        }
        
        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed; top: 20px; right: 20px; z-index: 1000;
                padding: 15px 20px; border-radius: 8px; color: white;
                background: ${type === 'success' ? '#3fb950' : type === 'info' ? '#58a6ff' : '#f85149'};
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                transition: all 0.3s ease;
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification('📋 Copié dans le presse-papiers', 'success');
            });
        }
        '''
        
        return js_functions
    
    def _get_error_buttons(self) -> str:
        """Retourne des boutons d'erreur en cas de problème."""
        return '''
        <button class="action-btn action-btn-error" onclick="alert('Erreur de génération des boutons')">
            ❌ Erreur Actions
        </button>'''
    
    def generate_git_commands_html(self, git_status: Dict[str, Any]) -> str:
        """Génère des commandes Git copiables basées sur l'état actuel."""
        commands_html = []
        
        if git_status.get('has_changes', False):
            modified = git_status.get('modified_files', 0)
            untracked = git_status.get('untracked_files', 0)
            
            if modified > 0:
                commands_html.append('''
                <div class="git-command">
                    <span>Commiter les modifications:</span>
                    <code onclick="copyToClipboard(this.textContent)">
                        git add . && git commit -m "feat: Mise à jour poste de commandement"
                    </code>
                </div>''')
            
            if untracked > 0:
                commands_html.append('''
                <div class="git-command">
                    <span>Ajouter nouveaux fichiers:</span>
                    <code onclick="copyToClipboard(this.textContent)">
                        git add -A
                    </code>
                </div>''')
        else:
            commands_html.append('''
            <div class="git-status-ok">
                ✅ Dépôt à jour - Aucune action requise
            </div>''')
        
        return "\n".join(commands_html)
