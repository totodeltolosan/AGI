# eve_src/simulation.py
"""
Système de simulation d'évolution révolutionnaire avec intelligence émergente,
écosystèmes adaptatifs et méta-évolution multi-niveaux.
"""
import random
import copy
import numpy as np
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
import json
import time

from eve_src.config import CONFIG
from eve_src.core.environnement import Environnement
from eve_src.core.genetique import Genome, crossover
from eve_src.archetypes.archetype_animal import Animal
from eve_src.archetypes.archetype_vegetal import Vegetal
from eve_src.archetypes.archetype_insecte import Insecte
from eve_src.evolution import MondeEvoManager


class EventType(Enum):
    """Types d'événements évolutifs majeurs"""

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
    """Métriques avancées de l'écosystème"""

    diversite_genetique: float = 0.0
    stabilite_population: float = 0.0
    efficacite_energetique: float = 0.0
    complexite_moyenne: float = 0.0
    cooperation_niveau: float = 0.0
    innovation_rate: float = 0.0
    adaptation_speed: float = 0.0
    resilience_score: float = 0.0
    emergent_behaviors: Set[str] = field(default_factory=set)


@dataclass
class EvolutionaryEvent:
    """Événement évolutif avec contexte enrichi"""

    type: EventType
    timestamp: int
    description: str
    impact_global: float
    organismes_affectes: List[str]
    consequences: Dict[str, Any]
    probability_recurrence: float


class IntelligenceEmergente:
    """Système d'intelligence collective émergente"""

    def __init__(self):
        self.collective_memory = defaultdict(list)
        self.behavior_patterns = {}
        self.learning_networks = {}
        self.consciousness_level = 0.0
        self.cultural_evolution = {}

    def analyze_collective_behavior(self, population):
        """Analyse les comportements collectifs émergents"""
        behaviors = defaultdict(int)
        spatial_patterns = defaultdict(list)

        # Détection de motifs comportementaux
        for unit in population:
            if isinstance(unit, Animal):
                behavior_key = self._get_behavior_signature(unit)
                behaviors[behavior_key] += 1
                spatial_patterns[behavior_key].append((unit.x, unit.y))

        # Identification de l'intelligence émergente
        return self._identify_emergent_intelligence(behaviors, spatial_patterns)

    def _get_behavior_signature(self, animal):
        """Génère une signature comportementale"""
        # Analyse des patterns de mouvement, alimentation, reproduction
        return f"{animal.etat}_{animal.genome.data.get('intelligence', {}).get('niveau', 0)}"

    def _identify_emergent_intelligence(self, behaviors, patterns):
        """Identifie l'émergence de l'intelligence collective"""
        complexity_score = len(behaviors) * len(patterns)
        coordination_level = self._measure_coordination(patterns)

        if complexity_score > 100 and coordination_level > 0.7:
            self.consciousness_level += 0.1
            return True
        return False

    def _measure_coordination(self, patterns):
        """Mesure le niveau de coordination entre individus"""
        if not patterns:
            return 0.0

        # Algorithme de mesure de coordination spatiale
        coordination_scores = []
        for pattern_positions in patterns.values():
            if len(pattern_positions) > 1:
                # Calcul de la cohésion spatiale
                avg_distance = np.mean(
                    [
                        abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
                        for i, p1 in enumerate(pattern_positions)
                        for j, p2 in enumerate(pattern_positions[i + 1 :])
                    ]
                )
                coordination_scores.append(1.0 / (1.0 + avg_distance))

        return np.mean(coordination_scores) if coordination_scores else 0.0


