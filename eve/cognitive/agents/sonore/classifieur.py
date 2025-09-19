# -*- coding: utf-8 -*-
"""
Capteur Sonore - Enfant : Classifieur de Sons (YAMNet)
"""
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
import io
import librosa

try:
    from . import parametres
except ImportError:
    import parametres

class ClassifieurSonore:
    """Utilise le modèle YAMNet pour classifier des sons."""

    def __init__(self):
        self.model = None
        self.class_names = []
        self.charger_modele()

    def charger_modele(self):
        """Charge le modèle YAMNet depuis TensorFlow Hub et les noms des classes."""
        try:
            print("[Classifieur] Chargement du modèle YAMNet depuis TensorFlow Hub...")
            self.model = hub.load('https://tfhub.dev/google/yamnet/1')
            print("[Classifieur] Modèle chargé avec succès.")

            # On charge aussi le fichier qui fait correspondre les numéros de classe aux noms
            self.class_names = self._charger_noms_classes()
            print("[Classifieur] Noms des 521 classes chargés.")

        except Exception as e:
            print(f"[Erreur Classifieur] Impossible de charger le modèle YAMNet. Vérifiez votre connexion internet. Erreur: {e}")

    def _charger_noms_classes(self):
        """Charge les noms des classes depuis le modèle."""
        class_map_path = self.model.class_map_path().numpy()
        with tf.io.gfile.GFile(class_map_path) as csvfile:
            reader = csv.reader(csvfile)
            # On ignore la première ligne (l'en-tête)
            next(reader)
            # On ne garde que les noms de classe (colonne 'displayName')
            return [row[2] for row in reader]

    def preparer_audio(self, waveform: np.ndarray):
        """Prépare l'onde sonore pour YAMNet (mono, 16kHz)."""
        waveform = waveform.astype(np.float32)
        # YAMNet attend un taux de 16000 Hz. On ré-échantillonne si nécessaire.
        if parametres.SAMPLE_RATE != 16000:
            waveform = librosa.resample(waveform, orig_sr=parametres.SAMPLE_RATE, target_sr=16000)
        return waveform

    def predire(self, waveform: np.ndarray, top_n=3):
        """
        Prédit la classe d'un son à partir de son onde.
        :param waveform: Les données audio brutes.
        :param top_n: Le nombre de meilleures prédictions à retourner.
        :return: Une liste de tuples (nom_de_classe, score_de_confiance).
        """
        if self.model is None or not self.class_names:
            return [("Modèle non chargé", 0.0)]

        try:
            # On prépare le son pour le modèle
            audio_prepare = self.preparer_audio(waveform)

            # Le modèle retourne des scores pour les 521 classes
            scores, embeddings, spectrogram = self.model(audio_prepare)

            # On prend la moyenne des scores sur la durée du son
            prediction_moyenne = np.mean(scores, axis=0)

            # On trouve les N classes avec les meilleurs scores
            top_n_indices = np.argsort(prediction_moyenne)[-top_n:][::-1]

            resultats = []
            for i in top_n_indices:
                nom_classe = self.class_names[i]
                score = prediction_moyenne[i]
                resultats.append((nom_classe, float(score)))

            return resultats

        except Exception as e:
            print(f"[Erreur Classifieur] Erreur lors de la prédiction : {e}")
            return [("Erreur d'analyse", 0.0)]


# --- Bloc de test ---
if __name__ == '__main__':
    from capture import CaptureAudio
    import time

    print("--- Test du classifieur de sons avec micro en direct ---")
    classifieur = ClassifieurSonore()

    if classifieur.model:
        capture = CaptureAudio()
        if capture.start():
            print("\nParlez, toussez, faites du bruit pendant 5 secondes...")
            time.sleep(5)
            capture.stop()

            # On récupère tout le son capturé
            audio_complet = []
            while not capture.audio_queue.empty():
                audio_complet.append(capture.audio_queue.get())

            if audio_complet:
                # On concatène tous les blocs en un seul signal
                signal_final = np.concatenate(audio_complet, axis=0).flatten()

                print("\nAnalyse du son capturé...")
                predictions = classifieur.predire(signal_final)

                print("\n--- L'IA a entendu : ---")
                for nom, score in predictions:
                    print(f"- {nom} (Confiance: {score:.2%})")
                print("\n--- Test du classifieur terminé. ---")
            else:
                print("Aucun son n'a été capturé.")
    else:
        print("\nLe test ne peut pas continuer car le modèle n'a pas pu être chargé.")
