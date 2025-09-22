#!/usr/bin/env python3
"""
Travailleur : Applicateur de Regex
Brique spécialisée dans l'application d'expressions régulières sur du contenu textuel.
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime


class RegexApplicateur:
    def __init__(self):
        """Initialise l'applicateur regex avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Applique des expressions régulières sur du contenu')
        parser.add_argument('--contenu', required=True,
                          help='Contenu textuel à analyser (ou chemin vers fichier)')
        parser.add_argument('--regle-regex', required=True,
                          help='JSON string avec la configuration regex')
        parser.add_argument('--sortie', default='resultats-regex.json',
                          help='Nom du fichier JSON de sortie')
        
        self.args = parser.parse_args()
        
        # Parsing de la règle regex
        try:
            self.regle = json.loads(self.args.regle_regex)
            self._validate_regle()
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR: Configuration regex invalide - {e}", file=sys.stderr)
            sys.exit(1)
    
    def _validate_regle(self):
        """Valide la structure de la règle regex."""
        required_fields = ['pattern']
        for field in required_fields:
            if field not in self.regle:
                raise ValueError(f"Champ requis manquant dans la règle : {field}")
        
        # Valeurs par défaut
        self.regle.setdefault('flags', [])
        self.regle.setdefault('nom', 'regex_search')
        self.regle.setdefault('description', 'Recherche par expression régulière')
        self.regle.setdefault('capture_groupes', True)
        self.regle.setdefault('limite_resultats', 1000)
    
    def run(self):
        """
        Logique principale : applique l'expression régulière sur le contenu
        et retourne toutes les correspondances trouvées avec leurs métadonnées.
        """
        try:
            print(f"🔎 Application regex : {self.regle['nom']}")
            print(f"📋 Pattern : {self.regle['pattern']}")
            
            # Récupération du contenu
            contenu = self._get_content()
            
            if not contenu:
                print("⚠️  Contenu vide - aucune correspondance possible")
                self._write_empty_results()
                return
            
            print(f"📄 Analyse de {len(contenu)} caractères")
            
            # Compilation du pattern regex avec les flags
            try:
                compiled_regex = self._compile_regex()
            except re.error as e:
                print(f"❌ ERREUR: Pattern regex invalide - {e}", file=sys.stderr)
                sys.exit(1)
            
            # Application de l'expression régulière
            correspondances = self._find_matches(compiled_regex, contenu)
            
            # Limitation des résultats si nécessaire
            if len(correspondances) > self.regle['limite_resultats']:
                print(f"⚠️  Limitation : {len(correspondances)} correspondances trouvées, "
                      f"gardant les {self.regle['limite_resultats']} premières")
                correspondances = correspondances[:self.regle['limite_resultats']]
            
            print(f"✅ {len(correspondances)} correspondances trouvées")
            
            # Préparation des résultats
            resultats = {
                "regle": self.regle,
                "timestamp": datetime.now().isoformat(),
                "contenu_stats": {
                    "taille_caracteres": len(contenu),
                    "lignes": contenu.count('\n') + 1,
                    "taille_analysee": len(contenu)
                },
                "total_correspondances": len(correspondances),
                "correspondances": correspondances
            }
            
            # Écriture du fichier de résultats
            Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.args.sortie, 'w', encoding='utf-8') as f:
                json.dump(resultats, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Résultats sauvegardés : {self.args.sortie}")
            
            # Affichage d'un échantillon
            self._display_sample_matches(correspondances)
            
        except Exception as e:
            print(f"❌ ERREUR lors de l'application regex : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _get_content(self):
        """
        Récupère le contenu à analyser (soit directement, soit depuis un fichier).
        """
        contenu = self.args.contenu
        
        # Si c'est un chemin de fichier existant, lire le fichier
        if os.path.exists(contenu):
            print(f"📁 Lecture du fichier : {contenu}")
            try:
                with open(contenu, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                # Essayer avec un encodage différent
                try:
                    with open(contenu, 'r', encoding='latin-1') as f:
                        return f.read()
                except Exception as e:
                    print(f"⚠️  Erreur lecture fichier : {e}")
                    return contenu  # Traiter comme du texte direct
        
        # Traiter comme du contenu textuel direct
        return contenu
    
    def _compile_regex(self):
        """
        Compile l'expression régulière avec les flags appropriés.
        """
        flags = 0
        
        for flag_name in self.regle['flags']:
            flag_name = flag_name.upper()
            if hasattr(re, flag_name):
                flags |= getattr(re, flag_name)
            elif flag_name == 'IGNORECASE' or flag_name == 'I':
                flags |= re.IGNORECASE
            elif flag_name == 'MULTILINE' or flag_name == 'M':
                flags |= re.MULTILINE
            elif flag_name == 'DOTALL' or flag_name == 'S':
                flags |= re.DOTALL
            else:
                print(f"⚠️  Flag regex inconnu ignoré : {flag_name}")
        
        return re.compile(self.regle['pattern'], flags)
    
    def _find_matches(self, compiled_regex, contenu):
        """
        Trouve toutes les correspondances et extrait les métadonnées.
        """
        correspondances = []
        
        for match in compiled_regex.finditer(contenu):
            correspondance = {
                "match_complet": match.group(0),
                "position_debut": match.start(),
                "position_fin": match.end(),
                "ligne": contenu[:match.start()].count('\n') + 1,
                "colonne": match.start() - contenu.rfind('\n', 0, match.start())
            }
            
            # Capture des groupes si demandé
            if self.regle['capture_groupes'] and match.groups():
                correspondance["groupes"] = list(match.groups())
                correspondance["groupes_nommes"] = match.groupdict()
            
            # Contexte autour de la correspondance (optionnel)
            contexte_avant = contenu[max(0, match.start()-50):match.start()]
            contexte_apres = contenu[match.end():match.end()+50]
            correspondance["contexte"] = {
                "avant": contexte_avant.replace('\n', '\\n'),
                "apres": contexte_apres.replace('\n', '\\n')
            }
            
            correspondances.append(correspondance)
        
        return correspondances
    
    def _write_empty_results(self):
        """Écrit un fichier de résultats vide."""
        resultats = {
            "regle": self.regle,
            "timestamp": datetime.now().isoformat(),
            "contenu_stats": {
                "taille_caracteres": 0,
                "lignes": 0,
                "taille_analysee": 0
            },
            "total_correspondances": 0,
            "correspondances": []
        }
        
        Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
        with open(self.args.sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)
    
    def _display_sample_matches(self, correspondances):
        """Affiche un échantillon des correspondances trouvées."""
        if not correspondances:
            print("📋 Aucune correspondance trouvée")
            return
        
        print("🔍 Échantillon des correspondances :")
        for i, match in enumerate(correspondances[:3]):
            print(f"   {i+1}. Ligne {match['ligne']}: '{match['match_complet'][:50]}'")
            if len(match['match_complet']) > 50:
                print("      [...]")
        
        if len(correspondances) > 3:
            print(f"   ... et {len(correspondances) - 3} autres correspondances")


if __name__ == "__main__":
    applicateur = RegexApplicateur()
    applicateur.run()
