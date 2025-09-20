#!/usr/bin/env python3
"""
TEMPLATE MANAGER - Module délégué conforme AGI
Gestion du template HTML du tableau de bord
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TemplateManager:
    """Gestionnaire spécialisé pour les templates HTML."""
    
    def __init__(self, project_root: Path):
        """Initialise le gestionnaire avec le répertoire racine."""
        self.project_root = project_root
        self.template_file = project_root / "tools" / "dashboard_template_v3.html"
        
        # Assurer que le dossier tools existe
        self.template_file.parent.mkdir(exist_ok=True)
    
    def ensure_template_exists(self):
        """S'assure que le template HTML existe, le crée si nécessaire."""
        if self.template_file.exists():
            logger.info("Template existant trouvé")
            return
        
        logger.info("Création du template HTML...")
        self._create_template()
    
    def render_template(self, context: Dict[str, Any]) -> str:
        """Rend le template avec le contexte donné."""
        try:
            from jinja2 import Template
            
            with open(self.template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            return template.render(**context)
            
        except Exception as e:
            logger.error(f"Erreur rendu template: {e}")
            return self._get_error_html(str(e))
    
    def _create_template(self):
        """Crée le fichier template HTML complet."""
        # Template HTML compact (focus sur l'essentiel)
        template_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Poste de Commandement Constitutionnel - AGI-EVE</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background-color: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #58a6ff; font-size: 2.5em; margin-bottom: 10px; }
        .actions-panel { display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }
        .action-btn { background: linear-gradient(135deg, #21262d, #30363d); border: 1px solid #30363d; color: #c9d1d9; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 500; transition: all 0.3s ease; cursor: pointer; }
        .action-btn:hover { background: linear-gradient(135deg, #30363d, #40464d); border-color: #58a6ff; color: #58a6ff; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 20px; }
        .widget { background: linear-gradient(135deg, #161b22, #21262d); border: 1px solid #30363d; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); transition: transform 0.2s ease; }
        .widget:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(88, 166, 255, 0.1); }
        .widget-title { color: #58a6ff; font-size: 1.1em; font-weight: 600; margin-bottom: 15px; }
        .metric-large { font-size: 3em; font-weight: bold; margin: 10px 0; text-align: center; }
        .metric-critical { color: #f85149; }
        .metric-success { color: #3fb950; }
        .metric-warning { color: #d29922; }
        .metric-subtitle { text-align: center; color: #8b949e; font-size: 0.9em; }
        .list-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #21262d; }
        .list-item:last-child { border-bottom: none; }
        .commit-item { padding: 10px; margin: 5px 0; border-radius: 6px; background: #21262d; }
        .commit-auto-corrector { border-left: 4px solid #58a6ff; background: #1c2128; }
        .commit-hash { color: #58a6ff; font-family: monospace; font-size: 0.85em; }
        .placeholder-widget { text-align: center; color: #8b949e; font-style: italic; }
        .error-message { color: #f85149; font-size: 0.9em; text-align: center; }
        .chart-container { height: 200px; margin-top: 10px; }
        .widget-span-4 { grid-column: span 4; }
        .widget-span-3 { grid-column: span 3; }
        .widget-span-6 { grid-column: span 6; }
        @media (max-width: 768px) { .widget { grid-column: span 12 !important; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Poste de Commandement Constitutionnel</h1>
            <p>AGI-EVE Dashboard v3.0 • Généré le {{ generation_time }}</p>
        </div>
        
        <div class="actions-panel">
            <button class="action-btn">🚀 Session Complète</button>
            <button class="action-btn" onclick="location.reload()">🔄 Rafraîchir</button>
            <button class="action-btn">🐙 GitHub</button>
            <button class="action-btn">🔬 Audit</button>
        </div>
        
        <div class="dashboard-grid">
            <!-- Widget 1: État Constitutionnel -->
            <div class="widget widget-span-4">
                <div class="widget-title">⚖️ État Constitutionnel</div>
                {% if constitutional.error %}
                    <div class="error-message">{{ constitutional.error }}</div>
                {% else %}
                    <div class="metric-large metric-critical">{{ constitutional.critical_violations }}</div>
                    <div class="metric-subtitle">{{ constitutional.total_violations }} violations • {{ constitutional.compliance_rate }}% conformité</div>
                {% endif %}
            </div>
            
            <!-- Widget 2: État Git -->
            <div class="widget widget-span-4">
                <div class="widget-title">💻 État du Travail</div>
                {% if git_status.error %}
                    <div class="error-message">{{ git_status.error }}</div>
                {% else %}
                    <div class="metric-large">{{ git_status.status_text }}</div>
                    <div class="metric-subtitle">{{ git_status.modified_files }} modifiés • {{ git_status.untracked_files }} non suivis</div>
                {% endif %}
            </div>
            
            <!-- Widget 3: Points Chauds -->
            <div class="widget widget-span-4">
                <div class="widget-title">🔥 Points Chauds (7j)</div>
                {% for file, changes in hot_spots %}
                    <div class="list-item"><span>{{ file }}</span><span class="metric-warning">{{ changes }}</span></div>
                {% endfor %}
            </div>
            
            <!-- Widget 4: Activité Récente -->
            <div class="widget widget-span-6">
                <div class="widget-title">📈 Activité Récente</div>
                {% for commit in recent_activity %}
                    <div class="commit-item {% if commit.is_auto_corrector %}commit-auto-corrector{% endif %}">
                        <div class="commit-hash">{{ commit.hash }}</div>
                        <div>{{ commit.message }}</div>
                        <div style="font-size: 0.8em; color: #8b949e;">{{ commit.author }} • {{ commit.date }}</div>
                    </div>
                {% endfor %}
            </div>
            
            <!-- Widget 5: Lois Violées -->
            <div class="widget widget-span-3">
                <div class="widget-title">🚨 Lois Violées</div>
                {% for law_id, count in constitutional.most_violated_laws %}
                    <div class="list-item"><span>{{ law_id }}</span><span class="metric-critical">{{ count }}</span></div>
                {% endfor %}
            </div>
            
            <!-- Widget 6: Tendance -->
            <div class="widget widget-span-3">
                <div class="widget-title">📊 Tendance</div>
                <div class="chart-container">{{ trends_chart | safe }}</div>
            </div>
        </div>
    </div>
    
    <script>
        setTimeout(() => location.reload(), 300000); // Auto-refresh 5min
        console.log('🚀 Poste de Commandement AGI-EVE v3.0 chargé');
    </script>
</body>
</html>'''
        
        with open(self.template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        logger.info(f"Template créé: {self.template_file}")
    
    def _get_error_html(self, error_msg: str) -> str:
        """Retourne un HTML d'erreur."""
        return f"<html><body><h1>Erreur Template</h1><p>{error_msg}</p></body></html>"
