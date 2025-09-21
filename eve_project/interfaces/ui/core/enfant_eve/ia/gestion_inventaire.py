from typing import Dict, List, Any, Tuple


class OptimisateurInventaire:
    """Optimise l'organisation de l'inventaire selon les besoins."""

    @staticmethod
    def analyser_frequence_utilisation(
        historique_actions: List[Dict],
    ) -> Dict[str, int]:
        """Analyse la fréquence d'utilisation des objets."""
        compteur_usage = {}
        for action in historique_actions[-100:]:  # 100 dernières actions
            if action.get("type") in ["CRAFT", "PLACER", "UTILISER"]:
                item = action.get("item", "")
                compteur_usage[item] = compteur_usage.get(item, 0) + 1
        return compteur_usage

    @staticmethod
    def calculer_priorite_acces(item: str, contexte: str) -> int:
        """Calcule la priorité d'accès rapide (1-9, 9 = plus prioritaire)."""
        priorites_construction = {
            "wood": 9,
            "stone": 8,
            "dirt": 7,
            "torch": 9,
            "pickaxe": 8,
            "axe": 7,
            "shovel": 6,
            "sword": 5,
        }
        priorites_exploration = {
            "torch": 9,
            "food": 8,
            "sword": 7,
            "bow": 6,
            "pickaxe": 8,
            "rope": 5,
            "compass": 4,
        }
        priorites_survie = {
            "food": 9,
            "torch": 8,
            "sword": 7,
            "armor": 6,
            "healing_potion": 9,
            "bed": 5,
        }

        tables_priorite = {
            "construction": priorites_construction,
            "exploration": priorites_exploration,
            "survie": priorites_survie,
        }

        return tables_priorite.get(contexte, {}).get(item, 1)


class StrategieRangement:
    """Stratégies de rangement intelligent."""

    @staticmethod
    def grouper_par_type(inventaire: Dict[str, int]) -> Dict[str, List[str]]:
        """Groupe les objets par type logique."""
        groupes = {
            "outils": [],
            "materiaux": [],
            "nourriture": [],
            "armes": [],
            "utilitaires": [],
            "decoratif": [],
        }

        classifications = {
            "pickaxe": "outils",
            "axe": "outils",
            "shovel": "outils",
            "wood": "materiaux",
            "stone": "materiaux",
            "iron": "materiaux",
            "bread": "nourriture",
            "meat": "nourriture",
            "apple": "nourriture",
            "sword": "armes",
            "bow": "armes",
            "arrow": "armes",
            "torch": "utilitaires",
            "rope": "utilitaires",
            "bucket": "utilitaires",
            "flower": "decoratif",
            "painting": "decoratif",
        }

        for item in inventaire:
            type_item = classifications.get(item, "utilitaires")
            groupes[type_item].append(item)

        return groupes

    @staticmethod
    def optimiser_emplacement_coffres(
        items: List[str], capacite_coffre: int = 27
    ) -> List[List[str]]:
        """Optimise la répartition des objets dans les coffres."""
        coffres = []
        coffre_actuel = []

        # Tri par priorité d'accès (items fréquents ensemble)
        items_tries = sorted(items, key=lambda x: x, reverse=True)

        for item in items_tries:
            if len(coffre_actuel) < capacite_coffre:
                coffre_actuel.append(item)
            else:
                coffres.append(coffre_actuel)
                coffre_actuel = [item]

        if coffre_actuel:
            coffres.append(coffre_actuel)

        return coffres


