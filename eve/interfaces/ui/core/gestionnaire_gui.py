import logging
import queue
import time
import multiprocessing as mp
from lanceur_constantes import GUI_UPDATE_INTERVAL, TIMEOUT_QUEUES

logger = logging.getLogger(__name__)


class GestionnaireGUI(mp.Process):
    def __init__(self, queues, config):
        super().__init__()
        self.queues = queues
        self.config = config
        self.running = True

    def run(self):
        """Boucle principale de l'interface graphique."""
        logger.info("Interface graphique démarrée")

        try:
            from tableau_bord import TableauBord
            import customtkinter as ctk

            root = ctk.CTk()
            tableau = TableauBord(
                root,
                self.queues["ia_vers_gui"],
                self.queues["gui_vers_ia"],
                self.config,
            )

            self._configurer_interface(root, tableau)
            root.mainloop()

        except Exception as e:
            logger.error(f"Erreur interface graphique: {e}")
        finally:
            self.running = False

    def _configurer_interface(self, root, tableau):
        """Configure l'interface graphique."""
        root.protocol("WM_DELETE_WINDOW", self._fermer_interface)
        self._programmer_mise_a_jour(root, tableau)

    def _programmer_mise_a_jour(self, root, tableau):
        """Programme les mises à jour périodiques."""

        def mise_a_jour():
            if self.running:
                self._traiter_messages(tableau)
                root.after(GUI_UPDATE_INTERVAL, mise_a_jour)

        root.after(GUI_UPDATE_INTERVAL, mise_a_jour)

    def _traiter_messages(self, tableau):
        """Traite les messages en provenance de l'IA."""
        try:
            while True:
                message = self.queues["ia_vers_gui"].get_nowait()
                self._dispatcher_message(tableau, message)
        except queue.Empty:
            pass

    def _dispatcher_message(self, tableau, message):
        """Dispatche un message vers le bon handler."""
        type_message = message.get("type")

        if type_message == "raisonnement":
            tableau.mettre_a_jour_raisonnement(message["donnees"])
        elif type_message == "rapport":
            tableau.afficher_rapport(message["contenu"])
        elif type_message == "reponse_interrogation":
            tableau.afficher_reponse(message)

    def _fermer_interface(self):
        """Ferme proprement l'interface."""
        self.running = False

        message_arret = {"type": "arret", "timestamp": time.time()}

        try:
            self.queues["gui_vers_ia"].put(message_arret, timeout=TIMEOUT_QUEUES)
        except queue.Full:
            pass

    def envoyer_interrogation(self, question):
        """Envoie une interrogation vers l'IA."""
        commande = {
            "type": "interrogation",
            "question": question,
            "timestamp": time.time(),
        }

        try:
            self.queues["gui_vers_ia"].put(commande, timeout=TIMEOUT_QUEUES)
            return True
        except queue.Full:
            logger.warning("Impossible d'envoyer interrogation")
            return False
