# eve_src/core/genetique.py
"""
Système génétique révolutionnaire avec épigénétique, mutations dirigées,
évolution en réseau et émergence de traits complexes.
Moteur ultra-avancé de l'évolution et de la spéciation dans EVE.
"""
import random
import copy
import numpy as np
import hashlib
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
import json
import time

from eve_src.config import CONFIG


class MutationType(Enum):
    """Types de mutations possibles"""

    POINT = "point_mutation"
    INSERTION = "insertion"
    DELETION = "deletion"
    DUPLICATION = "duplication"
    INVERSION = "inversion"
    TRANSLOCATION = "translocation"
    EPIGENETIC = "epigenetic_modification"
    HORIZONTAL_TRANSFER = "horizontal_gene_transfer"
    POLYPLOIDY = "chromosome_duplication"


class GeneExpression(Enum):
    """Niveaux d'expression génétique"""

    SILENCED = 0.0
    LOW = 0.25
    MODERATE = 0.5
    HIGH = 0.75
    OVEREXPRESSED = 1.0


@dataclass
class Gene:
    """Représentation d'un gène individuel avec métadonnées"""

    name: str
    sequence: List[float]
    expression_level: float = 1.0
    methylation_pattern: List[bool] = field(default_factory=list)
    evolutionary_age: int = 0
    regulatory_sites: Dict[str, float] = field(default_factory=dict)
    dominant: bool = True
    fitness_contribution: float = 0.0
    interaction_partners: Set[str] = field(default_factory=set)

    def __post_init__(self):
        if not self.methylation_pattern:
            self.methylation_pattern = [
                random.choice([True, False]) for _ in range(len(self.sequence))
            ]


@dataclass
class Chromosome:
    """Chromosome contenant plusieurs gènes avec structure complexe"""

    genes: Dict[str, Gene] = field(default_factory=dict)
    centromere_position: float = 0.5
    telomere_length: float = 1.0
    chromatin_state: str = "euchromatin"  # ou "heterochromatin"
    structural_variants: List[Dict] = field(default_factory=list)

    def add_gene(self, gene: Gene):
        """Ajoute un gène au chromosome"""
        self.genes[gene.name] = gene

    def get_active_genes(self) -> Dict[str, Gene]:
        """Retourne les gènes activement exprimés"""
        return {
            name: gene
            for name, gene in self.genes.items()
            if gene.expression_level > 0.1
        }


class EpigeneticController:
    """Contrôleur épigénétique pour la régulation de l'expression génique"""

    def __init__(self):
        self.methylation_enzymes = {"DNMT1": 1.0, "DNMT3A": 0.8, "DNMT3B": 0.7}
        self.histone_modifications = defaultdict(float)
        self.chromatin_remodeling = {}
        self.environmental_memory = deque(maxlen=100)

    def apply_environmental_regulation(self, genome, environmental_stress: float):
        """Applique une régulation épigénétique basée sur l'environnement"""
        stress_threshold = 0.7

        if environmental_stress > stress_threshold:
            # Activation des gènes de stress
            self._activate_stress_response_genes(genome)
            # Mémorisation épigénétique
            self.environmental_memory.append(
                {
                    "stress_level": environmental_stress,
                    "timestamp": time.time(),
                    "response": "stress_activation",
                }
            )

        # Hérédité épigénétique
        self._apply_transgenerational_effects(genome)

    def _activate_stress_response_genes(self, genome):
        """Active les gènes de réponse au stress"""
        stress_genes = ["robustesse_defense", "immunite", "resistance_poison"]

        for chrom in genome.chromosomes.values():
            for gene_name, gene in chrom.genes.items():
                if any(stress_gene in gene_name for stress_gene in stress_genes):
                    # Déméthylation pour activer le gène
                    gene.methylation_pattern = [False] * len(gene.methylation_pattern)
                    gene.expression_level = min(1.0, gene.expression_level * 1.5)

    def _apply_transgenerational_effects(self, genome):
        """Applique les effets transgénérationnels"""
        if len(self.environmental_memory) > 10:
            # Stress chronique -> modifications héritables
            chronic_stress = np.mean(
                [mem["stress_level"] for mem in self.environmental_memory]
            )

            if chronic_stress > 0.6:
                # Modifications épigénétiques héritables
                for chrom in genome.chromosomes.values():
                    for gene in chrom.genes.values():
                        if "adaptation" in gene.name:
                            gene.expression_level *= 1.2


