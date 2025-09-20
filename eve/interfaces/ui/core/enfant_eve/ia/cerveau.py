# cerveau.py
"""
Orchestrateur global du cerveau IA. Initialise les modules cognitifs
et délègue la boucle principale et les sous-processus aux modules enfants.
Respect strict des 150 lignes.
"""

import logging
from enfant_eve.ia.modele_monde import ModeleMonde
from enfant_eve.ia.planificateur import Planificateur
from enfant_eve.ia.comportement import ModeleComportemental
from enfant_eve.ia.ethique import ModuleEthique
from enfant_eve.ia.raisonnement import ModuleRaisonnement
from enfant_eve.ia.abstraction import ModuleAbstraction
from enfant_eve.ia.creativite import ModuleCreativite
from enfant_eve.ia.arbitrage import ModuleArbitrage
from enfant_eve.ia import cerveau_cycle

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Cerveau:
    """
    Classe principale orchestrant l'IA.
    """

    def __init__(self, config, q_jeu_ia, q_ia_jeu, q_ia_gui, q_mentor_ia):
        """TODO: Add docstring."""
        self.running = True
        self.config = config
        self.queues = {
            "jeu_vers_ia": q_jeu_ia,
            "ia_vers_jeu": q_ia_jeu,
            "ia_vers_gui": q_ia_gui,
            "mentor_vers_ia": q_mentor_ia,
        }

        # États internes
        self.mode_actuel = "DEMARRAGE"
        self.progres_recent = 0.0
        self.dernier_plan_genere = None
        self.action_en_cours = None

        # Initialisation des modules cognitifs
        self.modele_monde = ModeleMonde()
        self.comportement = ModeleComportemental(self.config.get("emotions", {}))
        self.raisonnement = ModuleRaisonnement(self.modele_monde)
        self.planificateur = Planificateur(self.modele_monde, self.config)
        self.ethique = ModuleEthique(self.config.get("ethique", {}))
        self.abstraction = ModuleAbstraction(self.modele_monde)
        self.creativite = ModuleCreativite(
            self.config.get("creativite", {}), self.modele_monde
        )
        self.arbitre = ModuleArbitrage(self.config.get("arbitrage", {}))

        logger.info("Cerveau initialisé avec tous les modules cognitifs.")

    def run(self):
        """
        Lance la séquence de démarrage (Directive 54) puis la boucle principale.
        """
        try:
            cerveau_cycle.sequence_demarrage(self)
            cerveau_cycle.boucle_principale(self)
        except KeyboardInterrupt:
            logger.info("Arrêt manuel reçu.")
        finally:
            self.running = False

    def lancer_diagnostic(self):
        """
        Mode maintenance rapide : diagnostic IA.
        """
        logger.warning("Diagnostic IA déclenché par le mentor.")
        self.mode_actuel = "MAINTENANCE"