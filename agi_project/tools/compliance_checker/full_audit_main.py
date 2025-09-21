#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_checker/full_audit_main.py
Rôle Fondamental (Conforme iaGOD.json) :
- Point d'entrée principal audit constitutionnel AGI
- Génération rapport console et orchestration finale
- Interface ligne de commande complète
- Taille: <200 lignes MAX
"""

import argparse
import sys
from pathlib import Path
from typing import List

from .full_audit_models import FileAuditResult, ComplianceStatus
from .full_audit_orchestrator import ConstitutionalOrchestrator


class ConstitutionalReporter:
    """Générateur de rapports console pour audit constitutionnel"""
    
    @staticmethod
    def _generate_console_report(results: List[FileAuditResult]) -> str:
        """Génère un rapport console détaillé"""
        lines = []
        lines.append("=" * 80)
        lines.append("  RAPPORT D'AUDIT CONSTITUTIONNEL AGI")
        lines.append("=" * 80)
        
        # Statistiques globales
        total_files = len(results)
        compliant_files = sum(1 for r in results if r.is_compliant())
        total_violations = sum(r.critical_violations + r.warnings for r in results)
        
        lines.append(f"📊 STATISTIQUES GLOBALES:")
        lines.append(f"   • Fichiers analysés: {total_files}")
        lines.append(f"   • Fichiers conformes: {compliant_files}")
        lines.append(f"   • Taux conformité: {(compliant_files/total_files*100):.1f}%" if total_files > 0 else "   • Taux conformité: 0%")
        lines.append(f"   • Violations totales: {total_violations}")
        lines.append("")
        
        # Détail par fichier (violations seulement)
        violation_files = [r for r in results if not r.is_compliant()]
        if violation_files:
            lines.append("🚨 FICHIERS EN VIOLATION:")
            lines.append("-" * 50)
            
            for result in violation_files:
                lines.append(f"📄 {result.file_path}")
                lines.append(f"   Lignes: {result.line_count} | Score: {result.global_score:.1f}%")
                lines.append(f"   Violations critiques: {result.critical_violations} | Avertissements: {result.warnings}")
                
                # Détail des violations
                violations = [d for d in result.directives_results if d.status == ComplianceStatus.VIOLEE]
                for violation in violations[:3]:  # Limiter à 3 violations max par fichier
                    lines.append(f"   ❌ {violation.id}: {violation.description}")
                    lines.append(f"      {violation.details}")
                
                if len(violations) > 3:
                    lines.append(f"   ... et {len(violations) - 3} autres violations")
                lines.append("")
        
        # Fichiers conformes (résumé)
        compliant_files_list = [r for r in results if r.is_compliant()]
        if compliant_files_list:
            lines.append("✅ FICHIERS CONFORMES:")
            lines.append("-" * 30)
            for result in compliant_files_list:
                lines.append(f"   ✅ {Path(result.file_path).name} ({result.line_count} lignes)")
            lines.append("")
        
        # Top violations par type
        lines.append("📈 ANALYSE DES VIOLATIONS:")
        lines.append("-" * 35)
        
        all_violations = []
        for result in results:
            violations = [d for d in result.directives_results if d.status == ComplianceStatus.VIOLEE]
            all_violations.extend(violations)
        
        if all_violations:
            # Compter par type de directive
            violation_counts = {}
            for violation in all_violations:
                key = violation.id
                violation_counts[key] = violation_counts.get(key, 0) + 1
            
            # Trier par fréquence
            sorted_violations = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)
            
            for directive_id, count in sorted_violations[:5]:  # Top 5
                lines.append(f"   {directive_id}: {count} occurrences")
            lines.append("")
        
        # Recommandations
        lines.append("💡 RECOMMANDATIONS:")
        lines.append("-" * 25)
        
        if total_violations > 0:
            lines.append("   1. Prioriser la correction des violations CRITICAL")
            lines.append("   2. Refactoriser les fichiers > 200 lignes")
            lines.append("   3. Améliorer la documentation et type hints")
            lines.append("   4. Renforcer la gestion d'erreurs")
        else:
            lines.append("   ✨ Excellent ! Tous les fichiers respectent la constitution AGI")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("  FIN DU RAPPORT - Constitution AGI respectée ✅" if total_violations == 0 else "  FIN DU RAPPORT - Corrections requises ⚠️")
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """Point d'entrée principal pour l'audit constitutionnel AGI"""
    parser = argparse.ArgumentParser(
        description="Audit constitutionnel complet du générateur AGI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 tools/compliance_checker/full_audit.py --target ./tools/project_initializer/
  python3 tools/compliance_checker/full_audit.py --file specific_file.py
  python3 tools/compliance_checker/full_audit.py --target ./tools/ --output report.json --format json
        """,
    )
    parser.add_argument("--target", type=str, help="Répertoire à auditer")
    parser.add_argument("--file", type=str, help="Fichier spécifique à auditer")
    parser.add_argument("--output", type=str, help="Fichier de sortie pour le rapport")
    parser.add_argument("--format", choices=["console", "json"], default="console", help="Format du rapport")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    
    args = parser.parse_args()
    
    # Validation des arguments
    if not args.target and not args.file:
        print("❌ Erreur: Spécifiez --target ou --file")
        parser.print_help()
        sys.exit(1)
    
    # Initialisation de l'auditeur
    auditor = ConstitutionalOrchestrator(verbose=args.verbose)
    reporter = ConstitutionalReporter()
    
    try:
        # Exécution de l'audit
        if args.file:
            file_path = Path(args.file)
            results = [auditor.audit_file(file_path)]
            print(f"🔍 Audit de: {file_path}")
        else:
            target_dir = Path(args.target)
            results = auditor.audit_directory(target_dir)
            print(f"🔍 Audit du répertoire: {target_dir}")
        
        print(f"📋 {len(results)} fichiers analysés")
        
        # Génération du rapport
        if args.format == "json":
            report = auditor.generate_report(results, "json")
        else:
            report = reporter._generate_console_report(results)
        
        # Sortie du rapport
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Rapport sauvegardé: {args.output}")
        else:
            print(report)
        
        # Code de retour basé sur les violations
        total_critical = sum(r.critical_violations for r in results)
        sys.exit(1 if total_critical > 0 else 0)
        
    except Exception as e:
        print(f"❌ Erreur durant l'audit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
