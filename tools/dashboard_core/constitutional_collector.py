#!/usr/bin/env python3
"""
CONSTITUTIONAL DATA COLLECTOR - Module délégué conforme AGI
Collecte des données constitutionnelles depuis violations.json
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConstitutionalDataCollector:
    """Collecteur spécialisé pour les données constitutionnelles."""
    
    def __init__(self, project_root: Path):
        """Initialise le collecteur avec le répertoire racine."""
        self.project_root = project_root
        self.violations_file = project_root / "violations.json"
    
    def collect_constitutional_data(self) -> Dict[str, Any]:
        """Collecte les données constitutionnelles depuis violations.json."""
        try:
            if not self.violations_file.exists():
                logger.warning(f"violations.json non trouvé: {self.violations_file}")
                return self._get_error_fallback("Fichier violations.json non trouvé")
            
            with open(self.violations_file, 'r', encoding='utf-8') as f:
                violations_data = json.load(f)
            
            return self._process_violations_data(violations_data)
            
        except Exception as e:
            logger.error(f"Erreur collecte constitutionnelle: {e}")
            return self._get_error_fallback(f"Erreur de lecture: {str(e)}")
    
    def _process_violations_data(self, violations_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite les données de violations et calcule les métriques."""
        violations = violations_data.get('violations', [])
        
        # Calcul des métriques principales
        critical_violations = len([v for v in violations if v.get('severity') == 'critical'])
        total_violations = len(violations)
        
        # Calcul du taux de conformité
        total_files = violations_data.get('total_files_analyzed', 1)
        files_with_violations = len(set(v.get('file', '') for v in violations))
        compliance_rate = max(0, (total_files - files_with_violations) / total_files * 100)
        
        # Top 3 des lois les plus violées
        most_violated_laws = self._calculate_most_violated_laws(violations)
        
        return {
            "critical_violations": critical_violations,
            "total_violations": total_violations,
            "compliance_rate": round(compliance_rate, 1),
            "most_violated_laws": most_violated_laws,
            "total_files": total_files,
            "files_with_violations": files_with_violations
        }
    
    def _calculate_most_violated_laws(self, violations: list) -> list:
        """Calcule le top 3 des lois les plus violées."""
        law_counts = {}
        for violation in violations:
            law_id = violation.get('law_id', 'UNKNOWN')
            law_counts[law_id] = law_counts.get(law_id, 0) + 1
        
        return sorted(law_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    def _get_error_fallback(self, error_message: str) -> Dict[str, Any]:
        """Retourne une structure de données d'erreur."""
        return {
            "error": error_message,
            "critical_violations": 0,
            "total_violations": 0,
            "compliance_rate": 0,
            "most_violated_laws": [],
            "total_files": 0,
            "files_with_violations": 0
        }
