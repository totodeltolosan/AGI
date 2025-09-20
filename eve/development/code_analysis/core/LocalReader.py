"""
PROJET PROMETHEUS - MODULE SPÉCIALISÉ LOCALREADER (V1.0)

Mission: Agir comme un bibliothécaire expert pour la BiblePython locale.
Ce module remplace complètement le WebSearcher.

Responsabilités:
- Indexer le contenu de tous les fichiers de la BiblePython au démarrage.
- Charger la carte des concepts de code (`code_concepts_map.json`).
- Recevoir une demande pour un concept et trouver le fichier le plus pertinent.
- Retourner le contenu textuel complet du fichier trouvé.
"""

import json
import os
from typing import List, Dict, Tuple


# --- CLASSE DE COULEURS PARTAGÉE ---
class Colors:
    """TODO: Add docstring."""
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


class LocalReader:
    """
    Spécialiste de la lecture et de l'indexation de la BiblePython locale.
    """

    def __init__(
        self,
        library_path: str = "BiblePython",
        concepts_map_file: str = "code_concepts_map.json",
    ):
        """
        Initialise le lecteur local.

        Args:
            library_path (str): Le chemin vers le dossier de la BiblePython.
            concepts_map_file (str): Le chemin vers le fichier de la carte des concepts.
        """
        self.library_path = library_path
        self.concepts_map = self._load_concepts_map(concepts_map_file)
        self.file_index = {}  # Dictionnaire pour stocker l'index: {filepath: content}

        if not os.path.isdir(self.library_path):
            print(
                f"{Colors.FAIL}[LOCAL-READER] - ERREUR CRITIQUE: Le dossier '{self.library_path}' est introuvable.{Colors.ENDC}"
            )
            print(
                f"{Colors.FAIL}Veuillez exécuter: git clone https://github.com/swaroopch/byte-of-python.git BiblePython{Colors.ENDC}"
            )
            exit(1)

        self._build_index()
        print(
            f"{Colors.OKCYAN}[LOCAL-READER] - Module initialisé. {len(self.file_index)} fichiers indexés depuis la BiblePython.{Colors.ENDC}"
        )

    """TODO: Add docstring."""
    def _load_concepts_map(self, file_path: str) -> List[Dict]:
        if not os.path.exists(file_path):
            print(
                f"{Colors.FAIL}[LOCAL-READER] - ERREUR CRITIQUE: Fichier '{file_path}' introuvable.{Colors.ENDC}"
            )
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("concepts", [])
        except Exception as e:
            print(
                f"{Colors.FAIL}[LOCAL-READER] - ERREUR CRITIQUE: Impossible de charger '{file_path}': {e}{Colors.ENDC}"
            )
            return []

    def _build_index(self):
        """
        Scanne la BiblePython et charge le contenu de chaque fichier .md en mémoire.
        """
        print(
            f"{Colors.OKCYAN}[LOCAL-READER] - Construction de l'index de la bibliothèque...{Colors.ENDC}"
        )
        for filename in os.listdir(self.library_path):
            if filename.endswith(".md"):
                file_path = os.path.join(self.library_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.file_index[file_path] = f.read().lower()
                except Exception as e:
                    print(
                        f"{Colors.FAIL}[LOCAL-READER] - AVERTISSEMENT: Impossible de lire le fichier '{file_path}': {e}{Colors.ENDC}"
                    )
                        """TODO: Add docstring."""

    def find_concept_data(self, concept_name: str) -> Dict | None:
        for concept in self.concepts_map:
            if concept.get("name") == concept_name.lower():
                return concept
        return None

    def find_content_for_concept(self, concept_name: str) -> Tuple[str, str] | None:
        """
        Méthode principale. Trouve le contenu le plus pertinent pour un concept.

        Returns:
            Tuple[str, str] | None: Un tuple contenant (chemin_du_fichier, contenu_du_fichier) ou None si rien n'est trouvé.
        """
        print(
            f"{Colors.OKCYAN}[LOCAL-READER] - Recherche du contenu pour le concept: '{concept_name}'{Colors.ENDC}"
        )

        concept_data = self.find_concept_data(concept_name)
        if not concept_data:
            print(
                f"{Colors.FAIL}[LOCAL-READER] - AVERTISSEMENT: Concept '{concept_name}' non trouvé dans la carte.{Colors.ENDC}"
            )
            return None

        # Utilise les termes de recherche pour trouver le meilleur fichier
        search_terms = concept_data.get("search_queries", [])
        best_match_file = None
        highest_score = 0

        for file_path, content in self.file_index.items():
            current_score = 0
            for term in search_terms:
                # Donne plus de poids aux termes de recherche principaux
                if term in content:
                    current_score += content.count(term)

            # Bonus si le nom du concept est dans le nom du fichier
            if concept_name.lower() in os.path.basename(file_path):
                current_score += 10

            if current_score > highest_score:
                highest_score = current_score
                best_match_file = file_path

        if not best_match_file:
            print(
                f"{Colors.FAIL}[LOCAL-READER] - ÉCHEC: Aucun contenu pertinent trouvé pour '{concept_name}' dans la BiblePython.{Colors.ENDC}"
            )
            return None

        # Retourne le contenu original (non-minuscule) du meilleur fichier trouvé
        original_content = ""
        try:
            with open(best_match_file, "r", encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            print(
                f"{Colors.FAIL}[LOCAL-READER] - ERREUR: Impossible de relire le fichier '{best_match_file}': {e}{Colors.ENDC}"
            )
            return None

        print(
            f"{Colors.OKGREEN}[LOCAL-READER] - SUCCÈS: Contenu trouvé dans le fichier '{os.path.basename(best_match_file)}' (Score: {highest_score}){Colors.ENDC}"
        )
        return best_match_file, original_content


# --- BLOC DE TEST INDÉPENDANT ---
if __name__ == "__main__":
    print(f"{Colors.OKCYAN}--- TEST DU MODULE LOCALREADER ---{Colors.ENDC}")

    reader = LocalReader()

    if reader.file_index:
        print("\n--- Test 1: Recherche pour 'fonction' ---")
        result = reader.find_content_for_concept("fonction")
        if result:
            file_path, content = result
            print(f"  Fichier trouvé: {os.path.basename(file_path)}")
            print(f"  Taille du contenu: {len(content)} caractères")
            print(f"  Extrait: {content[:100].strip()}...")
        else:
            print("  Aucun résultat.")

        print("\n--- Test 2: Recherche pour 'classe' ---")
        result = reader.find_content_for_concept("classe")
        if result:
            file_path, content = result
            print(f"  Fichier trouvé: {os.path.basename(file_path)}")
            print(f"  Taille du contenu: {len(content)} caractères")
            print(f"  Extrait: {content[:100].strip()}...")
        else:
            print("  Aucun résultat.")