class ModuleGestionInventaire:
    """
    Gère l'inventaire comme une extension de la mémoire de travail.
    Implémente la Directive 37.
    """

    def __init__(self, modele_monde):
        """TODO: Add docstring."""
        self.modele_monde = modele_monde
        self.optimisateur = OptimisateurInventaire()
        self.strategie = StrategieRangement()
        self.historique_organisations = []

    def creer_plan_organisation_pour_construction(
        self, plan_construction: Dict
    ) -> List[Dict]:
        """Génère un plan d'organisation optimale pour un projet de construction."""
        materiaux_requis = plan_construction.get("materiaux", [])
        outils_necessaires = self._identifier_outils_necessaires(plan_construction)

        plan_organisation = []

        # Phase 1: Préparation de la barre d'accès rapide
        barre_rapide = self._optimiser_barre_acces_rapide(
            materiaux_requis + outils_necessaires
        )
        for slot, item in enumerate(barre_rapide[:9]):
            plan_organisation.append(
                {"type": "PLACER_BARRE_RAPIDE", "slot": slot, "item": item}
            )

        # Phase 2: Organisation des matériaux par proximité
        plan_organisation.extend(self._organiser_materiaux_proximite(materiaux_requis))

        # Phase 3: Préparation des outils de secours
        plan_organisation.extend(self._preparer_outils_secours())

        return plan_organisation

    def _identifier_outils_necessaires(self, plan_construction: Dict) -> List[str]:
        """Identifie les outils nécessaires pour un plan de construction."""
        complexite = plan_construction.get("complexite", "basique")
        materiaux = plan_construction.get("materiaux", [])

        outils_base = ["pickaxe", "axe", "shovel"]

        if "stone" in materiaux or "cobble" in materiaux:
            outils_base.append("pickaxe")
        if "wood" in materiaux:
            outils_base.append("axe")
        if complexite in ["intermediaire", "avancee"]:
            outils_base.extend(["bucket", "compass", "torch"])

        return list(set(outils_base))

    def _optimiser_barre_acces_rapide(self, items_prioritaires: List[str]) -> List[str]:
        """Optimise l'organisation de la barre d'accès rapide."""
        # Récupération de l'historique depuis le modèle du monde
        historique = self.modele_monde.graphe_connaissances.get(
            "historique_actions", []
        )
        frequences = self.optimisateur.analyser_frequence_utilisation(historique)

        # Combinaison priorité + fréquence d'usage
        items_scores = []
        for item in items_prioritaires:
            priorite = self.optimisateur.calculer_priorite_acces(item, "construction")
            frequence = frequences.get(item, 0)
            score_total = priorite * 2 + frequence  # Priorité x2 + fréquence
            items_scores.append((item, score_total))

        # Tri par score décroissant et sélection des 9 premiers
        items_scores.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in items_scores[:9]]

    def _organiser_materiaux_proximite(self, materiaux: List[str]) -> List[Dict]:
        """Organise les matériaux par proximité logique."""
        groupes = self.strategie.grouper_par_type({mat: 1 for mat in materiaux})
        actions_organisation = []

        for type_groupe, items_groupe in groupes.items():
            if items_groupe:
                actions_organisation.append(
                    {
                        "type": "REGROUPER_MATERIAUX",
                        "groupe": type_groupe,
                        "items": items_groupe,
                        "conteneur": f"coffre_{type_groupe}",
                    }
                )

        return actions_organisation

    def _preparer_outils_secours(self) -> List[Dict]:
        """Prépare des outils de secours pour les imprévus."""
        return [
            {
                "type": "VERIFIER_DURABILITE",
                "outils": ["pickaxe", "axe", "shovel"],
                "seuil_remplacement": 10,
            },
            {
                "type": "PREPARER_SECOURS",
                "items": ["torch", "food", "wood"],
                "quantites": [10, 5, 20],
            },
        ]

    def analyser_efficacite_organisation(self, resultats_construction: Dict) -> Dict:
        """Analyse l'efficacité de la dernière organisation."""
        temps_construction = resultats_construction.get("duree_totale", 0)
        interruptions = resultats_construction.get("nb_interruptions", 0)

        score_efficacite = max(
            0, 100 - interruptions * 5 - max(0, temps_construction - 300) // 60
        )

        analyse = {
            "score_efficacite": score_efficacite,
            "temps_total": temps_construction,
            "interruptions": interruptions,
            "recommandations": [],
        }

        if interruptions > 3:
            analyse["recommandations"].append("Améliorer la préparation des outils")
        if temps_construction > 600:
            analyse["recommandations"].append(
                "Optimiser l'ordre des matériaux dans la barre rapide"
            )

        self.historique_organisations.append(analyse)
        return analyse

    def generer_rapport_inventaire(self) -> Dict:
        """Génère un rapport sur l'état et l'efficacité de l'inventaire."""
        if not self.historique_organisations:
            return {"message": "Aucune organisation analysée"}

        scores = [org["score_efficacite"] for org in self.historique_organisations]
        moyenne_efficacite = sum(scores) / len(scores)

        return {
            "efficacite_moyenne": moyenne_efficacite,
            "nb_organisations": len(self.historique_organisations),
            "derniere_analyse": self.historique_organisations[-1],
            "tendance": (
                "amelioration"
                if len(scores) > 1 and scores[-1] > scores[-2]
                else "stable"
            ),
        }