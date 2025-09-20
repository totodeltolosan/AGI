#!/usr/bin/env python3
"""
DIRECTIVE CONSTITUTIONNELLE : DASHBOARD-GEN-v3.0 (CONFORME)
Générateur du Poste de Commandement Constitutionnel AGI-EVE

Ce script respecte la limite constitutionnelle de 200 lignes via délégation modulaire.
Architecture conforme : Orchestrateur + Délégués spécialisés.
"""

import sys
from pathlib import Path
from datetime import datetime
import logging

# Délégués spécialisés (conformes 200 lignes chacun)
try:
    from .dashboard_core.constitutional_collector import ConstitutionalDataCollector
    from .dashboard_core.git_collector import GitDataCollector
    from .dashboard_core.template_manager import TemplateManager
    from .dashboard_core.chart_generator import ChartGenerator
    from .dashboard_core.dashboard_orchestrator import DashboardOrchestrator
except ImportError:
    # Fallback pour exécution directe
    sys.path.append(str(Path(__file__).parent))
    from dashboard_core.constitutional_collector import ConstitutionalDataCollector
    from dashboard_core.git_collector import GitDataCollector
    from dashboard_core.template_manager import TemplateManager
    from dashboard_core.chart_generator import ChartGenerator
    from dashboard_core.dashboard_orchestrator import DashboardOrchestrator

# Configuration du logging constitutionnel
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_dependencies():
    """Valide la présence des dépendances obligatoires."""
    try:
        import git, jinja2, plotly
        return True
    except ImportError as e:
        logger.error(f"❌ Dépendance manquante: {e}")
        print(f"💡 Solution: pip install gitpython jinja2 plotly")
        return False

def main():
    """Point d'entrée principal - Orchestrateur constitutionnel."""
    logger.info("🚀 DASHBOARD-GEN-v3.0 - Générateur Constitutionnel (CONFORME)")
    
    try:
        # Validation des prérequis
        if not validate_dependencies():
            sys.exit(1)
            
        # Détection du répertoire racine
        project_root = Path.cwd()
        start_time = datetime.now()
        
        # Orchestration via délégation (pattern constitutionnel)
        orchestrator = DashboardOrchestrator(project_root)
        success = orchestrator.generate_complete_dashboard()
        
        # Mesure de performance
        execution_time = (datetime.now() - start_time).total_seconds()
        
        if success:
            logger.info(f"✅ Dashboard généré en {execution_time:.2f}s")
            print(f"\n✅ SUCCÈS: Poste de Commandement opérationnel!")
            print(f"📄 Fichier: {project_root}/AGI_Dashboard.html")
            print(f"🌐 Ouvrez le fichier dans votre navigateur")
            sys.exit(0)
        else:
            logger.error("❌ Échec de la génération")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Génération interrompue")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
