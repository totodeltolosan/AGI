# Système AGI - Architecture de Gouvernance Intelligente

## Description

Système avancé d'audit de code automatisé utilisant une architecture hiérarchique de 71 workflows GitHub Actions répartis sur 7 niveaux.

## Architecture - Face 1 (Gouvernance)

Le système est organisé en 7 niveaux hiérarchiques avec 71 workflows:

- **Niveau 0**: Maître (1 workflow) - contrôle humain
- **Niveau 1**: Orchestre (1 workflow) - point d'entrée automatique
- **Niveau 2**: Généraux (8 workflows) - coordination des audits
- **Niveaux 4-5**: Ouvriers et Qualiticiens (52 workflows) - exécution et validation
- **Niveau 6**: Travailleurs (6 workflows) - briques de base
- **Niveau 7**: Nettoyeurs (3 workflows) - formatage des résultats

**Total: 71 workflows pour la Face 1 (Gouvernance)**

## Installation

```bash
pip install -e .
```

## Usage Local

```bash
python run_agi_audit.py
```

## Constitution et Documentation

- `iaGOD.json` : Constitution complète du système
- `hierarchie.md` : Architecture hiérarchique détaillée
- `Systemeneuronal.md` : Spécifications techniques des workflows

## État du Système

- **Face 1 (Gouvernance)**: 71 workflows actifs
- **Faces 2-6**: En préparation

