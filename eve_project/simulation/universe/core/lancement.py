# Fichier : lancement.py
# Version 11.0 ("Orchestrateur Robuste") - Architecture modulaire et gestion d'erreurs avancée

"""
Orchestrateur principal de l'application Projet Monde.
Architecture refactorisée avec séparation des responsabilités, diagnostic approfondi
et gestion d'erreurs robuste. Configuration flexible et monitoring avancé.
"""

import sys
import os
import logging
import signal
import argparse
import json
import traceback
from typing import Optional, Dict, Any, List, Tuple, Union
from queue import Queue
from multiprocessing import freeze_support
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMessageBox, QProgressDialog, QSplashScreen
from PyQt6.QtGui import QPixmap

# ========================================================================
# CONFIGURATION ET ÉNUMÉRATIONS
# ========================================================================


class NiveauLog(Enum):
    """Niveaux de logging disponibles."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EtatApplication(Enum):
    """États possibles de l'application."""

    INITIALISATION = "initialisation"
    DEMARRAGE = "demarrage"
    EXECUTION = "execution"
    PAUSE = "pause"
    FERMETURE = "fermeture"
    ERREUR = "erreur"


@dataclass
class ConfigurationApplication:
    """Configuration centralisée de l'application."""

    # Simulation
    type_univers: str = "BIG_BANG_CLASSIQUE"
    forcer_nouveau: bool = False
    univers_personnalise: Optional[Dict[str, Any]] = None

    # Interface
    fps_interface: int = 60
    intervalle_sauvegarde_minutes: int = 30
    intervalle_surveillance_secondes: int = 5
    taille_queue: int = 15

    # Système
    niveau_log: NiveauLog = NiveauLog.INFO
    diagnostic_startup: bool = True
    backup_multiple: bool = True
    backup_fermeture: bool = True
    redemarrage_auto: bool = False

    # Performance
    limite_entites_interface: int = 50000
    monitoring_ressources: bool = True
    optimisation_auto: bool = True


# ========================================================================
# GESTIONNAIRE DE CONFIGURATION
# ========================================================================


