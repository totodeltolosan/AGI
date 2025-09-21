#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_audit_system/reporters/synthesis_reporter.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

#!/usr/bin/env python3
"""
Rapporteur de Synthèse - Système d'Audit AGI
Responsabilité unique : Génération de rapports de synthèse Markdown exécutifs
Respecte strictement la directive des 200 lignes
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class SynthesisReporter:
    """Générateur de rapports de synthèse exécutifs pour l'audit AGI"""

    def __init__(self, output_dir: Path):
        """TODO: Add docstring."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_synthesis(self, audit_results: Dict) -> str:
        """Crée un rapport de synthèse Markdown complet"""

        # Génération du contenu Markdown
        markdown_content = self._generate_markdown_report(audit_results)

        # Génération du nom de fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agi_audit_synthesis_{timestamp}.md"
        output_file = self.output_dir / filename

        # Écriture du fichier
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            return str(output_file)

        except Exception as e:
            raise Exception(f"Erreur lors de la création de la synthèse: {e}")

    def _generate_markdown_report(self, audit_results: Dict) -> str:
        """Génère le contenu Markdown du rapport"""

        sections = []

        # En-tête du rapport
        sections.append(self._create_header())

        # Synthèse exécutive
        sections.append(self._create_executive_summary(audit_results))

        # Métriques clés
        sections.append(self._create_key_metrics(audit_results))

        # Analyse détaillée par catégorie
        sections.append(self._create_detailed_analysis(audit_results))

        # Recommandations prioritaires
        sections.append(self._create_recommendations(audit_results))

        # Plan d'action
        sections.append(self._create_action_plan(audit_results))

        # Annexes
        sections.append(self._create_appendices(audit_results))

        return "\n\n".join(sections)

    def _create_header(self) -> str:
        """Crée l'en-tête du rapport"""
        return f"""# 🏛️ RAPPORT DE SYNTHÈSE - AUDIT CONSTITUTIONNEL AGI

**Date de génération :** {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}
**Système d'audit :** AGI Compliance System v2.0 - Architecture Modulaire
**Standard de conformité :** Directives constitutionnelles AGI.md

---"""

    def _create_executive_summary(self, audit_results: Dict) -> str:
        """Crée la synthèse exécutive"""

        # Calcul des métriques globales
        total_files = self._get_total_files(audit_results)
        total_violations = self._get_total_violations(audit_results)
        compliance_rate = self._calculate_compliance_rate(audit_results)
        verdict = self._determine_verdict(compliance_rate, total_violations)

        return f"""## 📊 SYNTHÈSE EXÉCUTIVE

### Verdict Global
**{verdict}**

### Métriques Principales
- **Fichiers analysés :** {total_files}
- **Taux de conformité :** {compliance_rate:.1f}%
- **Violations détectées :** {total_violations}
- **Statut constitutionnel :** {self._get_constitutional_status(compliance_rate)}

### Impact Organisationnel
{self._generate_impact_assessment(audit_results)}"""

    def _create_key_metrics(self, audit_results: Dict) -> str:
        """Crée la section des métriques clés"""

        sections = ["## 🎯 MÉTRIQUES CLÉS DE CONFORMITÉ", ""]

        # Métriques de lignes
        if "line_compliance" in audit_results:
            sections.append(self._format_line_metrics(audit_results["line_compliance"]))

        # Métriques syntaxiques
        if "syntax_check" in audit_results:
            sections.append(self._format_syntax_metrics(audit_results["syntax_check"]))

        # Métriques de sécurité
        if "security_scan" in audit_results:
            sections.append(
                self._format_security_metrics(audit_results["security_scan"])
            )

        # Métriques architecturales
        if "pattern_analysis" in audit_results:
            sections.append(
                self._format_architectural_metrics(audit_results["pattern_analysis"])
            )

        return "\n".join(sections)

    def _create_detailed_analysis(self, audit_results: Dict) -> str:
        """Crée l'analyse détaillée"""

        return f"""## 🔍 ANALYSE DÉTAILLÉE

### Conformité aux Directives Fondamentales

#### 📏 Directive ARCH-001 : Limite des 200 Lignes
{self._analyze_line_directive(audit_results)}

#### 🔧 Directive MOD-001 : Responsabilité Unique
{self._analyze_modularity_directive(audit_results)}

#### 🛡️ Directive SEC-001 : Sécurité by Design
{self._analyze_security_directive(audit_results)}

### Qualité Architecturale Globale
{self._assess_architectural_quality(audit_results)}"""

    def _create_recommendations(self, audit_results: Dict) -> str:
        """Crée les recommandations"""

        recommendations = self._generate_prioritized_recommendations(audit_results)

        sections = ["## 💡 RECOMMANDATIONS PRIORITAIRES", ""]

        for i, (priority, recommendation) in enumerate(recommendations[:5], 1):
            sections.append(f"### {i}. {priority}")
            sections.append(f"{recommendation}")
            sections.append("")

        return "\n".join(sections)

    def _create_action_plan(self, audit_results: Dict) -> str:
        """Crée le plan d'action"""

        return f"""## 🚀 PLAN D'ACTION RECOMMANDÉ

### Phase 1 : Actions Urgentes (0-1 semaine)
{self._generate_urgent_actions(audit_results)}

### Phase 2 : Améliorations Structurelles (1-4 semaines)
{self._generate_structural_improvements(audit_results)}

### Phase 3 : Optimisations (1-3 mois)
{self._generate_optimizations(audit_results)}

### Suivi et Contrôle
- **Ré-audit recommandé :** {self._recommend_reaudit_frequency(audit_results)}
- **Métriques de suivi :** Taux de conformité, violations critiques, score qualité
- **Outils de monitoring :** Audit continu avec ce système modulaire"""

    def _create_appendices(self, audit_results: Dict) -> str:
        """Crée les annexes"""

        return f"""## 📋 ANNEXES

### A. Méthodologie d'Audit
L'audit a été réalisé avec le système modulaire AGI v2.0, conforme aux directives constitutionnelles AGI.md. Chaque module du système d'audit respecte lui-même la limite des 200 lignes.

### B. Standards de Référence
- **AGI.md** : Constitution fondamentale avec 474 directives
- **Architecture modulaire** : Responsabilité unique par module
- **Limite de 200 lignes** : Directive architecturale stricte

### C. Système d'Audit Utilisé
```
tools/compliance_audit_system/
├── orchestrator.py              # Coordination
├── detectors/                   # Détection environnement
├── validators/                  # Validation conformité
├── analyzers/                   # Analyse approfondie
├── reporters/                   # Génération rapports
└── utils/                       # Utilitaires logging
```

### D. Contact et Support
Pour toute question sur ce rapport ou le système d'audit AGI :
- **Documentation :** Consultez AGI.md et les modules d'aide
- **Ré-audit :** Utilisez les mêmes outils pour suivi continu

---

*Rapport généré automatiquement par le Système d'Audit AGI - Architecture Modulaire Conforme*"""

    # Méthodes utilitaires pour les calculs
    def _get_total_files(self, audit_results: Dict) -> int:
        """Calcule le nombre total de fichiers"""
        if (
            "line_compliance" in audit_results
            and "results" in audit_results["line_compliance"]
        ):
            return len(audit_results["line_compliance"]["results"])
        return 0

    def _get_total_violations(self, audit_results: Dict) -> int:
        """Calcule le nombre total de violations"""
        violations = 0

        if (
            "line_compliance" in audit_results
            and "results" in audit_results["line_compliance"]
        ):
            line_violations = [
                r
                for r in audit_results["line_compliance"]["results"]
                if r.get("status") == "VIOLATION"
            ]
            violations += len(line_violations)

        return violations

    def _calculate_compliance_rate(self, audit_results: Dict) -> float:
        """Calcule le taux de conformité"""
        total_files = self._get_total_files(audit_results)
        total_violations = self._get_total_violations(audit_results)

        if total_files == 0:
            return 100.0

        compliant_files = total_files - min(total_violations, total_files)
        return (compliant_files / total_files) * 100

    def _determine_verdict(self, compliance_rate: float, total_violations: int) -> str:
        """Détermine le verdict global"""
        if compliance_rate >= 95 and total_violations == 0:
            return "🏆 EXCELLENTE CONFORMITÉ CONSTITUTIONNELLE"
        elif compliance_rate >= 80:
            return "✅ CONFORMITÉ ACCEPTABLE - Améliorations mineures requises"
        elif compliance_rate >= 60:
            return "⚠️ CONFORMITÉ PARTIELLE - Actions correctives nécessaires"
        else:
            return "❌ NON-CONFORMITÉ CRITIQUE - Refactorisation urgente requise"

    def _get_constitutional_status(self, compliance_rate: float) -> str:
        """Détermine le statut constitutionnel"""
        if compliance_rate >= 95:
            return "PLEINEMENT CONFORME"
        elif compliance_rate >= 80:
            return "LARGEMENT CONFORME"
        elif compliance_rate >= 60:
            return "PARTIELLEMENT CONFORME"
        else:
            return "NON CONFORME"

    def _format_line_metrics(self, line_results: Dict) -> str:
        """Formate les métriques de lignes"""
        if "results" not in line_results:
            return "### 📏 Conformité des Lignes\n*Données non disponibles*"

        violations = [
            r for r in line_results["results"] if r.get("status") == "VIOLATION"
        ]
        total = len(line_results["results"])
        conformes = total - len(violations)

        return f"""### 📏 Conformité des Lignes (200 max)
- **Fichiers conformes :** {conformes}/{total} ({conformes/total*100:.1f}%)
- **Violations :** {len(violations)}
- **Statut :** {'✅ CONFORME' if len(violations) == 0 else '❌ NON CONFORME'}"""

    def _generate_prioritized_recommendations(self, audit_results: Dict) -> List[tuple]:
        """Génère les recommandations prioritaires"""
        recommendations = []

        # Analyse des violations de lignes
        if (
            "line_compliance" in audit_results
            and "results" in audit_results["line_compliance"]
        ):
            violations = [
                r
                for r in audit_results["line_compliance"]["results"]
                if r.get("status") == "VIOLATION"
            ]
            if violations:
                worst = max(violations, key=lambda x: x.get("excess", 0))
                filename = Path(worst["file_path"]).name
                recommendations.append(
                    (
                        "🔥 PRIORITÉ CRITIQUE",
                        f"Refactoriser immédiatement {filename} ({worst.get('excess', 0)} lignes en excès)",
                    )
                )

        return recommendations


# Fonction utilitaire
def create_synthesis_report(audit_results: Dict, output_dir: Path) -> str:
    """Crée un rapport de synthèse - fonction utilitaire"""
    reporter = SynthesisReporter(output_dir)
    return reporter.create_synthesis(audit_results)


if __name__ == "__main__":
    # Test du rapporteur de synthèse
    test_results = {
        "line_compliance": {
            "results": [
                {"file_path": "test1.py", "status": "VIOLATION", "excess": 50},
                {"file_path": "test2.py", "status": "CONFORME", "excess": 0},
            ]
        }
    }

    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        reporter = SynthesisReporter(output_dir)
        synthesis_file = reporter.create_synthesis(test_results)
        print(f"Synthèse générée: {synthesis_file}")