#!/usr/bin/env python3
"""
🔍 Le Stratège - Analyseur de Progression de Fusion EVE
Directive FUSION-PROGRESS-v1.0

Mission: Transformer la boîte noire de fusion en intelligence stratégique
Auteur: Le Stratège (AGI Architecture Bot)
"""

import os
import sys
import json
import ast
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, NamedTuple
from dataclasses import dataclass
from collections import defaultdict

try:
    from radon.complexity import cc_visit
    from radon.metrics import h_visit, mi_visit
    from tabulate import tabulate
except ImportError as e:
    print(f"❌ Dépendance manquante: {e}")
    print("💡 Installer avec: pip install radon tabulate")
    sys.exit(1)


@dataclass
class FileAnalysis:
    """Analyse complète d'un fichier Python"""
    path: str
    lines: int
    is_violation: bool
    excess_lines: int
    complexity: int
    maintainability: float
    size_category: str


@dataclass
class ModuleReport:
    """Rapport d'un module EVE"""
    name: str
    total_files: int
    violations: int
    conformity_rate: float
    total_complexity: int
    avg_complexity: float
    quick_wins: List[FileAnalysis]
    major_challenges: List[FileAnalysis]


class FusionStrategist:
    """🎯 Le Stratège - Intelligence de Fusion EVE"""
    
    def __init__(self, eve_root: str, report_dir: str):
        self.eve_root = Path(eve_root)
        self.report_dir = Path(report_dir)
        self.compliance_limit = 200  # COMP-ARC-001
        self.modules_data = {}
        self.global_stats = {}
        
    def analyze_file_complexity(self, file_path: Path) -> Tuple[int, float]:
        """Calcule la complexité cyclomatique et la maintenabilité"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
                
            # Complexité cyclomatique
            complexity_blocks = cc_visit(code)
            total_complexity = sum(block.complexity for block in complexity_blocks)
            
            # Index de maintenabilité
            try:
                mi_score = mi_visit(code, multi=True)
                maintainability = mi_score.mi if hasattr(mi_score, 'mi') else 0
            except:
                maintainability = 0
                
            return total_complexity, maintainability
            
        except Exception as e:
            print(f"⚠️  Erreur analyse {file_path}: {e}")
            return 0, 0
    
    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyse complète d'un fichier Python"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = len(f.readlines())
                
            is_violation = lines > self.compliance_limit
            excess_lines = max(0, lines - self.compliance_limit)
            
            complexity, maintainability = self.analyze_file_complexity(file_path)
            
            # Catégorisation par taille
            if lines <= 250:
                size_category = "quick_win"
            elif lines <= 500:
                size_category = "medium"
            else:
                size_category = "major_challenge"
                
            return FileAnalysis(
                path=str(file_path.relative_to(self.eve_root)),
                lines=lines,
                is_violation=is_violation,
                excess_lines=excess_lines,
                complexity=complexity,
                maintainability=maintainability,
                size_category=size_category
            )
            
        except Exception as e:
            print(f"⚠️  Erreur lecture {file_path}: {e}")
            return None
    
    def discover_modules(self) -> List[str]:
        """Découvre les modules principaux d'EVE"""
        if not self.eve_root.exists():
            print(f"❌ Dossier EVE non trouvé: {self.eve_root}")
            return []
            
        modules = []
        for item in self.eve_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Vérifier s'il contient des fichiers Python
                py_files = list(item.glob('**/*.py'))
                if py_files:
                    modules.append(item.name)
                    
        print(f"🔍 Modules détectés: {modules}")
        return sorted(modules)
    
    def analyze_module(self, module_name: str) -> ModuleReport:
        """Analyse complète d'un module EVE"""
        module_path = self.eve_root / module_name
        python_files = list(module_path.glob('**/*.py'))
        
        print(f"📊 Analyse module {module_name}: {len(python_files)} fichiers")
        
        file_analyses = []
        for py_file in python_files:
            analysis = self.analyze_file(py_file)
            if analysis:
                file_analyses.append(analysis)
        
        if not file_analyses:
            return ModuleReport(
                name=module_name,
                total_files=0,
                violations=0,
                conformity_rate=100.0,
                total_complexity=0,
                avg_complexity=0,
                quick_wins=[],
                major_challenges=[]
            )
        
        # Calculs statistiques
        violations = [f for f in file_analyses if f.is_violation]
        total_files = len(file_analyses)
        violation_count = len(violations)
        conformity_rate = ((total_files - violation_count) / total_files) * 100
        
        total_complexity = sum(f.complexity for f in file_analyses)
        avg_complexity = total_complexity / total_files if total_files > 0 else 0
        
        # Quick Wins: violations petites (201-250 lignes)
        quick_wins = sorted(
            [f for f in violations if 201 <= f.lines <= 250],
            key=lambda x: x.lines
        )[:5]
        
        # Défis Majeurs: fichiers les plus longs et complexes
        major_challenges = sorted(
            violations,
            key=lambda x: (x.lines + x.complexity),
            reverse=True
        )[:3]
        
        return ModuleReport(
            name=module_name,
            total_files=total_files,
            violations=violation_count,
            conformity_rate=conformity_rate,
            total_complexity=total_complexity,
            avg_complexity=avg_complexity,
            quick_wins=quick_wins,
            major_challenges=major_challenges
        )
    
    def generate_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Génère une barre de progression textuelle"""
        filled = int((percentage / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def generate_report(self, modules_reports: List[ModuleReport]) -> str:
        """Génère le rapport stratégique complet"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculs globaux
        total_files = sum(r.total_files for r in modules_reports)
        total_violations = sum(r.violations for r in modules_reports)
        global_conformity = ((total_files - total_violations) / total_files) * 100 if total_files > 0 else 100
        total_complexity = sum(r.total_complexity for r in modules_reports)
        
        report_content = f"""# 🔍 RAPPORT STRATÉGIQUE EVE - Le Stratège
**Analyse de Progression de Fusion**  
**Timestamp:** {timestamp}  
**Directive:** FUSION-PROGRESS-v1.0  

---

## 📊 VISION GLOBALE ÉCOSYSTÈME EVE

| Métrique | Valeur | Statut |
|----------|---------|---------|
| **Fichiers Totaux** | {total_files:,} | 📁 |
| **Conformité Globale** | {global_conformity:.1f}% | {'🟢' if global_conformity >= 90 else '🟡' if global_conformity >= 70 else '🔴'} |
| **Violations Totales** | {total_violations:,} | {'🟢' if total_violations < 100 else '🟡' if total_violations < 500 else '🔴'} |
| **Complexité Globale** | {total_complexity:,} | 🧠 |

{self.generate_progress_bar(global_conformity, 30)}

---

## 🏗️ ANALYSE PAR MODULE

"""
        
        # Tableau récapitulatif des modules
        module_table = []
        for module_report in sorted(modules_reports, key=lambda x: x.conformity_rate, reverse=True):
            status_icon = "🟢" if module_report.conformity_rate >= 90 else "🟡" if module_report.conformity_rate >= 70 else "🔴"
            module_table.append([
                f"{status_icon} {module_report.name}",
                f"{module_report.total_files:,}",
                f"{module_report.violations:,}",
                f"{module_report.conformity_rate:.1f}%",
                f"{module_report.avg_complexity:.1f}",
                self.generate_progress_bar(module_report.conformity_rate, 15)
            ])
        
        report_content += tabulate(
            module_table,
            headers=["Module", "Fichiers", "Violations", "Conformité", "Complexité Moy.", "Progression"],
            tablefmt="pipe"
        )
        
        report_content += "\n\n---\n\n"
        
        # Détails par module
        for module_report in modules_reports:
            report_content += f"""### 🧩 Module: {module_report.name}

**Conformité:** {self.generate_progress_bar(module_report.conformity_rate, 25)}

| Métrique | Valeur |
|----------|---------|
| Fichiers Total | {module_report.total_files:,} |
| Violations | {module_report.violations:,} |
| Conformité | {module_report.conformity_rate:.1f}% |
| Complexité Totale | {module_report.total_complexity:,} |
| Complexité Moyenne | {module_report.avg_complexity:.1f} |

"""
            
            # Quick Wins
            if module_report.quick_wins:
                report_content += "#### 🎯 Quick Wins (Corrections Rapides)\n\n"
                for i, qw in enumerate(module_report.quick_wins, 1):
                    report_content += f"{i}. **{qw.path}** - {qw.lines} lignes (+{qw.excess_lines}) - Complexité: {qw.complexity}\n"
                report_content += "\n"
            
            # Défis Majeurs
            if module_report.major_challenges:
                report_content += "#### 🏔️ Défis Majeurs (Chantiers Long Terme)\n\n"
                for i, mc in enumerate(module_report.major_challenges, 1):
                    report_content += f"{i}. **{mc.path}** - {mc.lines} lignes (+{mc.excess_lines}) - Complexité: {mc.complexity}\n"
                report_content += "\n"
            
            report_content += "---\n\n"
        
        # Recommandations stratégiques
        best_module = max(modules_reports, key=lambda x: x.conformity_rate)
        worst_module = min(modules_reports, key=lambda x: x.conformity_rate)
        most_quick_wins = max(modules_reports, key=lambda x: len(x.quick_wins))
        
        report_content += f"""## 🎯 INTELLIGENCE STRATÉGIQUE

### 📈 Recommandations Basées sur les Données

1. **Champion de Conformité:** `{best_module.name}` ({best_module.conformity_rate:.1f}%) - Modèle à suivre
2. **Zone Critique:** `{worst_module.name}` ({worst_module.conformity_rate:.1f}%) - Attention prioritaire
3. **Potentiel Quick Wins:** `{most_quick_wins.name}` ({len(most_quick_wins.quick_wins)} opportunités)

### 🎲 Stratégies Recommandées

| Stratégie | Avantages | Inconvénients | Impact Estimé |
|-----------|-----------|---------------|---------------|
| **Quick Wins First** | Amélioration rapide du score | Impact limité long terme | +5-10% conformité |
| **Focus Module Critique** | Résolution problème majeur | Effort important | +15-25% conformité |
| **Approche Hybride** | Équilibre gains/effort | Complexité gestion | +10-15% conformité |

---

## 🤔 Question Stratégique pour l'Architecte

**Architecte, basé sur ce rapport stratégique :**

1. **Quel module devrions-nous prioriser** pour la prochaine phase de refactorisation ?
   - 🎯 **{most_quick_wins.name}** pour {len(most_quick_wins.quick_wins)} quick wins rapides ?
   - 🔥 **{worst_module.name}** pour résoudre la zone critique ?
   - 🏆 **{best_module.name}** pour pousser l'excellence ?

2. **Quelle stratégie adopter :**
   - Se concentrer sur les **Quick Wins** pour améliorer rapidement le score global ?
   - Attaquer un **Défi Majeur** pour un impact architectural profond ?
   - Adopter une **approche hybride** mélangeant les deux ?

3. **Ressources recommandées :**
   - Effort estimé Quick Wins: **1-2 semaines** 
   - Effort estimé Défi Majeur: **1-2 mois**
   - Impact conformité Quick Wins: **+{len(most_quick_wins.quick_wins)*2}%**
   - Impact conformité Défi Majeur: **+{worst_module.violations*0.5:.0f}%**

**💡 Ma recommandation Le Stratège:** Commencer par {len(most_quick_wins.quick_wins)} quick wins du module `{most_quick_wins.name}` pour un gain de motivation, puis attaquer `{worst_module.name}` avec l'élan créé.

---

*Rapport généré par 🔍 Le Stratège - Intelligence de Fusion EVE*  
*Prochaine analyse: {(datetime.now().replace(hour=2, minute=0, second=0) + 
                      __import__('datetime').timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report_content
    
    def save_raw_data(self, modules_reports: List[ModuleReport]) -> None:
        """Sauvegarde les données brutes pour visualisations"""
        raw_data = {
            'timestamp': datetime.now().isoformat(),
            'global_stats': self.global_stats,
            'modules': []
        }
        
        for report in modules_reports:
            module_data = {
                'name': report.name,
                'total_files': report.total_files,
                'violations': report.violations,
                'conformity_rate': report.conformity_rate,
                'total_complexity': report.total_complexity,
                'avg_complexity': report.avg_complexity,
                'quick_wins': [
                    {
                        'path': qw.path,
                        'lines': qw.lines,
                        'excess': qw.excess_lines,
                        'complexity': qw.complexity
                    }
                    for qw in report.quick_wins
                ],
                'major_challenges': [
                    {
                        'path': mc.path,
                        'lines': mc.lines,
                        'excess': mc.excess_lines,
                        'complexity': mc.complexity
                    }
                    for mc in report.major_challenges
                ]
            }
            raw_data['modules'].append(module_data)
        
        assets_dir = self.report_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        
        with open(assets_dir / 'fusion_data.json', 'w') as f:
            json.dump(raw_data, f, indent=2)
        
        print(f"💾 Données sauvegardées: {assets_dir / 'fusion_data.json'}")
    
    def execute_strategic_analysis(self) -> None:
        """🎯 Mission principale: Analyse stratégique complète"""
        print("🔍 Le Stratège - Début de l'analyse stratégique EVE")
        print(f"📁 Racine EVE: {self.eve_root}")
        print(f"📊 Rapports: {self.report_dir}")
        
        # Créer le dossier de rapports
        self.report_dir.mkdir(exist_ok=True)
        
        # Découverte des modules
        modules = self.discover_modules()
        if not modules:
            print("❌ Aucun module EVE détecté")
            return
        
        # Analyse de chaque module
        modules_reports = []
        for module in modules:
            print(f"\n🧩 Analyse module: {module}")
            module_report = self.analyze_module(module)
            modules_reports.append(module_report)
            print(f"✅ {module}: {module_report.conformity_rate:.1f}% conformité")
        
        # Génération du rapport
        print("\n📋 Génération du rapport stratégique...")
        report_content = self.generate_report(modules_reports)
        
        # Sauvegarde
        report_path = self.report_dir / 'FUSION_PROGRESS_REPORT.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Sauvegarde données brutes
        self.save_raw_data(modules_reports)
        
        print(f"✅ Rapport généré: {report_path}")
        print("🎯 Mission accomplie - Le Stratège")


def main():
    """Point d'entrée principal"""
    eve_root = os.environ.get('EVE_ROOT', 'eve')
    report_dir = os.environ.get('REPORT_DIR', 'reports')
    
    strategist = FusionStrategist(eve_root, report_dir)
    strategist.execute_strategic_analysis()


if __name__ == "__main__":
    main()
