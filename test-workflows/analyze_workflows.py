#!/usr/bin/env python3
"""
🔍 AGI Workflows Analyzer - Analyse détaillée de l'architecture
"""

import yaml
import json
from pathlib import Path
from collections import Counter, defaultdict
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()

def analyze_workflows():
    """Analyse complète des 89 workflows"""
    workflows_dir = Path("../.github/workflows")
    
    if not workflows_dir.exists():
        console.print("❌ Dossier workflows introuvable")
        return
    
    workflows = list(workflows_dir.glob("*.yml"))
    console.print(f"🔍 Analyse de {len(workflows)} workflows...")
    
    # Statistiques par niveau
    levels = defaultdict(list)
    triggers = Counter()
    sizes = []
    
    for workflow_file in workflows:
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
                sizes.append(len(content))
                
                # Déterminer niveau par préfixe
                name = workflow_file.stem
                if name.startswith('00-'):
                    levels[0].append(name)
                elif name.startswith('01-'):
                    levels[1].append(name)
                elif name.startswith('02-'):
                    levels[2].append(name)
                elif name.startswith('03-'):
                    levels[3].append(name)
                elif name.startswith('04-'):
                    levels[4].append(name)
                elif name.startswith('05-'):
                    levels[5].append(name)
                elif name.startswith('06-'):
                    levels[6].append(name)
                elif name.startswith('07-'):
                    levels[7].append(name)
                else:
                    levels[99].append(name)  # Autres
                
                # Parser YAML pour triggers
                try:
                    data = yaml.safe_load(content)
                    if 'on' in data:
                        for trigger in data['on'].keys():
                            triggers[trigger] += 1
                except:
                    pass
                    
        except Exception as e:
            console.print(f"⚠️ Erreur lecture {workflow_file.name}: {e}")
    
    # Affichage des résultats
    tree = Tree("🏗️ [bold]Architecture AGI - 89 Workflows[/bold]")
    
    for level in sorted(levels.keys()):
        if level == 99:
            branch = tree.add(f"🔧 [yellow]Autres ({len(levels[level])} workflows)[/yellow]")
        else:
            level_names = {
                0: "👑 NIVEAU 0 - Maître",
                1: "🎼 NIVEAU 1 - Orchestre", 
                2: "⚔️ NIVEAU 2 - Généraux",
                3: "🔧 NIVEAU 3 - Contremaîtres",
                4: "🏭 NIVEAU 4 - Ouvriers",
                5: "✅ NIVEAU 5 - Qualiticiens",
                6: "⚡ NIVEAU 6 - Travailleurs",
                7: "🎨 NIVEAU 7 - Nettoyeurs"
            }
            branch = tree.add(f"{level_names.get(level, f'Niveau {level}')} ({len(levels[level])} workflows)")
        
        for workflow in sorted(levels[level])[:5]:  # Limite 5 par niveau
            branch.add(f"📄 {workflow}")
        
        if len(levels[level]) > 5:
            branch.add(f"... +{len(levels[level]) - 5} autres")
    
    console.print(tree)
    
    # Tableau statistiques
    table = Table(title="📊 Statistiques Workflows")
    table.add_column("Métrique", style="cyan")
    table.add_column("Valeur", style="green")
    
    table.add_row("Total workflows", str(len(workflows)))
    table.add_row("Taille moyenne", f"{sum(sizes)//len(sizes)} caractères")
    table.add_row("Plus gros workflow", f"{max(sizes)} caractères")
    table.add_row("Triggers les plus fréquents", ", ".join([f"{k}({v})" for k, v in triggers.most_common(3)]))
    
    console.print(table)
    
    return {
        "total": len(workflows),
        "by_level": dict(levels),
        "triggers": dict(triggers)
    }

if __name__ == '__main__':
    analyze_workflows()
