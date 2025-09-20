#!/usr/bin/env python3
"""
📋 Le Concierge - Générateur de Rapports
Directive SYNTAX-CORRECTOR-v1.0

Mission: Générer des rapports détaillés des corrections
Auteur: Le Concierge Reporter (AGI Architecture Bot)
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class ConciergeReporter:
    """📋 Générateur de rapports de correction"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.report_data = {}

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"📋 {message}")

    def load_correction_data(self) -> Dict[str, Any]:
        """Charger les données de correction depuis les logs"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "corrections": [],
            "errors": [],
            "summary": {}
        }

        # Charger depuis le log JSON si disponible
        if Path("concierge_log.json").exists():
            try:
                with open("concierge_log.json", 'r') as f:
                    data.update(json.load(f))
                self.log("Données de correction chargées depuis concierge_log.json")
            except Exception as e:
                self.log(f"Erreur chargement log: {e}")

        # Charger depuis le rapport de correction si disponible
        if Path("correction_report.md").exists():
            try:
                with open("correction_report.md", 'r') as f:
                    content = f.read()
                    data["markdown_report"] = content
                self.log("Rapport Markdown chargé")
            except Exception as e:
                self.log(f"Erreur chargement rapport: {e}")

        return data

    def generate_detailed_report(self, data: Dict[str, Any]) -> str:
        """Générer un rapport détaillé"""
        timestamp = data.get("timestamp", datetime.now().isoformat())
        corrections = data.get("corrections", [])
        errors = data.get("errors", [])
        summary = data.get("summary", {})

        report = f"""# 🧹 Rapport Détaillé Le Concierge

**Timestamp:** {timestamp}
**Directive:** SYNTAX-CORRECTOR-v1.0

---

## 📊 Résumé Exécutif

| Métrique | Valeur |
|----------|---------|
| **Corrections Totales** | {summary.get('total_corrections', 0)} |
| **Corrections Réussies** | {summary.get('successful_corrections', 0)} |
| **Erreurs Rencontrées** | {summary.get('total_errors', 0)} |
| **Taux de Réussite** | {summary.get('success_rate', 0):.1f}% |

---

## 🛠️ Outils Utilisés

"""

        tools_used = summary.get('tools_used', {})
        if tools_used:
            for tool, count in tools_used.items():
                emoji = {"autoflake": "🗑️", "isort": "📋", "black": "⚫", "autopep8": "🔧"}.get(tool, "🔨")
                report += f"- **{emoji} {tool}**: {count} application(s)\n"
        else:
            report += "Aucun outil utilisé.\n"

        report += "\n---\n\n"

        # Détails des corrections
        if corrections:
            report += "## 📝 Détails des Corrections\n\n"

            files_corrected = {}
            for correction in corrections:
                file_path = correction.get('file', 'Inconnu')
                if file_path not in files_corrected:
                    files_corrected[file_path] = []
                files_corrected[file_path].append(correction)

            for file_path, file_corrections in files_corrected.items():
                successful = [c for c in file_corrections if c.get('success', False)]
                failed = [c for c in file_corrections if not c.get('success', False)]

                status = "✅" if len(failed) == 0 else "⚠️" if len(successful) > 0 else "❌"

                report += f"### {status} `{file_path}`\n\n"

                if successful:
                    report += "**Corrections réussies:**\n"
                    for correction in successful:
                        tool = correction.get('tool', 'Inconnu')
                        timestamp = correction.get('timestamp', '')
                        report += f"- ✅ {tool} ({timestamp})\n"

                if failed:
                    report += "\n**Corrections échouées:**\n"
                    for correction in failed:
                        tool = correction.get('tool', 'Inconnu')
                        details = correction.get('details', 'Aucun détail')
                        report += f"- ❌ {tool}: {details}\n"

                report += "\n"

        # Erreurs détaillées
        if errors:
            report += "\n## ⚠️ Erreurs Rencontrées\n\n"

            for error in errors:
                file_path = error.get('file', 'Inconnu')
                error_type = error.get('type', 'Erreur')
                message = error.get('message', 'Aucun message')
                timestamp = error.get('timestamp', '')

                report += f"### ❌ {file_path}\n"
                report += f"- **Type**: {error_type}\n"
                report += f"- **Message**: {message}\n"
                report += f"- **Timestamp**: {timestamp}\n\n"

        # Recommandations
        report += self.generate_recommendations(summary, errors)

        # Footer
        report += f"""

---

