import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class AnalyseurStrategies:
    """Analyse les stratégies et meilleures pratiques découvertes."""

    @staticmethod
    def extraire_strategies_reussies(
        historique_raisonnements: List[Dict],
    ) -> List[Dict]:
        """Extrait les stratégies qui ont donné de bons résultats."""
        strategies_reussies = []

        for raisonnement in historique_raisonnements:
            if raisonnement.get("succes", False):
                strategie = {
                    "contexte": raisonnement.get("mode", "INCONNU"),
                    "approche": raisonnement.get("plan", ""),
                    "phase_vie": raisonnement.get("phase_vie", ""),
                    "efficacite": raisonnement.get("score_efficacite", 0.5),
                    "timestamp": raisonnement.get("timestamp", 0),
                }
                strategies_reussies.append(strategie)

        return sorted(strategies_reussies, key=lambda x: x["efficacite"], reverse=True)

    @staticmethod
    def identifier_patterns_comportementaux(graphe_connaissances: Dict) -> Dict:
        """Identifie les patterns comportementaux dans les connaissances."""
        noeuds = graphe_connaissances.get("noeuds", {})
        patterns = {
            "preferences_materiaux": {},
            "strategies_construction": [],
            "techniques_survie": [],
            "optimisations_decouvertes": [],
        }

        for noeud_id, noeud_data in noeuds.items():
            tags = noeud_data.get("tags", [])

            if "construction" in tags:
                patterns["strategies_construction"].append(
                    {
                        "technique": noeud_id,
                        "fiabilite": noeud_data.get("niveau_confiance", 3),
                        "contexte": noeud_data.get("contexte", "general"),
                    }
                )

            elif "survie" in tags:
                patterns["techniques_survie"].append(
                    {
                        "technique": noeud_id,
                        "urgence": noeud_data.get("urgence", "normale"),
                        "efficacite": noeud_data.get("efficacite", 0.5),
                    }
                )

            elif "optimisation" in tags:
                patterns["optimisations_decouvertes"].append(
                    {
                        "optimisation": noeud_id,
                        "gain_efficacite": noeud_data.get("gain", 0),
                        "domaine": noeud_data.get("domaine", "general"),
                    }
                )

        return patterns


class GenerateurRecommandations:
    """Génère des recommandations basées sur l'expérience acquise."""

    @staticmethod
    def generer_meilleures_pratiques(patterns: Dict) -> List[Dict]:
        """Génère une liste de meilleures pratiques."""
        pratiques = []

        # Pratiques de construction
        for strategie in patterns.get("strategies_construction", []):
            if strategie["fiabilite"] <= 2:  # Haute confiance
                pratiques.append(
                    {
                        "domaine": "construction",
                        "pratique": strategie["technique"],
                        "niveau_confiance": "haute",
                        "contexte_application": strategie["contexte"],
                        "type": "technique_validee",
                    }
                )

        # Pratiques de survie
        for technique in patterns.get("techniques_survie", []):
            if technique["efficacite"] > 0.7:
                pratiques.append(
                    {
                        "domaine": "survie",
                        "pratique": technique["technique"],
                        "niveau_confiance": "moyenne",
                        "urgence": technique["urgence"],
                        "type": "technique_survie",
                    }
                )

        # Optimisations découvertes
        for optim in patterns.get("optimisations_decouvertes", []):
            if optim["gain_efficacite"] > 0.2:
                pratiques.append(
                    {
                        "domaine": optim["domaine"],
                        "pratique": optim["optimisation"],
                        "niveau_confiance": "experimentale",
                        "gain_estime": optim["gain_efficacite"],
                        "type": "optimisation",
                    }
                )

        return pratiques

    @staticmethod
    def generer_recommandations_futures(cerveau_data: Dict) -> List[str]:
        """Génère des recommandations pour futures IA."""
        recommandations = []

        stats = cerveau_data.get("statistiques", {})
        efficacite = stats.get("efficacite_decision", {}).get("score", 0)

        if efficacite < 50:
            recommandations.append("Prioriser l'exploration de nouvelles stratégies")
            recommandations.append(
                "Augmenter la durée d'analyse avant prise de décision"
            )

        if stats.get("concepts_totaux", 0) < 100:
            recommandations.append("Encourager l'expérimentation active")
            recommandations.append("Diversifier les sources d'apprentissage")

        evolution = stats.get("evolution_emotionnelle", {})
        if evolution.get("stabilite_emotionnelle", 1.0) < 0.6:
            recommandations.append("Implémenter des mécanismes de gestion du stress")
            recommandations.append(
                "Renforcer les stratégies de récupération émotionnelle"
            )

        return recommandations


