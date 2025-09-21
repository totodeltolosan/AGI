import logging
import time
import random
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ProcessusJeu:
    """
    Processus qui simule le jeu Minetest avec état persistant
    Implémente les Directives D18 (lecture progrès), D48 (phases de vie)
    """

    def __init__(self, config, q_jeu_ia, q_ia_jeu):
        """TODO: Add docstring."""
        self.config = config
        self.q_entree = q_ia_jeu  # Commandes de l'IA
        self.q_sortie = q_jeu_ia  # État du monde vers l'IA
        self.running = True

        # État du monde persistant
        self.etat_monde = self._initialiser_etat_monde()
        self.tick_counter = 0
        self.phase_jour_nuit = "jour"  # jour, crepuscule, nuit, aube
        self.temps_monde = 0.0  # Temps de jeu en heures

        # Statistiques de jeu (Directive D18)
        self.stats_jeu = {
            "session_demarree": time.time(),
            "temps_jeu_total": 0.0,
            "actions_executees": 0,
            "blocs_places": 0,
            "blocs_casses": 0,
            "distance_parcourue": 0.0,
            "morts": 0,
            "niveau_experience": 0,
        }

        # Charger sauvegarde si existe
        self._charger_sauvegarde()

    def _initialiser_etat_monde(self):
        """Initialise l'état du monde par défaut"""
        return {
            "timestamp": time.time(),
            "etat_joueur": {
                "vie": 20.0,  # Sur 20 (comme Minecraft)
                "faim": 20.0,  # Sur 20
                "oxygene": 20.0,  # Sous l'eau
                "experience": 0,
                "niveau": 0,
                "position": {"x": 0.0, "y": 64.0, "z": 0.0},
                "rotation": {"yaw": 0.0, "pitch": 0.0},
                "inventaire": {
                    "bois": 0,
                    "pierre": 0,
                    "fer": 0,
                    "charbon": 0,
                    "nourriture": 3,
                    "outils": [],
                    "armes": [],
                },
                "equipement": {
                    "main": None,
                    "casque": None,
                    "plastron": None,
                    "jambieres": None,
                    "bottes": None,
                },
            },
            "environnement": {
                "biomes_autour": ["plaines"],
                "niveau_lumiere": 15,  # 0-15 (comme Minecraft)
                "meteo": "clair",  # clair, pluie, orage, neige
                "temperature": 20.0,
                "y_surface": 64,
                "structures_proches": [],
                "mobs_proches": [],
                "ressources_visibles": ["arbres", "pierre_surface"],
            },
            "dernier_evenement": {
                "type": "spawn",
                "description": "Apparition dans le monde",
                "timestamp": time.time(),
                "position": {"x": 0.0, "y": 64.0, "z": 0.0},
            },
            "progres_jeu": {
                # Progrès de base (Directive D18)
                "premier_connexion": True,
                "a_regarde_autour": False,
                "premier_deplacement": False,
                "bois_collecte": False,
                "pierre_collectee": False,
                "premier_outil": False,
                "premier_abri": False,
                "premiere_nuit_survivee": False,
                "premier_combat": False,
                "premiere_mort": False,
                # Phases de vie (Directive D48)
                "phase_actuelle": "decouverte",  # decouverte, survie, expansion, maitrise
                "score_phase": {
                    "decouverte": 0,
                    "survie": 0,
                    "expansion": 0,
                    "maitrise": 0,
                },
                # Objectifs spéciaux
                "objectifs_secrets_decouverts": [],
                "artefacts_trouves": [],
                "boss_affrontes": [],
            },
            "monde": {
                "seed": random.randint(1000000, 9999999),
                "chunks_charges": [(0, 0)],
                "constructions_joueur": [],
                "modifications_terrain": [],
            },
        }

    def run(self):
        """Boucle principale du processus jeu avec simulation avancée"""
        logger.info("ProcessusJeu démarré - Simulation Minetest avancée")

        # Message de bienvenue détaillé
        spawn_msg = {
            "type": "message_jeu",
            "contenu": "Bienvenue dans Le Simulateur ! Vous apparaissez dans un monde procedural infini.",
            "couleur": "vert",
        }
        self._envoyer_etat_monde(spawn_msg)

        while self.running:
            try:
                # Mise à jour temporelle
                self._mettre_a_jour_temps()

                # Traitement des commandes de l'IA
                self._traiter_commandes_ia()

                # Simulation environnement
                self._simuler_environnement()

                # Mise à jour progrès et phases (Directives D18, D48)
                self._evaluer_progres()

                # Envoyer état mis à jour
                if self.tick_counter % 5 == 0:  # Tous les 5 ticks
                    self._envoyer_etat_monde()

                # Sauvegarde périodique
                if self.tick_counter % 100 == 0:  # Toutes les 100 secondes
                    self._sauvegarder_etat()

                self.tick_counter += 1
                self.stats_jeu["temps_jeu_total"] += 1.0
                time.sleep(1.0)

            except KeyboardInterrupt:
                logger.info("Arrêt demandé du ProcessusJeu")
                break
            except Exception as e:
                logger.error("Erreur processus JEU: %s", e, exc_info=True)
                time.sleep(0.5)

        # Sauvegarde finale
        self._sauvegarder_etat()
        logger.info("ProcessusJeu terminé")

    def _mettre_a_jour_temps(self):
        """Met à jour le temps de jeu et cycles jour/nuit"""
        self.temps_monde += 1.0 / 60.0  # 1 minute réelle = 1 heure jeu

        # Cycle jour/nuit (24h = 24 minutes réelles)
        heure_jour = int(self.temps_monde) % 24

        if 6 <= heure_jour < 18:
            if self.phase_jour_nuit != "jour":
                self.phase_jour_nuit = "jour"
                self._creer_evenement("lever_soleil", "Le soleil se lève")
        elif 18 <= heure_jour < 20:
            if self.phase_jour_nuit != "crepuscule":
                self.phase_jour_nuit = "crepuscule"
                self._creer_evenement("crepuscule", "Le crépuscule arrive")
        elif 20 <= heure_jour or heure_jour < 6:
            if self.phase_jour_nuit != "nuit":
                self.phase_jour_nuit = "nuit"
                self._creer_evenement(
                    "coucher_soleil", "La nuit tombe, attention aux monstres!"
                )

        # Mise à jour niveau lumière
        if self.phase_jour_nuit == "jour":
            self.etat_monde["environnement"]["niveau_lumiere"] = 15
        elif self.phase_jour_nuit == "crepuscule":
            self.etat_monde["environnement"]["niveau_lumiere"] = 8
        else:  # nuit
            self.etat_monde["environnement"]["niveau_lumiere"] = 2

    def _traiter_commandes_ia(self):
        """Traite les commandes envoyées par l'IA"""
        commandes_traitees = 0

        while not self.q_entree.empty() and commandes_traitees < 10:
            try:
                commande = self.q_entree.get_nowait()
                resultat = self._executer_commande(commande)

                if resultat:
                    logger.info(
                        "JEU: Commande '%s' exécutée avec succès",
                        commande.get("type", "UNKNOWN"),
                    )
                    self.stats_jeu["actions_executees"] += 1

                commandes_traitees += 1

            except Exception as e:
                logger.error("Erreur traitement commande: %s", e)

    def _executer_commande(self, commande):
        """Exécute une commande spécifique de l'IA"""
        if not isinstance(commande, dict):
            return False

        type_commande = commande.get("type")
        joueur = self.etat_monde["etat_joueur"]

        if type_commande == "REGARDER_AUTOUR":
            # L'IA regarde autour d'elle
            if not self.etat_monde["progres_jeu"]["a_regarde_autour"]:
                self.etat_monde["progres_jeu"]["a_regarde_autour"] = True
                self._creer_evenement(
                    "premiere_observation",
                    "Vous observez attentivement votre environnement",
                )

            # Découvrir ressources selon le biome
            self._decouvrir_ressources_proches()
            return True

        elif type_commande == "DEPLACEMENT":
            # L'IA se déplace
            destination = commande.get("destination", {})
            if self._deplacer_joueur(destination):
                if not self.etat_monde["progres_jeu"]["premier_deplacement"]:
                    self.etat_monde["progres_jeu"]["premier_deplacement"] = True
                    self._creer_evenement("premier_pas", "Premier déplacement effectué")
                return True

        elif type_commande == "CASSER_BLOC":
            # L'IA casse un bloc
            cible = commande.get("cible", {})
            type_bloc = commande.get("bloc", "terre")
            return self._casser_bloc(cible, type_bloc)

        elif type_commande == "PLACER_BLOC":
            # L'IA place un bloc
            position = commande.get("position", {})
            type_bloc = commande.get("bloc", "terre")
            return self._placer_bloc(position, type_bloc)

        elif type_commande == "CRAFTER":
            # L'IA craft un objet
            recette = commande.get("recette")
            return self._crafter_objet(recette)

        elif type_commande == "CONSTRUIRE":
            # L'IA construit une structure
            plan = commande.get("plan", {})
            return self._construire_structure(plan)

        elif type_commande == "ATTAQUER":
            # L'IA attaque un mob
            cible = commande.get("cible")
            return self._attaquer_cible(cible)

        return False

    def _deplacer_joueur(self, destination):
        """Déplace le joueur vers une destination"""
        if not isinstance(destination, dict) or "x" not in destination:
            return False

        pos_actuelle = self.etat_monde["etat_joueur"]["position"]
        nouvelle_pos = {
            "x": destination.get("x", pos_actuelle["x"]),
            "y": destination.get("y", pos_actuelle["y"]),
            "z": destination.get("z", pos_actuelle["z"]),
        }

        # Calculer distance
        distance = (
            (nouvelle_pos["x"] - pos_actuelle["x"]) ** 2
            + (nouvelle_pos["z"] - pos_actuelle["z"]) ** 2
        ) ** 0.5

        # Limiter déplacement par tick
        if distance > 10.0:
            direction_x = (nouvelle_pos["x"] - pos_actuelle["x"]) / distance
            direction_z = (nouvelle_pos["z"] - pos_actuelle["z"]) / distance
            nouvelle_pos["x"] = pos_actuelle["x"] + direction_x * 10.0
            nouvelle_pos["z"] = pos_actuelle["z"] + direction_z * 10.0
            distance = 10.0

        # Mettre à jour position
        self.etat_monde["etat_joueur"]["position"] = nouvelle_pos
        self.stats_jeu["distance_parcourue"] += distance

        # Consommer faim selon distance
        faim_consommee = distance * 0.01
        self.etat_monde["etat_joueur"]["faim"] -= faim_consommee

        return True

    def _casser_bloc(self, position, type_bloc):
        """Simule casser un bloc et récupérer ressources"""
        if type_bloc == "bois":
            self.etat_monde["etat_joueur"]["inventaire"]["bois"] += 1
            if not self.etat_monde["progres_jeu"]["bois_collecte"]:
                self.etat_monde["progres_jeu"]["bois_collecte"] = True
                self._creer_evenement("premier_bois", "Premier bois collecté !")

        elif type_bloc == "pierre":
            self.etat_monde["etat_joueur"]["inventaire"]["pierre"] += 1
            if not self.etat_monde["progres_jeu"]["pierre_collectee"]:
                self.etat_monde["progres_jeu"]["pierre_collectee"] = True
                self._creer_evenement("premiere_pierre", "Première pierre collectée !")

        self.stats_jeu["blocs_casses"] += 1
        return True

    def _placer_bloc(self, position, type_bloc):
        """Place un bloc dans le monde"""
        inventaire = self.etat_monde["etat_joueur"]["inventaire"]

        if type_bloc in inventaire and inventaire[type_bloc] > 0:
            inventaire[type_bloc] -= 1
            self.stats_jeu["blocs_places"] += 1

            # Enregistrer construction
            construction = {
                "type": "bloc",
                "materiau": type_bloc,
                "position": position,
                "timestamp": time.time(),
            }
            self.etat_monde["monde"]["constructions_joueur"].append(construction)

            return True
        return False

    def _crafter_objet(self, recette):
        """Craft un objet selon une recette"""
        inventaire = self.etat_monde["etat_joueur"]["inventaire"]

        if recette == "pioche_bois":
            if inventaire["bois"] >= 3:
                inventaire["bois"] -= 3
                inventaire["outils"].append("pioche_bois")

                if not self.etat_monde["progres_jeu"]["premier_outil"]:
                    self.etat_monde["progres_jeu"]["premier_outil"] = True
                    self._creer_evenement(
                        "premier_outil", "Premier outil crafté : pioche en bois !"
                    )
                return True

        elif recette == "epee_bois":
            if inventaire["bois"] >= 2:
                inventaire["bois"] -= 2
                inventaire["armes"].append("epee_bois")
                return True

        return False

    def _construire_structure(self, plan):
        """Construit une structure selon un plan"""
        if plan.get("type") == "abri_simple":
            inventaire = self.etat_monde["etat_joueur"]["inventaire"]

            # Coût en matériaux
            if inventaire["bois"] >= 10:
                inventaire["bois"] -= 10

                # Créer structure
                structure = {
                    "type": "abri",
                    "nom": "Abri de survie",
                    "taille": "3x3x3",
                    "position": self.etat_monde["etat_joueur"]["position"].copy(),
                    "timestamp": time.time(),
                }
                self.etat_monde["monde"]["constructions_joueur"].append(structure)

                if not self.etat_monde["progres_jeu"]["premier_abri"]:
                    self.etat_monde["progres_jeu"]["premier_abri"] = True
                    self._creer_evenement(
                        "premier_abri",
                        "Premier abri construit ! Vous êtes maintenant protégé.",
                    )

                return True
        return False

    def _simuler_environnement(self):
        """Simule les changements dans l'environnement"""
        env = self.etat_monde["environnement"]

        # Météo aléatoire
        if random.random() < 0.01:  # 1% chance par tick
            meteos = ["clair", "pluie", "orage", "brouillard"]
            ancienne_meteo = env["meteo"]
            env["meteo"] = random.choice(meteos)

            if env["meteo"] != ancienne_meteo:
                self._creer_evenement(
                    "changement_meteo", f"La météo change : {env['meteo']}"
                )

        # Spawn de mobs la nuit
        if (
            self.phase_jour_nuit == "nuit"
            and random.random() < 0.05
            and len(env["mobs_proches"]) < 3
        ):

            mobs_nuit = ["zombie", "squelette", "araignee", "creeper"]
            nouveau_mob = random.choice(mobs_nuit)
            env["mobs_proches"].append(
                {
                    "type": nouveau_mob,
                    "vie": 20,
                    "position": self._position_aleatoire_proche(),
                }
            )

            self._creer_evenement(
                "apparition_mob", f"Un {nouveau_mob} apparaît dans l'obscurité!"
            )

    def _evaluer_progres(self):
        """Évalue et met à jour les progrès et phases (Directive D48)"""
        progres = self.etat_monde["progres_jeu"]
        score_phases = progres["score_phase"]

        # Calcul score phase découverte
        decouverte_score = (
            int(progres["a_regarde_autour"]) * 10
            + int(progres["premier_deplacement"]) * 15
            + int(progres["bois_collecte"]) * 20
            + int(progres["pierre_collectee"]) * 20
        )
        score_phases["decouverte"] = decouverte_score

        # Calcul score phase survie
        survie_score = (
            int(progres["premier_outil"]) * 30
            + int(progres["premier_abri"]) * 50
            + int(progres["premiere_nuit_survivee"]) * 40
        )
        score_phases["survie"] = survie_score

        # Déterminer phase actuelle
        if (
            score_phases["decouverte"] >= 50
            and progres["phase_actuelle"] == "decouverte"
        ):
            progres["phase_actuelle"] = "survie"
            self._creer_evenement(
                "changement_phase",
                "Phase de survie atteinte ! Focus sur la protection et les outils.",
            )

        elif score_phases["survie"] >= 100 and progres["phase_actuelle"] == "survie":
            progres["phase_actuelle"] = "expansion"
            self._creer_evenement(
                "changement_phase",
                "Phase d'expansion atteinte ! Explorez et construisez davantage.",
            )

    def _decouvrir_ressources_proches(self):
        """Découvre les ressources visibles selon le biome"""
        env = self.etat_monde["environnement"]
        biome_principal = env["biomes_autour"][0] if env["biomes_autour"] else "plaines"

        nouvelles_ressources = []

        if biome_principal == "plaines":
            nouvelles_ressources = [
                "arbres_chene",
                "fleurs",
                "herbe_haute",
                "pierres_surface",
            ]
        elif biome_principal == "foret":
            nouvelles_ressources = [
                "arbres_varies",
                "champignons",
                "baies",
                "bois_mort",
            ]
        elif biome_principal == "montagne":
            nouvelles_ressources = [
                "minerai_fer",
                "minerai_charbon",
                "rochers",
                "neige",
            ]
        elif biome_principal == "desert":
            nouvelles_ressources = ["cactus", "sable", "grès", "oasis_rare"]

        # Ajouter ressources non découvertes
        for ressource in nouvelles_ressources:
            if ressource not in env["ressources_visibles"]:
                env["ressources_visibles"].append(ressource)

    def _position_aleatoire_proche(self):
        """Génère une position aléatoire proche du joueur"""
        pos_joueur = self.etat_monde["etat_joueur"]["position"]
        return {
            "x": pos_joueur["x"] + random.randint(-20, 20),
            "y": pos_joueur["y"] + random.randint(-5, 5),
            "z": pos_joueur["z"] + random.randint(-20, 20),
        }

    def _creer_evenement(self, type_event, description):
        """Crée un nouvel événement dans le monde"""
        self.etat_monde["dernier_evenement"] = {
            "type": type_event,
            "description": description,
            "timestamp": time.time(),
            "position": self.etat_monde["etat_joueur"]["position"].copy(),
        }

    def _envoyer_etat_monde(self, message_special=None):
        """Envoie l'état actuel du monde à l'IA"""
        try:
            # Mettre à jour timestamp
            self.etat_monde["timestamp"] = time.time()

            # Ajouter informations de session
            self.etat_monde["session_info"] = {
                "phase_jour_nuit": self.phase_jour_nuit,
                "temps_monde_heures": round(self.temps_monde, 1),
                "tick_counter": self.tick_counter,
                "stats_jeu": self.stats_jeu.copy(),
            }

            # Message spécial ou état normal
            if message_special:
                etat_complet = {**self.etat_monde, **message_special}
            else:
                etat_complet = self.etat_monde

            if not self.q_sortie.full():
                self.q_sortie.put(etat_complet)

            # Log périodique détaillé
            if self.tick_counter % 20 == 0:
                pos = self.etat_monde["etat_joueur"]["position"]
                logger.info(
                    "JEU: État envoyé - Phase:%s Pos:(%.1f,%.1f,%.1f) Vie:%.1f",
                    self.etat_monde["progres_jeu"]["phase_actuelle"],
                    pos["x"],
                    pos["y"],
                    pos["z"],
                    self.etat_monde["etat_joueur"]["vie"],
                )

        except Exception as e:
            logger.error("Erreur envoi état monde: %s", e)

    def _sauvegarder_etat(self):
        """Sauvegarde l'état du jeu (Directive D18)"""
        try:
            sauvegarde_dir = Path("saves")
            sauvegarde_dir.mkdir(exist_ok=True)

            sauvegarde = {
                "etat_monde": self.etat_monde,
                "stats_jeu": self.stats_jeu,
                "timestamp_sauvegarde": time.time(),
            }

            with open(
                sauvegarde_dir / "partie_courante.json", "w", encoding="utf-8"
            ) as f:
                json.dump(sauvegarde, f, indent=2, ensure_ascii=False)

            logger.info("JEU: Sauvegarde effectuée")

        except Exception as e:
            logger.error("Erreur sauvegarde: %s", e)

    def _charger_sauvegarde(self):
        """Charge une sauvegarde existante si disponible"""
        try:
            sauvegarde_path = Path("saves/partie_courante.json")
            if sauvegarde_path.exists():
                with open(sauvegarde_path, "r", encoding="utf-8") as f:
                    sauvegarde = json.load(f)

                self.etat_monde = sauvegarde.get("etat_monde", self.etat_monde)
                self.stats_jeu = sauvegarde.get("stats_jeu", self.stats_jeu)

                logger.info("JEU: Sauvegarde chargée avec succès")

        except Exception as e:
            logger.warning("Impossible de charger la sauvegarde: %s", e)
            logger.info("JEU: Démarrage d'une nouvelle partie")