# -*- coding: utf-8 -*-
"""
Capteur Sonore - Enfant : Capture Audio (v2.4 - Robuste et Finalisé)
"""
import sounddevice as sd
import numpy as np
import queue
import time

try:
    from . import parametres
except ImportError:
    import parametres

class CaptureAudio:
    """Gère le flux audio du microphone de manière robuste et configurable."""

    def __init__(self, device_id=None):
        self.device = device_id
        self.gain = parametres.AMPLIFICATION_LOGICIELLE
        self.listeners = []
        self.stream = None
        self.is_running = False

    def ajouter_auditeur(self, audio_queue: queue.Queue):
        if audio_queue not in self.listeners:
            self.listeners.append(audio_queue)

    def _callback(self, indata, frames, time, status):
        if status: print(f"[Avertissement Capture] {status}")
        donnees_traitees = indata * self.gain
        for q in self.listeners: q.put(donnees_traitees.copy())

    def set_gain(self, nouveau_gain: float):
        self.gain = nouveau_gain

    def start(self):
        if self.is_running: return True
        try:
            # CORRECTION : On détermine le périphérique par défaut de manière plus sûre
            if self.device is None:
                self.device = sd.default.device['input']

            device_info = sd.query_devices(self.device)
            print(f"[Capture] Démarrage du flux pour le micro : '{device_info['name']}' (ID: {self.device})")

            self.stream = sd.InputStream(
                device=self.device,
                samplerate=parametres.SAMPLE_RATE,
                channels=parametres.CHANNELS,
                blocksize=parametres.CHUNK_SIZE,
                callback=self._callback
            )
            self.stream.start()
            self.is_running = True
            return True
        except Exception as e:
            print(f"[Erreur Capture] Démarrage impossible: {e}")
            return False

    def stop(self):
        if self.stream and self.is_running:
            self.stream.stop(); self.stream.close()
            self.is_running = False; self.stream = None
            print("[Capture] Microphone arrêté.")

    @staticmethod
    def lister_peripheriques_entree():
        try:
            return [(i, d['name']) for i, d in enumerate(sd.query_devices()) if d['max_input_channels'] > 0]
        except Exception as e:
            print(f"Erreur lors du listage des périphériques : {e}")
            return []

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du module de capture audio v2.4 ---")
    devices = CaptureAudio.lister_peripheriques_entree()
    if devices:
        for index, name in devices: print(f"  ID {index}: {name}")

    capture = CaptureAudio()
    test_queue = queue.Queue()
    capture.ajouter_auditeur(test_queue)

    if capture.start():
        print("\nLa capture va durer 3 secondes...")
        time.sleep(3)
        capture.stop()
        print(f"\n{test_queue.qsize()} blocs audio ont été capturés.")
        print("--- Test de capture réussi ! ---")
