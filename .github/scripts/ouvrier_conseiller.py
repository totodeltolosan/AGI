#!/usr/bin/env python3
"""
Ouvrier : Conseiller Lignes
Génère des recommandations Markdown basées sur les statistiques d'analyse.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class ConseillerLignes:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Génère des recommandations Markdown')
        parser.add_argument('--artefact-statistiques', required=True,
                          help='Artefact JSON des statistiques')
        parser.add_argument('--sortie', default='recommandations.md',
                          help='Nom du fichier Markdown de sortie')
        parser.add_argument('--niveau-detail', choices=['base', 'detaille', 'expert'], 
                          default='detaille',
                          help='Niveau de détail des recommandations')
        parser.add_argument('--inclure-exemples', action='store_true',
                          help='Inclure des exemples de code dans les recommandations')
        
        self.args = parser.parse_args()
    
    def run(self):
        try:
            print(f"📝 Génération des recommandations")
            print(f"🎯 Niveau : {self.args.niveau_detail}")
            
            # Chargement des statistiques
            statistiques = self._load_statistics()
            
            if not statistiques:
                self._write_empty_recommendations()
                return
            
            # Génération du contenu Markdown
            contenu_md = self._generate_markdown_content(statistiques)
            
            # Écriture du fichier
            self._write_markdown_file(contenu_md)
            
            print(f"✅ Recommandations générées")
            
        except Exception as e:
            print(f"❌ ERREUR lors de la génération des recommandations : {e}", file=sys.stderr)
            sys.exit(1)
    
    def _load_statistics(self):
        try:
            with open(self.args.artefact_statistiques, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erreur chargement statistiques : {e}")
            return None
    
    def _generate_markdown_content(self, stats):
        sections = []
        
        # En-tête
        sections.append(self._generate_header(stats))
        
        # Résumé exécutif
        sections.append(self._generate_executive_summary(stats))
        
        # Analyse détaillée
        if self.args.niveau_detail in ['detaille', 'expert']:
            sections.append(self._generate_detailed_analysis(stats))
        
        # Recommandations principales
        sections.append(self._generate_main_recommendations(stats))
        
        # Actions concrètes
        sections.append(self._generate_action_items(stats))
        
        # Métriques et seuils
        if self.args.niveau_detail == 'expert':
            sections.append(self._generate_metrics_section(stats))
        
        # Exemples de code
        if self.args.inclure_exemples:
            sections.append(self._generate_code_examples())
        
        # Conclusion
        sections.append(self._generate_conclusion(stats))
        
        return '\n\n'.join(sections)
    
    def _generate_header(self, stats):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_fichiers = stats.get('metadonnees', {}).get('total_fichiers_analysees', 0)
        
        return f"""# 📊 Recommandations - Gouvernance des Lignes de Code

**Date de génération :** {timestamp}  
**Fichiers analysés :** {total_fichiers}  
**Limite appliquée :** {stats.get('metadonnees', {}).get('limite_lignes_appliquee', 0)} lignes/fichier

---"""
    
    def _generate_executive_summary(self, stats):
        conformite = stats.get('statistiques_conformite', {})
        base = stats.get('statistiques_base', {})
        
        taux_conformite = conformite.get('taux_conformite', 0)
        moyenne_lignes = base.get('moyenne_lignes', 0)
        
        # Détermination du niveau de priorité
        if taux_conformite >= 95:
            niveau = "🟢 **EXCELLENT**"
            priorite = "Maintenance"
        elif taux_conformite >= 80:
            niveau = "🟡 **BON**"
            priorite = "Amélioration continue"
        elif taux_conformite >= 60:
            niveau = "🟠 **MODÉRÉ**"
            priorite = "Action requise"
        else:
            niveau = "🔴 **CRITIQUE**"
            priorite = "Action urgente"
        
        return f"""## 🎯 Résumé Exécutif

**Niveau de conformité :** {niveau}  
**Taux de conformité :** {taux_conformite:.1f}%  
**Moyenne lignes/fichier :** {moyenne_lignes:.1f}  
**Priorité d'intervention :** {priorite}

