# Templates d'Orchestration GitHub Actions

## orchestration-moderne-example.yml

Template d'exemple montrant la structure correcte pour l'orchestration GitHub Actions :

- ✅ Utilise `uses:` et `needs:` (CORRECT)
- ❌ N'utilise PAS `gh workflow run` (INCORRECT)

Ce template montre comment remplacer les scripts "Contremaîtres" problématiques par des chaînes de jobs YAML natives.

### Structure Recommandée

```yaml
jobs:
  step1:
    uses: ./.github/workflows/workflow1.yml

  step2:
    needs: step1
    uses: ./.github/workflows/workflow2.yml

  step3:
    needs: step2
    uses: ./.github/workflows/workflow3.yml
```

### Éviter

```python
# NE PAS FAIRE - Ceci ne fonctionne pas dans GitHub Actions
subprocess.run(["gh", "workflow", "run", "workflow.yml"])
```
