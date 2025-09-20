#!/usr/bin/env python3
"""
COMMAND ORCHESTRATOR FINAL - Module v4.0 conforme AGI
Orchestrateur principal assemblant tous les composants v4.0
Limite: 200 lignes (Délégation complète)
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Imports des composants v4.0
from .widgets.widget_manager import WidgetManager
from .commands.github_commander import GitHubCommander
from .terminal.web_terminal import WebTerminal
from .template_complete_v4 import CompleteTemplateV4

# Imports v3.0 réutilisés
from .constitutional_collector import ConstitutionalDataCollector
from .git_collector import GitDataCollector
from .strategic_analyzer import StrategicAnalyzer
from .scoring_engine import ScoringEngine
from .intelligence_collector import IntelligenceCollector

logger = logging.getLogger(__name__)

class CommandOrchestratorFinal:
    """Orchestrateur principal du poste de commandement v4.0 complet."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_file = project_root / "AGI_Command_Center.html"
        
        # Initialisation des gestionnaires
        self.widget_manager = WidgetManager(project_root)
        self.github_commander = GitHubCommander(project_root)
        self.web_terminal = WebTerminal(project_root)
        self.template_manager = CompleteTemplateV4(project_root)
        
        # Collecteurs de données
        self.constitutional_collector = ConstitutionalDataCollector(project_root)
        self.git_collector = GitDataCollector(project_root)
        self.strategic_analyzer = StrategicAnalyzer()
        self.scoring_engine = ScoringEngine(project_root)
        self.intelligence_collector = IntelligenceCollector(project_root)
    
    def generate_complete_command_center(self) -> bool:
        """Génère le poste de commandement complet v4.0."""
        try:
            logger.info("🎯 Génération Poste de Commandement v4.0 COMPLET")
            
            # Phase 1: Collecte intelligence complète
            data_context = self._collect_complete_intelligence()
            
            # Phase 2: Génération des 9 widgets
            widgets_html = self.widget_manager.generate_all_widgets(data_context)
            
            # Phase 3: Assemblage des widgets en grille
            complete_widgets = self._assemble_widgets_grid(widgets_html)
            
            # Phase 4: Création du template complet
            self.template_manager.create_complete_template()
            
            # Phase 5: Rendu final
            return self._render_complete_dashboard(complete_widgets, data_context)
            
        except Exception as e:
            logger.error(f"Erreur génération complète: {e}")
            return False
    
    def _collect_complete_intelligence(self) -> Dict[str, Any]:
        """Collecte toutes les données pour les 9 widgets."""
        logger.info("📊 Collecte intelligence complète v4.0")
        
        # Données constitutionnelles
        constitutional = self.constitutional_collector.collect_constitutional_data()
        
        # Données Git
        git_status = self.git_collector.collect_git_status()
        hot_spots = self.git_collector.collect_hot_spots()
        recent_activity = self.git_collector.collect_recent_activity()
        
        # Analyse stratégique
        strategic_analysis = self.strategic_analyzer.analyze_constitutional_health(constitutional)
        
        # Scoring global
        health_score = self.scoring_engine.calculate_overall_health_score(constitutional)
        
        # Intelligence IA (avec timeout réduit)
        project_data = {
            'constitutional': constitutional,
            'git_status': git_status,
            'hot_spots': hot_spots,
            'recent_activity': recent_activity
        }
        ai_insights = self.intelligence_collector.collect_ai_insights(project_data)
        
        # Analyse des violations pour widget stratégique
        violations_analysis = self._analyze_violations_for_widget(constitutional)
        
        # Métriques de code (placeholder)
        code_metrics = self._get_code_metrics_placeholder()
        
        # Tendances (placeholder)
        trends = {'trend_direction': 'stable', 'percentage': 0}
        
        return {
            'constitutional': constitutional,
            'git_status': git_status,
            'hot_spots': hot_spots,
            'recent_activity': recent_activity,
            'strategic_analysis': strategic_analysis,
            'health_score': health_score,
            'ai_insights': ai_insights,
            'violations_analysis': violations_analysis,
            'code_metrics': code_metrics,
            'trends': trends
        }
    
    def _analyze_violations_for_widget(self, constitutional: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les violations pour le widget stratégique."""
        violations = constitutional.get('violations', [])
        
        # Top 3 lois violées
        law_counts = {}
        for violation in violations:
            law_id = violation.get('law_id', 'UNKNOWN')
            law_counts[law_id] = law_counts.get(law_id, 0) + 1
        
        top_violated_laws = sorted(law_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Top 3 fichiers problématiques
        file_data = {}
        for violation in violations:
            file_path = violation.get('file', 'unknown')
            lines = violation.get('lines', 0)
            excess = violation.get('excess', 0)
            
            if file_path not in file_data:
                file_data[file_path] = {'lines': lines, 'excess': excess, 'count': 0}
            file_data[file_path]['count'] += 1
        
        top_problematic_files = sorted(
            file_data.items(), 
            key=lambda x: x[1]['excess'], 
            reverse=True
        )[:3]
        
        return {
            'top_violated_laws': top_violated_laws,
            'top_problematic_files': top_problematic_files
        }
    
    def _get_code_metrics_placeholder(self) -> Dict[str, Any]:
        """Métriques de code placeholder pour widget exploitation."""
        return {
            'coverage': 'En attente coverage.py',
            'complexity': 'En attente radon',
            'status': 'placeholder'
        }
    
    def _assemble_widgets_grid(self, widgets_html: Dict[str, str]) -> str:
        """Assemble les widgets en grille HTML."""
        # Ordre spécifique des widgets selon la directive
        widget_order = [
            'health_score', 'constitutional_health', 'git_status',
            'strategic_violations', 'recent_activity', 'trend_analysis',
            'code_exploitation', 'ai_recommendations', 'command_terminal'
        ]
        
        assembled_html = ""
        for widget_id in widget_order:
            if widget_id in widgets_html:
                assembled_html += widgets_html[widget_id] + "\n"
        
        return assembled_html
    
    def _render_complete_dashboard(self, widgets_html: str, data_context: Dict[str, Any]) -> bool:
        """Rend le dashboard complet final."""
        try:
            from jinja2 import Template
            
            # Chargement du template complet
            with open(self.template_manager.template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Ajout des fonctions JavaScript pour le terminal
            js_terminal = self._get_terminal_javascript()
            template_content = template_content.replace(
                '</script>',
                js_terminal + '</script>'
            )
            
            template = Template(template_content)
            
            # Contexte de rendu complet
            render_context = {
                'generation_time': datetime.now().strftime("%d/%m/%Y à %H:%M:%S"),
                'widgets_html': widgets_html,
                'server_url': 'http://localhost:5000',
                **data_context
            }
            
            # Rendu final
            html_output = template.render(**render_context)
            
            # Sauvegarde
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_output)
            
            logger.info(f"✅ Poste de Commandement v4.0 COMPLET: {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur rendu final: {e}")
            return False
    
    def _get_terminal_javascript(self) -> str:
        """JavaScript pour le terminal intégré."""
        return '''
        // TERMINAL INTÉGRÉ v4.0
        function initializeTerminal() {
            const terminalInput = document.getElementById('terminal-input');
            if (terminalInput) {
                terminalInput.addEventListener('keypress', handleTerminalInput);
                addTerminalLine('🎯 Terminal AGI v4.0 initialisé - Tapez "help" pour aide');
            }
        }
        
        async function handleTerminalInput(event) {
            if (event.key === 'Enter') {
                const input = event.target;
                const command = input.value.trim();
                
                if (command) {
                    addTerminalLine('agi@command:~$ ' + command);
                    input.value = '';
                    await executeTerminalCommand(command);
                }
            }
        }
        
        async function executeTerminalCommand(command) {
            if (!serverConnected) {
                addTerminalLine('❌ Serveur déconnecté - Commandes limitées');
                executeLocalCommand(command);
                return;
            }
            
            try {
                const response = await fetch('http://localhost:5000/api/terminal/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                
                const result = await response.json();
                
                if (result.output) {
                    addTerminalLine(result.output);
                }
                if (result.error) {
                    addTerminalLine('❌ ' + result.error);
                }
                
            } catch (error) {
                addTerminalLine('❌ Erreur réseau: ' + error.message);
            }
        }
        
        function executeLocalCommand(command) {
            const localCommands = {
                'help': 'Commandes disponibles:\\n  help - Cette aide\\n  clear - Effacer terminal\\n  status - Statut système',
                'clear': 'CLEAR',
                'status': 'Statut: Mode local (serveur déconnecté)'
            };
            
            if (command in localCommands) {
                if (command === 'clear') {
                    clearTerminal();
                } else {
                    addTerminalLine(localCommands[command]);
                }
            } else {
                addTerminalLine('Commande inconnue: ' + command);
            }
        }
        
        function addTerminalLine(text) {
            const output = document.getElementById('terminal-output');
            if (output) {
                output.textContent += text + '\\n';
                output.scrollTop = output.scrollHeight;
            }
        }
        
        function clearTerminal() {
            const output = document.getElementById('terminal-output');
            if (output) {
                output.textContent = '';
                addTerminalLine('🎯 Terminal effacé');
            }
        }
        
        function executeQuickCommand(command) {
            const input = document.getElementById('terminal-input');
            if (input) {
                input.value = command;
                handleTerminalInput({ key: 'Enter', target: input });
            }
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification('📋 Copié: ' + text, 'success');
            });
        }
        '''
