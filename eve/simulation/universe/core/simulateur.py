# Fichier : simulateur.py
# Version 9.0 ("Orchestrateur Robuste") - Architecture modulaire optimisée et résiliente.

"""
Module du Simulateur pour le Projet Monde.
Agit comme un "producteur" : calcule les états de l'univers aussi vite que
possible et les place dans une file d'attente partagée.
Architecture robuste avec gestion d'erreurs avancée, métriques de performance
et système de récupération automatique des agents.
"""

import logging
import time
import json
import importlib
import inspect
import threading
from queue import Queue, Full, Empty
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker, pyqtSlot

from etatmonde import EtatMonde

logger = logging.getLogger(__name__)

# ========================================================================
# CONFIGURATION ET ÉNUMÉRATIONS
# ========================================================================


class EtatAgent(Enum):
    """États possibles d'un agent."""

    ACTIF = "actif"
    DESACTIVE = "desactive"
    EN_ERREUR = "en_erreur"
    EN_RECOVERY = "en_recovery"


@dataclass
class ConfigurationSimulateur:
    """Configuration centralisée du simulateur."""

    # Gestion des erreurs
    seuil_erreurs_max: int = 5
    cycles_avant_recovery: int = 100
    recovery_automatique: bool = True

    # Performance
    limite_entites_performance: int = 20000
    frequence_nettoyage_cache: int = 1000
    monitoring_performance: bool = True

    # Modules d'agents
    modules_agents: List[str] = field(
        default_factory=lambda: [
            "agents",
            "agents_physiques",
            "agents_complexes",
            "agents_emergents",
        ]
    )

    # Ordre d'exécution des agents
    ordre_modificateurs: List[str] = field(
        default_factory=lambda: [
            "calculateurlois",  # Gravité et mouvement (base physique)
            "alchimiste",  # Fusion particules → atomes
            "astrophysicien",  # Formation d'étoiles
            "chimiste",  # Évolution stellaire et supernovae
            "planetologue",  # Formation de planètes
            "biologiste",  # Émergence de la vie
            "galacticien",  # Structures galactiques
            "physicienexotique",  # Trous noirs et phénomènes extrêmes
        ]
    )

    ordre_analyseurs: List[str] = field(
        default_factory=lambda: ["evolutif", "analystecosmique"]
    )


@dataclass
class MetriqueAgent:
    """Métriques de performance d'un agent."""

    nom: str
    etat: EtatAgent = EtatAgent.ACTIF
    executions_totales: int = 0
    executions_reussies: int = 0
    erreurs_consecutives: int = 0
    derniere_execution: float = 0.0
    temps_execution_total: float = 0.0
    derniere_erreur: str = ""
    cycle_derniere_recovery: int = 0

    def temps_execution_moyen(self) -> float:
        """Calcule le temps d'exécution moyen."""
        return (
            self.temps_execution_total / self.executions_totales
            if self.executions_totales > 0
            else 0.0
        )

    def taux_reussite(self) -> float:
        """Calcule le taux de réussite."""
        return (
            self.executions_reussies / self.executions_totales
            if self.executions_totales > 0
            else 0.0
        )


# ========================================================================
# GESTIONNAIRE D'AGENTS ROBUSTE
# ========================================================================