### Verdict Global

{self._get_verdict_message(taux_conformite, moyenne_lignes)}"""
    
    def _get_verdict_message(self, taux_conformite, moyenne):
        if taux_conformite >= 95:
            return "✅ La base de code respecte excellemment les standards de taille. Maintenir les bonnes pratiques et surveiller les nouveaux développements."
        elif taux_conformite >= 80:
            return "👍 La base de code respecte globalement les standards. Quelques améliorations ponctuelles sont recommandées."
        elif taux_conformite >= 60:
            return "⚠️ La conformité est modérée. Un plan de refactoring ciblé est recommandé pour améliorer la maintenabilité."
        else:
            return "🚨 La conformité est critique. Un refactoring majeur est nécessaire pour assurer la qualité à long terme."
    
    def _generate_detailed_analysis(self, stats):
        conformite = stats.get('statistiques_conformite', {})
        distribution = stats.get('statistiques_distribution', {})
        base = stats.get('statistiques_base', {})
        
        content = "## 📈 Analyse Détaillée\n\n"
        
        # Répartition par statut
        if 'repartition_statuts' in conformite:
            content += "### Répartition par Statut\n\n"
            for statut, count in conformite['repartition_statuts'].items():
                emoji = self._get_status_emoji(statut)
                content += f"- {emoji} **{statut}** : {count} fichier(s)\n"
            content += "\n"
        
        # Distribution par tailles
        if 'distribution_tranches' in distribution:
            content += "### Distribution par Taille\n\n"
            tranches = distribution['distribution_tranches']
            for tranche, count in tranches.items():
                percentage = (count / base.get('total_fichiers', 1)) * 100
                content += f"- **{tranche} lignes** : {count} fichiers ({percentage:.1f}%)\n"
            content += "\n"
        
        # Outliers
        outliers = distribution.get('outliers', {})
        if outliers.get('count', 0) > 0:
            content += "### ⚠️ Fichiers Atypiques\n\n"
            content += f"**{outliers['count']} fichier(s) atypique(s)** détecté(s) "
            content += f"({outliers.get('pourcentage', 0):.1f}% du total).\n\n"
            
            if outliers.get('values'):
                content += "**Tailles atypiques détectées :**\n"
                for value in outliers['values'][:5]:  # Limiter à 5 exemples
                    content += f"- {value} lignes\n"
                if len(outliers['values']) > 5:
                    content += f"- ... et {len(outliers['values']) - 5} autres\n"
                content += "\n"
        
        return content
    
    def _get_status_emoji(self, statut):
        emojis = {
            'CONFORME': '✅',
            'NON_CONFORME_MINEUR': '⚠️',
            'NON_CONFORME_MAJEUR': '🚨',
            'ERREUR': '❌'
        }
        return emojis.get(statut, '📄')
    
    def _generate_main_recommendations(self, stats):
        conformite = stats.get('statistiques_conformite', {})
        taux_conformite = conformite.get('taux_conformite', 0)
        
        content = "## 💡 Recommandations Principales\n\n"
        
        # Recommandations automatiques des statistiques
        recommandations_auto = stats.get('recommandations_auto', [])
        
        if recommandations_auto:
            content += "### Recommandations Automatiques\n\n"
            for rec in recommandations_auto:
                priorite_emoji = {'HAUTE': '🔴', 'MOYENNE': '🟡', 'BASSE': '🟢'}.get(rec['priorite'], '📌')
                content += f"**{priorite_emoji} {rec['type']}** - Priorité {rec['priorite']}\n"
                content += f"{rec['message']}\n\n"
        
        # Recommandations contextuelles
        content += "### Recommandations Spécifiques\n\n"
        
        if taux_conformite < 50:
            content += self._get_critical_recommendations()
        elif taux_conformite < 80:
            content += self._get_moderate_recommendations()
        else:
            content += self._get_maintenance_recommendations()
        
        return content
    
    def _get_critical_recommendations(self):
        return """#### 🚨 Situation Critique - Actions Immédiates

