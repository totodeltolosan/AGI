import json
from pathlib import Path
from datetime import datetime


def _get_project_root():
    """TODO: Add docstring."""
    return Path(__file__).parent


    """TODO: Add docstring."""
def _load_report_data():
    root = _get_project_root()
    data = {}
    reports = {
        "statique": root / "rapport_statique.json",
        "architecture": root / "rapport_architecture.json",
        "tests": root / "rapport_tests.json",
        "ia": root / "rapport_ia.json",
    }
    for key, path in reports.items():
        if path.exists():
            try:
                data[key] = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                data[key] = {"erreur": str(e)}
        else:
            data[key] = {"erreur": f"Fichier {path.name} manquant"}
    return data

    """TODO: Add docstring."""

def _calculate_static_scores(statique_data):
    score = 0
    max_score = 6
    if "taches" not in statique_data:
        return 0, 0
    taches = statique_data["taches"]
    if taches.get("arborescence", {}).get("conformite_arborescence", False):
        score += 1
    if not taches.get("dependances", {}).get("dependances_manquantes"):
        score += 1
    if not taches.get("syntaxe_style", {}).get("erreurs_black") and not taches.get(
        "syntaxe_style", {}
    ).get("erreurs_flake8"):
        score += 1
    if not taches.get("fichiers_inutiles", {}).get("fichiers_suspects"):
        score += 1
    if not taches.get("refactorisation", {}).get(
        "fichiers_trop_longs"
    ) and not taches.get("refactorisation", {}).get("fonctions_complexes"):
        score += 1
    if not taches.get("documentation", {}).get(
        "variables_non_explicites"
    ) and not taches.get("documentation", {}).get("fonctions_non_explicites"):
        score += 1
    return score, max_score
        """TODO: Add docstring."""


def _calculate_archi_scores(archi_data):
    score = 0
    max_score = 6
    if "validations" not in archi_data:
        return 0, 0
    validations = archi_data["validations"]
    if all(
        validations.get("architecture_globale", {})
        .get("processus_presents", {})
        .values()
    ):
        score += 1
    if validations.get("coherence_config", {}).get(
        "config_valide", False
    ) and not validations.get("coherence_config", {}).get("erreurs_validation"):
        score += 1
    if validations.get("schemas_exportation", {}).get(
        "cerveau_json_valide", False
    ) and validations.get("schemas_exportation", {}).get("guide_jsonl_valide", False):
        score += 1
    if validations.get("securite_erreurs", {}).get(
        "try_except_present", False
    ) and validations.get("securite_erreurs", {}).get("logging_present", False):
        score += 1
    if validations.get("integration_qualite", {}).get("precommit_valide", False):
        score += 1
    if all(validations.get("gestion_memoire_disque", {}).values()):
        score += 1
            """TODO: Add docstring."""
    return score, max_score


def _calculate_test_scores(tests_data):
    score = 0
    max_score = 3
    if "tests_dynamiques" not in tests_data:
        return 0, 0
    dyn_tests = tests_data["tests_dynamiques"]
    unit_tests = dyn_tests.get("tests_unitaires", {})
    if unit_tests.get("tests_executes", 0) > 0 and unit_tests.get(
        "tests_reussis", 0
    ) == unit_tests.get("tests_executes", 0):
        score += 1
    integ_tests = dyn_tests.get("tests_integration", {})
    if integ_tests.get("communication_processus", False) and integ_tests.get(
        "queues_fonctionnelles", False
    ):
        score += 1
    scenario_tests = dyn_tests.get("scenario_minetest", {})
    if scenario_tests.get("etat_final_valide", False):
        """TODO: Add docstring."""
        score += 1
    return score, max_score


def _calculate_ia_scores(ia_data):
    score = 0
    max_score = 7
    if "evaluations_ia" not in ia_data:
        return 0, 0
    eval_ia = ia_data["evaluations_ia"]
    if eval_ia.get("autonomie_decisions", {}).get("decisions_proactives", 0) > 0:
        score += 1
    if not eval_ia.get("besoins_amelioration", {}).get("domaines_difficultes"):
        score += 1
    if eval_ia.get("adherence_ethique", {}).get("score_ethique_global", 0.0) > 0.7:
        score += 1
    if eval_ia.get("coherence_connaissances", {}).get("graphe_coherent", False):
        score += 1
    if eval_ia.get("cycles_environnementaux", {}).get("adaptation_jour_nuit", False):
        score += 1
    if eval_ia.get("creativite_nouveaute", {}).get("constructions_originales", 0) > 0:
        score += 1
            """TODO: Add docstring."""
    if eval_ia.get("finalite_projet_eve", {}).get("preparation_eve", 0.0) > 0.7:
        score += 1
    return score, max_score


