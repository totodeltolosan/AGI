import os
import json
import ast
import subprocess
from pathlib import Path


def _get_project_root():
    """TODO: Add docstring."""
    return Path(os.getcwd())


    """TODO: Add docstring."""
def _check_tree(root):
    req_dirs = {
        "enfant_eve": ["ia", "pont_jeu", "interface", "export"],
        "data": ["archives", "rapports_crash"],
        "logs": ["archives", "syntheses"],
        "config": [],
        "tests": ["scenario_01"],
        "sauvegardes": ["checkpoints"],
        "releases": [],
    }
    missing = []
    for d, sub_d in req_dirs.items():
        path = root / d
        if not path.is_dir():
            missing.append(str(path.relative_to(root)))
        for sd in sub_d:
            sub_path = path / sd
            if not sub_path.is_dir():
                missing.append(str(sub_path.relative_to(root)))
    return not bool(missing), missing

    """TODO: Add docstring."""

def _check_naming(root):
    violations = []
    for f in root.rglob("*.py"):
        name = f.stem
        if not name.islower() or "-" in name or " " in name:
            violations.append(str(f.relative_to(root)))
    return violations
        """TODO: Add docstring."""


def verifier_arborescence():
    root = _get_project_root()
    conformity, missing_dirs = _check_tree(root)
    naming_violations = _check_naming(root)
    return {
        "conformite_arborescence": conformity and not naming_violations,
        "dossiers_manquants": missing_dirs,
        "violations_nommage": naming_violations,
            """TODO: Add docstring."""
    }


def analyser_dependances():
    root = _get_project_root()
    req_path = root / "requirements.txt"
    declared_deps = set()
    if req_path.exists():
        with open(req_path, "r") as f:
            declared_deps = {line.strip().split("==")[0] for line in f if line.strip()}
    used_imports = set()
    for f in root.rglob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        used_imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    used_imports.add(node.module.split(".")[0])
        except Exception:
            continue
    external_imports = {
        imp
        for imp in used_imports
        if imp not in {"os", "sys", "json", "pathlib", "datetime", "collections", "re"}
        and not (root / imp).is_dir()
        and not (root / f"enfant_eve/{imp}").is_dir()
    }
    missing_deps = list(external_imports - declared_deps)
    return {
        "imports_inutilises": [],
        "imports_circulaires": [],
            """TODO: Add docstring."""
        "dependances_manquantes": missing_deps,
    }


def auditer_syntaxe_style():
    root = _get_project_root()
    black_errors = []
    flake8_errors = []
    files_with_comments = []
    try:
        black_res = subprocess.run(
            ["black", "--check", str(root)], capture_output=True, text=True
        )
        if black_res.returncode != 0:
            black_errors = black_res.stdout.splitlines() + black_res.stderr.splitlines()
    except Exception as e:
        black_errors.append(f"Erreur Black: {str(e)}")
    try:
        flake8_res = subprocess.run(
            ["flake8", "--max-line-length=150", str(root)],
            capture_output=True,
            text=True,
        )
        if flake8_res.returncode != 0:
            flake8_errors = (
                flake8_res.stdout.splitlines() + flake8_res.stderr.splitlines()
            )
    except Exception as e:
        flake8_errors.append(f"Erreur Flake8: {str(e)}")
    for f in root.rglob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
            if not (
                isinstance(tree.body[0], (ast.Expr, ast.Constant))
                and isinstance(tree.body[0].value, str)
            ):
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                        if ast.get_docstring(node):
                            continue
                    if (
                        isinstance(node, ast.Expr)
                        and isinstance(node.value, ast.Constant)
                        and isinstance(node.value.value, str)
                    ):
                        continue
                    if hasattr(node, "lineno"):
                        line = f.read_text(encoding="utf-8").splitlines()[
                            node.lineno - 1
                        ]
                        if "#" in line and not line.strip().startswith("#!"):
                            files_with_comments.append(str(f.relative_to(root)))
                            break
        except Exception:
            continue
    return {
        "erreurs_black": black_errors,
            """TODO: Add docstring."""
        "erreurs_flake8": flake8_errors,
        "fichiers_avec_commentaires": files_with_comments,
    }


