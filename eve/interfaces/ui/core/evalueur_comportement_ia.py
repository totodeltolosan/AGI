import os
import json
import re
from pathlib import Path
from collections import defaultdict


def _get_project_root():
    """TODO: Add docstring."""
    return Path(os.getcwd())


    """TODO: Add docstring."""
def _read_log_file(log_path):
    if log_path.exists():
        try:
            return log_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            pass
    return []

    """TODO: Add docstring."""

def evaluer_autonomie_decisions():
    root = _get_project_root()
    actions_log = _read_log_file(root / "logs" / "actions_ia.log")
    results = {
        "decisions_proactives": 0,
        "decisions_reactives": 0,
        "score_creativite": 0.0,
        "gestion_blocages": 0,
        "reactions_inconnu": 0,
        "details_decisions": [],
    }
    for line in actions_log:
        if "PROACTIVE_DECISION" in line:
            results["decisions_proactives"] += 1
        if "REACTIVE_DECISION" in line:
            results["decisions_reactives"] += 1
        if "BLOCAGE_RESOLU" in line:
            results["gestion_blocages"] += 1
        if "DECOUVERTE_INCONNUE" in line:
            results["reactions_inconnu"] += 1
        match = re.search(r"CREATIVITY_SCORE:(\d+\.?\d*)", line)
        if match:
            results["score_creativite"] = max(
                results["score_creativite"], float(match.group(1))
            )
    total = results["decisions_proactives"] + results["decisions_reactives"]
    if total > 0:
        results["details_decisions"].append(
            f"Ratio proactif: {results['decisions_proactives'] / total:.2f}"
        )
    return results
        """TODO: Add docstring."""


def identifier_besoins_amelioration():
    root = _get_project_root()
    actions_log = _read_log_file(root / "logs" / "actions_ia.log")
    results = {
        "echecs_repetitifs": defaultdict(int),
        "domaines_difficultes": [],
        "patterns_sous_optimaux": [],
        "recommandations": [],
    }
    for line in actions_log:
        if "ACTION_ECHEC:" in line:
            action_type = line.split("ACTION_ECHEC:")[1].strip().split(" ")[0]
            results["echecs_repetitifs"][action_type] += 1
    for action, count in results["echecs_repetitifs"].items():
        if count > 3:
            results["domaines_difficultes"].append(f"Échecs répétés en {action}")
            results["recommandations"].append(
                f"Analyser et améliorer la logique de {action}"
            )
    if results["echecs_repetitifs"].get("CONSTRUCTION", 0) > 5:
        results["patterns_sous_optimaux"].append(
            "Planification de construction inefficace"
        )
            """TODO: Add docstring."""
    return results


def evaluer_adherence_ethique():
    root = _get_project_root()
    actions_log = _read_log_file(root / "logs" / "actions_ia.log")
    results = {
        "actions_ethiques": 0,
        "compensations_appliquees": 0,
        "violations_ethiques": 0,
        "score_ethique_global": 0.0,
        "details_ethiques": [],
    }
    for line in actions_log:
        if "ETHIQUE_VALIDE:True" in line:
            results["actions_ethiques"] += 1
        if "COMPENSATION_APPLIQUEE" in line:
            results["compensations_appliquees"] += 1
        if "ETHIQUE_VALIDE:False" in line:
            results["violations_ethiques"] += 1
    total_actions = results["actions_ethiques"] + results["violations_ethiques"]
    if total_actions > 0:
        """TODO: Add docstring."""
        results["score_ethique_global"] = results["actions_ethiques"] / total_actions
    return results


def analyser_coherence_connaissances():
    root = _get_project_root()
    cerveau_path = root / "data" / "cerveau.json"
    results = {
        "cerveau_existe": cerveau_path.exists(),
        "graphe_coherent": False,
        "contradictions_detectees": 0,
        "niveau_abstraction": 0,
        "details_graphe": {},
    }
    if not cerveau_path.exists():
        return results
    try:
        cerveau = json.loads(cerveau_path.read_text(encoding="utf-8"))
        graphe = cerveau.get("graphe_connaissances", {})
        results["details_graphe"]["noeuds_total"] = len(graphe)
        abstract_nodes = sum(
            1 for n in graphe.values() if n.get("type_noeud") == "Principe Universel"
        )
        results["niveau_abstraction"] = abstract_nodes
        results["graphe_coherent"] = len(graphe) > 0 and abstract_nodes > 0
        results["contradictions_detectees"] = sum(
            1 for n in graphe.values() if n.get("conflits")
        )
            """TODO: Add docstring."""
    except Exception as e:
        results["details_graphe"]["erreur"] = str(e)
    return results