def calculer_statistiques_avancement(data):
    total_score = 0
    total_max_score = 0
    s_score, s_max = _calculate_static_scores(data.get("statique", {}))
    a_score, a_max = _calculate_archi_scores(data.get("architecture", {}))
    t_score, t_max = _calculate_test_scores(data.get("tests", {}))
    i_score, i_max = _calculate_ia_scores(data.get("ia", {}))
    total_score = s_score + a_score + t_score + i_score
    total_max_score = s_max + a_max + t_max + i_max
    global_score = (total_score / total_max_score) if total_max_score > 0 else 0.0
    return {
        "score_global": global_score,
        "conformite_directives": (s_score / s_max) if s_max > 0 else 0.0,
        "couverture_tests": (t_score / t_max) if t_max > 0 else 0.0,
        "qualite_code": (s_score / s_max) if s_max > 0 else 0.0,
        "maturite_ia": (i_score / i_max) if i_max > 0 else 0.0,
        "preparation_eve": data.get("ia", {})
            """TODO: Add docstring."""
        .get("evaluations_ia", {})
        .get("finalite_projet_eve", {})
        .get("preparation_eve", 0.0),
    }


def _gen_css():
    return """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%); color: #e0e0e0; line-height: 1.6; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; padding: 30px; background: rgba(0, 255, 255, 0.1); border: 2px solid #00ffff; border-radius: 15px; box-shadow: 0 0 30px rgba(0, 255, 255, 0.3); }
        .header h1 { font-size: 2.5em; color: #00ffff; text-shadow: 0 0 20px #00ffff; margin-bottom: 10px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .stat-card { background: rgba(22, 33, 62, 0.8); border: 1px solid #00ffff; border-radius: 10px; padding: 20px; text-align: center; transition: all 0.3s ease; }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 255, 255, 0.2); }
        .stat-value { font-size: 2.5em; font-weight: bold; color: #00ff88; text-shadow: 0 0 10px #00ff88; }
        .stat-label { color: #a0a0a0; margin-top: 5px; }
        .section { background: rgba(26, 26, 46, 0.9); border: 1px solid #444; border-radius: 10px; margin-bottom: 30px; overflow: hidden; }
        .section-header { background: linear-gradient(90deg, #1a1a2e, #16213e); padding: 15px 25px; border-bottom: 2px solid #00ffff; }
        .section-header h2 { color: #00ffff; font-size: 1.5em; }
        .section-content { padding: 25px; }
        .task-item { background: rgba(16, 16, 32, 0.8); border-left: 4px solid #00ff88; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
        .task-item.warning { border-left-color: #ffaa00; }
        .task-item.error { border-left-color: #ff4444; }
        .task-title { color: #00ffff; font-weight: bold; margin-bottom: 8px; }
        .task-description { color: #c0c0c0; margin-bottom: 10px; }
        .task-status { display: inline-block; padding: 4px 12px; border-radius: 15px; font-size: 0.8em; font-weight: bold; }
        .status-success { background: #00ff88; color: #000; }
        .status-warning { background: #ffaa00; color: #000; }
        .status-error { background: #ff4444; color: #fff; }
        .code-block { background: #0a0a0a; border: 1px solid #333; border-radius: 5px; padding: 15px; margin: 10px 0; overflow-x: auto; font-family: 'Courier New', monospace; color: #00ff88; }
        .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .table th, .table td { border: 1px solid #444; padding: 10px; text-align: left; }
            """TODO: Add docstring."""
        .table th { background: rgba(0, 255, 255, 0.2); color: #00ffff; }
        .progress-bar { background: #333; border-radius: 10px; overflow: hidden; height: 20px; margin: 10px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #00ff88, #00ffff); transition: width 0.5s ease; }
    </style>
    """


def _gen_status_tag(is_ok, warning_count=0, error_count=0):
    if error_count > 0:
        return f"<span class='task-status status-error'>{error_count} ERREUR(S)</span>"
    if warning_count > 0:
        return (
            f"<span class='task-status status-warning'>{warning_count} ALERTE(S)</span>"
                """TODO: Add docstring."""
        )
    return (
        "<span class='task-status status-success'>OK</span>"
            """TODO: Add docstring."""
        if is_ok
        else "<span class='task-status status-error'>ÉCHEC</span>"
    )


