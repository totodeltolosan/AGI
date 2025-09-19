import logging
import queue
import time
import multiprocessing as mp
from lanceur_constantes import TIMEOUT_QUEUES

logger = logging.getLogger(__name__)


class ProcessusIA(mp.Process):
    def __init__(self, queues, config):
        super().__init__()
        self.queues = queues
        self.config = config
        self.running = True

    def run(self):
        """Boucle principale du processus IA."""
        logger.info("Processus IA démarré")

        try:
            from enfant_eve.ia.cerveau import Cerveau

            cerveau = Cerveau(self.queues, self.config)

            while self.running:
                self._traiter_commandes_gui()
                cerveau.cycle_principal()
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Erreur processus IA: {e}")
            self.running = False

    def _traiter_commandes_gui(self):
        """Traite les commandes provenant de l'interface."""
        try:
            while True:
                commande = self.queues["gui_vers_ia"].get_nowait()
                self._executer_commande(commande)
        except queue.Empty:
            pass

    def _executer_commande(self, commande):
        """Exécute une commande reçue."""
        if commande["type"] == "interrogation":
            self._traiter_interrogation(commande)
        elif commande["type"] == "arret":
            self.running = False

    def _traiter_interrogation(self, commande):
        """Traite une interrogation du mentor."""
        question = commande.get("question", "")

        reponse = {
            "type": "reponse_interrogation",
            "question": question,
            "reponse": f"Analyse en cours pour: {question}",
            "timestamp": time.time(),
        }

        try:
            self.queues["ia_vers_gui"].put(reponse, timeout=TIMEOUT_QUEUES)
        except queue.Full:
            logger.warning("Queue ia_vers_gui pleine")

    def _envoyer_raisonnement(self, donnees):
        """Envoie les données de raisonnement vers l'interface."""
        message = {"type": "raisonnement", "donnees": donnees, "timestamp": time.time()}

        try:
            self.queues["ia_vers_gui"].put(message, timeout=TIMEOUT_QUEUES)
        except queue.Full:
            logger.warning("Impossible d'envoyer raisonnement")

    def _envoyer_rapport(self, rapport):
        """Envoie un rapport vers l'interface."""
        message = {"type": "rapport", "contenu": rapport, "timestamp": time.time()}

        try:
            self.queues["ia_vers_gui"].put(message, timeout=TIMEOUT_QUEUES)
        except queue.Full:
            logger.warning("Impossible d'envoyer rapport")

    def arreter(self):
        """Arrête proprement le processus."""
        self.running = False
