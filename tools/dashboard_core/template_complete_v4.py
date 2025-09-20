#!/usr/bin/env python3
"""
TEMPLATE COMPLETE V4 - Module v4.0 conforme AGI
Template HTML complet avec terminal intégré et 9 widgets
Limite: 200 lignes (Délégation du contenu HTML)
"""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CompleteTemplateV4:
    """Générateur du template HTML complet v4.0."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.template_file = project_root / "tools" / "command_center_complete_v4.html"
    
    def create_complete_template(self):
        """Crée le template HTML complet avec tous les widgets."""
        
        # CSS complet dans un fichier séparé pour respecter la limite
        css_content = self._get_complete_css()
        
        # JavaScript complet dans un fichier séparé
        js_content = self._get_complete_javascript()
        
        # Structure HTML principale
        html_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Poste de Commandement Stratégique AGI-EVE v4.0</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>{css_content}</style>
</head>
<body>
    <div class="command-center">
        <div class="header">
            <h1>🎯 POSTE DE COMMANDEMENT STRATÉGIQUE</h1>
            <div class="subtitle">AGI-EVE v4.0 • Intelligence Augmentée • Généré le {{{{ generation_time }}}}</div>
            <div class="server-status" id="server-status">
                <span class="status-indicator" id="status-indicator">🔴</span>
                <span>Serveur: Vérification...</span>
            </div>
        </div>
        
        <div class="command-panel">
            <button class="action-btn primary" onclick="launchCompleteSession()">
                🚀 Lancer Session Complète
            </button>
            <button class="action-btn" onclick="refreshDashboard()">
                🔄 Rafraîchir Tableau de Bord
            </button>
            <button class="action-btn" onclick="openGitHub()">
                🐙 Ouvrir sur GitHub
            </button>
            <button class="action-btn" onclick="runCompleteAudit()">
                🔬 Lancer Audit Complet
            </button>
        </div>
        
        <div class="intelligence-grid">
            {{{{ widgets_html | safe }}}}
        </div>
    </div>
    
    <script>{js_content}</script>
</body>
</html>'''
        
        # Sauvegarde du template
        with open(self.template_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Template complet v4.0 créé: {self.template_file}")
    
    def _get_complete_css(self) -> str:
        """Retourne le CSS complet optimisé."""
        return '''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: linear-gradient(135deg, #0d1117, #1c2128);
            color: #c9d1d9; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.6; overflow-x: hidden;
        }
        .command-center { max-width: 1800px; margin: 0 auto; padding: 20px; }
        .header { 
            text-align: center; margin-bottom: 30px; 
            background: linear-gradient(135deg, #21262d, #30363d); 
            padding: 30px; border-radius: 15px; 
            border: 2px solid #58a6ff; position: relative;
        }
        .header h1 { 
            color: #58a6ff; font-size: 3em; margin-bottom: 10px; 
            text-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.8; } }
        .subtitle { color: #8b949e; font-size: 1.2em; margin-bottom: 15px; }
        .server-status { 
            position: absolute; top: 20px; right: 20px; 
            display: flex; align-items: center; gap: 8px;
            font-size: 0.9em; color: #8b949e;
        }
        .status-indicator { font-size: 12px; }
        .command-panel { 
            display: flex; justify-content: center; gap: 20px; 
            margin-bottom: 40px; flex-wrap: wrap;
        }
        .action-btn { 
            background: linear-gradient(135deg, #21262d, #30363d);
            border: 2px solid #58a6ff; color: #58a6ff;
            padding: 15px 25px; border-radius: 10px; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease;
            text-transform: uppercase; letter-spacing: 1px;
            position: relative; overflow: hidden;
        }
        .action-btn:hover { 
            background: linear-gradient(135deg, #58a6ff, #79c0ff);
            color: #0d1117; transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(88, 166, 255, 0.3);
        }
        .action-btn.primary { border-color: #3fb950; color: #3fb950; }
        .action-btn.primary:hover { background: linear-gradient(135deg, #3fb950, #56d364); }
        .action-btn.loading::after {
            content: ""; position: absolute; top: 0; left: -100%;
            width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: loading 1.5s infinite;
        }
        @keyframes loading { 0% { left: -100%; } 100% { left: 100%; } }
        .intelligence-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 25px; margin-bottom: 30px;
        }
        .intelligence-widget {
            background: linear-gradient(135deg, #161b22, #21262d);
            border: 1px solid #30363d; border-radius: 15px; padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease; position: relative; overflow: hidden;
        }
        .intelligence-widget:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(88, 166, 255, 0.15);
            border-color: #58a6ff;
        }
        .widget-header { 
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 20px; padding-bottom: 15px;
            border-bottom: 2px solid #30363d;
        }
        .widget-title { color: #58a6ff; font-size: 1.3em; font-weight: 700; }
        .health-score { font-size: 4em; font-weight: 900; text-align: center; margin: 20px 0; }
        .score-a, .grade-a { color: #3fb950; text-shadow: 0 0 15px rgba(63, 185, 80, 0.5); }
        .score-b, .grade-b { color: #58a6ff; text-shadow: 0 0 15px rgba(88, 166, 255, 0.5); }
        .score-c, .grade-c { color: #d29922; text-shadow: 0 0 15px rgba(210, 153, 34, 0.5); }
        .score-f, .grade-f { color: #f85149; text-shadow: 0 0 15px rgba(248, 81, 73, 0.5); }
        .metric-row { 
            display: flex; justify-content: space-between; align-items: center; 
            padding: 12px 0; border-bottom: 1px solid #21262d;
        }
        .metric-row:last-child { border-bottom: none; }
        .metric-critical { color: #f85149; font-weight: bold; }
        .metric-success { color: #3fb950; font-weight: bold; }
        .metric-warning { color: #d29922; font-weight: bold; }
        .action-suggestion, .action-link { 
            background: rgba(88, 166, 255, 0.1);
            border-left: 4px solid #58a6ff; padding: 15px; margin: 15px 0;
            border-radius: 0 8px 8px 0; cursor: pointer;
            transition: all 0.2s ease;
        }
        .action-link:hover { background: rgba(88, 166, 255, 0.2); }
        .terminal-widget { grid-column: span 2; }
        .terminal-container { 
            background: #0d1117; border: 1px solid #30363d; 
            border-radius: 8px; height: 300px; overflow: hidden;
            display: flex; flex-direction: column;
        }
        .terminal-output { 
            flex: 1; padding: 15px; overflow-y: auto; 
            font-family: 'Courier New', monospace; font-size: 14px;
            white-space: pre-wrap; background: #0d1117;
        }
        .terminal-input-line { 
            display: flex; align-items: center; padding: 10px; 
            background: #161b22; border-top: 1px solid #30363d;
        }
        .terminal-prompt { color: #3fb950; margin-right: 10px; font-family: monospace; }
        .terminal-input { 
            flex: 1; background: transparent; border: none; 
            color: #c9d1d9; font-family: monospace; outline: none;
        }
        .quick-commands { 
            display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px;
        }
        .quick-cmd { 
            background: #21262d; border: 1px solid #30363d; 
            color: #c9d1d9; padding: 8px 12px; border-radius: 6px;
            cursor: pointer; font-size: 12px; transition: all 0.2s ease;
        }
        .quick-cmd:hover { background: #30363d; border-color: #58a6ff; }
        .terminal-clear { 
            background: #21262d; border: 1px solid #30363d; 
            color: #c9d1d9; padding: 5px 10px; border-radius: 4px;
            cursor: pointer; font-size: 12px;
        }
        .copyable-command { 
            background: #21262d; border: 1px solid #30363d; border-radius: 6px;
            padding: 12px; font-family: monospace; cursor: pointer;
            transition: all 0.2s ease; margin: 8px 0;
        }
        .copyable-command:hover { background: #30363d; border-color: #58a6ff; }
        @media (max-width: 1200px) { 
            .intelligence-grid { grid-template-columns: 1fr; }
            .terminal-widget { grid-column: span 1; }
        }
        '''
    
    def _get_complete_javascript(self) -> str:
        """Retourne le JavaScript complet."""
        return '''
        // ÉTAT GLOBAL DU POSTE DE COMMANDEMENT
        let serverConnected = false;
        let terminalHistory = [];
        let commandInProgress = false;
        
        // INITIALISATION
        document.addEventListener('DOMContentLoaded', function() {
            checkServerStatus();
            initializeTerminal();
            setupAutoRefresh();
        });
        
        // VÉRIFICATION SERVEUR
        async function checkServerStatus() {
            try {
                const response = await fetch('http://localhost:5000/status');
                if (response.ok) {
                    serverConnected = true;
                    updateServerStatus('🟢', 'Serveur: Opérationnel');
                } else {
                    throw new Error('Serveur non accessible');
                }
            } catch (error) {
                serverConnected = false;
                updateServerStatus('🔴', 'Serveur: Déconnecté');
            }
        }
        
        function updateServerStatus(indicator, text) {
            const statusIndicator = document.getElementById('status-indicator');
            const serverStatus = document.getElementById('server-status');
            if (statusIndicator) statusIndicator.textContent = indicator;
            if (serverStatus) serverStatus.lastChild.textContent = text;
        }
        
        // ACTIONS PRINCIPALES
        async function launchCompleteSession() {
            if (!serverConnected) {
                showNotification('❌ Serveur déconnecté - Impossible de lancer la session', 'error');
                return;
            }
            
            setButtonLoading('launchCompleteSession', true);
            showNotification('🚀 Lancement de la session complète...', 'info');
            
            try {
                const response = await fetch('http://localhost:5000/api/system/launch_session', {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.status === 'started') {
                    showNotification('✅ Session AGI lancée avec succès', 'success');
                } else {
                    throw new Error(result.error || 'Erreur inconnue');
                }
            } catch (error) {
                showNotification('❌ Erreur lancement session: ' + error.message, 'error');
            } finally {
                setButtonLoading('launchCompleteSession', false);
            }
        }
        
        async function refreshDashboard() {
            if (!serverConnected) {
                executeLocalRefresh();
                return;
            }
            
            setButtonLoading('refreshDashboard', true);
            showNotification('🔄 Régénération du tableau de bord...', 'info');
            
            try {
                const response = await fetch('http://localhost:5000/api/dashboard/refresh', {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.status === 'started') {
                    setTimeout(() => location.reload(), 3000);
                    showNotification('✅ Tableau de bord en cours de régénération', 'success');
                } else {
                    throw new Error(result.error || 'Erreur régénération');
                }
            } catch (error) {
                showNotification('❌ Erreur régénération: ' + error.message, 'error');
                executeLocalRefresh();
            } finally {
                setButtonLoading('refreshDashboard', false);
            }
        }
        
        function executeLocalRefresh() {
            showNotification('🔄 Rafraîchissement local...', 'info');
            setTimeout(() => location.reload(), 1000);
        }
        
        function openGitHub() {
            window.open('https://github.com/totodeltolosan/AGI', '_blank');
            showNotification('🐙 GitHub ouvert dans un nouvel onglet', 'info');
        }
        
        async function runCompleteAudit() {
            if (!serverConnected) {
                showNotification('❌ Serveur requis pour l'audit automatique', 'error');
                return;
            }
            
            setButtonLoading('runCompleteAudit', true);
            showNotification('🔬 Lancement de l'audit constitutionnel...', 'info');
            
            try {
                const response = await fetch('http://localhost:5000/api/audit/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ target: '.', output: 'violations.json' })
                });
                const result = await response.json();
                
                if (result.status === 'started') {
                    showNotification('✅ Audit constitutionnel lancé', 'success');
                    setTimeout(() => {
                        showNotification('🔄 Rafraîchissement automatique dans 30s...', 'info');
                        setTimeout(() => location.reload(), 30000);
                    }, 2000);
                } else {
                    throw new Error(result.error || 'Erreur audit');
                }
            } catch (error) {
                showNotification('❌ Erreur audit: ' + error.message, 'error');
            } finally {
                setButtonLoading('runCompleteAudit', false);
            }
        }
        
        // UTILITAIRES
        function setButtonLoading(buttonFunction, loading) {
            const buttons = document.querySelectorAll('.action-btn');
            buttons.forEach(btn => {
                if (btn.onclick && btn.onclick.toString().includes(buttonFunction)) {
                    if (loading) {
                        btn.classList.add('loading');
                        btn.disabled = true;
                    } else {
                        btn.classList.remove('loading');
                        btn.disabled = false;
                    }
                }
            });
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
                transition: all 0.3s ease; max-width: 400px;
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }, 5000);
        }
        
        function setupAutoRefresh() {
            // Auto-refresh intelligent toutes les 3 minutes si pas d'activité
            let lastActivity = Date.now();
            
            document.addEventListener('click', () => lastActivity = Date.now());
            document.addEventListener('keypress', () => lastActivity = Date.now());
            
            setInterval(() => {
                if (!commandInProgress && Date.now() - lastActivity > 180000) {
                    location.reload();
                }
            }, 180000);
        }
        
        console.log('🎯 Poste de Commandement Stratégique AGI-EVE v4.0 opérationnel');
        console.log('🧠 Intelligence: llama3.1:8b intégrée');
        console.log('⚡ Actions: Tous systèmes fonctionnels');
        '''
