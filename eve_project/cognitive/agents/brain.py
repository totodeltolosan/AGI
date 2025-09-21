# -*- coding: utf-8 -*-
# brain.py (v7.3 - Robuste et Contextuel)
# Gère la présence, les données manquantes et la structure des données.
import os
import joblib
import pandas as pd
import collections
import statistics
import json

class CerveauAlma:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self):
        self.pipeline_ia = None
        self.label_encoder = None
        self.charger_modele_ia()
        self.TAILLE_MEMOIRE = 50
        self.SEUIL_APPRENTISSAGE = 10
        self.FICHIER_BASELINE = 'baseline_alma.json'
        self.memoire_cpu = collections.deque(maxlen=self.TAILLE_MEMOIRE)
        self.baseline = {"calculee": False, "cpu": {}}
        self._charger_baseline()
            """TODO: Add docstring."""

    def charger_modele_ia(self):
        model_file = 'alma_model.joblib'
        if os.path.exists(model_file):
            try:
                artefacts = joblib.load(model_file)
                self.pipeline_ia = artefacts['pipeline']
                self.label_encoder = artefacts['label_encoder']
                print("[Brain] Cerveau IA (XGBoost + Encodeur) chargé avec succès.")
            except Exception as e:
                print(f"[Brain] Erreur critique lors du chargement du cerveau : {e}")
        else:
            print("[Brain] Aucun cerveau pré-entraîné (alma_model.joblib) trouvé.")

    def _preparer_donnees_pour_ia(self, donnees_brutes: dict) -> pd.DataFrame:
        """Aplatit et nettoie les données brutes pour les rendre compatibles avec le modèle."""
        donnees_aplati = {
            'cpu_charge': donnees_brutes.get('cpu_charge_globale', {}).get('charge_cpu_pourcentage', 0.0),
            'ram_usage_pourcentage': donnees_brutes.get('memoire_ram', {}).get('usage_pourcentage', 0.0),
            'top_processus_nom': donnees_brutes.get('processus_top', {}).get('details', [{}])[0].get('name', 'INCONNU'),
            'environnement_sonore': donnees_brutes.get('environnement_sonore', 'INCONNU')
        }

        # S'assure que toutes les colonnes attendues sont présentes
        donnees_finales = {}
        colonnes_attendues = self.pipeline_ia.feature_names_in_
        for col in colonnes_attendues:
            donnees_finales[col] = donnees_aplati.get(col, 'INCONNU')

    """TODO: Add docstring."""
        return pd.DataFrame([donnees_finales])

    def analyser(self, donnees_completes: dict, presence_on: bool = True):
        diagnostics = []
        if not self.baseline["calculee"]:
            charge_cpu = donnees_completes.get('cpu_charge_globale', {}).get('charge_cpu_pourcentage', 0)
            self.memoire_cpu.append(charge_cpu)
            if len(self.memoire_cpu) >= self.SEUIL_APPRENTISSAGE:
                self._calculer_et_sauvegarder_baseline()
            message = f"Phase d'apprentissage ({len(self.memoire_cpu)}/{self.SEUIL_APPRENTISSAGE})"
            return [f"ROUTINE : {message}"]

        charge_cpu = donnees_completes.get('cpu_charge_globale', {}).get('charge_cpu_pourcentage', 0)
        seuil_anomalie_cpu = self.baseline["cpu"]["moyenne"] + 3 * self.baseline["cpu"]["ecart_type"]
        seuil_declenchement = 20 if presence_on else 15

        if charge_cpu > seuil_anomalie_cpu and charge_cpu > seuil_declenchement:
            diag_base = f"ANOMALIE CPU{' (Mode Absence)' if not presence_on else ''} : Charge de {charge_cpu:.1f}% détectée."
            diagnostics.append(diag_base)

            if self.pipeline_ia and self.label_encoder:
                try:
                    df_temps_reel = self._preparer_donnees_pour_ia(donnees_completes)

                    probabilities = self.pipeline_ia.predict_proba(df_temps_reel)[0]
                    max_proba_index = probabilities.argmax()
                    max_proba = probabilities[max_proba_index]
                    seuil_confiance = 0.6 if presence_on else 0.4

                    if max_proba > seuil_confiance:
                        cause_predite = self.label_encoder.inverse_transform([max_proba_index])[0]
                        diagnostics.append(f"PRÉDICTION IA : Cause probable -> {cause_predite} (Confiance: {max_proba:.1%})")

                except Exception as e:
                    diagnostics.append(f"[AVERTISSEMENT] Erreur lors de l'inférence IA : {e}")

        if not diagnostics:
            """TODO: Add docstring."""
            return ["ROUTINE : État Nominal"]
        return diagnostics

    def _calculer_et_sauvegarder_baseline(self):
        self.baseline["cpu"]["moyenne"] = statistics.mean(self.memoire_cpu)
        self.baseline["cpu"]["ecart_type"] = statistics.stdev(self.memoire_cpu) if len(self.memoire_cpu) > 1 else 0
            """TODO: Add docstring."""
        self.baseline["calculee"] = True
        print("[Brain] Ligne de base PC calculée.")
        self._sauvegarder_baseline()

    def _sauvegarder_baseline(self):
        try:
            with open(self.FICHIER_BASELINE, 'w', encoding='utf-8') as f:
                """TODO: Add docstring."""
                json.dump(self.baseline, f, indent=4)
            print(f"[Brain] Ligne de base sauvegardée dans {self.FICHIER_BASELINE}.")
        except Exception as e:
            print(f"[Brain] Erreur lors de la sauvegarde de la baseline : {e}")

    def _charger_baseline(self):
        if os.path.exists(self.FICHIER_BASELINE):
            try:
                with open(self.FICHIER_BASELINE, 'r', encoding='utf-8') as f:
                    self.baseline = json.load(f)
                if self.baseline.get("calculee"):
                    print(f"[Brain] Ligne de base chargée depuis {self.FICHIER_BASELINE}.")
                else: self.baseline = {"calculee": False, "cpu": {}}
            except Exception as e:
                print(f"[Brain] Erreur lors du chargement de la baseline : {e}. Une nouvelle sera calculée.")
                self.baseline = {"calculee": False, "cpu": {}}