def _gen_code_block(content):
    return f"<div class='code-block'><pre><code>{content}</code></pre></div>"


def _gen_section_statique(data):
    html = ""
    statique = data.get("statique", {})
    if "erreur" in statique:
        return f"<div class='task-item error'>Rapport statique non disponible: {statique['erreur']}</div>"
    taches = statique.get("taches", {})
    html += f"<div class='task-item'> <div class='task-title'>1.1. Vérification Arborescence</div> {_gen_status_tag(taches.get('arborescence', {}).get('conformite_arborescence', False))} </div>"
    if taches.get("arborescence", {}).get("dossiers_manquants"):
        html += f"<p>Dossiers manquants: {', '.join(taches['arborescence']['dossiers_manquants'])}</p>"
    html += f"<div class='task-item'> <div class='task-title'>1.2. Analyse Dépendances et Imports</div> {_gen_status_tag(not taches.get('dependances', {}).get('dependances_manquantes'))} </div>"
    if taches.get("dependances", {}).get("dependances_manquantes"):
        html += f"<p>Dépendances manquantes: {', '.join(taches['dependances']['dependances_manquantes'])}</p>"
    black_err = len(taches.get("syntaxe_style", {}).get("erreurs_black", []))
    flake8_err = len(taches.get("syntaxe_style", {}).get("erreurs_flake8", []))
    comments_found = len(
        taches.get("syntaxe_style", {}).get("fichiers_avec_comments", [])
    )
    html += f"<div class='task-item'> <div class='task-title'>1.3. Audit Syntaxe et Style</div> {_gen_status_tag(black_err == 0 and flake8_err == 0 and comments_found == 0, black_err + flake8_err + comments_found)} </div>"
    if black_err > 0:
        html += f"<p>Erreurs Black: {_gen_code_block('<br>'.join(taches['syntaxe_style']['erreurs_black']))}</p>"
    if flake8_err > 0:
        html += f"<p>Erreurs Flake8: {_gen_code_block('<br>'.join(taches['syntaxe_style']['erreurs_flake8']))}</p>"
    if comments_found > 0:
        html += f"<p>Fichiers avec commentaires: {', '.join(taches['syntaxe_style']['fichiers_avec_comments'])}</p>"
    html += f"<div class='task-item'> <div class='task-title'>1.4. Détection Fichiers Inutiles</div> {_gen_status_tag(not taches.get('fichiers_inutiles', {}).get('fichiers_suspects'))} </div>"
    if taches.get("fichiers_inutiles", {}).get("fichiers_suspects"):
        html += f"<p>Fichiers suspects: {', '.join(taches['fichiers_inutiles']['fichiers_suspects'])}</p>"
    long_files = len(taches.get("refactorisation", {}).get("fichiers_trop_longs", []))
    complex_funcs = len(
        taches.get("refactorisation", {}).get("fonctions_complexes", [])
    )
    html += f"<div class='task-item'> <div class='task-title'>1.5. Recommandation Refactorisation</div> {_gen_status_tag(long_files == 0 and complex_funcs == 0, long_files + complex_funcs)} </div>"
    if long_files > 0:
        html += f"<p>Fichiers trop longs: {_gen_code_block(json.dumps(taches['refactorisation']['fichiers_trop_longs'], indent=2))}</p>"
    if complex_funcs > 0:
        html += f"<p>Fonctions complexes: {_gen_code_block(json.dumps(taches['refactorisation']['fonctions_complexes'], indent=2))}</p>"
            """TODO: Add docstring."""
    non_explicit_vars = len(
        taches.get("documentation", {}).get("variables_non_explicites", [])
    )
    non_explicit_funcs = len(
        taches.get("documentation", {}).get("fonctions_non_explicites", [])
    )
    html += f"<div class='task-item'> <div class='task-title'>1.6. Analyse Documentation Interne</div> {_gen_status_tag(non_explicit_vars == 0 and non_explicit_funcs == 0, non_explicit_vars + non_explicit_funcs)} </div>"
    return html


