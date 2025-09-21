"""
PROJET PROMETHEUS - MODULE SPÉCIALISÉ CODEVALIDATOR (V1.0)

Mission: Agir comme un expert de l'assurance qualité du code. Ce module
est le "juge" du CodeHunter.

Responsabilités:
- Charger la carte des concepts de code.
- Valider la syntaxe d'un snippet de code.
- Valider la PERTINENCE sémantique d'un snippet par rapport à un concept.
- Analyser les constructions présentes dans le code (fonctions, classes, etc.).
- Gérer l'interface de validation finale avec le Superviseur.
"""

import ast
import re
from typing import List, Dict


# --- CLASSE DE COULEURS PARTAGÉE ---
class Colors:
    """TODO: Add docstring."""
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class CodeValidator:
    """
    Spécialiste de la validation syntaxique et sémantique du code.
    """

    def __init__(self, supervisor_interface, local_reader):
        """
        Initialise le validateur de code.

        Args:
            supervisor_interface: L'interface pour parler au Superviseur.
            local_reader: L'instance du LocalReader pour accéder à la carte des concepts.
        """
        self.supervisor = supervisor_interface
        self.local_reader = local_reader
        print(f"{Colors.OKCYAN}[CODE-VALIDATOR] - Module initialisé.{Colors.ENDC}")

    def validate_snippet(self, snippet: str, concept_name: str) -> Dict | None:
        """
        Méthode principale. Orchestre la validation complète d'un snippet.

        Returns:
            Dict | None: Un dictionnaire de validation si le code est valide et pertinent, sinon None.
        """
        # 1. Validation de la syntaxe
        syntax_check = self._check_syntax(snippet)
        if not syntax_check["is_valid"]:
            print(
                f"{Colors.FAIL}[CODE-VALIDATOR] - Rejet: Syntaxe invalide. Erreur: {syntax_check['error']}{Colors.ENDC}"
            )
            return None

        # 2. Validation de la pertinence sémantique
        concept_data = self.local_reader.find_concept_data(concept_name)
        if not concept_data:
            print(
                f"{Colors.FAIL}[CODE-VALIDATOR] - Rejet: Concept '{concept_name}' inconnu, impossible de valider la pertinence.{Colors.ENDC}"
            )
            return None

        relevance_check = self._check_relevance(snippet, concept_data)
        if not relevance_check["is_relevant"]:
            print(
                f"{Colors.FAIL}[CODE-VALIDATOR] - Rejet: Non pertinent. Le motif '{relevance_check['pattern']}' est manquant.{Colors.ENDC}"
            )
            return None

        # 3. Si tout est bon, on prépare le rapport de validation
        validation_report = {
            "syntax_valid": True,
            "relevance_valid": True,
            "constructs": syntax_check.get("constructs", []),
            "line_count": syntax_check.get("line_count", 0),
        }

        print(
            f"{Colors.OKGREEN}[CODE-VALIDATOR] - Succès: Le snippet est valide et pertinent pour '{concept_name}'.{Colors.ENDC}"
        )
        return validation_report

    def _check_syntax(self, code: str) -> Dict:
        """Valide la syntaxe Python du code en utilisant l'AST."""
        try:
            tree = ast.parse(code)
            constructs = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    constructs.append(f"fonction '{node.name}'")
                elif isinstance(node, ast.ClassDef):
                    constructs.append(f"classe '{node.name}'")
                elif isinstance(node, ast.For):
                    constructs.append("boucle for")
                elif isinstance(node, ast.If):
                    constructs.append("condition if")

            return {
                "is_valid": True,
                "error": None,
                "constructs": list(set(constructs)),  # Élimine les doublons
                "line_count": len(code.split("\n")),
            }
        except SyntaxError as e:
            return {"is_valid": False, "error": f"Ligne {e.lineno}: {e.msg}"}
        except Exception as e:
            return {"is_valid": False, "error": str(e)}

    def _check_relevance(self, code: str, concept_data: Dict) -> Dict:
        """
        Valide si le code est un exemple pertinent du concept
        en utilisant le 'validation_pattern' de la carte des concepts.
        """
        pattern = concept_data.get("validation_pattern")
        if not pattern:
            # Si pas de motif, on considère pertinent par défaut (cas rare)
            return {"is_relevant": True, "pattern": None}

        # On utilise une expression régulière simple pour trouver le motif
        # 're.MULTILINE' permet de chercher sur plusieurs lignes
        if re.search(pattern, code, re.MULTILINE):
            return {"is_relevant": True, "pattern": pattern}
        else:
            return {"is_relevant": False, "pattern": pattern}

    def present_for_final_approval(
        self, snippet: str, concept_name: str, source_url: str, validation_report: Dict
    ) -> bool:
        """
        Présente un snippet pré-validé au Superviseur pour l'approbation finale.
        """
        print(f"\n{Colors.HEADER}--- VALIDATION FINALE DU SUPERVISEUR ---{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Concept:{Colors.ENDC} {concept_name}")
        print(f"{Colors.OKBLUE}Source:{Colors.ENDC} {source_url}")

        constructs = validation_report.get("constructs", [])
        if constructs:
            print(
                f"{Colors.OKGREEN}Constructions détectées:{Colors.ENDC} {', '.join(constructs)}"
            )

        print(
            f"{Colors.OKBLUE}Code ({validation_report.get('line_count', 0)} lignes):{Colors.ENDC}"
        )
        self._display_code_snippet(snippet)

        return (
            self.supervisor.get_authorization(
                "Approuvez-vous ce code comme exemple final ?"
            )
            == "oui"
        )

    def _display_code_snippet(self, code: str):
        """Affichage amélioré du code avec numérotation."""
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            print(f"{Colors.WARNING}{i:2d}:{Colors.ENDC} {line}")