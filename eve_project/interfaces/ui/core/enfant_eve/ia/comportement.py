"""
Modèle comportemental et émotionnel (Directive 29).
Gère personnalité et états émotionnels IA.
"""

import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ModeleComportemental:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, config_emotions):
        self.config = config_emotions
        self.emotions_actuelles = self._initialiser_emotions()
        self.traits_personnalite = self._initialiser_personnalite()
        self.historique_emotions = []

    def _initialiser_emotions(self) -> Dict[str, float]:
        """Initialise états émotionnels de base."""
        return {
            "curiosite": 0.7,
            "confiance": 0.5,
            "frustration": 0.1,
            "satisfaction": 0.5,
            "prudence": 0.6,
            "determination": 0.8,
        }

    def _initialiser_personnalite(self) -> Dict[str, float]:
        """Initialise traits de personnalité fixes."""
        return {
            "ouverture": 0.9,
            "conscienciosité": 0.8,
            "extraversion": 0.3,
            "agreable": 0.7,
            "stabilite_emotionnelle": 0.6,
        }

    def mettre_a_jour_emotions(self, evenement: Dict[str, Any]):
        """Met à jour émotions selon événement."""
        type_evenement = evenement.get("type", "")
        impact = evenement.get("impact", 0.0)

        if type_evenement == "succes_action":
            self._ajuster_emotion("satisfaction", impact * 0.3)
            self._ajuster_emotion("confiance", impact * 0.2)
            self._ajuster_emotion("frustration", -impact * 0.1)

        elif type_evenement == "echec_action":
            self._ajuster_emotion("frustration", impact * 0.4)
            self._ajuster_emotion("confiance", -impact * 0.2)
            self._ajuster_emotion("determination", impact * 0.1)

        elif type_evenement == "decouverte":
            self._ajuster_emotion("curiosite", impact * 0.5)
            self._ajuster_emotion("satisfaction", impact * 0.2)

        elif type_evenement == "danger":
            self._ajuster_emotion("prudence", impact * 0.6)
            self._ajuster_emotion("confiance", -impact * 0.3)

        self._enregistrer_etat_emotionnel()

    def _ajuster_emotion(self, emotion: str, delta: float):
        """Ajuste niveau d'une émotion."""
        if emotion in self.emotions_actuelles:
            nouvelle_valeur = self.emotions_actuelles[emotion] + delta
            self.emotions_actuelles[emotion] = max(0.0, min(1.0, nouvelle_valeur))

    def _enregistrer_etat_emotionnel(self):
        """Enregistre état émotionnel dans historique."""
        etat = {"timestamp": time.time(), "emotions": self.emotions_actuelles.copy()}

        self.historique_emotions.append(etat)

        if len(self.historique_emotions) > 1000:
            self.historique_emotions = self.historique_emotions[-800:]

    def calculer_motivation(self, action: str) -> float:
        """Calcule motivation pour une action donnée."""
        motivation_base = 0.5

        if "exploration" in action.lower():
            motivation_base += self.emotions_actuelles["curiosite"] * 0.3

        if "construction" in action.lower():
            motivation_base += self.emotions_actuelles["satisfaction"] * 0.2
            motivation_base += self.traits_personnalite["conscienciosité"] * 0.2

        if "combat" in action.lower():
            motivation_base += self.emotions_actuelles["determination"] * 0.4
            motivation_base -= self.emotions_actuelles["prudence"] * 0.3

        return max(0.0, min(1.0, motivation_base))

    def obtenir_modificateur_comportement(self) -> Dict[str, float]:
        """Obtient modificateurs comportementaux actuels."""
        return {
            "vitesse_decision": 1.0 - self.emotions_actuelles["prudence"] * 0.5,
            "prise_risque": self.emotions_actuelles["confiance"] * 0.7,
            "persistence": self.emotions_actuelles["determination"] * 0.8,
            "exploration": self.emotions_actuelles["curiosite"] * 0.9,
        }

    def evoluer_personnalite(self, experience: Dict[str, Any]):
        """Fait évoluer traits personnalité selon expérience."""
        type_exp = experience.get("type", "")
        intensite = experience.get("intensite", 0.1)

        if type_exp == "reussite_planification":
            self.traits_personnalite["conscienciosité"] += intensite * 0.01

        elif type_exp == "decouverte_majeure":
            self.traits_personnalite["ouverture"] += intensite * 0.01

        elif type_exp == "resolution_conflit":
            self.traits_personnalite["stabilite_emotionnelle"] += intensite * 0.01

        for trait in self.traits_personnalite:
            self.traits_personnalite[trait] = max(
                0.0, min(1.0, self.traits_personnalite[trait])
            )