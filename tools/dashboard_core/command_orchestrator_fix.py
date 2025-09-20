# Patch rapide pour corriger le bug de rendu
# Ajouter après la ligne 165 environ dans _render_command_center

# Dans le contexte, ajouter les variables manquantes avant le rendu
strategic_context = self._collect_strategic_intelligence()
advanced_analysis = self._perform_advanced_analysis(strategic_context)

# Contexte complet pour le rendu (CORRECTION)
context = {
    'generation_time': datetime.now().strftime("%d/%m/%Y à %H:%M:%S"),
    'ai_model': self.ai_model,
    'constitutional': strategic_context.get('constitutional', {}),
    'git_status': strategic_context.get('git_status', {}),
    'ai_insights': strategic_context.get('ai_insights', {}),
    'strategic_analysis': advanced_analysis.get('strategic_analysis', {}),
    'health_score': advanced_analysis.get('health_score', {'grade': 'C', 'overall_score': 70, 'diagnosis': 'Données limitées'}),
    'file_risks': advanced_analysis.get('file_risks', []),
    'ai_recommendations': [{"title": "Maintenance", "description": "Surveillance continue", "priority": "LOW"}],
    'git_commands': '<div>Aucune action Git requise</div>',
    **action_context
}
