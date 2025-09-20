#!/usr/bin/env python3
"""
SCORING ENGINE - Module v4.0 conforme AGI (RÉDUIT)
Moteur de scoring constitutionnel simplifié
Limite: 200 lignes (Version conforme)
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ScoringEngine:
    """Moteur de scoring constitutionnel simplifié."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.grade_thresholds = {'A+': 95, 'A': 85, 'B': 70, 'C': 50, 'D': 25, 'F': 0}
    
    def calculate_overall_health_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score de santé global simplifié."""
        try:
            critical = metrics.get('critical_violations', 0)
            total = metrics.get('total_violations', 0)
            compliance = metrics.get('compliance_rate', 0)
            
            # Calcul simplifié
            if critical == 0 and total < 10:
                score, grade = 95, 'A+'
            elif critical < 5 and total < 50:
                score, grade = 80, 'B'
            elif critical < 15:
                score, grade = 65, 'C'
            else:
                score, grade = 40, 'F'
            
            diagnosis = self._get_diagnosis(grade)
            recommendations = self._get_recommendations(grade)
            
            return {
                "overall_score": score,
                "grade": grade,
                "constitutional_score": score,
                "coverage_score": 75,  # Estimation
                "complexity_score": 70,  # Estimation
                "diagnosis": diagnosis,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul score: {e}")
            return self._get_error_score()
    
    def calculate_file_risk_scores(self, violations: List[Dict]) -> List[Dict[str, Any]]:
        """Calcule les scores de risque par fichier."""
        file_scores = {}
        
        for violation in violations:
            file_path = violation.get('file', 'unknown')
            excess = violation.get('excess', 0)
            
            if file_path not in file_scores:
                file_scores[file_path] = {'excess': 0, 'count': 0}
            
            file_scores[file_path]['excess'] += excess
            file_scores[file_path]['count'] += 1
        
        # Conversion en format de sortie
        scored_files = []
        for file_path, data in file_scores.items():
            risk_score = min(100, data['excess'] / 10 + data['count'] * 5)
            risk_level = self._get_risk_level(risk_score)
            
            scored_files.append({
                'file': file_path,
                'risk_score': int(risk_score),
                'risk_level': risk_level,
                'data': data
            })
        
        return sorted(scored_files, key=lambda x: x['risk_score'], reverse=True)[:10]
    
    def _get_diagnosis(self, grade: str) -> str:
        """Génère un diagnostic basé sur la note."""
        diagnoses = {
            'A+': "🏆 Excellence architecturale - Projet modèle",
            'A': "✅ Très bonne santé constitutionnelle",
            'B': "🟢 Santé constitutionnelle satisfaisante",
            'C': "🟡 Attention requise - Dette technique modérée",
            'D': "🟠 Problèmes constitutionnels significatifs",
            'F': "🚨 URGENCE - Refactorisation critique nécessaire"
        }
        return diagnoses.get(grade, "Diagnostic indéterminé")
    
    def _get_recommendations(self, grade: str) -> List[str]:
        """Génère des recommandations basées sur la note."""
        recommendations = {
            'A+': ["Maintenir l'excellence", "Documentation des bonnes pratiques"],
            'A': ["Optimisation continue", "Surveillance préventive"],
            'B': ["Traiter violations mineures", "Améliorer couverture tests"],
            'C': ["Résoudre violations critiques", "Planifier refactorisation"],
            'D': ["Intervention architecturale", "Audit complet requis"],
            'F': ["URGENT: Refactorisation immédiate", "Révision architecture complète"]
        }
        return recommendations.get(grade, ["Surveillance continue"])
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Détermine le niveau de risque."""
        if risk_score >= 80:
            return "CRITIQUE"
        elif risk_score >= 60:
            return "ÉLEVÉ"
        elif risk_score >= 40:
            return "MODÉRÉ"
        elif risk_score >= 20:
            return "FAIBLE"
        else:
            return "MINIMAL"
    
    def _get_error_score(self) -> Dict[str, Any]:
        """Score d'erreur."""
        return {
            "overall_score": 0,
            "grade": "ERROR",
            "constitutional_score": 0,
            "coverage_score": 0,
            "complexity_score": 0,
            "diagnosis": "Erreur de calcul du score",
            "recommendations": ["Vérifier l'intégrité des données"]
        }