class GestionnaireAgents:
    """Gère le chargement, l'exécution et la récupération des agents."""

    def __init__(self, config: ConfigurationSimulateur):
        self.config = config
        self.agents_charges: Dict[str, Any] = {}
        self.metriques: Dict[str, MetriqueAgent] = {}
        self.agents_desactives: Set[str] = set()
        self.cycle_actuel = 0

    def decouvrir_et_charger_agents(self) -> bool:
        """
        Découvre et charge tous les agents des modules spécifiés.

        Returns:
            bool: True si au moins MaitreTemps est chargé
        """
        logger.info("Découverte et chargement des agents...")
        agents_charges = {}

        for nom_module in self.config.modules_agents:
            try:
                module = importlib.import_module(nom_module)

                for nom, cls in inspect.getmembers(module, inspect.isclass):
                    # Filtrer les classes du module actuel seulement
                    if cls.__module__ == nom_module and not nom.startswith("_"):
                        try:
                            instance = cls()
                            nom_lower = nom.lower()
                            agents_charges[nom_lower] = instance

                            # Initialiser les métriques
                            self.metriques[nom_lower] = MetriqueAgent(nom=nom_lower)

                            logger.info(
                                f"-> Agent '{nom}' chargé depuis '{nom_module}.py'"
                            )

                        except Exception as e:
                            logger.error(
                                f"Impossible d'instancier l'agent '{nom}': {e}"
                            )

            except ImportError as e:
                logger.warning(f"Module '{nom_module}.py' introuvable: {e}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de '{nom_module}.py': {e}")

        self.agents_charges = agents_charges

        # Vérification critique de MaitreTemps
        if "maitretemps" not in agents_charges:
            logger.critical("ERREUR CRITIQUE : Agent 'MaitreTemps' introuvable")
            logger.critical(f"Agents trouvés : {list(agents_charges.keys())}")
            return False

        logger.info(f"Chargement terminé : {len(agents_charges)} agents disponibles")
        return True

    def executer_agent(
        self, nom_agent: str, etatmonde: EtatMonde, **kwargs
    ) -> Tuple[EtatMonde, bool]:
        """
        Exécute un agent avec gestion d'erreurs et métriques.

        Args:
            nom_agent: Nom de l'agent à exécuter
            etatmonde: État de l'univers
            **kwargs: Arguments additionnels pour l'agent

        Returns:
            Tuple[EtatMonde, bool]: Nouvel état et succès de l'exécution
        """
        if nom_agent in self.agents_desactives:
            return etatmonde, False

        agent = self.agents_charges.get(nom_agent)
        metrique = self.metriques.get(nom_agent)

        if not agent or not metrique:
            return etatmonde, False

        # Vérification de récupération automatique
        if (
            metrique.etat == EtatAgent.EN_ERREUR
            and self.config.recovery_automatique
            and self.cycle_actuel - metrique.cycle_derniere_recovery
            > self.config.cycles_avant_recovery
        ):

            logger.info(
                f"Tentative de récupération automatique pour agent '{nom_agent}'"
            )
            metrique.etat = EtatAgent.EN_RECOVERY
            metrique.erreurs_consecutives = 0

        if metrique.etat == EtatAgent.DESACTIVE:
            return etatmonde, False

        # Exécution avec métriques
        temps_debut = time.time()
        metrique.executions_totales += 1

        try:
            # Obtenir la méthode correspondante
            methode = getattr(agent, nom_agent)

            # Exécution selon le type d'agent
            if nom_agent == "analystecosmique":
                duree_cycle = kwargs.get("duree_cycle", 0.0)
                resultat = methode(etatmonde, duree_cycle)
                etatmonde_retour = etatmonde  # AnalysteCosmique ne modifie pas l'état
            else:
                resultat = methode(etatmonde)
                etatmonde_retour = (
                    resultat if isinstance(resultat, EtatMonde) else etatmonde
                )

            # Succès de l'exécution
            temps_execution = time.time() - temps_debut
            metrique.executions_reussies += 1
            metrique.erreurs_consecutives = 0
            metrique.derniere_execution = temps_execution
            metrique.temps_execution_total += temps_execution

            if metrique.etat == EtatAgent.EN_RECOVERY:
                logger.info(f"Agent '{nom_agent}' récupéré avec succès")
                metrique.etat = EtatAgent.ACTIF

            return etatmonde_retour, True

        except Exception as e:
            # Gestion d'erreur avec métriques
            metrique.erreurs_consecutives += 1
            metrique.derniere_erreur = str(e)

            logger.error(
                f"Erreur dans l'agent '{nom_agent}' (#{metrique.erreurs_consecutives}): {e}",
                exc_info=True,
            )

            # Décision de désactivation
            if metrique.erreurs_consecutives >= self.config.seuil_erreurs_max:
                if self.config.recovery_automatique:
                    metrique.etat = EtatAgent.EN_ERREUR
                    metrique.cycle_derniere_recovery = self.cycle_actuel
                    logger.warning(
                        f"Agent '{nom_agent}' en erreur, récupération programmée dans "
                        f"{self.config.cycles_avant_recovery} cycles"
                    )
                else:
                    metrique.etat = EtatAgent.DESACTIVE
                    self.agents_desactives.add(nom_agent)
                    logger.warning(f"Agent '{nom_agent}' désactivé définitivement")

            return etatmonde, False

    def obtenir_rapport_performance(self) -> Dict[str, Any]:
        """Génère un rapport de performance des agents."""
        rapport = {
            "agents_actifs": len(
                [m for m in self.metriques.values() if m.etat == EtatAgent.ACTIF]
            ),
            "agents_en_erreur": len(
                [m for m in self.metriques.values() if m.etat == EtatAgent.EN_ERREUR]
            ),
            "agents_desactives": len(self.agents_desactives),
            "metriques_detaillees": {},
        }

        for nom, metrique in self.metriques.items():
            rapport["metriques_detaillees"][nom] = {
                "etat": metrique.etat.value,
                "executions": metrique.executions_totales,
                "taux_reussite": metrique.taux_reussite(),
                "temps_moyen_ms": metrique.temps_execution_moyen() * 1000,
                "erreurs_consecutives": metrique.erreurs_consecutives,
            }

        return rapport