class EvolutionaryConstraints:
    """Système de contraintes évolutives et canalisations"""

    def __init__(self):
        self.developmental_constraints = {}
        self.phylogenetic_constraints = {}
        self.functional_constraints = {}
        self.trade_off_matrix = np.zeros((10, 10))  # Matrice des compromis évolutifs

    def evaluate_mutation_feasibility(self, genome, proposed_mutation):
        """Évalue la faisabilité d'une mutation proposée"""
        feasibility_score = 1.0

        # Contraintes développementales
        feasibility_score *= self._check_developmental_constraints(proposed_mutation)

        # Contraintes phylogénétiques
        feasibility_score *= self._check_phylogenetic_constraints(
            genome, proposed_mutation
        )

        # Contraintes fonctionnelles
        feasibility_score *= self._check_functional_constraints(proposed_mutation)

        return feasibility_score

    def _check_developmental_constraints(self, mutation):
        """Vérifie les contraintes développementales"""
        # Certaines mutations sont incompatibles avec le développement
        if mutation["type"] == MutationType.DELETION:
            if "essential" in mutation.get("target_gene", ""):
                return 0.1  # Très faible probabilité
        return 1.0

    def _check_phylogenetic_constraints(self, genome, mutation):
        """Vérifie les contraintes phylogénétiques"""
        # Certaines mutations sont plus probables selon l'histoire évolutive
        phylo_bias = 1.0

        if hasattr(genome, "evolutionary_history"):
            recent_changes = genome.evolutionary_history[-10:]
            similar_mutations = sum(
                1 for change in recent_changes if change["type"] == mutation["type"]
            )

            if similar_mutations > 3:
                phylo_bias = 0.5  # Réduction si trop de mutations similaires récentes

        return phylo_bias

    def _check_functional_constraints(self, mutation):
        """Vérifie les contraintes fonctionnelles"""
        # Certaines fonctions ne peuvent pas être perdues
        critical_functions = ["metabolism", "reproduction", "survival"]

        if mutation.get("affects_function") in critical_functions:
            if mutation["type"] in [MutationType.DELETION, MutationType.SILENCED]:
                return 0.2

        return 1.0


class NetworkEvolution:
    """Système d'évolution en réseau des interactions génétiques"""

    def __init__(self):
        self.gene_networks = defaultdict(set)
        self.regulatory_networks = defaultdict(dict)
        self.protein_interactions = defaultdict(set)
        self.metabolic_pathways = {}

    def build_interaction_network(self, genome):
        """Construit le réseau d'interactions génétiques"""
        # Analyse des interactions entre gènes
        for chrom in genome.chromosomes.values():
            for gene_name, gene in chrom.genes.items():
                # Construction du réseau basé sur les partenaires d'interaction
                for partner in gene.interaction_partners:
                    self.gene_networks[gene_name].add(partner)
                    self.gene_networks[partner].add(gene_name)

                # Réseaux de régulation
                for regulator, strength in gene.regulatory_sites.items():
                    self.regulatory_networks[regulator][gene_name] = strength

    def evolve_network_properties(self, genome):
        """Fait évoluer les propriétés du réseau"""
        # Évolution de la connectivité
        self._evolve_connectivity(genome)

        # Évolution de la modularité
        self._evolve_modularity(genome)

        # Évolution de la robustesse
        self._evolve_robustness(genome)

    def _evolve_connectivity(self, genome):
        """Fait évoluer la connectivité du réseau"""
        for chrom in genome.chromosomes.values():
            for gene in chrom.genes.values():
                # Probabilité de former de nouvelles interactions
                if random.random() < 0.05:
                    available_partners = [
                        g
                        for g in chrom.genes.keys()
                        if g not in gene.interaction_partners
                    ]
                    if available_partners:
                        new_partner = random.choice(available_partners)
                        gene.interaction_partners.add(new_partner)

                # Probabilité de perdre des interactions
                if len(gene.interaction_partners) > 1 and random.random() < 0.02:
                    lost_partner = random.choice(list(gene.interaction_partners))
                    gene.interaction_partners.remove(lost_partner)

    def _evolve_modularity(self, genome):
        """Fait évoluer la structure modulaire"""
        # Détection et renforcement des modules fonctionnels
        modules = self._detect_functional_modules(genome)

        for module in modules:
            if len(module) > 2:  # Module significatif
                # Renforcement des interactions intra-module
                for gene1 in module:
                    for gene2 in module:
                        if gene1 != gene2 and random.random() < 0.1:
                            if gene1 in genome.get_all_genes():
                                genome.get_all_genes()[gene1].interaction_partners.add(
                                    gene2
                                )

    def _detect_functional_modules(self, genome):
        """Détecte les modules fonctionnels dans le réseau"""
        # Algorithme de détection de communautés simplifié
        modules = []
        visited = set()

        for gene_name in genome.get_all_gene_names():
            if gene_name not in visited:
                module = self._find_connected_component(gene_name, visited)
                if len(module) > 1:
                    modules.append(module)

        return modules

    def _find_connected_component(self, start_gene, visited):
        """Trouve la composante connectée d'un gène"""
        component = set()
        stack = [start_gene]

        while stack:
            gene = stack.pop()
            if gene not in visited:
                visited.add(gene)
                component.add(gene)

                # Ajouter les voisins
                if gene in self.gene_networks:
                    for neighbor in self.gene_networks[gene]:
                        if neighbor not in visited:
                            stack.append(neighbor)

        return component

    def _evolve_robustness(self, genome):
        """Fait évoluer la robustesse du réseau"""
        # Ajout de redondance fonctionnelle
        critical_genes = self._identify_critical_genes(genome)

        for critical_gene in critical_genes:
            if random.random() < 0.03:  # 3% de chance de duplication
                self._duplicate_gene_function(genome, critical_gene)

    def _identify_critical_genes(self, genome):
        """Identifie les gènes critiques pour la survie"""
        critical_genes = []

        for chrom in genome.chromosomes.values():
            for gene_name, gene in chrom.genes.items():
                # Gènes avec beaucoup d'interactions = critiques
                if len(gene.interaction_partners) > 5:
                    critical_genes.append(gene_name)

                # Gènes avec forte contribution à la fitness
                if gene.fitness_contribution > 0.7:
                    critical_genes.append(gene_name)

        return critical_genes

    def _duplicate_gene_function(self, genome, gene_name):
        """Duplique la fonction d'un gène critique"""
        # Trouve le gène original
        original_gene = None
        source_chrom = None

        for chrom_name, chrom in genome.chromosomes.items():
            if gene_name in chrom.genes:
                original_gene = chrom.genes[gene_name]
                source_chrom = chrom
                break

        if original_gene:
            # Crée une copie avec légères variations
            duplicate_gene = copy.deepcopy(original_gene)
            duplicate_gene.name = f"{gene_name}_duplicate"
            duplicate_gene.expression_level *= random.uniform(0.8, 1.2)

            # Ajoute au même chromosome ou à un autre
            target_chrom = random.choice(list(genome.chromosomes.values()))
            target_chrom.add_gene(duplicate_gene)