1. **Audit de code prioritaire**
   - Identifier les 5-10 fichiers les plus volumineux
   - Analyser leur complexité et responsabilités
   - Planifier leur décomposition

2. **Mise en place de garde-fous**
   - Intégrer des vérifications dans la CI/CD
   - Bloquer les commits dépassant la limite
   - Former l'équipe aux bonnes pratiques

3. **Refactoring progressif**
   - Décomposer les fichiers critiques
   - Appliquer le principe de responsabilité unique
   - Créer des modules cohérents

"""
    
    def _get_moderate_recommendations(self):
        return """#### ⚠️ Amélioration Nécessaire - Plan d'Action

1. **Refactoring ciblé**
   - Prioriser les fichiers non conformes les plus utilisés
   - Extraire des fonctions et classes cohérentes
   - Améliorer la modularité

2. **Prévention**
   - Sensibiliser l'équipe aux limites de taille
   - Réviser le processus de code review
   - Documenter les standards de codage

3. **Monitoring continu**
   - Suivre l'évolution des métriques
   - Alerter sur les régressions
   - Célébrer les améliorations

"""
    
    def _get_maintenance_recommendations(self):
        return """#### ✅ Maintenir l'Excellence - Amélioration Continue

1. **Surveillance proactive**
   - Monitor les nouvelles modifications
   - Prévenir les régressions
   - Maintenir les standards

2. **Optimisation fine**
   - Identifier les opportunités d'amélioration
   - Simplifier le code existant
   - Améliorer la lisibilité

3. **Partage de connaissances**
   - Documenter les bonnes pratiques
   - Former les nouveaux développeurs
   - Promouvoir la culture qualité

"""
    
    def _generate_action_items(self, stats):
        conformite = stats.get('statistiques_conformite', {})
        non_conformes = conformite.get('fichiers_non_conformes', 0)
        
        content = "## 📋 Plan d'Action\n\n"
        
        content += "### Actions Immédiates (0-2 semaines)\n\n"
        
        if non_conformes > 0:
            content += f"- [ ] Auditer les {min(non_conformes, 5)} fichiers les plus volumineux\n"
            content += "- [ ] Identifier les causes racines de la non-conformité\n"
            content += "- [ ] Créer un backlog de refactoring priorisé\n"
        
        content += "- [ ] Intégrer cette analyse dans le processus de CI/CD\n"
        content += "- [ ] Sensibiliser l'équipe aux résultats\n\n"
        
        content += "### Actions Moyen Terme (2-8 semaines)\n\n"
        content += "- [ ] Implémenter les corrections prioritaires\n"
        content += "- [ ] Mettre à jour la documentation de codage\n"
        content += "- [ ] Former l'équipe aux bonnes pratiques\n"
        content += "- [ ] Établir un processus de monitoring continu\n\n"
        
        content += "### Actions Long Terme (2+ mois)\n\n"
        content += "- [ ] Réviser et optimiser l'architecture globale\n"
        content += "- [ ] Automatiser les vérifications de qualité\n"
        content += "- [ ] Établir des métriques de qualité continues\n"
        content += "- [ ] Cultiver une culture de qualité dans l'équipe\n\n"
        
        return content
    
    def _generate_metrics_section(self, stats):
        base = stats.get('statistiques_base', {})
        
        content = "## 📊 Métriques Techniques\n\n"
        content += "### Statistiques Descriptives\n\n"
        content += f"- **Total fichiers :** {base.get('total_fichiers', 0)}\n"
        content += f"- **Total lignes :** {base.get('total_lignes', 0):,}\n"
        content += f"- **Moyenne :** {base.get('moyenne_lignes', 0):.1f} lignes/fichier\n"
        content += f"- **Médiane :** {base.get('mediane_lignes', 0):.1f} lignes/fichier\n"
        content += f"- **Écart-type :** {base.get('ecart_type', 0):.1f}\n"
        content += f"- **Min/Max :** {base.get('min_lignes', 0):.0f} / {base.get('max_lignes', 0):.0f} lignes\n\n"
        
        if 'percentiles' in stats:
            percentiles = stats['percentiles']
            content += "### Percentiles\n\n"
            for p, value in percentiles.items():
                content += f"- **{p.upper()} :** {value:.1f} lignes\n"
            content += "\n"
        
        return content
    
    def _generate_code_examples(self):
        return """## 💻 Exemples de Bonnes Pratiques

