"""
Modèle du monde et graphe de connaissances (Directives 15, 51).
Structure mémoire auto-organisée et évolutive.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class GrapheDeConnaissances:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self):
        self.noeuds = {}
        self.liens = {}
        self.version = 1
        self.derniere_reorganisation = time.time()

    def ajouter_noeud(self, id_noeud: str, donnees: Dict[str, Any]):
        """Ajoute nœud au graphe."""
        self.noeuds[id_noeud] = {
            "id": id_noeud,
            "donnees": donnees,
            "timestamp_creation": time.time(),
            "derniere_utilisation": time.time(),
            "compteur_acces": 0,
        }

    def ajouter_lien(
        self, id_source: str, id_cible: str, type_lien: str, poids: float = 1.0
    ):
        """Ajoute lien entre nœuds."""
        if id_source not in self.liens:
            self.liens[id_source] = {}

        self.liens[id_source][id_cible] = {
            "type": type_lien,
            "poids": poids,
            "timestamp": time.time(),
        }

    def obtenir_noeud(self, id_noeud: str) -> Optional[Dict[str, Any]]:
        """Obtient nœud et met à jour statistiques."""
        if id_noeud in self.noeuds:
            self.noeuds[id_noeud]["derniere_utilisation"] = time.time()
            self.noeuds[id_noeud]["compteur_acces"] += 1
            return self.noeuds[id_noeud]
        return None

    def reorganiser_memoire(self):
        """Réorganise mémoire selon fréquence usage."""
        maintenant = time.time()

        if maintenant - self.derniere_reorganisation < 300:
            return

        noeuds_inutiles = []
        for id_noeud, noeud in self.noeuds.items():
            if (
                maintenant - noeud["derniere_utilisation"] > 3600
                and noeud["compteur_acces"] < 3
            ):
                noeuds_inutiles.append(id_noeud)

        for id_noeud in noeuds_inutiles:
            self._archiver_noeud(id_noeud)

        self.derniere_reorganisation = maintenant
        logger.info(f"Mémoire réorganisée: {len(noeuds_inutiles)} nœuds archivés")

    def _archiver_noeud(self, id_noeud: str):
        """Archive nœud peu utilisé."""
        if id_noeud in self.noeuds:
            del self.noeuds[id_noeud]

        if id_noeud in self.liens:
            del self.liens[id_noeud]


    """TODO: Add docstring."""
    """TODO: Add docstring."""
class ModeleMonde:
    def __init__(self):
        self.graphe_connaissances = GrapheDeConnaissances()
        self.etat_actuel = {}
        self.historique_etats = []
        self.carte_locale = {}

    def update(self, nouvel_etat: Dict[str, Any]):
        """Met à jour modèle avec nouvel état."""
        self.etat_actuel = nouvel_etat
        self.historique_etats.append({"timestamp": time.time(), "etat": nouvel_etat})

        if len(self.historique_etats) > 1000:
            self.historique_etats = self.historique_etats[-800:]

        self._integrer_connaissances(nouvel_etat)

    def _integrer_connaissances(self, etat: Dict[str, Any]):
        """Intègre nouvel état dans graphe connaissances."""
        timestamp = str(time.time())

        if "entites_proches" in etat:
            for entite in etat["entites_proches"]:
                id_entite = f"entite_{entite['id']}"
                self.graphe_connaissances.ajouter_noeud(
                    id_entite,
                    {
                        "type_noeud": "Entite",
                        "donnees": entite,
                        "tags": ["vivant", entite["type"]],
                    },
                )

    def obtenir_entites_par_type(self, type_entite: str) -> List[Dict[str, Any]]:
        """Obtient entités par type."""
        entites = []
        for noeud in self.graphe_connaissances.noeuds.values():
            if noeud["donnees"].get("type_noeud") == "Entite" and type_entite in noeud[
                "donnees"
            ].get("tags", []):
                entites.append(noeud["donnees"]["donnees"])
        return entites

    def maintenance_periodique(self):
        """Maintenance périodique du modèle."""
        self.graphe_connaissances.reorganiser_memoire()