def _gen_section_architecture(data):
    html = ""
    archi = data.get("architecture", {})
    if "erreur" in archi:
        return f"<div class='task-item error'>Rapport architecture non disponible: {archi['erreur']}</div>"
    validations = archi.get("validations", {})
    proc_pres = validations.get("architecture_globale", {}).get(
        "processus_presents", {}
    )
    proc_ok = sum(proc_pres.values())
    total_proc = len(proc_pres)
    html += f"<div class='task-item'> <div class='task-title'>2.1. Processus Principaux</div> {_gen_status_tag(proc_ok == total_proc, total_proc - proc_ok)} </div>"
    if proc_ok < total_proc:
        html += f"<p>Processus manquants: {', '.join([p for p, exists in proc_pres.items() if not exists])}</p>"
    config_valide = validations.get("coherence_config", {}).get("config_valide", False)
    config_err = len(
        validations.get("coherence_config", {}).get("erreurs_validation", [])
    )
    html += f"<div class='task-item'> <div class='task-title'>2.2. Cohérence Configuration JSON</div> {_gen_status_tag(config_valide and config_err == 0, config_err)} </div>"
    if config_err > 0:
        html += f"<p>Erreurs config: {_gen_code_block('<br>'.join(validations['coherence_config']['erreurs_validation']))}</p>"
    cerveau_valide = validations.get("schemas_exportation", {}).get(
        "cerveau_json_valide", False
    )
    guide_valide = validations.get("schemas_exportation", {}).get(
        "guide_jsonl_valide", False
    )
    export_err = len(
        validations.get("schemas_exportation", {}).get("erreurs_schemas", [])
    )
    html += f"<div class='task-item'> <div class='task-title'>2.3. Validation Schémas Exportation</div> {_gen_status_tag(cerveau_valide and guide_valide, export_err)} </div>"
    if export_err > 0:
        html += f"<p>Erreurs schémas: {_gen_code_block('<br>'.join(validations['schemas_exportation']['erreurs_schemas']))}</p>"
    sec_err = len(validations.get("securite_erreurs", {}).get("points_vulnerables", []))
    html += f"<div class='task-item'> <div class='task-title'>2.4. Audit Sécurité et Erreurs</div> {_gen_status_tag(sec_err == 0, sec_err)} </div>"
    if sec_err > 0:
        html += f"<p>Points vulnérables: {_gen_code_block('<br>'.join(validations['securite_erreurs']['points_vulnerables']))}</p>"
    precommit_valide = validations.get("integration_qualite", {}).get(
        "precommit_valide", False
    )
        """TODO: Add docstring."""
    precommit_err = len(
        validations.get("integration_qualite", {}).get("erreurs_precommit", [])
    )
    html += f"<div class='task-item'> <div class='task-title'>2.5. Intégration Outils Qualité</div> {_gen_status_tag(precommit_valide, precommit_err)} </div>"
    if precommit_err > 0:
        html += f"<p>Erreurs pre-commit: {_gen_code_block('<br>'.join(validations['integration_qualite']['erreurs_precommit']))}</p>"
    mem_disk_ok = all(validations.get("gestion_memoire_disque", {}).values())
    html += f"<div class='task-item'> <div class='task-title'>2.6. Gestion Mémoire et Disque</div> {_gen_status_tag(mem_disk_ok)} </div>"
    return html


def _gen_section_tests(data):
    html = ""
    tests = data.get("tests", {})
    if "erreur" in tests:
        return f"<div class='task-item error'>Rapport tests non disponible: {tests['erreur']}</div>"
    dyn_tests = tests.get("tests_dynamiques", {})
    unit_tests = dyn_tests.get("tests_unitaires", {})
    exec_count = unit_tests.get("tests_executes", 0)
    fail_count = unit_tests.get("tests_echecs", 0)
    html += f"<div class='task-item'> <div class='task-title'>3.1. Tests Unitaires</div> {_gen_status_tag(fail_count == 0 and exec_count > 0, fail_count, fail_count)} </div>"
    if fail_count > 0:
        html += f"<p>Détails échecs: {_gen_code_block('<br>'.join(unit_tests['details_echecs']))}</p>"
    integ_tests = dyn_tests.get("tests_integration", {})
    integ_ok = integ_tests.get("communication_processus", False) and integ_tests.get(
        "queues_fonctionnelles", False
    )
    integ_err = len(integ_tests.get("erreurs_integration", []))
        """TODO: Add docstring."""
    html += f"<div class='task-item'> <div class='task-title'>3.2. Tests d'Intégration</div> {_gen_status_tag(integ_ok, integ_err, integ_err)} </div>"
    if integ_err > 0:
        html += f"<p>Erreurs intégration: {_gen_code_block('<br>'.join(integ_tests['erreurs_integration']))}</p>"
    scenario_tests = dyn_tests.get("scenario_minetest", {})
    scenario_ok = scenario_tests.get("etat_final_valide", False)
    scenario_err = len(scenario_tests.get("erreurs_scenario", []))
    html += f"<div class='task-item'> <div class='task-title'>3.3. Scénarios Minetest</div> {_gen_status_tag(scenario_ok, scenario_err, scenario_err)} </div>"
    if scenario_err > 0:
        html += f"<p>Erreurs scénario: {_gen_code_block('<br>'.join(scenario_tests['erreurs_scenario']))}</p>"
    return html


