# Fichier : agents_emergents.py
# Module des agents d'émergence - Biologie, évolution, civilisations et phénomènes exotiques

import logging
import random
import string
from typing import TYPE_CHECKING, List

import numpy as np

from etatmonde import (
    EtatMonde,
    Planete,
    CelluleSimple,
    OrganismeComplexe,
    Civilisation,
    TrouNoir,
)

if TYPE_CHECKING:
    from etatmonde import EtatMonde

try:
    from scipy.spatial import cKDTree
except ImportError:
    cKDTree = None

logger = logging.getLogger(__name__)


class Biologiste:
    """Rôle : Catalyseur de Vie"""

    def __init__(self):
        """Initialise les paramètres d'émergence de la vie."""
        self.probabilite_abiogenese = 0.0001  # Très faible probabilité par cycle
        self.temp_min_vie = 200.0  # Température minimale pour la vie
        self.temp_max_vie = 400.0  # Température maximale pour la vie

    def _planete_habitable(self, planete: Planete) -> bool:
        """Détermine si une planète peut abriter la vie."""
        # Conditions : température modérée + présence d'eau (O + H)
        temp_ok = self.temp_min_vie <= planete.temperature <= self.temp_max_vie

        oxygene = planete.composition.get("oxygene", 0)
        hydrogene = planete.composition.get("hydrogene", 0)
        eau_possible = oxygene > 0 and hydrogene > 0

        masse_suffisante = planete.masse > 30.0  # Gravité pour retenir une atmosphère

        return temp_ok and eau_possible and masse_suffisante

    def biologiste(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Déclenche l'émergence de la vie sur les planètes favorables."""
        planetes: List[Planete] = etatmonde.entites.get("planetes", [])
        if not planetes:
            return etatmonde

        nouvelles_cellules = []

        for planete in planetes:
            # Vérifier si la planète abrite déjà la vie
            cellules_existantes = [
                c
                for c in etatmonde.entites.get("cellules_simples", [])
                if c.planete_hote_id == str(planete.id)
            ]

            if cellules_existantes:
                continue  # La vie existe déjà

            if self._planete_habitable(planete):
                # Tentative d'abiogenèse
                if random.random() < self.probabilite_abiogenese:
                    # Génération d'un ADN initial aléatoire
                    longueur_adn = random.randint(20, 50)
                    adn_initial = "".join(
                        random.choices(["A", "T", "G", "C"], k=longueur_adn)
                    )

                    nouvelle_cellule = CelluleSimple(
                        planete_hote_id=str(planete.id),
                        adn=adn_initial,
                        masse=0.001,  # Masse négligeable
                        position=planete.position.copy(),
                    )
                    nouvelles_cellules.append(nouvelle_cellule)

                    logger.info(
                        f"ABIOGENÈSE au Temps {etatmonde.temps}! "
                        f"Première vie sur planète {str(planete.id)[:8]}... "
                        f"(T: {planete.temperature:.1f}K, ADN: {len(adn_initial)} bases)"
                    )

        if nouvelles_cellules:
            etatmonde.entites["cellules_simples"].extend(nouvelles_cellules)

            if not any("PremiereVie" in p for p in etatmonde.paliers):
                etatmonde.paliers.append(f"[Temps: {etatmonde.temps}] - PremiereVie")

        return etatmonde


class Evolutif:
    """Rôle : Moteur de l'Évolution"""

    def __init__(self):
        """Initialise les paramètres évolutifs."""
        self.probabilite_mutation = 0.01
        self.seuil_complexite_evolution = 100  # Longueur d'ADN pour évoluer
        self.taux_evolution = 0.001  # Probabilité d'évolution vers une forme complexe

    def _muter_adn(self, adn: str) -> str:
        """Applique des mutations à une chaîne ADN."""
        adn_liste = list(adn)
        bases = ["A", "T", "G", "C"]

        # Mutations ponctuelles
        for i in range(len(adn_liste)):
            if random.random() < self.probabilite_mutation:
                adn_liste[i] = random.choice(bases)

        # Duplications (rares)
        if random.random() < 0.001 and len(adn_liste) < 200:
            segment_debut = random.randint(0, len(adn_liste) - 1)
            segment_fin = min(segment_debut + random.randint(1, 10), len(adn_liste))
            segment_duplique = adn_liste[segment_debut:segment_fin]
            position_insertion = random.randint(0, len(adn_liste))
            adn_liste[position_insertion:position_insertion] = segment_duplique

        return "".join(adn_liste)

    def evolutif(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Fait évoluer la vie simple vers des formes complexes."""
        cellules: List[CelluleSimple] = etatmonde.entites.get("cellules_simples", [])
        if not cellules:
            return etatmonde

        cellules_a_evoluer = []
        nouveaux_organismes = []

        for cellule in cellules:
            # Mutation de l'ADN
            ancien_adn = cellule.adn
            cellule.adn = self._muter_adn(cellule.adn)

            # Vérification de l'évolution vers une forme complexe
            if (
                len(cellule.adn) >= self.seuil_complexite_evolution
                and random.random() < self.taux_evolution
            ):

                # Calcul de la complexité génétique
                complexite = len(cellule.adn) + len(set(cellule.adn)) * 10

                nouvel_organisme = OrganismeComplexe(
                    planete_hote_id=cellule.planete_hote_id,
                    complexite_genetique=complexite,
                    masse=cellule.masse * 100,  # Plus gros qu'une cellule simple
                    position=cellule.position.copy(),
                )
                nouveaux_organismes.append(nouvel_organisme)
                cellules_a_evoluer.append(cellule)

                logger.info(
                    f"Évolution biologique au Temps {etatmonde.temps}: "
                    f"Organisme complexe émergé sur planète {cellule.planete_hote_id[:8]}... "
                    f"(Complexité génétique: {complexite:.0f})"
                )

        # Mise à jour de l'état du monde
        if nouveaux_organismes:
            etatmonde.entites["organismes_complexes"].extend(nouveaux_organismes)
            etatmonde.entites["cellules_simples"] = [
                c for c in cellules if c not in cellules_a_evoluer
            ]

            if not any("PremierOrganismeComplexe" in p for p in etatmonde.paliers):
                etatmonde.paliers.append(
                    f"[Temps: {etatmonde.temps}] - PremierOrganismeComplexe"
                )

        return etatmonde


class Sociologue:
    """Rôle : Déclencheur de Civilisation"""

    def __init__(self):
        """Initialise les paramètres d'émergence civilisationnelle."""
        self.seuil_complexite_intelligence = 500
        self.probabilite_intelligence = 0.0001  # Extrêmement rare

    def sociologue(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Fait émerger l'intelligence et la civilisation à partir d'organismes complexes."""
        organismes: List[OrganismeComplexe] = etatmonde.entites.get(
            "organismes_complexes", []
        )
        if not organismes:
            return etatmonde

        organismes_a_civiliser = []
        nouvelles_civilisations = []

        for organisme in organismes:
            if (
                organisme.complexite_genetique >= self.seuil_complexite_intelligence
                and random.random() < self.probabilite_intelligence
            ):

                # Émergence de l'intelligence
                population_initiale = random.uniform(1000, 10000)
                niveau_tech_initial = 1  # Âge de pierre

                nouvelle_civilisation = Civilisation(
                    planete_mere_id=organisme.planete_hote_id,
                    niveau_technologique=niveau_tech_initial,
                    population=population_initiale,
                    expansion=0.0,
                    masse=organisme.masse * population_initiale,
                    position=organisme.position.copy(),
                )
                nouvelles_civilisations.append(nouvelle_civilisation)
                organismes_a_civiliser.append(organisme)

                logger.info(
                    f"ÉMERGENCE CIVILISATIONNELLE au Temps {etatmonde.temps}! "
                    f"Civilisation primitive sur planète {organisme.planete_hote_id[:8]}... "
                    f"(Population: {population_initiale:.0f}, Tech Level: {niveau_tech_initial})"
                )

        # Mise à jour de l'état du monde
        if nouvelles_civilisations:
            etatmonde.entites["civilisations"].extend(nouvelles_civilisations)
            etatmonde.entites["organismes_complexes"] = [
                o for o in organismes if o not in organismes_a_civiliser
            ]

            if not any("PremiereCivilisation" in p for p in etatmonde.paliers):
                etatmonde.paliers.append(
                    f"[Temps: {etatmonde.temps}] - PremiereCivilisation"
                )

        return etatmonde


class PhysicienExotique:
    """Rôle : Gardien des Phénomènes Extrêmes"""

    def __init__(self):
        """Initialise les paramètres des phénomènes exotiques."""
        self.masse_critique_trou_noir = 1000.0
        self.rayon_influence_trou_noir = 50.0

    def physicienexotique(self, etatmonde: "EtatMonde") -> "EtatMonde":
        """Gère la formation de trous noirs et leur influence gravitationnelle."""
        if cKDTree is None:
            return etatmonde

        # Phase 1 : Formation de trous noirs à partir d'étoiles effondrées
        etoiles: List = etatmonde.entites.get("etoiles", [])
        nouveaux_trous_noirs = []
        etoiles_a_effondrer = []

        for etoile in etoiles:
            # Condition d'effondrement : étoile très massive + épuisement complet d'hydrogène
            if (
                etoile.masse > self.masse_critique_trou_noir
                and hasattr(etoile, "inventaire_elements")
                and etoile.inventaire_elements.get("hydrogene", 0) < etoile.masse * 0.01
            ):

                rayon_schwarzschild = (
                    2 * etoile.masse * 6.67430e-11 / (3e8**2)
                )  # Formule simplifiée

                nouveau_trou_noir = TrouNoir(
                    masse=etoile.masse * 1.5,  # Gain de masse lors de l'effondrement
                    position=etoile.position.copy(),
                    rayon_schwarzschild=rayon_schwarzschild,
                )
                nouveaux_trous_noirs.append(nouveau_trou_noir)
                etoiles_a_effondrer.append(etoile)

                logger.info(
                    f"EFFONDREMENT GRAVITATIONNEL au Temps {etatmonde.temps}! "
                    f"Trou noir formé (Masse: {nouveau_trou_noir.masse:.2f}, "
                    f"Rs: {rayon_schwarzschild:.6f})"
                )

        # Phase 2 : Influence des trous noirs existants
        trous_noirs: List[TrouNoir] = (
            etatmonde.entites.get("trous_noirs", []) + nouveaux_trous_noirs
        )

        if trous_noirs:
            positions_trous_noirs = np.array([tn.position for tn in trous_noirs])
            arbre_trous_noirs = cKDTree(positions_trous_noirs)

            # Attraction et destruction de matière
            entites_destructibles = []
            for categorie in ["particules", "atomes"]:
                entites_destructibles.extend(
                    [(e, categorie) for e in etatmonde.entites.get(categorie, [])]
                )

            entites_detruites = {cat: [] for cat in ["particules", "atomes"]}

            for entite, categorie in entites_destructibles:
                distances, indices = arbre_trous_noirs.query(entite.position, k=1)
                if distances < self.rayon_influence_trou_noir:
                    # L'entité est attirée et détruite par le trou noir
                    trou_noir = trous_noirs[indices]
                    trou_noir.masse += entite.masse * 0.1  # Gain de masse partiel
                    entites_detruites[categorie].append(entite)

            # Suppression des entités détruites
            for categorie, entites_a_supprimer in entites_detruites.items():
                if entites_a_supprimer:
                    ids_a_supprimer = {e.id for e in entites_a_supprimer}
                    etatmonde.entites[categorie] = [
                        e
                        for e in etatmonde.entites[categorie]
                        if e.id not in ids_a_supprimer
                    ]
                    logger.info(
                        f"Accrétion trou noir : {len(entites_a_supprimer)} {categorie} détruits"
                    )

        # Mise à jour de l'état du monde
        if nouveaux_trous_noirs:
            etatmonde.entites["trous_noirs"].extend(nouveaux_trous_noirs)
            etatmonde.entites["etoiles"] = [
                e for e in etoiles if e not in etoiles_a_effondrer
            ]

            if not any("PremierTrouNoir" in p for p in etatmonde.paliers):
                etatmonde.paliers.append(
                    f"[Temps: {etatmonde.temps}] - PremierTrouNoir"
                )

        return etatmonde


class AnalysteCosmique:
    """Rôle : Observateur Quantifiable (version étendue)"""

    def analystecosmique(self, etatmonde: "EtatMonde", dureecycle: float) -> dict:
        """
        Calcule les statistiques étendues, détecte les paliers et formate l'état pour l'affichage.
        Version étendue pour supporter toutes les nouvelles entités.
        """
        # Statistiques de base
        for categorie in etatmonde.entites:
            etatmonde.statistiques[f"nombre{categorie}"] = len(
                etatmonde.entites[categorie]
            )

        # Calculs spatiaux
        toutes_positions_list = [
            e.position for cat in etatmonde.entites.values() for e in cat
        ]
        taille_univers, centre_de_masse = 0.0, [0.0, 0.0, 0.0]
        if toutes_positions_list:
            toutes_positions_np = np.array(toutes_positions_list)
            centre_de_masse = np.mean(toutes_positions_np, axis=0).tolist()
            rayon_univers = np.max(
                np.linalg.norm(toutes_positions_np - centre_de_masse, axis=1)
            )
            taille_univers = round(rayon_univers * 2, 2)

        # Statistiques avancées
        etoiles = etatmonde.entites.get("etoiles", [])
        if etoiles:
            temp_moyenne = np.mean([e.temperature for e in etoiles])
            etatmonde.statistiques["temperature_moyenne_etoiles"] = round(
                temp_moyenne, 1
            )

        civilisations = etatmonde.entites.get("civilisations", [])
        if civilisations:
            population_totale = sum(c.population for c in civilisations)
            niveau_tech_max = max(c.niveau_technologique for c in civilisations)
            etatmonde.statistiques["population_totale_civilisations"] = int(
                population_totale
            )
            etatmonde.statistiques["niveau_technologique_max"] = niveau_tech_max

        etatmonde.statistiques.update(
            {"dureecycle": round(dureecycle, 4), "tailleunivers": taille_univers}
        )

        # Détection de nouveaux paliers
        paliers_a_detecter = [
            ("nombreatomes", "PremiereNucleosynthese"),
            ("nombreetoiles", "PremiereEtoile"),
            ("nombreplanetes", "PremierePlanete"),
            ("nombrecellules_simples", "PremiereVie"),
            ("nombreorganismes_complexes", "PremierOrganismeComplexe"),
            ("nombrecivilisations", "PremiereCivilisation"),
            ("nombregalaxi", "PremiereGalaxie"),
            ("nombretrous_noirs", "PremierTrouNoir"),
        ]

        for stat_key, palier_name in paliers_a_detecter:
            if etatmonde.statistiques.get(stat_key, 0) > 0 and not any(
                palier_name in p for p in etatmonde.paliers
            ):
                etatmonde.paliers.append(f"[Temps: {etatmonde.temps}] - {palier_name}")
                logger.info(f"Palier atteint au Temps {etatmonde.temps}: {palier_name}")

        # Formatage pour l'interface
        entites_pour_json = {}
        for cat, elist in etatmonde.entites.items():
            entites_pour_json[cat] = []
            for entite in elist:
                data = {k: v for k, v in entite.__dict__.items()}
                data["categorie"] = entite.categorie
                data["id"] = str(data["id"])
                data["position"] = data["position"].tolist()
                if "vecteur" in data:
                    data["vecteur"] = data["vecteur"].tolist()
                entites_pour_json[cat].append(data)

        return {
            "temps": etatmonde.temps,
            "statistiques": etatmonde.statistiques,
            "paliers": etatmonde.paliers,
            "entites": entites_pour_json,
            "visualisation": {
                "centredemasse": centre_de_masse,
                "rayonunivers": taille_univers / 2,
            },
        }
