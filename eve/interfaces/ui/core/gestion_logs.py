import logging
import logging.handlers
import time
import threading
import json
import hashlib
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
import queue
from typing import Optional, Dict, List, Any


class ConfigurationLogs:
    """Configuration centralisée pour le système de logs."""

    def __init__(self, config_dict: Dict[str, Any] = None):
        config = config_dict or {}

        # Tailles et limites
        self.taille_max_mo = config.get("taille_max_mo", 2)
        self.nb_fichiers_backup = config.get("nb_fichiers_backup", 5)
        self.taille_max_archive_go = config.get("taille_max_archive_go", 1)
        self.retention_jours = config.get("retention_jours", 30)

        # Intervalles de maintenance
        self.intervalle_verification_sec = config.get(
            "intervalle_verification_sec", 3600
        )
        self.intervalle_synthese_sec = config.get("intervalle_synthese_sec", 86400)
        self.intervalle_nettoyage_sec = config.get("intervalle_nettoyage_sec", 7200)

        # Seuils d'alerte
        self.seuil_synthese_pct = config.get("seuil_synthese_pct", 80)
        self.seuil_alerte_espace_pct = config.get("seuil_alerte_espace_pct", 90)
        self.seuil_erreur_critique = config.get("seuil_erreur_critique", 100)

        # Niveaux de logging
        self.niveau_defaut = getattr(
            logging, config.get("niveau_defaut", "INFO").upper()
        )
        self.niveau_console = getattr(
            logging, config.get("niveau_console", "WARNING").upper()
        )
        self.niveau_fichier = getattr(
            logging, config.get("niveau_fichier", "DEBUG").upper()
        )

        # Options avancées
        self.compression_active = config.get("compression_active", True)
        self.synthese_automatique = config.get("synthese_automatique", True)
        self.monitoring_performance = config.get("monitoring_performance", True)
        self.validation_integrite = config.get("validation_integrite", True)


class MetriquesLogs:
    """Collecte et analyse des métriques de logging."""

    def __init__(self):
        self.compteurs = defaultdict(int)
        self.historique_tailles = deque(maxlen=1440)  # 24h de données par minute
        self.erreurs_recentes = deque(maxlen=100)
        self.dernier_reset = time.time()
        self.verrou = threading.RLock()

    def incrementer(self, metrique: str, valeur: int = 1):
        """Incrémente un compteur de métrique de façon thread-safe."""
        with self.verrou:
            self.compteurs[metrique] += valeur

    def enregistrer_taille(self, taille_mo: float):
        """Enregistre la taille actuelle des logs."""
        with self.verrou:
            self.historique_tailles.append((time.time(), taille_mo))

    def enregistrer_erreur(self, erreur: str):
        """Enregistre une erreur pour analyse."""
        with self.verrou:
            self.erreurs_recentes.append((time.time(), erreur))

    def obtenir_rapport(self) -> Dict[str, Any]:
        """Génère un rapport des métriques."""
        with self.verrou:
            maintenant = time.time()
            duree = maintenant - self.dernier_reset

            return {
                "duree_monitoring_sec": duree,
                "compteurs": dict(self.compteurs),
                "taille_actuelle_mo": (
                    self.historique_tailles[-1][1] if self.historique_tailles else 0
                ),
                "croissance_moyenne_mo_h": self._calculer_croissance_moyenne(),
                "erreurs_recentes": list(self.erreurs_recentes)[-10:],
                "timestamp": maintenant,
            }

    def _calculer_croissance_moyenne(self) -> float:
        """Calcule la croissance moyenne en Mo/h."""
        if len(self.historique_tailles) < 2:
            return 0.0

        premiere = self.historique_tailles[0]
        derniere = self.historique_tailles[-1]
        duree_h = (derniere[0] - premiere[0]) / 3600

        if duree_h <= 0:
            return 0.0

        return (derniere[1] - premiere[1]) / duree_h


