#!/usr/bin/env python3
"""
Script Principal d'Audit AGI - Version Constitutionnelle Réelle
================================================================

CHEMIN: run_agi_audit.py

Rôle Fondamental (Conforme iaGOD.json) :
- Interface utilisateur pour audit constitutionnel réel
- Délégation vers système modulaire conforme
- Intégration vraie avec iaGOD.json (pas de mensonges)
- Respecter directive < 200 lignes

Conforme aux directives constitutionnelles:
- META-001: Directive Suprême de Finalité  
- META-003: Axiome de la Vérité Constitutionnelle
- COMP-CST-001: Constitution Exécutable iaGOD.json
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Import du système d'audit constitutionnel réel
from compliance import (
    ConstitutionLoader,
    BasicAuditor, 
    ConstitutionalReporter
)

def setup_logging(verbose: bool = False):
    """Configure le système de logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )

def main():
    """Point d'entrée principal conforme iaGOD.json"""
    parser = argparse.ArgumentParser(
        description="🏛️ Audit AGI - Système Constitutionnel Réel (iaGOD.json)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLES D'UTILISATION:

  Audit constitutionnel complet:
    python run_agi_audit.py --full --target ./tools/project_initializer/

  Audit rapide (syntaxe + 200 lignes):
    python run_agi_audit.py --target ./compliance/

  Avec rapport détaillé:
    python run_agi_audit.py --target . --output ./audit_report.txt --verbose

ARCHITECTURE RÉELLE:
  Ce script utilise le système modulaire compliance/ qui implémente
  vraiment les directives constitutionnelles iaGOD.json.
  
  Modules: ConstitutionLoader, BasicAuditor, ConstitutionalReporter
  Constitution: iaGOD.json (source de vérité unique)
        """
    )
    
    parser.add_argument(
        "--target", 
        type=str, 
        default=".",
        help="Répertoire à auditer (défaut: répertoire courant)"
    )
    
    parser.add_argument(
        "--output", 
        type=str,
        help="Fichier de sortie pour rapport détaillé"
    )
    
    parser.add_argument(
        "--full", 
        action="store_true",
        help="Audit constitutionnel complet (recommandé)"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Mode verbeux avec détails d'exécution"
    )
    
    args = parser.parse_args()
    
    # Configuration
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🏛️ Démarrage audit constitutionnel AGI")
        
        # 1. Charger la constitution iaGOD.json
        logger.info("📜 Chargement constitution iaGOD.json...")
        constitution_loader = ConstitutionLoader()
        
        if not constitution_loader.load_constitution():
            logger.error("❌ Échec chargement constitution iaGOD.json")
            return 1
        
        logger.info(f"✅ Constitution chargée: {len(constitution_loader.get_all_laws())} lois")
        
        # 2. Initialiser l'auditeur
        logger.info("🔍 Initialisation auditeur constitutionnel...")
        auditor = BasicAuditor(constitution_loader)
        
        # 3. Exécuter l'audit
        target_path = Path(args.target)
        if not target_path.exists():
            logger.error(f"❌ Répertoire cible inexistant: {target_path}")
            return 1
        
        logger.info(f"🚀 Audit en cours: {target_path}")
        violations = auditor.audit_directory(target_path)
        
        # 4. Générer les rapports
        reporter = ConstitutionalReporter()
        
        # Rapport console
        console_report = reporter.generate_console_report(violations)
        print(console_report)
        
        # Rapport fichier si demandé
        if args.output:
            output_path = Path(args.output)
            reporter.save_detailed_report(violations, output_path)
            logger.info(f"📄 Rapport sauvegardé: {output_path}")
        
        # Code de sortie selon résultats
        if not violations:
            logger.info("✅ Audit réussi: Aucune violation constitutionnelle")
            return 0
        else:
            critical_violations = len([v for v in violations if v.severity == "CRITICAL"])
            if critical_violations > 0:
                logger.error(f"❌ Audit échoué: {critical_violations} violations critiques")
                return 1
            else:
                logger.warning(f"⚠️ Audit avec avertissements: {len(violations)} violations mineures")
                return 0
                
    except Exception as e:
        logger.error(f"💥 Erreur fatale audit: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 2

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Audit interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        sys.exit(255)
