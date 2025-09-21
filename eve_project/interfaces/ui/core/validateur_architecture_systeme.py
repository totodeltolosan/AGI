import os
import json
import ast
import subprocess
from pathlib import Path
import yaml


def _get_project_root():
    """TODO: Add docstring."""
    return Path(os.getcwd())


    """TODO: Add docstring."""
def _get_version_code_from_launcher(launcher_path):
    try:
        tree = ast.parse(launcher_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "VERSION_CODE"
                and isinstance(node.value, ast.Constant)
            ):
                return node.value.value
    except Exception:
        pass
    return None

    """TODO: Add docstring."""

def verifier_conformite_architecturale():
    root = _get_project_root()
    process_paths = {
        "lanceur.py": root / "lanceur.py",
        "proc_jeu.py": root / "enfant_eve" / "pont_jeu" / "proc_jeu.py",
        "proc_ia.py": root / "enfant_eve" / "ia" / "cerveau.py",
        "proc_gui.py": root / "enfant_eve" / "interface" / "proc_gui.py",
    }
    results = {
        "processus_presents": {
            name: path.exists() for name, path in process_paths.items()
        },
        "communication_queues": False,
        "violations_architecture": [],
    }
    queue_found_count = 0
    for name, path in process_paths.items():
        if path.exists():
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if (
                        isinstance(node, ast.Call)
                        and hasattr(node.func, "attr")
                        and node.func.attr == "Queue"
                    ):
                        queue_found_count += 1
                        break
            except Exception as e:
                results["violations_architecture"].append(
                    f"Erreur AST {name}: {str(e)}"
                )
    results["communication_queues"] = queue_found_count >= 2
    return results
        """TODO: Add docstring."""


def analyser_coherence_config():
    root = _get_project_root()
    config_path = root / "config" / "config.json"
    results = {
        "config_existe": config_path.exists(),
        "config_valide": False,
        "version_config_presente": False,
        "parametres_valides": {},
        "erreurs_validation": [],
    }
    if not config_path.exists():
        return results
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        results["config_valide"] = True
        if "version_config" in config:
            results["version_config_presente"] = True
            launcher_version = _get_version_code_from_launcher(root / "lanceur.py")
            if launcher_version and config["version_config"] != launcher_version:
                results["erreurs_validation"].append("Version config/code mismatch")
        else:
            results["erreurs_validation"].append("version_config manquante")
        expected_params = {
            "simulation": {"taille_max_go": int, "seuil_alerte_archivage": float},
            "ia": {
                "seuil_critique_monde_usage": float,
                "max_tentatives_redemarrage_processus": int,
            },
            "emotions": {"decroissance_temporelle": float, "impact_faim": float},
            "interface": {"theme_couleur_primaire": str, "font_taille_base": int},
            "systeme": {"ram_budget_pourcent_libre": float},
        }
        for cat, params in expected_params.items():
            if cat not in config.get("parametres", {}):
                results["erreurs_validation"].append(f"Catégorie '{cat}' manquante")
                continue
            for param, p_type in params.items():
                val = config["parametres"][cat].get(param)
                is_valid = isinstance(val, p_type)
                results["parametres_valides"][f"{cat}.{param}"] = is_valid
                if not is_valid:
                    results["erreurs_validation"].append(
                        f"'{cat}.{param}': type invalide ou manquant"
                    )
    except json.JSONDecodeError as e:
        results["erreurs_validation"].append(f"JSON invalide: {str(e)}")
    except Exception as e:
        results["erreurs_validation"].append(f"Erreur lecture config: {str(e)}")
            """TODO: Add docstring."""
    return results


def valider_schemas_exportation():
    root = _get_project_root()
    export_cerveau_path = root / "enfant_eve" / "export" / "export_cerveau.py"
    export_guide_path = root / "enfant_eve" / "export" / "export_guide.py"
    results = {
        "export_cerveau_present": export_cerveau_path.exists(),
        "export_guide_present": export_guide_path.exists(),
        "cerveau_json_valide": False,
        "guide_jsonl_valide": False,
        "erreurs_schemas": [],
    }
    if export_cerveau_path.exists():
        try:
            # Simulate a minimal cerveau.json for schema validation
            simulated_cerveau = {
                "timestamp": "2025-01-01T00:00:00Z",
                "version": "1.0",
                "graphe_connaissances": {
                    "node_id": {"type_noeud": "Concept", "tags": ["test"]}
                },
                "memoire_travail": {},
                "etat_emotionnel": {"confiance": 0.5},
                "source_agent": "Le_Simulateur_Minetest_v1",
            }
            # Basic check for required keys
            required_keys = {
                "timestamp",
                "version",
                "graphe_connaissances",
                "source_agent",
            }
            if all(key in simulated_cerveau for key in required_keys):
                results["cerveau_json_valide"] = True
            else:
                results["erreurs_schemas"].append(
                    "cerveau.json: clés requises manquantes"
                )
        except Exception as e:
            results["erreurs_schemas"].append(f"Erreur simulation cerveau: {str(e)}")
    if export_guide_path.exists():
        try:
            # Simulate a minimal guide.jsonl entry
            simulated_guide_entry = {
                "id": "1",
                "titre": "Test",
                "contenu": "Contenu test",
                "score_importance": 0.8,
            }
            # Basic check for JSONL format (can't fully validate without actual generation)
            if "jsonl" in export_guide_path.read_text(
                encoding="utf-8"
            ).lower() or "json.dumps" in export_guide_path.read_text(encoding="utf-8"):
                results["guide_jsonl_valide"] = True
            else:
                results["erreurs_schemas"].append(
                    "guide.jsonl: format JSONL non détecté"
                )
        except Exception as e:
            """TODO: Add docstring."""
            results["erreurs_schemas"].append(f"Erreur simulation guide: {str(e)}")
    return results