def _gen_section_ia(data):
    html = ""
    ia_data = data.get("ia", {})
    if "erreur" in ia_data:
        return f"<div class='task-item error'>Rapport IA non disponible: {ia_data['erreur']}</div>"
    eval_ia = ia_data.get("evaluations_ia", {})
    autonomie = eval_ia.get("autonomie_decisions", {})
    proactive_ratio = (
        (
            autonomie.get("decisions_proactives", 0)
            / (
                autonomie.get("decisions_proactives", 0)
                + autonomie.get("decisions_reactives", 1)
            )
        )
        if (
            autonomie.get("decisions_proactives", 0)
            + autonomie.get("decisions_reactives", 0)
        )
        > 0
        else 0.0
    )
    html += f"<div class='task-item'> <div class='task-title'>4.1. Autonomie et Décisions</div> {_gen_status_tag(proactive_ratio > 0.5, 0, 1 if proactive_ratio == 0 else 0)} </div>"
    if proactive_ratio == 0:
        html += "<p>Aucune décision proactive détectée.</p>"
    besoins = eval_ia.get("besoins_amelioration", {})
    diff_count = len(besoins.get("domaines_difficultes", []))
    html += f"<div class='task-item'> <div class='task-title'>4.2. Besoins d'Amélioration</div> {_gen_status_tag(diff_count == 0, diff_count)} </div>"
    if diff_count > 0:
        html += f"<p>Domaines de difficultés: {', '.join(besoins['domaines_difficultes'])}</p>"
    ethique_score = eval_ia.get("adherence_ethique", {}).get(
        "score_ethique_global", 0.0
    )
    html += f"<div class='task-item'> <div class='task-title'>4.3. Adhérence Éthique</div> {_gen_status_tag(ethique_score > 0.7, 0, 1 if ethique_score < 0.5 else 0)} </div>"
    connaissances = eval_ia.get("coherence_connaissances", {})
    graphe_ok = connaissances.get("graphe_coherent", False)
    contradictions = connaissances.get("contradictions_detectees", 0)
    html += f"<div class='task-item'> <div class='task-title'>4.4. Cohérence Connaissances</div> {_gen_status_tag(graphe_ok and contradictions == 0, contradictions)} </div>"
    cycles = eval_ia.get("cycles_environnementaux", {})
        """TODO: Add docstring."""
    cycles_ok = cycles.get("adaptation_jour_nuit", False) and cycles.get(
        "adaptation_meteo", False
    )
    html += f"<div class='task-item'> <div class='task-title'>4.5. Exploitation Cycles Environnementaux</div> {_gen_status_tag(cycles_ok)} </div>"
    creativite = eval_ia.get("creativite_nouveaute", {})
    creative_ok = creativite.get("constructions_originales", 0) > 0
    html += f"<div class='task-item'> <div class='task-title'>4.6. Créativité et Nouveauté</div> {_gen_status_tag(creative_ok)} </div>"
    finalite = eval_ia.get("finalite_projet_eve", {})
    eve_prep = finalite.get("preparation_eve", 0.0)
    html += f"<div class='task-item'> <div class='task-title'>4.7. Préparation EVE</div> {_gen_status_tag(eve_prep > 0.7, 0, 1 if eve_prep < 0.5 else 0)} </div>"
    return html


