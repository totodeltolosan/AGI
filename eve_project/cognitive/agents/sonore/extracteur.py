# -*- coding: utf-8 -*-
"""Capteur Sonore - Enfant : Extracteur de Caractéristiques (v1.2)"""

import librosa
import numpy as np

try:
    from . import parametres
except ImportError:
    import parametres

def extraire_mfcc(signal_audio: np.ndarray):
    """
    Extrait les caractéristiques MFCC d'un signal audio.
    """
    try:
        signal_audio = signal_audio.astype(np.float32).flatten()

        # CORRECTION : On spécifie la taille de la fenêtre d'analyse (n_fft)
        # pour qu'elle corresponde à notre taille de bloc (CHUNK_SIZE).
        mfccs = librosa.feature.mfcc(
            y=signal_audio,
            sr=parametres.SAMPLE_RATE,
            n_mfcc=40,
            n_fft=parametres.CHUNK_SIZE
        )

        mfccs_scaled = np.mean(mfccs.T, axis=0)
        return mfccs_scaled
    except Exception as e:
        print(f"[Erreur Extracteur] {e}")
        return None

# --- Bloc de test (inchangé) ---
if __name__ == '__main__':
    print("--- Test de l'extracteur de caractéristiques ---")
    sr = parametres.SAMPLE_RATE; duree = 1; frequence = 440
    temps = np.linspace(0., duree, int(sr * duree))
    amplitude = np.iinfo(np.int16).max * 0.5
    signal_test = amplitude * np.sin(2. * np.pi * frequence * temps)
    print("Extraction des MFCC d'un son de test (La 440 Hz)...")
    empreinte_sonore = extraire_mfcc(signal_test)
    if empreinte_sonore is not None:
        print(f"Extraction réussie ! Empreinte obtenue (forme) : {empreinte_sonore.shape}")
        print("--- Test d'extraction réussi ! ---")
    else:
        print("--- Test d'extraction échoué. ---")
