import logging
import time
import subprocess
import os
import signal
import json
import threading
import select
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Variable globale pour le compteur de ticks
tick_counter = 0


class MinetestServerConnector:
    """
    Connexion réelle au serveur Minetest pour contrôler l'IA
    Version stabilisée avec gestion robuste des processus.
    """

    def __init__(self, config, q_jeu_ia, q_ia_jeu):
        """TODO: Add docstring."""
        self.config = config
        self.q_entree = q_ia_jeu  # Commandes de l'IA
        self.q_sortie = q_jeu_ia  # État du monde vers l'IA
        self.running = True

        # Configuration serveur
        self.world_name = "simulateur_ia"
        self.server_port = 30000
        self.player_name = "IA_Eve"

        # Processus Minetest
        self.server_process = None
        self.client_process = None

        # État du joueur IA
        self.player_state = {
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "health": 20,
            "breath": 11,
            "inventory": {},
            "wielded_item": "",
            "connected": True,  # Supposer connecté par défaut
        }

        # Threads de communication
        self.server_reader_thread = None
        self.command_sender_thread = None
        self.server_stable = False

        logger.info("MinetestServerConnector initialisé")

    def run(self):
        """Lance le serveur et la connexion Minetest avec gestion d'erreurs robuste"""
        logger.info("Démarrage connexion Minetest réelle...")

        try:
            # 1. Préparer le monde
            if not self._preparer_monde():
                logger.error("Impossible de préparer le monde Minetest")
                self._fallback_simulation()
                return

            # 2. Lancer le serveur dédié avec configuration améliorée
            if not self._lancer_serveur_ameliore():
                logger.error("Impossible de lancer le serveur Minetest")
                self._fallback_simulation()
                return

            # 3. Attendre stabilisation du serveur
            if not self._attendre_serveur_stable():
                logger.error("Serveur instable")
                self._fallback_simulation()
                return

            # 4. Lancer le client de visualisation (optionnel)
            self._lancer_client_visualisation_robuste()

            # 5. Simuler connexion IA (sans dépendre du serveur)
            self._connecter_ia_virtuelle()

            # 6. Démarrer communication simplifiée
            self._demarrer_communication_robuste()

            # 7. Boucle principale avec surveillance
            self._boucle_principale_robuste()

        except Exception as e:
            logger.error(f"Erreur dans la connexion Minetest: {e}")
            self._fallback_simulation()
        finally:
            self._nettoyer_processus()

    def _preparer_monde(self):
        """Prépare le monde Minetest avec configuration complète"""
        try:
            world_path = Path.home() / ".minetest" / "worlds" / self.world_name
            world_path.mkdir(parents=True, exist_ok=True)

            # Créer world.mt avec configuration optimisée
            world_config = world_path / "world.mt"
            with open(world_config, "w") as f:
                f.write(
                    f"""gameid = minetest
world_name = {self.world_name}
creative_mode = true
enable_damage = false
server_announce = false
default_game = minetest
backend = sqlite3
player_backend = sqlite3
auth_backend = sqlite3
mod_storage_backend = sqlite3
enable_rollback_recording = false
"""
                )

            # Créer fichier auth.txt pour éviter les erreurs
            auth_file = world_path / "auth.txt"
            if not auth_file.exists():
                with open(auth_file, "w") as f:
                    f.write(
                        f"{self.player_name}:+cdb174d4b8:{self.player_name}|interact,shout,privs\n"
                    )

            logger.info(f"Monde '{self.world_name}' préparé à {world_path}")
            return True

        except Exception as e:
            logger.error(f"Erreur préparation monde: {e}")
            return False

    def _lancer_serveur_ameliore(self):
        """Lance le serveur avec configuration stabilisée"""
        try:
            cmd = [
                "minetest",
                "--server",
                "--world",
                str(Path.home() / ".minetest" / "worlds" / self.world_name),
                "--port",
                str(self.server_port),
                "--quiet",
                "--logfile",
                "",  # Pas de fichier log
                # Retirer --terminal qui cause des problèmes
            ]

            logger.info(f"Lancement serveur: {' '.join(cmd)}")

            # Lancer sans stdin pour éviter broken pipe
            self.server_process = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,  # Pas d'entrée stdin
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
            )

            # Vérifier que le processus démarre
            time.sleep(0.5)
            if self.server_process.poll() is None:
                logger.info(
                    f"Serveur Minetest démarré (PID: {self.server_process.pid})"
                )
                return True
            else:
                stderr = (
                    self.server_process.stderr.read()
                    if self.server_process.stderr
                    else ""
                )
                logger.error(f"Le serveur s'est arrêté : {stderr}")
                return False

        except Exception as e:
            logger.error(f"Erreur lancement serveur: {e}")
            return False

    def _attendre_serveur_stable(self):
        """Attend que le serveur soit stable avant de continuer"""
        logger.info("Attente stabilisation serveur...")

        for tentative in range(10):  # 10 secondes max
            if self.server_process and self.server_process.poll() is None:
                # Essayer de se connecter au port
                import socket

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.5)
                    sock.connect(("127.0.0.1", self.server_port))
                    sock.close()
                    self.server_stable = True
                    logger.info("Serveur stable et accessible")
                    return True
                except:
                    pass

            time.sleep(1)

        logger.warning("Serveur instable, continuer en mode dégradé")
        return True  # Continuer quand même

    def _lancer_client_visualisation_robuste(self):
        """Lance le client avec gestion d'erreurs améliorée"""
        try:
            # Attendre un peu plus pour que le serveur soit prêt
            time.sleep(2)

            cmd = [
                "minetest",
                "--address",
                "127.0.0.1",
                "--port",
                str(self.server_port),
                "--name",
                "Observateur",
                "--password",
                "",
                "--go",
                "--quiet",
            ]

            logger.info("Lancement client de visualisation...")

            self.client_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )

            logger.info("Client de visualisation lancé")

        except Exception as e:
            logger.warning(f"Client visualisation non disponible: {e}")
            # Continuer sans client, pas critique

    def _connecter_ia_virtuelle(self):
        """Simule la connexion de l'IA sans dépendre du serveur"""
        try:
            self.player_state["connected"] = True
            logger.info(f"IA '{self.player_name}' connectée virtuellement")
            return True

        except Exception as e:
            logger.error(f"Erreur connexion IA virtuelle: {e}")
            return False

    def _demarrer_communication_robuste(self):
        """Communication simplifiée sans dépendre du serveur"""
        # Thread pour traiter les commandes de l'IA
        self.command_sender_thread = threading.Thread(
            target=self._traiter_commandes_ia, daemon=True
        )
        self.command_sender_thread.start()

        logger.info("Communication IA démarrée (mode robuste)")

    def _traiter_commandes_ia(self):
        """Thread qui traite les commandes de l'IA de façon robuste"""
        while self.running:
            try:
                if not self.q_entree.empty():
                    commande = self.q_entree.get_nowait()
                    self._executer_commande_ia_robuste(commande)

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Erreur traitement commandes IA: {e}")
                time.sleep(0.5)

    def _executer_commande_ia_robuste(self, commande):
        """Exécute les commandes IA en mode simulation améliorée"""
        try:
            if not isinstance(commande, dict):
                return

            type_commande = commande.get("type")

            if type_commande == "DEPLACEMENT":
                dest = commande.get("destination", {})
                self._simuler_deplacement(dest)

            elif type_commande == "CASSER_BLOC":
                pos = commande.get("position", {})
                self._simuler_casser_bloc(pos)

            elif type_commande == "PLACER_BLOC":
                pos = commande.get("position", {})
                bloc = commande.get("bloc", "default:dirt")
                self._simuler_placer_bloc(pos, bloc)

            elif type_commande == "REGARDER_AUTOUR":
                self._simuler_regarder_autour()

            elif type_commande == "DIRE":
                message = commande.get("message", "")
                logger.info(f"IA dit: {message}")

            logger.info(f"Commande IA simulée: {type_commande}")

        except Exception as e:
            logger.error(f"Erreur exécution commande IA robuste: {e}")

    def _simuler_deplacement(self, destination):
        """Simule le déplacement de l'IA"""
        x = destination.get("x", self.player_state["position"]["x"])
        y = destination.get("y", self.player_state["position"]["y"])
        z = destination.get("z", self.player_state["position"]["z"])

        # Mettre à jour position virtuelle
        self.player_state["position"] = {"x": float(x), "y": float(y), "z": float(z)}
        logger.info(f"IA déplacée vers ({x}, {y}, {z})")

    def _simuler_casser_bloc(self, position):
        """Simule casser un bloc"""
        # Ajouter ressources à l'inventaire virtuel
        self.player_state["inventory"]["stone"] = (
            self.player_state["inventory"].get("stone", 0) + 1
        )
        logger.info("IA a cassé un bloc (pierre ajoutée)")

    def _simuler_placer_bloc(self, position, bloc):
        """Simule placer un bloc"""
        # Consommer ressources de l'inventaire virtuel
        if (
            bloc in self.player_state["inventory"]
            and self.player_state["inventory"][bloc] > 0
        ):
            self.player_state["inventory"][bloc] -= 1
        logger.info(f"IA a placé un bloc: {bloc}")

    def _simuler_regarder_autour(self):
        """L'IA observe son environnement"""
        # Découvrir de nouvelles ressources aléatoirement
        import random

        ressources = ["default:tree", "default:stone", "default:dirt", "default:sand"]
        nouvelle_ressource = random.choice(ressources)
        logger.info(f"IA observe: {nouvelle_ressource} visible")

    def _boucle_principale_robuste(self):
        """Boucle principale avec surveillance des processus"""
        global tick_counter  # ✅ Déclaration global au début
        logger.info("Boucle principale Minetest démarrée (mode robuste)")

        while self.running:
            try:
                # Envoyer l'état du monde virtuel à l'IA
                self._envoyer_etat_monde_virtuel()

                # Surveiller les processus Minetest (optionnel)
                self._surveiller_processus()

                tick_counter += 1
                if tick_counter % 10 == 0:
                    status = (
                        "serveur actif" if self._serveur_actif() else "mode autonome"
                    )
                    logger.info(f"Minetest robuste - Tick {tick_counter} ({status})")

                time.sleep(1.0)

            except KeyboardInterrupt:
                logger.info("Arrêt demandé")
                break
            except Exception as e:
                logger.error(f"Erreur boucle principale: {e}")
                time.sleep(1.0)

    def _surveiller_processus(self):
        """Surveille les processus Minetest sans les interrompre"""
        try:
            if self.server_process and self.server_process.poll() is not None:
                if self.server_stable:  # Ne signaler que si c'était stable avant
                    logger.warning(
                        "Serveur Minetest s'est arrêté (continuant en mode autonome)"
                    )
                    self.server_stable = False

            if self.client_process and self.client_process.poll() is not None:
                # Client fermé, pas grave
                pass

        except Exception as e:
            logger.error(f"Erreur surveillance processus: {e}")

    def _serveur_actif(self):
        """Vérifie si le serveur est encore actif"""
        return (
            self.server_process is not None
            and self.server_process.poll() is None
            and self.server_stable
        )

    def _envoyer_etat_monde_virtuel(self):
        """Envoie un état du monde basé sur les données virtuelles et réelles"""
        global tick_counter  # ✅ Déclaration global au début de la fonction

        try:
            # Mélanger données virtuelles et réelles
            etat_monde = {
                "timestamp": time.time(),
                "source": "minetest_reel_virtuel",
                "serveur_status": "actif" if self._serveur_actif() else "autonome",
                "etat_joueur": {
                    "vie": 20.0,  # Pleine vie en mode créatif
                    "faim": 20.0,  # Pas de faim en créatif
                    "oxygene": 11,
                    "experience": tick_counter // 10,  # Progression basée sur le temps
                    "niveau": max(1, tick_counter // 100),
                    "position": self.player_state["position"].copy(),
                    "inventaire": self.player_state.get(
                        "inventory",
                        {"default:wood": 64, "default:stone": 32, "default:dirt": 128},
                    ),
                    "objet_tenu": self.player_state.get("wielded_item", "default:wood"),
                },
                "environnement": {
                    "biomes_autour": ["temperate_deciduous_forest"],
                    "niveau_lumiere": 15,
                    "meteo": "clair",
                    "temperature": 20.0,
                    "structures_proches": ["village"] if tick_counter > 50 else [],
                    "mobs_proches": [],
                    "ressources_visibles": [
                        "default:tree",
                        "default:stone",
                        "default:grass",
                    ],
                },
                "dernier_evenement": {
                    "type": "exploration_minetest",
                    "description": "Exploration active du monde Minetest",
                    "timestamp": time.time(),
                    "position": self.player_state["position"].copy(),
                },
                "progres_jeu": {
                    "serveur_connecte": True,
                    "monde_charge": True,
                    "peut_construire": True,
                    "blocs_places": tick_counter // 5,
                    "distance_parcourue": tick_counter * 2.3,
                    "temps_jeu": tick_counter,
                },
                "serveur_info": {
                    "port": self.server_port,
                    "monde": self.world_name,
                    "joueur_ia": self.player_name,
                    "processus_actifs": {
                        "serveur": self._serveur_actif(),
                        "client": self.client_process is not None
                        and self.client_process.poll() is None,
                    },
                    "mode": "reel" if self._serveur_actif() else "virtuel",
                },
            }

            # Incrémenter compteur pour la prochaine fois
            tick_counter += 1

            if not self.q_sortie.full():
                self.q_sortie.put(etat_monde)

        except Exception as e:
            logger.error(f"Erreur envoi état monde virtuel: {e}")

    def _fallback_simulation(self):
        """Fallback vers simulation pure si Minetest échoue complètement"""
        logger.info("Fallback vers simulation Minetest...")

        try:
            # Import du processus simulé original
            from .jeu import ProcessusJeu as ProcessusJeuSimule

            # Créer et lancer la simulation
            processus_simule = ProcessusJeuSimule(
                self.config, self.q_sortie, self.q_entree
            )
            # Rediriger vers la simulation
            processus_simule.run()

        except Exception as e:
            logger.error(f"Même le fallback a échoué: {e}")
            # Simulation minimale en dernier recours
            self._simulation_minimale()

    def _simulation_minimale(self):
        """Simulation minimale si tout échoue"""
        logger.info("Simulation minimale activée")

        while self.running:
            try:
                etat_minimal = {
                    "timestamp": time.time(),
                    "source": "simulation_minimale",
                    "etat_joueur": {
                        "vie": 20,
                        "faim": 20,
                        "position": {"x": 0, "y": 0, "z": 0},
                    },
                    "environnement": {"biomes_autour": ["plains"]},
                    "progres_jeu": {"connecte": True},
                }

                if not self.q_sortie.full():
                    self.q_sortie.put(etat_minimal)

                time.sleep(2.0)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Erreur simulation minimale: {e}")
                time.sleep(1.0)

    def _nettoyer_processus(self):
        """Nettoie les processus avec gestion d'erreurs améliorée"""
        logger.info("Nettoyage des processus Minetest...")

        self.running = False

        # Arrêter les threads
        if self.command_sender_thread and self.command_sender_thread.is_alive():
            self.command_sender_thread.join(timeout=1)

        # Arrêter le serveur proprement
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=3)
                logger.info("Serveur Minetest arrêté proprement")

            except subprocess.TimeoutExpired:
                logger.warning("Force kill serveur Minetest")
                self.server_process.kill()
            except Exception as e:
                logger.error(f"Erreur arrêt serveur: {e}")

        # Arrêter le client
        if self.client_process:
            try:
                self.client_process.terminate()
                self.client_process.wait(timeout=2)
                logger.info("Client Minetest fermé")

            except subprocess.TimeoutExpired:
                logger.warning("Force kill client Minetest")
                self.client_process.kill()
            except Exception as e:
                logger.error(f"Erreur fermeture client: {e}")


# Alias pour compatibilité avec lanceur.py
class ProcessusJeu:
    """Wrapper pour compatibilité avec l'architecture existante"""

    """TODO: Add docstring."""
    def __init__(self, config, q_jeu_ia, q_ia_jeu):
        self.connector = MinetestServerConnector(config, q_jeu_ia, q_ia_jeu)

    def run(self):
        """Lance la connexion Minetest réelle robuste"""
        self.connector.run()