class AdvancedGenome:
    """Génome révolutionnaire avec architecture chromosomique complexe"""

    def __init__(self, parent_genome_data=None, parent_epigenome=None):
        """Initialise un génome avancé avec structure chromosomique"""
        self.chromosomes = {}
        self.evolutionary_history = []
        self.mutation_rate = CONFIG.get("genetique", {}).get("taux_mutation_base", 0.01)
        self.generation = 0
        self.lineage_id = self._generate_lineage_id()

        # Systèmes de contrôle avancés
        self.epigenetic_controller = EpigeneticController()
        self.evolution_constraints = EvolutionaryConstraints()
        self.network_evolution = NetworkEvolution()

        # Métriques de qualité génomique
        self.genome_stability = 1.0
        self.mutational_load = 0.0
        self.adaptive_potential = random.uniform(0.5, 1.0)

        if parent_genome_data:
            self._inherit_from_parent(parent_genome_data, parent_epigenome)
        else:
            self._create_founder_genome()

        # Construction du réseau d'interactions
        self.network_evolution.build_interaction_network(self)

    def _generate_lineage_id(self):
        """Génère un identifiant unique de lignée"""
        return hashlib.md5(f"{time.time()}_{random.random()}".encode()).hexdigest()[:8]

    def _inherit_from_parent(self, parent_data, parent_epigenome):
        """Hérite des caractéristiques parentales avec modifications"""
        self.generation = parent_data.get("generation", 0) + 1
        self.lineage_id = parent_data.get("lineage_id", self._generate_lineage_id())

        # Héritage chromosomique
        if "chromosomes" in parent_data:
            self.chromosomes = copy.deepcopy(parent_data["chromosomes"])
        else:
            self._convert_legacy_genome(parent_data)

        # Héritage épigénétique
        if parent_epigenome:
            self.epigenetic_controller = copy.deepcopy(parent_epigenome)

    def _convert_legacy_genome(self, legacy_data):
        """Convertit un ancien format de génome en format chromosomique"""
        # Création de chromosomes à partir de l'ancien format
        autosome1 = Chromosome()
        autosome2 = Chromosome()
        sex_chromosome = Chromosome()

        # Conversion des gènes physiques
        if "physique" in legacy_data:
            for trait_name, value in legacy_data["physique"].items():
                gene = Gene(
                    name=f"physique_{trait_name}",
                    sequence=[value],
                    evolutionary_age=0,
                    fitness_contribution=random.uniform(0.1, 0.5),
                )
                autosome1.add_gene(gene)

        # Conversion des gènes d'alimentation
        if "alimentation" in legacy_data:
            for trait_name, value in legacy_data["alimentation"].items():
                gene = Gene(
                    name=f"alimentation_{trait_name}",
                    sequence=(
                        [value]
                        if isinstance(value, (int, float))
                        else [hash(str(value)) % 100 / 100.0]
                    ),
                    evolutionary_age=0,
                    fitness_contribution=random.uniform(0.2, 0.8),
                )
                autosome2.add_gene(gene)

        # Conversion des gènes sociaux
        if "social" in legacy_data:
            for trait_name, value in legacy_data["social"].items():
                sequence = (
                    value
                    if isinstance(value, list)
                    else (
                        [value]
                        if isinstance(value, (int, float))
                        else [random.random()]
                    )
                )
                gene = Gene(
                    name=f"social_{trait_name}",
                    sequence=sequence,
                    evolutionary_age=0,
                    fitness_contribution=random.uniform(0.3, 0.7),
                )
                sex_chromosome.add_gene(gene)

        # Conversion du cerveau
        if "cerveau" in legacy_data and "poids" in legacy_data["cerveau"]:
            brain_weights = legacy_data["cerveau"]["poids"]
            flattened_weights = [w for row in brain_weights for w in row]

            brain_gene = Gene(
                name="cerveau_neural_network",
                sequence=flattened_weights,
                evolutionary_age=0,
                fitness_contribution=0.9,
                interaction_partners={"physique_vitesse", "social_communication"},
            )
            autosome1.add_gene(brain_gene)

        self.chromosomes = {
            "autosome_1": autosome1,
            "autosome_2": autosome2,
            "sex_chromosome": sex_chromosome,
        }

    def _create_founder_genome(self):
        """Crée un génome fondateur riche avec potentiel évolutif"""
        # Chromosome autosomique 1 - Traits physiques et métaboliques
        autosome1 = Chromosome()

        # Gènes physiques avancés
        physical_genes = {
            "taille": Gene(
                "physique_taille", [random.uniform(0.8, 1.2)], fitness_contribution=0.3
            ),
            "vitesse": Gene(
                "physique_vitesse", [random.uniform(0.8, 1.2)], fitness_contribution=0.4
            ),
            "robustesse": Gene(
                "physique_robustesse",
                [random.uniform(0.8, 1.2)],
                fitness_contribution=0.5,
            ),
            "endurance": Gene(
                "physique_endurance",
                [random.uniform(0.5, 1.5)],
                fitness_contribution=0.3,
                expression_level=GeneExpression.MODERATE.value,
            ),
            "metabolisme": Gene(
                "physique_metabolisme",
                [random.uniform(0.7, 1.3)],
                fitness_contribution=0.6,
            ),
        }

        for gene in physical_genes.values():
            autosome1.add_gene(gene)

        # Chromosome autosomique 2 - Traits comportementaux et cognitifs
        autosome2 = Chromosome()

        behavioral_genes = {
            "intelligence": Gene(
                "cerveau_intelligence",
                [random.uniform(0.0, 0.5)],
                expression_level=GeneExpression.LOW.value,
                fitness_contribution=0.8,
            ),
            "memoire": Gene(
                "cerveau_memoire", [random.uniform(0.2, 0.8)], fitness_contribution=0.6
            ),
            "apprentissage": Gene(
                "cerveau_apprentissage",
                [random.uniform(0.1, 0.6)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.7,
            ),
            "creativite": Gene(
                "cerveau_creativite",
                [random.uniform(0.0, 0.3)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.5,
            ),
            "neural_plasticity": Gene(
                "cerveau_plasticite",
                [random.uniform(0.3, 0.9)],
                fitness_contribution=0.7,
            ),
        }

        for gene in behavioral_genes.values():
            autosome2.add_gene(gene)

        # Chromosome sexuel - Traits sociaux et reproductifs
        sex_chromosome = Chromosome()

        social_genes = {
            "cooperation": Gene(
                "social_cooperation",
                [random.uniform(0.0, 0.4)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.4,
            ),
            "leadership": Gene(
                "social_leadership",
                [random.uniform(0.0, 0.2)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.3,
            ),
            "empathie": Gene(
                "social_empathie",
                [random.uniform(0.0, 0.3)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.4,
            ),
            "communication": Gene(
                "social_communication",
                [random.uniform(0.0, 0.1)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.9,
            ),
            "tribu_id": Gene(
                "social_tribu_id", [random.random(), 0.9, 1.0], fitness_contribution=0.2
            ),
        }

        for gene in social_genes.values():
            sex_chromosome.add_gene(gene)

        # Chromosome spécialisé - Adaptations environnementales
        adaptation_chromosome = Chromosome()

        adaptation_genes = {
            "resistance_froid": Gene(
                "adaptation_froid",
                [random.uniform(0.0, 0.2)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.3,
            ),
            "resistance_chaleur": Gene(
                "adaptation_chaleur",
                [random.uniform(0.0, 0.2)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.3,
            ),
            "vision_nocturne": Gene(
                "adaptation_vision_nuit",
                [random.uniform(0.0, 0.1)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.4,
            ),
            "toxin_resistance": Gene(
                "adaptation_toxines",
                [random.uniform(0.0, 0.1)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.5,
            ),
            "regeneration": Gene(
                "adaptation_regeneration",
                [random.uniform(0.0, 0.05)],
                expression_level=GeneExpression.SILENCED.value,
                fitness_contribution=0.6,
            ),
        }

        for gene in adaptation_genes.values():
            adaptation_chromosome.add_gene(gene)

        self.chromosomes = {
            "autosome_1": autosome1,
            "autosome_2": autosome2,
            "sex_chromosome": sex_chromosome,
            "adaptation_chromosome": adaptation_chromosome,
        }

    def advanced_mutation(self, environmental_pressure=0.0, mutagenic_factors=None):
        """Système de mutation ultra-avancé avec contraintes évolutives"""
        mutation_events = []

        # Ajustement du taux de mutation basé sur l'environnement
        adjusted_mutation_rate = self._calculate_adaptive_mutation_rate(
            environmental_pressure
        )

        if random.random() < adjusted_mutation_rate:
            # Sélection du type de mutation basée sur les contraintes
            mutation_type = self._select_mutation_type(environmental_pressure)

            # Application de la mutation avec vérification de faisabilité
            mutation_event = self._apply_constrained_mutation(
                mutation_type, mutagenic_factors
            )

            if mutation_event:
                mutation_events.append(mutation_event)
                self.evolutionary_history.append(mutation_event)

        # Mutations épigénétiques
        self.epigenetic_controller.apply_environmental_regulation(
            self, environmental_pressure
        )

        # Évolution du réseau d'interactions
        self.network_evolution.evolve_network_properties(self)

        return mutation_events

    def _calculate_adaptive_mutation_rate(self, environmental_pressure):
        """Calcule un taux de mutation adaptatif"""
        base_rate = self.mutation_rate

        # Augmentation du taux en cas de stress environnemental
        stress_multiplier = 1.0 + environmental_pressure * 2.0

        # Réduction si la charge mutationnelle est déjà élevée
        load_reducer = max(0.1, 1.0 - self.mutational_load)

        # Augmentation si le potentiel adaptatif est faible
        adaptation_booster = 1.0 + (1.0 - self.adaptive_potential) * 0.5

        return base_rate * stress_multiplier * load_reducer * adaptation_booster

    def _select_mutation_type(self, environmental_pressure):
        """Sélectionne un type de mutation basé sur le contexte"""
        mutation_weights = {
            MutationType.POINT: 0.6,
            MutationType.INSERTION: 0.1,
            MutationType.DELETION: 0.05,
            MutationType.DUPLICATION: 0.08,
            MutationType.INVERSION: 0.03,
            MutationType.EPIGENETIC: 0.1,
            MutationType.HORIZONTAL_TRANSFER: 0.02,
            MutationType.POLYPLOIDY: 0.01,
        }

        # Ajustement basé sur la pression environnementale
        if environmental_pressure > 0.7:
            mutation_weights[
                MutationType.DUPLICATION
            ] *= 2.0  # Plus de duplications sous stress
            mutation_weights[MutationType.EPIGENETIC] *= 3.0  # Plus d'épigénétique
            mutation_weights[MutationType.HORIZONTAL_TRANSFER] *= 1.5

        # Sélection pondérée
        mutation_types = list(mutation_weights.keys())
        weights = list(mutation_weights.values())

        return np.random.choice(mutation_types, p=np.array(weights) / np.sum(weights))

    def _apply_constrained_mutation(self, mutation_type, mutagenic_factors=None):
        """Applique une mutation en respectant les contraintes évolutives"""
        # Sélection du chromosome et du gène cibles
        target_chromosome = random.choice(list(self.chromosomes.keys()))
        target_chrom_obj = self.chromosomes[target_chromosome]

        if not target_chrom_obj.genes:
            return None

        target_gene_name = random.choice(list(target_chrom_obj.genes.keys()))

        # Création de l'événement de mutation proposé
        proposed_mutation = {
            "type": mutation_type,
            "target_chromosome": target_chromosome,
            "target_gene": target_gene_name,
            "timestamp": time.time(),
            "mutagenic_factors": mutagenic_factors or {},
        }

        # Évaluation de la faisabilité
        feasibility = self.evolution_constraints.evaluate_mutation_feasibility(
            self, proposed_mutation
        )

        if random.random() < feasibility:
            # Application de la mutation
            return self._execute_mutation(proposed_mutation)

        return None

    def _execute_mutation(self, mutation_event):
        """Exécute une mutation spécifique"""
        mutation_type = mutation_event["type"]
        target_chrom = self.chromosomes[mutation_event["target_chromosome"]]
        target_gene = target_chrom.genes[mutation_event["target_gene"]]

        if mutation_type == MutationType.POINT:
            self._point_mutation(target_gene)
        elif mutation_type == MutationType.INSERTION:
            self._insertion_mutation(target_gene)
        elif mutation_type == MutationType.DELETION:
            self._deletion_mutation(target_gene)
        elif mutation_type == MutationType.DUPLICATION:
            self._duplication_mutation(target_chrom, target_gene)
        elif mutation_type == MutationType.EPIGENETIC:
            self._epigenetic_mutation(target_gene)
        elif mutation_type == MutationType.HORIZONTAL_TRANSFER:
            self._horizontal_transfer_mutation()
        elif mutation_type == MutationType.POLYPLOIDY:
            self._polyploidy_mutation()

        # Mise à jour des métriques génomiques
        self._update_genome_metrics()

        mutation_event["executed"] = True
        mutation_event["effects"] = self._calculate_mutation_effects(target_gene)

        return mutation_event

    def _point_mutation(self, gene):
        """Mutation ponctuelle dans une séquence génique"""
        if gene.sequence:
            index = random.randint(0, len(gene.sequence) - 1)
            mutation_strength = random.uniform(-0.2, 0.2)
            gene.sequence[index] += mutation_strength
            gene.sequence[index] = max(-2.0, min(2.0, gene.sequence[index]))

    def _insertion_mutation(self, gene):
        """Insertion d'éléments dans la séquence génique"""
        insert_position = random.randint(0, len(gene.sequence))
        new_element = random.uniform(-1.0, 1.0)
        gene.sequence.insert(insert_position, new_element)

        # Ajustement de la méthylation
        gene.methylation_pattern.insert(insert_position, random.choice([True, False]))

    def _deletion_mutation(self, gene):
        """Délétion d'éléments de la séquence génique"""
        if len(gene.sequence) > 1:
            delete_position = random.randint(0, len(gene.sequence) - 1)
            del gene.sequence[delete_position]
            if delete_position < len(gene.methylation_pattern):
                del gene.methylation_pattern[delete_position]

    def _duplication_mutation(self, chromosome, gene):
        """Duplication d'un gène entier"""
        duplicated_gene = copy.deepcopy(gene)
        duplicated_gene.name = f"{gene.name}_dup_{len(chromosome.genes)}"
        duplicated_gene.expression_level *= random.uniform(0.5, 1.5)
        chromosome.add_gene(duplicated_gene)

    def _epigenetic_mutation(self, gene):
        """Modification épigénétique de l'expression"""
        # Modification de la méthylation
        for i in range(len(gene.methylation_pattern)):
            if random.random() < 0.1:
                gene.methylation_pattern[i] = not gene.methylation_pattern[i]

        # Ajustement de l'expression basé sur la méthylation
        methylation_ratio = sum(gene.methylation_pattern) / len(
            gene.methylation_pattern
        )
        gene.expression_level = max(0.0, 1.0 - methylation_ratio * 0.8)

    def _horizontal_transfer_mutation(self):
        """Transfert horizontal de gènes entre chromosomes"""
        if len(self.chromosomes) < 2:
            return

        source_chrom_name = random.choice(list(self.chromosomes.keys()))
        target_chrom_name = random.choice(
            [c for c in self.chromosomes.keys() if c != source_chrom_name]
        )

        source_chrom = self.chromosomes[source_chrom_name]
        target_chrom = self.chromosomes[target_chrom_name]

        if source_chrom.genes:
            transferred_gene_name = random.choice(list(source_chrom.genes.keys()))
            transferred_gene = copy.deepcopy(source_chrom.genes[transferred_gene_name])
            transferred_gene.name = f"{transferred_gene.name}_transferred"
            transferred_gene.expression_level *= random.uniform(
                0.3, 0.8
            )  # Expression réduite

            target_chrom.add_gene(transferred_gene)

    def _polyploidy_mutation(self):
        """Duplication chromosomique (polyploïdie)"""
        if len(self.chromosomes) < 6:  # Limite pour éviter une explosion chromosomique
            chromosome_to_duplicate = random.choice(list(self.chromosomes.keys()))
            duplicated_chrom = copy.deepcopy(self.chromosomes[chromosome_to_duplicate])

            # Modification légère des gènes dupliqués
            for gene in duplicated_chrom.genes.values():
                gene.expression_level *= random.uniform(0.7, 1.3)
                gene.name = f"{gene.name}_polyploid"

            new_chrom_name = f"{chromosome_to_duplicate}_duplicate"
            self.chromosomes[new_chrom_name] = duplicated_chrom

    def _calculate_mutation_effects(self, target_gene):
        """Calcule les effets d'une mutation sur la fitness"""
        effects = {
            "fitness_change": 0.0,
            "expression_change": 0.0,
            "interaction_changes": [],
            "phenotype_effects": {},
        }

        # Calcul de l'impact sur la fitness
        base_contribution = target_gene.fitness_contribution
        sequence_change = (
            np.std(target_gene.sequence) if len(target_gene.sequence) > 1 else 0.0
        )

        effects["fitness_change"] = (
            base_contribution * sequence_change * random.uniform(-0.1, 0.1)
        )

        # Impact sur l'expression
        old_expression = getattr(
            target_gene, "_previous_expression", target_gene.expression_level
        )
        effects["expression_change"] = target_gene.expression_level - old_expression

        return effects

    def _update_genome_metrics(self):
        """Met à jour les métriques de qualité génomique"""
        total_genes = sum(len(chrom.genes) for chrom in self.chromosomes.values())

        # Calcul de la charge mutationnelle
        deleterious_mutations = 0
        beneficial_mutations = 0

        for chrom in self.chromosomes.values():
            for gene in chrom.genes.values():
                fitness_contrib = gene.fitness_contribution
                if fitness_contrib < 0:
                    deleterious_mutations += 1
                elif fitness_contrib > 0.5:
                    beneficial_mutations += 1

        self.mutational_load = deleterious_mutations / max(total_genes, 1)

        # Calcul du potentiel adaptatif
        silent_genes = sum(
            1
            for chrom in self.chromosomes.values()
            for gene in chrom.genes.values()
            if gene.expression_level < 0.1
        )

        self.adaptive_potential = silent_genes / max(total_genes, 1)

        # Stabilité génomique
        recent_mutations = len(
            [
                event
                for event in self.evolutionary_history[-10:]
                if "executed" in event and event["executed"]
            ]
        )
        self.genome_stability = max(0.0, 1.0 - recent_mutations * 0.1)

    def get_phenotype(self):
        """Calcule le phénotype basé sur l'expression génique"""
        phenotype = {
            "physique": {},
            "alimentation": {},
            "social": {},
            "cerveau": {},
            "adaptation": {},
            "biologie": {},
        }

        # Agrégation des effets géniques par catégorie
        for chrom in self.chromosomes.values():
            for gene in chrom.genes.values():
                if gene.expression_level > 0.1:  # Gène exprimé
                    category = gene.name.split("_")[0]
                    trait = "_".join(gene.name.split("_")[1:])

                    if category in phenotype:
                        # Calcul de la valeur phénotypique
                        gene_value = np.mean(gene.sequence) * gene.expression_level

                        if trait in phenotype[category]:
                            # Moyenne pondérée si plusieurs gènes pour le même trait
                            phenotype[category][trait] = (
                                phenotype[category][trait] + gene_value
                            ) / 2
                        else:
                            phenotype[category][trait] = gene_value

        # Normalisation et contraintes biologiques
        phenotype = self._apply_phenotype_constraints(phenotype)

        return phenotype

    def _apply_phenotype_constraints(self, phenotype):
        """Applique des contraintes biologiques au phénotype"""
        # Contraintes physiques
        if "physique" in phenotype:
            if "taille" in phenotype["physique"]:
                phenotype["physique"]["taille"] = max(
                    0.3, min(3.0, phenotype["physique"]["taille"])
                )
            if "vitesse" in phenotype["physique"]:
                phenotype["physique"]["vitesse"] = max(
                    0.1, min(2.0, phenotype["physique"]["vitesse"])
                )

        # Contraintes neurologiques
        if "cerveau" in phenotype and "intelligence" in phenotype["cerveau"]:
            # L'intelligence ne peut pas dépasser certaines limites sans support métabolique
            max_intelligence = (
                phenotype.get("physique", {}).get("metabolisme", 1.0) * 1.5
            )
            phenotype["cerveau"]["intelligence"] = min(
                phenotype["cerveau"]["intelligence"], max_intelligence
            )

        # Contraintes énergétiques (compromis évolutifs)
        total_energy_cost = 0
        for category, traits in phenotype.items():
            for trait, value in traits.items():
                total_energy_cost += abs(value) * 0.1

        if total_energy_cost > 2.0:  # Limite énergétique
            reduction_factor = 2.0 / total_energy_cost
            for category in phenotype:
                for trait in phenotype[category]:
                    phenotype[category][trait] *= reduction_factor

        return phenotype

    def get_all_genes(self):
        """Retourne tous les gènes du génome"""
        all_genes = {}
        for chrom in self.chromosomes.values():
            all_genes.update(chrom.genes)
        return all_genes

    def get_all_gene_names(self):
        """Retourne tous les noms de gènes"""
        return list(self.get_all_genes().keys())

    def calculate_genetic_distance(self, other_genome):
        """Calcule la distance génétique avec un autre génome"""
        if not isinstance(other_genome, AdvancedGenome):
            return 1.0  # Distance maximale si types incompatibles

        self_genes = self.get_all_genes()
        other_genes = other_genome.get_all_genes()

        # Gènes communs
        common_genes = set(self_genes.keys()) & set(other_genes.keys())

        if not common_genes:
            return 1.0

        total_distance = 0.0
        for gene_name in common_genes:
            self_gene = self_genes[gene_name]
            other_gene = other_genes[gene_name]

            # Distance basée sur les séquences
            seq_distance = self._sequence_distance(
                self_gene.sequence, other_gene.sequence
            )

            # Distance épigénétique
            epig_distance = self._epigenetic_distance(self_gene, other_gene)

            gene_distance = (seq_distance + epig_distance) / 2
            total_distance += gene_distance

        return total_distance / len(common_genes)

    def _sequence_distance(self, seq1, seq2):
        """Calcule la distance entre deux séquences"""
        if not seq1 or not seq2:
            return 1.0

        min_len = min(len(seq1), len(seq2))
        max_len = max(len(seq1), len(seq2))

        # Distance basée sur les différences de valeurs
        differences = sum(abs(seq1[i] - seq2[i]) for i in range(min_len))

        # Pénalité pour les différences de longueur
        length_penalty = abs(len(seq1) - len(seq2)) / max_len

        normalized_distance = (differences / min_len + length_penalty) / 2
        return min(1.0, normalized_distance)

    def _epigenetic_distance(self, gene1, gene2):
        """Calcule la distance épigénétique entre deux gènes"""
        # Distance d'expression
        expr_distance = abs(gene1.expression_level - gene2.expression_level)

        # Distance de méthylation
        meth_distance = 0.0
        if len(gene1.methylation_pattern) == len(gene2.methylation_pattern):
            differences = sum(
                1
                for a, b in zip(gene1.methylation_pattern, gene2.methylation_pattern)
                if a != b
            )
            meth_distance = differences / len(gene1.methylation_pattern)
        else:
            meth_distance = 1.0

        return (expr_distance + meth_distance) / 2


def advanced_crossover(genome1, genome2, recombination_rate=0.5):
    """
    Croisement génétique ultra-avancé avec recombinaison chromosomique,
    épigénétique et réseaux d'interactions.
    """
    if not isinstance(genome1, AdvancedGenome) or not isinstance(
        genome2, AdvancedGenome
    ):
        # Fallback pour les anciens génomes
        return legacy_crossover_adapter(genome1, genome2)

    # Création du génome enfant
    child_genome = AdvancedGenome()
    child_genome.generation = max(genome1.generation, genome2.generation) + 1
    child_genome.lineage_id = f"{genome1.lineage_id[:4]}_{genome2.lineage_id[:4]}"

    # Héritage chromosomique avec recombinaison
    child_genome.chromosomes = {}

    # Pour chaque type de chromosome
    all_chrom_types = set(genome1.chromosomes.keys()) | set(genome2.chromosomes.keys())

    for chrom_type in all_chrom_types:
        child_chrom = Chromosome()

        # Sources parentales
        parent1_chrom = genome1.chromosomes.get(chrom_type)
        parent2_chrom = genome2.chromosomes.get(chrom_type)

        if parent1_chrom and parent2_chrom:
            # Recombinaison entre chromosomes homologues
            child_chrom = _recombine_chromosomes(
                parent1_chrom, parent2_chrom, recombination_rate
            )
        elif parent1_chrom:
            child_chrom = copy.deepcopy(parent1_chrom)
        elif parent2_chrom:
            child_chrom = copy.deepcopy(parent2_chrom)

        child_genome.chromosomes[chrom_type] = child_chrom

    # Héritage épigénétique
    _inherit_epigenetic_marks(child_genome, genome1, genome2)

    # Évolution du réseau d'interactions
    _evolve_interaction_networks(child_genome, genome1, genome2)

    # Application de mutations de novo
    child_genome.advanced_mutation(environmental_pressure=0.1)

    return child_genome


def _recombine_chromosomes(chrom1, chrom2, recombination_rate):
    """Recombinaison génétique entre deux chromosomes homologues"""
    child_chrom = Chromosome()

    # Mélange des propriétés chromosomiques
    child_chrom.centromere_position = np.mean(
        [chrom1.centromere_position, chrom2.centromere_position]
    )
    child_chrom.telomere_length = np.mean(
        [chrom1.telomere_length, chrom2.telomere_length]
    )
    child_chrom.chromatin_state = random.choice(
        [chrom1.chromatin_state, chrom2.chromatin_state]
    )

    # Recombinaison génique
    all_genes = set(chrom1.genes.keys()) | set(chrom2.genes.keys())

    for gene_name in all_genes:
        gene1 = chrom1.genes.get(gene_name)
        gene2 = chrom2.genes.get(gene_name)

        if gene1 and gene2:
            # Recombinaison intragénique
            child_gene = _recombine_genes(gene1, gene2, recombination_rate)
            child_chrom.add_gene(child_gene)
        elif gene1:
            child_chrom.add_gene(copy.deepcopy(gene1))
        elif gene2:
            child_chrom.add_gene(copy.deepcopy(gene2))

    return child_chrom


def _recombine_genes(gene1, gene2, recombination_rate):
    """Recombinaison au niveau génique"""
    # Nom du gène (priorité au parent le plus exprimé)
    if gene1.expression_level >= gene2.expression_level:
        child_gene = copy.deepcopy(gene1)
    else:
        child_gene = copy.deepcopy(gene2)

    # Recombinaison des séquences
    if len(gene1.sequence) == len(gene2.sequence):
        child_sequence = []
        for i in range(len(gene1.sequence)):
            if random.random() < recombination_rate:
                # Point de recombinaison
                parent_source = random.choice([gene1, gene2])
                child_sequence.append(parent_source.sequence[i])
            else:
                # Moyenne pondérée
                weight1 = gene1.expression_level / (
                    gene1.expression_level + gene2.expression_level + 1e-6
                )
                child_sequence.append(
                    gene1.sequence[i] * weight1 + gene2.sequence[i] * (1 - weight1)
                )

        child_gene.sequence = child_sequence

    # Héritage de l'expression (dominance/récessivité)
    if gene1.dominant and not gene2.dominant:
        child_gene.expression_level = gene1.expression_level
    elif gene2.dominant and not gene1.dominant:
        child_gene.expression_level = gene2.expression_level
    else:
        # Co-dominance ou moyenne
        child_gene.expression_level = (
            gene1.expression_level + gene2.expression_level
        ) / 2

    # Héritage des interactions
    child_gene.interaction_partners = (
        gene1.interaction_partners | gene2.interaction_partners
    )

    # Contribution à la fitness (moyenne)
    child_gene.fitness_contribution = (
        gene1.fitness_contribution + gene2.fitness_contribution
    ) / 2

    return child_gene


def _inherit_epigenetic_marks(child_genome, parent1, parent2):
    """Héritage des marques épigénétiques"""
    # Mélange des contrôleurs épigénétiques
    child_genome.epigenetic_controller.methylation_enzymes = {}

    for enzyme in parent1.epigenetic_controller.methylation_enzymes:
        level1 = parent1.epigenetic_controller.methylation_enzymes.get(enzyme, 0)
        level2 = parent2.epigenetic_controller.methylation_enzymes.get(enzyme, 0)
        child_genome.epigenetic_controller.methylation_enzymes[enzyme] = (
            level1 + level2
        ) / 2

    # Héritage de la mémoire environnementale
    combined_memory = list(parent1.epigenetic_controller.environmental_memory) + list(
        parent2.epigenetic_controller.environmental_memory
    )

    # Conservation des événements les plus récents et significatifs
    significant_memories = sorted(
        combined_memory,
        key=lambda x: x.get("stress_level", 0) * x.get("timestamp", 0),
        reverse=True,
    )[:50]

    child_genome.epigenetic_controller.environmental_memory.extend(significant_memories)


def _evolve_interaction_networks(child_genome, parent1, parent2):
    """Évolution des réseaux d'interactions dans la descendance"""
    # Fusion des réseaux parentaux
    child_genome.network_evolution.gene_networks = defaultdict(set)

    # Héritage des interactions avec innovation
    for parent in [parent1, parent2]:
        for gene, partners in parent.network_evolution.gene_networks.items():
            child_genome.network_evolution.gene_networks[gene].update(partners)

            # Innovation : nouvelles interactions avec faible probabilité
            if random.random() < 0.05:
                available_genes = list(child_genome.get_all_gene_names())
                if gene in available_genes:
                    available_genes.remove(gene)

                if available_genes:
                    new_partner = random.choice(available_genes)
                    child_genome.network_evolution.gene_networks[gene].add(new_partner)
                    child_genome.network_evolution.gene_networks[new_partner].add(gene)


def legacy_crossover_adapter(genome1, genome2):
    """Adaptateur pour la compatibilité avec les anciens génomes"""
    # Conversion en format avancé si nécessaire
    if not isinstance(genome1, AdvancedGenome):
        advanced_genome1 = AdvancedGenome()
        if hasattr(genome1, "data"):
            advanced_genome1._convert_legacy_genome(genome1.data)
        else:
            advanced_genome1._create_founder_genome()
    else:
        advanced_genome1 = genome1

    if not isinstance(genome2, AdvancedGenome):
        advanced_genome2 = AdvancedGenome()
        if hasattr(genome2, "data"):
            advanced_genome2._convert_legacy_genome(genome2.data)
        else:
            advanced_genome2._create_founder_genome()
    else:
        advanced_genome2 = genome2

    return advanced_crossover(advanced_genome1, advanced_genome2)


# Alias pour la compatibilité avec le code existant
Genome = AdvancedGenome
crossover = advanced_crossover