class AdaptiveEcosystem:
    """Écosystème adaptatif auto-régulateur"""

    def __init__(self, environnement):
        self.env = environnement
        self.carrying_capacity = {}
        self.resource_flow = defaultdict(float)
        self.niche_dynamics = {}
        self.symbiotic_relationships = []
        self.ecosystem_memory = deque(maxlen=1000)

    def update_ecosystem_dynamics(self, population):
        """Met à jour la dynamique écosystémique"""
        # Calcul de la capacité de charge adaptative
        self._update_carrying_capacity(population)

        # Gestion des flux de ressources
        self._manage_resource_flows(population)

        # Évolution des niches écologiques
        self._evolve_ecological_niches(population)

        # Formation de relations symbiotiques
        self._develop_symbioses(population)

        # Mémorisation de l'état écosystémique
        self._store_ecosystem_state(population)

    def _update_carrying_capacity(self, population):
        """Calcul dynamique de la capacité de charge"""
        for species in ["Animal", "Vegetal", "Insecte"]:
            species_pop = [u for u in population if type(u).__name__ == species]

            # Facteurs environnementaux
            seasonal_factor = 1.0 + 0.2 * np.sin(self.env.age_monde / 100.0)
            resource_factor = min(1.0, self.env.ressources_globales / 1000.0)

            # Capacité adaptative basée sur l'historique
            historical_factor = self._calculate_historical_factor(species)

            self.carrying_capacity[species] = int(
                CONFIG["organisme"][f"population_initiale_{species.lower()}"]
                * seasonal_factor
                * resource_factor
                * historical_factor
            )

    def _calculate_historical_factor(self, species):
        """Calcule un facteur basé sur l'historique de l'espèce"""
        if len(self.ecosystem_memory) < 10:
            return 1.0

        recent_states = list(self.ecosystem_memory)[-10:]
        success_rate = sum(
            1 for state in recent_states if state.get(f"pop_{species.lower()}", 0) > 0
        ) / len(recent_states)

        return 0.5 + success_rate

    def _manage_resource_flows(self, population):
        """Gestion avancée des flux de ressources"""
        # Modélisation des chaînes trophiques complexes
        energy_flow = defaultdict(float)

        for unit in population:
            unit_type = type(unit).__name__
            if hasattr(unit, "energie"):
                energy_flow[unit_type] += unit.energie

        # Régulation automatique des ressources
        total_energy = sum(energy_flow.values())
        if total_energy > 0:
            for resource_type in ["nutrition", "eau", "abri"]:
                flow_rate = energy_flow.get("Animal", 0) / total_energy
                self.resource_flow[resource_type] = flow_rate

    def _evolve_ecological_niches(self, population):
        """Évolution dynamique des niches écologiques"""
        niche_occupancy = defaultdict(list)

        for unit in population:
            if isinstance(unit, Animal):
                # Définition de niche basée sur traits comportementaux
                niche = self._define_ecological_niche(unit)
                niche_occupancy[niche].append(unit)

        # Pression de sélection basée sur la compétition de niche
        for niche, occupants in niche_occupancy.items():
            if len(occupants) > self.carrying_capacity.get(niche, 10):
                # Compétition intra-niche -> pression évolutive
                self._apply_niche_pressure(occupants)

    def _define_ecological_niche(self, animal):
        """Définit la niche écologique d'un animal"""
        traits = animal.genome.data

        # Niche basée sur alimentation, habitat et comportement
        diet = traits.get("alimentation", {}).get("type", "omnivore")
        social = traits.get("social", {}).get("gregaire", False)
        intelligence = traits.get("intelligence", {}).get("niveau", 0)

        return f"{diet}_{social}_{intelligence//10}"

    def _apply_niche_pressure(self, occupants):
        """Applique une pression évolutive sur les occupants de niche"""
        # Les moins adaptés perdent de l'énergie
        fitness_scores = [self._calculate_fitness(unit) for unit in occupants]
        mean_fitness = np.mean(fitness_scores)

        for unit, fitness in zip(occupants, fitness_scores):
            if fitness < mean_fitness:
                unit.energie *= 0.95  # Pénalité énergétique

    def _calculate_fitness(self, unit):
        """Calcule la fitness d'une unité dans son environnement"""
        base_fitness = unit.energie / 100.0

        # Facteurs environnementaux
        seasonal_bonus = 1.0 if self.env.saison in ["printemps", "ete"] else 0.8

        # Facteurs sociaux
        social_bonus = 1.0
        if hasattr(unit.genome, "data") and unit.genome.data.get("social", {}).get(
            "gregaire"
        ):
            # Bonus si d'autres unités similaires sont proches
            social_bonus = 1.2

        return base_fitness * seasonal_bonus * social_bonus

    def _develop_symbioses(self, population):
        """Développement de relations symbiotiques"""
        potential_partnerships = []

        # Recherche de partenaires symbiotiques potentiels
        for i, unit1 in enumerate(population):
            for unit2 in population[i + 1 :]:
                if self._can_form_symbiosis(unit1, unit2):
                    symbiosis_strength = self._calculate_symbiosis_potential(
                        unit1, unit2
                    )
                    if symbiosis_strength > 0.7:
                        potential_partnerships.append(
                            (unit1, unit2, symbiosis_strength)
                        )

        # Formation des meilleures symbioses
        potential_partnerships.sort(key=lambda x: x[2], reverse=True)
        for unit1, unit2, strength in potential_partnerships[:5]:  # Top 5 symbioses
            self._establish_symbiosis(unit1, unit2, strength)

    def _can_form_symbiosis(self, unit1, unit2):
        """Vérifie si deux unités peuvent former une symbiose"""
        # Différents types d'organismes
        if type(unit1) == type(unit2):
            return False

        # Proximité spatiale
        distance = abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)
        return distance <= 3

    def _calculate_symbiosis_potential(self, unit1, unit2):
        """Calcule le potentiel symbiotique entre deux unités"""
        # Complémentarité des traits
        complementarity = 0.0

        if isinstance(unit1, Animal) and isinstance(unit2, Vegetal):
            # Symbiose animal-plante (pollinisation, protection)
            complementarity = 0.8
        elif isinstance(unit1, Insecte) and isinstance(unit2, Vegetal):
            # Symbiose insecte-plante
            complementarity = 0.9
        elif isinstance(unit1, Animal) and isinstance(unit2, Insecte):
            # Symbiose animal-insecte (nettoyage, transport)
            complementarity = 0.6

        # Facteur de stress environnemental (favorise la coopération)
        stress_factor = 1.0 - (unit1.energie + unit2.energie) / 200.0

        return min(1.0, complementarity + stress_factor * 0.3)

    def _establish_symbiosis(self, unit1, unit2, strength):
        """Établit une relation symbiotique"""
        symbiosis = {
            "partners": (id(unit1), id(unit2)),
            "strength": strength,
            "type": f"{type(unit1).__name__}_{type(unit2).__name__}",
            "benefits": self._define_symbiotic_benefits(unit1, unit2),
            "established_at": time.time(),
        }

        self.symbiotic_relationships.append(symbiosis)

    def _define_symbiotic_benefits(self, unit1, unit2):
        """Définit les bénéfices de la symbiose"""
        return {
            "unit1_benefits": ["energie_bonus", "protection"],
            "unit2_benefits": ["nutrients", "reproduction_boost"],
            "mutual_benefits": ["stress_reduction", "survival_boost"],
        }

    def _store_ecosystem_state(self, population):
        """Stocke l'état actuel de l'écosystème"""
        state = {
            "timestamp": time.time(),
            "pop_total": len(population),
            "pop_animal": len([u for u in population if isinstance(u, Animal)]),
            "pop_vegetal": len([u for u in population if isinstance(u, Vegetal)]),
            "pop_insecte": len([u for u in population if isinstance(u, Insecte)]),
            "resource_levels": dict(self.resource_flow),
            "symbioses": len(self.symbiotic_relationships),
            "niches": len(self.niche_dynamics),
        }

        self.ecosystem_memory.append(state)


