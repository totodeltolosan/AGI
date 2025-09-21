# -*- coding: utf-8 -*-
# core/orchestrateur.py
# Rôle : Le "Pilote" d'Alma. Point d'entrée pour démarrer et arrêter
# les services de surveillance. Il construit le moteur et le gère.

import queue
import threading
from .moteur import MoteurAlma # Import relatif depuis le même paquet 'core'

class Orchestrateur:
    """
    Classe de haut niveau qui gère le cycle de vie du moteur de surveillance.
    C'est le seul objet que l'interface (UI) doit connaître pour piloter Alma.
    """
    def __init__(self):
        """
        Initialise l'orchestrateur, le moteur et les canaux de communication.
        """
        print("[Orchestrateur] Initialisation...")
        # Crée la file d'attente pour la communication Moteur -> Interface
        self.ui_queue = queue.Queue()

        # Crée l'événement pour signaler l'arrêt aux threads
        self.stop_event = threading.Event()

        # Construit le moteur en lui fournissant ses dépendances
        self.moteur = MoteurAlma(self.ui_queue, self.stop_event)

        self.thread_moteur = None
        print("[Orchestrateur] Prêt.")

    def demarrer_surveillance(self):
        """
        Démarre le moteur Alma dans un thread dédié pour ne pas bloquer l'interface.
        """
        if self.thread_moteur and self.thread_moteur.is_alive():
            print("[Orchestrateur] Le moteur tourne déjà.")
            return

        print("[Orchestrateur] Ordre de démarrage envoyé au moteur.")
        # On s'assure que le signal d'arrêt est bien baissé
        self.stop_event.clear()

        # Le moteur est démarré dans son propre thread pour être non-bloquant
        self.thread_moteur = threading.Thread(
            target=self.moteur.executer_boucles_surveillance,
            daemon=True
        )
        self.thread_moteur.start()

    def arreter_surveillance(self):
        """
        Envoie le signal d'arrêt au moteur et attend que son thread se termine.
        """
        if not self.thread_moteur or not self.thread_moteur.is_alive():
            print("[Orchestrateur] Le moteur est déjà à l'arrêt.")
            return

        print("[Orchestrateur] Ordre d'arrêt envoyé au moteur.")
        self.stop_event.set()

        # On attend que le thread du moteur se termine proprement
        self.thread_moteur.join(timeout=5)

        if self.thread_moteur.is_alive():
            print("[Orchestrateur] AVERTISSEMENT: Le thread moteur n'a pas pu s'arrêter.")
        else:
            print("[Orchestrateur] Moteur arrêté proprement.")
        self.thread_moteur = None
