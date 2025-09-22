#!/usr/bin/env python3
"""
Qualiticien : Validation d'Artefacts
Script pour valider les artefacts non-JSON (CSV, Markdown, TXT, etc.).
"""

import argparse
import csv
import os
import sys
import re
from datetime import datetime
from pathlib import Path


class ValidationArtefact:
    def __init__(self):
        """Initialise le validateur avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Valide un artefact non-JSON')
        parser.add_argument('--artefact', required=True,
                          help='Chemin vers l\'artefact à valider')
        parser.add_argument('--type-attendu', required=True,
                          choices=['csv', 'markdown', 'txt', 'json', 'auto'],
                          help='Type d\'artefact attendu')
        parser.add_argument('--taille-min', type=int, default=0,
                          help='Taille minimale en octets (défaut: 0)')
        parser.add_argument('--lignes-min', type=int, default=1,
                          help='Nombre minimum de lignes (défaut: 1)')
        parser.add_argument('--validation-custom', 
                          help='Règles de validation personnalisées (JSON)')
        
        self.args = parser.parse_args()
        
        # Détection automatique du type si nécessaire
        if self.args.type_attendu == 'auto':
            self.args.type_attendu = self._detect_file_type()
    
    def run(self):
        """
        Logique principale : valide l'existence, la structure et le contenu
        de l'artefact selon son type.
        """
        try:
            print(f"🔍 Validation artefact : {self.args.artefact}")
            print(f"📄 Type attendu : {self.args.type_attendu}")
            
            # Validation de base (existence, taille, lignes)
            basic_errors = self._validate_basic_properties()
            
            if basic_errors:
                print(f"❌ VALIDATION DE BASE ÉCHOUÉE :")
                for error in basic_errors:
                    print(f"   • {error}")
                sys.exit(1)
            
            # Validation spécifique par type
            type_errors = self._validate_by_type()
            
            if type_errors:
                print(f"❌ VALIDATION DE TYPE ÉCHOUÉE :")
                for error in type_errors:
                    print(f"   • {error}")
                sys.exit(1)
            
            print("✅ VALIDATION RÉUSSIE : Artefact conforme")
            self._display_validation_summary()
            
        except Exception as e:
            print(f"❌ ERREUR lors de la validation : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _validate_basic_properties(self):
        """
        Valide les propriétés de base : existence, taille, nombre de lignes.
        """
        errors = []
        
        # Vérification existence
        if not os.path.exists(self.args.artefact):
            errors.append(f"Artefact introuvable : {self.args.artefact}")
            return errors
        
        # Vérification taille
        file_size = os.path.getsize(self.args.artefact)
        if file_size < self.args.taille_min:
            errors.append(f"Taille insuffisante : {file_size} < {self.args.taille_min} octets")
        
        # Vérification nombre de lignes
        try:
            with open(self.args.artefact, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            if line_count < self.args.lignes_min:
                errors.append(f"Nombre de lignes insuffisant : {line_count} < {self.args.lignes_min}")
                
        except UnicodeDecodeError:
            # Essayer avec un autre encodage
            try:
                with open(self.args.artefact, 'r', encoding='latin-1') as f:
                    line_count = sum(1 for _ in f)
                
                if line_count < self.args.lignes_min:
                    errors.append(f"Nombre de lignes insuffisant : {line_count} < {self.args.lignes_min}")
                    
            except Exception as e:
                errors.append(f"Impossible de lire le fichier : {e}")
        
        return errors
    
    def _validate_by_type(self):
        """
        Valide l'artefact selon son type spécifique.
        """
        validators = {
            'csv': self._validate_csv,
            'markdown': self._validate_markdown,
            'txt': self._validate_txt,
            'json': self._validate_json
        }
        
        validator = validators.get(self.args.type_attendu)
        if validator:
            return validator()
        else:
            return [f"Type de validation non supporté : {self.args.type_attendu}"]
    
    def _validate_csv(self):
        """Valide un fichier CSV."""
        errors = []
        
        try:
            with open(self.args.artefact, 'r', encoding='utf-8') as f:
                # Détection du dialecte CSV
                sample = f.read(1024)
                f.seek(0)
                
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
                except csv.Error:
                    # Utiliser le dialecte par défaut si la détection échoue
                    dialect = csv.excel
                
                # Lecture et validation du CSV
                reader = csv.reader(f, dialect=dialect)
                
                rows = list(reader)
                if not rows:
                    errors.append("Fichier CSV vide")
                    return errors
                
                header_row = rows[0]
                data_rows = rows[1:] if len(rows) > 1 else []
                
                # Validation en-têtes
                if not header_row or all(cell.strip() == '' for cell in header_row):
                    errors.append("En-têtes CSV manquants ou vides")
                
                # Validation cohérence colonnes
                expected_cols = len(header_row)
                for i, row in enumerate(data_rows):
                    if len(row) != expected_cols:
                        errors.append(f"Ligne {i+2}: {len(row)} colonnes au lieu de {expected_cols}")
                        break  # Éviter trop d'erreurs similaires
                
                print(f"📊 CSV validé : {len(header_row)} colonnes, {len(data_rows)} lignes de données")
                
        except Exception as e:
            errors.append(f"Erreur lecture CSV : {e}")
        
        return errors
    
    def _validate_markdown(self):
        """Valide un fichier Markdown."""
        errors = []
        
        try:
            with open(self.args.artefact, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                errors.append("Fichier Markdown vide")
                return errors
            
            # Vérifications de base Markdown
            lines = content.split('\n')
            
            # Vérifier s'il y a au moins un élément de structure Markdown
            has_headers = any(line.strip().startswith('#') for line in lines)
            has_lists = any(line.strip().startswith(('-', '*', '+')) or re.match(r'^\d+\.', line.strip()) for line in lines)
            has_emphasis = '**' in content or '*' in content or '__' in content or '_' in content
            has_links = '[' in content and '](' in content
            
            if not any([has_headers, has_lists, has_emphasis, has_links]):
                errors.append("Aucun élément Markdown détecté (texte brut ?)")
            
            # Vérification syntaxe de base
            bracket_balance = content.count('[') - content.count(']')
            if bracket_balance != 0:
                errors.append(f"Crochets non équilibrés : {abs(bracket_balance)} en trop")
            
            paren_balance = content.count('(') - content.count(')')
            if paren_balance != 0:
                errors.append(f"Parenthèses non équilibrées : {abs(paren_balance)} en trop")
            
            print(f"📝 Markdown validé : {len(lines)} lignes, éléments détectés: "
                  f"titres={has_headers}, listes={has_lists}, emphasis={has_emphasis}, liens={has_links}")
            
        except Exception as e:
            errors.append(f"Erreur lecture Markdown : {e}")
        
        return errors
    
    def _validate_txt(self):
        """Valide un fichier texte simple."""
        errors = []
        
        try:
            with open(self.args.artefact, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                errors.append("Fichier texte vide")
                return errors
            
            # Vérifications basiques pour un fichier texte
            lines = content.split('\n')
            empty_lines = sum(1 for line in lines if not line.strip())
            content_lines = len(lines) - empty_lines
            
            if content_lines == 0:
                errors.append("Aucune ligne avec du contenu")
            
            print(f"📄 Texte validé : {len(lines)} lignes totales, {content_lines} lignes de contenu")
            
        except Exception as e:
            errors.append(f"Erreur lecture fichier texte : {e}")
        
        return errors
    
    def _validate_json(self):
        """Valide un fichier JSON (fallback)."""
        errors = []
        
        try:
            import json
            with open(self.args.artefact, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            print(f"📋 JSON validé : {type(json_data).__name__} de niveau racine")
            
        except json.JSONDecodeError as e:
            errors.append(f"JSON invalide : {e}")
        except Exception as e:
            errors.append(f"Erreur lecture JSON : {e}")
        
        return errors
    
    def _detect_file_type(self):
        """
        Détecte automatiquement le type de fichier.
        """
        if not os.path.exists(self.args.artefact):
            return 'txt'  # Par défaut
        
        # Détection par extension
        ext = Path(self.args.artefact).suffix.lower()
        
        extension_map = {
            '.csv': 'csv',
            '.md': 'markdown', 
            '.markdown': 'markdown',
            '.txt': 'txt',
            '.json': 'json'
        }
        
        return extension_map.get(ext, 'txt')
    
    def _display_validation_summary(self):
        """
        Affiche un résumé de la validation réussie.
        """
        file_size = os.path.getsize(self.args.artefact)
        
        print(f"📋 Résumé de validation :")
        print(f"   • Fichier : {Path(self.args.artefact).name}")
        print(f"   • Type : {self.args.type_attendu}")
        print(f"   • Taille : {self._format_size(file_size)}")
        
        try:
            with open(self.args.artefact, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            print(f"   • Lignes : {line_count}")
        except Exception:
            print(f"   • Lignes : Non déterminable")
        
        print(f"   • Validation : {datetime.now().strftime('%H:%M:%S')}")
    
    def _format_size(self, size_bytes):
        """Formate la taille en bytes de manière lisible."""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB']
        i = 0
        while size_bytes >= 1024.0 and i < len(units) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {units[i]}"


if __name__ == "__main__":
    validator = ValidationArtefact()
    validator.run()