# ========================================================================
# SIMULATEUR PRINCIPAL AMÉLIORÉ
# ========================================================================


class Simulateur(QObject):
    """
    Le cœur de la simulation. Version robuste avec gestion d'erreurs avancée,
    métriques de performance et système de récupération automatique.
    """

    etatMiseAJour = pyqtSignal(str)
    sauvegardeEffectuee = pyqtSignal(bool, str)
    metriquesDisponibles = pyqtSignal(dict)  # Nouveau signal pour métriques

    def __init__(
        self,
        etatmonde: EtatMonde,
        file_etats: Queue,
        config: Optional[ConfigurationSimulateur] = None,
    ):
        """Initialise le simulateur avec configuration flexible."""
        super().__init__()

        # Configuration
        self.config = config or ConfigurationSimulateur()

        # État de simulation
        self.etatmonde = etatmonde
        self.file_etats = file_etats

        # Gestionnaire d'agents
        self.gestionnaire_agents = GestionnaireAgents(self.config)

        # État du simulateur
        self._en_marche = True
        self._en_pause = False
        self._multiplicateur_cycle = 1
        self._mutex = QMutex()
        self._cycle_actuel = 0
        self._arret_demande = threading.Event()

        # Métriques de performance
        self.metriques_simulation = {
            "cycles_total": 0,
            "temps_simulation_total": 0.0,
            "cycles_par_seconde": 0.0,
            "derniere_mise_a_jour_metriques": time.time(),
        }

        # Initialisation
        succes_chargement = self.gestionnaire_agents.decouvrir_et_charger_agents()
        if not succes_chargement:
            logger.critical("Échec du chargement des agents critiques")
            self._en_marche = False

    def _calculer_metriques_performance(self, duree_cycle: float) -> None:
        """Calcule et met à jour les métriques de performance."""
        self.metriques_simulation["cycles_total"] += 1
        self.metriques_simulation["temps_simulation_total"] += duree_cycle

        # Calcul CPS (Cycles Per Second) toutes les 100 itérations
        if self.metriques_simulation["cycles_total"] % 100 == 0:
            maintenant = time.time()
            temps_ecoule = (
                maintenant - self.metriques_simulation["derniere_mise_a_jour_metriques"]
            )

            if temps_ecoule > 0:
                self.metriques_simulation["cycles_par_seconde"] = 100.0 / temps_ecoule
                self.metriques_simulation["derniere_mise_a_jour_metriques"] = maintenant

                # Émission du signal métriques
                rapport_complet = {
                    "simulation": self.metriques_simulation.copy(),
                    "agents": self.gestionnaire_agents.obtenir_rapport_performance(),
                }
                self.metriquesDisponibles.emit(rapport_complet)

    def _optimiser_selon_charge(self) -> Dict[str, Any]:
        """Optimise les paramètres selon la charge actuelle."""
        total_entites = sum(len(cat) for cat in self.etatmonde.entites.values())

        optimisations = {
            "skip_agents_lourds": False,
            "frequence_reduite": 1,
            "limite_calculs": False,
        }

        if total_entites > self.config.limite_entites_performance:
            logger.info(f"Optimisation activée pour {total_entites} entités")
            optimisations.update(
                {
                    "skip_agents_lourds": True,
                    "frequence_reduite": 3,  # Exécuter 1 cycle sur 3 pour agents lourds
                    "limite_calculs": True,
                }
            )

        return optimisations

    @pyqtSlot()
    def lancerboucle(self):
        """
        Boucle principale de simulation avec optimisations et monitoring.
        """
        maitre_temps = self.gestionnaire_agents.agents_charges.get("maitretemps")
        if not maitre_temps:
            logger.critical("Impossible de démarrer sans MaitreTemps")
            return

        logger.info("Démarrage de la boucle de simulation robuste")

        while self._en_marche and not self._arret_demande.is_set():
            # Vérification état et récupération des paramètres thread-safe
            with QMutexLocker(self._mutex):
                en_pause = self._en_pause
                cycles_a_calculer = self._multiplicateur_cycle

            if en_pause:
                time.sleep(0.1)
                continue

            temps_debut_tour = time.time()
            optimisations = self._optimiser_selon_charge()

            # Mise à jour du cycle pour recovery
            self.gestionnaire_agents.cycle_actuel = self._cycle_actuel

            # Exécution des cycles de calcul
            for cycle_idx in range(cycles_a_calculer):
                # 1. Avancement temporel (toujours en premier)
                nouvel_etat, succes = self.gestionnaire_agents.executer_agent(
                    "maitretemps", self.etatmonde
                )
                if succes:
                    self.etatmonde = nouvel_etat
                    self._cycle_actuel += 1
                else:
                    logger.critical("Échec critique de MaitreTemps, arrêt simulation")
                    self._en_marche = False
                    break

                # 2. Agents modificateurs dans l'ordre d'émergence
                for nom_agent in self.config.ordre_modificateurs:
                    if nom_agent not in self.gestionnaire_agents.agents_charges:
                        continue

                    # Optimisation : skip agents lourds selon charge
                    if optimisations["skip_agents_lourds"] and nom_agent in [
                        "galacticien"
                    ]:
                        if cycle_idx % optimisations["frequence_reduite"] != 0:
                            continue

                    nouvel_etat, succes = self.gestionnaire_agents.executer_agent(
                        nom_agent, self.etatmonde
                    )
                    if succes:
                        self.etatmonde = nouvel_etat

            duree_calcul_total = time.time() - temps_debut_tour

            # 3. Exécution des agents d'analyse
            for nom_agent in self.config.ordre_analyseurs:
                if nom_agent not in self.gestionnaire_agents.agents_charges:
                    continue

                kwargs = {}
                if nom_agent == "analystecosmique":
                    kwargs["duree_cycle"] = (
                        duree_calcul_total / cycles_a_calculer
                        if cycles_a_calculer > 0
                        else 0.0
                    )

                resultat, succes = self.gestionnaire_agents.executer_agent(
                    nom_agent, self.etatmonde, **kwargs
                )

                # Gestion spéciale pour AnalysteCosmique
                if succes and nom_agent == "analystecosmique":
                    try:
                        # resultat contient les données JSON pour l'interface
                        json_data = json.dumps(resultat)

                        # Gestion optimisée de la queue
                        try:
                            self.file_etats.put_nowait(json_data)
                        except Full:
                            # Queue pleine : retirer ancien état et ajouter nouveau
                            try:
                                self.file_etats.get_nowait()
                                self.file_etats.put_nowait(json_data)
                            except Empty:
                                pass  # Queue vidée entre temps

                    except (TypeError, ValueError) as e:
                        logger.error(f"Erreur sérialisation JSON AnalysteCosmique: {e}")

                # Mise à jour état pour agents modificateurs comme Evolutif
                elif succes and isinstance(resultat, EtatMonde):
                    self.etatmonde = resultat

            # 4. Calcul et émission des métriques
            if self.config.monitoring_performance:
                self._calculer_metriques_performance(duree_calcul_total)

            # 5. Nettoyage périodique
            if self._cycle_actuel % self.config.frequence_nettoyage_cache == 0:
                self._nettoyer_caches()

    def _nettoyer_caches(self) -> None:
        """Nettoyage périodique des caches et optimisations mémoire."""
        try:
            # Nettoyage de l'index des entités
            entries_nettoyees = self.etatmonde.nettoyer_index()
            if entries_nettoyees > 0:
                logger.debug(f"Cache nettoyé : {entries_nettoyees} entrées obsolètes")

            # Validation périodique de cohérence
            if self._cycle_actuel % (self.config.frequence_nettoyage_cache * 5) == 0:
                rapport = self.etatmonde.valider_coherence()
                if rapport["erreurs"]:
                    logger.warning(
                        f"Problèmes de cohérence détectés : {len(rapport['erreurs'])} erreurs"
                    )

        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des caches : {e}")

    @pyqtSlot()
    def arreter(self):
        """Arrête la simulation proprement avec nettoyage des ressources."""
        logger.info("Arrêt du simulateur demandé...")

        with QMutexLocker(self._mutex):
            self._en_marche = False

        self._arret_demande.set()

        # Nettoyage des pools de processus
        for nom_agent, agent in self.gestionnaire_agents.agents_charges.items():
            if hasattr(agent, "fermer_pool"):
                try:
                    agent.fermer_pool()
                    logger.debug(f"Pool de {nom_agent} fermé")
                except Exception as e:
                    logger.warning(f"Erreur fermeture pool {nom_agent}: {e}")

    @pyqtSlot()
    def mettre_en_pause(self):
        """Met la simulation en pause."""
        logger.info("Mise en pause de la simulation.")
        with QMutexLocker(self._mutex):
            self._en_pause = True

    @pyqtSlot()
    def reprendre(self):
        """Reprend la simulation après une pause."""
        logger.info("Reprise de la simulation.")
        with QMutexLocker(self._mutex):
            self._en_pause = False

    @pyqtSlot(str)
    def changer_vitesse(self, multiplicateur: str):
        """Ajuste le multiplicateur de vitesse avec validation."""
        with QMutexLocker(self._mutex):
            try:
                valeur = int(multiplicateur)
                # Limitation raisonnable du multiplicateur
                self._multiplicateur_cycle = max(1, min(valeur, 10000))

                logger.info(f"Vitesse ajustée à x{self._multiplicateur_cycle}")

                # Avertissement pour vitesses très élevées
                if self._multiplicateur_cycle > 1000:
                    logger.warning(
                        "Vitesse très élevée : risque d'instabilité numérique"
                    )

            except (ValueError, TypeError):
                logger.warning(
                    f"Valeur de vitesse invalide : '{multiplicateur}', conservation de x{self._multiplicateur_cycle}"
                )

    @pyqtSlot()
    def sauvegarder_maintenant(self):
        """Sauvegarde manuelle avec pause temporaire et feedback détaillé."""
        logger.info("Sauvegarde manuelle demandée...")

        # Pause temporaire thread-safe
        with QMutexLocker(self._mutex):
            en_pause_avant = self._en_pause
            self._en_pause = True

        # Attente stabilisation
        time.sleep(0.2)

        try:
            archiviste = self.gestionnaire_agents.agents_charges.get("archiviste")
            if archiviste:
                # Tentative de sauvegarde avec métriques
                temps_debut = time.time()
                succes = archiviste.archiviste(self.etatmonde, "sauvegarder")
                duree_sauvegarde = time.time() - temps_debut

                if succes:
                    message = (
                        f"Univers sauvegardé avec succès au Temps: {self.etatmonde.temps} "
                        f"({duree_sauvegarde:.2f}s, {len(self.etatmonde._index_entites)} entités)"
                    )
                    logger.info(message)
                else:
                    message = "Échec de la sauvegarde (vérifiez l'espace disque)"
                    logger.error(message)

                self.sauvegardeEffectuee.emit(succes, message)
            else:
                message = "Agent Archiviste non disponible"
                logger.error(message)
                self.sauvegardeEffectuee.emit(False, message)

        except Exception as e:
            message = f"Erreur inattendue lors de la sauvegarde : {e}"
            logger.error(message)
            self.sauvegardeEffectuee.emit(False, message)

        finally:
            # Restauration de l'état de pause
            with QMutexLocker(self._mutex):
                self._en_pause = en_pause_avant

    @pyqtSlot()
    def obtenir_etat_simulation(self) -> Dict[str, Any]:
        """Retourne l'état détaillé de la simulation pour debug."""
        with QMutexLocker(self._mutex):
            return {
                "en_marche": self._en_marche,
                "en_pause": self._en_pause,
                "multiplicateur_cycle": self._multiplicateur_cycle,
                "cycle_actuel": self._cycle_actuel,
                "temps_univers": self.etatmonde.temps,
                "total_entites": sum(
                    len(cat) for cat in self.etatmonde.entites.values()
                ),
                "file_etats_taille": self.file_etats.qsize(),
                "agents_charges": len(self.gestionnaire_agents.agents_charges),
                "agents_actifs": len(
                    [
                        m
                        for m in self.gestionnaire_agents.metriques.values()
                        if m.etat == EtatAgent.ACTIF
                    ]
                ),
                "performance": self.metriques_simulation.copy(),
            }

    @pyqtSlot(str)
    def reactiver_agent(self, nom_agent: str):
        """Réactive manuellement un agent désactivé."""
        if nom_agent in self.gestionnaire_agents.agents_desactives:
            self.gestionnaire_agents.agents_desactives.remove(nom_agent)
            if nom_agent in self.gestionnaire_agents.metriques:
                self.gestionnaire_agents.metriques[nom_agent].etat = EtatAgent.ACTIF
                self.gestionnaire_agents.metriques[nom_agent].erreurs_consecutives = 0
                logger.info(f"Agent '{nom_agent}' réactivé manuellement")