class GestionnaireConfiguration:
    """Gestionnaire centralisé de la configuration avec validation."""

    def __init__(self):
        """TODO: Add docstring."""
        self.config_par_defaut = self._obtenir_config_defaut()
        self.config_actuelle: Optional[ConfigurationApplication] = None

    def _obtenir_config_defaut(self) -> Dict[str, Any]:
        """Retourne la configuration par défaut."""
        return {
            "type_univers": "BIG_BANG_CLASSIQUE",
            "niveau_log": "INFO",
            "fps_interface": 60,
            "intervalle_sauvegarde_minutes": 30,
            "intervalle_surveillance_secondes": 5,
            "diagnostic_startup": True,
            "backup_multiple": True,
            "backup_fermeture": True,
            "redemarrage_auto": False,
            "taille_queue": 15,
            "monitoring_ressources": True,
            "optimisation_auto": True,
        }

    def charger_configuration(
        self, fichier_config: str = "config.json"
    ) -> ConfigurationApplication:
        """Charge et valide la configuration depuis un fichier."""
        config_finale = self.config_par_defaut.copy()

        # Chargement du fichier de configuration
        if Path(fichier_config).exists():
            try:
                with open(fichier_config, "r", encoding="utf-8") as f:
                    config_fichier = json.load(f)

                # Fusion avec validation
                config_finale.update(self._valider_config(config_fichier))

            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"ERREUR: Configuration {fichier_config} invalide: {e}")
                print("Utilisation de la configuration par défaut.")
            except Exception as e:
                print(f"ERREUR: Problème lecture configuration: {e}")

        # Conversion en dataclass
        try:
            self.config_actuelle = ConfigurationApplication(**config_finale)
            return self.config_actuelle
        except TypeError as e:
            print(f"ERREUR: Configuration invalide pour dataclass: {e}")
            return ConfigurationApplication()

    def _valider_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les valeurs de configuration."""
        config_validee = {}

        # Validation des valeurs numériques
        validations = {
            "fps_interface": (lambda x: max(1, min(120, int(x))), 60),
            "intervalle_sauvegarde_minutes": (lambda x: max(1, min(180, int(x))), 30),
            "taille_queue": (lambda x: max(5, min(100, int(x))), 15),
        }

        for cle, (validateur, defaut) in validations.items():
            if cle in config:
                try:
                    config_validee[cle] = validateur(config[cle])
                except (ValueError, TypeError):
                    config_validee[cle] = defaut
            else:
                config_validee[cle] = defaut

        # Validation des booléens
        for cle in ["diagnostic_startup", "backup_multiple", "redemarrage_auto"]:
            if cle in config:
                config_validee[cle] = bool(config[cle])

        # Validation niveau de log
        if "niveau_log" in config:
            try:
                NiveauLog(config["niveau_log"].upper())
                config_validee["niveau_log"] = config["niveau_log"].upper()
            except ValueError:
                config_validee["niveau_log"] = "INFO"

        return config_validee

    def appliquer_arguments_cli(
        self, config: ConfigurationApplication, args: argparse.Namespace
    ) -> ConfigurationApplication:
        """Applique les arguments CLI par-dessus la configuration."""
        if args.type:
            config.type_univers = args.type.upper()
        if args.nouveau:
            config.forcer_nouveau = True
        if args.fps:
            config.fps_interface = max(1, min(120, args.fps))
        if args.log_level:
            config.niveau_log = NiveauLog(args.log_level)

        return config


# ========================================================================
# SYSTÈME DE DIAGNOSTIC AVANCÉ
# ========================================================================


class DiagnosticSysteme:
    """Diagnostic système complet avec rapports détaillés."""

    """TODO: Add docstring."""
    def __init__(self):
        self.derniere_verification: Optional[float] = None
        self.cache_dependances: Optional[Dict[str, bool]] = None

    def verifier_dependances_critiques(self) -> Tuple[bool, Dict[str, bool]]:
        """Vérifie les dépendances critiques pour démarrage."""
        if self.cache_dependances:
            return self._evaluer_dependances(self.cache_dependances)

        dependances = {}

        # Dépendances Python absolument critiques
        modules_critiques = {
            "numpy": "Calculs scientifiques haute performance",
            "PyQt6": "Interface graphique moderne",
            "PyQt6.QtCore": "Système de signaux Qt",
            "PyQt6.QtWidgets": "Widgets d'interface",
        }

        for module, description in modules_critiques.items():
            try:
                __import__(module)
                dependances[module] = True
            except ImportError:
                dependances[module] = False
                print(f"CRITIQUE: {module} manquant - {description}")

        # Dépendances recommandées
        modules_recommandes = {
            "scipy": "Optimisations calculs gravitationnels",
            "psutil": "Monitoring ressources système",
            "numba": "Compilation JIT pour performance",
        }

        for module, description in modules_recommandes.items():
            try:
                __import__(module)
                dependances[module] = True
            except ImportError:
                dependances[module] = False
                print(f"RECOMMANDÉ: {module} manquant - {description}")

        # Modules d'agents du projet
        modules_agents = [
            "etatmonde",
            "simulateur",
            "interface",
            "generateurmonde",
            "agents_physiques",
            "agents_complexes",
            "agents_emergents",
        ]

        for module in modules_agents:
            try:
                __import__(module)
                dependances[f"module_{module}"] = True
            except ImportError as e:
                dependances[f"module_{module}"] = False
                print(f"ERREUR MODULE: {module} - {e}")

        self.cache_dependances = dependances
        return self._evaluer_dependances(dependances)

    def _evaluer_dependances(
        self, deps: Dict[str, bool]
    ) -> Tuple[bool, Dict[str, bool]]:
        """Évalue si les dépendances permettent un démarrage."""
        # Dépendances critiques absolues
        critiques = ["numpy", "PyQt6", "module_etatmonde", "module_simulateur"]

        critiques_manquantes = [
            dep for dep in critiques if dep in deps and not deps[dep]
        ]

        peut_demarrer = len(critiques_manquantes) == 0
        return peut_demarrer, deps

    def verifier_ressources_systeme(self) -> Dict[str, Any]:
        """Vérifie les ressources système avec recommandations."""
        try:
            import psutil

            memoire = psutil.virtual_memory()
            disque = psutil.disk_usage(".")

            ressources = {
                "memoire_totale_gb": memoire.total / (1024**3),
                "memoire_disponible_gb": memoire.available / (1024**3),
                "memoire_pourcentage": memoire.percent,
                "cpu_count": psutil.cpu_count(),
                "cpu_frequence": (
                    psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
                ),
                "espace_disque_libre_gb": disque.free / (1024**3),
                "espace_disque_total_gb": disque.total / (1024**3),
            }

            # Analyse des ressources
            ressources["recommandations"] = []

            if ressources["memoire_disponible_gb"] < 2.0:
                ressources["recommandations"].append(
                    "⚠️ Mémoire faible (<2GB) - Réduisez le nombre d'entités"
                )

            if ressources["espace_disque_libre_gb"] < 1.0:
                ressources["recommandations"].append(
                    "⚠️ Espace disque faible (<1GB) - Nettoyez les backups"
                )

            if ressources["cpu_count"] < 4:
                ressources["recommandations"].append(
                    "ℹ️ CPU limité - Désactivez la parallélisation"
                )

            return ressources

        except ImportError:
            return {
                "erreur": "psutil non disponible",
                "recommandations": ["Installez psutil pour monitoring ressources"],
            }
        except Exception as e:
            return {
                "erreur": f"Erreur vérification ressources: {e}",
                "recommandations": [],
            }

    def generer_rapport_complet(self) -> str:
        """Génère un rapport diagnostic complet."""
        peut_demarrer, deps = self.verifier_dependances_critiques()

        rapport = "=" * 50 + "\n"
        rapport += "DIAGNOSTIC SYSTÈME PROJET MONDE v11.0\n"
        rapport += "=" * 50 + "\n"

        # Informations système
        rapport += f"Python: {sys.version}\n"
        rapport += f"Plateforme: {sys.platform}\n"
        rapport += f"Répertoire: {os.getcwd()}\n\n"

        # État des dépendances
        rapport += "DÉPENDANCES:\n"
        rapport += "-" * 20 + "\n"

        for dep, disponible in sorted(deps.items()):
            statut = "✓ OK" if disponible else "✗ MANQUANT"
            niveau = "CRITIQUE" if dep in ["numpy", "PyQt6"] else "NORMAL"
            rapport += f"  {dep:25} {statut:10} ({niveau})\n"

        # Ressources système
        rapport += "\nRESSORCES SYSTÈME:\n"
        rapport += "-" * 20 + "\n"

        ressources = self.verifier_ressources_systeme()
        if "erreur" not in ressources:
            rapport += f"  RAM disponible: {ressources['memoire_disponible_gb']:.1f} GB / {ressources['memoire_totale_gb']:.1f} GB ({ressources['memoire_pourcentage']:.1f}%)\n"
            rapport += f"  CPU cores: {ressources['cpu_count']}\n"
            rapport += (
                f"  Disque libre: {ressources['espace_disque_libre_gb']:.1f} GB\n"
            )

            if ressources["recommandations"]:
                rapport += "\nRECOMMANDATIONS:\n"
                for rec in ressources["recommandations"]:
                    rapport += f"  {rec}\n"
        else:
            rapport += f"  Erreur: {ressources['erreur']}\n"

        # Conclusion
        rapport += "\n" + "=" * 50 + "\n"
        if peut_demarrer:
            rapport += "STATUT: ✓ PRÊT POUR DÉMARRAGE\n"
        else:
            rapport += "STATUT: ✗ DÉPENDANCES MANQUANTES - IMPOSSIBLE DE DÉMARRER\n"
        rapport += "=" * 50

        return rapport


# ========================================================================
# GESTIONNAIRE DE LOGGING AVANCÉ
# ========================================================================


class GestionnaireLogging:
    """Gestionnaire centralisé du système de logging."""

    @staticmethod
    def configurer_logging(
        niveau: Union[str, NiveauLog] = NiveauLog.INFO,
        fichier_log: str = "monde.log",
        rotation: bool = True,
    ) -> logging.Logger:
        """Configure le système de logging avec options avancées."""

        # Conversion du niveau
        if isinstance(niveau, str):
            try:
                niveau_enum = NiveauLog(niveau.upper())
            except ValueError:
                niveau_enum = NiveauLog.INFO
        else:
            niveau_enum = niveau

        niveau_logging = getattr(logging, niveau_enum.value)

        # Configuration des handlers
        handlers = []

        # Handler fichier
        try:
            file_handler = logging.FileHandler(fichier_log, mode="w", encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - [%(levelname)8s] - %(name)s:%(lineno)d - %(message)s"
                )
            )
            handlers.append(file_handler)
        except Exception as e:
            print(f"ATTENTION: Impossible de créer le fichier de log: {e}")

        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
        )
        handlers.append(console_handler)

        # Configuration finale
        logging.basicConfig(level=niveau_logging, handlers=handlers, force=True)

        # Logger principal
        main_logger = logging.getLogger("projet_monde")
        main_logger.info(f"Logging configuré - Niveau: {niveau_enum.value}")

        return main_logger


# ========================================================================
# FACTORY POUR CRÉATION D'OBJETS
# ========================================================================


class FactoryComposants:
    """Factory pour créer les composants de l'application de manière robuste."""
        """TODO: Add docstring."""

    def __init__(self, config: ConfigurationApplication, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def creer_univers(self) -> Optional["EtatMonde"]:
        """Crée ou charge un univers selon la configuration."""
        # Import sécurisé après configuration du logging
        try:
            from agents_physiques import Archiviste
        except ImportError:
            try:
                from agents import Archiviste
            except ImportError:
                self.logger.warning("Archiviste non disponible")
                Archiviste = None

        # Tentative de chargement d'un univers existant
        if Archiviste and not self.config.forcer_nouveau:
            try:
                archiviste = Archiviste()
                etatmonde = archiviste.archiviste(instruction="charger")
                if etatmonde is not None:
                    self.logger.info(
                        f"Univers existant chargé (Temps: {etatmonde.temps})"
                    )
                    return etatmonde
            except Exception as e:
                self.logger.warning(f"Échec chargement univers existant: {e}")

        # Création d'un nouvel univers
        return self._creer_nouvel_univers()

    def _creer_nouvel_univers(self) -> Optional["EtatMonde"]:
        """Crée un nouvel univers selon le type configuré."""
        try:
            from generateurmonde import (
                creerbigbang,
                TypeUnivers,
                creer_univers_personnalise,
            )

            type_univers_str = self.config.type_univers

            # Validation du type d'univers
            try:
                type_univers = TypeUnivers(type_univers_str.lower())
            except ValueError:
                self.logger.warning(
                    f"Type d'univers inconnu '{type_univers_str}', "
                    "utilisation du Big Bang classique"
                )
                type_univers = TypeUnivers.BIG_BANG_CLASSIQUE

            # Création selon le type
            if self.config.univers_personnalise:
                self.logger.info("Création d'un univers personnalisé...")
                etatmonde = creer_univers_personnalise(self.config.univers_personnalise)
            else:
                self.logger.info(f"Création d'un nouvel univers : {type_univers.value}")
                etatmonde = creerbigbang(type_univers)

            return etatmonde

        except ImportError as e:
            self.logger.critical(f"Modules de génération non disponibles: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur création univers: {e}")
            return None

    def creer_simulateur(
        self, etatmonde: "EtatMonde", file_etats: Queue
    ) -> Optional["Simulateur"]:
        """Crée le simulateur avec configuration adaptée."""
        try:
            from simulateur import Simulateur, ConfigurationSimulateur

            # Configuration du simulateur selon les ressources
            config_sim = ConfigurationSimulateur()

            # Adaptation selon monitoring ressources
            if self.config.monitoring_ressources:
                diagnostic = DiagnosticSysteme()
                ressources = diagnostic.verifier_ressources_systeme()

                if "memoire_disponible_gb" in ressources:
                    if ressources["memoire_disponible_gb"] < 4.0:
                        config_sim.limite_entites_performance = 10000
                        self.logger.info("Mémoire limitée: réduction limite entités")

            return Simulateur(etatmonde, file_etats, config_sim)

        except ImportError as e:
            self.logger.critical(f"Module simulateur non disponible: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur création simulateur: {e}")
            return None

    def creer_interface(self) -> Optional["FenetrePrincipale"]:
        """Crée l'interface principale avec gestion d'erreurs."""
        try:
            from interface import FenetrePrincipale

            return FenetrePrincipale()
        except ImportError as e:
            self.logger.critical(f"Module interface non disponible: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur création interface: {e}")
            return None


# ========================================================================
# GESTIONNAIRE DE TIMERS
# ========================================================================


class GestionnaireTimers:
    """TODO: Add docstring."""
    """Gestionnaire centralisé des timers avec configuration flexible."""

    def __init__(
        self, parent: QObject, config: ConfigurationApplication, logger: logging.Logger
    ):
        self.parent = parent
        self.config = config
        self.logger = logger
        self.timers: Dict[str, QTimer] = {}

    def configurer_timer_affichage(self, callback) -> None:
        """Configure le timer d'affichage selon la configuration."""
        fps_cible = self.config.fps_interface
        intervalle_ms = max(16, int(1000 / fps_cible))  # Minimum 16ms (60 FPS max)

        timer = QTimer(self.parent)
        timer.timeout.connect(callback)
        timer.start(intervalle_ms)

        self.timers["affichage"] = timer
        self.logger.info(f"Timer affichage: {fps_cible} FPS ({intervalle_ms}ms)")

    def configurer_timer_sauvegarde(self, callback) -> None:
        """Configure le timer de sauvegarde automatique."""
        intervalle_minutes = self.config.intervalle_sauvegarde_minutes
        intervalle_ms = intervalle_minutes * 60 * 1000

        timer = QTimer(self.parent)
        timer.timeout.connect(callback)
        timer.start(intervalle_ms)

        self.timers["sauvegarde"] = timer
        self.logger.info(f"Sauvegarde automatique: {intervalle_minutes} minutes")

    def configurer_timer_surveillance(self, callback) -> None:
        """Configure le timer de surveillance système."""
        intervalle_secondes = self.config.intervalle_surveillance_secondes
        intervalle_ms = intervalle_secondes * 1000

        timer = QTimer(self.parent)
        timer.timeout.connect(callback)
        timer.start(intervalle_ms)

        self.timers["surveillance"] = timer
        self.logger.debug(f"Surveillance système: {intervalle_secondes}s")

    def arreter_tous_timers(self) -> None:
        """Arrête tous les timers proprement."""
        for nom, timer in self.timers.items():
            if timer and timer.isActive():
                timer.stop()
                self.logger.debug(f"Timer {nom} arrêté")


# ========================================================================
# APPLICATION PRINCIPALE REFACTORISÉE
# ========================================================================


    """TODO: Add docstring."""
class Application(QObject):
    """Application principale avec architecture modulaire et monitoring avancé."""

    def __init__(self, app: QApplication, config: ConfigurationApplication):
        super().__init__()
        self.app = app
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.Application")

        # État de l'application
        self.etat = EtatApplication.INITIALISATION
        self.fermeture_en_cours = False

        # Composants principaux
        self.file_etats: Optional[Queue] = None
        self.thread_simulation: Optional[QThread] = None
        self.simulateur: Optional["Simulateur"] = None
        self.fenetre: Optional["FenetrePrincipale"] = None

        # Gestionnaires
        self.factory = FactoryComposants(config, self.logger)
        self.gestionnaire_timers: Optional[GestionnaireTimers] = None

        # Diagnostic
        self.diagnostic = DiagnosticSysteme()

    def initialiser(self) -> bool:
        """Initialise tous les composants avec diagnostic et validation."""
        self.logger.info("Début d'initialisation de l'application...")

        try:
            # Phase 1: Diagnostic système
            if not self._executer_diagnostic_startup():
                return False

            # Phase 2: Création des composants core
            if not self._creer_composants_principaux():
                return False

            # Phase 3: Configuration des connexions
            if not self._configurer_connexions():
                return False

            # Phase 4: Configuration des timers
            self._configurer_gestionnaire_timers()

            self.etat = EtatApplication.DEMARRAGE
            self.logger.info("Initialisation réussie")
            return True

        except Exception as e:
            self.logger.critical("Erreur fatale initialisation", exc_info=True)
            self._afficher_erreur_fatale(e)
            return False

    def _executer_diagnostic_startup(self) -> bool:
        """Exécute le diagnostic de démarrage."""
        if not self.config.diagnostic_startup:
            return True

        self.logger.info("Exécution du diagnostic système...")

        peut_demarrer, deps = self.diagnostic.verifier_dependances_critiques()

        if not peut_demarrer:
            deps_critiques_manquantes = [
                dep
                for dep in ["numpy", "PyQt6", "module_etatmonde"]
                if dep in deps and not deps[dep]
            ]

            self.logger.critical(
                f"Dépendances critiques manquantes: {deps_critiques_manquantes}"
            )
            return False

        # Vérification ressources
        ressources = self.diagnostic.verifier_ressources_systeme()
        if "memoire_disponible_gb" in ressources:
            if ressources["memoire_disponible_gb"] < 1.0:
                self.logger.warning(
                    "Mémoire très faible, problèmes de performance possibles"
                )

        return True

    def _creer_composants_principaux(self) -> bool:
        """Crée les composants principaux de l'application."""
        try:
            # File d'états
            self.file_etats = Queue(maxsize=self.config.taille_queue)

            # Création de l'univers
            etatmonde = self.factory.creer_univers()
            if etatmonde is None:
                self.logger.error("Impossible de créer ou charger un univers")
                return False

            # Création du simulateur
            self.simulateur = self.factory.creer_simulateur(etatmonde, self.file_etats)
            if self.simulateur is None:
                self.logger.error("Impossible de créer le simulateur")
                return False

            # Création de l'interface
            self.fenetre = self.factory.creer_interface()
            if self.fenetre is None:
                self.logger.error("Impossible de créer l'interface")
                return False

            # Thread de simulation
            self.thread_simulation = QThread(self)
            self.simulateur.moveToThread(self.thread_simulation)

            self.logger.info("Composants principaux créés avec succès")
            return True

        except Exception as e:
            self.logger.error(f"Erreur création composants: {e}")
            return False

    def _configurer_connexions(self) -> bool:
        """Configure toutes les connexions de signaux."""
        try:
            if not all([self.thread_simulation, self.simulateur, self.fenetre]):
                self.logger.error("Composants manquants pour connexions")
                return False

            # Connexion thread
            self.thread_simulation.started.connect(self.simulateur.lancerboucle)

            # Connexions de contrôle
            self.fenetre.pause_demandee.connect(self._on_pause_demandee)
            self.fenetre.reprise_demandee.connect(self._on_reprise_demandee)
            self.fenetre.vitesse_changee.connect(self._on_vitesse_changee)
            self.fenetre.sauvegarde_demandee.connect(self._on_sauvegarde_demandee)

            # Signal de sauvegarde
            self.simulateur.sauvegardeEffectuee.connect(
                self.fenetre.afficher_notification_sauvegarde
            )

            # Signal de fermeture
            self.app.aboutToQuit.connect(self.fermeture_propre)

            self.logger.info("Connexions configurées")
            return True

        except Exception as e:
            self.logger.error(f"Erreur configuration connexions: {e}")
            return False

    def _configurer_gestionnaire_timers(self) -> None:
        """Configure le gestionnaire de timers."""
        self.gestionnaire_timers = GestionnaireTimers(self, self.config, self.logger)

    def executer(self) -> None:
        """Lance l'application avec monitoring complet."""
        if not all([self.thread_simulation, self.fenetre, self.simulateur]):
            self.logger.error("Tentative d'exécution avec composants manquants")
            return

        self.logger.info("Démarrage de l'application...")
        self.etat = EtatApplication.EXECUTION

        # Démarrage des composants
        self.thread_simulation.start()
        self.fenetre.show()

        # Configuration des timers
        if self.gestionnaire_timers:
            self.gestionnaire_timers.configurer_timer_affichage(
                self._mettre_a_jour_interface
            )
            self.gestionnaire_timers.configurer_timer_sauvegarde(
                self._on_sauvegarde_automatique
            )
            self.gestionnaire_timers.configurer_timer_surveillance(
                self._verifier_simulation
            )

        self.logger.info("Application démarrée avec succès")

    # ========================================================================
    # GESTIONNAIRES D'ÉVÉNEMENTS
    # ========================================================================

    @pyqtSlot()
    def _on_pause_demandee(self) -> None:
        """Gestionnaire de demande de pause."""
        self.logger.info("Pause demandée par l'interface")
        self.etat = EtatApplication.PAUSE
        if self.simulateur:
            self.simulateur.mettre_en_pause()

    @pyqtSlot()
    def _on_reprise_demandee(self) -> None:
        """Gestionnaire de demande de reprise."""
        self.logger.info("Reprise demandée par l'interface")
        self.etat = EtatApplication.EXECUTION
        if self.simulateur:
            self.simulateur.reprendre()

    @pyqtSlot(str)
    def _on_vitesse_changee(self, vitesse: str) -> None:
        """Gestionnaire de changement de vitesse."""
        self.logger.info(f"Changement vitesse demandé: x{vitesse}")
        if self.simulateur:
            self.simulateur.changer_vitesse(vitesse)

    @pyqtSlot()
    def _on_sauvegarde_demandee(self) -> None:
        """Gestionnaire de sauvegarde manuelle."""
        self.logger.info("Sauvegarde manuelle demandée")
        if self.simulateur:
            self.simulateur.sauvegarder_maintenant()

    def _on_sauvegarde_automatique(self) -> None:
        """Gestionnaire de sauvegarde automatique."""
        if self.etat != EtatApplication.EXECUTION:
            return

        self.logger.info("Sauvegarde automatique...")
        try:
            if self.simulateur:
                self.simulateur.sauvegarder_maintenant()

                # Backup additionnel si configuré
                if self.config.backup_multiple:
                    self._creer_backup_securite()

        except Exception as e:
            self.logger.error(f"Erreur sauvegarde automatique: {e}")

    def _mettre_a_jour_interface(self) -> None:
        """Met à jour l'interface avec optimisations."""
        if not self.file_etats or not self.fenetre:
            return

        try:
            # Consommation optimisée de la queue
            if not self.file_etats.empty():
                etat_json = self.file_etats.get_nowait()
                self.fenetre.mise_a_jour(etat_json)  # Nouvelle API

                # Vider queue si accumulation
                compteur = 0
                while not self.file_etats.empty() and compteur < 5:
                    try:
                        self.file_etats.get_nowait()
                        compteur += 1
                    except:
                        break

        except Exception as e:
            self.logger.debug(f"Erreur mineure mise à jour interface: {e}")

    def _verifier_simulation(self) -> None:
        """Surveillance avancée de la simulation."""
        try:
            # Vérification thread
            if not self.thread_simulation or not self.thread_simulation.isRunning():
                self.logger.error("Thread simulation arrêté de manière inattendue")
                self._gerer_arret_thread()
                return

            # Métriques de performance
            if self.file_etats:
                taille_queue = self.file_etats.qsize()
                if taille_queue > self.config.taille_queue * 0.8:
                    self.logger.warning(
                        f"Queue saturée: {taille_queue}/{self.config.taille_queue}"
                    )

        except Exception as e:
            self.logger.error(f"Erreur surveillance: {e}")

    def _gerer_arret_thread(self) -> None:
        """Gère l'arrêt inopiné du thread de simulation."""
        if self.config.redemarrage_auto and not self.fermeture_en_cours:
            self.logger.info("Tentative de redémarrage automatique...")
            try:
                self.thread_simulation = QThread(self)
                if self.simulateur:
                    self.simulateur.moveToThread(self.thread_simulation)
                    self.thread_simulation.started.connect(self.simulateur.lancerboucle)
                    self.thread_simulation.start()
                    self.logger.info("Thread redémarré avec succès")
            except Exception as e:
                self.logger.error(f"Échec redémarrage: {e}")
                self.app.quit()
        else:
            self.app.quit()

    def _creer_backup_securite(self) -> None:
        """Crée un backup de sécurité horodaté."""
        try:
            from datetime import datetime
            import shutil

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            if Path("memoire.monde").exists():
                backup_path = backup_dir / f"memoire_backup_{timestamp}.monde"
                shutil.copy2("memoire.monde", backup_path)
                self.logger.debug(f"Backup créé: {backup_path.name}")

        except Exception as e:
            self.logger.warning(f"Échec création backup: {e}")

    def _afficher_erreur_fatale(self, erreur: Exception) -> None:
        """Affiche une erreur fatale avec diagnostic."""
        diagnostic = self.diagnostic.generer_rapport_complet()

        QMessageBox.critical(
            None,
            "Erreur Fatale - Projet Monde",
            f"L'application ne peut pas démarrer:\n\n{erreur}\n\n"
            f"Consultez le fichier monde.log pour plus de détails.\n\n"
            f"Diagnostic:\n{diagnostic[:300]}...",
        )

    def fermeture_propre(self) -> None:
        """Séquence de fermeture propre avec sauvegarde."""
        if self.fermeture_en_cours:
            return

        self.fermeture_en_cours = True
        self.etat = EtatApplication.FERMETURE
        self.logger.info("Début fermeture propre...")

        try:
            # Arrêt des timers
            if self.gestionnaire_timers:
                self.gestionnaire_timers.arreter_tous_timers()

            # Sauvegarde finale
            if self.simulateur:
                self.logger.info("Sauvegarde finale...")
                self.simulateur.arreter()
                self.simulateur.sauvegarder_maintenant()

                if self.config.backup_fermeture:
                    self._creer_backup_securite()

            # Arrêt thread simulation
            if self.thread_simulation:
                self.thread_simulation.quit()
                if not self.thread_simulation.wait(3000):
                    self.logger.warning("Forçage arrêt thread simulation")
                    self.thread_simulation.terminate()
                    self.thread_simulation.wait(1000)

            self.logger.info("Fermeture propre terminée")

        except Exception as e:
            self.logger.error(f"Erreur pendant fermeture: {e}")


# ========================================================================
# UTILITAIRES
# ========================================================================


def parse_arguments() -> argparse.Namespace:
    """Parse et valide les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Projet Monde v11.0 - Simulateur d'Univers Avancé",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python lancement.py                          # Démarrage standard
  python lancement.py --nouveau --type chaos_primordial  # Nouvel univers chaotique
  python lancement.py --diagnostic             # Diagnostic système
  python lancement.py --fps 30 --config test.json       # Configuration personnalisée
        """,
    )

    # Import sécurisé pour les choix
    try:
        from generateurmonde import TypeUnivers

        types_disponibles = [t.value for t in TypeUnivers]
    except ImportError:
        types_disponibles = ["bigbang_classique", "univers_mature"]

    parser.add_argument(
        "--type", choices=types_disponibles, help="Type d'univers à créer"
    )
    parser.add_argument(
        "--nouveau", action="store_true", help="Force la création d'un nouvel univers"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Fichier de configuration (défaut: config.json)",
    )
    parser.add_argument(
        "--log-level",
        choices=[niveau.value for niveau in NiveauLog],
        default="INFO",
        help="Niveau de logging (défaut: INFO)",
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Affiche le diagnostic système et quitte",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        metavar="N",
        help="FPS cible de l'interface (1-120, défaut: 60)",
    )
    parser.add_argument("--version", action="version", version="Projet Monde v11.0")

    args = parser.parse_args()

    # Validation des arguments
    if args.fps:
        args.fps = max(1, min(120, args.fps))

    return args


