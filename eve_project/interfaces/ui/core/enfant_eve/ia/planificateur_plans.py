import logging

logger = logging.getLogger(__name__)


class Plan:
    """
    Classe Plan avec compatibilité dictionnaire pour l'interface avec le cerveau.
    Implémente les méthodes dict nécessaires : get(), keys(), items(), etc.
    """

    def __init__(self, nom, actions=None):
        """TODO: Add docstring."""
        self.nom = nom
        self.actions_initiales = actions or []
        self.actions_recuperees = []
        self.index_actuel = 0
        self.priorite = "normale"
        self.timestamp_creation = None
        self.duree_estimee = len(self.actions_initiales) * 5

        # Attributs pour compatibilité dictionnaire
        self._dict_representation = {
            "nom": self.nom,
            "type": "plan",
            "actions": self.actions_initiales,
            "index_actuel": self.index_actuel,
            "priorite": self.priorite,
            "duree_estimee": self.duree_estimee,
            "status": "actif",
        }

    def prochaine_action(self):
        """Retourne la prochaine action à exécuter"""
        if self.index_actuel < len(self.actions_initiales):
            action = self.actions_initiales[self.index_actuel]
            self.index_actuel += 1
            self._dict_representation["index_actuel"] = self.index_actuel
            return action
        return None

    def a_des_actions(self):
        """Vérifie s'il reste des actions à exécuter"""
        return self.index_actuel < len(self.actions_initiales)

    def progression(self):
        """Retourne le pourcentage de progression du plan"""
        if not self.actions_initiales:
            return 100.0
        return (self.index_actuel / len(self.actions_initiales)) * 100.0

    def get(self, key, default=None):
        """Méthode get() comme les dictionnaires"""
        self._dict_representation.update(
            {
                "nom": self.nom,
                "actions": self.actions_initiales,
                "index_actuel": self.index_actuel,
                "priorite": self.priorite,
                "duree_estimee": self.duree_estimee,
                "progression": self.progression(),
            }
        )
        return self._dict_representation.get(key, default)

    def keys(self):
        """Retourne les clés comme un dictionnaire"""
        self._dict_representation.update(
            {
                "nom": self.nom,
                "actions": self.actions_initiales,
                "index_actuel": self.index_actuel,
                "priorite": self.priorite,
                "duree_estimee": self.duree_estimee,
                "progression": self.progression(),
            }
        )
        return self._dict_representation.keys()

    def items(self):
        """Retourne les items comme un dictionnaire"""
        self._dict_representation.update(
            {
                "nom": self.nom,
                "actions": self.actions_initiales,
                "index_actuel": self.index_actuel,
                "priorite": self.priorite,
                "duree_estimee": self.duree_estimee,
                "progression": self.progression(),
            }
        )
        return self._dict_representation.items()

    def to_dict(self):
        """Conversion explicite en dictionnaire"""
        return {
            "nom": self.nom,
            "type": "plan",
            "actions": self.actions_initiales.copy(),
            "index_actuel": self.index_actuel,
            "priorite": self.priorite,
            "duree_estimee": self.duree_estimee,
            "progression": self.progression(),
            "actions_restantes": len(self.actions_initiales) - self.index_actuel,
            "status": "terminé" if not self.a_des_actions() else "actif",
        }

    def __str__(self):
        """Représentation string du plan"""
        return f"Plan('{self.nom}', {len(self.actions_initiales)} actions, {self.progression():.1f}% complété)"

    """TODO: Add docstring."""
    def __repr__(self):
        return self.__str__()


class PlanDeconstruction(Plan):
    """Plan de déconstruction pour récupérer des matériaux"""
        """TODO: Add docstring."""

    def __init__(self, plan_echoue):
        super().__init__(f"Deconstruction de {plan_echoue.nom}")
        self.plan_origine = plan_echoue
        self.priorite = "haute"


class PlanObservation(Plan):
    """TODO: Add docstring."""
    """Plan d'observation systématique d'une cible"""

    def __init__(self, cible_id):
        actions_observation = [
            {"type": "OBSERVER", "cible": cible_id, "duree": 30},
            {"type": "ANALYSER_COMPORTEMENT", "cible": cible_id},
            {"type": "DOCUMENTER_OBSERVATIONS", "sujet": cible_id},
        ]
        super().__init__(f"Observation de {cible_id}", actions_observation)
        self.cible = cible_id


    """TODO: Add docstring."""
class PlanInteractionLimitee(Plan):
    """Plan d'interaction prudente avec une entité"""

    def __init__(self, cible_id):
        actions_interaction = [
            {"type": "APPROCHE_PRUDENTE", "cible": cible_id},
            {"type": "INTERACTION_MINIMALE", "cible": cible_id},
            {"type": "EVALUER_REACTION", "cible": cible_id},
        ]
        super().__init__(f"Interaction prudente avec {cible_id}", actions_interaction)
        self.cible = cible_id

    """TODO: Add docstring."""

class PlanEtudeAnomalie(Plan):
    """Plan d'étude scientifique d'une anomalie détectée"""

    def __init__(self, anomalie_detectee):
        actions_etude = [
            {"type": "SCANNER_ANOMALIE", "anomalie": anomalie_detectee},
            {"type": "COLLECTER_ECHANTILLONS", "source": anomalie_detectee},
            {"type": "ANALYSER_DONNEES", "anomalie": anomalie_detectee},
            {"type": "FORMULER_HYPOTHESES", "sujet": anomalie_detectee},
        ]
        super().__init__(
            f"Etude scientifique de l'anomalie: {anomalie_detectee}", actions_etude
        )
        self.anomalie = anomalie_detectee
            """TODO: Add docstring."""


class PlanRecuperationEquipement(Plan):
    """Plan de récupération d'équipement après une mort"""

    def __init__(self, lieu_de_la_mort):
        actions_recuperation = [
            {"type": "NAVIGUER_VERS", "destination": lieu_de_la_mort},
            {"type": "SECURISER_ZONE", "position": lieu_de_la_mort},
            {"type": "RECUPERER_OBJETS", "position": lieu_de_la_mort},
            {"type": "RETOUR_SECURISE"},
        ]
        super().__init__(
            f"Récupération de l'équipement à {lieu_de_la_mort}", actions_recuperation
        )
        self.lieu_mort = lieu_de_la_mort
            """TODO: Add docstring."""
        self.priorite = "critique"


class PlanUrgence(Plan):
    """Plan d'urgence pour situations critiques"""

    def __init__(self, nom, actions_urgence=None):
        actions_urgence = actions_urgence or [
            {"type": "EVALUER_SITUATION", "priorite": "critique"},
            {"type": "ACTION_IMMEDIATE", "mode": "survie"},
        ]
        super().__init__(nom, actions_urgence)
        self.priorite = "critique"