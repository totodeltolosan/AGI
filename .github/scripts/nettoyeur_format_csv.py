#!/usr/bin/env python3
"""
Nettoyeur : Formateur CSV
Transforme des données JSON en fichier CSV propre avec en-têtes.
"""

import argparse
import json
import csv
import os
import sys
from pathlib import Path


class CSVFormatter:
    def __init__(self):
        """Initialise le formateur CSV avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Formate des données JSON en CSV')
        parser.add_argument('--artefact-entree-json', required=True,
                          help='Nom de l\'artefact JSON à consommer')
        parser.add_argument('--nom-fichier-sortie-csv', required=True,
                          help='Nom du fichier CSV à créer')
        parser.add_argument('--colonnes', required=True,
                          help='JSON string définissant les colonnes à extraire')
        
        self.args = parser.parse_args()
        
        # Validation des arguments
        try:
            self.colonnes_config = json.loads(self.args.colonnes)
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR: Configuration colonnes invalide - {e}", file=sys.stderr)
            sys.exit(1)
    
    def run(self):
        """
        Logique principale : lit le JSON d'entrée, extrait les données 
        selon la configuration des colonnes, et génère un CSV propre.
        """
        try:
            # Lecture du fichier JSON d'entrée
            if not os.path.exists(self.args.artefact_entree_json):
                print(f"❌ ERREUR: Fichier d'entrée introuvable : {self.args.artefact_entree_json}", 
                      file=sys.stderr)
                sys.exit(1)
            
            with open(self.args.artefact_entree_json, 'r', encoding='utf-8') as f:
                donnees_json = json.load(f)
            
            print(f"📊 Traitement de {len(donnees_json) if isinstance(donnees_json, list) else 1} enregistrements")
            
            # Préparation du chemin de sortie
            Path(self.args.nom_fichier_sortie_csv).parent.mkdir(parents=True, exist_ok=True)
            
            # Génération du fichier CSV
            with open(self.args.nom_fichier_sortie_csv, 'w', newline='', encoding='utf-8') as csvfile:
                if isinstance(donnees_json, list) and len(donnees_json) > 0:
                    # Cas d'une liste d'objets
                    writer = csv.DictWriter(csvfile, fieldnames=self.colonnes_config)
                    writer.writeheader()
                    
                    for item in donnees_json:
                        row = {}
                        for col in self.colonnes_config:
                            # Navigation dans les objets imbriqués si nécessaire
                            row[col] = self._extract_nested_value(item, col)
                        writer.writerow(row)
                        
                elif isinstance(donnees_json, dict):
                    # Cas d'un seul objet
                    writer = csv.DictWriter(csvfile, fieldnames=self.colonnes_config)
                    writer.writeheader()
                    
                    row = {}
                    for col in self.colonnes_config:
                        row[col] = self._extract_nested_value(donnees_json, col)
                    writer.writerow(row)
                
                else:
                    print("⚠️  ATTENTION: Données JSON vides ou format non supporté")
                    # Créer un CSV vide avec juste les en-têtes
                    writer = csv.DictWriter(csvfile, fieldnames=self.colonnes_config)
                    writer.writeheader()
            
            print(f"✅ Fichier CSV créé avec succès : {self.args.nom_fichier_sortie_csv}")
            
            # Vérification de la création du fichier
            if os.path.exists(self.args.nom_fichier_sortie_csv):
                taille = os.path.getsize(self.args.nom_fichier_sortie_csv)
                print(f"📄 Taille du fichier généré : {taille} octets")
            
        except Exception as e:
            print(f"❌ ERREUR lors du formatage CSV : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _extract_nested_value(self, data, key):
        """
        Extrait une valeur d'un objet, supportant la navigation
        dans des objets imbriqués (ex: 'stats.total').
        """
        if '.' in key:
            keys = key.split('.')
            value = data
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return ''
            return str(value) if value is not None else ''
        else:
            return str(data.get(key, '')) if isinstance(data, dict) else ''


if __name__ == "__main__":
    formatter = CSVFormatter()
    formatter.run()
