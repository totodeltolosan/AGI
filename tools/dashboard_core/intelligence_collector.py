#!/usr/bin/env python3
"""
INTELLIGENCE COLLECTOR - Module v4.0 conforme AGI
Collecteur d'intelligence augmentée avec intégration Llama 7B local
Limite: 200 lignes (Conforme à la directive constitutionnelle)
"""

import logging
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class IntelligenceCollector:
    """Collecteur d'intelligence augmentée avec IA locale."""
    
    def __init__(self, project_root: Path):
        """Initialise le collecteur d'intelligence."""
        self.project_root = project_root
        self.llama_available = self._check_llama_availability()
        
    def collect_ai_insights(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collecte des insights IA sur l'état du projet."""
        try:
            if not self.llama_available:
                return self._get_fallback_insights(project_data)
            
            # Préparation du contexte pour Llama
            context = self._prepare_analysis_context(project_data)
            
            # Analyse par Llama 7B
            ai_analysis = self._query_llama_analysis(context)
            
            # Parsing et structuration des résultats
            structured_insights = self._structure_ai_insights(ai_analysis)
            
            return structured_insights
            
        except Exception as e:
            logger.error(f"Erreur collecte intelligence IA: {e}")
            return self._get_error_insights()
    
    def generate_action_recommendations(self, violations_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Génère des recommandations d'action via IA."""
        if not self.llama_available:
            return self._get_fallback_recommendations()
        
        try:
            # Contexte pour recommandations
            recommendation_prompt = self._build_recommendation_prompt(violations_data)
            
            # Requête à Llama
            ai_recommendations = self._query_llama_recommendations(recommendation_prompt)
            
            # Parsing des recommandations
            return self._parse_recommendations(ai_recommendations)
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations IA: {e}")
            return self._get_fallback_recommendations()
    
    def analyze_code_patterns(self, hotspots: List[Dict]) -> Dict[str, Any]:
        """Analyse les patterns de code via IA pour identification des causes."""
        if not self.llama_available or not hotspots:
            return {"analysis": "Analyse IA non disponible", "patterns": []}
        
        try:
            # Contexte d'analyse des patterns
            patterns_prompt = self._build_patterns_prompt(hotspots)
            
            # Analyse par Llama
            pattern_analysis = self._query_llama_patterns(patterns_prompt)
            
            return {
                "analysis": pattern_analysis,
                "patterns": self._extract_patterns(pattern_analysis),
                "root_causes": self._extract_root_causes(pattern_analysis)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse patterns IA: {e}")
            return {"analysis": "Erreur d'analyse", "patterns": []}
    
    def _check_llama_availability(self) -> bool:
        """Vérifie la disponibilité de Llama via ollama."""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and 'llama' in result.stdout.lower()
        except Exception:
            logger.warning("Llama/Ollama non disponible - mode fallback")
            return False
    
    def _prepare_analysis_context(self, project_data: Dict[str, Any]) -> str:
        """Prépare le contexte d'analyse pour Llama."""
        constitutional = project_data.get('constitutional', {})
        git_status = project_data.get('git_status', {})
        
        context = f"""
        ANALYSE DU PROJET AGI - CONTEXTE CONSTITUTIONNEL
        
        État Constitutionnel:
        - Violations critiques: {constitutional.get('critical_violations', 0)}
        - Violations totales: {constitutional.get('total_violations', 0)}
        - Taux de conformité: {constitutional.get('compliance_rate', 0)}%
        
        État Git:
        - Statut: {git_status.get('status_text', 'Inconnu')}
        - Fichiers modifiés: {git_status.get('modified_files', 0)}
        
        Question: Analyse la santé de ce projet et identifie les 3 actions prioritaires.
        """
        
        return context
    
    def _query_llama_analysis(self, context: str) -> str:
        """Lance une requête d'analyse à Llama."""
        try:
            result = subprocess.run([
                'ollama', 'run', 'llama2:7b', context
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Erreur Llama: {result.stderr}")
                return "Analyse indisponible"
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout Llama - analyse interrompue")
            return "Analyse interrompue (timeout)"
        except Exception as e:
            logger.error(f"Erreur exécution Llama: {e}")
            return "Erreur d'analyse"
    
    def _structure_ai_insights(self, ai_analysis: str) -> Dict[str, Any]:
        """Structure les insights IA en format exploitable."""
        # Parsing simple de la réponse Llama
        insights = {
            "analysis_summary": ai_analysis[:200] + "..." if len(ai_analysis) > 200 else ai_analysis,
            "confidence_level": "Modéré" if self.llama_available else "Faible",
            "key_findings": self._extract_key_findings(ai_analysis),
            "priority_actions": self._extract_priority_actions(ai_analysis),
            "risk_assessment": self._extract_risk_assessment(ai_analysis)
        }
        
        return insights
    
    def _build_recommendation_prompt(self, violations_data: Dict[str, Any]) -> str:
        """Construit le prompt pour les recommandations."""
        violations = violations_data.get('violations', [])
        top_violations = violations[:5] if violations else []
        
        prompt = f"""
        RECOMMANDATIONS POUR CORRECTION CONSTITUTIONNELLE
        
        Top 5 violations:
        {json.dumps(top_violations, indent=2)}
        
        Génère 3 recommandations d'action spécifiques et priorisées.
        """
        
        return prompt
    
    def _query_llama_recommendations(self, prompt: str) -> str:
        """Requête spécifique pour recommandations."""
        return self._query_llama_analysis(prompt)
    
    def _query_llama_patterns(self, prompt: str) -> str:
        """Requête spécifique pour analyse de patterns."""
        return self._query_llama_analysis(prompt)
    
    def _build_patterns_prompt(self, hotspots: List[Dict]) -> str:
        """Construit le prompt pour l'analyse de patterns."""
        hotspots_summary = []
        for hotspot in hotspots[:3]:
            hotspots_summary.append(f"- {hotspot[0]}: {hotspot[1]} modifications")
        
        prompt = f"""
        ANALYSE DES PATTERNS DE MODIFICATION
        
        Fichiers les plus modifiés:
        {chr(10).join(hotspots_summary)}
        
        Identifie les patterns et causes racines possibles.
        """
        
        return prompt
    
    def _extract_key_findings(self, analysis: str) -> List[str]:
        """Extrait les points clés de l'analyse."""
        # Parsing simple - recherche de listes ou points
        findings = []
        lines = analysis.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*') or line.startswith('1.'):
                findings.append(line.lstrip('-*123456789. '))
        
        return findings[:3] if findings else ["Analyse en cours"]
    
    def _extract_priority_actions(self, analysis: str) -> List[str]:
        """Extrait les actions prioritaires."""
        # Recherche de mots-clés d'action
        action_keywords = ['action', 'recommand', 'priorité', 'urgent', 'immédiat']
        actions = []
        
        lines = analysis.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in action_keywords):
                actions.append(line.strip())
        
        return actions[:3] if actions else ["Maintenance continue"]
    
    def _extract_risk_assessment(self, analysis: str) -> str:
        """Extrait l'évaluation du risque."""
        risk_keywords = {
            'critique': 'CRITIQUE',
            'urgent': 'ÉLEVÉ', 
            'attention': 'MODÉRÉ',
            'stable': 'FAIBLE'
        }
        
        analysis_lower = analysis.lower()
        for keyword, risk_level in risk_keywords.items():
            if keyword in analysis_lower:
                return risk_level
        
        return 'MODÉRÉ'
    
    def _parse_recommendations(self, recommendations_text: str) -> List[Dict[str, str]]:
        """Parse les recommandations en format structuré."""
        recommendations = []
        lines = recommendations_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith(str(i+1))):
                recommendations.append({
                    "title": f"Recommandation {len(recommendations)+1}",
                    "description": line.lstrip('-123456789. '),
                    "priority": "HIGH" if i < 2 else "MEDIUM"
                })
        
        return recommendations[:3]
    
    def _extract_patterns(self, analysis: str) -> List[str]:
        """Extrait les patterns identifiés."""
        # Recherche de patterns dans l'analyse
        pattern_keywords = ['pattern', 'tendance', 'récurrent', 'fréquent']
        patterns = []
        
        for line in analysis.split('\n'):
            if any(keyword in line.lower() for keyword in pattern_keywords):
                patterns.append(line.strip())
        
        return patterns[:3]
    
    def _extract_root_causes(self, analysis: str) -> List[str]:
        """Extrait les causes racines identifiées."""
        cause_keywords = ['cause', 'origine', 'source', 'problème']
        causes = []
        
        for line in analysis.split('\n'):
            if any(keyword in line.lower() for keyword in cause_keywords):
                causes.append(line.strip())
        
        return causes[:2]
    
    def _get_fallback_insights(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insights de fallback sans IA."""
        constitutional = project_data.get('constitutional', {})
        critical = constitutional.get('critical_violations', 0)
        
        return {
            "analysis_summary": f"Analyse basique: {critical} violations critiques détectées",
            "confidence_level": "Règles prédéfinies",
            "key_findings": [
                "Utilisation des règles de scoring standard",
                "Analyse basée sur les métriques constitutionnelles",
                "Recommandations génériques appliquées"
            ],
            "priority_actions": [
                "Traiter les violations critiques en priorité",
                "Maintenir la surveillance constitutionnelle",
                "Appliquer les bonnes pratiques"
            ],
            "risk_assessment": "MODÉRÉ" if critical < 10 else "ÉLEVÉ"
        }
    
    def _get_fallback_recommendations(self) -> List[Dict[str, str]]:
        """Recommandations de fallback."""
        return [
            {
                "title": "Audit constitutionnel",
                "description": "Lancer un audit complet des violations",
                "priority": "HIGH"
            },
            {
                "title": "Refactorisation ciblée", 
                "description": "Traiter les fichiers les plus problématiques",
                "priority": "MEDIUM"
            },
            {
                "title": "Surveillance continue",
                "description": "Maintenir la supervision constitutionnelle",
                "priority": "LOW"
            }
        ]
    
    def _get_error_insights(self) -> Dict[str, Any]:
        """Insights d'erreur."""
        return {
            "analysis_summary": "Erreur de collecte d'intelligence",
            "confidence_level": "Aucun",
            "key_findings": ["Système d'analyse indisponible"],
            "priority_actions": ["Vérifier la configuration IA"],
            "risk_assessment": "INDÉTERMINÉ"
        }
