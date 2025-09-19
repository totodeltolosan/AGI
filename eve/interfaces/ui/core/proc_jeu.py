"""
Processus enfant 1 - Pont avec Minetest (Directive 21).
Maintient communication avec jeu via enfant_eve/pont_jeu/.
"""

import logging
import time
import queue
import multiprocessing as mp
from enfant_eve.pont_jeu.connexion import ConnexionMinetest
from enfant_eve.pont_jeu.commandes import ExecuteurCommandes

logger = logging.getLogger(__name__)


class ProcessusJeu(mp.Process):
    def __init__(self, queues, config):
        super().__init__()
        self.queues = queues
        self.config = config
        self.running = True
        self.connexion = None
        self.executeur = None

    def run(self):
        """Boucle principale processus jeu."""
        logger.info("Processus jeu démarré")

        try:
            self.connexion = ConnexionMinetest(self.config.get("minetest", {}))
            self.executeur = ExecuteurCommandes(self.connexion)

            while self.running:
                self._traiter_commandes_ia()
                self._envoyer_etat_monde()
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Erreur processus jeu: {e}")
        finally:
            self._fermer_connexion()

    def _traiter_commandes_ia(self):
        """Traite commandes provenant de l'IA."""
        try:
            while True:
                commande = self.queues["ia_vers_jeu"].get_nowait()
                self.executeur.executer(commande)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Erreur traitement commandes: {e}")

    def _envoyer_etat_monde(self):
        """Envoie état monde vers IA."""
        try:
            etat = self.connexion.lire_etat_monde()
            if etat:
                self.queues["jeu_vers_ia"].put(etat, timeout=1.0)
        except queue.Full:
            logger.warning("Queue jeu_vers_ia pleine")
        except Exception as e:
            logger.error(f"Erreur envoi état monde: {e}")

    def _fermer_connexion(self):
        """Ferme connexion proprement."""
        if self.connexion:
            self.connexion.fermer()
        logger.info("Processus jeu arrêté")

    def arreter(self):
        """Arrête processus jeu."""
        self.running = False