class MetaEvolutionEngine:
    """Moteur de méta-évolution multi-niveaux"""

    def __init__(self):
        self.evolution_history = []
        self.adaptation_strategies = {}
        self.evolutionary_pressure = {}
        self.breakthrough_threshold = 0.8
        self.innovation_pool = []

    def analyze_evolutionary_trends(self, stats_history):
        """Analyse les tendances évolutives à long terme"""
        if len(stats_history) < 100:
            return None

        recent_trends = self._calculate_trends(stats_history[-100:])
        long_term_trends = self._calculate_trends(stats_history)

        # Détection de changements révolutionnaires
        breakthrough_indicators = self._detect_breakthroughs(
            recent_trends, long_term_trends
        )

        if breakthrough_indicators["score"] > self.breakthrough_threshold:
            return self._generate_evolutionary_event(breakthrough_indicators)

        return None

    def _calculate_trends(self, data):
        """Calcule les tendances dans les données"""
        trends = {}

        # Analyse de la complexité
        complexity_values = [d.get("complexite_max", 0) for d in data]
        trends["complexity_trend"] = np.polyfit(
            range(len(complexity_values)), complexity_values, 1
        )[0]

        # Analyse de la diversité
        pop_ratios = [
            d.get("pop_animal", 0) / max(d.get("pop_total", 1), 1) for d in data
        ]
        trends["diversity_trend"] = np.std(pop_ratios)

        # Analyse de l'innovation
        innovation_indicators = []
        for i in range(1, len(data)):
            prev_tribes = len(data[i - 1].get("tribus", set()))
            curr_tribes = len(data[i].get("tribus", set()))
            innovation_indicators.append(max(0, curr_tribes - prev_tribes))

        trends["innovation_rate"] = (
            np.mean(innovation_indicators) if innovation_indicators else 0
        )

        return trends

    def _detect_breakthroughs(self, recent, long_term):
        """Détecte les percées évolutives"""
        indicators = {
            "complexity_acceleration": recent.get("complexity_trend", 0)
            / max(long_term.get("complexity_trend", 0.001), 0.001),
            "diversity_explosion": recent.get("diversity_trend", 0)
            / max(long_term.get("diversity_trend", 0.001), 0.001),
            "innovation_surge": recent.get("innovation_rate", 0)
            / max(long_term.get("innovation_rate", 0.001), 0.001),
        }

        # Score composite
        score = (
            np.mean(
                [
                    min(indicators["complexity_acceleration"], 3.0),
                    min(indicators["diversity_explosion"], 2.0),
                    min(indicators["innovation_surge"], 4.0),
                ]
            )
            / 3.0
        )

        indicators["score"] = score
        return indicators

    def _generate_evolutionary_event(self, indicators):
        """Génère un événement évolutif basé sur les indicateurs"""
        if indicators["complexity_acceleration"] > 2.0:
            return EvolutionaryEvent(
                type=EventType.EMERGENCE_INTELLIGENCE,
                timestamp=int(time.time()),
                description="Émergence d'une intelligence collective supérieure",
                impact_global=0.9,
                organismes_affectes=["Animal"],
                consequences={
                    "intelligence_boost": 2.0,
                    "cooperation_increase": 1.5,
                    "technology_unlock": True,
                },
                probability_recurrence=0.1,
            )

        elif indicators["innovation_surge"] > 3.0:
            return EvolutionaryEvent(
                type=EventType.FORMATION_CIVILISATION,
                timestamp=int(time.time()),
                description="Formation des premières proto-civilisations",
                impact_global=0.8,
                organismes_affectes=["Animal"],
                consequences={
                    "social_structures": True,
                    "tool_use": True,
                    "culture_emergence": True,
                },
                probability_recurrence=0.2,
            )

        elif indicators["diversity_explosion"] > 1.8:
            return EvolutionaryEvent(
                type=EventType.RENAISSANCE_EVOLUTIVE,
                timestamp=int(time.time()),
                description="Renaissance évolutive - explosion de la biodiversité",
                impact_global=0.7,
                organismes_affectes=["Animal", "Vegetal", "Insecte"],
                consequences={
                    "mutation_rate_increase": 2.0,
                    "new_species_probability": 0.3,
                    "niche_diversification": True,
                },
                probability_recurrence=0.3,
            )

        return None


