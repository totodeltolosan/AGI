 Rapport de Spécification Finale du Script generate_diagram.py
Version : "Artisan-Valideur"
1. Synthèse et Mission Générale
Ce document définit les spécifications complètes du script Python generate_diagram.py. Le script a pour mission principale d'analyser le document d'architecture Systemeneuronal.md, d'en extraire l'intégralité de la structure des 365 workflows répartis sur 5 "Faces" cognitives, et de générer un unique et gigantesque diagramme PlantUML qui représente cette architecture de manière visuellement riche et informative.
Le comportement du script est défini par le concept de "l'Artisan-Valideur" : il travaillera de manière lente, méthodique et totalement transparente, en validant son propre travail pour garantir un résultat final 100% fonctionnel.
Catégorie	Décision Clé
Objectif Final	Un unique diagramme .puml complet et valide.
Source de Données	Le fichier /home/toni/Documents/Projet AGI/.github/workflows/Systemeneuronal.md.
Comportement	Verbeux, contrôlé, avec validation et journalisation.
Configuration	Aucune configuration externe, tout est défini dans le script.
Estimation Finale	Environ 1200 lignes de code Python.
2. Spécifications d'Analyse et de Données
Le cœur du script réside dans sa capacité à comprendre le document source.
Méthode d'Identification des Workflows : Le script utilisera une méthode de capture par section combinée à une expression régulière flexible. Il découpera d'abord le document en chapitres correspondant à chaque "Face", puis appliquera une regex à l'intérieur de chaque section pour identifier les noms de workflows avec une grande précision.
Analyse des Flux de Dépendances : Pour dessiner les flèches entre les workflows, le script utilisera une triple source d'information :
Analyse Hiérarchique : Déduction des flux logiques basés sur la hiérarchie des niveaux (N3 appelle N4, etc.).
Analyse Textuelle : Lecture du contenu descriptif du .md pour trouver les mentions explicites d'autres workflows.
Fichier Externe : Lecture d'un fichier flux.csv pour permettre l'ajout de relations manuelles non décrites dans le document.
Gestion des Changements : Le script intègre un mécanisme de mise en cache. Il sauvegardera une empreinte (hash) de la dernière analyse réussie. Si le fichier Systemeneuronal.md est modifié entre deux exécutions, le script le détectera et générera un rapport de différences clair, listant les workflows ajoutés et supprimés avant de procéder à la nouvelle génération.
3. Spécifications de Génération Visuelle
Le résultat final est un diagramme unique, dont l'apparence est précisément définie.
Mise en Page Globale : Le diagramme sera structuré autour de 5 grands conteneurs centraux, un pour chaque Face cognitive. L'ensemble sera entouré d'un cadre visuel thématique évoquant un patron de dodécaèdre pour l'esthétique et le contexte.
Organisation Interne : À l'intérieur de chaque conteneur "Face", les workflows seront organisés selon une triple hiérarchie stricte :
Regroupement par Niveau Hiérarchique (N0, N1, N2...).
Sous-regroupement par Division Fonctionnelle (Division Lignes, Travailleurs...).
Le script tentera de regrouper visuellement les miroirs d'un même workflow de base.
Apparence des Workflows : Chaque workflow sera représenté par une boîte contenant un maximum d'informations visuelles :
Un stéréotype textuel (<<Action>>, <<Neuronal>>).
Une couleur de fond spécifique à sa Face.
Une icône représentative de son rôle.
Apparence des Flux : Les flèches de dépendances seront stylisées. En fonction du type de relation déduite ("appelle", "valide"), elles auront un style (continu, pointillé) et une étiquette textuelle.
Thème Visuel : Le script appliquera un thème moderne intégré (!theme vibrant) et ajoutera des couleurs de bordure spécifiques à chaque Division pour améliorer encore la lisibilité.
4. Spécifications Comportementales et Opérationnelles
Le script est conçu pour être fiable et transparent.
Gestion du Processus : L'exécution sera lente, contrôlée et très verbeuse. L'utilisateur verra chaque étape s'afficher dans le terminal, accompagnée d'une barre de progression pour les tâches longues. Des pauses délibérées seront observées.
Validation de Syntaxe : Après l'assemblage complet du fichier .puml, le script lancera une phase de validation automatique en utilisant plantuml.jar -checkonly. Le processus ne sera considéré comme un succès que si la syntaxe est 100% valide.
Gestion des Fichiers de Sortie :
Le fichier .puml final sera généré dans un dossier unique et horodaté pour chaque exécution, afin de ne jamais écraser un résultat précédent.
Un unique fichier generation.log sera maintenu et mis à jour à chaque exécution (mode cumulatif).
Gestion des Erreurs : Le script effectuera une validation des prérequis en amont (présence du fichier source, de plantuml.jar, etc.). Tout au long de son exécution, il interceptera les erreurs techniques pour les présenter à l'utilisateur sous forme de messages clairs et en français, tout en enregistrant les détails techniques complets dans le fichier de log.
Documentation et Interaction :
Le fichier generation.log sera rédigé de manière pédagogique, pour servir de rapport d'exécution détaillé et compréhensible.
L'interaction avec l'utilisateur sera strictement informative et verbeuse, sans questions ou menus interactifs, pour une exécution prévisible.
Ce rapport constitue le cahier des charges final et complet. La prochaine étape est la rédaction du code Python qui implémentera rigoureusement chacune de ces spécifications.
