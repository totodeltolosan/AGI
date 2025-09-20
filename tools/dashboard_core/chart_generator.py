#!/usr/bin/env python3
"""
CHART GENERATOR - Module délégué conforme AGI
Génération des graphiques Plotly pour le tableau de bord
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Générateur spécialisé pour les graphiques Plotly."""
    
    def __init__(self):
        """Initialise le générateur de graphiques."""
        pass
    
    def generate_trends_chart(self, current_violations: int) -> str:
        """Génère le graphique de tendance des violations (simulé pour l'instant)."""
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
            
            # Données simulées pour 7 jours (le dernier point = violations actuelles)
            dates = self._generate_date_range()
            violations_trend = self._simulate_trend_data(current_violations)
            
            # Création du graphique Plotly
            fig = self._create_plotly_figure(dates, violations_trend)
            
            # Conversion en HTML
            chart_html = pyo.plot(fig, output_type='div', include_plotlyjs=False)
            return chart_html
            
        except Exception as e:
            logger.error(f"Erreur génération graphique: {e}")
            return self._get_error_chart(str(e))
    
    def _generate_date_range(self) -> list:
        """Génère une plage de dates pour les 7 derniers jours."""
        return [(datetime.now() - timedelta(days=i)).strftime("%d/%m") for i in range(6, -1, -1)]
    
    def _simulate_trend_data(self, current_violations: int) -> list:
        """Simule une tendance décroissante vers la valeur actuelle."""
        base_value = max(current_violations, 10)
        return [
            base_value + 15,
            base_value + 12,
            base_value + 8,
            base_value + 5,
            base_value + 3,
            base_value + 1,
            current_violations  # Valeur réelle actuelle
        ]
    
    def _create_plotly_figure(self, dates: list, violations_trend: list) -> Any:
        """Crée la figure Plotly avec le style constitutionnel."""
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=violations_trend,
            mode='lines+markers',
            name='Violations Critiques',
            line=dict(color='#f85149', width=3),
            marker=dict(size=8, color='#f85149')
        ))
        
        fig.update_layout(
            title="Tendance Constitutionnelle (7 jours)",
            title_font=dict(color='#c9d1d9', size=14),
            paper_bgcolor='#161b22',
            plot_bgcolor='#161b22',
            font=dict(color='#c9d1d9'),
            xaxis=dict(gridcolor='#30363d'),
            yaxis=dict(gridcolor='#30363d'),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40),
            height=200
        )
        
        return fig
    
    def _get_error_chart(self, error_msg: str) -> str:
        """Retourne un placeholder HTML en cas d'erreur."""
        return f'''
        <div class="chart-error" style="
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 200px; 
            color: #f85149; 
            border: 1px dashed #f85149; 
            border-radius: 8px;
        ">
            <div>
                <div style="font-size: 1.2em;">📊 Erreur Graphique</div>
                <div style="font-size: 0.8em; margin-top: 5px;">{error_msg}</div>
            </div>
        </div>
        '''
    
    def generate_placeholder_chart(self, title: str, message: str) -> str:
        """Génère un graphique placeholder pour les widgets futurs."""
        return f'''
        <div class="chart-placeholder" style="
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 200px; 
            color: #8b949e; 
            border: 1px dashed #30363d; 
            border-radius: 8px;
        ">
            <div style="text-align: center;">
                <div style="font-size: 1.2em;">{title}</div>
                <div style="font-size: 0.8em; margin-top: 5px;">{message}</div>
            </div>
        </div>
        '''
