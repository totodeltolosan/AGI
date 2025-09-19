#!/usr/bin/env python3
"""
Constitution Loader - Chargeur iaGOD.json Conforme COMP-CPL-001
================================================================

CHEMIN: compliance/constitution_loader.py

Rôle Fondamental (Conforme iaGOD.json COMP-CPL-001) :
- Charger et valider la constitution iaGOD.json en mémoire
- Transformer en ensemble de politiques exécutables
- Fournir interface d'accès aux lois constitutionnelles
- Respecter directive < 200 lignes
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ConstitutionalLaw:
    """Représentation d'une loi constitutionnelle"""
    id: str
    name: str
    version: str
    description: str
    section_id: int
    specifications: List[Dict[str, Any]]
    
class ConstitutionLoader:
    """
    Chargeur de Constitution iaGOD.json - Conforme COMP-CPL-001
    
    Implémente le chargement dynamique de la constitution selon
    la directive constitutionnelle COMP-CPL-001 de iaGOD.json
    """
    
    def __init__(self, constitution_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.constitution_path = constitution_path or Path("iaGOD.json")
        self.constitution_data: Optional[Dict] = None
        self.laws: Dict[str, ConstitutionalLaw] = {}
        
    def load_constitution(self) -> bool:
        """
        Charge iaGOD.json et valide sa conformité
        
        Returns:
            bool: True si chargé avec succès, False sinon
        """
        try:
            if not self.constitution_path.exists():
                self.logger.error(f"Constitution iaGOD.json introuvable: {self.constitution_path}")
                return False
                
            with open(self.constitution_path, 'r', encoding='utf-8') as f:
                self.constitution_data = json.load(f)
                
            if not self._validate_constitution_schema():
                return False
                
            self._parse_constitutional_laws()
            self.logger.info(f"Constitution chargée: {len(self.laws)} lois constitutionnelles")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur parsing JSON iaGOD.json: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur fatale chargement constitution: {e}")
            return False
    
    def _validate_constitution_schema(self) -> bool:
        """Valide le schéma de base de iaGOD.json"""
        required_fields = ["iaGOD_SpecVersion", "constitution"]
        
        for field in required_fields:
            if field not in self.constitution_data:
                self.logger.error(f"Champ requis manquant dans iaGOD.json: {field}")
                return False
                
        return True
    
    def _parse_constitutional_laws(self):
        """Parse et structure les lois constitutionnelles"""
        constitution_sections = self.constitution_data.get("constitution", [])
        
        for section in constitution_sections:
            section_id = section.get("section_id")
            laws = section.get("laws", [])
            
            for law_data in laws:
                law = ConstitutionalLaw(
                    id=law_data.get("id", ""),
                    name=law_data.get("name", ""),
                    version=law_data.get("version", "1.0.0"),
                    description=law_data.get("description", ""),
                    section_id=section_id,
                    specifications=law_data.get("specifications", [])
                )
                
                self.laws[law.id] = law
    
    def get_law(self, law_id: str) -> Optional[ConstitutionalLaw]:
        """Récupère une loi spécifique par son ID"""
        return self.laws.get(law_id)
    
    def get_laws_by_domain(self, domain: str) -> List[ConstitutionalLaw]:
        """Récupère toutes les lois d'un domaine (ex: COMP-, META-)"""
        return [law for law in self.laws.values() if law.id.startswith(domain)]
    
    def get_all_laws(self) -> Dict[str, ConstitutionalLaw]:
        """Récupère toutes les lois constitutionnelles"""
        return self.laws.copy()
    
    def is_loaded(self) -> bool:
        """Vérifie si la constitution est chargée"""
        return self.constitution_data is not None and len(self.laws) > 0
