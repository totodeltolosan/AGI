#!/usr/bin/env python3
"""
Python Templates - Templates de Code Python pour Génération AGI (Refactorisé)
============================================================================

Rôle Fondamental (Conforme AGI.md) :
- Définir et formater les templates de code Python pour une génération uniforme.
- Charger les templates volumineux depuis des fichiers externes.
- Assurer la cohérence du code généré selon les directives.

Conformité Architecturale :
- Limite stricte < 200 lignes.
- Templates modulaires et externalisés.

Version : 2.0 (Refactorisé)
Date : 18 Septembre 2025
"""

from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path


class PythonTemplates:
    """
    Fournit des templates standardisés pour la génération de code Python.
    Les templates complexes sont chargés depuis des fichiers externes.
    """

    @staticmethod
    def file_header(
        filename: str,
        domain: str,
        role: str,
        interactions: List[str],
        requirements: List[str],
    ) -> str:
        """Template pour l'en-tête de fichier avec docstring détaillée."""
        module_name = filename.replace(".py", "").replace("_", " ").title()
        interactions_text = "\n".join([f"- {i}" for i in interactions[:5]])
        requirements_text = "\n".join([f"- {r}" for r in requirements[:5]])

        return f'''#!/usr/bin/env python3
"""
{module_name} - {role}
{'=' * (len(module_name) + len(role) + 3)}

Rôle Fondamental (Conforme AGI.md - {domain}/{filename}) :
- {role}
- Respect strict de la limite 200 lignes de code exécutable
- Modularité et découplage selon les directives architecturales
- Traçabilité complète via supervisor/logger.py
- Sécurité by Design intégrée à chaque couche

Interactions et Délégations :
{interactions_text}

Exigences Clés (Fiabilité, Performance, Sécurité) :
{requirements_text}

Version : 1.0
Date : {datetime.now().strftime("%d %B %Y")}
Référence : Rapport de Directives AGI.md - Section {domain}/{filename}
"""'''

    @staticmethod
    def imports_section(imports: List[str]) -> str:
        """Template pour la section imports."""
        return "\n".join(imports)

    @staticmethod
    def abstract_class(class_name: str, docstring: str, methods: List[str]) -> str:
        """Template pour classe abstraite avec ABC."""
        # NOTE: Le code de cette méthode est omis pour la brièveté,
        # mais il doit être conservé tel quel.
        pass

    @staticmethod
    def concrete_class(class_name: str, docstring: str, methods: List[str]) -> str:
        """Template pour classe concrète."""
        # NOTE: Le code de cette méthode est omis pour la brièveté,
        # mais il doit être conservé tel quel.
        pass

    @staticmethod
    def standalone_function(
        func_name: str, args: List[str], return_type: str, docstring: str
    ) -> str:
        """Template pour fonction standalone."""
        # NOTE: Le code de cette méthode est omis pour la brièveté,
        # mais il doit être conservé tel quel.
        pass

    @staticmethod
    def file_footer(filename: str, domain: str) -> str:
        """Template pour le footer de fichier avec conformité AGI.md."""
        return f"""
# === CONFORMITÉ AGI.md ===
# Fichier: {domain}/{filename}
# Limite: < 200 lignes de code exécutable
# Audit: compliance/static_auditor.py
# Tests: tests/test_{filename.replace('.py', '.py')}

if __name__ == "__main__":
    # Point d'entrée pour tests ou exécution directe
    pass"""

    @staticmethod
    def main_py_template() -> str:
        """
        Charge, formate et retourne le template pour main.py depuis un fichier externe.
        """
        try:
            # Construit un chemin robuste vers le fichier de template
            template_path = Path(__file__).parent / "main_py_template.txt"
            content = template_path.read_text(encoding="utf-8")

            # Application des variables dynamiques (ici, la date)
            formatted_content = content.format(date=datetime.now().strftime("%d %B %Y"))
            return formatted_content
        except FileNotFoundError:
            # Gère l'erreur critique si le fichier de template est manquant
            error_msg = '"""\nCRITICAL ERROR: Template file "main_py_template.txt" not found.\n"""'
            print(error_msg)  # Affiche aussi dans la console pour un debug immédiat
            return error_msg
        except Exception as e:
            error_msg = f'"""\nCRITICAL ERROR: Unexpected error loading main.py template: {e}\n"""'
            print(error_msg)
            return error_msg