class ValidateurLogs:
    """Validation et vérification d'intégrité des fichiers de logs."""

    @staticmethod
    def valider_chemin_fichier(chemin: Path) -> bool:
        """Valide qu'un chemin de fichier est sécurisé."""
        try:
            chemin_resolu = chemin.resolve()
            # Vérifier que le chemin ne remonte pas au-dessus du dossier autorisé
            return str(chemin_resolu).startswith(str(Path.cwd().resolve()))
        except (OSError, ValueError):
            return False

    @staticmethod
    def valider_taille_fichier(chemin: Path, taille_max_mo: float) -> bool:
        """Valide que la taille d'un fichier est dans les limites."""
        try:
            if not chemin.exists():
                return True
            taille_mo = chemin.stat().st_size / (1024 * 1024)
            return taille_mo <= taille_max_mo * 1.1  # Tolérance de 10%
        except (OSError, ValueError):
            return False

    @staticmethod
    def calculer_checksum(chemin: Path) -> Optional[str]:
        """Calcule le checksum MD5 d'un fichier."""
        try:
            hash_md5 = hashlib.md5()
            with open(chemin, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, ValueError):
            return None

    @staticmethod
    def verifier_integrite_logs(dossier: Path) -> List[str]:
        """Vérifie l'intégrité de tous les fichiers de logs."""
        problemes = []

        try:
            for fichier_log in dossier.glob("*.log*"):
                if not fichier_log.is_file():
                    continue

                # Vérifier la lisibilité
                try:
                    with open(fichier_log, "r", encoding="utf-8") as f:
                        f.read(1024)  # Test de lecture
                except UnicodeDecodeError:
                    problemes.append(f"Encodage invalide: {fichier_log}")
                except PermissionError:
                    problemes.append(f"Permissions insuffisantes: {fichier_log}")
                except OSError as e:
                    problemes.append(f"Erreur lecture {fichier_log}: {e}")

        except Exception as e:
            problemes.append(f"Erreur globale vérification: {e}")

        return problemes


