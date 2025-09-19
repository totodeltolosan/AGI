#!/usr/bin/env python3
"""
Reporter - Générateur de Rapports d'Audit Constitutionnel
==========================================================

CHEMIN: compliance/reporter.py

Rôle Fondamental (Conforme iaGOD.json) :
- Générer rapports d'audit lisibles et actionnables
- Formater sorties console et fichiers selon standards AGI
- Respecter directive < 200 lignes (version optimisée)
"""

import logging
from typing import List, Dict, Any
from pathlib import Path
from .basic_auditor import ViolationReport

class ConstitutionalReporter:
    """Générateur de Rapports Constitutionnels AGI"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_console_report(self, violations: List[ViolationReport]) -> str:
        """Génère un rapport console formaté"""
        if not violations:
            return self._generate_success_report()
        
        report_lines = [
            "🚨 RAPPORT D'AUDIT CONSTITUTIONNEL AGI",
            "=" * 50, "",
            f"📊 STATISTIQUES:",
            f"   • Total violations: {len(violations)}",
            f"   • Violations critiques: {len([v for v in violations if v.severity == 'CRITICAL'])}",
            f"   • Violations moyennes: {len([v for v in violations if v.severity == 'MEDIUM'])}",
            "", "🔍 DÉTAIL DES VIOLATIONS:", "-" * 30
        ]
        
        # Grouper par sévérité et formater
        for severity, name in [("CRITICAL", "CRITIQUES"), ("MEDIUM", "MOYENNES"), ("LOW", "MINEURES")]:
            severity_violations = [v for v in violations if v.severity == severity]
            if severity_violations:
                report_lines.extend(self._format_violations_group(name, severity_violations))
        
        # Recommandations
        report_lines.extend([
            "", "💡 RECOMMANDATIONS:", "-" * 20,
            "1. Corriger les violations CRITIQUES en priorité",
            "2. Refactoriser les fichiers > 200 lignes selon architecture AGI",
            "3. Ajouter les en-têtes constitutionnels manquants",
            "4. Consulter iaGOD.json pour les directives complètes",
            "", "📚 RESSOURCES:",
            "   • Constitution: iaGOD.json",
            "   • Architecture: AGI.md",
            "   • Aide: python run_agi_audit.py --help"
        ])
        
        return "\n".join(report_lines)
    
    def _generate_success_report(self) -> str:
        """Génère un rapport de succès (aucune violation)"""
        return """
✅ AUDIT CONSTITUTIONNEL RÉUSSI

🏛️  CONFORMITÉ TOTALE À iaGOD.json
   Aucune violation constitutionnelle détectée.
   
📊 RÉSULTATS:
   • Fichiers audités: Conformes
   • Limite 200 lignes: Respectée
   • Syntaxe Python: Valide
   • Pratiques AGI: Conformes

🎯 STATUT: PROJET CONSTITUTIOMELLEMENT CONFORME
   
👏 Félicitations ! Votre projet AGI est exemplaire.
"""
    
    def _format_violations_group(self, group_name: str, violations: List[ViolationReport]) -> List[str]:
        """Formate un groupe de violations"""
        lines = [f"", f"❌ VIOLATIONS {group_name} ({len(violations)}):"]
        
        for i, violation in enumerate(violations, 1):
            lines.extend([
                f"", f"   {i}. {violation.law_name} (ID: {violation.law_id})",
                f"      📁 Fichier: {violation.file_path}",
                f"      📍 Ligne: {violation.line_number}",
                f"      📝 Description: {violation.description}"
            ])
            
            if violation.suggested_fix:
                lines.append(f"      💡 Solution: {violation.suggested_fix}")
        
        return lines
    
    def generate_github_comment(self, violations: List[ViolationReport]) -> str:
        """Génère un commentaire GitHub pour Pull Request"""
        if not violations:
            return """## ✅ Audit Constitutionnel Réussi

🏛️ **Conformité Totale à iaGOD.json**

**Statut**: ✅ CONFORME
**Action**: Pull Request approuvée par l'audit constitutionnel
"""
        
        critical_count = len([v for v in violations if v.severity == "CRITICAL"])
        comment_lines = [
            "## 🚨 Audit Constitutionnel Échoué", "",
            f"**Violations détectées**: {len(violations)}",
            f"**Violations critiques**: {critical_count}", "",
            "### 📋 Résumé des Violations", ""
        ]
        
        # Limiter à 5 violations pour éviter les commentaires trop longs
        displayed_violations = violations[:5]
        
        for violation in displayed_violations:
            severity_emoji = {"CRITICAL": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(violation.severity, "⚪")
            comment_lines.extend([
                f"**{severity_emoji} {violation.law_name}**",
                f"- 📁 `{violation.file_path}:{violation.line_number}`",
                f"- 📝 {violation.description}", ""
            ])
        
        if len(violations) > 5:
            comment_lines.append(f"*... et {len(violations) - 5} autres violations*")
        
        comment_lines.extend([
            "", "### 🔧 Actions Requises",
            "1. Corriger les violations critiques avant merge",
            "2. Consulter `iaGOD.json` pour les directives complètes", 
            "3. Relancer l'audit: `python run_agi_audit.py --full`", "",
            "---", "*Audit automatique mandaté par la Loi DEV-TOOL-002 de iaGOD.json*"
        ])
        
        return "\n".join(comment_lines)
    
    def save_detailed_report(self, violations: List[ViolationReport], output_path: Path):
        """Sauvegarde un rapport détaillé dans un fichier"""
        try:
            detailed_report = self.generate_console_report(violations)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(detailed_report)
            self.logger.info(f"Rapport détaillé sauvegardé: {output_path}")
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde rapport {output_path}: {e}")
