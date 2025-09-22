#!/usr/bin/env python3
"""
Ouvrier : Juge Lignes
Compare les résultats de comptage à la limite autorisée et émet un jugement.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class JugeLignes:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Juge la conformité du nombre de lignes')
        parser.add_argument('--artefact-resultats-bruts', required=True,
                          help='Artefact JSON des résultats bruts du comptage')
        parser.add_argument('--limite-lignes', type=int, required=True,
                          help='Limite maximale de lignes autorisée par fichier')
        parser.add_argument('--sortie', default='resultats-juges.json',
                          help='Nom du fichier JSON de sortie')
        
        self.args = parser.parse_args()
    
    def run(self):
        try:
            print(f"⚖️  Démarrage du jugement conformité lignes")
            print(f"📏 Limite autorisée : {self.args.limite_lignes} lignes/fichier")
            
            # Chargement des résultats bruts
            resultats_bruts = self._load_raw_results()
            
            if not resultats_bruts:
                self._write_empty_results()
                return
            
            # Jugement de chaque fichier
            evaluations = []
            stats_jugement = {
                'total_fichiers': len(resultats_bruts.get('fichiers', [])),
                'conformes': 0,
                'non_conformes': 0,
                'erreurs_analyse': 0,
                'limite_appliquee': self.args.limite_lignes
            }
            
            for fichier_data in resultats_bruts.get('fichiers', []):
                evaluation = self._evaluate_file(fichier_data)
                evaluations.append(evaluation)
                
                if evaluation['erreur']:
                    stats_jugement['erreurs_analyse'] += 1
                elif evaluation['conforme']:
                    stats_jugement['conformes'] += 1
                else:
                    stats_jugement['non_conformes'] += 1
            
            # Jugement global
            jugement_global = self._determine_global_judgment(stats_jugement)
            
            resultats_finaux = {
                'timestamp': datetime.now().isoformat(),
                'limite_lignes': self.args.limite_lignes,
                'jugement_global': jugement_global,
                'statistiques': stats_jugement,
                'evaluations': evaluations,
                'violations_critiques': [e for e in evaluations if not e['conforme'] and not e['erreur']],
                'source_donnees': self.args.artefact_resultats_bruts
            }
            
            self._write_results(resultats_finaux)
            
            print(f"✅ Jugement terminé : {stats_jugement['conformes']}/{stats_jugement['total_fichiers']} fichiers conformes")
            
        except Exception as e:
            print(f"❌ ERREUR lors du jugement : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _load_raw_results(self):
        try:
            with open(self.args.artefact_resultats_bruts, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erreur chargement résultats bruts : {e}")
            return None
    
    def _evaluate_file(self, fichier_data):
        evaluation = {
            'fichier': fichier_data.get('nom', 'Unknown'),
            'chemin': fichier_data.get('chemin', ''),
            'lignes': fichier_data.get('lignes_total', 0),
            'limite': self.args.limite_lignes,
            'conforme': False,
            'ecart': 0,
            'statut': '',
            'erreur': fichier_data.get('erreur'),
            'jugement_timestamp': datetime.now().isoformat()
        }
        
        if evaluation['erreur']:
            evaluation['statut'] = 'ERREUR'
            return evaluation
        
        evaluation['ecart'] = evaluation['lignes'] - self.args.limite_lignes
        
        if evaluation['lignes'] <= self.args.limite_lignes:
            evaluation['conforme'] = True
            evaluation['statut'] = 'CONFORME'
        else:
            evaluation['conforme'] = False
            if evaluation['ecart'] <= 50:  # Marge de tolérance
                evaluation['statut'] = 'NON_CONFORME_MINEUR'
            else:
                evaluation['statut'] = 'NON_CONFORME_MAJEUR'
        
        return evaluation
    
    def _determine_global_judgment(self, stats):
        total = stats['total_fichiers']
        conformes = stats['conformes']
        
        if total == 0:
            return {'verdict': 'AUCUN_FICHIER', 'confiance': 100}
        
        taux_conformite = (conformes / total) * 100
        
        if taux_conformite == 100:
            return {'verdict': 'CONFORME', 'taux_conformite': taux_conformite, 'confiance': 100}
        elif taux_conformite >= 95:
            return {'verdict': 'LARGEMENT_CONFORME', 'taux_conformite': taux_conformite, 'confiance': 90}
        elif taux_conformite >= 80:
            return {'verdict': 'PARTIELLEMENT_CONFORME', 'taux_conformite': taux_conformite, 'confiance': 70}
        else:
            return {'verdict': 'NON_CONFORME', 'taux_conformite': taux_conformite, 'confiance': 95}
    
    def _write_empty_results(self):
        resultats_vides = {
            'timestamp': datetime.now().isoformat(),
            'limite_lignes': self.args.limite_lignes,
            'jugement_global': {'verdict': 'AUCUNE_DONNEE', 'confiance': 100},
            'statistiques': {'total_fichiers': 0, 'conformes': 0, 'non_conformes': 0},
            'evaluations': [],
            'violations_critiques': []
        }
        self._write_results(resultats_vides)
    
    def _write_results(self, resultats):
        Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
        with open(self.args.sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)
        print(f"💾 Jugement sauvegardé : {self.args.sortie}")


if __name__ == "__main__":
    juge = JugeLignes()
    juge.run()