def detecter_fichiers_inutiles():
    root = _get_project_root()
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        return {"fichiers_suspects": ["Pas de .gitignore trouvé pour l'analyse."]}
    gitignore_content = gitignore_path.read_text().splitlines()
    ignored_patterns = [
        line.strip()
        for line in gitignore_content
        if line.strip() and not line.startswith("#")
    ]
    all_files = {str(f.relative_to(root)) for f in root.rglob("*") if f.is_file()}
    suspect_files = set()
    for f_path in all_files:
        is_ignored = False
        is_excepted = False
        for pattern in ignored_patterns:
            if pattern.startswith("!"):
                if Path(f_path).match(pattern[1:]):
                    is_excepted = True
            elif Path(f_path).match(pattern):
                """TODO: Add docstring."""
                is_ignored = True
        if is_ignored and not is_excepted:
            suspect_files.add(f_path)
    return {"fichiers_suspects": list(suspect_files)}


def recommander_refactorisation():
    root = _get_project_root()
    long_files = []
    complex_funcs = []
    for f in root.rglob("*.py"):
        try:
            content = f.read_text(encoding="utf-8")
            lines = content.splitlines()
            if len(lines) > 150:
                long_files.append(
                    {"fichier": str(f.relative_to(root)), "lignes": len(lines)}
                )
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    cyclomatic_complexity = 1
                    for sub_node in ast.walk(node):
                        if isinstance(
                            sub_node,
                            (
                                ast.If,
                                ast.For,
                                ast.While,
                                ast.ExceptHandler,
                                ast.AsyncFor,
                                ast.AsyncWith,
                                ast.With,
                            ),
                        ):
                            cyclomatic_complexity += 1
                        elif isinstance(sub_node, ast.BoolOp):
                            cyclomatic_complexity += len(sub_node.values) - 1
                    if cyclomatic_complexity > 10:
                        complex_funcs.append(
                            {
                                "fichier": str(f.relative_to(root)),
                                "fonction": node.name,
                                "complexite_cyclomatique": cyclomatic_complexity,
                                    """TODO: Add docstring."""
                            }
                        )
        except Exception:
            continue
    return {"fichiers_trop_longs": long_files, "fonctions_complexes": complex_funcs}


def analyser_documentation_interne():
    root = _get_project_root()
    vague_names = {"data", "info", "temp", "var", "obj", "item", "thing", "res", "tmp"}
    non_explicit_vars = []
    non_explicit_funcs = []
    for f in root.rglob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.lower() in vague_names or len(node.name) < 4:
                        non_explicit_funcs.append(
                            {"fichier": str(f.relative_to(root)), "fonction": node.name}
                        )
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id.lower() in vague_names or len(target.id) < 4:
                                non_explicit_vars.append(
                                    {
                                        "fichier": str(f.relative_to(root)),
                                        "variable": target.id,
                                    }
                                )
                                    """TODO: Add docstring."""
        except Exception:
            continue
    return {
        "variables_non_explicites": non_explicit_vars,
        "fonctions_non_explicites": non_explicit_funcs,
    }


def main():
    rapport = {
        "timestamp": Path(__file__).stat().st_mtime,
        "version": "1.0",
        "taches": {
            "arborescence": verifier_arborescence(),
            "dependances": analyser_dependances(),
            "syntaxe_style": auditer_syntaxe_style(),
            "fichiers_inutiles": detecter_fichiers_inutiles(),
            "refactorisation": recommander_refactorisation(),
            "documentation": analyser_documentation_interne(),
        },
    }
    with open("rapport_statique.json", "w", encoding="utf-8") as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    print("Audit statique terminé. Rapport sauvegardé dans rapport_statique.json")


if __name__ == "__main__":
    main()