*Rapport généré par 🧹 Le Concierge Reporter*
*Système de correction automatique constitutionnelle*
"""

        return report

    def generate_recommendations(self, summary: Dict[str, Any], errors: List[Dict[str, Any]]) -> str:
        """Générer des recommandations basées sur les résultats"""
        recommendations = "\n## 💡 Recommandations\n\n"

        success_rate = summary.get('success_rate', 0)
        total_errors = summary.get('total_errors', 0)

        if success_rate >= 95:
            recommendations += "🎉 **Excellent !** Taux de réussite très élevé. Le code suit bien les standards.\n\n"
        elif success_rate >= 80:
            recommendations += "👍 **Bon travail !** La plupart des corrections ont réussi. Quelques ajustements mineurs nécessaires.\n\n"
        elif success_rate >= 60:
            recommendations += "⚠️ **Attention !** Plusieurs corrections ont échoué. Révision manuelle recommandée.\n\n"
        else:
            recommendations += "🚨 **Action requise !** Nombreux échecs de correction. Intervention manuelle urgente.\n\n"

        if total_errors > 0:
            recommendations += "### 🔧 Actions Suggérées\n\n"

            # Analyser les types d'erreurs communes
            error_types = {}
            for error in errors:
                error_type = error.get('type', 'Inconnu')
                error_types[error_type] = error_types.get(error_type, 0) + 1

            if 'SyntaxError' in error_types:
                recommendations += "- 🐍 **Erreurs de syntaxe**: Vérifier manuellement la structure du code\n"

            if 'IndentationError' in error_types:
                recommendations += "- 📏 **Problèmes d'indentation**: Uniformiser l'utilisation des espaces/tabulations\n"

            if 'ImportError' in error_types:
                recommendations += "- 📦 **Problèmes d'imports**: Vérifier les dépendances et la structure des modules\n"

            recommendations += "- 🔍 **Review manuelle**: Examiner les fichiers en erreur individuellement\n"
            recommendations += "- 🧪 **Tests locaux**: Exécuter `python -m py_compile` sur les fichiers problématiques\n"

        return recommendations

    def generate_json_report(self, data: Dict[str, Any]) -> str:
        """Générer un rapport JSON structuré"""
        json_report = {
            "concierge_report": {
                "metadata": {
                    "timestamp": data.get("timestamp"),
                    "directive": "SYNTAX-CORRECTOR-v1.0",
                    "generator": "Le Concierge Reporter"
                },
                "summary": data.get("summary", {}),
                "corrections": data.get("corrections", []),
                "errors": data.get("errors", []),
                "recommendations": self.extract_recommendations(data)
            }
        }

        return json.dumps(json_report, indent=2, ensure_ascii=False)

    def extract_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Extraire les recommandations sous forme de liste"""
        summary = data.get("summary", {})
        errors = data.get("errors", [])
        success_rate = summary.get('success_rate', 0)

        recommendations = []

        if success_rate >= 95:
            recommendations.append("Excellent taux de réussite - continuer les bonnes pratiques")
        elif success_rate >= 80:
            recommendations.append("Bon taux de réussite - ajustements mineurs nécessaires")
        elif success_rate >= 60:
            recommendations.append("Taux de réussite moyen - révision manuelle recommandée")
        else:
            recommendations.append("Taux de réussite faible - intervention manuelle urgente")

        if errors:
            recommendations.append("Examiner manuellement les fichiers en erreur")
            recommendations.append("Exécuter des tests de compilation locaux")

        return recommendations


def parse_arguments() -> argparse.Namespace:
    """Parser les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="📋 Le Concierge Reporter - Générateur de Rapports"
    )

    parser.add_argument(
        '--output',
        type=str,
        default='concierge_detailed_report.md',
        help='Fichier de sortie pour le rapport détaillé'
    )

    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'both'],
        default='both',
        help='Format du rapport de sortie'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbose'
    )

    return parser.parse_args()


def main():
    """Point d'entrée principal"""
    args = parse_arguments()

    print("📋 Le Concierge Reporter - Génération des rapports...")

    reporter = ConciergeReporter(args.verbose)

    # Charger les données
    data = reporter.load_correction_data()

    # Générer les rapports selon le format demandé
    if args.format in ['markdown', 'both']:
        markdown_report = reporter.generate_detailed_report(data)

        output_path = args.output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)

        print(f"✅ Rapport Markdown généré: {output_path}")

    if args.format in ['json', 'both']:
        json_report = reporter.generate_json_report(data)

        json_output_path = args.output.replace('.md', '.json')
        with open(json_output_path, 'w', encoding='utf-8') as f:
            f.write(json_report)

        print(f"✅ Rapport JSON généré: {json_output_path}")

    print("📋 Mission accomplie - Le Concierge Reporter")


if __name__ == "__main__":
    main()