### Décomposition d'une Fonction Trop Longue

**❌ Avant (trop long)**
```python
def process_data(data):
    # 50+ lignes de traitement complexe
    # Validation, transformation, sauvegarde, logging...
    pass
```

**✅ Après (modularisé)**
```python
def process_data(data):
    validated_data = validate_data(data)
    transformed_data = transform_data(validated_data)
    result = save_data(transformed_data)
    log_processing_result(result)
    return result

def validate_data(data):
    # Logique de validation spécifique
    pass

def transform_data(data):
    # Logique de transformation spécifique
    pass
```

### Extraction de Classe

**❌ Avant (classe trop large)**
```python
class DataProcessor:
    # 200+ lignes gérant validation, transformation, 
    # sauvegarde, logging, configuration, etc.
    pass
```

**✅ Après (responsabilités séparées)**
```python
class DataValidator:
    # Responsabilité unique : validation
    pass

class DataTransformer:
    # Responsabilité unique : transformation
    pass

class DataProcessor:
    # Orchestration des composants
    def __init__(self):
        self.validator = DataValidator()
        self.transformer = DataTransformer()
```

"""
    
    def _generate_conclusion(self, stats):
        conformite = stats.get('statistiques_conformite', {})
        taux_conformite = conformite.get('taux_conformite', 0)
        
        content = "## 🎯 Conclusion\n\n"
        
        if taux_conformite >= 95:
            content += "🏆 **Excellence atteinte !** Votre base de code respecte remarquablement les standards de taille. "
            content += "Continuez sur cette voie en maintenant la vigilance sur les nouveaux développements.\n\n"
        elif taux_conformite >= 80:
            content += "👍 **Bon niveau de qualité.** Votre base de code respecte globalement les standards. "
            content += "Quelques ajustements ciblés permettront d'atteindre l'excellence.\n\n"
        else:
            content += "⚠️ **Opportunités d'amélioration significatives.** Un plan d'action structuré "
            content += "permettra d'améliorer substantiellement la maintenabilité de votre code.\n\n"
        
        content += "### Prochaines Étapes\n\n"
        content += "1. **Prioriser** les actions selon l'impact et la faisabilité\n"
        content += "2. **Planifier** les interventions dans les sprints à venir\n"
        content += "3. **Mesurer** les progrès régulièrement\n"
        content += "4. **Ajuster** la stratégie selon les résultats\n\n"
        
        content += "---\n"
        content += f"*Rapport généré automatiquement le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}*  \n"
        content += "*Par l'Ouvrier Conseiller du système de Gouvernance AGI*"
        
        return content
    
    def _write_empty_recommendations(self):
        contenu_vide = f"""# 📊 Recommandations - Gouvernance des Lignes de Code

**Date de génération :** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ⚠️ Aucune Donnée Disponible

Aucune statistique n'est disponible pour générer des recommandations.

### Actions Suggérées

1. Vérifier que l'analyse des fichiers a bien eu lieu
2. Contrôler la disponibilité des artefacts d'entrée
3. Relancer le processus d'analyse si nécessaire

---
*Rapport généré automatiquement par l'Ouvrier Conseiller*
"""
        self._write_markdown_file(contenu_vide)
    
    def _write_markdown_file(self, contenu):
        Path(self.args.sortie).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.args.sortie, 'w', encoding='utf-8') as f:
            f.write(contenu)
        
        print(f"💾 Recommandations sauvegardées : {self.args.sortie}")
        
        # Statistiques du fichier généré
        lignes = contenu.count('\n') + 1
        mots = len(contenu.split())
        caracteres = len(contenu)
        
        print(f"📄 Document généré : {lignes} lignes, {mots} mots, {caracteres} caractères")


if __name__ == "__main__":
    conseiller = ConseillerLignes()
    conseiller.run()
