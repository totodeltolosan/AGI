#!/usr/bin/env python3
"""
Nettoyeur : Formateur Markdown
Transforme des données JSON en rapport Markdown lisible par l'humain.
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path


class MarkdownFormatter:
    def __init__(self):
        """Initialise le formateur Markdown avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Formate des données JSON en rapport Markdown')
        parser.add_argument('--artefact-entree-json', required=True,
                          help='Nom de l\'artefact JSON à consommer')
        parser.add_argument('--template-markdown', required=True,
                          help='Template Markdown avec placeholders')
        parser.add_argument('--nom-fichier-sortie', default='rapport.md',
                          help='Nom du fichier Markdown à créer')
        
        self.args = parser.parse_args()
    
    def run(self):
        """
        Logique principale : lit le JSON d'entrée, applique le template Markdown
        et génère un rapport formaté lisible par l'humain.
        """
        try:
            # Lecture du fichier JSON d'entrée
            if not os.path.exists(self.args.artefact_entree_json):
                print(f"❌ ERREUR: Fichier d'entrée introuvable : {self.args.artefact_entree_json}", 
                      file=sys.stderr)
                sys.exit(1)
            
            with open(self.args.artefact_entree_json, 'r', encoding='utf-8') as f:
                donnees_json = json.load(f)
            
            print(f"📄 Traitement des données pour rapport Markdown")
            
            # Préparation des données pour le template
            contexte_template = self._prepare_template_context(donnees_json)
            
            # Application du template
            rapport_markdown = self._apply_template(self.args.template_markdown, contexte_template)
            
            # Préparation du chemin de sortie
            Path(self.args.nom_fichier_sortie).parent.mkdir(parents=True, exist_ok=True)
            
            # Écriture du fichier Markdown
            with open(self.args.nom_fichier_sortie, 'w', encoding='utf-8') as f:
                f.write(rapport_markdown)
            
            print(f"✅ Rapport Markdown créé avec succès : {self.args.nom_fichier_sortie}")
            
            # Statistiques du rapport généré
            if os.path.exists(self.args.nom_fichier_sortie):
                taille = os.path.getsize(self.args.nom_fichier_sortie)
                with open(self.args.nom_fichier_sortie, 'r', encoding='utf-8') as f:
                    lignes = len(f.readlines())
                print(f"📊 Statistiques : {taille} octets, {lignes} lignes")
            
        except Exception as e:
            print(f"❌ ERREUR lors du formatage Markdown : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _prepare_template_context(self, donnees):
        """
        Prépare le contexte de données pour l'application du template.
        Ajoute des variables utiles comme la date, les statistiques, etc.
        """
        contexte = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'donnees': donnees
        }
        
        # Ajout de statistiques automatiques selon le type de données
        if isinstance(donnees, list):
            contexte['total_items'] = len(donnees)
            if len(donnees) > 0 and isinstance(donnees[0], dict):
                # Analyse des clés communes
                all_keys = set()
                for item in donnees:
                    if isinstance(item, dict):
                        all_keys.update(item.keys())
                contexte['colonnes'] = sorted(list(all_keys))
        
        elif isinstance(donnees, dict):
            contexte['total_cles'] = len(donnees.keys())
            contexte['cles'] = list(donnees.keys())
            
            # Recherche de métriques numériques
            contexte['metriques'] = {}
            for cle, valeur in donnees.items():
                if isinstance(valeur, (int, float)):
                    contexte['metriques'][cle] = valeur
        
        return contexte
    
    def _apply_template(self, template, contexte):
        """
        Applique le template Markdown en remplaçant les placeholders.
        Supporte les placeholders de type {{variable}} et {{#section}}...{{/section}}.
        """
        resultat = template
        
        # Remplacement des variables simples {{variable}}
        for cle, valeur in contexte.items():
            if isinstance(valeur, (str, int, float)):
                pattern = r'\{\{\s*' + re.escape(cle) + r'\s*\}\}'
                resultat = re.sub(pattern, str(valeur), resultat)
        
        # Remplacement des sections conditionnelles {{#if condition}}...{{/if}}
        if_pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
        for match in re.finditer(if_pattern, resultat, re.DOTALL):
            condition = match.group(1)
            contenu = match.group(2)
            
            if condition in contexte and contexte[condition]:
                resultat = resultat.replace(match.group(0), contenu)
            else:
                resultat = resultat.replace(match.group(0), '')
        
        # Remplacement des listes {{#each array}}...{{/each}}
        each_pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}'
        for match in re.finditer(each_pattern, resultat, re.DOTALL):
            array_name = match.group(1)
            item_template = match.group(2)
            
            if array_name in contexte and isinstance(contexte[array_name], list):
                items_html = []
                for item in contexte[array_name]:
                    item_content = item_template
                    if isinstance(item, dict):
                        for k, v in item.items():
                            item_content = item_content.replace(f'{{{{item.{k}}}}}', str(v))
                    else:
                        item_content = item_content.replace('{{item}}', str(item))
                    items_html.append(item_content)
                
                resultat = resultat.replace(match.group(0), '\n'.join(items_html))
            else:
                resultat = resultat.replace(match.group(0), '')
        
        # Formatage final - nettoyage des espaces et lignes vides multiples
        resultat = re.sub(r'\n\s*\n\s*\n', '\n\n', resultat)
        resultat = resultat.strip()
        
        return resultat


if __name__ == "__main__":
    formatter = MarkdownFormatter()
    formatter.run()
