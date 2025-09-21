"""
Processus enfant 2 - Cerveau IA (Directive 21).
Contient logique principale et modules cognitifs.
"""

import logging
import time
import multiprocessing as mp
from enfant_eve.ia.cerveau import Cerveau

logger = logging.getLogger(__name__)


class ProcessusIA(mp.Process):
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, queues, config):
        super().__init__()
        self.queues = queues
        self.config = config
        self.running = True
        self.cerveau = None

    def run(self):
        """Boucle principale processus IA."""
        logger.info("Processus IA démarré")

        try:
            self.cerveau = Cerveau(self.queues, self.config)

            while self.running:
                self.cerveau.cycle_principal()
                time.sleep(0.05)

        except Exception as e:
            logger.error(f"Erreur processus IA: {e}")
        finally:
            logger.info("Processus IA arrêté")

    def arreter(self):
        """Arrête processus IA."""
        self.running = False
        if self.cerveau:
            self.cerveau.arreter()