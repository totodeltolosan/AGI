#!/usr/bin/env python3
"""
Travailleur : Parser AST Python
Brique d'analyse de code Python via l'Arbre de Syntaxe Abstraite (AST).
"""

import argparse
import json
import os
import sys
import ast
from pathlib import Path
from datetime import datetime


class ASTParser:
    def __init__(self):
        """Initialise le parser AST avec les arguments de ligne de commande."""
        parser = argparse.ArgumentParser(description='Parse le code Python en AST JSON')
        parser.add_argument('--contenu-fichier-python', required=True,
                          help='Contenu Python à analyser ou chemin vers fichier .py')
        parser.add_argument('--sortie', default='arbre-syntaxe.json',
                          help='Nom du fichier JSON de sortie')
        parser.add_argument('--niveau-detail', choices=['basic', 'complet'], default='complet',
                          help='Niveau de détail de l\'analyse AST')
        
        self.args = parser.parse_args()
    
    def run(self):
        """
        Logique principale : parse le code Python et génère une représentation
        JSON structurée de l'Arbre de Syntaxe Abstraite.
        """
        try:
            print(f"🐍 Analyse AST Python - Niveau: {self.args.niveau_detail}")
            
            # Récupération du code source Python
            code_source = self._get_python_source()
            
            if not code_source.strip():
                print("⚠️  Code source vide")
                self._write_empty_results()
                return
            
            print(f"📄 Analyse de {len(code_source)} caractères de code Python")
            
            # Parsing AST
            try:
                arbre_ast = ast.parse(code_source)
            except SyntaxError as e:
                print(f"❌ ERREUR: Syntaxe Python invalide - {e}", file=sys.stderr)
                self._write_error_results(f"Erreur syntaxe: {e}")
                return
            except Exception as e:
                print(f"❌ ERREUR: Échec parsing AST - {e}", file=sys.stderr)
                sys.exit(1)
            
            print("✅ AST parsé avec succès")
            
            # Analyse de la structure
            analyseur = StructureAnalyzer(self.args.niveau_detail)
            structure = analyseur.analyze(arbre_ast, code_source)
            
            # Préparation des résultats
            resultats = {
                "timestamp": datetime.now().isoformat(),
                "niveau_detail": self.args.niveau_detail,
                "code_stats": {
                    "taille_caracteres": len(code_source),
                    "lignes": code_source.count('\n') + 1,
                    "lignes_non_vides": len([l for l in code_source.split('\n') if l.strip()]),
                },
                "structure": structure,
                "elements_ast": analyseur.get_summary()
            }
            
            print(f"🔍 Éléments détectés: {analyseur.get_summary()}")
            
            # Écriture du fichier de résultats
            Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.args.sortie, 'w', encoding='utf-8') as f:
                json.dump(resultats, f, indent=2, ensure_ascii=False)
            
            print(f"📊 AST sauvegardé : {self.args.sortie}")
            
        except Exception as e:
            print(f"❌ ERREUR lors du parsing AST : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _get_python_source(self):
        """
        Récupère le code source Python (depuis fichier ou contenu direct).
        """
        contenu = self.args.contenu_fichier_python
        
        # Si c'est un chemin de fichier .py existant
        if os.path.exists(contenu) and contenu.endswith('.py'):
            print(f"📁 Lecture du fichier Python : {contenu}")
            try:
                with open(contenu, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                try:
                    with open(contenu, 'r', encoding='latin-1') as f:
                        return f.read()
                except Exception as e:
                    print(f"⚠️  Erreur lecture fichier : {e}")
                    return contenu
        
        # Traiter comme du code Python direct
        return contenu
    
    def _write_empty_results(self):
        """Écrit un fichier de résultats pour code vide."""
        resultats = {
            "timestamp": datetime.now().isoformat(),
            "niveau_detail": self.args.niveau_detail,
            "code_stats": {"taille_caracteres": 0, "lignes": 0, "lignes_non_vides": 0},
            "structure": {"type": "Module", "elements": []},
            "elements_ast": {"total": 0}
        }
        
        Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
        with open(self.args.sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)
    
    def _write_error_results(self, erreur):
        """Écrit un fichier de résultats en cas d'erreur de syntaxe."""
        resultats = {
            "timestamp": datetime.now().isoformat(),
            "niveau_detail": self.args.niveau_detail,
            "erreur": erreur,
            "code_stats": {"taille_caracteres": len(self.args.contenu_fichier_python), 
                          "lignes": self.args.contenu_fichier_python.count('\n') + 1, 
                          "lignes_non_vides": 0},
            "structure": None,
            "elements_ast": {"total": 0, "erreur": True}
        }
        
        Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
        with open(self.args.sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)


class StructureAnalyzer(ast.NodeVisitor):
    """Analyseur de structure AST Python."""
    
    def __init__(self, niveau_detail='complet'):
        self.niveau_detail = niveau_detail
        self.elements = []
        self.compteurs = {
            'classes': 0, 'fonctions': 0, 'methodes': 0, 'imports': 0,
            'variables': 0, 'decorateurs': 0, 'try_except': 0, 'boucles': 0
        }
        self.current_class = None
        self.source_lines = []
    
    def analyze(self, node, source):
        """Point d'entrée principal de l'analyse."""
        self.source_lines = source.split('\n')
        self.visit(node)
        return {
            "type": "Module",
            "elements": self.elements
        }
    
    def get_summary(self):
        """Retourne un résumé des éléments détectés."""
        return dict(self.compteurs, total=sum(self.compteurs.values()))
    
    def visit_ClassDef(self, node):
        """Visite une définition de classe."""
        self.compteurs['classes'] += 1
        
        classe_info = {
            "type": "ClassDef",
            "nom": node.name,
            "ligne": node.lineno,
            "decorateurs": [self._get_decorator_name(d) for d in node.decorator_list],
            "bases": [self._get_node_name(base) for base in node.bases]
        }
        
        if self.niveau_detail == 'complet':
            classe_info["docstring"] = ast.get_docstring(node)
            classe_info["methodes"] = []
        
        # Analyse des méthodes de la classe
        old_class = self.current_class
        self.current_class = node.name
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.compteurs['methodes'] += 1
                if self.niveau_detail == 'complet':
                    methode_info = self._analyze_function(item, is_method=True)
                    classe_info["methodes"].append(methode_info)
        
        self.current_class = old_class
        self.elements.append(classe_info)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visite une définition de fonction."""
        if self.current_class is None:  # Fonction de module, pas méthode
            self.compteurs['fonctions'] += 1
            
            fonction_info = self._analyze_function(node, is_method=False)
            self.elements.append(fonction_info)
        
        self.generic_visit(node)
    
    def _analyze_function(self, node, is_method=False):
        """Analyse une fonction ou méthode."""
        info = {
            "type": "MethodDef" if is_method else "FunctionDef",
            "nom": node.name,
            "ligne": node.lineno,
            "decorateurs": [self._get_decorator_name(d) for d in node.decorator_list],
            "arguments": len(node.args.args)
        }
        
        if self.niveau_detail == 'complet':
            info.update({
                "docstring": ast.get_docstring(node),
                "args": [arg.arg for arg in node.args.args],
                "returns": self._has_return_statements(node),
                "async": isinstance(node, ast.AsyncFunctionDef),
                "lignes_code": self._count_function_lines(node)
            })
        
        return info
    
    def visit_Import(self, node):
        """Visite un import."""
        self.compteurs['imports'] += 1
        
        import_info = {
            "type": "Import",
            "ligne": node.lineno,
            "modules": [alias.name for alias in node.names]
        }
        
        if self.niveau_detail == 'complet':
            import_info["aliases"] = [alias.asname for alias in node.names if alias.asname]
        
        self.elements.append(import_info)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visite un import from."""
        self.compteurs['imports'] += 1
        
        import_info = {
            "type": "ImportFrom",
            "ligne": node.lineno,
            "module": node.module,
            "names": [alias.name for alias in node.names]
        }
        
        self.elements.append(import_info)
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """Visite une assignation."""
        if self.current_class is None and isinstance(node.targets[0], ast.Name):
            self.compteurs['variables'] += 1
            
            if self.niveau_detail == 'complet':
                var_info = {
                    "type": "Assignment",
                    "ligne": node.lineno,
                    "variable": node.targets[0].id,
                    "type_valeur": type(node.value).__name__
                }
                self.elements.append(var_info)
        
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Visite un bloc try/except."""
        self.compteurs['try_except'] += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Visite une boucle for."""
        self.compteurs['boucles'] += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Visite une boucle while."""
        self.compteurs['boucles'] += 1
        self.generic_visit(node)
    
    def _get_decorator_name(self, decorator):
        """Extrait le nom d'un décorateur."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_node_name(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            return self._get_node_name(decorator.func)
        return str(decorator)
    
    def _get_node_name(self, node):
        """Extrait le nom d'un nœud AST."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return str(node)
    
    def _has_return_statements(self, func_node):
        """Vérifie si une fonction a des instructions return."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return):
                return True
        return False
    
    def _count_function_lines(self, func_node):
        """Compte les lignes de code d'une fonction."""
        if hasattr(func_node, 'end_lineno') and func_node.end_lineno:
            return func_node.end_lineno - func_node.lineno + 1
        return 0


if __name__ == "__main__":
    parser = ASTParser()
    parser.run()
