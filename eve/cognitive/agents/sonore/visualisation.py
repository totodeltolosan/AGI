# -*- coding: utf-8 -*-
"""Capteur Sonore - Enfant : Visualisation Audio (v1.3 - Import Définitif)"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import queue

# CORRECTION DÉFINITIVE : Bloc d'import intelligent
try:
    from . import parametres
    from .capture import CaptureAudio
except ImportError:
    import parametres
    from capture import CaptureAudio

# --- LE RESTE DU FICHIER EST INCHANGÉ ---
fig, ax = plt.subplots(); line, = ax.plot(np.zeros(parametres.CHUNK_SIZE))
ax.set_ylim(-0.5, 0.5); ax.set_xlim(0, parametres.CHUNK_SIZE)
ax.set_title("Visualisation du Son en Temps Réel")

def visualiser_depuis_queue(audio_queue):
    def update_plot(frame):
        data = None
        while not audio_queue.empty(): data = audio_queue.get_nowait()
        if data is not None: line.set_ydata(data)
        return line,
    ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=30)
    plt.show()

if __name__ == '__main__':
    import threading
    print("--- Test de la visualisation en temps réel ---")
    q = queue.Queue(); cap = CaptureAudio(); cap.audio_queue = q
    capture_thread = threading.Thread(target=cap.start, daemon=True)
    capture_thread.start()
    visualiser_depuis_queue(q)
    cap.stop()
    print("--- Test de visualisation terminé. ---")
