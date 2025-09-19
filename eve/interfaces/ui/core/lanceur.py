"""
Lanceur principal projet Le Simulateur (Directive 60).
Orchestrateur processus et interface utilisateur.
"""

import logging
import json
import multiprocessing as mp
from lanceur_utils import (
    charger_configuration,
    initialiser_logging,
    verifier_dependances,
    creer_queues_communication,
    nettoyer_ressources,
)
from lanceur_constantes import MAX_RESTART_ATTEMPTS, PROCESS_CHECK_INTERVAL
from processus_ia import ProcessusIA
from gestionnaire_gui import GestionnaireGUI

logger = logging.getLogger(__name__)


class SimulateurHybride:
    def __init__(self):
        self.config = charger_configuration()
        self.queues = creer_queues_communication()
        self.processus = {}
        self.running = True
        self.restart_count = 0

    def demarrer(self):
        """Démarre le simulateur complet."""
        initialiser_logging()
        logger.info("Démarrage du Simulateur Le Simulateur")

        if not verifier_dependances():
            logger.error("Dépendances manquantes")
            return False

        try:
            self._demarrer_processus()
            self._boucle_surveillance()
            return True
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur")
            return True
        except Exception as e:
            logger.error(f"Erreur critique: {e}")
            return False
        finally:
            self._arreter_proprement()

    def _demarrer_processus(self):
        """Démarre tous les processus du simulateur."""
        logger.info("Démarrage des processus...")

        self.processus["ia"] = ProcessusIA(self.queues, self.config)
        self.processus["gui"] = GestionnaireGUI(self.queues, self.config)

        for nom, proc in self.processus.items():
            proc.start()
            logger.info(f"Processus {nom} démarré (PID: {proc.pid})")

    def _boucle_surveillance(self):
        """Boucle de surveillance des processus."""
        while self.running:
            if not self._verifier_processus():
                if self.restart_count < MAX_RESTART_ATTEMPTS:
                    self._redemarrer_processus_defaillants()
                else:
                    logger.error("Trop de redémarrages, arrêt du simulateur")
                    break

            time.sleep(PROCESS_CHECK_INTERVAL)

    def _verifier_processus(self):
        """Vérifie l'état de tous les processus."""
        tous_vivants = True

        for nom, proc in self.processus.items():
            if not proc.is_alive():
                logger.warning(f"Processus {nom} arrêté (PID: {proc.pid})")
                tous_vivants = False

        return tous_vivants

    def _redemarrer_processus_defaillants(self):
        """Redémarre les processus qui ont échoué."""
        self.restart_count += 1
        logger.info(
            f"Tentative de redémarrage {self.restart_count}/{MAX_RESTART_ATTEMPTS}"
        )

        for nom, proc in list(self.processus.items()):
            if not proc.is_alive():
                proc.terminate()
                proc.join(timeout=5)

                if nom == "ia":
                    nouveau_proc = ProcessusIA(self.queues, self.config)
                elif nom == "gui":
                    nouveau_proc = GestionnaireGUI(self.queues, self.config)

                nouveau_proc.start()
                self.processus[nom] = nouveau_proc
                logger.info(f"Processus {nom} redémarré")

    def _arreter_proprement(self):
        """Arrête proprement tous les processus."""
        logger.info("Arrêt du simulateur...")
        self.running = False

        processus_list = list(self.processus.values())
        nettoyer_ressources(self.queues, processus_list)

        logger.info("Simulateur arrêté")


def main():
    """Point d'entrée principal du simulateur."""
    mp.set_start_method("spawn", force=True)

    simulateur = SimulateurHybride()
    success = simulateur.demarrer()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
