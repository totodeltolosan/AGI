#!/usr/bin/env python3
"""
SCORING ENGINE - Module v4.0 conforme AGI
Moteur de scoring et d'évaluation pour le poste de commandement
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import logging
from typing import Dict, Any, List, Tuple
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ScoringEngine:
    """Moteur de scoring pour l'évaluation constitutionnelle et stratégique."""
    
    def __init__(self):
        """Initialise le moteur de scoring."""
        self.scoring_weights = {
            'critical_violations': 0.4,    # 40% du score
            'compliance_rate': 0.3,        # 30% du score
            'code_coverage': 0.2,          # 20% du score (si disponible)
            'code_complexity': 0.1         # 10% du score (si disponible)
        }
        
        self.grade_thresholds = {
            'A+': 95, 'A': 85, 'B': 70, 'C': 50, 'D': 25, 'F': 0
        }
    
    def calculate_overall_health_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score de santé global du projet."""
        try:
            # Extraction des métriques
            critical_violations = metrics.get('critical_violations', 0)
            total_violations = metrics.get('total_violations', 0)
            compliance_rate = metrics.get('compliance_rate', 0)
            
            # Calcul des sous-scores
            constitutional_score = self._calculate_constitutional_score(
                critical_violations, total_violations, compliance_rate
            )
            
            # Score de couverture de code (simulé pour v4.0)
            coverage_score = self._calculate_coverage_score(metrics)
            
            # Score de complexité (simulé pour v4.0)
            complexity_score = self._calculate_complexity_score(metrics)
            
            # Score global pondéré
            overall_score = (
                constitutional_score * self.scoring_weights['critical_violations'] +
                compliance_rate * self.scoring_weights['compliance_rate'] +
                coverage_score * self.scoring_weights['code_coverage'] +
                complexity_score * self.scoring_weights['code_complexity']
            )
            
            # Détermination de la note
            grade = self._score_to_grade(overall_score)
            
            return {
                "overall_score": round(overall_score, 1),
                "grade": grade,
                "constitutional_score": round(constitutional_score, 1),
                "coverage_score": round(coverage_score, 1),
                "complexity_score": round(complexity_score, 1),
                "diagnosis": self._get_diagnosis(grade, overall_score),
                "recommendations": self._generate_recommendations(overall_score, metrics)
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul score global: {e}")
            return self._get_error_score()
    
    def calculate_file_risk_scores(self, violations: List[Dict]) -> List[Dict[str, Any]]:
        """Calcule les scores de risque par fichier."""
        file_scores = {}
        
        for violation in violations:
            file_path = violation.get('file', 'unknown')
            lines = violation.get('lines', 0)
            excess = violation.get('excess', 0)
            severity = violation.get('severity', 'normal')
            
            if file_path not in file_scores:
                file_scores[file_path] = {
                    'violations_count': 0,
                    'total_excess': 0,
                    'max_lines': 0,
                    'critical_count': 0,
                    'risk_factors': []
                }
            
            file_scores[file_path]['violations_count'] += 1
            file_scores[file_path]['total_excess'] += excess
            file_scores[file_path]['max_lines'] = max(file_scores[file_path]['max_lines'], lines)
            
            if severity == 'critical':
                file_scores[file_path]['critical_count'] += 1
            
            # Calcul des facteurs de risque
            risk_factors = []
            if lines > 1000:
                risk_factors.append("Fichier volumineux")
            if excess > 500:
                risk_factors.append("Excès critique")
            if severity == 'critical':
                risk_factors.append("Violation critique")
            
            file_scores[file_path]['risk_factors'] = risk_factors
        
        # Calcul du score de risque pour chaque fichier
        scored_files = []
        for file_path, data in file_scores.items():
            risk_score = self._calculate_file_risk_score(data)
            scored_files.append({
                'file': file_path,
                'risk_score': risk_score,
                'risk_level': self._get_risk_level(risk_score),
                'data': data
            })
        
        # Tri par score de risque décroissant
        return sorted(scored_files, key=lambda x: x['risk_score'], reverse=True)[:10]
    
    def calculate_trend_score(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calcule le score de tendance basé sur l'historique."""
        # TODO: Implémenter quand l'historique des violations sera disponible
        # Pour l'instant, simulation
        return {
            "trend_direction": "stable",
            "trend_percentage": 0,
            "trend_score": 75,
            "prediction": "Stabilité maintenue"
        }
    
    def _calculate_constitutional_score(self, critical: int, total: int, compliance: float) -> float:
        """Calcule le score constitutionnel."""
        if total == 0:
            return 100.0
        
        # Pénalité pour violations critiques (impact fort)
        critical_penalty = min(critical * 5, 50)  # Max 50 points de pénalité
        
        # Pénalité pour violations totales (impact modéré)
        total_penalty = min(total * 0.5, 30)  # Max 30 points de pénalité
        
        # Bonus pour conformité
        compliance_bonus = compliance * 0.2  # Max 20 points de bonus
        
        score = 100 - critical_penalty - total_penalty + compliance_bonus
        return max(0, min(100, score))
    
    def _calculate_coverage_score(self, metrics: Dict[str, Any]) -> float:
        """Calcule le score de couverture de code."""
        # TODO: Intégrer avec coverage.py quand disponible
        # Simulation basée sur la structure du projet
        total_files = metrics.get('total_files', 100)
        conformant_files = total_files - metrics.get('files_with_violations', 0)
        
        if total_files == 0:
            return 0
        
        # Estimation de la couverture basée sur la conformité
        estimated_coverage = (conformant_files / total_files) * 85  # Estimation
        return min(100, estimated_coverage)
    
    def _calculate_complexity_score(self, metrics: Dict[str, Any]) -> float:
        """Calcule le score de complexité."""
        # TODO: Intégrer avec radon quand disponible
        # Estimation basée sur les violations
        total_violations = metrics.get('total_violations', 0)
        
        if total_violations == 0:
            return 95  # Excellente complexité
        elif total_violations < 50:
            return 80  # Bonne complexité
        elif total_violations < 100:
            return 60  # Complexité modérée
        else:
            return 40  # Complexité élevée
    
    def _score_to_grade(self, score: float) -> str:
        """Convertit un score numérique en note."""
        for grade, threshold in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return 'F'
    
    def _get_diagnosis(self, grade: str, score: float) -> str:
        """Génère un diagnostic basé sur la note et le score."""
        diagnoses = {
            'A+': "🏆 Excellence architecturale - Projet modèle",
            'A': "✅ Très bonne santé constitutionnelle",
            'B': "🟢 Santé constitutionnelle satisfaisante",
            'C': "🟡 Attention requise - Dette technique modérée",
            'D': "🟠 Problèmes constitutionnels significatifs",
            'F': "🚨 URGENCE - Refactorisation critique nécessaire"
        }
        return diagnoses.get(grade, "Diagnostic indéterminé")
    
    def _generate_recommendations(self, score: float, metrics: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur le score."""
        recommendations = []
        
        if score >= 90:
            recommendations.extend([
                "Maintenir l'excellence actuelle",
                "Focus sur l'optimisation et la documentation",
                "Considérer partage de bonnes pratiques"
            ])
        elif score >= 70:
            recommendations.extend([
                "Traiter les violations mineures restantes",
                "Améliorer la couverture de tests",
                "Optimiser les modules complexes"
            ])
        elif score >= 50:
            recommendations.extend([
                "PRIORITÉ: Résoudre les violations critiques",
                "Planifier session de refactorisation",
                "Réviser l'architecture des gros modules"
            ])
        else:
            recommendations.extend([
                "URGENT: Intervention architecturale nécessaire",
                "Refactorisation immédiate des modules critiques",
                "Audit complet de l'architecture"
            ])
        
        return recommendations
    
    def _calculate_file_risk_score(self, file_data: Dict[str, Any]) -> float:
        """Calcule le score de risque d'un fichier."""
        base_score = 0
        
        # Impact des violations
        base_score += file_data['violations_count'] * 10
        base_score += file_data['critical_count'] * 25
        base_score += min(file_data['total_excess'] / 10, 50)
        
        # Facteurs de risque
        base_score += len(file_data['risk_factors']) * 15
        
        return min(100, base_score)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Détermine le niveau de risque basé sur le score."""
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
        """Retourne un score d'erreur."""
        return {
            "overall_score": 0,
            "grade": "ERROR",
            "constitutional_score": 0,
            "coverage_score": 0,
            "complexity_score": 0,
            "diagnosis": "Erreur de calcul du score",
            "recommendations": ["Vérifier l'intégrité des données"]
        }
