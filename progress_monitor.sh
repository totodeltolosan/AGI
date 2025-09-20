#!/bin/bash
echo "📊 SUIVI PROGRESSION AGI CONSTITUTIONNEL"
echo "========================================"
echo "Total issues audit: $(gh issue list --label audit --json number | jq length)"
echo "Issues critiques: $(gh issue list --label critical --json number | jq length)"
echo "Issues ouvertes: $(gh issue list --state open --json number | jq length)"
echo "Issues fermées: $(gh issue list --state closed --json number | jq length)"
echo ""
echo "🎯 Taux de résolution: $(gh issue list --state closed --json number | jq length) / 328 = $(( $(gh issue list --state closed --json number | jq length) * 100 / 328 ))%"
