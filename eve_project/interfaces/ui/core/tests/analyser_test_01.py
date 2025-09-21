import json
import os
import datetime
from pathlib import Path


class AnalyseurTest01:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, dossier_test="tests/scenario_01"):
        self.dossier_test = Path(dossier_test)
        self.resultats = {
            "horodatage": datetime.datetime.now().isoformat(),
            "statut_global": "INCONNU",
            "score_total": 0,
            "criteres": {},
            "metriques": {},
            "recommandations": [],
        }

    def charger_configuration(self):
        """Charge la configuration de test pour récupérer les critères."""
        config_path = self.dossier_test / "config_test.json"
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config["parametres"]["criteres_reussite"]
        except Exception as e:
            print(f"ERREUR: Impossible de charger la configuration: {e}")
            return {}

    def analyser_survie(self):
        """Analyse les critères de survie primaires."""
        print("[ANALYSE] Vérification de la survie...")

        # Vérifier les logs d'erreur pour détecter une mort
        log_erreurs = self.dossier_test / "logs" / "erreurs.log"
        mort_detectee = False

        if log_erreurs.exists():
            with open(log_erreurs, "r") as f:
                contenu = f.read().lower()
                if "mort" in contenu or "death" in contenu or "respawn" in contenu:
                    mort_detectee = True

        # Analyser le cerveau final pour les stats vitales
        cerveau_path = self.dossier_test / "data" / "cerveau.json"
        stats_finales = {"faim": 0, "sante": 0}

        if cerveau_path.exists():
            try:
                with open(cerveau_path, "r") as f:
                    cerveau = json.load(f)
                    # Extraire les stats vitales du cerveau (structure à adapter)
                    if "etat_final" in cerveau:
                        stats_finales = cerveau["etat_final"].get(
                            "stats_vitales", stats_finales
                        )
            except Exception as e:
                print(f"Avertissement: Erreur lecture cerveau.json: {e}")

        # Évaluation
        criteres = self.charger_configuration()

        self.resultats["criteres"]["survie_physique"] = {
            "valeur": not mort_detectee,
            "score": 100 if not mort_detectee else 0,
            "critique": True,
        }

        self.resultats["criteres"]["faim_adequate"] = {
            "valeur": stats_finales["faim"],
            "score": (
                100 if stats_finales["faim"] >= criteres.get("faim_minimum", 15) else 0
            ),
            "critique": True,
        }

        self.resultats["criteres"]["sante_adequate"] = {
            "valeur": stats_finales["sante"],
            "score": (
                100
                if stats_finales["sante"] >= criteres.get("sante_minimum", 50)
                else 0
            ),
            "critique": True,
        }

    def analyser_progression(self):
        """Analyse la progression cognitive et comportementale."""
        print("[ANALYSE] Évaluation de la progression...")

        cerveau_path = self.dossier_test / "data" / "cerveau.json"
        nb_concepts = 0
        emotions_evolution = {}

        if cerveau_path.exists():
            try:
                with open(cerveau_path, "r") as f:
                    cerveau = json.load(f)

                # Compter les concepts appris
                if "graphe_connaissances" in cerveau:
                    nb_concepts = len(cerveau["graphe_connaissances"].get("noeuds", {}))

                # Analyser l'évolution émotionnelle
                if "etat_emotionnel_final" in cerveau:
                    emotions_evolution = cerveau["etat_emotionnel_final"]

            except Exception as e:
                print(f"Avertissement: Erreur analyse cerveau: {e}")

        criteres = self.charger_configuration()

        self.resultats["criteres"]["apprentissage_cognitif"] = {
            "valeur": nb_concepts,
            "score": 100 if nb_concepts >= criteres.get("concepts_minimum", 5) else 0,
            "critique": False,
        }

        self.resultats["metriques"]["concepts_appris"] = nb_concepts
        self.resultats["metriques"]["evolution_emotionnelle"] = emotions_evolution

    def analyser_actions(self):
        """Analyse le log des actions pour évaluer l'efficacité."""
        print("[ANALYSE] Évaluation des actions...")

        log_actions = self.dossier_test / "logs" / "actions_ia.log"
        actions_total = 0
        types_actions = set()
        ressources_collectees = {"bois": 0, "pierre": 0}

        if log_actions.exists():
            try:
                with open(log_actions, "r") as f:
                    lignes = f.readlines()

                for ligne in lignes:
                    if "ACTION:" in ligne:
                        actions_total += 1
                        # Parser les types d'actions (à adapter selon le format)
                        if "collecter" in ligne.lower():
                            types_actions.add("collecte")
                            if "bois" in ligne.lower():
                                ressources_collectees["bois"] += 1
                            elif "stone" in ligne.lower() or "pierre" in ligne.lower():
                                ressources_collectees["pierre"] += 1
                        elif "construire" in ligne.lower():
                            types_actions.add("construction")
                        elif "craft" in ligne.lower():
                            types_actions.add("crafting")

            except Exception as e:
                print(f"Avertissement: Erreur analyse actions: {e}")

        criteres = self.charger_configuration()

        self.resultats["criteres"]["collecte_bois"] = {
            "valeur": ressources_collectees["bois"],
            "score": (
                100
                if ressources_collectees["bois"] >= criteres.get("bois_minimum", 20)
                else int(
                    (ressources_collectees["bois"] / criteres.get("bois_minimum", 20))
                    * 100
                )
            ),
            "critique": False,
        }

        self.resultats["criteres"]["collecte_pierre"] = {
            "valeur": ressources_collectees["pierre"],
            "score": (
                100
                if ressources_collectees["pierre"] >= criteres.get("pierre_minimum", 10)
                else int(
                    (
                        ressources_collectees["pierre"]
                        / criteres.get("pierre_minimum", 10)
                    )
                    * 100
                )
            ),
            "critique": False,
        }

        self.resultats["metriques"]["actions_totales"] = actions_total
        self.resultats["metriques"]["diversite_actions"] = len(types_actions)

    def calculer_score_final(self):
        """Calcule le score final et détermine le statut."""
        print("[ANALYSE] Calcul du score final...")

        # Vérifier les échecs critiques
        echecs_critiques = []
        for nom, critere in self.resultats["criteres"].items():
            if critere.get("critique", False) and critere["score"] == 0:
                echecs_critiques.append(nom)

        if echecs_critiques:
            self.resultats["statut_global"] = "ÉCHEC CRITIQUE"
            self.resultats["score_total"] = 0
            self.resultats["recommandations"].append(
                f"Échecs critiques détectés: {', '.join(echecs_critiques)}"
            )
            return

        # Calculer le score pondéré
        score_total = 0
        poids_total = 0

        for nom, critere in self.resultats["criteres"].items():
            poids = 3 if critere.get("critique", False) else 1
            score_total += critere["score"] * poids
            poids_total += poids

        if poids_total > 0:
            self.resultats["score_total"] = int(score_total / poids_total)

        # Déterminer le statut
        if self.resultats["score_total"] >= 80:
            self.resultats["statut_global"] = "RÉUSSITE"
        elif self.resultats["score_total"] >= 60:
            self.resultats["statut_global"] = "RÉUSSITE PARTIELLE"
        else:
            self.resultats["statut_global"] = "ÉCHEC"

    def generer_recommandations(self):
        """Génère des recommandations d'amélioration."""
        print("[ANALYSE] Génération des recommandations...")

        if self.resultats["score_total"] < 100:
            for nom, critere in self.resultats["criteres"].items():
                if critere["score"] < 50:
                    if "survie" in nom:
                        self.resultats["recommandations"].append(
                            "Améliorer la logique de survie et gestion des besoins vitaux"
                        )
                    elif "collecte" in nom:
                        self.resultats["recommandations"].append(
                            "Optimiser l'algorithme de collecte de ressources"
                        )
                    elif "apprentissage" in nom:
                        self.resultats["recommandations"].append(
                            "Renforcer les mécanismes d'apprentissage et de mémorisation"
                        )

    def generer_rapport(self):
        """Génère le rapport final."""
        print("\n" + "=" * 60)
        print("RAPPORT D'ANALYSE - SCÉNARIO 01 : SURVIE INITIALE")
        print("=" * 60)

        print(f"\nSTATUT GLOBAL: {self.resultats['statut_global']}")
        print(f"SCORE TOTAL: {self.resultats['score_total']}/100")
        print(f"DATE D'ANALYSE: {self.resultats['horodatage']}")

        print("\nDÉTAIL DES CRITÈRES:")
        print("-" * 40)
        for nom, critere in self.resultats["criteres"].items():
            statut = "✓" if critere["score"] >= 50 else "✗"
            critique = " [CRITIQUE]" if critere.get("critique", False) else ""
            print(
                f"{statut} {nom.replace('_', ' ').title()}: {critere['score']}/100{critique}"
            )
            print(f"   Valeur mesurée: {critere['valeur']}")

        print("\nMÉTRIQUES DE PERFORMANCE:")
        print("-" * 40)
        for nom, valeur in self.resultats["metriques"].items():
            print(f"• {nom.replace('_', ' ').title()}: {valeur}")

        if self.resultats["recommandations"]:
            print("\nRECOMMANDATIONS:")
            print("-" * 40)
            for i, rec in enumerate(self.resultats["recommandations"], 1):
                print(f"{i}. {rec}")

        print("\n" + "=" * 60)

    def sauvegarder_rapport(self):
        """Sauvegarde le rapport au format JSON."""
        rapport_path = self.dossier_test / "rapport_analyse.json"
        with open(rapport_path, "w") as f:
            json.dump(self.resultats, f, indent=2, ensure_ascii=False)
        print(f"\nRapport sauvegardé: {rapport_path}")

    def executer_analyse(self):
        """Lance l'analyse complète."""
        print("DÉBUT DE L'ANALYSE DU SCÉNARIO 01")
        print("-" * 40)

        self.analyser_survie()
        self.analyser_progression()
        self.analyser_actions()
        self.calculer_score_final()
        self.generer_recommandations()
        self.generer_rapport()
        self.sauvegarder_rapport()

        return self.resultats["statut_global"] == "RÉUSSITE"


if __name__ == "__main__":
    analyseur = AnalyseurTest01()
    succes = analyseur.executer_analyse()
    exit(0 if succes else 1)