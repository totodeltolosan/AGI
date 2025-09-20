#!/usr/bin/env python3
"""
Constitution Loader - Chargeur iaGOD.json Conforme COMP-CPL-001
================================================================

CHEMIN: compliance/loader.py

Rôle Fondamental (Conforme iaGOD.json COMP-CPL-001) :
- Charger et valider la constitution iaGOD.json en mémoire.
- Transformer les lois en objets `ConstitutionalLaw` conformes au contrat.
- Fournir une interface d'accès aux lois.
- Respecter la directive < 200 lignes.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# Import du contrat de données défini dans models.py
from .models import ConstitutionalLaw


class ConstitutionLoader:
    """
    Charge et parse la constitution `iaGOD.json` en objets `ConstitutionalLaw`.
    Conforme à la directive COMP-CPL-001.
    """

    def __init__(self, constitution_path: Optional[Path] = None):
        """TODO: Add docstring."""
        self.logger = logging.getLogger(__name__)
        self.constitution_path = constitution_path or Path("iaGOD.json")
        self._laws: Dict[str, ConstitutionalLaw] = {}

    def load(self) -> bool:
        """
        Charge et parse la constitution.

        Returns:
            True si le chargement et le parsing réussissent, False sinon.
        """
        if not self.constitution_path.exists():
            self.logger.error(f"Constitution introuvable: {self.constitution_path}")
            return False

        try:
            with self.constitution_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if not self._validate_schema(data):
                return False

            self._parse_laws(data)
            self.logger.info(f"Constitution chargée: {len(self._laws)} lois validées.")
            return True

        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur de parsing JSON dans iaGOD.json: {e}")
            return False
        except Exception as e:
            self.logger.error(
                f"Erreur fatale lors du chargement de la constitution: {e}"
            )
            return False

    def get_all_laws(self) -> Dict[str, ConstitutionalLaw]:
        """Retourne une copie de toutes les lois chargées."""
        return self._laws.copy()

    def is_loaded(self) -> bool:
        """Vérifie si la constitution a été chargée avec succès."""
        return bool(self._laws)

    def _validate_schema(self, data: Dict[str, Any]) -> bool:
        """Valide le schéma de base de la constitution."""
        required_fields = ["iaGOD_SpecVersion", "constitution"]
        for field in required_fields:
            if field not in data:
                self.logger.error(f"Champ requis manquant dans iaGOD.json: '{field}'")
                return False
        return True

    def _parse_laws(self, data: Dict[str, Any]):
        """Extrait et transforme les lois en objets `ConstitutionalLaw`."""
        self._laws.clear()
        for section in data.get("constitution", []):
            section_id = section.get("section_id", -1)
            for law_data in section.get("laws", []):
                law = ConstitutionalLaw(
                    id=law_data.get("id", "UNKNOWN_ID"),
                    name=law_data.get("name", "Unnamed Law"),
                    version=law_data.get("version", "1.0.0"),
                    description=law_data.get("description", ""),
                    section_id=section_id,
                    specifications=law_data.get("specifications", []),
                )
                if law.id != "UNKNOWN_ID":
                    self._laws[law.id] = law