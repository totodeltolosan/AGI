#!/usr/bin/env python3
"""
DASHBOARD ORCHESTRATOR - Module délégué conforme AGI
Orchestrateur principal du tableau de bord constitutionnel
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

from .constitutional_collector import ConstitutionalDataCollector
from .git_collector import GitDataCollector
from .template_manager import TemplateManager
from .chart_generator import ChartGenerator

logger = logging.getLogger(__name__)

class DashboardOrchestrator:
    """Orchestrateur principal du tableau de bord constitutionnel."""
    
    def __init__(self, project_root: Path):
        """Initialise l'orchestrateur avec tous ses délégués."""
        self.project_root = project_root
        self.output_file = project_root / "AGI_Dashboard.html"
        
        # Délégués spécialisés (pattern de délégation constitutionnel)
        self.constitutional_collector = ConstitutionalDataCollector(project_root)
        self.git_collector = GitDataCollector(project_root)
        self.template_manager = TemplateManager(project_root)
        self.chart_generator = ChartGenerator()
    
    def generate_complete_dashboard(self) -> bool:
        """Génère le tableau de bord complet via orchestration des délégués."""
        try:
            logger.info("🚀 Démarrage génération dashboard constitutionnel")
            
            # Phase 1: Préparation des ressources
            self.template_manager.ensure_template_exists()
            
            # Phase 2: Collecte orchestrée des données
            context = self._orchestrate_data_collection()
            
            # Phase 3: Rendu et finalisation
            return self._finalize_dashboard(context)
            
        except Exception as e:
            logger.error(f"❌ Erreur orchestration: {e}")
            return False
    
    def _orchestrate_data_collection(self) -> Dict[str, Any]:
        """Orchestre la collecte de toutes les données via les délégués."""
        logger.info("📊 Orchestration collecte données...")
        
        # Collecte constitutionnelle
        constitutional = self.constitutional_collector.collect_constitutional_data()
        logger.info("✅ Données constitutionnelles collectées")
        
        # Collecte Git
        git_status = self.git_collector.collect_git_status()
        hot_spots = self.git_collector.collect_hot_spots()
        recent_activity = self.git_collector.collect_recent_activity()
        logger.info("✅ Données Git collectées")
        
        # Génération graphiques
        trends_chart = self.chart_generator.generate_trends_chart(
            constitutional.get('critical_violations', 0)
        )
        logger.info("✅ Graphiques générés")
        
        # Compilation du contexte
        return {
            'generation_time': datetime.now().strftime("%d/%m/%Y à %H:%M:%S"),
            'constitutional': constitutional,
            'git_status': git_status,
            'hot_spots': hot_spots,
            'recent_activity': recent_activity,
            'trends_chart': trends_chart
        }
    
    def _finalize_dashboard(self, context: Dict[str, Any]) -> bool:
        """Finalise la génération du dashboard."""
        try:
            logger.info("🎨 Rendu final du template...")
            
            # Rendu via le gestionnaire de template
            html_output = self.template_manager.render_template(context)
            
            # Écriture du fichier final
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_output)
            
            logger.info(f"✅ Dashboard finalisé: {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur finalisation: {e}")
            return False
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du dashboard pour monitoring."""
        return {
            "output_file": str(self.output_file),
            "output_exists": self.output_file.exists(),
            "template_file": str(self.template_manager.template_file),
            "template_exists": self.template_manager.template_file.exists(),
            "project_root": str(self.project_root)
        }