def afficher_splash_screen(app: QApplication) -> QSplashScreen:
    """Affiche un écran de démarrage pendant l'initialisation."""
    try:
        # Création d'un splash screen simple
        splash = QSplashScreen()
        splash.showMessage(
            "Projet Monde v11.0\nInitialisation en cours...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        )
        splash.show()
        app.processEvents()
        return splash
    except Exception:
        return None


def main() -> int:
    """Point d'entrée principal avec architecture robuste."""
    # Configuration signaux système
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    try:
        # Parse arguments (avant logging pour --diagnostic)
        args = parse_arguments()

        # Configuration logging IMMÉDIATE
        gestionnaire_log = GestionnaireLogging()
        main_logger = gestionnaire_log.configurer_logging(args.log_level, "monde.log")

        main_logger.info("=" * 60)
        main_logger.info("DÉMARRAGE PROJET MONDE v11.0")
        main_logger.info("=" * 60)
        main_logger.info(f"Arguments CLI: {vars(args)}")

        # Diagnostic système si demandé
        if args.diagnostic:
            diagnostic = DiagnosticSysteme()
            rapport = diagnostic.generer_rapport_complet()
            print(rapport)
            return 0

        # Chargement et validation de la configuration
        gestionnaire_config = GestionnaireConfiguration()
        config = gestionnaire_config.charger_configuration(args.config)
        config = gestionnaire_config.appliquer_arguments_cli(config, args)

        main_logger.info(f"Configuration finale: {config}")

        # Création de l'application Qt
        q_app = QApplication(sys.argv)
        q_app.setApplicationName("Projet Monde")
        q_app.setApplicationVersion("11.0")
        q_app.setOrganizationName("Simulation Cosmologique")

        # Splash screen pendant initialisation
        splash = afficher_splash_screen(q_app)

        try:
            # Création et initialisation de l'application
            application = Application(q_app, config)

            if application.initialiser():
                if splash:
                    splash.close()

                main_logger.info("Lancement de la boucle principale Qt...")
                application.executer()

                # Exécution de la boucle Qt
                return q_app.exec()
            else:
                if splash:
                    splash.close()
                main_logger.critical("Échec d'initialisation")
                return 1

        except Exception as e:
            if splash:
                splash.close()
            main_logger.critical("Erreur dans boucle principale", exc_info=True)

            # Diagnostic en cas d'erreur
            diagnostic = DiagnosticSysteme()
            rapport = diagnostic.generer_rapport_complet()

            QMessageBox.critical(
                None,
                "Crash Fatal - Projet Monde",
                f"Erreur fatale:\n{e}\n\n"
                f"Diagnostic:\n{rapport[:400]}...\n\n"
                f"Consultez monde.log pour détails complets.",
            )
            return 1

    except KeyboardInterrupt:
        print("\nInterruption clavier détectée. Fermeture propre...")
        return 0

    except Exception as e:
        print(f"ERREUR CRITIQUE avant configuration logging: {e}")
        traceback.print_exc()
        return 1


# ========================================================================
# POINT D'ENTRÉE AVEC PROTECTION
# ========================================================================

if __name__ == "__main__":
    freeze_support()  # Support multiprocessing Windows

    try:
        exit_code = main()
        sys.exit(exit_code)
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERREUR CATASTROPHIQUE: {e}")
        traceback.print_exc()
        sys.exit(1)