def _gen_recommendations(data):
    html = ""
    recos = []
    statique = data.get("statique", {}).get("taches", {})
    if statique.get("arborescence", {}).get("dossiers_manquants"):
        recos.append("Haute: Compléter l'arborescence du projet.")
    if statique.get("dependances", {}).get("dependances_manquantes"):
        recos.append(
            "Haute: Mettre à jour requirements.txt avec les dépendances manquantes."
        )
    if statique.get("syntaxe_style", {}).get("erreurs_black") or statique.get(
        "syntaxe_style", {}
    ).get("erreurs_flake8"):
        recos.append(
            "Haute: Corriger les erreurs de style et de syntaxe (black, flake8)."
        )
    if statique.get("syntaxe_style", {}).get("fichiers_avec_comments"):
        recos.append(
            "Moyenne: Supprimer les commentaires non-docstrings (Directive 65)."
        )
    if statique.get("refactorisation", {}).get("fichiers_trop_longs") or statique.get(
        "refactorisation", {}
    ).get("fonctions_complexes"):
        recos.append(
            "Moyenne: Refactoriser les fichiers/fonctions trop longs ou complexes (Directives 61, 73, 85)."
        )
    archi = data.get("architecture", {}).get("validations", {})
    if not all(
        archi.get("architecture_globale", {}).get("processus_presents", {}).values()
    ):
        recos.append(
            "Haute: Implémenter tous les processus principaux (lanceur, proc_jeu, proc_ia, proc_gui)."
        )
    if not archi.get("coherence_config", {}).get("config_valide"):
        recos.append("Haute: Corriger la structure et les valeurs de config.json.")
    tests = data.get("tests", {}).get("tests_dynamiques", {})
    if (
        tests.get("tests_unitaires", {}).get("tests_echecs", 0) > 0
        or tests.get("tests_unitaires", {}).get("tests_executes", 0) == 0
    ):
        recos.append("Haute: Écrire/corriger les tests unitaires.")
            """TODO: Add docstring."""
    if not tests.get("scenario_minetest", {}).get("etat_final_valide"):
        recos.append("Haute: Développer des scénarios Minetest fonctionnels.")
    ia_data = data.get("ia", {}).get("evaluations_ia", {})
    if ia_data.get("autonomie_decisions", {}).get("decisions_proactives", 0) == 0:
        recos.append(
            "Moyenne: Améliorer la génération de décisions proactives par l'IA."
        )
    for r in recos:
        priority = r.split(":")[0]
        desc = r.split(":")[1].strip()
        html += f"<div class='task-item {'warning' if priority == 'Moyenne' else ''}'> <div class='task-title'>{priority}</div> <div class='task-description'>{desc}</div> </div>"
    return html


def generer_rapport_html():
    data = _load_report_data()
    stats = calculer_statistiques_avancement(data)
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rapport d'Audit - Le Simulateur</title>
        {_gen_css()}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>RAPPORT D'AUDIT</h1>
                <h2>Projet "Le Simulateur"</h2>
                <p>Généré le {timestamp}</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{stats['score_global']:.1%}</div>
                    <div class="stat-label">Score Global</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['conformite_directives']:.1%}</div>
                    <div class="stat-label">Conformité Directives</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['couverture_tests']:.1%}</div>
                    <div class="stat-label">Couverture Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['maturite_ia']:.1%}</div>
                    <div class="stat-label">Maturité IA</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['preparation_eve']:.1%}</div>
                    <div class="stat-label">Préparation EVE</div>
                </div>
            </div>

            <div class="section">
                <div class="section-header">
                    <h2>1. Analyse Statique du Code</h2>
                </div>
                <div class="section-content">
                    {_gen_section_statique(data)}
                </div>
            </div>

            <div class="section">
                <div class="section-header">
                    <h2>2. Validation Architecture Système</h2>
                </div>
                <div class="section-content">
                    {_gen_section_architecture(data)}
                </div>
            </div>

            <div class="section">
                <div class="section-header">
                    <h2>3. Tests Dynamiques</h2>
                </div>
                <div class="section-content">
                    {_gen_section_tests(data)}
                </div>
            </div>

            <div class="section">
                <div class="section-header">
                    <h2>4. Évaluation Comportement IA</h2>
                </div>
                <div class="section-content">
                    {_gen_section_ia(data)}
                </div>
            </div>

    """TODO: Add docstring."""
            <div class="section">
                <div class="section-header">
                    <h2>5. Recommandations</h2>
                </div>
                <div class="section-content">
                    {_gen_recommendations(data)}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


def main():
    print("Chargement des données de rapport...")
    data = _load_report_data()
    print("Calcul des statistiques d'avancement...")
    stats = calculer_statistiques_avancement(data)
    print("Génération du rapport HTML...")
    html_content = generer_rapport_html()
    with open("rapport_audit_simulateur.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Rapport HTML généré avec succès: rapport_audit_simulateur.html")
    print(f"Score global du projet: {stats['score_global']:.1%}")


if __name__ == "__main__":
    main()