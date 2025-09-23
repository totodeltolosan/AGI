#!/usr/bin/env python3
"""
Ouvrier : Compteur de Lignes
Compte les lignes de code dans les fichiers fournis via une liste de fichiers.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class CompteurLignes:
    def __init__(self):
        """Initialise le compteur avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Compte les lignes de fichiers')
        parser.add_argument('--artefact-liste-fichiers', required=True,
                          help='Artefact JSON contenant la liste des fichiers à analyser')
        parser.add_argument('--sortie', default='resultats-bruts-compteur.json',
                          help='Nom du fichier JSON de sortie')
        parser.add_argument('--inclure-vides', action='store_true',
                          help='Inclure les lignes vides dans le comptage')
        parser.add_argument('--inclure-commentaires', action='store_true', default=True,
                          help='Inclure les commentaires dans le comptage')
        
        self.args = parser.parse_args()
    
    def run(self):
        """
        Logique principale : charge la liste de fichiers et compte les lignes
        de chaque fichier, produisant des statistiques détaillées.
        """
        try:
            print(f"📊 Démarrage du comptage de lignes")
            print(f"📄 Liste de fichiers : {self.args.artefact_liste_fichiers}")
            
            # Chargement de la liste des fichiers
            fichiers_data = self._load_file_list()
            
            if not fichiers_data or not fichiers_data.get('fichiers'):
                print("⚠️  Aucun fichier à analyser")
                self._write_empty_results()
                return
            
            fichiers = fichiers_data['fichiers']
            print(f"🔍 {len(fichiers)} fichiers à analyser")
            
            # Comptage des lignes pour chaque fichier
            resultats_fichiers = []
            stats_globales = {
                'total_fichiers': len(fichiers),
                'fichiers_analyses': 0,
                'fichiers_erreur': 0,
                'total_lignes': 0,
                'total_lignes_code': 0,
                'total_lignes_vides': 0,
                'total_lignes_commentaires': 0
            }
            
            for fichier_path in fichiers:
                resultat_fichier = self._count_file_lines(fichier_path)
                resultats_fichiers.append(resultat_fichier)
                
                if resultat_fichier['erreur']:
                    stats_globales['fichiers_erreur'] += 1
                else:
                    stats_globales['fichiers_analyses'] += 1
                    stats_globales['total_lignes'] += resultat_fichier['lignes_total']
                    stats_globales['total_lignes_code'] += resultat_fichier['lignes_code']
                    stats_globales['total_lignes_vides'] += resultat_fichier['lignes_vides']
                    stats_globales['total_lignes_commentaires'] += resultat_fichier['lignes_commentaires']
            
            # Calcul de statistiques additionnelles
            if stats_globales['fichiers_analyses'] > 0:
                stats_globales['moyenne_lignes_par_fichier'] = round(
                    stats_globales['total_lignes'] / stats_globales['fichiers_analyses'], 2)
                stats_globales['pourcentage_lignes_code'] = round(
                    (stats_globales['total_lignes_code'] / stats_globales['total_lignes']) * 100, 2) if stats_globales['total_lignes'] > 0 else 0
            
            print(f"✅ Analyse terminée : {stats_globales['fichiers_analyses']} fichiers analysés")
            print(f"📈 Total lignes : {stats_globales['total_lignes']}")
            
            # Préparation des résultats finaux
            resultats_finaux = {
                'timestamp': datetime.now().isoformat(),
                'parametres': {
                    'inclure_vides': self.args.inclure_vides,
                    'inclure_commentaires': self.args.inclure_commentaires,
                    'source_liste': self.args.artefact_liste_fichiers
                },
                'stats_globales': stats_globales,
                'fichiers': resultats_fichiers,
                'total_fichiers': len(fichiers),
                'erreurs': [f['erreur'] for f in resultats_fichiers if f['erreur']]
            }
            
            # Écriture du fichier de résultats
            self._write_results(resultats_finaux)
            
        except Exception as e:
            print(f"❌ ERREUR lors du comptage : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _load_file_list(self):
        """
        Charge la liste des fichiers depuis l'artefact JSON.
        """
        try:
            if not os.path.exists(self.args.artefact_liste_fichiers):
                print(f"❌ Liste de fichiers introuvable : {self.args.artefact_liste_fichiers}")
                return None
            
            with open(self.args.artefact_liste_fichiers, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📋 Liste chargée : {data.get('total_fichiers', 0)} fichiers")
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Format JSON invalide : {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur chargement liste : {e}")
            return None
    
    def _count_file_lines(self, file_path):
        """
        Compte les lignes d'un fichier spécifique avec classification.
        """
        resultat = {
            'nom': os.path.basename(file_path),
            'chemin': file_path,
            'lignes_total': 0,
            'lignes_code': 0,
            'lignes_vides': 0,
            'lignes_commentaires': 0,
            'encodage': None,
            'erreur': None,
            'analyse': datetime.now().isoformat()
        }
        
        try:
            # Tentative de lecture avec différents encodages
            content = None
            encodages_a_tester = ['utf-8', 'latin-1', 'cp1252']
            
            for encodage in encodages_a_tester:
                try:
                    with open(file_path, 'r', encoding=encodage) as f:
                        content = f.read()
                    resultat['encodage'] = encodage
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                resultat['erreur'] = "Impossible de décoder le fichier"
                return resultat
            
            lines = content.split('\n')
            resultat['lignes_total'] = len(lines)
            
            # Classification des lignes
            for line in lines:
                line_stripped = line.strip()
                
                if not line_stripped:
                    # Ligne vide
                    resultat['lignes_vides'] += 1
                elif self._is_comment_line(line_stripped, file_path):
                    # Ligne de commentaire
                    resultat['lignes_commentaires'] += 1
                else:
                    # Ligne de code
                    resultat['lignes_code'] += 1
            
            # Ajustement selon les options
            if not self.args.inclure_vides:
                resultat['lignes_total'] -= resultat['lignes_vides']
            
            if not self.args.inclure_commentaires:
                resultat['lignes_total'] -= resultat['lignes_commentaires']
            
        except FileNotFoundError:
            resultat['erreur'] = "Fichier introuvable"
        except PermissionError:
            resultat['erreur'] = "Permission refusée"
        except Exception as e:
            resultat['erreur'] = f"Erreur lecture : {str(e)}"
        
        return resultat
    
    def _is_comment_line(self, line, file_path):
        """
        Détermine si une ligne est un commentaire selon l'extension du fichier.
        """
        ext = Path(file_path).suffix.lower()
        
        # Patterns de commentaires par type de fichier
        comment_patterns = {
            '.py': ['#'],
            '.js': ['//', '/*', '*/', '/**'],
            '.ts': ['//', '/*', '*/', '/**'],
            '.java': ['//', '/*', '*/', '/**'],
            '.cpp': ['//', '/*', '*/', '/**'],
            '.c': ['//', '/*', '*/', '/**'],
            '.h': ['//', '/*', '*/', '/**'],
            '.css': ['/*', '*/'],
            '.html': ['<!--', '-->'],
            '.xml': ['<!--', '-->'],
            '.sh': ['#'],
            '.bash': ['#'],
            '.yml': ['#'],
            '.yaml': ['#'],
            '.json': [],  # JSON n'a pas de commentaires standards
            '.md': [],    # Markdown, pas de commentaires standards
            '.txt': []    # Texte brut, pas de commentaires standards
        }
        
        patterns = comment_patterns.get(ext, ['#'])  # Par défaut, assume #
        
        for pattern in patterns:
            if line.startswith(pattern):
                return True
        
        return False
    
    def _write_empty_results(self):
        """
        Écrit un fichier de résultats vide.
        """
        resultats_vides = {
            'timestamp': datetime.now().isoformat(),
            'parametres': {
                'inclure_vides': self.args.inclure_vides,
                'inclure_commentaires': self.args.inclure_commentaires,
                'source_liste': self.args.artefact_liste_fichiers
            },
            'stats_globales': {
                'total_fichiers': 0,
                'fichiers_analyses': 0,
                'fichiers_erreur': 0,
                'total_lignes': 0
            },
            'fichiers': [],
            'total_fichiers': 0,
            'erreurs': []
        }
        
        self._write_results(resultats_vides)
    
    def _write_results(self, resultats):
        """
        Écrit les résultats dans le fichier de sortie.
        """
        try:
            Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.args.sortie, 'w', encoding='utf-8') as f:
                json.dump(resultats, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Résultats sauvegardés : {self.args.sortie}")
            
            # Affichage d'un résumé
            stats = resultats['stats_globales']
            print(f"📊 Résumé :")
            print(f"   • Fichiers analysés : {stats['fichiers_analyses']}")
            print(f"   • Total lignes : {stats['total_lignes']}")
            if 'moyenne_lignes_par_fichier' in stats:
                print(f"   • Moyenne par fichier : {stats['moyenne_lignes_par_fichier']}")
            if stats['fichiers_erreur'] > 0:
                print(f"   ⚠️ Fichiers en erreur : {stats['fichiers_erreur']}")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde résultats : {e}")
            sys.exit(1)


if __name__ == "__main__":
    compteur = CompteurLignes()
    compteur.run()
