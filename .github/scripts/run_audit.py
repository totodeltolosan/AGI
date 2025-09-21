import json
import os
from collections import defaultdict
import sys


# --- CLASSE POUR GÉRER LE RAPPORT ---
class AuditReport:
    def __init__(self, filename="constitutional-report.md"):
        self.filename = filename
        self.content = []

    def add_header(self, text, level=2):
        self.content.append(f"\n{'#' * level} {text}\n")

    def add_line(self, text=""):
        self.content.append(text)

    def write(self):
        # On ajoute au fichier existant au lieu de l'écraser
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write("\n".join(self.content))

    # --- FONCTION D'AUDIT DE LA CONSTITUTION ---
    def audit_constitution_file(report):
        report.add_header("📜 Analyse de la Constitution (iaGOD.json)")
        try:
            with open("iaGOD.json", "r", encoding="utf-8") as f:
                constitution = json.load(f)

            laws_count = len(constitution.get("laws", []))
            principles_count = len(constitution.get("principles", []))

            report.add_line(f"- ✅ **Lois constitutionnelles** : {laws_count}")
            report.add_line(f"- ✅ **Principes fondamentaux** : {principles_count}")

            required_laws = [
                "200_lines_limit",
                "documentation_required",
                "security_compliance",
            ]
            for law in required_laws:
                if any(law in str(l) for l in constitution.get("laws", [])):
                    report.add_line(f"- ✅ **Loi requise** `{law}` : Définie")
                else:
                    report.add_line(f"- ⚠️ **Loi requise** `{law}` : Manquante")
            return True

        except FileNotFoundError:
            report.add_line(
                "- ❌ **Erreur Critique** : Fichier `iaGOD.json` non trouvé."
            )
            return False
        except json.JSONDecodeError as e:
            report.add_line(
                f"- ❌ **Erreur Critique** : Fichier `iaGOD.json` mal formaté. Erreur : {e}"
            )
            return False
        except Exception as e:
            report.add_line(
                f"- ❌ **Erreur Critique** : Erreur inattendue lors de la lecture du fichier. Erreur : {e}"
            )
            return False

    # --- FONCTION D'AUDIT DE LA LONGUEUR DES FICHIERS ---
    def audit_file_length(report):
        report.add_header("📏 Audit de la Loi des 200 Lignes")
        violations = []

        for root, dirs, files in os.walk("."):
            if ".git" in dirs:
                dirs.remove(".git")  # Exclure le répertoire .git

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    try:
                        with open(
                            filepath, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            num_lines = len(f.readlines())
                        if num_lines > 200:
                            violations.append({"file": filepath, "lines": num_lines})
                    except IOError:
                        # Ignorer les fichiers qui ne peuvent pas être lus
                        pass

        total_files = sum(len(files) for _, _, files in os.walk(".") if ".git" not in _)
        total_py_files = (
            sum(1 for v in violations)
            + sum(1 for _, _, files in os.walk(".") for f in files if f.endswith(".py"))
            - len(violations)
        )

        report.add_line(f"- **Fichiers Python analysés** : {total_py_files}")
        report.add_line(f"- **Violations détectées** : {len(violations)}")

        if violations:
            report.add_line("\n| Fichier en Violation | Nombre de Lignes |")
            report.add_line("|---|---|")
            for v in sorted(violations, key=lambda x: x["lines"], reverse=True)[
                :10
            ]:  # Top 10
                report.add_line(f"| `{v['file']}` | **{v['lines']}** |")
        else:
            report.add_line(
                "\n- ✅ **Verdict** : Conformité exemplaire. Aucun fichier ne dépasse la limite de 200 lignes."
            )

        # Exporte le nombre de violations pour les étapes suivantes
        print(f"::set-output name=line_violations::{len(violations)}")


# --- SCRIPT PRINCIPAL ---
if __name__ == "__main__":
    main_report = AuditReport()

    # Exécuter l'audit de la constitution
    if not audit_constitution_file(main_report):
        main_report.write()
        sys.exit(1)  # Arrêter le script si la constitution est invalide

    # Exécuter l'audit de la longueur des fichiers
    audit_file_length(main_report)

    # Écrire le rapport final
    main_report.write()

# ==============================================================================
# FONCTION D'AUDIT DE SÉCURITÉ
# ------------------------------------------------------------------------------
# Cette fonction sera ajoutée à notre script Python principal.
# ==============================================================================


def audit_security(report):
    """
    Analyse les fichiers Python à la recherche de patterns de code potentiellement dangereux.
    """
    report.add_header("🛡️ Audit de la Loi de Sécurité Constitutionnelle")

    # Règles de sécurité définies avec des expressions régulières compilées pour la performance.
    security_rules = [
        {
            "id": "SEC001",
            "pattern": re.compile(r"eval\s*\("),
            "severity": "critical",
            "description": "Usage de `eval()` interdit",
        },
        {
            "id": "SEC002",
            "pattern": re.compile(r"exec\s*\("),
            "severity": "critical",
            "description": "Usage de `exec()` interdit",
        },
        {
            "id": "SEC003",
            "pattern": re.compile(r"subprocess\.call\s*\(.*shell=True"),
            "severity": "critical",
            "description": "Risque d'injection shell avec `shell=True`",
        },
        {
            "id": "SEC004",
            "pattern": re.compile(r"pickle\.loads?\s*\("),
            "severity": "high",
            "description": "Risque de désérialisation non sécurisée avec `pickle`",
        },
        {
            "id": "SEC005",
            "pattern": re.compile(r"__import__\s*\("),
            "severity": "high",
            "description": "Usage d'import dynamique non contrôlé",
        },
    ]

    violations = []
    files_scanned = 0

    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                files_scanned += 1
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        # Lire ligne par ligne pour obtenir le numéro de ligne exact
                        for line_num, line_content in enumerate(f, 1):
                            for rule in security_rules:
                                if rule["pattern"].search(line_content):
                                    violations.append(
                                        {
                                            "file": filepath,
                                            "line": line_num,
                                            "rule_id": rule["id"],
                                            "description": rule["description"],
                                            "severity": rule["severity"],
                                            "code": line_content.strip(),
                                        }
                                    )
                except IOError as e:
                    report.add_line(
                        f"- ⚠️ Erreur de lecture sur le fichier `{filepath}`: {e}"
                    )

    # --- Génération du rapport de sécurité ---
    report.add_line(f"- **Fichiers Python analysés** : {files_scanned}")
    report.add_line(f"- **Violations de sécurité détectées** : {len(violations)}")

    if violations:
        # Regrouper les violations par sévérité
        by_severity = defaultdict(list)
        for v in violations:
            by_severity[v["severity"]].append(v)

        report.add_line("\n### Répartition par Sévérité")
        for severity in ["critical", "high", "medium", "low"]:
            if severity in by_severity:
                count = len(by_severity[severity])
                icon = {"critical": "🚨", "high": "🔥", "medium": "⚠️", "low": "➡️"}[
                    severity
                ]
                report.add_line(
                    f"- {icon} **{severity.capitalize()}** : {count} violation(s)"
                )

        report.add_line("\n### Détail des Violations Critiques")
        report.add_line("| Sévérité | Fichier:Ligne | Règle Violée | Code Suspect |")
        report.add_line("|---|---|---|---|")
        # Afficher toutes les violations, triées par sévérité
        for v in sorted(
            violations,
            key=lambda x: ["critical", "high", "medium", "low"].index(x["severity"]),
        )[
            :15
        ]:  # Top 15
            report.add_line(
                f"| {v['severity'].capitalize()} | `{v['file']}:{v['line']}` | {v['description']} | `{v['code']}` |"
            )

    # Verdict final
    report.add_line("\n### Verdict de Sécurité Constitutionnelle")
    critical_violations_count = len(by_severity.get("critical", []))
    if critical_violations_count > 0:
        report.add_line(
            f"- 🚨 **NON-CONFORME** : {critical_violations_count} violation(s) critique(s) détectée(s). Correction immédiate requise."
        )
    elif len(violations) == 0:
        report.add_line(
            "- ✅ **CONFORMITÉ EXCELLENTE** : Aucune violation de sécurité détectée."
        )
    else:
        report.add_line(
            "- ⚠️ **CONFORMITÉ PARTIELLE** : Des violations non-critiques ont été détectées. Un audit manuel est recommandé."
        )

    # Exporte le nombre de violations critiques pour les étapes suivantes
    print(f"::set-output name=security_violations::{len(violations)}")
    print(
        f"::set-output name=critical_security_violations::{critical_violations_count}"
    )


# ==============================================================================
# FONCTION D'AUDIT DE LA DOCUMENTATION
# ------------------------------------------------------------------------------
# Cette fonction sera ajoutée à notre script Python principal.
# ==============================================================================


def audit_documentation(report):
    """
    Analyse les fichiers Python pour vérifier la couverture des docstrings.
    """
    report.add_header("📚 Audit de la Loi de Documentation")

    stats = defaultdict(int)
    missing_docs = []

    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                stats["total_modules"] += 1
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                        tree = ast.parse(source)

                    if not ast.get_docstring(tree):
                        missing_docs.append(
                            f"`{filepath}`: Docstring de module manquant"
                        )
                    else:
                        stats["documented_modules"] += 1

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            stats["total_classes"] += 1
                            if not ast.get_docstring(node):
                                missing_docs.append(
                                    f"`{filepath}:{node.lineno}`: Classe `{node.name}`"
                                )
                            else:
                                stats["documented_classes"] += 1
                        elif isinstance(
                            node, ast.FunctionDef
                        ) and not node.name.startswith("_"):
                            stats["total_functions"] += 1
                            if not ast.get_docstring(node):
                                missing_docs.append(
                                    f"`{filepath}:{node.lineno}`: Fonction `{node.name}`"
                                )
                            else:
                                stats["documented_functions"] += 1

                except SyntaxError as e:
                    report.add_line(
                        f"- ⚠️ **Erreur de syntaxe** dans `{filepath}` (ligne {e.lineno}). Fichier ignoré de l'analyse de documentation."
                    )
                except Exception as e:
                    report.add_line(f"- ⚠️ **Erreur inattendue** sur `{filepath}`: {e}")

    # --- Génération du rapport de documentation ---
    def get_rate(documented, total):
        return (documented / max(total, 1)) * 100

    overall_documented = (
        stats["documented_modules"]
        + stats["documented_classes"]
        + stats["documented_functions"]
    )
    overall_total = (
        stats["total_modules"] + stats["total_classes"] + stats["total_functions"]
    )
    overall_rate = get_rate(overall_documented, overall_total)

    report.add_line("\n### Taux de Couverture de la Documentation")
    report.add_line("| Catégorie | Documentés / Total | Taux de Couverture |")
    report.add_line("|---|---|---|")
    report.add_line(
        f"| Modules   | {stats['documented_modules']} / {stats['total_modules']} | {get_rate(stats['documented_modules'], stats['total_modules']):.1f}% |"
    )
    report.add_line(
        f"| Classes   | {stats['documented_classes']} / {stats['total_classes']} | {get_rate(stats['documented_classes'], stats['total_classes']):.1f}% |"
    )
    report.add_line(
        f"| Fonctions | {stats['documented_functions']} / {stats['total_functions']} | {get_rate(stats['documented_functions'], stats['total_functions']):.1f}% |"
    )
    report.add_line(
        f"| **Global**  | **{overall_documented} / {overall_total}** | **{overall_rate:.1f}%** |"
    )

    # Verdict
    report.add_line("\n### Verdict de Documentation Constitutionnelle")
    if overall_rate >= 90:
        report.add_line("- ✅ **EXCELLENCE** : Couverture documentaire exemplaire.")
    elif overall_rate >= 70:
        report.add_line("- 👍 **BONNE** : Couverture satisfaisante.")
    else:
        report.add_line(
            "- ❌ **NON-CONFORME** : Couverture documentaire insuffisante. Action requise."
        )

    # Exporte le taux de couverture global pour les étapes suivantes
    print(f"::set-output name=doc_coverage::{overall_rate:.1f}")

# --- DÉFINITION DU CHEMIN DU SCRIPT ---
SCRIPT_FILE="/home/toni/Documents/Projet AGI/.github/scripts/run_audit.py"

# --- AJOUTER LE POINT D'ENTRÉE MANQUANT AU SCRIPT ---
cat >> "$SCRIPT_FILE" << 'EOF'

# --- SCRIPT PRINCIPAL (POINT D'ENTRÉE) ---
if __name__ == "__main__":
    # Initialiser le rapport
    main_report = AuditReport()

    # Exécuter l'audit de la constitution
    if not audit_constitution_file(main_report):
        main_report.write()
        print("::error::Audit de la constitution a échoué. Arrêt du workflow.")
        sys.exit(1) # Arrêter le script si la constitution est invalide

    # Exécuter les autres audits
    line_violations = audit_file_length(main_report)
    total_sec_violations, critical_sec_violations = audit_security(main_report)
    audit_documentation(main_report)

    # Écrire le rapport final sur le disque
    main_report.write()

    # Exporter les résultats pour les étapes suivantes du workflow
    print(f"::set-output name=line_violations::{line_violations}")
    print(f"::set-output name=critical_security_violations::{critical_sec_violations}")

    print("\n✅ Script d'audit terminé avec succès.")
EOF

echo "✅ Point d'entrée ajouté à run_audit.py. Le script est maintenant complet."
