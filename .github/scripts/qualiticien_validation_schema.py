#!/usr/bin/env python3
"""
Qualiticien : Validation de Schéma
Script générique pour valider la structure JSON des artefacts selon des schémas prédéfinis.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class ValidationSchema:
    def __init__(self):
        """Initialise le validateur avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Valide la structure JSON d\'un artefact')
        parser.add_argument('--artefact', required=True,
                          help='Nom de l\'artefact JSON à valider')
        parser.add_argument('--schema-type', required=True,
                          help='Type de schéma à appliquer')
        parser.add_argument('--schema-custom', required=False,
                          help='Schéma JSON personnalisé (optionnel)')
        parser.add_argument('--mode-strict', action='store_true',
                          help='Mode strict : toutes les clés doivent être présentes')
        
        self.args = parser.parse_args()
        
        # Chargement du schéma selon le type
        self.schema = self._load_schema()
        
        if not self.schema:
            print(f"❌ ERREUR: Schema type '{self.args.schema_type}' non reconnu", file=sys.stderr)
            sys.exit(1)
    
    def run(self):
        """
        Logique principale : charge l'artefact JSON et valide sa structure
        contre le schéma approprié.
        """
        try:
            print(f"🔍 Validation schéma : {self.args.schema_type}")
            print(f"📄 Artefact : {self.args.artefact}")
            print(f"⚙️  Mode strict : {'Activé' if self.args.mode_strict else 'Désactivé'}")
            
            # Chargement de l'artefact JSON
            data = self._load_artifact()
            
            if data is None:
                print("❌ Impossible de charger l'artefact")
                sys.exit(1)
            
            # Validation du schéma
            errors = self._validate_schema(data)
            
            if errors:
                print(f"❌ VALIDATION ÉCHOUÉE : {len(errors)} erreur(s) détectée(s)")
                for i, error in enumerate(errors, 1):
                    print(f"   {i}. {error}")
                sys.exit(1)
            else:
                print("✅ VALIDATION RÉUSSIE : Structure conforme au schéma")
                
                # Affichage d'un résumé de validation
                self._display_validation_summary(data)
            
        except Exception as e:
            print(f"❌ ERREUR lors de la validation : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _load_schema(self):
        """
        Charge le schéma de validation selon le type spécifié.
        """
        if self.args.schema_custom:
            try:
                return json.loads(self.args.schema_custom)
            except json.JSONDecodeError as e:
                print(f"❌ Schema personnalisé invalide : {e}", file=sys.stderr)
                return None
        
        # Schémas prédéfinis pour les différents types d'artefacts AGI
        schemas = {
            # Division Loi Lignes
            'resultats-bruts-compteur': {
                'required_keys': ['fichiers', 'total_fichiers', 'timestamp'],
                'optional_keys': ['stats_globales', 'erreurs'],
                'nested_validations': {
                    'fichiers': 'array_of_objects',
                    'fichiers[].nom': 'string',
                    'fichiers[].lignes': 'number',
                    'fichiers[].chemin': 'string'
                }
            },
            'resultats-juges': {
                'required_keys': ['evaluations', 'limite_lignes', 'timestamp'],
                'optional_keys': ['resume', 'violations_critiques'],
                'nested_validations': {
                    'evaluations': 'array_of_objects',
                    'evaluations[].fichier': 'string',
                    'evaluations[].lignes': 'number',
                    'evaluations[].statut': 'string',
                    'evaluations[].conforme': 'boolean'
                }
            },
            'statistiques': {
                'required_keys': ['total_fichiers', 'total_lignes', 'moyenne_lignes'],
                'optional_keys': ['median_lignes', 'max_lignes', 'min_lignes', 'ecart_type'],
                'nested_validations': {
                    'total_fichiers': 'number',
                    'total_lignes': 'number',
                    'moyenne_lignes': 'number'
                }
            },
            'rapport-lignes': {
                'required_keys': ['en_tetes', 'lignes_donnees'],
                'optional_keys': ['metadata', 'format_version'],
                'nested_validations': {
                    'en_tetes': 'array',
                    'lignes_donnees': 'array_of_arrays'
                }
            },
            'recommandations': {
                'required_keys': ['recommandations', 'priorite_globale'],
                'optional_keys': ['actions_immediates', 'actions_long_terme'],
                'nested_validations': {
                    'recommandations': 'array_of_objects',
                    'recommandations[].type': 'string',
                    'recommandations[].message': 'string',
                    'recommandations[].priorite': 'string'
                }
            },
            
            # Division Loi Sécurité
            'violations-brutes': {
                'required_keys': ['violations', 'timestamp'],
                'optional_keys': ['regles_appliquees', 'stats'],
                'nested_validations': {
                    'violations': 'array_of_objects',
                    'violations[].fichier': 'string',
                    'violations[].ligne': 'number',
                    'violations[].regle': 'string',
                    'violations[].severite': 'string'
                }
            },
            'violations-triees': {
                'required_keys': ['critique', 'haute', 'moyenne', 'basse'],
                'optional_keys': ['info', 'stats_par_severite'],
                'nested_validations': {
                    'critique': 'array',
                    'haute': 'array',
                    'moyenne': 'array',
                    'basse': 'array'
                }
            },
            
            # Division Loi Documentation
            'faits-documentation': {
                'required_keys': ['elements', 'timestamp'],
                'optional_keys': ['stats_extraction', 'fichiers_analyses'],
                'nested_validations': {
                    'elements': 'array_of_objects',
                    'elements[].type': 'string',
                    'elements[].nom': 'string',
                    'elements[].a_une_docstring': 'boolean',
                    'elements[].fichier': 'string'
                }
            },
            'statistiques-documentation': {
                'required_keys': ['couverture_globale', 'total_elements', 'elements_documentes'],
                'optional_keys': ['couverture_par_type', 'seuils_respectes'],
                'nested_validations': {
                    'couverture_globale': 'number',
                    'total_elements': 'number',
                    'elements_documentes': 'number'
                }
            },
            
            # Division Loi Issues
            'violations-critiques': {
                'required_keys': ['violations', 'timestamp'],
                'optional_keys': ['source_rapports', 'filtres_appliques'],
                'nested_validations': {
                    'violations': 'array_of_objects',
                    'violations[].type': 'string',
                    'violations[].fichier': 'string',
                    'violations[].description': 'string',
                    'violations[].severite': 'string'
                }
            },
            
            # Schémas génériques
            'generic-json': {
                'required_keys': [],
                'optional_keys': ['*'],
                'nested_validations': {}
            },
            'liste-fichiers': {
                'required_keys': ['fichiers', 'total_fichiers'],
                'optional_keys': ['pattern', 'exclusions', 'timestamp'],
                'nested_validations': {
                    'fichiers': 'array',
                    'total_fichiers': 'number'
                }
            }
        }
        
        return schemas.get(self.args.schema_type)
    
    def _load_artifact(self):
        """
        Charge et parse l'artefact JSON à valider.
        """
        try:
            if not os.path.exists(self.args.artefact):
                print(f"❌ Artefact introuvable : {self.args.artefact}")
                return None
            
            with open(self.args.artefact, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📊 Artefact chargé : {len(str(data))} caractères JSON")
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide : {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur chargement artefact : {e}")
            return None
    
    def _validate_schema(self, data):
        """
        Valide les données contre le schéma chargé.
        """
        errors = []
        
        # Validation des clés requises
        for required_key in self.schema.get('required_keys', []):
            if required_key not in data:
                errors.append(f"Clé requise manquante : '{required_key}'")
        
        # Validation en mode strict (toutes les clés doivent être connues)
        if self.args.mode_strict:
            allowed_keys = set(self.schema.get('required_keys', [])) | set(self.schema.get('optional_keys', []))
            
            # Exclusion de la clé spéciale '*' qui autorise tout
            if '*' in allowed_keys:
                allowed_keys.remove('*')
            else:
                for key in data.keys():
                    if key not in allowed_keys:
                        errors.append(f"Clé non autorisée en mode strict : '{key}'")
        
        # Validations imbriquées
        for validation_path, expected_type in self.schema.get('nested_validations', {}).items():
            try:
                value = self._get_nested_value(data, validation_path)
                if value is not None and not self._validate_type(value, expected_type):
                    errors.append(f"Type incorrect pour '{validation_path}' : attendu '{expected_type}'")
            except Exception as e:
                if '[].', in validation_path:  # Validation de tableau optionnelle
                    continue
                errors.append(f"Erreur validation '{validation_path}' : {e}")
        
        return errors
    
    def _get_nested_value(self, data, path):
        """
        Récupère une valeur imbriquée dans la structure JSON selon le chemin.
        """
        if '[].' in path:
            # Cas spécial : validation d'éléments de tableau
            base_path, item_key = path.split('[].', 1)
            
            base_value = data
            if base_path:
                for key in base_path.split('.'):
                    if key in base_value:
                        base_value = base_value[key]
                    else:
                        return None
            
            if isinstance(base_value, list) and len(base_value) > 0:
                # Valider le premier élément comme échantillon
                sample_item = base_value[0]
                if isinstance(sample_item, dict) and item_key in sample_item:
                    return sample_item[item_key]
            return None
        else:
            # Cas standard : navigation dans l'objet
            value = data
            for key in path.split('.'):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value
    
    def _validate_type(self, value, expected_type):
        """
        Valide qu'une valeur correspond au type attendu.
        """
        type_validators = {
            'string': lambda x: isinstance(x, str),
            'number': lambda x: isinstance(x, (int, float)),
            'boolean': lambda x: isinstance(x, bool),
            'array': lambda x: isinstance(x, list),
            'object': lambda x: isinstance(x, dict),
            'array_of_objects': lambda x: isinstance(x, list) and all(isinstance(item, dict) for item in x),
            'array_of_strings': lambda x: isinstance(x, list) and all(isinstance(item, str) for item in x),
            'array_of_arrays': lambda x: isinstance(x, list) and all(isinstance(item, list) for item in x)
        }
        
        validator = type_validators.get(expected_type)
        return validator(value) if validator else False
    
    def _display_validation_summary(self, data):
        """
        Affiche un résumé de la validation réussie.
        """
        print(f"📋 Résumé de validation :")
        
        # Comptage des clés principales
        if isinstance(data, dict):
            print(f"   • Clés principales : {len(data.keys())}")
            
            # Affichage des clés trouvées
            required_keys = self.schema.get('required_keys', [])
            optional_keys = self.schema.get('optional_keys', [])
            
            found_required = [k for k in required_keys if k in data]
            found_optional = [k for k in optional_keys if k in data and k != '*']
            
            if found_required:
                print(f"   • Clés requises présentes : {', '.join(found_required)}")
            
            if found_optional:
                print(f"   • Clés optionnelles présentes : {', '.join(found_optional)}")
        
        elif isinstance(data, list):
            print(f"   • Type : Tableau de {len(data)} éléments")
        
        print(f"   • Schema appliqué : {self.args.schema_type}")
        print(f"   • Validation terminée : {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    validator = ValidationSchema()
    validator.run()
