#!/usr/bin/env python3
"""
📈 Le Stratège - Générateur de Visualisations EVE
Complément graphique pour l'analyse stratégique

Mission: Transformer les données en insights visuels
Auteur: Le Stratège (AGI Architecture Bot)
"""

import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import seaborn as sns
    from matplotlib.colors import LinearSegmentedColormap
except ImportError as e:
    print(f"❌ Dépendance manquante: {e}")
    print("💡 Installer avec: pip install matplotlib seaborn")
    exit(1)

# Configuration graphique
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ProgressVisualizer:
    """📊 Générateur de visualisations stratégiques"""

    def __init__(self, report_dir: str):
        self.report_dir = Path(report_dir)
        self.assets_dir = self.report_dir / 'assets'
        self.data = None

        # Configuration couleurs
        self.colors = {
            'excellent': '#10b981',    # Vert
            'good': '#3b82f6',         # Bleu
            'warning': '#f59e0b',      # Orange
            'critical': '#ef4444',     # Rouge
            'background': '#f8fafc',   # Gris clair
            'text': '#1f2937'          # Gris foncé
        }

    def load_data(self) -> bool:
        """Charge les données d'analyse"""
        data_file = self.assets_dir / 'fusion_data.json'

        if not data_file.exists():
            print(f"❌ Fichier de données non trouvé: {data_file}")
            return False

        try:
            with open(data_file, 'r') as f:
                self.data = json.load(f)
            print(f"✅ Données chargées: {len(self.data['modules'])} modules")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement données: {e}")
            return False

    def get_conformity_color(self, rate: float) -> str:
        """Retourne la couleur selon le taux de conformité"""
        if rate >= 90:
            return self.colors['excellent']
        elif rate >= 70:
            return self.colors['good']
        elif rate >= 50:
            return self.colors['warning']
        else:
            return self.colors['critical']

    def create_compliance_dashboard(self) -> str:
        """Génère le tableau de bord de conformité"""
        if not self.data:
            return None

        modules = self.data['modules']
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🔍 Dashboard Conformité EVE - Le Stratège', fontsize=20, fontweight='bold')

        # 1. Graphique en barres - Conformité par module
        module_names = [m['name'] for m in modules]
        conformity_rates = [m['conformity_rate'] for m in modules]
        colors = [self.get_conformity_color(rate) for rate in conformity_rates]

        bars1 = ax1.bar(module_names, conformity_rates, color=colors, alpha=0.8)
        ax1.set_title('📊 Taux de Conformité par Module', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Conformité (%)')
        ax1.set_ylim(0, 100)
        ax1.tick_params(axis='x', rotation=45)

        # Ajout des valeurs sur les barres
        for bar, rate in zip(bars1, conformity_rates):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')

        # Ligne de référence 90%
        ax1.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='Objectif 90%')
        ax1.legend()

        # 2. Graphique circulaire - Répartition globale
        total_files = sum(m['total_files'] for m in modules)
        total_violations = sum(m['violations'] for m in modules)
        conformes = total_files - total_violations

        sizes = [conformes, total_violations]
        labels = [f'Conformes\n{conformes:,} fichiers', f'Violations\n{total_violations:,} fichiers']
        colors_pie = [self.colors['excellent'], self.colors['critical']]
        explode = (0.05, 0)

        wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors_pie,
                                          autopct='%1.1f%%', explode=explode,
                                          shadow=True, startangle=90)
        ax2.set_title('🥧 Répartition Globale Conformité', fontsize=14, fontweight='bold')

        # 3. Complexité vs Taille des modules
        total_files = [m['total_files'] for m in modules]
        avg_complexity = [m['avg_complexity'] for m in modules]

        scatter = ax3.scatter(total_files, avg_complexity,
                            c=conformity_rates, cmap='RdYlGn',
                            s=100, alpha=0.7, edgecolors='black')

        for i, name in enumerate(module_names):
            ax3.annotate(name, (total_files[i], avg_complexity[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)

        ax3.set_title('🧠 Complexité vs Taille des Modules', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Nombre de Fichiers')
        ax3.set_ylabel('Complexité Moyenne')

        # Barre de couleur pour la conformité
        cbar = plt.colorbar(scatter, ax=ax3)
        cbar.set_label('Taux de Conformité (%)')

        # 4. Distribution des violations
        violations_data = [m['violations'] for m in modules]

        ax4.hist(violations_data, bins=max(1, len(modules)//3),
                color=self.colors['warning'], alpha=0.7, edgecolor='black')
        ax4.set_title('📈 Distribution des Violations', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Nombre de Violations')
        ax4.set_ylabel('Nombre de Modules')

        # Statistiques sur le graphique
        mean_violations = np.mean(violations_data)
        ax4.axvline(mean_violations, color='red', linestyle='--',
                   label=f'Moyenne: {mean_violations:.1f}')
        ax4.legend()

        plt.tight_layout()

        # Sauvegarde
        output_path = self.assets_dir / 'compliance_dashboard.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()

        print(f"📊 Dashboard généré: {output_path}")
        return str(output_path)

    def create_complexity_heatmap(self) -> str:
        """Génère une carte de chaleur de la complexité"""
        if not self.data:
            return None

        modules = self.data['modules']

        # Préparer les données pour la heatmap
        module_names = [m['name'] for m in modules]
        metrics = ['Fichiers', 'Violations', 'Conformité', 'Complexité Moy.']

        # Normaliser les données pour la heatmap
        data_matrix = []
        for module in modules:
            row = [
                module['total_files'],
                module['violations'],
                module['conformity_rate'],
                module['avg_complexity']
            ]
            data_matrix.append(row)

        # Normalisation par colonne (0-1)
        data_matrix = np.array(data_matrix)
        normalized_data = np.zeros_like(data_matrix)

        for j in range(data_matrix.shape[1]):
            col = data_matrix[:, j]
            if col.max() > col.min():
                normalized_data[:, j] = (col - col.min()) / (col.max() - col.min())

        # Créer la heatmap
        fig, ax = plt.subplots(figsize=(12, 8))

        # Colormap personnalisée
        colors_list = ['#ef4444', '#f59e0b', '#10b981']  # Rouge -> Orange -> Vert
        cmap = LinearSegmentedColormap.from_list('custom', colors_list)

        im = ax.imshow(normalized_data, cmap=cmap, aspect='auto')

        # Configuration des axes
        ax.set_xticks(np.arange(len(metrics)))
        ax.set_yticks(np.arange(len(module_names)))
        ax.set_xticklabels(metrics)
        ax.set_yticklabels(module_names)

        # Rotation des labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Ajout des valeurs dans les cellules
        for i in range(len(module_names)):
            for j in range(len(metrics)):
                text = ax.text(j, i, f'{data_matrix[i, j]:.1f}',
                             ha="center", va="center", color="white", fontweight='bold')

        ax.set_title('🔥 Carte de Chaleur - Métriques par Module',
                    fontsize=16, fontweight='bold', pad=20)

        # Barre de couleur
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Intensité Normalisée', rotation=270, labelpad=15)

        plt.tight_layout()

        # Sauvegarde
        output_path = self.assets_dir / 'complexity_heatmap.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()

        print(f"🔥 Heatmap générée: {output_path}")
        return str(output_path)

    def create_strategic_overview(self) -> str:
        """Génère vue d'ensemble stratégique"""
        if not self.data:
            return None

        modules = self.data['modules']

        # Créer figure avec subplot personnalisé
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Titre principal
        fig.suptitle('🎯 Vue Stratégique EVE - Le Stratège', fontsize=20, fontweight='bold')

        # 1. Radar chart des modules top/bottom
        ax1 = fig.add_subplot(gs[0, :])

        # Sélectionner top 5 et bottom 5 modules
        sorted_modules = sorted(modules, key=lambda x: x['conformity_rate'])
        bottom_modules = sorted_modules[:3]
        top_modules = sorted_modules[-3:]

        positions = np.arange(len(bottom_modules + top_modules))
        conformity_values = [m['conformity_rate'] for m in bottom_modules + top_modules]
        module_labels = [m['name'] for m in bottom_modules + top_modules]

        # Couleurs différentes pour top/bottom
        colors = ['red'] * len(bottom_modules) + ['green'] * len(top_modules)

        bars = ax1.barh(positions, conformity_values, color=colors, alpha=0.7)
        ax1.set_yticks(positions)
        ax1.set_yticklabels(module_labels)
        ax1.set_xlabel('Taux de Conformité (%)')
        ax1.set_title('🏆 Champions vs Zones Critiques', fontweight='bold')
        ax1.set_xlim(0, 100)

        # Ajout des valeurs
        for bar, value in zip(bars, conformity_values):
            width = bar.get_width()
            ax1.text(width + 1, bar.get_y() + bar.get_height()/2,
                    f'{value:.1f}%', ha='left', va='center', fontweight='bold')

        # 2. Quick Wins Analysis
        ax2 = fig.add_subplot(gs[1, 0])

        quick_wins_counts = [len(m['quick_wins']) for m in modules]
        modules_with_qw = [m['name'] for m in modules if len(m['quick_wins']) > 0]
        qw_counts = [len(m['quick_wins']) for m in modules if len(m['quick_wins']) > 0]

        if modules_with_qw:
            ax2.pie(qw_counts, labels=modules_with_qw, autopct='%1.0f',
                   colors=sns.color_palette("Set3", len(modules_with_qw)))
        ax2.set_title('🎯 Quick Wins\npar Module', fontweight='bold')

        # 3. Défis Majeurs
        ax3 = fig.add_subplot(gs[1, 1])

        major_challenges_counts = [len(m['major_challenges']) for m in modules]
        modules_with_mc = [m['name'] for m in modules if len(m['major_challenges']) > 0]
        mc_counts = [len(m['major_challenges']) for m in modules if len(m['major_challenges']) > 0]

        if modules_with_mc:
            ax3.pie(mc_counts, labels=modules_with_mc, autopct='%1.0f',
                   colors=sns.color_palette("Reds", len(modules_with_mc)))
        ax3.set_title('🏔️ Défis Majeurs\npar Module', fontweight='bold')

        # 4. Effort vs Impact Matrix
        ax4 = fig.add_subplot(gs[1, 2])

        # Calculer effort (basé sur violations) et impact (basé sur taille du module)
        effort = [m['violations'] for m in modules]
        impact = [m['total_files'] for m in modules]

        scatter = ax4.scatter(effort, impact,
                            c=[m['conformity_rate'] for m in modules],
                            s=100, cmap='RdYlGn', alpha=0.7, edgecolors='black')

        for i, name in enumerate([m['name'] for m in modules]):
            ax4.annotate(name, (effort[i], impact[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)

        ax4.set_xlabel('Effort Requis (Violations)')
        ax4.set_ylabel('Impact Potentiel (Taille)')
        ax4.set_title('💪 Effort vs Impact', fontweight='bold')

        # 5. Timeline de progression (simulation)
        ax5 = fig.add_subplot(gs[2, :])

        # Simuler progression possible
        current_conformity = sum(m['conformity_rate'] * m['total_files'] for m in modules) / sum(m['total_files'] for m in modules)

        weeks = np.arange(1, 13)  # 12 semaines
        quick_wins_progress = current_conformity + np.cumsum(np.random.exponential(2, 12)) * 0.5
        major_challenges_progress = current_conformity + np.cumsum(np.random.exponential(1, 12)) * 1.2

        ax5.plot(weeks, quick_wins_progress, 'g-', linewidth=3, label='Stratégie Quick Wins', marker='o')
        ax5.plot(weeks, major_challenges_progress, 'b-', linewidth=3, label='Stratégie Défis Majeurs', marker='s')
        ax5.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='Objectif 90%')
        ax5.axhline(y=95, color='orange', linestyle='--', alpha=0.7, label='Excellence 95%')

        ax5.set_xlabel('Semaines')
        ax5.set_ylabel('Conformité (%)')
        ax5.set_title('📈 Projection de Progression - Stratégies Comparées', fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_ylim(current_conformity - 5, 100)

        # Sauvegarde
        output_path = self.assets_dir / 'strategic_overview.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()

        print(f"🎯 Vue stratégique générée: {output_path}")
        return str(output_path)

    def generate_all_visualizations(self) -> Dict[str, str]:
        """Génère toutes les visualisations"""
        print("📈 Le Stratège - Génération des visualisations...")

        if not self.load_data():
            return {}

        results = {}

        try:
            # Dashboard de conformité
            results['compliance_dashboard'] = self.create_compliance_dashboard()

            # Carte de chaleur complexité
            results['complexity_heatmap'] = self.create_complexity_heatmap()

            # Vue d'ensemble stratégique
            results['strategic_overview'] = self.create_strategic_overview()

            print("✅ Toutes les visualisations générées avec succès")

        except Exception as e:
            print(f"❌ Erreur génération visualisations: {e}")

        return results


def main():
    """Point d'entrée principal"""
    report_dir = os.environ.get('REPORT_DIR', 'reports')

    visualizer = ProgressVisualizer(report_dir)
    results = visualizer.generate_all_visualizations()

    if results:
        print("\n📊 Visualisations générées:")
        for name, path in results.items():
            print(f"  • {name}: {path}")
    else:
        print("❌ Aucune visualisation générée")


if __name__ == "__main__":
    main()
