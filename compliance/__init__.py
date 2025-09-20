#!/usr/bin/env python3
"""
Compliance Module - Système d'Audit Constitutionnel AGI (v2.1 Corrigé)
======================================================================

CHEMIN: compliance/__init__.py

Rôle Fondamental (Conforme iaGOD.json) :
- Marquer le répertoire 'compliance' comme un package Python.
- Ne contient plus d'imports directs pour éviter les dépendances circulaires
  lors de l'initialisation.
"""

__version__ = "2.1.0"
__author__ = "AGI Development Team (Refactored)"

# Les imports sont maintenant gérés directement par les modules qui en ont besoin.
# Cela rend le package plus robuste aux erreurs d'import circulaire.
