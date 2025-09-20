# -*- coding: utf-8 -*-
"""
inspecteur_cerveau.py

Un outil de diagnostic pour charger le cerveau d'Alma et inspecter
sa structure et ses connaissances.
"""
import joblib
import os

MODEL_FILE = 'alma_model.joblib'

def inspecter_cerveau():
    """TODO: Add docstring."""
    print("="*60)
    print("===== INSPECTION DU CERVEAU D'ALMA =====")
    print("="*60)

    if not os.path.exists(MODEL_FILE):
        print(f"[ERREUR] Fichier '{MODEL_FILE}' introuvable. Avez-vous lancé un entraînement ?")
        return

    try:
        print(f"\n[Action] Chargement des artefacts depuis '{MODEL_FILE}'...")
        artefacts = joblib.load(MODEL_FILE)
        print("[Succès] Cerveau chargé.")
    except Exception as e:
        print(f"[ERREUR] Impossible de charger le cerveau : {e}")
        return

    # --- Inspection du Pipeline ---
    print("\n--- 1. Analyse du Pipeline d'IA ---")
    if 'pipeline' in artefacts:
        pipeline = artefacts['pipeline']
        print(f"Type de modèle final : {type(pipeline.named_steps.get('xgbclassifier')).__name__}")
        print("Étapes du pipeline :")
        for name, step in pipeline.named_steps.items():
            print(f"  - {name}: {type(step).__name__}")

        print("\nParamètres du modèle optimisé (XGBoost) :")
        print(pipeline.named_steps.get('xgbclassifier').get_params())
    else:
        print("[Alerte] Aucun 'pipeline' trouvé dans les artefacts.")

    # --- Inspection de l'Encodeur ---
    print("\n--- 2. Analyse de l'Encodeur de Causes ---")
    if 'label_encoder' in artefacts:
        label_encoder = artefacts['label_encoder']
        print("Le cerveau a appris à reconnaître les causes suivantes :")
        for i, classe in enumerate(label_encoder.classes_):
            print(f"  - '{classe}' (encodé en -> {i})")
    else:
        print("[Alerte] Aucun 'label_encoder' trouvé dans les artefacts.")

    print("\n" + "="*60)
    print("===== FIN DE L'INSPECTION =====")
    print("="*60)

if __name__ == "__main__":
    inspecter_cerveau()