class GestionnaireSynthese:
    """Gestion intelligente de la synthèse des logs."""

    def __init__(self, config: ConfigurationLogs):
        self.config = config
        self.patterns_erreur = [
            r"ERROR|CRITICAL|FATAL",
            r"Exception|Traceback",
            r"ERREUR|CRITIQUE",
        ]
        self.patterns_performance = [
            r"temps.*(?P<duree>\d+\.\d+)",
            r"mémoire.*(?P<memoire>\d+)",
            r"performance",
        ]

    def analyser_logs_pour_synthese(self, fichier_log: Path) -> Dict[str, Any]:
        """Analyse un fichier de log pour en extraire les points clés."""
        try:
            statistiques = {
                "total_lignes": 0,
                "erreurs": [],
                "avertissements": [],
                "performances": [],
                "periode": {"debut": None, "fin": None},
            }

            with open(fichier_log, "r", encoding="utf-8") as f:
                for ligne in f:
                    statistiques["total_lignes"] += 1

                    # Extraction de la timestamp
                    if statistiques["debut"] is None:
                        timestamp = self._extraire_timestamp(ligne)
                        if timestamp:
                            statistiques["periode"]["debut"] = timestamp

                    # Analyse des erreurs
                    if any(
                        pattern.lower() in ligne.lower()
                        for pattern in ["error", "erreur", "critical"]
                    ):
                        statistiques["erreurs"].append(ligne.strip()[:200])

                    # Analyse des avertissements
                    elif any(
                        pattern.lower() in ligne.lower()
                        for pattern in ["warning", "warn", "avertissement"]
                    ):
                        statistiques["avertissements"].append(ligne.strip()[:200])

                    # Dernière ligne pour timestamp de fin
                    timestamp_fin = self._extraire_timestamp(ligne)
                    if timestamp_fin:
                        statistiques["periode"]["fin"] = timestamp_fin

            return statistiques

        except Exception as e:
            return {"erreur": f"Impossible d'analyser {fichier_log}: {e}"}

    def _extraire_timestamp(self, ligne: str) -> Optional[str]:
        """Extrait un timestamp d'une ligne de log."""
        import re

        # Format: 2024-01-01 12:00:00
        pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        match = re.search(pattern, ligne)
        return match.group(1) if match else None

    def generer_synthese(self, fichiers_logs: List[Path]) -> str:
        """Génère une synthèse intelligente à partir de plusieurs fichiers."""
        synthese_globale = {
            "periode_analysee": {"debut": None, "fin": None},
            "total_lignes": 0,
            "total_erreurs": 0,
            "total_avertissements": 0,
            "fichiers_analyses": len(fichiers_logs),
            "problemes_frequents": defaultdict(int),
        }

        synthese_texte = "# Synthèse Automatique des Logs\n\n"

        for fichier in fichiers_logs:
            if not fichier.exists():
                continue

            analyse = self.analyser_logs_pour_synthese(fichier)
            if "erreur" in analyse:
                continue

            synthese_globale["total_lignes"] += analyse.get("total_lignes", 0)
            synthese_globale["total_erreurs"] += len(analyse.get("erreurs", []))
            synthese_globale["total_avertissements"] += len(
                analyse.get("avertissements", [])
            )

            # Mise à jour des périodes
            if analyse["periode"]["debut"]:
                if not synthese_globale["periode_analysee"]["debut"]:
                    synthese_globale["periode_analysee"]["debut"] = analyse["periode"][
                        "debut"
                    ]
                else:
                    synthese_globale["periode_analysee"]["debut"] = min(
                        synthese_globale["periode_analysee"]["debut"],
                        analyse["periode"]["debut"],
                    )

            if analyse["periode"]["fin"]:
                synthese_globale["periode_analysee"]["fin"] = max(
                    synthese_globale["periode_analysee"]["fin"] or "",
                    analyse["periode"]["fin"],
                )

        # Construction du texte de synthèse
        synthese_texte += f"## Résumé Exécutif\n\n"
        synthese_texte += f"- **Période analysée**: {synthese_globale['periode_analysee']['debut']} → {synthese_globale['periode_analysee']['fin']}\n"
        synthese_texte += (
            f"- **Fichiers traités**: {synthese_globale['fichiers_analyses']}\n"
        )
        synthese_texte += f"- **Total lignes**: {synthese_globale['total_lignes']:,}\n"
        synthese_texte += (
            f"- **Erreurs détectées**: {synthese_globale['total_erreurs']}\n"
        )
        synthese_texte += (
            f"- **Avertissements**: {synthese_globale['total_avertissements']}\n\n"
        )

        # Évaluation de la santé
        if synthese_globale["total_erreurs"] == 0:
            synthese_texte += "✅ **État**: Aucune erreur critique détectée\n\n"
        elif synthese_globale["total_erreurs"] < 10:
            synthese_texte += (
                "⚠️ **État**: Quelques erreurs détectées, surveillance recommandée\n\n"
            )
        else:
            synthese_texte += (
                "🚨 **État**: Nombreuses erreurs, investigation requise\n\n"
            )

        return synthese_texte


