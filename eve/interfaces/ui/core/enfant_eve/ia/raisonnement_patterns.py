import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AnalyseurPatterns:
    """
    Analyse les patterns dans les données pour la déduction.
    Respecte Directive 61 avec focus sur l'analyse uniquement.
    """

    @staticmethod
    def identifier_correlations(historique: List[Dict]) -> Dict[str, float]:
        """Identifie des corrélations simples dans l'historique."""
        correlations = {}

        if len(historique) < 5:
            return correlations

        try:
            # Corrélation heure/sécurité
            dangers_nuit = sum(
                1
                for h in historique
                if h.get("heure", 0.5) > 0.8 and h.get("menace", False)
            )
            total_nuit = sum(1 for h in historique if h.get("heure", 0.5) > 0.8)

            if total_nuit > 0:
                correlations["danger_nocturne"] = dangers_nuit / total_nuit

            # Corrélation biome/ressources
            foret_bois = sum(
                1
                for h in historique
                if "foret" in str(h.get("biome", "")) and h.get("bois_trouve", 0) > 0
            )
            total_foret = sum(
                1 for h in historique if "foret" in str(h.get("biome", ""))
            )

            if total_foret > 0:
                correlations["foret_bois"] = foret_bois / total_foret

            # Corrélation altitude/minerais
            minerai_profond = sum(
                1
                for h in historique
                if h.get("altitude", 70) < 30 and h.get("minerai_trouve", False)
            )
            total_profond = sum(1 for h in historique if h.get("altitude", 70) < 30)

            if total_profond > 0:
                correlations["profondeur_minerais"] = minerai_profond / total_profond

            # Corrélation outils/efficacité
            outils_avances = sum(
                1
                for h in historique
                if h.get("outil_utilise", "") in ["diamond_pickaxe", "iron_pickaxe"]
                and h.get("efficacite", 0) > 0.7
            )
            total_outils_avances = sum(
                1
                for h in historique
                if h.get("outil_utilise", "") in ["diamond_pickaxe", "iron_pickaxe"]
            )

            if total_outils_avances > 0:
                correlations["outils_efficacite"] = (
                    outils_avances / total_outils_avances
                )

        except Exception as e:
            logger.error(f"Erreur identification corrélations: {e}")

        return correlations

    @staticmethod
    def detecter_sequences_causales(evenements: List[Dict]) -> List[Dict]:
        """Détecte des séquences de cause à effet."""
        sequences = []

        try:
            for i in range(len(evenements) - 1):
                evt_actuel = evenements[i]
                evt_suivant = evenements[i + 1]

                # Règle : Action de minage -> Acquisition de ressource
                if (
                    evt_actuel.get("action") == "miner"
                    and evt_suivant.get("type") == "acquisition_ressource"
                ):
                    sequences.append(
                        {
                            "cause": evt_actuel["action"],
                            "effet": evt_suivant["type"],
                            "fiabilite": 0.8,
                            "contexte": evt_actuel.get("lieu", "inconnu"),
                            "delai": evt_suivant.get("timestamp", 0)
                            - evt_actuel.get("timestamp", 0),
                        }
                    )

                # Règle : Construction abri -> Sécurité accrue
                if evt_actuel.get("action") == "construire_abri" and evt_suivant.get(
                    "securite", 0
                ) > evt_actuel.get("securite", 0):
                    sequences.append(
                        {
                            "cause": "construction_abri",
                            "effet": "amelioration_securite",
                            "fiabilite": 0.9,
                            "contexte": evt_actuel.get("lieu", "inconnu"),
                            "delai": evt_suivant.get("timestamp", 0)
                            - evt_actuel.get("timestamp", 0),
                        }
                    )

                # Règle : Exploration -> Découverte ressources
                if (
                    evt_actuel.get("action") == "explorer"
                    and evt_suivant.get("nouvelles_ressources", 0) > 0
                ):
                    sequences.append(
                        {
                            "cause": "exploration",
                            "effet": "decouverte_ressources",
                            "fiabilite": 0.6,
                            "contexte": evt_actuel.get("direction", "inconnue"),
                            "delai": evt_suivant.get("timestamp", 0)
                            - evt_actuel.get("timestamp", 0),
                        }
                    )

        except Exception as e:
            logger.error(f"Erreur détection séquences causales: {e}")

        return sequences

    @staticmethod
    def analyser_patterns_construction(carte_monde: Dict) -> Dict:
        """Analyse les patterns dans la construction pour optimiser."""
        try:
            patterns = {
                "zones_denses": [],
                "zones_vides": [],
                "structures_detectees": [],
                "efficacite_spatiale": 0.0,
            }

            if not carte_monde:
                return patterns

            # Analyser la densité de construction
            zones_construites = {}
            for pos_str, bloc_type in carte_monde.items():
                if bloc_type not in ["air", "water", "lava"]:
                    try:
                        pos = tuple(map(float, pos_str.split(",")))
                        zone_key = (
                            int(pos[0] // 10),
                            int(pos[2] // 10),
                        )  # Grouper par zones 10x10
                        zones_construites[zone_key] = (
                            zones_construites.get(zone_key, 0) + 1
                        )
                    except:
                        continue

            # Identifier zones denses et vides
            if zones_construites:
                seuil_dense = max(zones_construites.values()) * 0.7
                patterns["zones_denses"] = [
                    k for k, v in zones_construites.items() if v >= seuil_dense
                ]
                patterns["zones_vides"] = [
                    k for k, v in zones_construites.items() if v < seuil_dense * 0.3
                ]
                patterns["efficacite_spatiale"] = len(patterns["zones_denses"]) / max(
                    1, len(zones_construites)
                )

            # Détecter des structures connues
            structures_potentielles = []
            for pos_str, bloc_type in carte_monde.items():
                if any(
                    struct in str(bloc_type)
                    for struct in ["house", "tower", "farm", "wall", "bridge"]
                ):
                    structures_potentielles.append(bloc_type)

            patterns["structures_detectees"] = list(set(structures_potentielles))

            return patterns

        except Exception as e:
            logger.error(f"Erreur analyse patterns construction: {e}")
            return {
                "zones_denses": [],
                "zones_vides": [],
                "structures_detectees": [],
                "efficacite_spatiale": 0.0,
            }

    @staticmethod
    def analyser_patterns_deplacement(historique_deplacement: List[Dict]) -> Dict:
        """Analyse les patterns de déplacement pour optimiser les routes."""
        try:
            patterns = {
                "trajets_frequents": [],
                "goulots_etranglement": [],
                "zones_evitees": [],
                "efficacite_moyenne": 0.0,
            }

            if len(historique_deplacement) < 5:
                return patterns

            # Analyser fréquence des trajets
            trajets = {}
            for deplacement in historique_deplacement:
                origine = deplacement.get("origine", "inconnue")
                destination = deplacement.get("destination", "inconnue")
                trajet = f"{origine}->{destination}"

                trajets[trajet] = trajets.get(trajet, 0) + 1

            # Identifier trajets fréquents
            if trajets:
                seuil_frequent = max(trajets.values()) * 0.3
                patterns["trajets_frequents"] = [
                    trajet for trajet, freq in trajets.items() if freq >= seuil_frequent
                ]

            # Analyser efficacité
            efficacites = [d.get("efficacite", 0.5) for d in historique_deplacement]
            if efficacites:
                patterns["efficacite_moyenne"] = sum(efficacites) / len(efficacites)

            # Identifier zones évitées (faible fréquentation)
            zones_visitees = {}
            for deplacement in historique_deplacement:
                zone = deplacement.get("zone", "inconnue")
                zones_visitees[zone] = zones_visitees.get(zone, 0) + 1

            if zones_visitees:
                seuil_evitement = max(zones_visitees.values()) * 0.1
                patterns["zones_evitees"] = [
                    zone
                    for zone, freq in zones_visitees.items()
                    if freq <= seuil_evitement
                ]

            return patterns

        except Exception as e:
            logger.error(f"Erreur analyse patterns déplacement: {e}")
            return {
                "trajets_frequents": [],
                "goulots_etranglement": [],
                "zones_evitees": [],
                "efficacite_moyenne": 0.0,
            }

    @staticmethod
    def analyser_patterns_ressources(historique_collecte: List[Dict]) -> Dict:
        """Analyse les patterns de collecte de ressources."""
        try:
            patterns = {
                "ressources_abondantes": [],
                "ressources_rares": [],
                "zones_productives": [],
                "heures_optimales": {},
            }

            if not historique_collecte:
                return patterns

            # Analyser abondance des ressources
            ressources_collectees = {}
            for collecte in historique_collecte:
                ressource = collecte.get("ressource", "inconnue")
                quantite = collecte.get("quantite", 0)
                ressources_collectees[ressource] = (
                    ressources_collectees.get(ressource, 0) + quantite
                )

            if ressources_collectees:
                quantite_moyenne = sum(ressources_collectees.values()) / len(
                    ressources_collectees
                )
                patterns["ressources_abondantes"] = [
                    res
                    for res, qte in ressources_collectees.items()
                    if qte > quantite_moyenne * 1.5
                ]
                patterns["ressources_rares"] = [
                    res
                    for res, qte in ressources_collectees.items()
                    if qte < quantite_moyenne * 0.3
                ]

            # Analyser zones productives
            zones_productivite = {}
            for collecte in historique_collecte:
                zone = collecte.get("zone", "inconnue")
                efficacite = collecte.get("efficacite", 0.5)
                if zone not in zones_productivite:
                    zones_productivite[zone] = []
                zones_productivite[zone].append(efficacite)

            for zone, efficacites in zones_productivite.items():
                efficacite_moyenne = sum(efficacites) / len(efficacites)
                if efficacite_moyenne > 0.7:
                    patterns["zones_productives"].append(zone)

            # Analyser heures optimales
            heures_efficacite = {}
            for collecte in historique_collecte:
                heure = collecte.get("heure", 0.5)
                efficacite = collecte.get("efficacite", 0.5)
                plage_horaire = int(heure * 4)  # 4 plages de 6h

                if plage_horaire not in heures_efficacite:
                    heures_efficacite[plage_horaire] = []
                heures_efficacite[plage_horaire].append(efficacite)

            for plage, efficacites in heures_efficacite.items():
                efficacite_moyenne = sum(efficacites) / len(efficacites)
                if efficacite_moyenne > 0.6:
                    noms_plages = ["Nuit", "Matin", "Jour", "Soir"]
                    patterns["heures_optimales"][
                        noms_plages[plage]
                    ] = efficacite_moyenne

            return patterns

        except Exception as e:
            logger.error(f"Erreur analyse patterns ressources: {e}")
            return {
                "ressources_abondantes": [],
                "ressources_rares": [],
                "zones_productives": [],
                "heures_optimales": {},
            }
