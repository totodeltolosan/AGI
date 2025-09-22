#!/usr/bin/env python3
"""
Ouvrier : Statisticien Lignes
Calcule des métriques statistiques globales à partir des résultats du jugement.
"""

import argparse
import json
import os
import sys
import statistics
from datetime import datetime
from pathlib import Path


class StatisticienLignes:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Calcule les statistiques globales des lignes')
        parser.add_argument('--artefact-resultats-juges', required=True,
                          help='Artefact JSON des résultats du jugement')
        parser.add_argument('--sortie', default='statistiques.json',
                          help='Nom du fichier JSON de sortie')
        parser.add_argument('--inclure-percentiles', action='store_true',
                          help='Inclure les percentiles dans les statistiques')
        
        self.args = parser.parse_args()
    
    def run(self):
        try:
            print(f"📊 Démarrage du calcul des statistiques")
            
            # Chargement des résultats du jugement
            resultats_juges = self._load_judgment_results()
            
            if not resultats_juges or not resultats_juges.get('evaluations'):
                self._write_empty_results()
                return
            
            evaluations = resultats_juges['evaluations']
            
            # Filtrage des données valides (sans erreur)
            donnees_valides = [
                eval for eval in evaluations 
                if not eval.get('erreur') and isinstance(eval.get('lignes'), (int, float))
            ]
            
            if not donnees_valides:
                print("⚠️  Aucune donnée valide pour les statistiques")
                self._write_empty_results()
                return
            
            print(f"📈 Calcul sur {len(donnees_valides)} fichiers valides")
            
            # Extraction des valeurs numériques
            lignes_values = [eval['lignes'] for eval in donnees_valides]
            
            # Calcul des statistiques de base
            stats_base = self._calculate_basic_stats(lignes_values)
            
            # Statistiques de conformité
            stats_conformite = self._calculate_compliance_stats(donnees_valides, resultats_juges)
            
            # Statistiques de distribution
            stats_distribution = self._calculate_distribution_stats(lignes_values)
            
            # Compilation des résultats
            statistiques_finales = {
                'timestamp': datetime.now().isoformat(),
                'source_donnees': self.args.artefact_resultats_juges,
                'metadonnees': {
                    'total_fichiers_analysees': len(donnees_valides),
                    'fichiers_avec_erreurs': len(evaluations) - len(donnees_valides),
                    'limite_lignes_appliquee': resultats_juges.get('limite_lignes', 0)
                },
                'statistiques_base': stats_base,
                'statistiques_conformite': stats_conformite,
                'statistiques_distribution': stats_distribution
            }
            
            # Ajout des percentiles si demandé
            if self.args.inclure_percentiles:
                statistiques_finales['percentiles'] = self._calculate_percentiles(lignes_values)
            
            # Recommandations automatiques
            statistiques_finales['recommandations_auto'] = self._generate_recommendations(statistiques_finales)
            
            self._write_results(statistiques_finales)
            
            print(f"✅ Statistiques calculées")
            print(f"   • Moyenne : {stats_base['moyenne_lignes']:.1f} lignes")
            print(f"   • Médiane : {stats_base['mediane_lignes']:.1f} lignes")
            print(f"   • Conformité : {stats_conformite['taux_conformite']:.1f}%")
            
        except Exception as e:
            print(f"❌ ERREUR lors du calcul des statistiques : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _load_judgment_results(self):
        try:
            with open(self.args.artefact_resultats_juges, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erreur chargement résultats jugement : {e}")
            return None
    
    def _calculate_basic_stats(self, values):
        return {
            'total_fichiers': len(values),
            'total_lignes': sum(values),
            'moyenne_lignes': statistics.mean(values),
            'mediane_lignes': statistics.median(values),
            'min_lignes': min(values),
            'max_lignes': max(values),
            'ecart_type': statistics.stdev(values) if len(values) > 1 else 0,
            'variance': statistics.variance(values) if len(values) > 1 else 0
        }
    
    def _calculate_compliance_stats(self, evaluations, resultats_juges):
        total = len(evaluations)
        conformes = sum(1 for e in evaluations if e.get('conforme', False))
        non_conformes = total - conformes
        
        # Analyse des écarts
        ecarts = [e.get('ecart', 0) for e in evaluations if not e.get('conforme', True)]
        
        stats = {
            'total_evalues': total,
            'fichiers_conformes': conformes,
            'fichiers_non_conformes': non_conformes,
            'taux_conformite': (conformes / total * 100) if total > 0 else 0,
            'taux_violation': (non_conformes / total * 100) if total > 0 else 0
        }
        
        if ecarts:
            stats['ecarts_statistiques'] = {
                'ecart_moyen': statistics.mean(ecarts),
                'ecart_max': max(ecarts),
                'ecart_median': statistics.median(ecarts)
            }
        
        # Classification par statut
        statuts = {}
        for eval in evaluations:
            statut = eval.get('statut', 'INCONNU')
            statuts[statut] = statuts.get(statut, 0) + 1
        
        stats['repartition_statuts'] = statuts
        
        return stats
    
    def _calculate_distribution_stats(self, values):
        # Calcul des quartiles
        values_sorted = sorted(values)
        n = len(values_sorted)
        
        stats = {
            'q1': values_sorted[n//4] if n >= 4 else values_sorted[0],
            'q3': values_sorted[3*n//4] if n >= 4 else values_sorted[-1],
            'iqr': 0,  # Sera calculé après
        }
        
        stats['iqr'] = stats['q3'] - stats['q1']
        
        # Détection d'outliers (méthode IQR)
        iqr_threshold = 1.5 * stats['iqr']
        lower_bound = stats['q1'] - iqr_threshold
        upper_bound = stats['q3'] + iqr_threshold
        
        outliers = [v for v in values if v < lower_bound or v > upper_bound]
        
        stats['outliers'] = {
            'count': len(outliers),
            'values': sorted(outliers),
            'pourcentage': (len(outliers) / len(values) * 100) if len(values) > 0 else 0
        }
        
        # Distribution par tranches
        tranches = {
            '0-50': sum(1 for v in values if 0 <= v <= 50),
            '51-100': sum(1 for v in values if 51 <= v <= 100),
            '101-200': sum(1 for v in values if 101 <= v <= 200),
            '201-500': sum(1 for v in values if 201 <= v <= 500),
            '500+': sum(1 for v in values if v > 500)
        }
        
        stats['distribution_tranches'] = tranches
        
        return stats
    
    def _calculate_percentiles(self, values):
        percentiles_to_calc = [10, 25, 50, 75, 90, 95, 99]
        result = {}
        
        for p in percentiles_to_calc:
            try:
                # Utilisation de la méthode quantiles de statistics (Python 3.8+)
                if hasattr(statistics, 'quantiles'):
                    quantiles = statistics.quantiles(values, n=100)
                    result[f'p{p}'] = quantiles[p-1] if p-1 < len(quantiles) else values[-1]
                else:
                    # Fallback manuel
                    pos = (p / 100) * (len(values) - 1)
                    lower = int(pos)
                    upper = min(lower + 1, len(values) - 1)
                    weight = pos - lower
                    
                    sorted_values = sorted(values)
                    result[f'p{p}'] = sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight
            except:
                # Fallback simple
                sorted_values = sorted(values)
                idx = int((p / 100) * len(sorted_values))
                result[f'p{p}'] = sorted_values[min(idx, len(sorted_values) - 1)]
        
        return result
    
    def _generate_recommendations(self, stats):
        recommandations = []
        
        # Analyse du taux de conformité
        taux_conformite = stats['statistiques_conformite']['taux_conformite']
        
        if taux_conformite < 50:
            recommandations.append({
                'type': 'CRITIQUE',
                'message': 'Taux de conformité très faible. Refactoring urgent nécessaire.',
                'priorite': 'HAUTE'
            })
        elif taux_conformite < 80:
            recommandations.append({
                'type': 'AMÉLIORATION',
                'message': 'Taux de conformité modéré. Plannifier un refactoring.',
                'priorite': 'MOYENNE'
            })
        else:
            recommandations.append({
                'type': 'MAINTENANCE',
                'message': 'Bon taux de conformité. Maintenir la qualité.',
                'priorite': 'BASSE'
            })
        
        # Analyse des outliers
        outliers_pct = stats['statistiques_distribution']['outliers']['pourcentage']
        
        if outliers_pct > 10:
            recommandations.append({
                'type': 'QUALITÉ',
                'message': f'{outliers_pct:.1f}% de fichiers atypiques détectés. Investigation recommandée.',
                'priorite': 'MOYENNE'
            })
        
        # Analyse de la moyenne
        moyenne = stats['statistiques_base']['moyenne_lignes']
        limite = stats['metadonnees']['limite_lignes_appliquee']
        
        if moyenne > limite * 0.8:
            recommandations.append({
                'type': 'PRÉVENTION',
                'message': 'Moyenne proche de la limite. Surveiller les nouveaux développements.',
                'priorite': 'BASSE'
            })
        
        return recommandations
    
    def _write_empty_results(self):
        resultats_vides = {
            'timestamp': datetime.now().isoformat(),
            'source_donnees': self.args.artefact_resultats_juges,
            'metadonnees': {'total_fichiers_analysees': 0},
            'statistiques_base': {'total_fichiers': 0, 'total_lignes': 0},
            'statistiques_conformite': {'taux_conformite': 0},
            'recommandations_auto': []
        }
        self._write_results(resultats_vides)
    
    def _write_results(self, resultats):
        Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
        with open(self.args.sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)
        print(f"💾 Statistiques sauvegardées : {self.args.sortie}")


if __name__ == "__main__":
    statisticien = StatisticienLignes()
    statisticien.run()
