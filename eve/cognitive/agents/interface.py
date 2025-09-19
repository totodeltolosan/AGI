# -*- coding: utf-8 -*-
# interface.py (v6.6 - Gestion de la Charge)
# Limite le nombre de cartes affichées pour éviter les fuites de ressources.

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os, subprocess, sys, time
from datetime import datetime
from core.orchestrateur import Orchestrateur
import historique
from sonore import db_sonore
import collections # On importe collections pour la deque

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistant IA Alma - Panneau de Contrôle v2.5")
        self.geometry("950x700")
        self.minsize(800, 500)

        self.orchestrateur = None
        self.surveillance_active = False
        self.nouveaux_feedbacks_compteur = 0
        self.presence_on = tk.BooleanVar(value=True)

        # --- NOUVEAU : Limiteur de cartes ---
        self.MAX_CARTES_AFFICHEES = 50
        self.cartes_affiches = collections.deque(maxlen=self.MAX_CARTES_AFFICHEES)
        # --- FIN NOUVEAU ---

        self.causes_feedback_pc = self._charger_json("causes_feedback.json", "causes PC")
        self.causes_feedback_sonore = self._charger_json("sonore/causes_sonores.json", "causes Sonores")
        self.traducteur_yamnet = self._charger_json("sonore/traduction_yamnet.json", "Traductions YAMNet")
        if self.causes_feedback_pc is None or self.causes_feedback_sonore is None or self.traducteur_yamnet is None:
            self.after(100, self.destroy)
            return
        self._creer_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    # ... (les fonctions _charger_json et _creer_widgets sont identiques) ...
    def _charger_json(self, filename, nom):
        try:
            with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception as e:
            messagebox.showerror("Erreur Critique", f"Fichier '{filename}' ({nom}) introuvable ou illisible.\n{e}\nL'application va se fermer.")
            return None

    def _creer_widgets(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        control_frame = ttk.Frame(self, padding="10")
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,0))
        control_frame.columnconfigure(2, weight=1)
        self.bouton_lancer = ttk.Button(control_frame, text="LANCER LA SURVEILLANCE", command=self.demarrer_surveillance)
        self.bouton_lancer.grid(row=0, column=0, padx=5, ipady=5)
        self.bouton_arreter = ttk.Button(control_frame, text="Arrêter", command=self.arreter_surveillance, state=tk.DISABLED)
        self.bouton_arreter.grid(row=0, column=1, padx=5)
        presence_frame = ttk.Frame(control_frame)
        presence_frame.grid(row=0, column=3, padx=10)
        ttk.Label(presence_frame, text="Présence :").pack(side=tk.LEFT)
        self.switch_presence = ttk.Checkbutton(presence_frame, text="ON", style='Switch.TCheckbutton', variable=self.presence_on, command=self.toggle_presence)
        self.switch_presence.pack(side=tk.LEFT)
        self.label_statut = ttk.Label(control_frame, text="Statut : Prêt", font=('Segoe UI', 10, 'bold'), anchor='e')
        self.label_statut.grid(row=0, column=4, padx=5, sticky='e')
        log_frame = ttk.Labelframe(self, text="Journal des Événements et Feedback", padding=10)
        log_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        canvas = tk.Canvas(log_frame)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def toggle_presence(self):
        etat_actuel = self.presence_on.get()
        self.switch_presence.config(text="ON" if etat_actuel else "OFF")
        if self.orchestrateur and self.surveillance_active:
            print(f"[Interface] Mode Présence changé à : {'ON' if etat_actuel else 'OFF'}")
            self.orchestrateur.definir_etat_presence(etat_actuel)

    def demarrer_surveillance(self):
        self.nouveaux_feedbacks_compteur = 0
        # On vide la liste des cartes au démarrage
        for carte in self.cartes_affiches: carte.destroy()
        self.cartes_affiches.clear()

        self.bouton_lancer.config(state=tk.DISABLED)
        self.bouton_arreter.config(state=tk.NORMAL)
        self.label_statut.config(text="Statut : Démarrage en cours...")
        self.orchestrateur = Orchestrateur(presence_initiale=self.presence_on.get())
        self.orchestrateur.demarrer_surveillance()
        self.surveillance_active = True
        self.label_statut.config(text="Statut : Surveillance active.")
        self._verifier_queue()

    def _ajouter_carte(self, carte_frame):
        """Ajoute une nouvelle carte et supprime la plus ancienne si la limite est atteinte."""
        if len(self.cartes_affiches) >= self.MAX_CARTES_AFFICHEES:
            carte_a_supprimer = self.cartes_affiches.popleft() # Retire la plus ancienne de la liste
            carte_a_supprimer.destroy() # Détruit le widget
        self.cartes_affiches.append(carte_frame) # Ajoute la nouvelle

    def _creer_carte_feedback(self, titre):
        event_frame = ttk.Labelframe(self.scrollable_frame, text=titre, padding=10)
        event_frame.pack(padx=10, pady=5, fill=tk.X, anchor="n")
        # On ajoute la carte à notre gestionnaire
        self._ajouter_carte(event_frame)
        return event_frame

    # ... (le reste du fichier est identique) ...
    def arreter_surveillance(self):
        if self.orchestrateur: self.orchestrateur.arreter_surveillance()
        self.surveillance_active = False
        self.bouton_lancer.config(state=tk.NORMAL)
        self.bouton_arreter.config(state=tk.DISABLED)
        self.label_statut.config(text="Statut : Arrêté.")
        self._gerer_fin_session()

    def _verifier_queue(self):
        if not self.surveillance_active: return
        try:
            while not self.orchestrateur.ui_queue.empty():
                ticket = self.orchestrateur.ui_queue.get_nowait()
                if ticket.get("type") == "SON": self._afficher_feedback_sonore(ticket)
                elif ticket.get("type") == "PC":
                    diagnostics = ticket.get('diagnostics', [])
                    if diagnostics:
                        if "ROUTINE :" in diagnostics[0]: self.label_statut.config(text=f"Statut : {diagnostics[0].replace('ROUTINE : ', '')}")
                        else:
                            self.label_statut.config(text="Statut : Événement PC Détecté!")
                            self._afficher_feedback_pc(ticket)
        except Exception as e: print(f"[Interface] Erreur lors de la vérification de la queue: {e}")
        finally: self.after(500, self._verifier_queue)

    def _afficher_feedback_pc(self, ticket):
        ts = datetime.fromisoformat(ticket['timestamp']).timestamp()
        titre = f"Diagnostic PC ({time.strftime('%H:%M:%S', time.localtime(ts))})"
        frame = self._creer_carte_feedback(titre)
        frame.update_idletasks()
        wraplength = self.scrollable_frame.winfo_width() - 40
        ttk.Label(frame, text="\n".join(ticket['diagnostics']), wraplength=wraplength, justify=tk.LEFT).pack(padx=5, pady=5, anchor="w")
        ttk.Label(frame, text="Votre feedback ?", font=('Segoe UI', 9, 'italic')).pack(pady=(10, 5), anchor="w")
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=5, fill=tk.X)
        for code, nom in self.causes_feedback_pc.items():
            btn = ttk.Button(buttons_frame, text=nom, command=lambda t=ticket, c=code, f=frame: self._soumettre_feedback_pc(t, c, f))
            btn.pack(side=tk.LEFT, padx=2, pady=2)

    def _afficher_feedback_sonore(self, ticket):
        ts = datetime.fromisoformat(ticket['timestamp']).timestamp()
        titre = f"Son Détecté ({time.strftime('%H:%M:%S', time.localtime(ts))})"
        frame = self._creer_carte_feedback(titre)
        ttk.Label(frame, text="Prédictions de YAMNet (cliquez pour valider) :").pack(anchor="w", padx=5, pady=(0,5))
        predictions = ticket.get('predictions', [])
        mfcc = ticket.get('empreinte_mfcc')
        predictions_affichables = False
        for code_yamnet, score in predictions:
            if score < 0.1 or code_yamnet == 'Silence': continue
            nom_traduit = self.traducteur_yamnet.get(code_yamnet, code_yamnet)
            code_cause_interne = next((code for code, nom in self.causes_feedback_sonore.items() if nom == nom_traduit), None)
            if code_cause_interne:
                predictions_affichables = True
                line_frame = ttk.Frame(frame)
                line_frame.pack(fill=tk.X, padx=5, pady=1)
                btn_text = f"✔  C'était bien : {nom_traduit} ({score:.1%})"
                btn = ttk.Button(line_frame, text=btn_text, style='success.TButton', command=lambda cause=nom_traduit, m=mfcc, f=frame: self._soumettre_feedback_sonore(cause, m, f))
                btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if not predictions_affichables:
            texte_prediction = "\n".join([f"- {self.traducteur_yamnet.get(nom, nom)} ({score:.1%})" for nom, score in predictions if score > 0.1])
            ttk.Label(frame, text=texte_prediction if texte_prediction else "Aucun son pertinent détecté.").pack(anchor="w", padx=5)
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10, padx=5)
        ttk.Label(frame, text="Ou corrigez avec une autre cause :", font=('Segoe UI', 9, 'italic')).pack(pady=(5, 5), anchor="w", padx=5)
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=5, fill=tk.X, padx=5)
        selected_cause = tk.StringVar()
        cause_menu = ttk.Combobox(buttons_frame, textvariable=selected_cause, values=list(self.causes_feedback_sonore.values()), state="readonly", width=30)
        cause_menu.pack(side=tk.LEFT)
        cause_menu.set("Choisir une cause...")
        submit_button = ttk.Button(buttons_frame, text="Valider", command=lambda m=mfcc, f=frame: self._soumettre_feedback_sonore(cause_menu.get(), m, f))
        submit_button.pack(side=tk.LEFT, padx=5)

    def _soumettre_feedback_pc(self, ticket, cause_code, frame):
        cause_reelle = cause_code
        if cause_code == "AUTRE":
            nouvelle_cause = simpledialog.askstring("Nouvelle Cause", "Décrire la cause :", parent=self)
            if nouvelle_cause and nouvelle_cause.strip(): cause_reelle = nouvelle_cause.strip().upper().replace(" ", "_")
            else: return
        donnees_brutes = ticket.get('donnees_brutes', {})
        evenement = {'timestamp': ticket['timestamp'], 'cpu_charge': donnees_brutes.get('cpu_charge_globale', {}).get('charge_cpu_pourcentage', 0), 'ram_usage_pourcentage': donnees_brutes.get('memoire_ram', {}).get('usage_pourcentage', 0), 'top_processus_nom': donnees_brutes.get('processus_top',{}).get('details',[{}])[0].get('name','N/A'), 'environnement_sonore': donnees_brutes.get('environnement_sonore', 'INCONNU'), 'diagnostic_initial': "; ".join(ticket['diagnostics']), 'cause_reelle': cause_reelle}
        historique.enregistrer_evenement(evenement)
        self.nouveaux_feedbacks_compteur += 1
        self._confirmer_feedback_ui(frame, self.causes_feedback_pc.get(cause_code, cause_code))

    def _soumettre_feedback_sonore(self, nom_cause, mfcc, frame):
        if not nom_cause or nom_cause == "Choisir une cause...":
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une cause dans le menu.")
            return
        code_cause = next((code for code, nom in self.causes_feedback_sonore.items() if nom == nom_cause), None)
        if not code_cause:
             messagebox.showerror("Erreur", f"La cause '{nom_cause}' est inconnue.")
             return
        if code_cause == "AUTRE_SON":
            nouvelle_cause = simpledialog.askstring("Nouvelle Cause Sonore", "Décrire le son :", parent=self)
            if nouvelle_cause and nouvelle_cause.strip(): code_cause = nouvelle_cause.strip().upper().replace(" ", "_")
            else: return
        if code_cause:
            db_sonore.sauvegarder_son(mfcc, code_cause)
            self.nouveaux_feedbacks_compteur += 1
            self._confirmer_feedback_ui(frame, nom_cause)

    def _confirmer_feedback_ui(self, frame, cause_nom):
        for widget in frame.winfo_children(): widget.destroy()
        ttk.Label(frame, text=f"✔ Merci ! Feedback '{cause_nom}' enregistré.", foreground="green", font=('Segoe UI', 10, 'bold')).pack(pady=10)

    def _gerer_fin_session(self):
        messagebox.showinfo("Fin de Session", f"Session terminée.\n\nNouveaux feedbacks enregistrés : {self.nouveaux_feedbacks_compteur}")
        if self.nouveaux_feedbacks_compteur > 0:
            if messagebox.askyesno("Entraînement", "De nouvelles connaissances sont disponibles.\nVoulez-vous lancer un entraînement pour améliorer Alma ?"):
                self._lancer_entrainement()

    def _lancer_entrainement(self):
        try:
            command = [sys.executable, "entrainement.py"]
            if sys.platform == "win32": subprocess.Popen(["start", "cmd", "/k"] + command, shell=True)
            elif sys.platform == "darwin": subprocess.Popen(["open", "-a", "Terminal", command[0], "--args"] + command[1:])
            else: subprocess.Popen(["gnome-terminal", "--"] + command)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer l'entraînement automatiquement:\n{e}\n\nVeuillez le lancer manuellement:\npython entrainement.py")

    def _on_closing(self):
        if self.surveillance_active: self.arreter_surveillance()
        self.destroy()

if __name__ == "__main__":
    app = Application()
    style = ttk.Style(app)
    style.configure('success.TButton', foreground='green', font=('Segoe UI', 9, 'bold'))
    style.configure('Switch.TCheckbutton', font=('Segoe UI', 9, 'bold'))
    app.mainloop()
