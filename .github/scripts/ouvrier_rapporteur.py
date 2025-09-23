#!/usr/bin/env python3
"""
Ouvrier : Rapporteur Lignes
Génère un rapport CSV final combinant jugements et statistiques.
"""

import argparse
import json
import csv
import os
import sys
from datetime import datetime
from pathlib import Path


class RapporteurLignes:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Génère un rapport CSV des lignes')
        parser.add_argument('--artefact-resultats-juges', required=True,
                          help='Artefact JSON des résultats du jugement')
        parser.add_argument('--artefact-statistiques', required=True,
                          help='Artefact JSON des statistiques')
        parser.add_argument('--sortie', default='rapport-lignes.csv',
                          help='Nom du fichier CSV de sortie')
        parser.add_argument('--format-detaille', action='store_true',
                          help='Inclure des colonnes additionnelles')
        
        self.args = parser.parse_args()
    
    def run(self):
        try:
            print(f"📋 Génération du rapport CSV")
            
            # Chargement des données sources
            jugements = self._load_json_file(self.args.artefact_resultats_juges)
            statistiques = self._load_json_file(self.args.artefact_statistiques)
            
            if not jugements or not statistiques:
                self._write_empty_report()
                return
            
            # Préparation des données pour le CSV
            lignes_rapport = self._prepare_report_data(jugements, statistiques)
            
            # Génération du fichier CSV
            self._write_csv_report(lignes_rapport, statistiques)
            
            print(f"✅ Rapport généré : {len(lignes_rapport)} lignes de données")
            
        except Exception as e:
            print(f"❌ ERREUR lors de la génération du rapport : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _load_json_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erreur chargement {filepath} : {e}")
            return None
    
    def _prepare_report_data(self, jugements, statistiques):
        lignes_rapport = []
        
        evaluations = jugements.get('evaluations', [])
        stats_base = statistiques.get('statistiques_base', {})
        limite_lignes = jugements.get('limite_lignes', 0)
        
        for evaluation in evaluations:
            ligne = {
                'fichier': evaluation.get('fichier', 'Unknown'),
                'chemin': evaluation.get('chemin', ''),
                'lignes': evaluation.get('lignes', 0),
                'limite': limite_lignes,
                'conforme': 'OUI' if evaluation.get('conforme', False) else 'NON',
                'statut': evaluation.get('statut', 'INCONNU'),
                'ecart': evaluation.get('ecart', 0),
                'pourcentage_limite': round((evaluation.get('lignes', 0) / limite_lignes * 100), 1) if limite_lignes > 0 else 0
            }
            
            # Ajout de métadonnées conditionnelles
            if evaluation.get('erreur'):
                ligne['erreur'] = evaluation['erreur']
                ligne['conforme'] = 'ERREUR'
            
            # Colonnes détaillées si demandées
            if self.args.format_detaille:
                ligne['pourcentage_moyenne'] = round((evaluation.get('lignes', 0) / stats_base.get('moyenne_lignes', 1) * 100), 1)
                ligne['ecart_median'] = evaluation.get('lignes', 0) - stats_base.get('mediane_lignes', 0)
                ligne['categorie_taille'] = self._categorize_file_size(evaluation.get('lignes', 0))
            
            lignes_rapport.append(ligne)
        
        # Tri par nombre de lignes décroissant
        lignes_rapport.sort(key=lambda x: x['lignes'], reverse=True)
        
        return lignes_rapport
    
    def _categorize_file_size(self, lignes):
        if lignes <= 50:
            return 'TRES_PETIT'
        elif lignes <= 100:
            return 'PETIT'
        elif lignes <= 200:
            return 'MOYEN'
        elif lignes <= 500:
            return 'GRAND'
        else:
            return 'TRES_GRAND'
    
    def _write_csv_report(self, lignes_rapport, statistiques):
        Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
        
        # Détermination des colonnes
        colonnes_base = ['fichier', 'chemin', 'lignes', 'limite', 'conforme', 'statut', 'ecart', 'pourcentage_limite']
        
        if self.args.format_detaille:
            colonnes_base.extend(['pourcentage_moyenne', 'ecart_median', 'categorie_taille'])
        
        colonnes_base.append('erreur')  # Toujours en dernier
        
        with open(self.args.sortie, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=colonnes_base)
            
            # En-tête avec métadonnées
            writer.writeheader()
            
            # Ligne de métadonnées (commentaire CSV)
            metadata_row = {
                'fichier': f'# Rapport généré le {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'chemin': f'# Total fichiers: {len(lignes_rapport)}',
                'lignes': f'# Conformité: {statistiques.get("statistiques_conformite", {}).get("taux_conformite", 0):.1f}%',
                'limite': '# Limite appliquée',
                'conforme': '# OUI/NON/ERREUR',
                'statut': '# Statut détaillé',
                'ecart': '# Dépassement (+) ou marge (-)',
                'pourcentage_limite': '# % de la limite'
            }
            writer.writerow(metadata_row)
            
            # Données du rapport
            for ligne in lignes_rapport:
                # S'assurer que toutes les colonnes sont présentes
                ligne_complete = {col: ligne.get(col, '') for col in colonnes_base}
                writer.writerow(ligne_complete)
        
        print(f"💾 Rapport CSV sauvegardé : {self.args.sortie}")
        
        # Affichage d'un résumé
        conformes = sum(1 for l in lignes_rapport if l['conforme'] == 'OUI')
        non_conformes = sum(1 for l in lignes_rapport if l['conforme'] == 'NON')
        erreurs = sum(1 for l in lignes_rapport if l['conforme'] == 'ERREUR')
        
        print(f"📊 Contenu du rapport :")
        print(f"   • Fichiers conformes : {conformes}")
        print(f"   • Fichiers non conformes : {non_conformes}")
        print(f"   • Fichiers en erreur : {erreurs}")
        
        if lignes_rapport:
            max_lignes = max(l['lignes'] for l in lignes_rapport if isinstance(l['lignes'], (int, float)))
            min_lignes = min(l['lignes'] for l in lignes_rapport if isinstance(l['lignes'], (int, float)))
            print(f"   • Plage lignes : {min_lignes} - {max_lignes}")
    
    def _write_empty_report(self):
        Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.args.sortie, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['fichier', 'lignes', 'conforme', 'statut', 'message'])
            writer.writerow([f'# Rapport vide généré le {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 'N/A', 'AUCUNE_DONNEE', 'Aucun fichier à analyser'])
        
        print(f"📄 Rapport vide créé : {self.args.sortie}")


if __name__ == "__main__":
    rapporteur = RapporteurLignes()
    rapporteur.run()
