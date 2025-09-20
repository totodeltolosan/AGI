#!/usr/bin/env python3
"""
WIDGET MANAGER - Module v4.0 conforme AGI
Gestionnaire des 9 widgets du poste de commandement
Limite: 200 lignes (Délégation fine)
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class WidgetManager:
    """Gestionnaire des widgets du poste de commandement."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.widgets_config = {
            'constitutional_health': {'title': '⚖️ État Constitutionnel', 'priority': 1},
            'health_score': {'title': '🏆 Score de Santé Global', 'priority': 2},
            'git_status': {'title': '💻 État du Travail Local', 'priority': 3},
            'strategic_violations': {'title': '🚨 Analyse Stratégique des Violations', 'priority': 4},
            'recent_activity': {'title': '📈 Activité Récente & Robot', 'priority': 5},
            'trend_analysis': {'title': '📊 Tendance Constitutionnelle', 'priority': 6},
            'code_exploitation': {'title': '🔬 Analyse d\'Exploitation', 'priority': 7},
            'ai_recommendations': {'title': '🧠 Recommandations IA', 'priority': 8},
            'command_terminal': {'title': '⚡ Terminal de Commande', 'priority': 9}
        }
    
    def generate_all_widgets(self, data_context: Dict[str, Any]) -> Dict[str, str]:
        """Génère tous les widgets avec leurs données."""
        widgets_html = {}
        
        try:
            # Widget 1: État Constitutionnel
            widgets_html['constitutional_health'] = self._create_constitutional_widget(
                data_context.get('constitutional', {})
            )
            
            # Widget 2: Score de Santé
            widgets_html['health_score'] = self._create_health_score_widget(
                data_context.get('health_score', {})
            )
            
            # Widget 3: État Git
            widgets_html['git_status'] = self._create_git_status_widget(
                data_context.get('git_status', {})
            )
            
            # Widget 4: Violations Stratégiques
            widgets_html['strategic_violations'] = self._create_strategic_violations_widget(
                data_context.get('violations_analysis', {})
            )
            
            # Widget 5: Activité Récente
            widgets_html['recent_activity'] = self._create_activity_widget(
                data_context.get('recent_activity', [])
            )
            
            # Widget 6: Tendances
            widgets_html['trend_analysis'] = self._create_trend_widget(
                data_context.get('trends', {})
            )
            
            # Widget 7: Exploitation du Code
            widgets_html['code_exploitation'] = self._create_exploitation_widget(
                data_context.get('code_metrics', {})
            )
            
            # Widget 8: Recommandations IA
            widgets_html['ai_recommendations'] = self._create_ai_recommendations_widget(
                data_context.get('ai_insights', {})
            )
            
            # Widget 9: Terminal de Commande
            widgets_html['command_terminal'] = self._create_command_terminal_widget()
            
            return widgets_html
            
        except Exception as e:
            logger.error(f"Erreur génération widgets: {e}")
            return self._get_error_widgets()
    
    def _create_constitutional_widget(self, data: Dict[str, Any]) -> str:
        """Crée le widget d'état constitutionnel."""
        critical = data.get('critical_violations', 0)
        total = data.get('total_violations', 0)
        compliance = data.get('compliance_rate', 0)
        
        # Score de santé constitutionnelle
        if critical == 0 and total < 10:
            grade, diagnosis = 'A+', '🏆 Excellence Constitutionnelle'
        elif critical < 5:
            grade, diagnosis = 'B', '🟢 Bonne Santé Constitutionnelle'
        elif critical < 15:
            grade, diagnosis = 'C', '🟡 Dette Technique Modérée'
        else:
            grade, diagnosis = 'F', '🚨 URGENCE CONSTITUTIONNELLE'
        
        return f'''
        <div class="intelligence-widget">
            <div class="widget-header">
                <div class="widget-title">⚖️ État Constitutionnel</div>
                <div class="health-grade grade-{grade.lower()}">{grade}</div>
            </div>
            <div class="metric-row">
                <span>Violations Critiques:</span>
                <span class="metric-critical">{critical}</span>
            </div>
            <div class="metric-row">
                <span>Total Violations:</span>
                <span>{total}</span>
            </div>
            <div class="metric-row">
                <span>Taux de Conformité:</span>
                <span class="metric-success">{compliance}%</span>
            </div>
            <div class="diagnosis">{diagnosis}</div>
            <div class="action-suggestion">
                <button class="action-link" onclick="executeCommand('audit_critical')">
                    🔍 Voir les 5 violations les plus critiques
                </button>
            </div>
        </div>'''
    
    def _create_health_score_widget(self, data: Dict[str, Any]) -> str:
        """Crée le widget de score de santé global."""
        grade = data.get('grade', 'C')
        score = data.get('overall_score', 70)
        diagnosis = data.get('diagnosis', 'Analyse en cours')
        recommendations = data.get('recommendations', [])
        
        return f'''
        <div class="intelligence-widget">
            <div class="widget-header">
                <div class="widget-title">🏆 Score de Santé Global</div>
            </div>
            <div class="health-score score-{grade.lower()}">{grade}</div>
            <div class="score-percentage">{score}%</div>
            <div class="diagnosis">{diagnosis}</div>
            <div class="recommendations">
                <strong>Actions Prioritaires:</strong>
                {"".join([f"<div class='recommendation-item'>• {rec}</div>" for rec in recommendations[:3]])}
            </div>
        </div>'''
    
    def _create_git_status_widget(self, data: Dict[str, Any]) -> str:
        """Crée le widget d'état Git."""
        status_text = data.get('status_text', 'Inconnu')
        modified = data.get('modified_files', 0)
        untracked = data.get('untracked_files', 0)
        has_changes = data.get('has_changes', False)
        
        git_commands = ""
        if has_changes:
            git_commands = '''
            <div class="git-commands">
                <div class="copyable-command" onclick="copyToClipboard('git add . && git commit -m \\"feat: Mise à jour poste de commandement\\"')">
                    📝 git commit -m "feat: Mise à jour"
                </div>
            </div>'''
        
        return f'''
        <div class="intelligence-widget">
            <div class="widget-header">
                <div class="widget-title">💻 État du Travail Local</div>
            </div>
            <div class="git-status">{status_text}</div>
            <div class="metric-row">
                <span>Fichiers modifiés:</span>
                <span>{modified}</span>
            </div>
            <div class="metric-row">
                <span>Non suivis:</span>
                <span>{untracked}</span>
            </div>
            {git_commands}
        </div>'''
    
    def _create_strategic_violations_widget(self, data: Dict[str, Any]) -> str:
        """Crée le widget d'analyse stratégique des violations."""
        top_laws = data.get('top_violated_laws', [])
        top_files = data.get('top_problematic_files', [])
        
        laws_html = "".join([
            f'<div class="violation-item"><span>{law}</span><span class="count">{count}</span></div>'
            for law, count in top_laws[:3]
        ])
        
        files_html = "".join([
            f'''<div class="file-violation">
                <span class="file-name">{file}</span>
                <button class="auto-correct-btn" onclick="executeCommand('fix_file', '{file}')">
                    🔧 Auto-corriger
                </button>
            </div>'''
            for file, data in top_files[:3]
        ])
        
        return f'''
        <div class="intelligence-widget">
            <div class="widget-header">
                <div class="widget-title">🚨 Analyse Stratégique des Violations</div>
            </div>
            <div class="violations-section">
                <h4>Top 3 Lois Violées:</h4>
                {laws_html}
            </div>
            <div class="files-section">
                <h4>Fichiers Critiques:</h4>
                {files_html}
            </div>
        </div>'''
    
    def _create_command_terminal_widget(self) -> str:
        """Crée le widget terminal de commande intégré."""
        return '''
        <div class="intelligence-widget terminal-widget">
            <div class="widget-header">
                <div class="widget-title">⚡ Terminal de Commande</div>
                <button class="terminal-clear" onclick="clearTerminal()">🗑️ Clear</button>
            </div>
            <div class="terminal-container">
                <div id="terminal-output" class="terminal-output"></div>
                <div class="terminal-input-line">
                    <span class="terminal-prompt">agi@command:~$</span>
                    <input type="text" id="terminal-input" class="terminal-input" 
                           placeholder="Tapez une commande..." 
                           onkeypress="handleTerminalInput(event)">
                </div>
            </div>
            <div class="quick-commands">
                <button class="quick-cmd" onclick="executeQuickCommand('gh workflow list')">📋 Workflows</button>
                <button class="quick-cmd" onclick="executeQuickCommand('gh pr list')">🔄 Pull Requests</button>
                <button class="quick-cmd" onclick="executeQuickCommand('gh issue list')">🐛 Issues</button>
                <button class="quick-cmd" onclick="executeQuickCommand('git status')">📊 Git Status</button>
            </div>
        </div>'''
    
    def _create_activity_widget(self, activities: List[Dict]) -> str:
        """Crée le widget d'activité récente."""
        activities_html = "".join([
            f'''<div class="activity-item {'robot-activity' if activity.get('is_auto_corrector') else ''}">
                <div class="activity-hash">{activity.get('hash', 'N/A')}</div>
                <div class="activity-message">{activity.get('message', 'N/A')}</div>
                <div class="activity-meta">{activity.get('author', 'Unknown')} • {activity.get('date', 'N/A')}</div>
            </div>'''
            for activity in activities[:5]
        ])
        
        return f'''
        <div class="intelligence-widget">
            <div class="widget-header">
                <div class="widget-title">📈 Activité Récente & Robot</div>
            </div>
            {activities_html}
            <div class="robot-stats">
                <div class="metric-row">
                    <span>Commits Robot (24h):</span>
                    <span>En cours d'implémentation</span>
                </div>
            </div>
        </div>'''
    
    def _create_trend_widget(self, data: Dict[str, Any]) -> str:
        """Crée le widget de tendance."""
        return '''
        <div class="intelligence-widget">
            <div class="widget-header">
                <div class="widget-title">📊 Tendance Constitutionnelle</div>
            </div>
            <div class="trend-chart" id="trend-chart">
                <div class="chart-placeholder">Graphique en cours de génération...</div>
            </div>
            <div class="trend-verdict">
                <span>Tendance: Stabilité maintenue</span>
            </div>
        </div>'''
    
    def _create_exploitation_widget(self, data: Dict[str, Any]) -> str:
        """Crée le widget d'analyse d'exploitation."""
        return '''
        <div class="intelligence-widget">
            <div class="widget-header">
                <div class="widget-title">🔬 Analyse d'Exploitation</div>
            </div>
            <div class="exploitation-status">
                <div class="metric-row">
                    <span>Couverture Tests:</span>
                    <span class="status-pending">En attente coverage.py</span>
                </div>
                <div class="metric-row">
                    <span>Complexité:</span>
                    <span class="status-pending">En attente radon</span>
                </div>
            </div>
            <div class="action-suggestion">
                <button class="action-link" onclick="executeCommand('generate_coverage')">
                    📊 Générer rapport de couverture
                </button>
            </div>
        </div>'''
    
    def _create_ai_recommendations_widget(self, data: Dict[str, Any]) -> str:
        """Crée le widget de recommandations IA."""
        recommendations = data.get('priority_actions', ['Surveillance continue'])
        risk = data.get('risk_assessment', 'MODÉRÉ')
        
        recs_html = "".join([
            f'<div class="ai-recommendation">• {rec}</div>'
            for rec in recommendations[:3]
        ])
        
        return f'''
        <div class="intelligence-widget">
            <div class="widget-header">
                <div class="widget-title">🧠 Recommandations IA (llama3.1:8b)</div>
            </div>
            <div class="ai-analysis">
                {recs_html}
            </div>
            <div class="risk-assessment">
                <span>Évaluation Risque:</span>
                <span class="risk-indicator risk-{risk.lower()}">{risk}</span>
            </div>
        </div>'''
    
    def _get_error_widgets(self) -> Dict[str, str]:
        """Retourne des widgets d'erreur."""
        error_widget = '''
        <div class="intelligence-widget error-widget">
            <div class="widget-title">❌ Erreur de Génération</div>
            <p>Impossible de générer le widget</p>
        </div>'''
        
        return {widget_id: error_widget for widget_id in self.widgets_config.keys()}
