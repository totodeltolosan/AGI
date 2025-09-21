import customtkinter as ctk
import queue
import threading
import time
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)

# --- Configuration Globale de l'Interface (Directive 84) ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TableauBord:
    """
    Interface graphique complète avec communication bidirectionnelle.
    Implémente les Directives 19, 20, 23, 43, 55 et 84.
    """

    def __init__(self, root, q_ia_vers_gui, q_gui_vers_ia, config):
        """Initialise le tableau de bord avec communication bidirectionnelle."""
        self.root = root
        self.q_entree = q_ia_vers_gui  # Messages DE l'IA
        self.q_sortie = q_gui_vers_ia  # Commandes VERS l'IA
        self.config = config

        # État interne
        self.running = True
        self.donnees_apprentissage = deque(maxlen=1000)
        self.temps_apprentissage = deque(maxlen=1000)
        self.dernier_update = time.time()

        # Widgets interface
        self.progress_vie = None
        self.progress_faim = None
        self.label_mode = None
        self.text_strategie = None
        self.progress_emotions = {}
        self.fig = None
        self.ax = None
        self.canvas = None
        self.label_vitesse = None
        self.scale_vitesse = None
        self.var_inspection = ctk.BooleanVar()
        self.check_inspection = None

        # Configuration fenêtre principale
        self.root.title("Le Simulateur - Tableau de Bord")
        self.root.geometry("1400x800")
        self.root.protocol("WM_DELETE_WINDOW", self._fermer_interface)

        # Initialisation interface
        self.setup_interface()
        print("INFO: Interface tableau de bord initialisée")

    def setup_interface(self):
        """Construit l'intégralité de l'interface graphique."""
        self.root.grid_columnconfigure(1, weight=3)  # Vue principale
        self.root.grid_columnconfigure(0, weight=1)  # Panneau de stats
        self.root.grid_columnconfigure(2, weight=1)  # Panneau de contrôles
        self.root.grid_rowconfigure(0, weight=1)

        self._creer_panneau_principal()
        self._creer_panneau_visualisation()
        self._creer_panneau_controles()

    def _creer_panneau_principal(self):
        """Crée le panneau de gauche avec les statistiques de l'IA."""
        frame = ctk.CTkFrame(self.root)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            frame, text="SURVEILLANCE IA", font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Stats vitales (Directive 23)
        stats_frame = ctk.CTkFrame(frame)
        stats_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        stats_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            stats_frame, text="Stats Vitales", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=5)

        ctk.CTkLabel(stats_frame, text="Vie:").grid(row=1, column=0, padx=5, sticky="w")
        self.progress_vie = ctk.CTkProgressBar(stats_frame)
        self.progress_vie.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.progress_vie.set(0.8)  # Valeur par défaut

        ctk.CTkLabel(stats_frame, text="Faim:").grid(
            row=2, column=0, padx=5, sticky="w"
        )
        self.progress_faim = ctk.CTkProgressBar(stats_frame)
        self.progress_faim.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.progress_faim.set(0.6)  # Valeur par défaut

        # État contextuel
        self.label_mode = ctk.CTkLabel(
            frame,
            text="Mode: DÉMARRAGE",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8,
        )
        self.label_mode.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )

        # Stratégie actuelle
        strat_frame = ctk.CTkFrame(frame)
        strat_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(
            strat_frame,
            text="Stratégie Actuelle",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, pady=5)
        strat_frame.grid_columnconfigure(0, weight=1)
        self.text_strategie = ctk.CTkTextbox(strat_frame, height=80)
        self.text_strategie.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.text_strategie.insert("1.0", "Aucun")

        # Émotions (Directive 23)
        emotions_frame = ctk.CTkFrame(frame)
        emotions_frame.grid(
            row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew"
        )
        emotions_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            emotions_frame,
            text="État Émotionnel",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=5)

        self.progress_emotions = {}
        emotions_config = [
            ("confiance", 0.7),
            ("peur", 0.2),
            ("frustration", 0.1),
            ("fierte", 0.4),
        ]

        for i, (emotion, valeur_defaut) in enumerate(emotions_config):
            ctk.CTkLabel(emotions_frame, text=f"{emotion.title()}:").grid(
                row=i + 1, column=0, padx=5, sticky="w"
            )
            progress = ctk.CTkProgressBar(emotions_frame)
            progress.grid(row=i + 1, column=1, padx=5, pady=2, sticky="ew")
            progress.set(valeur_defaut)
            self.progress_emotions[emotion] = progress

    def _creer_panneau_visualisation(self):
        """Crée le panneau central avec la vue du jeu et les graphiques."""
        frame = ctk.CTkFrame(self.root)
        frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(1, weight=2)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="VISUALISATION", font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, pady=10)

        # Vue subjective (Directive 20)
        vue_subjective_frame = ctk.CTkFrame(frame, fg_color="black")
        vue_subjective_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        ctk.CTkLabel(
            vue_subjective_frame,
            text="VUE SUBJECTIVE (RECONSTRUCTION)",
            font=ctk.CTkFont(size=16),
        ).pack(expand=True)

        # Graphique d'apprentissage (Directive 43)
        self._initialiser_graphique(frame)

    def _initialiser_graphique(self, parent_frame):
        """Initialise le graphique matplotlib avec données par défaut."""
        self.fig, self.ax = plt.subplots(facecolor="#242424", figsize=(8, 4))
        self.ax.set_facecolor("#1a1a1a")
        self.ax.tick_params(axis="x", colors="white")
        self.ax.tick_params(axis="y", colors="white")
        self.ax.spines["bottom"].set_color("white")
        self.ax.spines["left"].set_color("white")
        self.ax.spines["top"].set_color("none")
        self.ax.spines["right"].set_color("none")
        self.ax.set_title(
            "Courbe d'Apprentissage (Concepts)", color="white", fontsize=14
        )

        # Données par défaut pour le graphique
        temps_defaut = list(range(86, 91))
        concepts_defaut = [7.0, 7.0, 7.0, 7.0, 7.0]
        self.ax.plot(temps_defaut, concepts_defaut, color="#00aaff", linewidth=2)
        self.ax.set_ylim(6.7, 7.3)

        self.canvas = FigureCanvasTkAgg(self.fig, parent_frame)
        self.canvas.get_tk_widget().grid(
            row=2, column=0, padx=10, pady=10, sticky="nsew"
        )

    def _creer_panneau_controles(self):
        """Crée le panneau de droite avec les outils du Mentor."""
        frame = ctk.CTkFrame(self.root, width=250)
        frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        frame.grid_propagate(False)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="CONTRÔLES MENTOR", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        # Contrôles temporels (Directive 19)
        temp_frame = ctk.CTkFrame(frame)
        temp_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(temp_frame, text="Contrôle Temporel").pack()

        ctk.CTkButton(
            temp_frame, text="Pause", command=self.pause_simulation, width=200
        ).pack(fill="x", pady=2)

        ctk.CTkButton(
            temp_frame, text="Reprendre", command=self.reprendre_simulation, width=200
        ).pack(fill="x", pady=2)

        self.label_vitesse = ctk.CTkLabel(temp_frame, text="Vitesse: x1.0")
        self.label_vitesse.pack(pady=(10, 0))

        self.scale_vitesse = ctk.CTkSlider(
            temp_frame,
            from_=1,
            to=100,
            number_of_steps=99,
            command=self.changer_vitesse,
        )
        self.scale_vitesse.set(10)
        self.scale_vitesse.pack(fill="x", padx=5, pady=5)

        # Outils d'interrogation (Directive 55)
        interrog_frame = ctk.CTkFrame(frame)
        interrog_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(interrog_frame, text="Interrogation IA").pack()

        ctk.CTkButton(
            interrog_frame,
            text="Pourquoi?",
            command=self.demander_raisonnement,
            width=200,
        ).pack(fill="x", pady=2)

        ctk.CTkButton(
            interrog_frame,
            text="Rapport Efficacité",
            command=self.demander_rapport,
            width=200,
        ).pack(fill="x", pady=2)

        self.check_inspection = ctk.CTkCheckBox(
            interrog_frame,
            text="Mode Inspection",
            variable=self.var_inspection,
            command=self.toggle_mode_inspection,
        )
        self.check_inspection.pack(pady=5)

        # Actions d'urgence
        urgence_frame = ctk.CTkFrame(frame)
        urgence_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(urgence_frame, text="Actions d'Urgence").pack()

        ctk.CTkButton(
            urgence_frame,
            text="Forcer Diagnostic",
            command=self.forcer_diagnostic,
            fg_color=("#cc6600", "#994400"),
            width=200,
        ).pack(fill="x", pady=2)

        ctk.CTkButton(
            urgence_frame,
            text="Arrêt d'Urgence",
            command=self.arret_urgence,
            fg_color=("#cc0000", "#990000"),
            width=200,
        ).pack(fill="x", pady=2)

    # === COMMUNICATION BIDIRECTIONNELLE CORRIGÉE ===

    def pause_simulation(self):
        """Envoie commande pause à l'IA."""
        try:
            self.q_sortie.put({"commande": "PAUSE"}, timeout=0.1)
            print("INFO: Commande PAUSE envoyée")
        except queue.Full:
            print("WARNING: Queue pleine - commande PAUSE ignorée")

    def reprendre_simulation(self):
        """Envoie commande reprendre à l'IA."""
        try:
            self.q_sortie.put({"commande": "REPRENDRE"}, timeout=0.1)
            print("INFO: Commande REPRENDRE envoyée")
        except queue.Full:
            print("WARNING: Queue pleine - commande REPRENDRE ignorée")

    def changer_vitesse(self, slider_value):
        """Change la vitesse de simulation."""
        vitesse = round(float(slider_value) / 10, 1)
        if self.label_vitesse:
            self.label_vitesse.configure(text=f"Vitesse: x{vitesse}")

        try:
            self.q_sortie.put(
                {"commande": "CHANGER_VITESSE", "valeur": vitesse}, timeout=0.1
            )
            print(f"INFO: Vitesse changée à x{vitesse}")
        except queue.Full:
            print("WARNING: Queue pleine - changement vitesse ignoré")

    def demander_raisonnement(self):
        """Demande le dernier raisonnement à l'IA."""
        try:
            self.q_sortie.put({"commande": "REQUETE_DERNIER_RAISONNEMENT"}, timeout=0.1)
            print("INFO: Demande de raisonnement envoyée")
        except queue.Full:
            print("WARNING: Queue pleine - demande raisonnement ignorée")

    def demander_rapport(self):
        """Demande un rapport d'efficacité à l'IA."""
        try:
            self.q_sortie.put(
                {"commande": "REQUETE_RAPPORT", "type": "efficacite"}, timeout=0.1
            )
            print("INFO: Demande de rapport envoyée")
        except queue.Full:
            print("WARNING: Queue pleine - demande rapport ignorée")

    def toggle_mode_inspection(self):
        """Active/désactive le mode inspection."""
        mode_actif = self.var_inspection.get()
        try:
            self.q_sortie.put(
                {"commande": "MODE_INSPECTION", "actif": mode_actif}, timeout=0.1
            )
            print(f"INFO: Mode inspection {'activé' if mode_actif else 'désactivé'}")
        except queue.Full:
            print("WARNING: Queue pleine - toggle inspection ignoré")

    def forcer_diagnostic(self):
        """Force un diagnostic de l'IA."""
        try:
            self.q_sortie.put("DECLENCHER_MAINTENANCE", timeout=0.1)
            print("INFO: Diagnostic forcé")
        except queue.Full:
            print("WARNING: Queue pleine - diagnostic ignoré")

    def arret_urgence(self):
        """Arrêt d'urgence avec confirmation."""
        if messagebox.askyesno(
            "Confirmation", "Êtes-vous sûr de vouloir lancer l'arrêt d'urgence ?"
        ):
            try:
                self.q_sortie.put("ARRET_URGENCE", timeout=0.1)
                print("INFO: Arrêt d'urgence déclenché")
                self.root.after(500, self._fermer_interface)
            except queue.Full:
                print("WARNING: Queue pleine - arrêt d'urgence par fermeture directe")
                self._fermer_interface()

    # === MONITORING SÉCURISÉ ===

    def demarrer_monitoring(self):
        """Lance le monitoring des messages IA."""
        print("INFO: Démarrage monitoring tableau de bord")
        threading.Thread(target=self._boucle_monitoring, daemon=True).start()

    def _boucle_monitoring(self):
        """Boucle de monitoring sécurisée."""
        while self.running:
            try:
                # Lecture non-bloquante avec timeout court
                message = self.q_entree.get(timeout=0.1)

                # Programmation thread-safe de la mise à jour GUI
                if self.running:
                    self.root.after(0, self._traiter_message_ia, message)

            except queue.Empty:
                continue
            except Exception as e:
                if self.running:  # Éviter spam d'erreurs lors fermeture
                    print(f"WARNING: Erreur monitoring GUI: {e}")
                    time.sleep(0.5)

    def _traiter_message_ia(self, message):
        """Traite les messages reçus de l'IA de façon sécurisée."""
        if not self.running or not isinstance(message, dict):
            return

        try:
            # Mise à jour du mode
            if "mode" in message and self.label_mode:
                mode = message["mode"]
                self.label_mode.configure(text=f"Mode: {mode}")

            # Mise à jour des émotions
            if "emotions" in message and isinstance(message["emotions"], dict):
                for emotion, value in message["emotions"].items():
                    if emotion in self.progress_emotions and isinstance(
                        value, (int, float)
                    ):
                        # Normaliser la valeur entre 0 et 1
                        valeur_normalisee = max(0.0, min(1.0, float(value)))
                        self.progress_emotions[emotion].set(valeur_normalisee)

            # Mise à jour de la stratégie
            if "plan_actuel" in message and self.text_strategie:
                plan = str(message["plan_actuel"])[:500]  # Limite taille
                self.text_strategie.delete("1.0", "end")
                self.text_strategie.insert("1.0", plan)

            # Mise à jour des statistiques vitales
            if "stats_vitales" in message and isinstance(
                message["stats_vitales"], dict
            ):
                stats = message["stats_vitales"]
                if "vie" in stats and self.progress_vie:
                    vie = max(0.0, min(1.0, float(stats["vie"])))
                    self.progress_vie.set(vie)
                if "faim" in stats and self.progress_faim:
                    faim = max(0.0, min(1.0, float(stats["faim"])))
                    self.progress_faim.set(faim)

            # Mise à jour de l'apprentissage
            if "connaissances" in message and isinstance(
                message["connaissances"], dict
            ):
                concepts = message["connaissances"].get("concepts_appris", 0)
                if isinstance(concepts, (int, float)):
                    self._ajouter_donnee_apprentissage(float(concepts))

        except Exception as e:
            print(f"WARNING: Erreur traitement message GUI: {e}")

    def _ajouter_donnee_apprentissage(self, concepts):
        """Ajoute une nouvelle donnée d'apprentissage au graphique."""
        try:
            current_time = time.time()
            self.donnees_apprentissage.append(concepts)
            self.temps_apprentissage.append(current_time)

            # Mise à jour du graphique (limitée dans le temps)
            if current_time - self.dernier_update > 1.0:  # Max 1 update/seconde
                self._mettre_a_jour_graphique()
                self.dernier_update = current_time

        except Exception as e:
            print(f"WARNING: Erreur graphique apprentissage: {e}")

    def _mettre_a_jour_graphique(self):
        """Met à jour le graphique d'apprentissage de façon sécurisée."""
        if not (self.ax and self.fig and self.canvas and self.running):
            return

        try:
            self.ax.clear()

            if len(self.donnees_apprentissage) > 1:
                self.ax.plot(
                    list(self.temps_apprentissage),
                    list(self.donnees_apprentissage),
                    color="#00aaff",
                    linewidth=2,
                )

            # Configuration graphique
            self.ax.set_title("Courbe d'Apprentissage (Concepts)", color="white")
            self.ax.set_facecolor("#1a1a1a")
            self.ax.tick_params(axis="x", colors="white")
            self.ax.tick_params(axis="y", colors="white")

            # Redessiner
            self.canvas.draw_idle()  # Version non-bloquante

        except Exception as e:
            print(f"WARNING: Erreur redessinage graphique: {e}")

    def _fermer_interface(self):
        """Ferme l'interface proprement."""
        print("INFO: Fermeture tableau de bord")
        self.running = False

        try:
            # Signal d'arrêt à l'IA
            self.q_sortie.put("INTERFACE_FERMEE", timeout=0.1)
        except:
            pass

        # Nettoyage matplotlib
        if self.fig:
            plt.close(self.fig)

        # Fermeture fenêtre
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

    def demarrer(self):
        """Démarre l'interface complète."""
        print("INFO: Démarrage interface tableau de bord")
        self.demarrer_monitoring()

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("INFO: Interruption clavier détectée")
        finally:
            self._fermer_interface()
