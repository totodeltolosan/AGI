import random
import math
import time
import logging
from typing import Dict, List, Tuple
from collections import deque

logger = logging.getLogger(__name__)


class GenerateurHypotheses:
    """
    Génère des hypothèses d'exploration intelligentes.
    Respecte Directive 61 avec focus sur la génération uniquement.
    """

    def __init__(self, modele_monde):
        """TODO: Add docstring."""
        self.modele_monde = modele_monde
        self.hypotheses_testees = deque(maxlen=50)

    def generer_hypotheses_exploration(self) -> List[Dict]:
        """Génère plusieurs hypothèses d'exploration."""
        hypotheses = []
        connaissances = self.modele_monde.graphe_connaissances["noeuds"]

        # Hypothèse basée sur les ressources manquantes
        if self._ressource_rare_detectee(connaissances):
            hypotheses.append(
                {
                    "type": "recherche_ressource",
                    "description": "Explorer les grottes profondes pour trouver des minerais rares",
                    "probabilite": 0.7,
                    "effort_estime": "elevé",
                    "zone_cible": self._estimer_zone_minerais(),
                    "methode": "exploration_souterraine",
                }
            )

        # Hypothèse basée sur les patterns géologiques
        if self._pattern_geologique_detecte(connaissances):
            hypotheses.append(
                {
                    "type": "pattern_geologique",
                    "description": "Suivre les veines de pierre pour découvrir des formations intéressantes",
                    "probabilite": 0.6,
                    "effort_estime": "moyen",
                    "zone_cible": self._suivre_formations_rocheuses(),
                    "methode": "suivi_geologique",
                }
            )

        # Hypothèse basée sur l'eau
        if "eau" in connaissances or self._cours_eau_detecte():
            hypotheses.append(
                {
                    "type": "suivi_eau",
                    "description": "Remonter ou descendre le cours d'eau pour découvrir de nouveaux biomes",
                    "probabilite": 0.8,
                    "effort_estime": "faible",
                    "zone_cible": self._suivre_cours_eau(),
                    "methode": "exploration_hydraulique",
                }
            )

        # Hypothèse basée sur les structures
        if self._structures_anciennes_detectees(connaissances):
            hypotheses.append(
                {
                    "type": "archeologie",
                    "description": "Investiguer les structures anciennes pour révéler des réseaux cachés",
                    "probabilite": 0.9,
                    "effort_estime": "moyen",
                    "zone_cible": self._localiser_structures_connexes(),
                    "methode": "exploration_archeologique",
                }
            )

        # Hypothèse basée sur les biomes non explorés
        biomes_connus = self._identifier_biomes_connus()
        if len(biomes_connus) < 4:
            hypotheses.append(
                {
                    "type": "diversification_biome",
                    "description": f"Chercher de nouveaux biomes - {4-len(biomes_connus)} types manquants",
                    "probabilite": 0.75,
                    "effort_estime": "moyen",
                    "zone_cible": self._prediction_nouveaux_biomes(),
                    "methode": "exploration_climatique",
                }
            )

        # Filtrer les hypothèses déjà testées récemment
        hypotheses_filtrees = [
            h for h in hypotheses if not self._hypothese_recemment_testee(h)
        ]

        return sorted(hypotheses_filtrees, key=lambda h: h["probabilite"], reverse=True)

    def _ressource_rare_detectee(self, connaissances: Dict) -> bool:
        """Vérifie si des indices de ressources rares ont été détectés."""
        ressources_rares = ["diamond", "emerald", "gold", "redstone", "lapis"]
        return any(ressource in connaissances for ressource in ressources_rares)

    def _pattern_geologique_detecte(self, connaissances: Dict) -> bool:
        """Détecte des patterns géologiques intéressants."""
        if "composition_terrain" in connaissances:
            terrain = connaissances["composition_terrain"]
            return terrain.get("stone", 0) > 20 and terrain.get("dirt", 0) < 5
        return False

    def _cours_eau_detecte(self) -> bool:
        """Détecte la présence de cours d'eau."""
        carte = getattr(self.modele_monde, "carte_du_monde", {})
        return any("water" in str(bloc) for bloc in carte.values())

    def _structures_anciennes_detectees(self, connaissances: Dict) -> bool:
        """Détecte la présence de structures anciennes."""
        structures = ["village", "temple", "dungeon", "stronghold", "mansion"]
        return any(structure in connaissances for structure in structures)

    def _identifier_biomes_connus(self) -> List[str]:
        """Identifie les biomes déjà connus."""
        connaissances = self.modele_monde.graphe_connaissances["noeuds"]
        biomes = []

        for noeud_id, data in connaissances.items():
            if "biome" in noeud_id.lower():
                biomes.append(noeud_id)

        # Ajouter détection depuis l'environnement actuel
        biome_actuel = (
            self.modele_monde.detecter_biome()
            if hasattr(self.modele_monde, "detecter_biome")
            else "inconnu"
        )
        if biome_actuel != "inconnu" and biome_actuel not in biomes:
            biomes.append(biome_actuel)

        return biomes

    def _estimer_zone_minerais(self) -> Tuple[float, float, float]:
        """Estime une zone probable pour trouver des minerais."""
        position = self.modele_monde.get_position_joueur()
        # Chercher plus profond et dans des zones rocheuses
        return (
            position[0] + random.randint(-50, 50),
            max(5, position[1] - random.randint(10, 30)),  # Plus profond
            position[2] + random.randint(-50, 50),
        )

    def _suivre_formations_rocheuses(self) -> Tuple[float, float, float]:
        """Suit les formations rocheuses pour explorer."""
        position = self.modele_monde.get_position_joueur()
        carte = getattr(self.modele_monde, "carte_du_monde", {})

        # Trouver la direction avec le plus de pierre
        directions_pierre = {}
        for pos_str, bloc in carte.items():
            if "stone" in str(bloc):
                try:
                    pos = tuple(map(float, pos_str.split(",")))
                    direction = (pos[0] - position[0], pos[2] - position[2])
                    angle = math.atan2(direction[1], direction[0])
                    secteur = int(angle * 4 / math.pi) % 8  # 8 secteurs
                    directions_pierre[secteur] = directions_pierre.get(secteur, 0) + 1
                except:
                    continue

        if directions_pierre:
            meilleur_secteur = max(directions_pierre, key=directions_pierre.get)
            angle = meilleur_secteur * math.pi / 4
            distance = 75
            return (
                position[0] + distance * math.cos(angle),
                position[1],
                position[2] + distance * math.sin(angle),
            )

        return (
            position[0] + random.randint(-100, 100),
            position[1],
            position[2] + random.randint(-100, 100),
        )

    def _suivre_cours_eau(self) -> Tuple[float, float, float]:
        """Suit un cours d'eau pour explorer."""
        position = self.modele_monde.get_position_joueur()
        carte = getattr(self.modele_monde, "carte_du_monde", {})

        # Trouver les blocs d'eau les plus éloignés
        eaux_distantes = []
        for pos_str, bloc in carte.items():
            if "water" in str(bloc):
                try:
                    pos = tuple(map(float, pos_str.split(",")))
                    distance = math.sqrt(
                        (pos[0] - position[0]) ** 2 + (pos[2] - position[2]) ** 2
                    )
                    if distance > 20:  # Suffisamment loin
                        eaux_distantes.append((pos, distance))
                except:
                    continue

        if eaux_distantes:
            cible = max(eaux_distantes, key=lambda x: x[1])[0]
            return cible

        # Direction aléatoire le long d'une rivière supposée
        angle = random.uniform(0, 2 * math.pi)
        distance = 100
        return (
            position[0] + distance * math.cos(angle),
            position[1],
            position[2] + distance * math.sin(angle),
        )

    def _localiser_structures_connexes(self) -> Tuple[float, float, float]:
        """Localise des structures potentiellement connectées."""
        position = self.modele_monde.get_position_joueur()
        # Les structures sont souvent espacées de 100-500 blocs
        distance = random.randint(150, 400)
        angle = random.uniform(0, 2 * math.pi)
        return (
            position[0] + distance * math.cos(angle),
            position[1],
            position[2] + distance * math.sin(angle),
        )

    def _prediction_nouveaux_biomes(self) -> Tuple[float, float, float]:
        """Prédit où trouver de nouveaux biomes."""
        position = self.modele_monde.get_position_joueur()
        biome_actuel = (
            self.modele_monde.detecter_biome()
            if hasattr(self.modele_monde, "detecter_biome")
            else "inconnu"
        )

        # Règles de transition de biomes
        if biome_actuel == "forêt":
            # Chercher montagne ou plaines
            return (
                position[0] + random.randint(200, 500),
                position[1] + random.randint(20, 80),
                position[2] + random.randint(-300, 300),
            )
        elif biome_actuel == "plaines":
            # Chercher désert ou océan
            return (
                position[0] + random.randint(-500, 500),
                position[1],
                position[2] + random.randint(300, 800),
            )
        else:
            # Exploration générale
            distance = random.randint(300, 600)
            angle = random.uniform(0, 2 * math.pi)
            return (
                position[0] + distance * math.cos(angle),
                position[1],
                position[2] + distance * math.sin(angle),
            )

    def _hypothese_recemment_testee(self, hypothese: Dict) -> bool:
        """Vérifie si une hypothèse similaire a été testée récemment."""
        for hypothese_testee in self.hypotheses_testees:
            if (
                hypothese_testee.get("type") == hypothese.get("type")
                and time.time() - hypothese_testee.get("timestamp", 0) < 1800
            ):  # 30 minutes
                return True
        return False