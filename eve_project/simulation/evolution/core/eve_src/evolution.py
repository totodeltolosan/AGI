# eve_src/evolution.py
"""Définit le MondeEvoManager, le gestionnaire de la méta-évolution."""
import logging
import random
import numpy as np
from eve_src.config import CONFIG

# ========================================================================
# ===== NOUVEAU : Configuration du système de journalisation (logging) =====
# ========================================================================
# Crée un logger spécifique pour l'histoire de l'évolution
log_evol = logging.getLogger("evolution_logger")
log_evol.setLevel(logging.INFO)
# Crée un gestionnaire de fichier pour écrire dans eve_history.log
file_handler = logging.FileHandler("eve_history.log", mode="w", encoding="utf-8")
# Crée un formateur simple : Âge de la sim - Message
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)
# Ajoute le gestionnaire au logger (s'il n'en a pas déjà un)
if not log_evol.hasHandlers():
    log_evol.addHandler(file_handler)
# ========================================================================


class MondeEvoManager:
    """Surveille la simulation et fait évoluer les lois du monde de manière dynamique."""

    def __init__(self):
        """Initialise les paliers d'évolution et les indicateurs de performance (KPIs)."""
        self.seuils = {
            "insecte": {"vegetal_pop": 1000, "debloque": False},
            "animal": {"insecte_pop": 400, "debloque": False},
            "humanoide": {"complexite_cerveau": 50.0, "debloque": False},
            "toxicite": {"pop_moyenne_animal": 150, "debloque": False},
            "epidemie": {"age_sim": 15000, "debloque": False},
            "sexuee": {"tribus_stables": 5, "debloque": False},
        }
        self.kpis = {
            "pop_histoire_animal": [],
            "tribus_stables_compteur": 0,
            "complexite_max_observee": 0.0,
        }
        self.dernier_evenement = "La Genèse"
        log_evol.info(f"Âge 0: {self.dernier_evenement}")

    def update(self, stats):
        """
        Analyse les statistiques du monde à chaque cycle et déclenche potentiellement
        des événements évolutifs.
        """
        self._mettre_a_jour_kpis(stats)

        nouvel_event = self._verifier_deblocages(stats)
        if nouvel_event:
            self.dernier_evenement = nouvel_event
            log_evol.info(f"Âge {stats['age']}: {nouvel_event}")
            return nouvel_event

        if stats["age"] % 2000 == 1 and stats["age"] > 1:
            ajustement_event = self._ajuster_difficulte(stats)
            if ajustement_event:
                self.dernier_evenement = ajustement_event
                log_evol.info(f"Âge {stats['age']}: {ajustement_event}")

        return None

    def _mettre_a_jour_kpis(self, stats):
        """Met à jour les indicateurs de performance clés."""
        self.kpis["pop_histoire_animal"].append(stats["pop_animal"])
        if len(self.kpis["pop_histoire_animal"]) > 1000:
            self.kpis["pop_histoire_animal"].pop(0)

        if stats["complexite_max"] > self.kpis["complexite_max_observee"]:
            self.kpis["complexite_max_observee"] = stats["complexite_max"]

    def _verifier_deblocages(self, stats):
        """Vérifie si un palier majeur a été atteint pour débloquer une nouvelle loi ou espèce."""
        if (
            not self.seuils["insecte"]["debloque"]
            and stats["pop_vegetal"] > self.seuils["insecte"]["vegetal_pop"]
        ):
            self.seuils["insecte"]["debloque"] = True
            return "Apparition des Insectes !"

        if (
            not self.seuils["animal"]["debloque"]
            and stats["pop_insecte"] > self.seuils["animal"]["insecte_pop"]
        ):
            self.seuils["animal"]["debloque"] = True
            return "L'âge des Animaux commence !"

        if (
            not self.seuils["sexuee"]["debloque"]
            and len(stats["tribus"]) > self.seuils["sexuee"]["tribus_stables"]
        ):
            self.kpis["tribus_stables_compteur"] += 1
            if self.kpis["tribus_stables_compteur"] > 1000:
                CONFIG["genetique"]["mode_reproduction"] = "sexuee"
                self.seuils["sexuee"]["debloque"] = True
                return "La reproduction sexuée apparaît !"
        else:
            self.kpis["tribus_stables_compteur"] = 0

        if (
            not self.seuils["humanoide"]["debloque"]
            and self.kpis["complexite_max_observee"]
            > self.seuils["humanoide"]["complexite_cerveau"]
        ):
            self.seuils["humanoide"]["debloque"] = True
            return "ÉVÉNEMENT COSMIQUE : L'INTELLIGENCE ÉMERGE !"

        return None

    def _ajuster_difficulte(self, stats):
        """Rend le monde légèrement plus difficile si la population est stable et prospère."""
        if len(self.kpis["pop_histoire_animal"]) < 1000:
            return None

        pop_moyenne_animaux = np.mean(self.kpis["pop_histoire_animal"])
        if pop_moyenne_animaux > 100:
            choix = random.random()
            if choix < 0.5:
                CONFIG["cycles_temporels"]["modificateur_ressources_hiver"] *= 0.98
                return "Le climat se refroidit légèrement..."
            elif choix < 0.8:
                CONFIG["evolution"]["gain_energie_vegetal"] *= 0.99
                CONFIG["evolution"]["gain_energie_insecte"] *= 0.99
                return "La valeur nutritive de la nourriture diminue..."
            else:
                CONFIG["evolution"]["cout_de_vie"] *= 1.01
                return "Le métabolisme de base devient plus coûteux..."
        return None
