import logging
from typing import Dict, List, Any
import time

logger = logging.getLogger(__name__)


class GenerateurActionsBesoins:
    """
    Générateur d'actions spécifiques selon les besoins identifiés.
    Implémente la logique d'adaptation des actions selon le contexte.
    """

    @staticmethod
    def actions_survie_immediate(urgence: int) -> List[Dict]:
        """
        Génère des actions de survie selon le niveau d'urgence.
        Actions adaptées dynamiquement selon la gravité de la situation.
        """
        try:
            actions = []
            timestamp = time.time()

            if urgence >= 80:
                # Urgence critique - actions immédiates
                actions.extend(
                    [
                        {"type": "CHERCHER_ABRI", "priorite": "critique", "duree": 60},
                        {"type": "CONSOMMER_NOURRITURE", "quantite": "disponible"},
                        {"type": "EVALUER_MENACES", "rayon": 20},
                    ]
                )
            elif urgence >= 60:
                # Urgence élevée - sécurisation rapide
                actions.extend(
                    [
                        {
                            "type": "CREER_ABRI_TEMPORAIRE",
                            "materiaux": ["dirt", "wood"],
                        },
                        {"type": "ALLUMER_TORCHES", "nombre": 4},
                        {"type": "PREPARER_DEFENSE", "outils": "disponibles"},
                    ]
                )
            elif urgence >= 40:
                # Urgence modérée - stabilisation
                actions.extend(
                    [
                        {"type": "COLLECTER_RESSOURCES_URGENTES", "focus": "food_wood"},
                        {"type": "AMELIORER_ABRI", "extensions": "basic"},
                        {"type": "SCANNER_ENVIRONNEMENT", "objectif": "ressources"},
                    ]
                )
            else:
                # Situation stable - préparation
                actions.extend(
                    [
                        {"type": "PLANIFIER_EXPEDITION", "objectif": "ressources"},
                        {"type": "OPTIMISER_INVENTAIRE", "methode": "tri_priorite"},
                        {"type": "EXPLORER_ZONE_SECURISEE", "rayon": 50},
                    ]
                )

            # Ajouter métadonnées pour traçabilité
            for action in actions:
                action["timestamp_generation"] = timestamp
                action["urgence_declencheur"] = urgence

            return actions[:8]  # Limiter à 8 actions pour éviter surcharge

        except Exception as e:
            logger.error(f"Erreur génération actions survie: {e}")
            return [
                {"type": "ANALYSER_SITUATION", "priorite": "immediate"},
                {"type": "ACTION_SECURITE_BASIQUE", "mode": "defensif"},
            ]

    @staticmethod
    def optimiser_actions_acquisition(ressources_manquantes: List[str]) -> List[Dict]:
        """
        Optimise l'ordre et la méthode de collecte des ressources.
        Groupe les actions par efficacité et proximité géographique.
        """
        try:
            actions = []
            timestamp = time.time()

            # Grouper ressources par zone/méthode d'acquisition
            zones_acquisition = GenerateurActionsBesoins._grouper_ressources_par_zone(
                ressources_manquantes
            )

            for zone, ressources in zones_acquisition.items():
                if zone == "surface":
                    actions.extend(
                        GenerateurActionsBesoins._actions_acquisition_surface(
                            ressources
                        )
                    )
                elif zone == "underground":
                    actions.extend(
                        GenerateurActionsBesoins._actions_acquisition_souterraine(
                            ressources
                        )
                    )
                elif zone == "biome_special":
                    actions.extend(
                        GenerateurActionsBesoins._actions_acquisition_biome(ressources)
                    )

            # Ajouter actions de préparation et finalisation
            actions_completes = (
                [
                    {
                        "type": "PREPARER_EXPEDITION",
                        "ressources": ressources_manquantes,
                        "timestamp": timestamp,
                    }
                ]
                + actions
                + [
                    {
                        "type": "RETOUR_BASE",
                        "condition": "inventaire_plein_ou_objectif_atteint",
                    },
                    {"type": "STOCKER_RESSOURCES", "organisation": "par_type"},
                    {"type": "EVALUER_RECOLTE", "objectifs": ressources_manquantes},
                ]
            )

            return actions_completes[:15]  # Limiter à 15 actions

        except Exception as e:
            logger.error(f"Erreur optimisation acquisition: {e}")
            return [
                {"type": "COLLECTER_BOIS", "quantite": 20},
                {"type": "COLLECTER_PIERRE", "quantite": 15},
            ]

    @staticmethod
    def generer_actions_construction(objectif: str, materiaux: List[str]) -> List[Dict]:
        """
        Génère une séquence d'actions pour un projet de construction.
        Optimise l'ordre des opérations et la gestion des ressources.
        """
        try:
            actions = []

            # Phase préparatoire
            actions.extend(
                [
                    {
                        "type": "CHOISIR_EMPLACEMENT",
                        "criteres": ["plat", "secure", "accessible"],
                    },
                    {"type": "VERIFIER_MATERIAUX", "liste": materiaux},
                    {
                        "type": "PREPARER_OUTILS",
                        "types": ["construction", "terrassement"],
                    },
                ]
            )

            # Phase de terrassement
            if "terraforming" in objectif.lower():
                actions.extend(
                    [
                        {"type": "MESURER_TERRAIN", "precision": "bloc"},
                        {"type": "NIVELER_SOL", "methode": "optimale"},
                    ]
                )

            # Phase de construction principale
            actions.extend(
                GenerateurActionsBesoins._actions_construction_specifiques(
                    objectif, materiaux
                )
            )

            # Phase de finition
            actions.extend(
                [
                    {"type": "VERIFIER_STRUCTURE", "controle": "stabilite"},
                    {"type": "AJOUTER_DETAILS", "niveau": "fonctionnel"},
                    {"type": "TESTER_FONCTIONNALITES", "objectif": objectif},
                ]
            )

            return actions[:12]  # Limiter à 12 actions

        except Exception as e:
            logger.error(f"Erreur génération actions construction: {e}")
            return [
                {"type": "PLACER_FONDATIONS", "materiau": "stone"},
                {"type": "CONSTRUIRE_MURS", "hauteur": 3},
                {"type": "AJOUTER_TOIT", "materiau": "wood"},
            ]

    @staticmethod
    def _grouper_ressources_par_zone(ressources: List[str]) -> Dict[str, List[str]]:
        """Groupe les ressources par zone d'acquisition"""
        zones = {"surface": [], "underground": [], "biome_special": []}

        mapping_zones = {
            "wood": "surface",
            "leaves": "surface",
            "food": "surface",
            "stone": "underground",
            "coal": "underground",
            "iron": "underground",
            "diamond": "underground",
            "redstone": "underground",
            "sand": "biome_special",
            "cactus": "biome_special",
            "ice": "biome_special",
        }

        for ressource in ressources:
            zone = mapping_zones.get(ressource, "surface")
            zones[zone].append(ressource)

        return {k: v for k, v in zones.items() if v}  # Retirer zones vides

    @staticmethod
    def _actions_acquisition_surface(ressources: List[str]) -> List[Dict]:
        """Actions pour ressources de surface"""
        actions = []
        if "wood" in ressources:
            actions.append(
                {"type": "COUPER_ARBRES", "quantite": 30, "especes": "chene"}
            )
        if "food" in ressources:
            actions.append(
                {"type": "CHASSER_ANIMAUX", "cibles": ["cow", "pig", "chicken"]}
            )
        return actions

    @staticmethod
    def _actions_acquisition_souterraine(ressources: List[str]) -> List[Dict]:
        """Actions pour ressources souterraines"""
        actions = [{"type": "DESCENDRE_MINE", "profondeur": "optimale"}]
        if "coal" in ressources:
            actions.append({"type": "MINER_CHARBON", "technique": "ramification"})
        if "iron" in ressources:
            actions.append({"type": "MINER_FER", "technique": "systématique"})
        return actions

    @staticmethod
    def _actions_acquisition_biome(ressources: List[str]) -> List[Dict]:
        """Actions pour ressources de biomes spéciaux"""
        actions = []
        if "sand" in ressources:
            actions.append({"type": "VOYAGER_DESERT", "objectif": "sable"})
        if "ice" in ressources:
            actions.append({"type": "VOYAGER_TUNDRA", "objectif": "glace"})
        return actions

    @staticmethod
    def _actions_construction_specifiques(
        objectif: str, materiaux: List[str]
    ) -> List[Dict]:
        """Actions spécifiques selon le type de construction"""
        actions = []

        if "maison" in objectif.lower():
            actions.extend(
                [
                    {"type": "CONSTRUIRE_FONDATIONS", "materiau": "stone"},
                    {"type": "ELEVER_MURS", "hauteur": 4, "materiau": materiaux[0]},
                    {"type": "INSTALLER_TOIT", "forme": "traditionnel"},
                    {"type": "AJOUTER_PORTE", "position": "sud"},
                    {"type": "INSTALLER_FENETRES", "nombre": 4},
                ]
            )
        elif "ferme" in objectif.lower():
            actions.extend(
                [
                    {"type": "DELIMITER_PARCELLES", "taille": "10x10"},
                    {"type": "INSTALLER_IRRIGATION", "systeme": "canaux"},
                    {"type": "CONSTRUIRE_SILO", "capacite": "grande"},
                ]
            )
        else:
            # Construction générique
            actions.extend(
                [
                    {"type": "ASSEMBLER_STRUCTURE", "methode": "modulaire"},
                    {"type": "RENFORCER_JOINTS", "materiau": "stone"},
                ]
            )

        return actions
