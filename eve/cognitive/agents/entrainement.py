# -*- coding: utf-8 -*-
"""
entrainement.py (v4.3 - Encodage de la Cible)

Le centre d'entraînement "Compétition" d'Alma.
Utilise XGBoost et gère correctement l'encodage des étiquettes textuelles.
"""

import pandas as pd
import joblib
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, LabelEncoder # On importe LabelEncoder
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# --- CONFIGURATION CENTRALE ---
CONFIG = {
    "fichier_historique": "historique_alma.csv",
    "fichier_modele": "alma_model.joblib",
    "fichier_rapport_visuel": "rapport_performance_cerveau.png",
    "features_souhaitees": ['cpu_charge', 'ram_usage_pourcentage', 'top_processus_nom', 'environnement_sonore'],
    "target": 'cause_reelle',
    "min_evenements_par_classe": 2,
    "test_size": 0.3
}

# --- Fonctions Utilitaires ---
def print_header(titre):
    print("\n" + "═"*70)
    print(f" {titre.upper()} ".center(70, "═"))
    print("═"*70)

def plot_confusion_matrix(y_true, y_pred, classes, filename):
    mat = confusion_matrix(y_true, y_pred, labels=classes)
    plt.figure(figsize=(12, 10))
    sns.heatmap(mat, annot=True, fmt='d', cmap='viridis',
                xticklabels=classes, yticklabels=classes)
    plt.title('Matrice de Confusion du Cerveau d\'Alma (XGBoost)', fontsize=16)
    plt.ylabel('Cause Réelle (votre feedback)', fontsize=12)
    plt.xlabel('Prédiction d\'Alma', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(filename)
    print(f"\n[Rapport] Matrice de confusion sauvegardée dans '{filename}'")

# --- Fonction Principale ---
def entrainer_nouveau_modele():
    print_header("Phase 1: Préparation des Données")
    try:
        df = pd.read_csv(CONFIG["fichier_historique"])
        print(f"[Info] Chargement de {len(df)} événements.")
    except FileNotFoundError:
        print(f"[Erreur] Fichier '{CONFIG['fichier_historique']}' introuvable. Arrêt.")
        return

    df_entrainement = df[df[CONFIG["target"]].notna() & (df[CONFIG["target"]] != 'NON_DEFINI')].copy()
    features_disponibles = [f for f in CONFIG["features_souhaitees"] if f in df_entrainement.columns]
    print(f"[Info] Features réellement disponibles et utilisées : {features_disponibles}")

    for feature in features_disponibles:
        if df_entrainement[feature].isnull().any():
             df_entrainement[feature] = df_entrainement[feature].fillna('INCONNU')

    class_counts = df_entrainement[CONFIG["target"]].value_counts()
    classes_minoritaires = class_counts[class_counts < CONFIG["min_evenements_par_classe"]].index
    if not classes_minoritaires.empty:
        print(f"[Alerte] Causes exclues (pas assez d'exemples): {list(classes_minoritaires)}")
        df_entrainement = df_entrainement[~df_entrainement[CONFIG["target"]].isin(classes_minoritaires)]

    if len(df_entrainement) < 10 or df_entrainement[CONFIG["target"]].nunique() < 2:
        print("[Erreur] Pas assez de données ou de classes différentes pour un entraînement. Arrêt.")
        return

    print(f"[Succès] {len(df_entrainement)} événements valides pour l'entraînement.")

    X = df_entrainement[features_disponibles]
    y_text = df_entrainement[CONFIG["target"]] # On garde les étiquettes textuelles pour les rapports

    # --- DÉBUT DE LA CORRECTION ---
    # On transforme les étiquettes textuelles (la cible y) en nombres
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_text)
    print(f"[Info] Encodage de {len(label_encoder.classes_)} causes : {list(label_encoder.classes_)}")
    # --- FIN DE LA CORRECTION ---

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=CONFIG["test_size"], random_state=42, stratify=y
    )

    print_header("Phase 2: Construction du Pipeline de Compétition (XGBoost)")

    colonnes_categorielles = [f for f in ['top_processus_nom', 'environnement_sonore'] if f in features_disponibles]
    print(f"[Info] Colonnes textuelles à encoder : {colonnes_categorielles}")

    preprocesseur = make_column_transformer(
        (OneHotEncoder(handle_unknown='ignore', sparse_output=False), colonnes_categorielles),
        remainder='passthrough'
    )

    # On retire 'use_label_encoder=False' qui est déprécié et inutile maintenant
    pipeline = make_pipeline(
        preprocesseur,
        xgb.XGBClassifier(objective='multi:softprob', eval_metric='mlogloss', random_state=42)
    )

    print_header("Phase 3: Optimisation Automatique (GridSearch)")

    param_grid = {
        'xgbclassifier__n_estimators': [100, 200],
        'xgbclassifier__max_depth': [3, 5, 7],
        'xgbclassifier__learning_rate': [0.05, 0.1]
    }

    grid_search = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, scoring='accuracy', verbose=2)

    print("[Action] Recherche des meilleurs hyperparamètres en cours... (peut prendre du temps)")
    start_time = time.time()
    grid_search.fit(X_train, y_train)
    end_time = time.time()

    print(f"\n[Succès] Optimisation terminée en {end_time - start_time:.2f} secondes.")
    print(f"[Info] Meilleurs paramètres trouvés: {grid_search.best_params_}")

    print_header("Phase 4: Évaluation du Cerveau Final")

    best_model = grid_search.best_estimator_
    predictions_encoded = best_model.predict(X_test)

    # --- DÉBUT DE LA CORRECTION ---
    # On re-transforme les prédictions numériques en texte pour les rapports
    predictions_text = label_encoder.inverse_transform(predictions_encoded)
    y_test_text = label_encoder.inverse_transform(y_test)
    class_names = label_encoder.classes_

    accuracy = accuracy_score(y_test_text, predictions_text)
    print(f"Précision du modèle final sur les données de test: {accuracy:.2%}")
    print("\nRapport de classification détaillé:")
    print(classification_report(y_test_text, predictions_text, labels=class_names, zero_division=0))

    plot_confusion_matrix(y_test_text, predictions_text, classes=class_names, filename=CONFIG["fichier_rapport_visuel"])
    # --- FIN DE LA CORRECTION ---

    print_header("Phase 5: Sauvegarde du Cerveau de Compétition")

    print("[Action] Ré-entraînement du modèle optimisé sur TOUTES les données...")
    final_model = grid_search.best_estimator_.fit(X, y)

    # On sauvegarde le modèle ET l'encodeur d'étiquettes ensemble
    artefacts_a_sauvegarder = {'pipeline': final_model, 'label_encoder': label_encoder}
    joblib.dump(artefacts_a_sauvegarder, CONFIG["fichier_modele"])
    print(f"[SUCCÈS] Le cerveau d'Alma (modèle + encodeur) a été mis à jour !")

if __name__ == "__main__":
    entrainer_nouveau_modele()
    input("\nAppuyez sur Entrée pour fermer cette fenêtre...")
