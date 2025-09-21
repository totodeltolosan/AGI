import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class CacheCreativite:
    """
    Gestionnaire de cache pour les plans de construction.
    Respecte Directive 61 avec focus sur la gestion du cache uniquement.
    """

    def __init__(self, duree_cache: int = 300):  # 5 minutes par défaut
        """TODO: Add docstring."""
        self._cache_plans = {}
        self._cache_timestamp = 0
        self._duree_cache = duree_cache

    def obtenir_plan(
        self, objectif: str, phase_de_vie: str, config: Dict
    ) -> Optional[Dict]:
        """Obtient un plan du cache s'il est valide."""
        if not self._cache_valide():
            return None

        cache_key = f"{objectif}_{phase_de_vie}_{hash(str(config))}"
        return self._cache_plans.get(cache_key)

    def stocker_plan(self, objectif: str, phase_de_vie: str, config: Dict, plan: Dict):
        """Stocke un plan dans le cache."""
        cache_key = f"{objectif}_{phase_de_vie}_{hash(str(config))}"
        self._cache_plans[cache_key] = plan
        self._cache_timestamp = time.time()

    def _cache_valide(self) -> bool:
        """Vérifie la validité du cache."""
        return (time.time() - self._cache_timestamp) < self._duree_cache

    def taille(self) -> int:
        """Retourne la taille du cache."""
        return len(self._cache_plans)

    def nettoyer_cache(self):
        """Nettoie le cache expiré."""
        if not self._cache_valide():
            self._cache_plans.clear()