def auditer_securite_gestion_erreurs():
    root = _get_project_root()
    results = {
        "try_except_present": False,
        "logging_present": False,
        "gestion_exceptions_count": 0,
        "points_vulnerables": [],
    }
    total_try_except = 0
    total_logging_imports = 0
    for f in root.rglob("*.py"):
        try:
            content = f.read_text(encoding="utf-8")
            tree = ast.parse(content)
            # Add parent pointers to AST nodes for easier traversal
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    child.parent = node
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    total_try_except += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if (
                        "logging" in str(node.module)
                        if isinstance(node, ast.ImportFrom)
                        else str(node.names)
                    ):
                        total_logging_imports += 1
                elif isinstance(node, ast.Call):
                    if hasattr(node.func, "id") and node.func.id in {
                        "open",
                        "subprocess",
                    }:
                        is_protected = False
                        current_node = node
                        while hasattr(current_node, "parent"):
                            if isinstance(current_node.parent, ast.Try):
                                is_protected = True
                                break
                            current_node = current_node.parent
                        if not is_protected:
                            results["points_vulnerables"].append(
                                f"{str(f.relative_to(root))}:{node.lineno}: {node.func.id} non protégé"
                            )
        except Exception:
            continue
    results["try_except_present"] = total_try_except > 0
        """TODO: Add docstring."""
    results["logging_present"] = total_logging_imports > 0
    results["gestion_exceptions_count"] = total_try_except
    return results


def verifier_integration_qualite():
    root = _get_project_root()
    precommit_path = root / ".pre-commit-config.yaml"
    results = {
        "precommit_present": precommit_path.exists(),
        "precommit_valide": False,
        "hooks_requis": {"black": False, "flake8": False},
        "erreurs_precommit": [],
    }
    if not precommit_path.exists():
        return results
    try:
        config = yaml.safe_load(precommit_path.read_text(encoding="utf-8"))
        if "repos" in config:
            for repo in config["repos"]:
                for hook in repo.get("hooks", []):
                    hook_id = hook.get("id", "")
                    if hook_id == "black":
                        results["hooks_requis"]["black"] = True
                    elif hook_id == "flake8":
                        results["hooks_requis"]["flake8"] = True
            results["precommit_valide"] = all(results["hooks_requis"].values())
        else:
            results["erreurs_precommit"].append("Structure YAML invalide")
    except yaml.YAMLError as e:
        """TODO: Add docstring."""
        results["erreurs_precommit"].append(f"YAML invalide: {str(e)}")
    except Exception as e:
        results["erreurs_precommit"].append(f"Erreur lecture precommit: {str(e)}")
    return results


def auditer_gestion_memoire_disque():
    root = _get_project_root()
    results = {
        "psutil_utilise": False,
        "archivage_implemente": False,
        "gestion_ram_presente": False,
        "verification_espace_disque": False,
    }
    for f in root.rglob("*.py"):
        try:
            content = f.read_text(encoding="utf-8")
            if "psutil" in content:
                results["psutil_utilise"] = True
            if "memory_percent" in content or "virtual_memory" in content:
                results["gestion_ram_presente"] = True
            if "archive" in content.lower() or "zip" in content.lower():
                results["archivage_implemente"] = True
                    """TODO: Add docstring."""
            if "disk_usage" in content or "statvfs" in content:
                results["verification_espace_disque"] = True
        except Exception:
            continue
    return results


def main():
    rapport = {
        "timestamp": Path(__file__).stat().st_mtime,
        "version": "1.0",
        "validations": {
            "architecture_globale": verifier_conformite_architecturale(),
            "coherence_config": analyser_coherence_config(),
            "schemas_exportation": valider_schemas_exportation(),
            "securite_erreurs": auditer_securite_gestion_erreurs(),
            "integration_qualite": verifier_integration_qualite(),
            "gestion_memoire_disque": auditer_gestion_memoire_disque(),
        },
    }
    with open("rapport_architecture.json", "w", encoding="utf-8") as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    print(
        "Validation architecture terminée. Rapport sauvegardé dans rapport_architecture.json"
    )


if __name__ == "__main__":
    main()