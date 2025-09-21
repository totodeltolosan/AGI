# -*- coding: utf-8 -*-
"""
generateur_html.py (v2.1 - Graphe Amélioré)

Génère un rapport HTML avec un graphe de dépendances visuellement
enrichi : couleurs par dossier, taille par complexité, et info-bulles
contextuelles.
"""

import os
import json
from pathlib import Path

def generer_rapport_complet(graphe_connaissance: dict):
    """
    Génère le rapport HTML complet à partir du graphe de connaissance.
    """
    chemin_rapport = Path(__file__).parent / "rapport_alma.html"
    chemin_css = Path(__file__).parent / "style_rapport.css"

    print("[Générateur] Génération du rapport HTML avec graphe amélioré...")

    # --- 1. Préparation des données pour vis.js ---
    nodes = []
    edges = []
    id_map = {}

    # --- NOUVEAU : Palette de couleurs par dossier ---
    palette_couleurs = {
        "core": "#e06c75",          # Rouge pour le cœur
        "capteurs": "#98c379",      # Vert pour les capteurs
        "sonore": "#61afef",        # Bleu pour le son
        "introspection": "#c678dd", # Violet pour l'introspection
        "racine": "#e5c07b"         # Jaune pour les fichiers à la racine
    }

    for i, fichier_analyse in enumerate(graphe_connaissance["fichiers"]):
        nom_fichier = fichier_analyse["nom"]
        chemin_relatif = Path(fichier_analyse["chemin"]).relative_to(graphe_connaissance["chemin_racine"])

        # Déterminer le groupe (dossier) pour la couleur
        dossier_parent = chemin_relatif.parts[0] if len(chemin_relatif.parts) > 1 else "racine"
        couleur_noeud = palette_couleurs.get(dossier_parent, "#abb2bf") # Gris par défaut

        # Déterminer la taille en fonction du nombre de lignes
        taille_noeud = 15 + (fichier_analyse["taille_lignes"] / 10)

        id_map[nom_fichier] = i
        nodes.append({
            "id": i,
            "label": nom_fichier,
            "title": f"<b>{nom_fichier}.py</b><br>{fichier_analyse['role_docstring'].split(os.linesep)[0]}", # Info-bulle riche
            "value": taille_noeud, # Pour la taille du noeud
            "color": couleur_noeud,
            "font": {"color": "white"}
        })

    for i, fichier_analyse in enumerate(graphe_connaissance["fichiers"]):
        source_id = id_map.get(fichier_analyse["nom"])
        if source_id is None: continue
        for dep_interne in fichier_analyse["dependances_internes"]:
            target_id = id_map.get(dep_interne)
            if target_id is not None:
                edges.append({
                    "from": source_id,
                    "to": target_id,
                    "arrows": "to"
                })

    # --- 2. Construction du contenu HTML (identique) ---
    contenu_html = ""
    for fichier_analyse in graphe_connaissance["fichiers"]:
        nom_fichier = fichier_analyse["nom"]
        contenu_html += f"<article id='{nom_fichier}'>"
        contenu_html += f"<h2>Analyse de : <code>{nom_fichier}.py</code></h2>"
        if fichier_analyse.get("erreur"):
            contenu_html += f"<p style='color:red;'><b>Erreur :</b> {fichier_analyse['erreur']}</p>"
        else:
            contenu_html += f"""
                <b>Taille :</b> {fichier_analyse['taille_lignes']} lignes<br><hr>
                <h4>🧠 Résumé par l'IA :</h4><p class="resume-ia">{fichier_analyse['resume_ia']}</p>
                <h4>📋 Rôle (d'après le docstring) :</h4><p class="docstring"><i>{fichier_analyse['role_docstring'].replace(os.linesep, '<br>')}</i></p><hr>
                <p><b>Classes :</b> {', '.join(f'<code>{c}</code>' for c in fichier_analyse['classes_definies']) or 'Aucune'}</p>
                <p><b>Fonctions :</b> {', '.join(f'<code>{f}()</code>' for f in fichier_analyse['fonctions_definies']) or 'Aucune'}</p>
                <p><b>Dépendances Externes :</b> {', '.join(f'<code>{i}</code>' for i in fichier_analyse['dependances_externes']) or 'Aucune'}</p>
            """
        contenu_html += "</article><div class='separator'></div>"

    # --- 3. CSS (avec des ajouts pour la légende) ---
    css_content = """
    :root { --bg-color: #1c1e22; --primary-color: #282c34; --secondary-color: #3498db; --text-color: #abb2bf; --header-color: #ffffff; --border-color: #4b5263; --link-color: #61afef; --ia-summary-bg: #21252b; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 2em; line-height: 1.6; }
    header { text-align: center; border-bottom: 2px solid var(--secondary-color); padding-bottom: 20px; margin-bottom: 40px; }
    header h1 { color: var(--header-color); font-size: 3em; margin: 0; }
    header p { font-size: 1.2em; color: var(--secondary-color); }
    main { display: grid; grid-template-columns: 400px 1fr; gap: 30px; }
    #navigation-container { background-color: var(--primary-color); border-radius: 8px; border: 1px solid var(--border-color); height: 85vh; position: sticky; top: 20px; display: flex; flex-direction: column; }
    #navigation-graph { flex-grow: 1; }
    #legend { padding: 10px; border-top: 1px solid var(--border-color); }
    #legend span { display: inline-block; margin-right: 15px; font-size: 0.9em; }
    .legend-color { width: 12px; height: 12px; display: inline-block; vertical-align: middle; margin-right: 5px; border-radius: 50%; }
    section#contenu { background-color: var(--primary-color); padding: 20px 40px; border-radius: 8px; border: 1px solid var(--border-color); max-height: 85vh; overflow-y: auto; }
    article { padding-top: 20px; margin-top: -20px; }
    h2 { color: var(--header-color); border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }
    code { background-color: var(--bg-color); padding: 3px 6px; border-radius: 4px; font-family: 'Consolas', monospace; }
    .resume-ia { background-color: var(--ia-summary-bg); border-left: 4px solid var(--secondary-color); padding: 15px; margin: 10px 0; border-radius: 0 5px 5px 0; }
    .docstring { background-color: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px; font-style: italic; }
    .separator { height: 2px; background-color: var(--border-color); margin: 40px 0; }
    """

    # --- 4. Template HTML final avec légende et options de graphe améliorées ---
    html_template = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rapport d'Introspection - Projet ALMA</title>
        <link rel="stylesheet" href="{chemin_css.name}">
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    </head>
    <body>
        <header>
            <h1>Rapport d'Introspection du Projet ALMA</h1>
            <p>Une documentation vivante, générée par Alma elle-même.</p>
        </header>
        <main>
            <div id="navigation-container">
                <div id="navigation-graph"></div>
                <div id="legend">
                    {''.join(f"<span><span class='legend-color' style='background-color:{color};'></span>{name.capitalize()}</span>" for name, color in palette_couleurs.items())}
                </div>
            </div>
            <section id="contenu">
                {contenu_html}
            </section>
        </main>

        <script type="text/javascript">
            const nodes = new vis.DataSet({json.dumps(nodes)});
            const edges = new vis.DataSet({json.dumps(edges)});
            const container = document.getElementById('navigation-graph');
            const data = {{ nodes: nodes, edges: edges }};
            const options = {{
                nodes: {{
                    shape: 'dot', // Forme de point pour un rendu plus "organique"
                    scaling: {{
                        label: {{
                            min: 12,
                            max: 20
                        }}
                    }},
                    font: {{ color: 'white' }}
                }},
                edges: {{
                    color: {{ inherit: 'from' }},
                    smooth: {{ type: "continuous" }}
                }},
                physics: {{
                    barnesHut: {{ gravitationalConstant: -2000, springLength: 95, springConstant: 0.04 }},
                    stabilization: {{ iterations: 2500 }}
                }},
                interaction: {{
                    tooltipDelay: 200,
                    hideEdgesOnDrag: true,
                    hover: true
                }}
            }};
            const network = new vis.Network(container, data, options);
            network.on("selectNode", function (params) {{
                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    const node = nodes.get(nodeId);
                    const element = document.getElementById(node.label);
                    if (element) {{
                        element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

    try:
        with open(chemin_css, 'w', encoding='utf-8') as f: f.write(css_content)
        with open(chemin_rapport, 'w', encoding='utf-8') as f: f.write(html_template)
        print(f"[Générateur] Succès ! Rapport généré : {chemin_rapport}")
        return str(chemin_rapport)
    except Exception as e:
        print(f"[Générateur] ERREUR : Impossible de générer le rapport. {e}")
        return None
