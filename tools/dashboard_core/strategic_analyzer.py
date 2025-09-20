#!/usr/bin/env python3
"""
STRATEGIC ANALYZER - Module v4.0 conforme AGI
Analyse stratégique des violations et scoring de santé constitutionnelle
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class StrategicAnalyzer:
    """Analyseur stratégique pour le scoring et l'évaluation constitutionnelle."""
    
    def __init__(self):
        """Initialise l'analyseur stratégique."""
        self.health_scores = {
            'A+': (95, 100, "🏆 Excellence Constitutionnelle"),
            'A': (85, 95, "✅ Stabilité Excellente"),
            'B': (70, 85, "🟢 Bonne Santé Constitutionnelle"),
            'C': (50, 70, "🟡 Dette Technique Modérée"),
            'D': (25, 50, "🟠 Problèmes Constitutionnels"),
            'F': (0, 25, "🚨 URGENCE CONSTITUTIONNELLE")
        }
    
    def analyze_constitutional_health(self, constitutional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse la santé constitutionnelle et calcule le score."""
        try:
            critical_violations = constitutional_data.get('critical_violations', 0)
            total_violations = constitutional_data.get('total_violations', 0)
            compliance_rate = constitutional_data.get('compliance_rate', 0)
            
            # Calcul du score de santé
            health_score = self._calculate_health_score(critical_violations, total_violations, compliance_rate)
            grade, diagnosis = self._get_grade_and_diagnosis(health_score)
            
            # Analyse des tendances
            trend_analysis = self._analyze_violation_trends(constitutional_data)
            
            # Suggestions d'action
            action_suggestions = self._generate_action_suggestions(critical_violations, total_violations)
            
            return {
                "health_score": health_score,
                "grade": grade,
                "diagnosis": diagnosis,
                "trend_analysis": trend_analysis,
                "action_suggestions": action_suggestions,
                "priority_level": self._get_priority_level(critical_violations)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse stratégique: {e}")
            return self._get_error_analysis()
    
    def analyze_violation_patterns(self, violations_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les patterns de violations pour identification des causes racines."""
        violations = violations_data.get('violations', [])
        
        # Analyse par type de loi
        law_analysis = self._analyze_by_law_type(violations)
        
        # Analyse par fichier
        file_analysis = self._analyze_by_file_pattern(violations)
        
        # Identification des hotspots critiques
        critical_hotspots = self._identify_critical_hotspots(violations)
        
        return {
            "law_type_analysis": law_analysis,
            "file_pattern_analysis": file_analysis,
            "critical_hotspots": critical_hotspots,
            "remediation_strategy": self._suggest_remediation_strategy(law_analysis)
        }
    
    def _calculate_health_score(self, critical: int, total: int, compliance: float) -> float:
        """Calcule le score de santé basé sur les métriques constitutionnelles."""
        if total == 0:
            return 100.0
        
        # Formule de scoring pondérée
        critical_penalty = (critical / max(total, 1)) * 40  # Impact critique = 40%
        total_penalty = min(total, 50) * 0.6  # Impact total = 30%
        compliance_bonus = compliance * 0.3  # Bonus conformité = 30%
        
        score = 100 - critical_penalty - total_penalty + compliance_bonus
        return max(0, min(100, score))
    
    def _get_grade_and_diagnosis(self, score: float) -> Tuple[str, str]:
        """Détermine la note et le diagnostic basés sur le score."""
        for grade, (min_score, max_score, diagnosis) in self.health_scores.items():
            if min_score <= score < max_score:
                return grade, diagnosis
        return 'F', "🚨 URGENCE CONSTITUTIONNELLE"
    
    def _analyze_violation_trends(self, data: Dict[str, Any]) -> str:
        """Analyse les tendances de violations (simulé pour v4.0)."""
        # TODO: Implémenter l'analyse historique des violations
        # Nécessite : Historique des violations.json des 7 derniers jours
        return "Tendance stable (données historiques requises)"
    
    def _generate_action_suggestions(self, critical: int, total: int) -> List[str]:
        """Génère des suggestions d'action basées sur l'état constitutionnel."""
        suggestions = []
        
        if critical > 10:
            suggestions.append("URGENT: Traiter immédiatement les violations critiques")
            suggestions.append("Lancer l'auto-correcteur sur les 5 fichiers les plus problématiques")
        
        if total > 50:
            suggestions.append("Planifier une session de refactorisation")
            suggestions.append("Réviser l'architecture des modules les plus volumineux")
        
        if critical == 0 and total < 10:
            suggestions.append("Maintenir la qualité actuelle")
            suggestions.append("Focus sur l'optimisation et la documentation")
        
        return suggestions or ["Continuer la surveillance constitutionnelle"]
    
    def _get_priority_level(self, critical: int) -> str:
        """Détermine le niveau de priorité basé sur les violations critiques."""
        if critical == 0:
            return "MAINTENANCE"
        elif critical <= 5:
            return "NORMAL"
        elif critical <= 15:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _analyze_by_law_type(self, violations: List[Dict]) -> Dict[str, int]:
        """Analyse les violations par type de loi."""
        law_counts = {}
        for violation in violations:
            law_id = violation.get('law_id', 'UNKNOWN')
            law_counts[law_id] = law_counts.get(law_id, 0) + 1
        return dict(sorted(law_counts.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def _analyze_by_file_pattern(self, violations: List[Dict]) -> Dict[str, Any]:
        """Analyse les patterns de fichiers problématiques."""
        file_data = {}
        for violation in violations:
            file_path = violation.get('file', 'unknown')
            if file_path not in file_data:
                file_data[file_path] = {'count': 0, 'lines': violation.get('lines', 0)}
            file_data[file_path]['count'] += 1
        
        # Top 5 des fichiers les plus problématiques
        sorted_files = sorted(file_data.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        return {"top_problematic_files": sorted_files}
    
    def _identify_critical_hotspots(self, violations: List[Dict]) -> List[Dict[str, Any]]:
        """Identifie les hotspots critiques nécessitant une attention immédiate."""
        hotspots = []
        for violation in violations:
            if violation.get('severity') == 'critical' and violation.get('lines', 0) > 1000:
                hotspots.append({
                    "file": violation.get('file'),
                    "lines": violation.get('lines'),
                    "excess": violation.get('excess', 0),
                    "urgency": "IMMEDIATE"
                })
        return sorted(hotspots, key=lambda x: x['excess'], reverse=True)[:3]
    
    def _suggest_remediation_strategy(self, law_analysis: Dict[str, int]) -> List[str]:
        """Suggère une stratégie de remédiation basée sur l'analyse."""
        strategies = []
        
        # Analyse du type de loi le plus violé
        if law_analysis:
            top_law = list(law_analysis.keys())[0]
            if 'COMP' in top_law:
                strategies.append("Focus: Refactorisation des composants complexes")
            elif 'SEC' in top_law:
                strategies.append("Focus: Révision des pratiques de sécurité")
            else:
                strategies.append("Focus: Amélioration de l'architecture générale")
        
        strategies.append("Appliquer le pattern de délégation constitutionnelle")
        return strategies
    
    def _get_error_analysis(self) -> Dict[str, Any]:
        """Retourne une analyse d'erreur."""
        return {
            "health_score": 0,
            "grade": "ERROR",
            "diagnosis": "Erreur d'analyse constitutionnelle",
            "trend_analysis": "Données non disponibles",
            "action_suggestions": ["Vérifier l'intégrité des données"],
            "priority_level": "CRITICAL"
        }