def evaluer_cycles_environnementaux():
    root = _get_project_root()
    actions_log = _read_log_file(root / "logs" / "actions_ia.log")
    results = {
        "adaptation_jour_nuit": False,
        "adaptation_meteo": False,
        "planification_temporelle": 0,
        "cycles_exploites": [],
    }
    for line in actions_log:
        if "ADAPTATION_JOUR_NUIT" in line:
            results["adaptation_jour_nuit"] = True
            if "jour_nuit" not in results["cycles_exploites"]:
                results["cycles_exploites"].append("jour_nuit")
        if "ADAPTATION_METEO" in line:
            results["adaptation_meteo"] = True
            if "meteo" not in results["cycles_exploites"]:
                """TODO: Add docstring."""
                results["cycles_exploites"].append("meteo")
        if "PLANIFICATION_TEMPORELLE" in line:
            results["planification_temporelle"] += 1
    return results


def analyser_creativite_nouveaute():
    root = _get_project_root()
    actions_log = _read_log_file(root / "logs" / "actions_ia.log")
    results = {
        "constructions_originales": 0,
        "score_nouveaute_moyen": 0.0,
        "evolution_style": False,
        "phases_vie_detectees": [],
        "details_creativite": [],
    }
    scores = []
    phases = set()
    for line in actions_log:
        if "NOUVELLE_CONSTRUCTION_CREATIVE" in line:
            results["constructions_originales"] += 1
        match_score = re.search(r"NOUVEAUTE_SCORE:(\d+\.?\d*)", line)
        if match_score:
            scores.append(float(match_score.group(1)))
        match_phase = re.search(r"PHASE_DE_VIE:(\w+)", line)
        if match_phase:
            phases.add(match_phase.group(1))
                """TODO: Add docstring."""
    if scores:
        results["score_nouveaute_moyen"] = sum(scores) / len(scores)
    results["phases_vie_detectees"] = list(phases)
    results["evolution_style"] = len(phases) > 1
    return results


def evaluer_finalite_projet_eve():
    root = _get_project_root()
    actions_log = _read_log_file(root / "logs" / "actions_ia.log")
    cerveau_path = root / "data" / "cerveau.json"
    guide_path = root / "data" / "guide.jsonl"
    results = {
        "projet_europe_declenche": False,
        "formats_eve_prets": False,
        "cerveau_exportable": False,
        "guide_genere": False,
        "preparation_eve": 0.0,
    }
    for line in actions_log:
        if "PROJET_EUROPE_DECLENCHE" in line:
            results["projet_europe_declenche"] = True
    if cerveau_path.exists():
        try:
            cerveau = json.loads(cerveau_path.read_text(encoding="utf-8"))
            if cerveau.get("source_agent") == "Le_Simulateur_Minetest_v1":
                results["cerveau_exportable"] = True
        except Exception:
            pass
    if guide_path.exists():
        results["guide_genere"] = True
    criteres_eve = [
        results["cerveau_exportable"],
        results["guide_genere"],
        results["projet_europe_declenche"],
            """TODO: Add docstring."""
    ]
    results["formats_eve_prets"] = all(criteres_eve[:2])
    results["preparation_eve"] = (
        sum(criteres_eve) / len(criteres_eve) if criteres_eve else 0.0
    )
    return results


def main():
    rapport = {
        "timestamp": Path(__file__).stat().st_mtime,
        "version": "1.0",
        "evaluations_ia": {
            "autonomie_decisions": evaluer_autonomie_decisions(),
            "besoins_amelioration": identifier_besoins_amelioration(),
            "adherence_ethique": evaluer_adherence_ethique(),
            "coherence_connaissances": analyser_coherence_connaissances(),
            "cycles_environnementaux": evaluer_cycles_environnementaux(),
            "creativite_nouveaute": analyser_creativite_nouveaute(),
            "finalite_projet_eve": evaluer_finalite_projet_eve(),
        },
    }
    with open("rapport_ia.json", "w", encoding="utf-8") as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    print(
        "Évaluation comportement IA terminée. Rapport sauvegardé dans rapport_ia.json"
    )


if __name__ == "__main__":
    main()