class ExporteurGuide:
    """
    Génère un guide JSONL avec les connaissances et stratégies.
    Implémente la Directive 77.
    """

    def __init__(self):
        """TODO: Add docstring."""
        self.analyseur = AnalyseurStrategies()
        self.generateur = GenerateurRecommandations()

    def generer_guide_complet(self, cerveau, chemin_export: str = None) -> str:
        """Génère le guide complet au format JSONL."""
        timestamp = datetime.now()

        if chemin_export is None:
            chemin_export = (
                f"guide_strategies_{timestamp.strftime('%Y%m%d_%H%M%S')}.jsonl"
            )

        # Extraction des données du cerveau
        strategies_reussies = self.analyseur.extraire_strategies_reussies(
            getattr(cerveau, "historique_raisonnements", [])
        )

        patterns = self.analyseur.identifier_patterns_comportementaux(
            cerveau.modele_monde.graphe_connaissances
        )

        meilleures_pratiques = self.generateur.generer_meilleures_pratiques(patterns)

        # Préparation du chemin d'export
        chemin_complet = Path("exports") / chemin_export
        chemin_complet.parent.mkdir(exist_ok=True)

        # Génération du fichier JSONL
        with open(chemin_complet, "w", encoding="utf-8") as f:
            # En-tête du guide
            entete = {
                "type": "guide_header",
                "version": "1.0",
                "timestamp": timestamp.isoformat(),
                "source_ia": "Enfant_EVE",
                "phase_finale": getattr(
                    cerveau.comportement, "phase_de_vie", "INCONNU"
                ),
                "total_strategies": len(strategies_reussies),
                "total_pratiques": len(meilleures_pratiques),
            }
            f.write(json.dumps(entete, ensure_ascii=False) + "\n")

            # Stratégies réussies
            for strategie in strategies_reussies:
                entry = {"type": "strategie_reussie", "data": strategie}
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # Meilleures pratiques
            for pratique in meilleures_pratiques:
                entry = {"type": "meilleure_pratique", "data": pratique}
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # Patterns comportementaux
            entry_patterns = {"type": "patterns_comportementaux", "data": patterns}
            f.write(json.dumps(entry_patterns, ensure_ascii=False) + "\n")

            # Recommandations futures
            cerveau_export_data = {
                "statistiques": {
                    "concepts_totaux": len(
                        cerveau.modele_monde.graphe_connaissances.get("noeuds", {})
                    ),
                    "efficacite_decision": {"score": 75},  # Placeholder
                    "evolution_emotionnelle": {
                        "stabilite_emotionnelle": 0.8
                    },  # Placeholder
                }
            }

            recommandations = self.generateur.generer_recommandations_futures(
                cerveau_export_data
            )
            entry_recommandations = {
                "type": "recommandations_futures",
                "data": recommandations,
            }
            f.write(json.dumps(entry_recommandations, ensure_ascii=False) + "\n")

            # Résumé exécutif
            resume = self._generer_resume_guide(
                strategies_reussies, meilleures_pratiques, patterns
            )
            entry_resume = {"type": "resume_executif", "data": resume}
            f.write(json.dumps(entry_resume, ensure_ascii=False) + "\n")

        print(f"✓ Guide des stratégies généré: {chemin_complet}")
        return str(chemin_complet)

    def _generer_resume_guide(
        self, strategies: List, pratiques: List, patterns: Dict
    ) -> Dict:
        """Génère un résumé exécutif du guide."""
        return {
            "strategies_principales": len(strategies),
            "pratiques_validees": len(
                [p for p in pratiques if p.get("niveau_confiance") == "haute"]
            ),
            "domaines_expertise": list(
                set(p.get("domaine", "general") for p in pratiques)
            ),
            "techniques_construction": len(patterns.get("strategies_construction", [])),
            "techniques_survie": len(patterns.get("techniques_survie", [])),
            "optimisations": len(patterns.get("optimisations_decouvertes", [])),
            "maturite_globale": self._evaluer_maturite_globale(strategies, pratiques),
        }

    def _evaluer_maturite_globale(self, strategies: List, pratiques: List) -> str:
        """Évalue le niveau de maturité global des connaissances."""
        if len(strategies) > 100 and len(pratiques) > 50:
            return "Expert"
        elif len(strategies) > 50 and len(pratiques) > 25:
            return "Avancé"
        elif len(strategies) > 20 and len(pratiques) > 10:
            return "Intermédiaire"
        else:
            return "Débutant"

    def valider_guide_qualite(self, chemin_guide: str) -> Dict:
        """Valide la qualité du guide généré."""
        try:
            with open(chemin_guide, "r", encoding="utf-8") as f:
                lignes = f.readlines()

            types_entries = {}
            erreurs = []

            for i, ligne in enumerate(lignes):
                try:
                    entry = json.loads(ligne.strip())
                    type_entry = entry.get("type", "inconnu")
                    types_entries[type_entry] = types_entries.get(type_entry, 0) + 1
                except json.JSONDecodeError as e:
                    erreurs.append(f"Ligne {i+1}: {e}")

            validation = {
                "valide": len(erreurs) == 0,
                "total_entries": len(lignes),
                "types_entries": types_entries,
                "erreurs": erreurs,
                "completude": "guide_header" in types_entries
                and "resume_executif" in types_entries,
            }

            return validation

        except Exception as e:
            return {"valide": False, "erreur": str(e)}


# Interface d'utilisation
def generer_guide(cerveau, chemin_export=None):
    """Interface simplifiée pour générer un guide."""
    exporteur = ExporteurGuide()
    return exporteur.generer_guide_complet(cerveau, chemin_export)


def valider_guide(chemin_guide):
    """Interface simplifiée pour valider un guide."""
    exporteur = ExporteurGuide()
    return exporteur.valider_guide_qualite(chemin_guide)