class GestionnaireFichiers:
    """Gestion avancée des fichiers avec compression et archivage."""

    def __init__(self, config: ConfigurationLogs):
        self.config = config
        self.verrou_fichiers = threading.RLock()

    def compresser_fichier(self, chemin_source: Path) -> Optional[Path]:
        """Compresse un fichier avec gzip."""
        if not self.config.compression_active:
            return None

        try:
            chemin_compresse = chemin_source.with_suffix(chemin_source.suffix + ".gz")

            with open(chemin_source, "rb") as f_in:
                with gzip.open(chemin_compresse, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Vérification de l'intégrité après compression
            if self._verifier_compression(chemin_source, chemin_compresse):
                chemin_source.unlink()  # Supprime l'original
                return chemin_compresse
            else:
                chemin_compresse.unlink()  # Supprime la version corrompue
                return None

        except Exception as e:
            print(f"Erreur compression {chemin_source}: {e}")
            return None

    def _verifier_compression(self, original: Path, compresse: Path) -> bool:
        """Vérifie l'intégrité d'un fichier compressé."""
        try:
            taille_originale = original.stat().st_size

            with gzip.open(compresse, "rb") as f:
                taille_decompressee = len(f.read())

            return taille_originale == taille_decompressee
        except Exception:
            return False

    def archiver_avec_metadata(self, fichier: Path, dossier_archive: Path) -> bool:
        """Archive un fichier avec ses métadonnées."""
        try:
            dossier_archive.mkdir(parents=True, exist_ok=True)

            # Génération du nom d'archive avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_archive = f"{fichier.stem}_{timestamp}{fichier.suffix}"
            chemin_archive = dossier_archive / nom_archive

            # Copie du fichier
            shutil.copy2(fichier, chemin_archive)

            # Création des métadonnées
            metadata = {
                "fichier_original": str(fichier),
                "taille_octets": fichier.stat().st_size,
                "checksum": ValidateurLogs.calculer_checksum(fichier),
                "date_archivage": datetime.now().isoformat(),
                "date_creation": datetime.fromtimestamp(
                    fichier.stat().st_ctime
                ).isoformat(),
                "date_modification": datetime.fromtimestamp(
                    fichier.stat().st_mtime
                ).isoformat(),
            }

            metadata_file = chemin_archive.with_suffix(".metadata.json")
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            return True

        except Exception as e:
            print(f"Erreur archivage {fichier}: {e}")
            return False

    def nettoyer_archives_anciennes(self, dossier_archive: Path) -> int:
        """Nettoie les archives anciennes selon la politique de rétention."""
        if not dossier_archive.exists():
            return 0

        compteur_supprime = 0
        limite_date = datetime.now() - timedelta(days=self.config.retention_jours)

        try:
            for fichier in dossier_archive.iterdir():
                if not fichier.is_file():
                    continue

                date_modif = datetime.fromtimestamp(fichier.stat().st_mtime)
                if date_modif < limite_date:
                    try:
                        fichier.unlink()
                        # Supprimer aussi le fichier de métadonnées associé
                        metadata_file = fichier.with_suffix(".metadata.json")
                        if metadata_file.exists():
                            metadata_file.unlink()
                        compteur_supprime += 1
                    except Exception as e:
                        print(f"Impossible de supprimer {fichier}: {e}")

        except Exception as e:
            print(f"Erreur nettoyage archives: {e}")

        return compteur_supprime


class GestionnaireLogsIntelligent:
    """
    Système de logging intelligent ultra-robuste.
    Implémente les Directives 25 et 91 avec haute disponibilité.
    """

    def __init__(self, config_dict: Dict[str, Any] = None):
        self.config = ConfigurationLogs(config_dict)
        self.dossier_logs = Path("logs")
        self.dossier_archive = self.dossier_logs / "archives"
        self.dossier_syntheses = self.dossier_logs / "syntheses"

        # Création des dossiers
        for dossier in [
            self.dossier_logs,
            self.dossier_archive,
            self.dossier_syntheses,
        ]:
            dossier.mkdir(parents=True, exist_ok=True)

        # Composants du système
        self.metriques = MetriquesLogs()
        self.synthese_manager = GestionnaireSynthese(self.config)
        self.fichiers_manager = GestionnaireFichiers(self.config)

        # État du système
        self.logger_principal = None
        self.loggers_specialises = {}
        self.threads_maintenance = []
        self.queue_alertes = queue.Queue()
        self.actif = False
        self.derniere_maintenance = time.time()

        # Verrous et synchronisation
        self.verrou_principal = threading.RLock()
        self.verrou_maintenance = threading.Lock()

    def configurer_logging(self, niveau: int = None) -> bool:
        """
        Configure le système de logging avec toutes les sécurités.
        """
        try:
            with self.verrou_principal:
                niveau = niveau or self.config.niveau_defaut

                # Nettoyage des handlers existants
                self._nettoyer_handlers_existants()

                # Configuration du logger principal
                self.logger_principal = logging.getLogger("simulateur")
                self.logger_principal.setLevel(niveau)

                # Formatter avec métadonnées enrichies
                formatter = logging.Formatter(
                    "%(asctime)s | %(levelname)-8s | %(name)s | PID:%(process)d | %(funcName)s:%(lineno)d | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )

                # Configuration des handlers sécurisés
                success = self._configurer_handlers_securises(formatter)
                if not success:
                    return False

                # Création des loggers spécialisés
                self._creer_loggers_specialises()

                # Validation finale
                if not self._valider_configuration():
                    return False

                self.actif = True
                self.metriques.incrementer("configurations_reussies")

                # Démarrage de la maintenance automatique
                self._demarrer_maintenance_automatique()

                print("✅ Système de logs intelligent configuré avec succès")
                return True

        except Exception as e:
            self.metriques.enregistrer_erreur(f"Erreur configuration: {e}")
            print(f"❌ Échec configuration logging: {e}")
            return False

    def _nettoyer_handlers_existants(self):
        """Nettoie tous les handlers existants pour éviter les doublons."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            try:
                handler.close()
            except:
                pass

    def _configurer_handlers_securises(self, formatter) -> bool:
        """Configure les handlers avec gestion d'erreurs robuste."""
        try:
            # Handler principal avec rotation sécurisée
            handler_principal = self._creer_rotating_handler(
                self.dossier_logs / "simulateur.log", formatter
            )
            if handler_principal:
                self.logger_principal.addHandler(handler_principal)

            # Handler console avec niveau adaptatif
            handler_console = logging.StreamHandler()
            handler_console.setFormatter(formatter)
            handler_console.setLevel(self.config.niveau_console)
            self.logger_principal.addHandler(handler_console)

            # Handler d'erreurs critiques (toujours actif)
            handler_erreurs = self._creer_rotating_handler(
                self.dossier_logs / "critiques.log", formatter, niveau=logging.ERROR
            )
            if handler_erreurs:
                self.logger_principal.addHandler(handler_erreurs)

            return True

        except Exception as e:
            print(f"Erreur configuration handlers: {e}")
            return False

    def _creer_rotating_handler(
        self, chemin: Path, formatter, niveau: int = None
    ) -> Optional[logging.Handler]:
        """Crée un handler rotatif sécurisé."""
        try:
            if not ValidateurLogs.valider_chemin_fichier(chemin):
                raise ValueError(f"Chemin non sécurisé: {chemin}")

            handler = logging.handlers.RotatingFileHandler(
                chemin,
                maxBytes=int(self.config.taille_max_mo * 1024 * 1024),
                backupCount=self.config.nb_fichiers_backup,
                encoding="utf-8",
                delay=True,  # Création différée du fichier
            )

            handler.setFormatter(formatter)
            if niveau:
                handler.setLevel(niveau)

            return handler

        except Exception as e:
            print(f"Erreur création handler {chemin}: {e}")
            return None

    def _creer_loggers_specialises(self):
        """Crée les loggers spécialisés avec isolation."""
        loggers_config = [
            ("ia", self.config.niveau_fichier),
            ("jeu", self.config.niveau_fichier),
            ("gui", self.config.niveau_fichier),
            ("performance", logging.DEBUG),
            ("securite", logging.INFO),
        ]

        for nom, niveau in loggers_config:
            try:
                logger = logging.getLogger(f"simulateur.{nom}")
                logger.setLevel(niveau)

                # Handler dédié pour ce logger
                formatter = logging.Formatter(
                    f"%(asctime)s | %(levelname)-8s | {nom.upper()} | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )

                handler = self._creer_rotating_handler(
                    self.dossier_logs / f"{nom}.log", formatter, niveau
                )

                if handler:
                    logger.addHandler(handler)
                    self.loggers_specialises[nom] = logger

            except Exception as e:
                print(f"Erreur création logger {nom}: {e}")

    def _valider_configuration(self) -> bool:
        """Valide que la configuration est opérationnelle."""
        try:
            # Test d'écriture
            self.logger_principal.info("Test de validation du système de logs")

            # Vérification de l'existence des fichiers
            fichier_principal = self.dossier_logs / "simulateur.log"
            if not fichier_principal.exists():
                return False

            # Test de lecture
            with open(fichier_principal, "r", encoding="utf-8") as f:
                contenu = f.read()
                if "Test de validation" not in contenu:
                    return False

            return True

        except Exception as e:
            print(f"Validation échouée: {e}")
            return False

    def _demarrer_maintenance_automatique(self):
        """Démarre les threads de maintenance automatique."""
        if not self.threads_maintenance:
            # Thread principal de maintenance
            thread_maintenance = threading.Thread(
                target=self._boucle_maintenance_principale,
                name="MaintenanceLogs",
                daemon=True,
            )
            thread_maintenance.start()
            self.threads_maintenance.append(thread_maintenance)

            # Thread de monitoring des métriques
            thread_metriques = threading.Thread(
                target=self._boucle_monitoring_metriques,
                name="MonitoringLogs",
                daemon=True,
            )
            thread_metriques.start()
            self.threads_maintenance.append(thread_metriques)

    def _boucle_maintenance_principale(self):
        """Boucle principale de maintenance."""
        while self.actif:
            try:
                with self.verrou_maintenance:
                    maintenant = time.time()

                    # Vérification périodique des logs
                    if (
                        maintenant - self.derniere_maintenance
                        >= self.config.intervalle_verification_sec
                    ):
                        self._maintenance_complete()
                        self.derniere_maintenance = maintenant

                time.sleep(60)  # Vérification toutes les minutes

            except Exception as e:
                self.metriques.enregistrer_erreur(f"Erreur maintenance: {e}")
                time.sleep(300)  # Attente plus longue en cas d'erreur

    def _boucle_monitoring_metriques(self):
        """Boucle de monitoring des métriques."""
        while self.actif:
            try:
                # Calcul de la taille actuelle
                taille_actuelle = self._calculer_taille_logs()
                self.metriques.enregistrer_taille(taille_actuelle)

                # Vérification des seuils
                self._verifier_seuils_alertes(taille_actuelle)

                time.sleep(60)  # Monitoring chaque minute

            except Exception as e:
                self.metriques.enregistrer_erreur(f"Erreur monitoring: {e}")
                time.sleep(120)

    def _maintenance_complete(self):
        """Effectue une maintenance complète du système."""
        try:
            print("🔧 Maintenance automatique des logs en cours...")

            # 1. Vérification de l'intégrité
            problemes = ValidateurLogs.verifier_integrite_logs(self.dossier_logs)
            if problemes:
                for probleme in problemes:
                    self.logger_principal.warning(f"Intégrité: {probleme}")

            # 2. Nettoyage et archivage
            fichiers_archives = self._archiver_anciens_logs()

            # 3. Compression des archives
            if self.config.compression_active:
                self._compresser_archives()

            # 4. Synthèse intelligente si nécessaire
            if self.config.synthese_automatique:
                self._generer_synthese_periodique()

            # 5. Nettoyage des archives anciennes
            supprimes = self.fichiers_manager.nettoyer_archives_anciennes(
                self.dossier_archive
            )
            if supprimes > 0:
                print(f"🗑️ {supprimes} archives anciennes supprimées")

            # 6. Mise à jour des métriques
            self.metriques.incrementer("maintenances_completees")

            print("✅ Maintenance automatique terminée")

        except Exception as e:
            self.metriques.enregistrer_erreur(f"Erreur maintenance complète: {e}")
            print(f"❌ Erreur pendant la maintenance: {e}")

    def verifier_et_synthetiser_logs(self, cerveau=None) -> Dict[str, Any]:
        """
        Interface principale pour vérification et synthèse.
        Retourne un rapport détaillé de l'opération.
        """
        try:
            with self.verrou_principal:
                rapport = {
                    "timestamp": time.time(),
                    "taille_avant": self._calculer_taille_logs(),
                    "actions_effectuees": [],
                    "erreurs": [],
                    "metriques": self.metriques.obtenir_rapport(),
                }

                # Vérification des seuils
                if rapport["taille_avant"] > self._calculer_seuil_synthese():
                    rapport["actions_effectuees"].append("synthese_declenchee")

                    if cerveau and hasattr(cerveau, "synthetiser_logs_recents"):
                        try:
                            synthese_ia = cerveau.synthetiser_logs_recents()
                            self._sauvegarder_synthese_ia(synthese_ia)
                            rapport["actions_effectuees"].append(
                                "synthese_ia_sauvegardee"
                            )
                        except Exception as e:
                            rapport["erreurs"].append(f"Erreur synthèse IA: {e}")

                    # Synthèse automatique comme fallback
                    try:
                        self._generer_synthese_automatique()
                        rapport["actions_effectuees"].append("synthese_automatique")
                    except Exception as e:
                        rapport["erreurs"].append(f"Erreur synthèse auto: {e}")

                # Archivage si nécessaire
                try:
                    nb_archives = self._archiver_anciens_logs()
                    if nb_archives > 0:
                        rapport["actions_effectuees"].append(
                            f"archivage_{nb_archives}_fichiers"
                        )
                except Exception as e:
                    rapport["erreurs"].append(f"Erreur archivage: {e}")

                rapport["taille_apres"] = self._calculer_taille_logs()
                rapport["reduction_mo"] = (
                    rapport["taille_avant"] - rapport["taille_apres"]
                )

                return rapport

        except Exception as e:
            self.metriques.enregistrer_erreur(f"Erreur vérification globale: {e}")
            return {
                "timestamp": time.time(),
                "erreur_critique": str(e),
                "metriques": self.metriques.obtenir_rapport(),
            }

    def _calculer_taille_logs(self) -> float:
        """Calcule la taille totale des logs en Mo avec gestion d'erreurs."""
        taille_totale = 0
        try:
            for pattern in ["*.log", "*.log.*"]:
                for fichier in self.dossier_logs.glob(pattern):
                    if fichier.is_file():
                        try:
                            taille_totale += fichier.stat().st_size
                        except (OSError, ValueError):
                            continue
        except Exception:
            pass

        return taille_totale / (1024 * 1024)

    def _calculer_seuil_synthese(self) -> float:
        """Calcule le seuil de déclenchement de la synthèse."""
        taille_max_totale = self.config.taille_max_mo * self.config.nb_fichiers_backup
        return taille_max_totale * (self.config.seuil_synthese_pct / 100)

    def _archiver_anciens_logs(self) -> int:
        """Archive les anciens logs avec métadonnées."""
        compteur = 0
        try:
            for fichier in self.dossier_logs.glob("*.log.*"):
                if fichier.suffix in [".1", ".2", ".3", ".4", ".5"]:
                    if self.fichiers_manager.archiver_avec_metadata(
                        fichier, self.dossier_archive
                    ):
                        fichier.unlink()
                        compteur += 1
        except Exception as e:
            print(f"Erreur archivage: {e}")

        return compteur

    def _compresser_archives(self):
        """Compresse les archives non compressées."""
        try:
            for fichier in self.dossier_archive.glob("*.log"):
                if fichier.is_file():
                    self.fichiers_manager.compresser_fichier(fichier)
        except Exception as e:
            print(f"Erreur compression: {e}")

    def _generer_synthese_periodique(self):
        """Génère une synthèse périodique intelligente."""
        try:
            fichiers_a_synthetiser = list(self.dossier_logs.glob("*.log"))
            if not fichiers_a_synthetiser:
                return

            synthese_contenu = self.synthese_manager.generer_synthese(
                fichiers_a_synthetiser
            )

            # Sauvegarde de la synthèse
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fichier_synthese = self.dossier_syntheses / f"synthese_auto_{timestamp}.md"

            with open(fichier_synthese, "w", encoding="utf-8") as f:
                f.write(synthese_contenu)

            print(f"📊 Synthèse automatique sauvée: {fichier_synthese.name}")

        except Exception as e:
            print(f"Erreur génération synthèse: {e}")

    def _generer_synthese_automatique(self):
        """Génère une synthèse automatique en cas d'indisponibilité de l'IA."""
        self._generer_synthese_periodique()

    def _sauvegarder_synthese_ia(self, contenu_synthese: str):
        """Sauvegarde une synthèse générée par l'IA."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fichier_synthese = self.dossier_syntheses / f"synthese_ia_{timestamp}.md"

            with open(fichier_synthese, "w", encoding="utf-8") as f:
                f.write(
                    f"# Synthèse par IA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                f.write(contenu_synthese)
                f.write(f"\n\n---\n*Synthèse générée automatiquement par l'IA*")

            print(f"🤖 Synthèse IA sauvée: {fichier_synthese.name}")

        except Exception as e:
            print(f"Erreur sauvegarde synthèse IA: {e}")

    def _verifier_seuils_alertes(self, taille_actuelle: float):
        """Vérifie les seuils et génère des alertes si nécessaire."""
        seuil_alerte = self._calculer_seuil_synthese() * (
            self.config.seuil_alerte_espace_pct / 100
        )

        if taille_actuelle > seuil_alerte:
            alerte = {
                "type": "SEUIL_ESPACE",
                "taille_actuelle": taille_actuelle,
                "seuil": seuil_alerte,
                "timestamp": time.time(),
            }

            try:
                self.queue_alertes.put_nowait(alerte)
                if self.logger_principal:
                    self.logger_principal.warning(
                        f"Seuil d'espace atteint: {taille_actuelle:.1f}Mo > {seuil_alerte:.1f}Mo"
                    )
            except queue.Full:
                pass  # Queue pleine, on ignore l'alerte

    def obtenir_statut_complet(self) -> Dict[str, Any]:
        """Retourne un statut complet du système de logs."""
        return {
            "actif": self.actif,
            "configuration": {
                "taille_max_mo": self.config.taille_max_mo,
                "nb_fichiers_backup": self.config.nb_fichiers_backup,
                "compression_active": self.config.compression_active,
                "synthese_automatique": self.config.synthese_automatique,
            },
            "metriques": self.metriques.obtenir_rapport(),
            "taille_actuelle_mo": self._calculer_taille_logs(),
            "nb_loggers_specialises": len(self.loggers_specialises),
            "nb_threads_maintenance": len(self.threads_maintenance),
            "derniere_maintenance": self.derniere_maintenance,
            "alertes_en_attente": self.queue_alertes.qsize(),
        }

    def arreter_proprement(self):
        """Arrête le système de logs proprement."""
        try:
            self.actif = False

            # Attente de l'arrêt des threads
            for thread in self.threads_maintenance:
                if thread.is_alive():
                    thread.join(timeout=5)

            # Fermeture des handlers
            if self.logger_principal:
                for handler in self.logger_principal.handlers:
                    try:
                        handler.close()
                    except:
                        pass

            print("✅ Système de logs arrêté proprement")

        except Exception as e:
            print(f"Erreur arrêt système logs: {e}")

    def creer_thread_monitoring(self, cerveau):
        """Crée un thread pour le monitoring continu des logs (interface de compatibilité)."""

        def monitoring_logs():
            while getattr(cerveau, "running", True) and self.actif:
                try:
                    rapport = self.verifier_et_synthetiser_logs(cerveau)
                    if rapport.get("erreurs"):
                        for erreur in rapport["erreurs"]:
                            self.metriques.enregistrer_erreur(erreur)

                    # Attente avec vérification périodique de l'état
                    for _ in range(self.config.intervalle_verification_sec):
                        if not getattr(cerveau, "running", True) or not self.actif:
                            break
                        time.sleep(1)

                except Exception as e:
                    self.metriques.enregistrer_erreur(f"Erreur thread monitoring: {e}")
                    time.sleep(300)

        thread_monitoring = threading.Thread(
            target=monitoring_logs, daemon=True, name="MonitoringExterne"
        )
        thread_monitoring.start()
        return thread_monitoring


# Instance globale avec configuration par défaut robuste
gestionnaire_logs = GestionnaireLogsIntelligent(
    {
        "taille_max_mo": 5,
        "nb_fichiers_backup": 10,
        "retention_jours": 60,
        "compression_active": True,
        "synthese_automatique": True,
        "monitoring_performance": True,
        "seuil_synthese_pct": 75,
        "niveau_defaut": "INFO",
    }
)


# Interfaces de compatibilité
def configurer_logging(niveau=logging.INFO):
    """Interface simple pour configurer le logging."""
    return gestionnaire_logs.configurer_logging(niveau)


def verifier_et_synthetiser_logs(cerveau=None):
    """Interface simple pour vérifier les logs."""
    return gestionnaire_logs.verifier_et_synthetiser_logs(cerveau)


def get_logger(nom="simulateur"):
    """Récupère un logger configuré."""
    return logging.getLogger(nom)


def obtenir_rapport_logs():
    """Récupère un rapport complet du système de logs."""
    return gestionnaire_logs.obtenir_statut_complet()
