#!/usr/bin/env python3
"""
Travailleur : Scanner de Fichiers
Brique fondamentale pour trouver des fichiers selon un pattern et des exclusions.
"""

import argparse
import json
import os
import sys
import fnmatch
from pathlib import Path


class ScannerFichiers:
    def __init__(self):
        """Initialise le scanner avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Scanne et filtre les fichiers selon un pattern')
        parser.add_argument('--pattern', required=True,
                          help='Pattern de fichiers à chercher (ex: *.py, *.js, **/*.md)')
        parser.add_argument('--chemin-racine', required=True,
                          help='Chemin racine où commencer la recherche')
        parser.add_argument('--exclusions', required=False, default='[]',
                          help='JSON array des patterns à exclure')
        parser.add_argument('--sortie', default='liste-fichiers.json',
                          help='Nom du fichier JSON de sortie')
        
        self.args = parser.parse_args()
        
        # Validation et parsing des exclusions
        try:
            self.exclusions = json.loads(self.args.exclusions)
            if not isinstance(self.exclusions, list):
                raise ValueError("Les exclusions doivent être une liste JSON")
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR: Format exclusions invalide - {e}", file=sys.stderr)
            sys.exit(1)
        
        # Validation du chemin racine
        if not os.path.exists(self.args.chemin_racine):
            print(f"❌ ERREUR: Chemin racine introuvable : {self.args.chemin_racine}", file=sys.stderr)
            sys.exit(1)
    
    def run(self):
        """
        Logique principale : scanne récursivement le système de fichiers
        pour trouver tous les fichiers correspondant au pattern, en appliquant les exclusions.
        """
        try:
            print(f"🔍 Scan des fichiers : pattern '{self.args.pattern}' depuis '{self.args.chemin_racine}'")
            print(f"🚫 Exclusions : {self.exclusions}")
            
            fichiers_trouves = []
            chemin_racine = Path(self.args.chemin_racine).resolve()
            
            # Scan récursif des fichiers
            for chemin_fichier in self._scan_recursive(chemin_racine):
                if self._should_include_file(chemin_fichier, chemin_racine):
                    # Conversion en chemin relatif pour la portabilité
                    chemin_relatif = os.path.relpath(chemin_fichier, chemin_racine)
                    fichiers_trouves.append(chemin_relatif)
            
            # Tri des résultats pour un ordre déterministe
            fichiers_trouves.sort()
            
            print(f"📁 {len(fichiers_trouves)} fichiers trouvés")
            
            # Préparation de la structure de sortie
            resultat = {
                "pattern": self.args.pattern,
                "chemin_racine": str(chemin_racine),
                "exclusions": self.exclusions,
                "timestamp": self._get_timestamp(),
                "total_fichiers": len(fichiers_trouves),
                "fichiers": fichiers_trouves
            }
            
            # Écriture du fichier JSON de sortie
            Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.args.sortie, 'w', encoding='utf-8') as f:
                json.dump(resultat, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Liste de fichiers sauvegardée : {self.args.sortie}")
            
            # Affichage d'un échantillon pour debug
            if len(fichiers_trouves) > 0:
                print("📄 Échantillon des fichiers trouvés :")
                for fichier in fichiers_trouves[:5]:
                    print(f"   • {fichier}")
                if len(fichiers_trouves) > 5:
                    print(f"   ... et {len(fichiers_trouves) - 5} autres")
            
        except Exception as e:
            print(f"❌ ERREUR lors du scan de fichiers : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _scan_recursive(self, chemin_racine):
        """
        Générateur qui scanne récursivement tous les fichiers depuis chemin_racine.
        """
        try:
            for root, dirs, files in os.walk(chemin_racine):
                # Filtrage des répertoires exclus pour éviter de les parcourir
                dirs[:] = [d for d in dirs if not self._is_excluded_dir(
                    os.path.join(root, d), chemin_racine)]
                
                for filename in files:
                    filepath = os.path.join(root, filename)
                    # Test du pattern principal
                    if self._matches_pattern(filename, self.args.pattern):
                        yield filepath
                        
        except PermissionError as e:
            print(f"⚠️  Permission refusée : {e}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Erreur lors du scan : {e}", file=sys.stderr)
    
    def _matches_pattern(self, filename, pattern):
        """
        Vérifie si un nom de fichier correspond au pattern.
        Supporte les wildcards standards et patterns globaux.
        """
        # Support des patterns simples avec fnmatch
        if fnmatch.fnmatch(filename, pattern):
            return True
        
        # Support des patterns avec chemins (ex: **/*.py)
        if '/' in pattern:
            return fnmatch.fnmatch(filename, os.path.basename(pattern))
        
        return False
    
    def _should_include_file(self, filepath, racine):
        """
        Détermine si un fichier doit être inclus selon les règles d'exclusion.
        """
        # Conversion en chemin relatif pour les tests
        try:
            chemin_relatif = os.path.relpath(filepath, racine)
        except ValueError:
            # Si le calcul du chemin relatif échoue, inclure le fichier
            return True
        
        # Test de chaque exclusion
        for exclusion in self.exclusions:
            # Test sur le nom du fichier seul
            if fnmatch.fnmatch(os.path.basename(filepath), exclusion):
                return False
            
            # Test sur le chemin complet relatif
            if fnmatch.fnmatch(chemin_relatif, exclusion):
                return False
            
            # Test avec pattern de répertoire
            if '/' in exclusion and exclusion in chemin_relatif:
                return False
        
        return True
    
    def _is_excluded_dir(self, dirpath, racine):
        """
        Détermine si un répertoire doit être exclu du scan.
        """
        try:
            dir_relatif = os.path.relpath(dirpath, racine)
            dir_name = os.path.basename(dirpath)
        except ValueError:
            return False
        
        for exclusion in self.exclusions:
            # Exclusions de répertoires communs
            if dir_name in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv']:
                return True
            
            if fnmatch.fnmatch(dir_name, exclusion):
                return True
            
            if fnmatch.fnmatch(dir_relatif, exclusion):
                return True
        
        return False
    
    def _get_timestamp(self):
        """Retourne un timestamp ISO pour la traçabilité."""
        from datetime import datetime
        return datetime.now().isoformat()


if __name__ == "__main__":
    scanner = ScannerFichiers()
    scanner.run()
