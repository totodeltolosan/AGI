# -*- coding: utf-8 -*-
# core/moteur.py (v7.2 - Focalisé sur le Dynamique)
# Rôle : Le "Bloc Moteur" d'Alma. Contient et exécute les boucles de
# surveillance intensive (PC et Son). Ne se préoccupe que de la performance.

import time
import threading
import queue
import numpy as np
from datetime import datetime

try:
    from sonore import capture, classifieur, extracteur
    import activite
    import brain
    import historique
except ImportError:
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from sonore import capture, classifieur, extracteur
    import activite, brain, historique

class MoteurAlma:
    def __init__(self, ui_queue, stop_event):
        self.ui_queue = ui_queue
        self.stop_event = stop_event
        self.audio_queue_interne = queue.Queue()
        self.capture_audio = capture.CaptureAudio()
        self.capture_audio.ajouter_auditeur(self.audio_queue_interne)
        self.classifieur_sonore = classifieur.ClassifieurSonore()
        self.cerveau_pc = brain.CerveauAlma()
        self.dernier_son_detecte = "Silence"
        self.lock_son = threading.Lock()

    def executer_boucles_surveillance(self):
        print("[Moteur] Démarrage des boucles de surveillance...")
        thread_pc = threading.Thread(target=self._boucle_surveillance_pc, daemon=True)
        thread_son = threading.Thread(target=self._boucle_surveillance_sonore, daemon=True)
        thread_pc.start()
        thread_son.start()
        self.stop_event.wait()
        thread_pc.join()
        thread_son.join()
        print("[Moteur] Boucles de surveillance terminées.")

    def _boucle_surveillance_pc(self):
        """
        Thread dédié à la surveillance des métriques système dynamiques.
        """
        # --- DÉBUT DE LA CORRECTION ---
        # On ne collecte plus les données statiques ici pour un démarrage rapide.
        # Le cerveau n'en a pas besoin pour son analyse en temps réel.
        print("[Moteur-PC] Surveillance démarrée.")
        while not self.stop_event.is_set():
            timestamp = datetime.now().isoformat()

            # On collecte uniquement les données dynamiques, qui sont rapides à obtenir.
            donnees_dynamiques = activite.collecter_donnees_dynamiques()

            with self.lock_son:
                donnees_dynamiques['environnement_sonore'] = self.dernier_son_detecte

            # Le cerveau reçoit directement les données complètes pour l'analyse.
            diagnostics = self.cerveau_pc.analyser(donnees_dynamiques)
            # --- FIN DE LA CORRECTION ---

            if diagnostics:
                ticket = {
                    "type": "PC",
                    "timestamp": timestamp,
                    "diagnostics": diagnostics,
                    "donnees_brutes": donnees_dynamiques
                }
                self.ui_queue.put(ticket)

            self.stop_event.wait(timeout=5)
        print("[Moteur-PC] Surveillance terminée.")

    def _boucle_surveillance_sonore(self):
        """
        Thread dédié à la surveillance de l'environnement sonore.
        """
        if not self.classifieur_sonore.model: return
        if not self.capture_audio.start(): return

        print("[Moteur-Son] Analyse sonore démarrée.")
        tampon_audio = []
        while not self.stop_event.is_set():
            try:
                donnees_audio = self.audio_queue_interne.get(timeout=1)
                tampon_audio.append(donnees_audio)

                if len(tampon_audio) >= 43:
                    signal = np.concatenate(tampon_audio, axis=0).flatten()
                    tampon_audio = []
                    empreinte = extracteur.extraire_mfcc(signal)
                    if empreinte is None: continue
                    predictions = self.classifieur_sonore.predire(signal)

                    if predictions and predictions[0][1] > 0.4 and "Silence" not in predictions[0][0]:
                        with self.lock_son:
                            self.dernier_son_detecte = predictions[0][0]
                        ticket = {
                            "type": "SON",
                            "timestamp": datetime.now().isoformat(),
                            "predictions": predictions,
                            "empreinte_mfcc": empreinte.tolist()
                        }
                        self.ui_queue.put(ticket)
            except queue.Empty:
                with self.lock_son:
                    self.dernier_son_detecte = "Silence"

        if self.capture_audio.is_running:
            self.capture_audio.stop()
        print("[Moteur-Son] Analyse sonore arrêtée.")
