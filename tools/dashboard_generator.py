#!/usr/bin/env python3
"""
DIRECTIVE CONSTITUTIONNELLE : DASHBOARD-CMD-v4.0 (FINAL)
Générateur du Poste de Commandement Stratégique AGI-EVE

Version finale respectant toutes les directives constitutionnelles :
- 9 widgets fonctionnels avec intelligence IA
- Terminal intégré avec commandes GitHub
- Boutons d'action exécutables
- Architecture modulaire conforme (<200 lignes par module)
"""

import sys
from pathlib import Path
from datetime import datetime
import logging

# Import de l'orchestrateur final
try:
    from .dashboard_core.command_orchestrator_final import CommandOrchestratorFinal
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from dashboard_core.command_orchestrator_final import CommandOrchestratorFinal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_dependencies():
    """Valide les dépendances pour le poste de commandement complet."""
    try:
        import git, jinja2, plotly, flask
        return True
    except ImportError as e:
        logger.error(f"❌ Dépendance manquante: {e}")
        print(f"💡 Installation: pip install gitpython jinja2 plotly flask flask-cors")
        return False

def main():
    """Point d'entrée principal - Poste de Commandement v4.0 COMPLET."""
    logger.info("🚀 DASHBOARD-CMD-v4.0 - Poste de Commandement Stratégique COMPLET")
    
    try:
        # Validation des prérequis
        if not validate_dependencies():
            sys.exit(1)
        
        # Détection du répertoire racine
        project_root = Path.cwd()
        start_time = datetime.now()
        
        # Orchestration complète v4.0
        orchestrator = CommandOrchestratorFinal(project_root)
        success = orchestrator.generate_complete_command_center()
        
        # Mesure de performance
        execution_time = (datetime.now() - start_time).total_seconds()
        
        if success:
            logger.info(f"✅ Poste de Commandement v4.0 COMPLET en {execution_time:.2f}s")
            print(f"\n🎯 SUCCÈS: Poste de Commandement Stratégique v4.0 déployé!")
            print(f"📄 Interface: {project_root}/AGI_Command_Center.html")
            print(f"⚡ Actions: 9 widgets + terminal intégré + commandes GitHub")
            print(f"🧠 Intelligence: Analyse IA + scoring A-F + recommandations")
            print(f"🚀 Serveur: python tools/command_server_extended.py")
            sys.exit(0)
        else:
            logger.error("❌ Échec du déploiement v4.0")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Déploiement interrompu")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
