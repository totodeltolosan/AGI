"""
Fenêtre visualisation écran partagé (Directive 20).
Vue subjective + carte tactique détaillée.
"""

import customtkinter as ctk
from tkinter import Canvas
import logging

logger = logging.getLogger(__name__)


class FenetreVisualisation:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, parent, queue_ia_vers_gui, config):
        self.parent = parent
        self.queue_entree = queue_ia_vers_gui
        self.config = config

        self.fenetre = ctk.CTkToplevel(parent)
        self.fenetre.title("Le Simulateur - Visualisation")
        self.fenetre.geometry("1000x600")

        self.canvas_subjectif = None
        self.canvas_carte = None

        self._creer_interface()

    def _creer_interface(self):
        """Crée interface écran partagé."""
        self.fenetre.grid_columnconfigure(0, weight=1)
        self.fenetre.grid_columnconfigure(1, weight=1)
        self.fenetre.grid_rowconfigure(0, weight=1)

        self._creer_vue_subjective()
        self._creer_carte_tactique()

    def _creer_vue_subjective(self):
        """Crée frame vue subjective (non-visuelle)."""
        frame_subjectif = ctk.CTkFrame(self.fenetre)
        frame_subjectif.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        label_titre = ctk.CTkLabel(frame_subjectif, text="Vue Subjective IA")
        label_titre.pack(pady=10)

        self.canvas_subjectif = Canvas(
            frame_subjectif, bg="#1a1a1a", highlightthickness=0
        )
        self.canvas_subjectif.pack(fill="both", expand=True, padx=10, pady=10)

    def _creer_carte_tactique(self):
        """Crée frame carte tactique détaillée."""
        frame_carte = ctk.CTkFrame(self.fenetre)
        frame_carte.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        label_titre = ctk.CTkLabel(frame_carte, text="Carte Tactique")
        label_titre.pack(pady=10)

        self.canvas_carte = Canvas(frame_carte, bg="#1a1a1a", highlightthickness=0)
        self.canvas_carte.pack(fill="both", expand=True, padx=10, pady=10)

    def mettre_a_jour_vue_subjective(self, donnees_perception):
        """Met à jour vue subjective avec données IA."""
        if not self.canvas_subjectif:
            return

        self.canvas_subjectif.delete("all")

        y_offset = 20
        for entite in donnees_perception.get("entites_visibles", []):
            self.canvas_subjectif.create_rectangle(
                10,
                y_offset,
                100,
                y_offset + 30,
                fill=self._couleur_entite(entite["type"]),
                outline="white",
            )
            self.canvas_subjectif.create_text(
                110,
                y_offset + 15,
                text=f"{entite['type']} ({entite['distance']:.1f}m)",
                fill="white",
                anchor="w",
            )
            y_offset += 40

    def mettre_a_jour_carte(self, donnees_carte):
        """Met à jour carte tactique."""
        if not self.canvas_carte:
            return

        self.canvas_carte.delete("all")

        centre_x = self.canvas_carte.winfo_width() // 2
        centre_y = self.canvas_carte.winfo_height() // 2

        for bloc in donnees_carte.get("blocs_proches", []):
            x = centre_x + bloc["position"]["x"] * 10
            y = centre_y + bloc["position"]["z"] * 10

            self.canvas_carte.create_rectangle(
                x - 5,
                y - 5,
                x + 5,
                y + 5,
                fill=self._couleur_bloc(bloc["type"]),
                outline="gray",
            )

    def _couleur_entite(self, type_entite):
        """Retourne couleur selon type entité."""
        couleurs = {
            "mob_hostile": "#ff4444",
            "mob_passif": "#44ff44",
            "joueur": "#4444ff",
            "objet": "#ffff44",
        }
        return couleurs.get(type_entite, "#888888")

    def _couleur_bloc(self, type_bloc):
        """Retourne couleur selon type bloc."""
        couleurs = {
            "air": "#000000",
            "stone": "#666666",
            "dirt": "#8B4513",
            "grass": "#228B22",
            "water": "#0066cc",
        }
        return couleurs.get(type_bloc, "#444444")