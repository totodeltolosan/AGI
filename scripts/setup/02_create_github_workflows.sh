#!/bin/bash
#
# SCRIPT DE CRÉATION DES WORKFLOWS GITHUB ACTIONS
# Ce script met en place les gardiens automatisés de notre projet.
#

echo "--- Étape 1/2 : Création de la structure des workflows ---"
mkdir -p .github/workflows
echo "[OK] Répertoire .github/workflows créé."
echo ""

# --- Création du workflow de validation ---
echo "--- Étape 2/2 : Création du workflow d'Audit Constitutionnel (pull_request_validation.yml) ---"
echo "Ce workflow exécutera notre système d'audit sur chaque Pull Request..."
cat << 'EOGW' > .github/workflows/pull_request_validation.yml
name: AGI Constitutional Audit

# Se déclenche sur chaque Pull Request visant la branche 'main'
on:
  pull_request:
    branches: [ main ]

jobs:
  constitutional-check:
    name: Constitutional Check
    runs-on: ubuntu-latest
    steps:
      - name: 1. Checkout du code source
        uses: actions/checkout@v3

      - name: 2. Mise en place de l'environnement Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: 3. Installation des dépendances (sera activé plus tard)
        run: echo "Étape d'installation des dépendances à venir."
        # run: pip install -r requirements.txt

      - name: 4. Exécution de l'Audit Constitutionnel Complet
        id: audit
        run: |
          # Exécute l'audit et sauvegarde la sortie dans un fichier
          python run_agi_audit.py --full --target . > audit_report.txt
        continue-on-error: true # Important pour que l'étape suivante s'exécute même en cas d'échec

      - name: 5. Publication du Rapport d'Audit dans la Pull Request
        # Cette étape ne s'exécute que si l'audit a échoué
        if: steps.audit.outcome == 'failure'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('audit_report.txt', 'utf8');
            const body = \`**🚨 Audit Constitutionnel Échoué 🚨**

            \`\`\`
            \${report}
            \`\`\`

            *Cette vérification est mandatée par la Loi DEV-TOOL-002 de iaGOD.json.*\`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
            
            core.setFailed('L'audit constitutionnel a révélé des violations.');
EOGW
echo "[OK] Fichier .github/workflows/pull_request_validation.yml créé."
echo ""
echo "✅ Workflows GitHub Actions préparés."
