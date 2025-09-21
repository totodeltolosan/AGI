# eve_src/core/structures.py
"""
Définit les structures de données avancées (dataclasses, Enums) utilisées
par le moteur de simulation et d'évolution.
Ce fichier sert de "vocabulaire" commun pour les concepts complexes.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Set
from enum import Enum


class EventType(Enum):
    """Énumération des types d'événements évolutifs majeurs pouvant survenir."""

    EMERGENCE_INTELLIGENCE = "emergence_intelligence"
    FORMATION_CIVILISATION = "formation_civilisation"
    CATASTROPHE_NATURELLE = "catastrophe_naturelle"
    MUTATION_MAJEURE = "mutation_majeure"
    SYMBIOSE_INTER_ESPECES = "symbiose_inter_especes"
    EVOLUTION_TECHNOLOGIQUE = "evolution_technologique"
    CHANGEMENT_CLIMATIQUE = "changement_climatique"
    EXTINCTION_MASSE = "extinction_masse"
    RENAISSANCE_EVOLUTIVE = "renaissance_evolutive"


@dataclass
class EcosystemMetrics:
    """Structure pour contenir les métriques avancées de l'écosystème."""

    diversite_genetique: float = 0.0
    stabilite_population: float = 0.0
    efficacite_energetique: float = 0.0
    complexite_moyenne_cerveau: float = 0.0
    niveau_cooperation: float = 0.0
    taux_innovation: float = 0.0
    vitesse_adaptation: float = 0.0
    score_resilience: float = 0.0
    comportements_emergents: Set[str] = field(default_factory=set)


@dataclass
class EvolutionaryEvent:
    """Représente un événement évolutif majeur avec son contexte enrichi."""

    type: EventType
    age_simulation: int
    description: str
    impact_estime: float
    organismes_affectes: List[str]
    consequences: Dict[str, Any]