class CalculateurMetriques:
    """
    Calculateur de métriques et utilitaires pour la créativité.
    Respecte Directive 61 avec focus sur les calculs uniquement.
    """

    """TODO: Add docstring."""
    def __init__(self):
        pass

    def calculer_dimensions_intelligentes(
        self, objectif: str, phase_de_vie: str
    ) -> List[int]:
        """Calcule des dimensions intelligentes selon objectif et phase."""
        try:
            # Dimensions de base par objectif
            dimensions_base = {
                "abri": [5, 3, 5],
                "maison": [7, 4, 7],
                "atelier": [9, 4, 6],
                "ferme": [12, 3, 8],
                "chateau": [20, 8, 20],
                "tour": [6, 12, 6],
                "pont": [20, 3, 4],
                "temple": [15, 6, 15],
                "construction_generale": [8, 4, 8],
            }

            dimensions = dimensions_base.get(
                objectif, dimensions_base["construction_generale"]
            )

            # Ajustement selon phase de vie
            facteurs_phase = {
                "ENFANCE": 0.8,
                "ADOLESCENCE": 1.0,
                "ADULTE": 1.3,
                "MAITRISE": 1.6,
            }

            facteur = facteurs_phase.get(phase_de_vie, 1.0)
            dimensions_ajustees = [max(3, int(d * facteur)) for d in dimensions]

            # Contraintes réalistes
            dimensions_ajustees[0] = min(50, dimensions_ajustees[0])  # Largeur max 50
            dimensions_ajustees[1] = min(30, dimensions_ajustees[1])  # Hauteur max 30
            dimensions_ajustees[2] = min(
                50, dimensions_ajustees[2]
            )  # Profondeur max 50

            return dimensions_ajustees

        except Exception as e:
            logger.error(f"Erreur calcul dimensions: {e}")
            return [8, 4, 8]

    def analyser_environnement_local(self, modele_monde) -> Dict:
        """Analyse sophistiquée de l'environnement local."""
        try:
            environnement = {
                "biome": "tempéré",
                "altitude": 70,
                "climat": "tempéré",
                "ressources_locales": [],
                "contraintes_terrain": [],
                "opportunites_construction": [],
            }

            # Obtenir données du modèle monde
            if hasattr(modele_monde, "get_etat_environnement"):
                env_data = modele_monde.get_etat_environnement()
                environnement["biome"] = env_data.get("biome", "tempéré")
                environnement["altitude"] = modele_monde.get_position_joueur()[1]

            # Analyser composition terrain
            connaissances = getattr(modele_monde, "graphe_connaissances", {}).get(
                "noeuds", {}
            )
            if "composition_terrain" in connaissances:
                terrain = connaissances["composition_terrain"]

                # Identifier ressources locales
                for ressource, quantite in terrain.items():
                    if quantite > 5:
                        environnement["ressources_locales"].append(ressource)

                # Analyser contraintes terrain
                if terrain.get("water", 0) > 10:
                    environnement["contraintes_terrain"].append("zone_humide")
                if terrain.get("lava", 0) > 0:
                    environnement["contraintes_terrain"].append("danger_volcanique")

            return environnement

        except Exception as e:
            logger.error(f"Erreur analyse environnement: {e}")
            return {"biome": "inconnu", "altitude": 70, "climat": "neutre"}

    def valider_liste_blocs(self, liste_blocs: List[Dict]) -> List[Dict]:
        """Valide et nettoie une liste de blocs."""
        try:
            blocs_valides = []

            for bloc in liste_blocs:
                if not isinstance(bloc, dict):
                    continue

                # Validation position
                position = bloc.get("position")
                if not isinstance(position, list) or len(position) != 3:
                    continue

                # Validation matériau
                materiau = bloc.get("materiau")
                if not materiau or not isinstance(materiau, str):
                    continue

                # Normalisation bloc
                bloc_normalise = {
                    "position": [int(position[0]), int(position[1]), int(position[2])],
                    "materiau": materiau.lower(),
                    "type": bloc.get("type", "construction"),
                    "importance": bloc.get("importance", "normale"),
                }

                blocs_valides.append(bloc_normalise)

            # Supprimer doublons par position
            positions_vues = set()
            blocs_uniques = []

            for bloc in blocs_valides:
                pos_tuple = tuple(bloc["position"])
                if pos_tuple not in positions_vues:
                    positions_vues.add(pos_tuple)
                    blocs_uniques.append(bloc)

            logger.info(
                f"Validation: {len(liste_blocs)} -> {len(blocs_uniques)} blocs valides"
            )
            return blocs_uniques

        except Exception as e:
            logger.error(f"Erreur validation blocs: {e}")
            return []

    def optimiser_construction_contextuelle(
        self, liste_blocs: List[Dict], contexte: Dict
    ) -> List[Dict]:
        """Optimise la construction selon le contexte."""
        try:
            if not liste_blocs:
                return liste_blocs

            # Tri par priorité de construction (fondations d'abord)
            ordre_importance = {
                "fondations": 0,
                "structurelle": 1,
                "normale": 2,
                "decorative": 3,
            }
                """TODO: Add docstring."""

            def priorite_bloc(bloc):
                type_bloc = bloc.get("type", "normale")
                if "fondation" in type_bloc:
                    return 0
                importance = bloc.get("importance", "normale")
                return ordre_importance.get(importance, 2)

            liste_blocs_triee = sorted(liste_blocs, key=priorite_bloc)

            # Optimisation selon phase de vie
            phase = contexte.get("phase_source", "ENFANCE")
            if phase == "ENFANCE":
                liste_blocs_triee = liste_blocs_triee[
                    :200
                ]  # Limiter pour apprentissage

            return liste_blocs_triee

        except Exception as e:
            logger.error(f"Erreur optimisation contextuelle: {e}")
            return liste_blocs

    def generer_construction_fallback(self, plan_abstrait: Dict) -> List[Dict]:
        """Génère une construction basique en cas d'erreur."""
        try:
            dimensions = plan_abstrait.get("dimensions", [5, 3, 5])
            largeur, hauteur, profondeur = dimensions

            blocs_fallback = []

            # Construction rectangulaire simple
            for y in range(hauteur):
                for x in range(largeur):
                    for z in range(profondeur):
                        # Murs et fondations seulement
                        if (
                            y == 0
                            or x == 0
                            or x == largeur - 1
                            or z == 0
                            or z == profondeur - 1
                        ):
                            materiau = "stone" if y == 0 else "wood"
                            blocs_fallback.append(
                                {
                                    "position": [x, y, z],
                                    "materiau": materiau,
                                    "type": "construction_fallback",
                                    "importance": "structurelle",
                                }
                            )

            logger.warning(
                f"Construction fallback générée: {len(blocs_fallback)} blocs"
            )
            return blocs_fallback

        except Exception as e:
            logger.error(f"Erreur construction fallback: {e}")
            return []

    def plan_construction_fallback(self, objectif: str, phase_de_vie: str) -> Dict:
        """Plan de construction fallback en cas d'erreur."""
        return {
            "type": "construction_fallback",
            "objectif": objectif,
            "dimensions": [5, 3, 5],
            "materiaux_autorises": ["wood", "stone"],
            "blocs_generes": self.generer_construction_fallback(
                {"dimensions": [5, 3, 5]}
            ),
            "score_nouveaute": 0.1,
            "timestamp_creation": time.time(),
            "phase_source": phase_de_vie,
        }

    def finaliser_plan_construction(self, plan: Dict) -> Dict:
        """Finalise un plan avec validations et optimisations."""
        try:
            # Validation dimensions réalistes
            if "dimensions" in plan:
                plan["dimensions"] = [max(3, min(50, d)) for d in plan["dimensions"]]

            # Calcul coût estimé
            plan["cout_estime"] = self._calculer_cout_construction(plan)

            # Calcul temps construction
            plan["temps_construction_estime"] = self._calculer_temps_construction(plan)

            # Ajout métadonnées finales
            plan["version_creativite"] = "2.0"
            plan["signature_ia"] = f"eve_creative_{int(time.time())}"

            return plan

        except Exception as e:
            logger.error(f"Erreur finalisation plan: {e}")
            return plan

    def _calculer_cout_construction(self, plan: Dict) -> int:
        """Calcule le coût estimé en ressources."""
        try:
            dimensions = plan.get("dimensions", [5, 3, 5])
            volume = dimensions[0] * dimensions[1] * dimensions[2]
            cout_base = int(volume * 0.7)
            complexite = plan.get("complexite_max", 3)
            multiplicateur_complexite = 1 + (complexite / 10)
            cout_total = int(cout_base * multiplicateur_complexite)
            return max(10, cout_total)
        except Exception as e:
            logger.error(f"Erreur calcul coût: {e}")
            return 50

    def _calculer_temps_construction(self, plan: Dict) -> str:
        """Calcule le temps estimé de construction."""
        try:
            cout = plan.get("cout_estime", 50)
            complexite = plan.get("complexite_max", 3)
            temps_total = (cout / 10) + (complexite * 5)

            if temps_total < 15:
                return "court (< 15 min)"
            elif temps_total < 60:
                return f"moyen ({int(temps_total)} min)"
            else:
                heures = int(temps_total // 60)
                minutes = int(temps_total % 60)
                return f"long ({heures}h{minutes:02d})"
        except Exception as e:
            logger.error(f"Erreur calcul temps: {e}")
            return "moyen (30 min)"

    def mettre_a_jour_metriques(self, metriques: Dict, plan: Dict) -> Dict:
        """Met à jour les métriques de créativité."""
        try:
            metriques["plans_generes"] += 1
            score_actuel = plan.get("score_nouveaute", 0)
            nb_plans = metriques["plans_generes"]
            score_moyen_precedent = metriques["score_moyen_nouveaute"]

            nouveau_score_moyen = (
                (score_moyen_precedent * (nb_plans - 1)) + score_actuel
            ) / nb_plans
            metriques["score_moyen_nouveaute"] = nouveau_score_moyen

            if plan.get("innovations_architecturales") or plan.get(
                "elements_monumentaux"
            ):
                metriques["innovations_introduites"] += 1

            return metriques
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques: {e}")
            return metriques

    def analyser_evolution_stylistique(
        self, portfolio: List[Dict], metriques: Dict, tendances: Dict
    ) -> Dict:
        """Analyse l'évolution créative avec métriques avancées."""
        try:
            # Analyse progression créative
            scores_nouveaute = [p.get("score_nouveaute", 0) for p in portfolio]
            progression_nouveaute = (
                "croissante"
                if scores_nouveaute[-3:] > scores_nouveaute[:3]
                else "stable"
            )

            # Analyse diversité matériaux
            tous_materiaux = set()
            for plan in portfolio:
                tous_materiaux.update(plan.get("materiaux_autorises", []))

            return {
                **tendances,
                "metriques_globales": metriques.copy(),
                "progression_nouveaute": progression_nouveaute,
                "diversite_materiaux": len(tous_materiaux),
                "niveau_artistique": self._evaluer_niveau_artistique(
                    metriques, portfolio
                ),
                "recommandations": self._generer_recommandations_artistiques(
                    metriques, portfolio
                ),
            }
        except Exception as e:
            logger.error(f"Erreur analyse évolution: {e}")
            return {"erreur": str(e)}

    def _evaluer_niveau_artistique(self, metriques: Dict, portfolio: List[Dict]) -> str:
        """Évalue le niveau de maturité artistique actuel."""
        nb_creations = len(portfolio)
        score_moyen = metriques.get("score_moyen_nouveaute", 0)
        diversite = metriques.get("diversite_stylistique", 0)
        innovations = metriques.get("innovations_introduites", 0)

        score_global = (
            min(20, nb_creations)
            + (score_moyen * 30)
            + (diversite * 5)
            + (innovations * 10)
        )

        if score_global >= 80:
            return "Maître Artiste"
        elif score_global >= 60:
            return "Artiste Confirmé"
        elif score_global >= 40:
            return "Créateur Prometteur"
        else:
            return "Apprenti Créatif"

    def _generer_recommandations_artistiques(
        self, metriques: Dict, portfolio: List[Dict]
    ) -> List[str]:
        """Génère des recommandations pour progresser artistiquement."""
        recommandations = []

        if metriques.get("score_moyen_nouveaute", 0) < 0.6:
            recommandations.append("Expérimenter avec de nouveaux matériaux et formes")

        if len(portfolio) < 10:
            recommandations.append("Créer plus d'œuvres pour développer l'expérience")

        if metriques.get("innovations_introduites", 0) == 0:
            recommandations.append(
                "Introduire des éléments innovants dans les créations"
            )

        return recommandations[:3]

    def recommander_prochain_projet(self, analyse: Dict, phase_de_vie: str) -> Dict:
        """Recommande le prochain projet créatif avec analyse contextuelle."""
        niveau = analyse.get("niveau_artistique", "Débutant Créatif")

        projets_recommandes = {
            "Apprenti Créatif": {
                "type": "fondamentaux",
                "projet": "Maîtriser les formes géométriques de base",
                "phase_recommandee": "ENFANCE",
            },
            "Créateur Prometteur": {
                "type": "expérimentation",
                "projet": "Explorer styles architecturaux variés",
                "phase_recommandee": "ADOLESCENCE",
            },
            "Artiste Confirmé": {
                "type": "intégration_environnementale",
                "projet": "Créer architecture harmonieuse avec l'environnement",
                "phase_recommandee": "ADULTE",
            },
            "Maître Artiste": {
                "type": "chef_oeuvre_signature",
                "projet": "Concevoir une œuvre monumentale unique",
                "phase_recommandee": "MAITRISE",
            },
        }

        return projets_recommandes.get(
            niveau,
            {
                "type": "exploration_generale",
                "projet": "Continuer l'exploration créative",
                "phase_recommandee": phase_de_vie,
            },
        )