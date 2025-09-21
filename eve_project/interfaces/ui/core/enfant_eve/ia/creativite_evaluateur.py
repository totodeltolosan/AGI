import time
import logging
from typing import Dict, List, Any
from collections import deque

logger = logging.getLogger(__name__)


class EvaluateurNouveaute:
    """
    Évalue la nouveauté et l'originalité des créations avec apprentissage.
    Respecte Directive 61 avec focus sur l'évaluation uniquement.
    """

    def __init__(self):
        """TODO: Add docstring."""
        self.creations_precedentes = deque(maxlen=50)  # Limite mémoire
        self.patterns_detectes = {}
        self.tendances_stylistiques = {}

    def evaluer_nouveaute(self, nouveau_plan: Dict) -> float:
        """Évalue le niveau de nouveauté avec analyse sophistiquée."""
        try:
            if not self.creations_precedentes:
                return 1.0  # Première création = totalement nouvelle

            score_nouveaute = 0.0

            # Analyse forme (25% du score)
            score_nouveaute += self._evaluer_nouveaute_forme(nouveau_plan) * 0.25

            # Analyse matériaux (25% du score)
            score_nouveaute += self._evaluer_nouveaute_materiaux(nouveau_plan) * 0.25

            # Analyse complexité (20% du score)
            score_nouveaute += self._evaluer_nouveaute_complexite(nouveau_plan) * 0.20

            # Analyse innovation technique (15% du score)
            score_nouveaute += self._evaluer_innovations(nouveau_plan) * 0.15

            # Analyse contextuelle (15% du score)
            score_nouveaute += self._evaluer_nouveaute_contextuelle(nouveau_plan) * 0.15

            return min(1.0, max(0.0, score_nouveaute))

        except Exception as e:
            logger.error(f"Erreur évaluation nouveauté: {e}")
            return 0.5

    def _evaluer_nouveaute_forme(self, plan: Dict) -> float:
        """Évalue la nouveauté de la forme."""
        forme_actuelle = plan.get("forme", "rectangulaire")
        formes_precedentes = [p.get("forme") for p in self.creations_precedentes]

        # Compter occurrences forme
        nb_occurrences = formes_precedentes.count(forme_actuelle)
        total_creations = len(self.creations_precedentes)

        if nb_occurrences == 0:
            return 1.0  # Forme jamais utilisée

        frequence = nb_occurrences / total_creations
        return max(0.0, 1.0 - frequence)

    def _evaluer_nouveaute_materiaux(self, plan: Dict) -> float:
        """Évalue la nouveauté de la combinaison de matériaux."""
        materiaux_actuels = set(plan.get("materiaux_autorises", []))

        scores_similitude = []
        for precedent in self.creations_precedentes:
            materiaux_precedents = set(precedent.get("materiaux_autorises", []))

            # Coefficient de Jaccard pour similarité
            intersection = len(materiaux_actuels.intersection(materiaux_precedents))
            union = len(materiaux_actuels.union(materiaux_precedents))

            similarite = intersection / union if union > 0 else 0
            scores_similitude.append(similarite)

        if not scores_similitude:
            return 1.0

        max_similarite = max(scores_similitude)
        return max(0.0, 1.0 - max_similarite)

    def _evaluer_nouveaute_complexite(self, plan: Dict) -> float:
        """Évalue la nouveauté du niveau de complexité."""
        complexite_actuelle = plan.get("complexite_max", 5)
        complexites_precedentes = [
            p.get("complexite_max", 5) for p in self.creations_precedentes
        ]

        if not complexites_precedentes:
            return 1.0

        # Évaluer si c'est un nouveau niveau de complexité
        max_complexite_precedente = max(complexites_precedentes)

        if complexite_actuelle > max_complexite_precedente:
            return 1.0  # Nouveau record de complexité

        # Évaluer rareté du niveau de complexité
        nb_meme_complexite = complexites_precedentes.count(complexite_actuelle)
        frequence_complexite = nb_meme_complexite / len(complexites_precedentes)

        return max(0.0, 1.0 - frequence_complexite)

    def _evaluer_innovations(self, plan: Dict) -> float:
        """Évalue les innovations techniques."""
        score = 0.0

        innovations_possibles = [
            "regles_avancees",
            "proportions_dorees",
            "integration_paysage",
            "innovations_technologiques",
            "durabilite_environnementale",
            "resistance_elements",
            "ventilation_naturelle",
            "eclairage_optimise",
        ]

        innovations_actuelles = [key for key in innovations_possibles if plan.get(key)]

        if not innovations_actuelles:
            return 0.0

        # Vérifier si innovations jamais utilisées avant
        for innovation in innovations_actuelles:
            precedent_usage = any(p.get(innovation) for p in self.creations_precedentes)
            if not precedent_usage:
                score += 0.5  # Innovation jamais vue
            else:
                score += 0.1  # Innovation rare

        return min(1.0, score)

    def _evaluer_nouveaute_contextuelle(self, plan: Dict) -> float:
        """Évalue la nouveauté contextuelle (adaptation environnement)."""
        architecture_type = plan.get("architecture_type", "standard")
        types_precedents = [
            p.get("architecture_type", "standard") for p in self.creations_precedentes
        ]

        nb_meme_type = types_precedents.count(architecture_type)
        if nb_meme_type == 0:
            return 1.0

        frequence = nb_meme_type / len(types_precedents)
        return max(0.0, 1.0 - frequence)

    def enregistrer_creation(self, plan: Dict):
        """Enregistre une création avec analyse des patterns."""
        try:
            plan_enregistre = plan.copy()
            plan_enregistre["timestamp"] = time.time()

            self.creations_precedentes.append(plan_enregistre)

            # Mise à jour patterns détectés
            self._mettre_a_jour_patterns(plan_enregistre)

            # Analyse tendances stylistiques
            self._analyser_tendances_stylistiques()

        except Exception as e:
            logger.error(f"Erreur enregistrement création: {e}")

    def _mettre_a_jour_patterns(self, plan: Dict):
        """Met à jour la détection de patterns créatifs."""
        forme = plan.get("forme", "inconnue")
        self.patterns_detectes[forme] = self.patterns_detectes.get(forme, 0) + 1

    def _analyser_tendances_stylistiques(self):
        """Analyse les tendances émergentes dans les créations."""
        if len(self.creations_precedentes) < 5:
            return

        # Analyse des 5 dernières créations pour tendances
        recentes = list(self.creations_precedentes)[-5:]

        # Tendance matériaux
        materiaux_recents = {}
        for creation in recentes:
            for materiau in creation.get("materiaux_autorises", []):
                materiaux_recents[materiau] = materiaux_recents.get(materiau, 0) + 1

        # Identifier matériau le plus utilisé récemment
        if materiaux_recents:
            materiau_tendance = max(materiaux_recents, key=materiaux_recents.get)
            self.tendances_stylistiques["materiau_favori"] = materiau_tendance

        # Tendance complexité
        complexites_recentes = [c.get("complexite_max", 5) for c in recentes]
        self.tendances_stylistiques["complexite_moyenne"] = sum(
            complexites_recentes
        ) / len(complexites_recentes)

    def obtenir_tendances(self) -> Dict:
        """Retourne l'analyse des tendances créatives."""
        return {
            "patterns_detectes": dict(self.patterns_detectes),
            "tendances_stylistiques": dict(self.tendances_stylistiques),
            "nb_creations_total": len(self.creations_precedentes),
            "diversite_formes": len(
                set(p.get("forme") for p in self.creations_precedentes)
            ),
            "evolution_complexite": self._calculer_evolution_complexite(),
        }

    def _calculer_evolution_complexite(self) -> str:
        """Calcule l'évolution de la complexité dans le temps."""
        if len(self.creations_precedentes) < 3:
            return "insuffisant"

        complexites = [p.get("complexite_max", 5) for p in self.creations_precedentes]
        debut = sum(complexites[:3]) / 3
        fin = sum(complexites[-3:]) / 3

        if fin > debut * 1.2:
            return "croissante"
        elif fin < debut * 0.8:
            return "décroissante"
        else:
            return "stable"

    def detecter_specialisation(self) -> str:
        """Détecte la spécialisation artistique émergente."""
        if len(self.creations_precedentes) < 10:
            return "en_developpement"

        # Analyser récurrence de styles
        formes_recentes = [
            p.get("forme", "") for p in list(self.creations_precedentes)[-5:]
        ]
        forme_dominante = (
            max(set(formes_recentes), key=formes_recentes.count)
            if formes_recentes
            else "variee"
        )

        specialisations = {
            "organique_complexe": "Architecture Organique",
            "circulaire_approx": "Géométrie Circulaire",
            "spirale_simple": "Formes Spiralées",
            "rectangulaire": "Classique Géométrique",
        }

        return specialisations.get(forme_dominante, "Style Éclectique")

    def evaluer_niveau_artistique(self, metriques: Dict) -> str:
        """Évalue le niveau de maturité artistique actuel."""
        nb_creations = len(self.creations_precedentes)
        score_moyen = metriques.get("score_moyen_nouveaute", 0)
        diversite = metriques.get("diversite_stylistique", 0)
        innovations = metriques.get("innovations_introduites", 0)

        score_global = (
            min(20, nb_creations)  # Max 20 points pour quantité
            + (score_moyen * 30)  # Max 30 points pour nouveauté
            + (diversite * 5)  # 5 points par style différent
            + (innovations * 10)  # 10 points par innovation
        )

        if score_global >= 80:
            return "Maître Artiste"
        elif score_global >= 60:
            return "Artiste Confirmé"
        elif score_global >= 40:
            return "Créateur Prometteur"
        elif score_global >= 20:
            return "Apprenti Créatif"
        else:
            return "Débutant Créatif"