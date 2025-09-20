import json
import time
from datetime import datetime
from pathlib import Path


class FormatteurGrapheConnaissances:
    """Formate le graphe de connaissances pour l'export."""

    @staticmethod
    def nettoyer_noeud(noeud_data: Dict) -> Dict:
        """Nettoie et formate les données d'un nœud."""
        noeud_propre = {}

        # Données essentielles
        if "valeur" in noeud_data:
            noeud_propre["valeur"] = noeud_data["valeur"]
        if "niveau_confiance" in noeud_data:
            noeud_propre["niveau_confiance"] = noeud_data["niveau_confiance"]
        if "tags" in noeud_data:
            noeud_propre["tags"] = noeud_data["tags"]
        if "timestamp_creation" in noeud_data:
            noeud_propre["timestamp_creation"] = noeud_data["timestamp_creation"]

        # Source de l'information
        noeud_propre["source"] = noeud_data.get("source", "inconnue")

        return noeud_propre

    @staticmethod
    def calculer_statistiques_graphe(graphe: Dict) -> Dict:
        """Calcule des statistiques sur le graphe de connaissances."""
        noeuds = graphe.get("noeuds", {})
        liens = graphe.get("liens", [])

        # Répartition par niveau de confiance
        repartition_confiance = {
            "EXPERIENCE_DIRECTE": 0,
            "DEDUCTION_LOGIQUE": 0,
            "LECON_MENTOR": 0,
        }
        for noeud_data in noeuds.values():
            niveau = noeud_data.get("niveau_confiance", 99)
            if niveau == 1:
                repartition_confiance["EXPERIENCE_DIRECTE"] += 1
            elif niveau == 2:
                repartition_confiance["DEDUCTION_LOGIQUE"] += 1
            elif niveau == 3:
                repartition_confiance["LECON_MENTOR"] += 1

        # Répartition par tags
        compteur_tags = {}
        for noeud_data in noeuds.values():
            for tag in noeud_data.get("tags", []):
                compteur_tags[tag] = compteur_tags.get(tag, 0) + 1

        return {
            "total_noeuds": len(noeuds),
            "total_liens": len(liens),
            "repartition_confiance": repartition_confiance,
            "tags_populaires": dict(
                sorted(compteur_tags.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
        }


class FormatteurEmotions:
    """Formate les données émotionnelles pour l'export."""

    @staticmethod
    def exporter_etat_emotionnel(comportement) -> Dict:
        """Exporte l'état émotionnel complet."""
        return {
            "emotions_actuelles": {
                "confiance": getattr(comportement, "confiance", 0.5),
                "peur": getattr(comportement, "peur", 0.0),
                "frustration": getattr(comportement, "frustration", 0.0),
                "fierte": getattr(comportement, "fierte", 0.0),
            },
            "phase_de_vie": getattr(comportement, "phase_de_vie", "ENFANCE"),
            "jours_survecus": getattr(comportement, "jours_survecus", 0),
            "config_emotions": getattr(comportement, "config", {}),
        }

    @staticmethod
    def analyser_evolution_emotionnelle(comportement) -> Dict:
        """Analyse l'évolution émotionnelle de l'IA."""
        emotions_actuelles = FormatteurEmotions.exporter_etat_emotionnel(comportement)

        # Évaluation de la stabilité émotionnelle
        emotions = emotions_actuelles["emotions_actuelles"]
        stabilite = 1.0 - (emotions["peur"] + emotions["frustration"]) / 2

        # Évaluation du bien-être général
        bien_etre = (emotions["confiance"] + emotions["fierte"] + stabilite) / 3

        return {
            "stabilite_emotionnelle": stabilite,
            "bien_etre_general": bien_etre,
            "emotions_dominantes": sorted(
                emotions.items(), key=lambda x: x[1], reverse=True
            ),
            "phase_maturite": emotions_actuelles["phase_de_vie"],
        }


class ExporteurCerveau:
    """
    Exporte l'état complet du cerveau au format JSON.
    Implémente les Directives 22 et 76.
    """

    def __init__(self):
        """TODO: Add docstring."""
        self.formatteur_graphe = FormatteurGrapheConnaissances()
        self.formatteur_emotions = FormatteurEmotions()

    def exporter_cerveau_complet(self, cerveau, chemin_export: str = None) -> Dict:
        """Exporte l'état complet du cerveau."""
        timestamp = datetime.now()

        if chemin_export is None:
            chemin_export = f"cerveau_export_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        # Construction de la structure d'export
        export_data = {
            "metadata": {
                "version_export": "1.0",
                "timestamp_export": timestamp.isoformat(),
                "mode_actuel": getattr(cerveau, "mode_actuel", "INCONNU"),
                "temps_execution": time.time()
                - getattr(cerveau, "progres_recent", time.time()),
            },
            "graphe_connaissances": self._exporter_graphe_connaissances(
                cerveau.modele_monde
            ),
            "etat_emotionnel": self.formatteur_emotions.exporter_etat_emotionnel(
                cerveau.comportement
            ),
            "historique_raisonnements": getattr(
                cerveau, "historique_raisonnements", []
            ),
            "configuration": getattr(cerveau, "config", {}),
            "statistiques": self._calculer_statistiques_globales(cerveau),
        }

        # Sauvegarde du fichier
        chemin_complet = Path("exports") / chemin_export
        chemin_complet.parent.mkdir(exist_ok=True)

        with open(chemin_complet, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"✓ Cerveau exporté: {chemin_complet}")
        return export_data

    def _exporter_graphe_connaissances(self, modele_monde) -> Dict:
        """Exporte le graphe de connaissances."""
        graphe_brut = modele_monde.graphe_connaissances

        # Nettoyage et formatage des nœuds
        noeuds_propres = {}
        for noeud_id, noeud_data in graphe_brut.get("noeuds", {}).items():
            noeuds_propres[noeud_id] = self.formatteur_graphe.nettoyer_noeud(noeud_data)

        graphe_exporte = {
            "noeuds": noeuds_propres,
            "liens": graphe_brut.get("liens", []),
            "statistiques": self.formatteur_graphe.calculer_statistiques_graphe(
                graphe_brut
            ),
        }

        return graphe_exporte

    def _calculer_statistiques_globales(self, cerveau) -> Dict:
        """Calcule des statistiques globales sur l'état du cerveau."""
        return {
            "concepts_totaux": len(
                cerveau.modele_monde.graphe_connaissances.get("noeuds", {})
            ),
            "plans_generes": len(getattr(cerveau, "historique_raisonnements", [])),
            "evolution_emotionnelle": self.formatteur_emotions.analyser_evolution_emotionnelle(
                cerveau.comportement
            ),
            "efficacite_decision": self._evaluer_efficacite_decisions(cerveau),
        }

    def _evaluer_efficacite_decisions(self, cerveau) -> Dict:
        """Évalue l'efficacité des décisions prises."""
        historique = getattr(cerveau, "historique_raisonnements", [])

        if not historique:
            return {"score": 0, "analyse": "Aucune donnée disponible"}

        # Analyse des modes utilisés
        modes_utilises = {}
        for raisonnement in historique:
            mode = raisonnement.get("mode", "INCONNU")
            modes_utilises[mode] = modes_utilises.get(mode, 0) + 1

        # Score basé sur la diversité des approches
        diversite_score = len(modes_utilises) * 10

        return {
            "score": min(100, diversite_score),
            "modes_utilises": modes_utilises,
            "total_decisions": len(historique),
            "analyse": "Évaluation basée sur la diversité des approches stratégiques",
        }

    def generer_resume_executif(self, cerveau) -> str:
        """Génère un résumé exécutif de l'état du cerveau."""
        stats = self._calculer_statistiques_globales(cerveau)
        emotions = self.formatteur_emotions.exporter_etat_emotionnel(
            cerveau.comportement
        )

        resume = f"""
RÉSUMÉ EXÉCUTIF - ÉTAT DU CERVEAU IA

Phase de développement: {emotions['phase_de_vie']}
Concepts appris: {stats['concepts_totaux']}
Décisions prises: {stats['plans_generes']}

ÉTAT ÉMOTIONNEL:
- Confiance: {emotions['emotions_actuelles']['confiance']:.2f}
- Stabilité: {stats['evolution_emotionnelle']['stabilite_emotionnelle']:.2f}
- Bien-être: {stats['evolution_emotionnelle']['bien_etre_general']:.2f}

PERFORMANCE:
- Efficacité décisions: {stats['efficacite_decision']['score']}/100
- Diversité approches: {len(stats['efficacite_decision']['modes_utilises'])} modes utilisés

STATUS: {"OPÉRATIONNEL" if stats['concepts_totaux'] > 10 else "EN DÉVELOPPEMENT"}
        """

        return resume.strip()


# Interface d'utilisation
def exporter_cerveau(cerveau, chemin_export=None):
    """Interface simplifiée pour exporter un cerveau."""
    exporteur = ExporteurCerveau()
    return exporteur.exporter_cerveau_complet(cerveau, chemin_export)


def generer_resume(cerveau):
    """Interface simplifiée pour générer un résumé."""
    exporteur = ExporteurCerveau()
    return exporteur.generer_resume_executif(cerveau)