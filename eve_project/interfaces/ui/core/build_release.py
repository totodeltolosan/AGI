#!/usr/bin/env python3
from pathlib import Path
from typing import Any, Dict


class ValidateurProjet:
    """Valide l'intégrité du projet avant publication."""

    @staticmethod
    def verifier_fichiers_requis() -> Dict[str, bool]:
        """Vérifie la présence de tous les fichiers critiques."""
        fichiers_critiques = [
            "lanceur.py",
            "requirements.txt",
            "config/config.json",
            "README.md",
            "enfant_eve/ia/cerveau.py",
            "enfant_eve/ia/planificateur.py",
            "enfant_eve/interface/tableau_bord.py",
            "enfant_eve/pont_jeu/connexion.py",
            "gestion_sauvegarde.py",
            "gestion_logs.py",
        ]

        resultats = {}
        for fichier in fichiers_critiques:
            resultats[fichier] = Path(fichier).exists()

        return resultats

    @staticmethod
    def verifier_syntaxe_python() -> Dict[str, Any]:
        """Vérifie la syntaxe de tous les fichiers Python."""
        fichiers_python = list(Path(".").rglob("*.py"))
        erreurs = []

        for fichier in fichiers_python:
            if "env/" in str(fichier) or "__pycache__" in str(fichier):
                continue

            try:
                with open(fichier, "r", encoding="utf-8") as f:
                    compile(f.read(), fichier, "exec")
            except SyntaxError as e:
                erreurs.append(f"{fichier}: {e}")

        return {"valide": len(erreurs) == 0, "erreurs": erreurs}

    @staticmethod
    def verifier_respect_limites() -> Dict[str, Any]:
        """Vérifie le respect de la limite de 150 lignes par fichier."""
        fichiers_python = list(Path(".").rglob("*.py"))
        violations = []

        for fichier in fichiers_python:
            if "env/" in str(fichier) or "__pycache__" in str(fichier):
                continue

            try:
                with open(fichier, "r", encoding="utf-8") as f:
                    nb_lignes = len(f.readlines())
                if nb_lignes > 150:
                    violations.append(f"{fichier}: {nb_lignes} lignes")
            except (OSError, UnicodeDecodeError):
                continue

        return {"conforme": len(violations) == 0, "violations": violations}
        return {"conforme": len(violations) == 0, "violations": violations}


class GenerateurDocumentation:
    """Génère la documentation finale du projet."""

    @staticmethod
    def generer_guide_installation() -> str:
        """Génère un guide d'installation détaillé."""
        guide = """# Guide d'Installation - Le Simulateur

## Prérequis Système
- Python 3.11 ou supérieur
- git
- 4 Go de RAM minimum
- 2 Go d'espace disque libre
- Connexion internet pour Minetest

## Installation Rapide

### 1. Cloner le projet
Remplacez `<repository_url>` par l'URL de votre dépôt Git.
```bash
git clone <repository_url>
cd le-simulateur
```

### 2. Créer un environnement virtuel
Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet.
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Installer les dépendances
Le fichier `requirements.txt` contient toutes les bibliothèques Python nécessaires.
```bash
pip install -r requirements.txt
```

## Lancement du Simulateur
Une fois l'installation terminée, vous pouvez lancer le simulateur.
```bash
python lanceur.py
```

Pour activer le mode debug, utilisez l'argument `--debug`.
```bash
python lanceur.py --debug
```
"""
        return guide
