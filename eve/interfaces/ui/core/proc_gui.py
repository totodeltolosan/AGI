"""
Processus enfant 3 - Interface utilisateur (Directive 21).
Gère fenêtres Tkinter sans calculs lourds.
"""

import logging
import multiprocessing as mp
from enfant_eve.interface.tableau_bord import TableauBord
from enfant_eve.interface.fenetre_visualisation import FenetreVisualisation
import customtkinter as ctk

logger = logging.getLogger(__name__)


class ProcessusGUI(mp.Process):
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, queues, config):
        super().__init__()
        self.queues = queues
        self.config = config
        self.running = True

    def run(self):
        """Boucle principale interface graphique."""
        logger.info("Processus GUI démarré")

        try:
            root = ctk.CTk()

            TableauBord(
                root,
                self.queues["ia_vers_gui"],
                self.queues["gui_vers_ia"],
                self.config,
            )

            FenetreVisualisation(root, self.queues["ia_vers_gui"], self.config)

            root.protocol("WM_DELETE_WINDOW", self._fermer_interface)
            root.mainloop()

        except Exception as e:
            logger.error(f"Erreur processus GUI: {e}")
        finally:
            self.running = False

    def _fermer_interface(self):
        """Ferme interface proprement."""
        self.running = False
        logger.info("Interface fermée")

    def arreter(self):
        """Arrête processus GUI."""
        self.running = False