class AdvancedSimulation:
    """Simulation d'évolution révolutionnaire avec IA émergente"""

    def __init__(self):
        self.monde = Environnement(CONFIG["environnement"]["taille"])
        self.population = []
        self.age_simulation = 0
        self.evo_manager = MondeEvoManager()

        # === NOUVEAUX SYSTÈMES RÉVOLUTIONNAIRES ===
        self.intelligence_emergente = IntelligenceEmergente()
        self.adaptive_ecosystem = AdaptiveEcosystem(self.monde)
        self.meta_evolution = MetaEvolutionEngine()

        # Historique et métriques avancées
        self.stats_history = deque(maxlen=10000)
        self.evolutionary_events = []
        self.ecosystem_metrics = EcosystemMetrics()

        # Systèmes de crise et récupération
        self.crisis_detector = self._init_crisis_detector()
        self.recovery_mechanisms = self._init_recovery_systems()

        self.init_population()

    def _init_crisis_detector(self):
        """Initialise le système de détection de crises"""
        return {
            "extinction_threshold": 0.1,  # 10% de la population initiale
            "stability_window": 50,  # Fenêtre d'analyse de stabilité
            "crisis_indicators": [],
            "active_crises": [],
        }

    def _init_recovery_systems(self):
        """Initialise les mécanismes de récupération"""
        return {
            "genetic_reservoir": [],  # Banque génétique d'urgence
            "recolonization_seeds": [],  # Graines de recolonisation
            "adaptive_mutations": {},  # Mutations adaptatives d'urgence
            "sanctuary_zones": [],  # Zones sanctuaires
        }

    def init_population(self):
        """Crée une population initiale diversifiée avec potentiel évolutif"""
        # Population de base
        for _ in range(CONFIG["organisme"]["population_initiale_vegetal"]):
            x, y = random.randint(0, self.monde.taille - 1), random.randint(
                0, self.monde.taille - 1
            )
            vegetal = Vegetal(x, y)
            # Diversification génétique initiale
            if hasattr(vegetal, "genome"):
                self._add_evolutionary_potential(vegetal.genome)
            self.population.append(vegetal)

        for _ in range(CONFIG["organisme"]["population_initiale_insecte"]):
            x, y = random.randint(0, self.monde.taille - 1), random.randint(
                0, self.monde.taille - 1
            )
            insecte = Insecte(x, y)
            if hasattr(insecte, "genome"):
                self._add_evolutionary_potential(insecte.genome)
            self.population.append(insecte)

        # Constitution de la réserve génétique
        self._build_genetic_reservoir()

    def _add_evolutionary_potential(self, genome):
        """Ajoute un potentiel évolutif aux génomes"""
        if hasattr(genome, "data"):
            # Gènes dormants pour l'évolution future
            genome.data["potential"] = {
                "intelligence_seeds": random.uniform(0.1, 0.3),
                "cooperation_genes": random.uniform(0.0, 0.5),
                "adaptation_flexibility": random.uniform(0.2, 0.8),
                "innovation_capacity": random.uniform(0.0, 0.4),
            }

    def _build_genetic_reservoir(self):
        """Constitue une réserve génétique diversifiée"""
        for unit in self.population[:50]:  # Échantillon des 50 premiers
            if hasattr(unit, "genome"):
                genetic_copy = copy.deepcopy(unit.genome)
                self.recovery_mechanisms["genetic_reservoir"].append(
                    {
                        "genome": genetic_copy,
                        "species": type(unit).__name__,
                        "fitness_score": random.uniform(0.5, 1.0),
                        "preserved_at": self.age_simulation,
                    }
                )

    def update(self):
        """Cycle de simulation révolutionnaire"""
        self.age_simulation += 1
        if not self.population:
            self._emergency_recovery()
            return

        # === PHASE 1: Mise à jour environnementale ===
        self.monde.update_cycle()
        self.adaptive_ecosystem.update_ecosystem_dynamics(self.population)

        # === PHASE 2: Simulation des organismes ===
        nouveaux_nes, morts = self._simulate_organisms()

        # === PHASE 3: Analyse de l'intelligence émergente ===
        if self.intelligence_emergente.analyze_collective_behavior(self.population):
            self._handle_intelligence_emergence()

        # === PHASE 4: Gestion des événements évolutifs ===
        stats = self.get_advanced_stats()
        self.stats_history.append(stats)

        # Détection de crises et activation des systèmes de récupération
        if self._detect_ecosystem_crisis(stats):
            self._activate_crisis_response()

        # Méta-évolution : analyse des tendances à long terme
        if len(self.stats_history) > 100 and self.age_simulation % 50 == 0:
            evolutionary_event = self.meta_evolution.analyze_evolutionary_trends(
                list(self.stats_history)
            )
            if evolutionary_event:
                self._handle_meta_evolutionary_event(evolutionary_event)

        # === PHASE 5: Finalisation du cycle ===
        self._finalize_cycle(nouveaux_nes, morts)

        # Système d'apprentissage de l'écosystème
        self._ecosystem_learning()

    def _simulate_organisms(self):
        """Simulation avancée des organismes avec interactions complexes"""
        nouveaux_nes, morts = [], []
        pop_dict = {(unite.x, unite.y): unite for unite in self.population}

        # Reproduction sexuée améliorée
        if CONFIG["genetique"]["mode_reproduction"] == "sexuee":
            nouveaux_nes.extend(self._advanced_sexual_reproduction())

        # Simulation de chaque organisme
        for unite in self.population:
            # Application des effets symbiotiques
            self._apply_symbiotic_effects(unite)

            # Vie de l'organisme
            resultat_vie = unite.vivre(self.monde, pop_dict)
            if resultat_vie:
                nouveau_ne = self._process_birth(unite, resultat_vie)
                if nouveau_ne:
                    nouveaux_nes.append(nouveau_ne)

            # Gestion de la reproduction
            if (
                isinstance(unite, Animal)
                and unite.energie >= CONFIG["evolution"]["seuil_reproduction"]
            ):
                unite.lancer_reproduction()

            # Gestion de la mort
            if unite.est_mort:
                morts.append(unite)

        return nouveaux_nes, morts

    def _advanced_sexual_reproduction(self):
        """Reproduction sexuée avec sélection sophistiquée"""
        nouveaux_nes = []

        # Groupement par compatibilité génétique et proximité
        partenaires_potentiels = [
            u
            for u in self.population
            if isinstance(u, Animal) and u.etat == "cherche_partenaire"
        ]

        # Algorithme de matching optimal
        couples = self._optimal_mate_matching(partenaires_potentiels)

        for p1, p2 in couples:
            # Reproduction avec innovations génétiques
            enfant_genome = self._advanced_crossover(p1.genome, p2.genome)

            # Placement stratégique du nouveau-né
            x, y = self._find_optimal_birth_location(p1, p2)

            nouveau_ne = Animal(x, y, genome=enfant_genome)

            # Héritage culturel et comportemental
            self._transfer_cultural_knowledge(nouveau_ne, [p1, p2])

            nouveaux_nes.append(nouveau_ne)

            # Coût énergétique ajusté
            cost = CONFIG["evolution"]["seuil_reproduction"] / 2
            p1.energie -= cost
            p2.energie -= cost
            p1.etat = p2.etat = "normal"

        return nouveaux_nes

    def _optimal_mate_matching(self, candidates):
        """Algorithme de matching optimal pour la reproduction"""
        couples = []
        used = set()

        # Tri par compatibilité génétique
        compatibility_matrix = []
        for i, c1 in enumerate(candidates):
            for j, c2 in enumerate(candidates[i + 1 :], i + 1):
                if abs(c1.x - c2.x) + abs(c1.y - c2.y) < 5:  # Proximité
                    compatibility = self._calculate_genetic_compatibility(c1, c2)
                    compatibility_matrix.append((i, j, compatibility))

        # Sélection des meilleures compatibilités
        compatibility_matrix.sort(key=lambda x: x[2], reverse=True)

        for i, j, compat in compatibility_matrix:
            if i not in used and j not in used and compat > 0.3:
                couples.append((candidates[i], candidates[j]))
                used.add(i)
                used.add(j)

        return couples

    def _calculate_genetic_compatibility(self, animal1, animal2):
        """Calcule la compatibilité génétique entre deux animaux"""
        if not (hasattr(animal1, "genome") and hasattr(animal2, "genome")):
            return 0.5

        genome1, genome2 = animal1.genome.data, animal2.genome.data

        # Facteurs de compatibilité
        compatibility_score = 0.0

        # Similarité comportementale
        if genome1.get("social", {}) == genome2.get("social", {}):
            compatibility_score += 0.3

        # Complémentarité alimentaire
        diet1 = genome1.get("alimentation", {}).get("type", "omnivore")
        diet2 = genome2.get("alimentation", {}).get("type", "omnivore")
        if diet1 == diet2:
            compatibility_score += 0.2

        # Diversité génétique (favorise la diversité)
        genetic_distance = self._calculate_genetic_distance(genome1, genome2)
        compatibility_score += min(0.5, genetic_distance)
