#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAPPORT D'ANALYSE SYSTÈME AVANCÉ (v3.6 - God Mode++++ - Partie 6 : L'Ultime Évolution IA)
Généré le : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Utilisateur : {getpass.getuser()}
Hôte : {socket.gethostname()}

Ce script Python avec interface graphique Tkinter est conçu pour effectuer une vérification complète,
des optimisations avancées, et guider l'utilisateur vers l'intégration d'outils d'intelligence artificielle
gratuits et optimisés sur un système Ubuntu.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import subprocess
import threading
import queue
import os
import time
import json  # For parsing pro security-status --format json
import re  # For regex in log parsing
import sys  # For Python version check
import datetime  # For dynamic date/time in header
import getpass  # For dynamic username
import socket  # For dynamic hostname

# Global variable for sudo password
GLOBAL_SUDO_PASSWORD = None


class SudoPasswordDialog(simpledialog.Dialog):
    """Dialogue pour demander le mot de passe sudo."""

    def body(self, master):
        tk.Label(master, text="Mot de passe sudo:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.entry = tk.Entry(master, show="*")
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        master.grid_columnconfigure(1, weight=1)
        return self.entry  # initial focus

    def apply(self):
        global GLOBAL_SUDO_PASSWORD
        GLOBAL_SUDO_PASSWORD = self.entry.get()
        self.result = True  # Indicate success


class SystemAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("Analyse Système God Mode++++ (Ultime Évolution IA)")
        master.geometry("1400x900")  # Increased size
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.output_queue = queue.Queue()

        # Initialize log_text early for tag configuration
        self.log_frame = ttk.LabelFrame(self.master, text="Journal des Opérations")
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame, wrap=tk.WORD, height=15, state=tk.DISABLED
        )

        # Configure tags for colored log messages
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("command", foreground="purple")
        self.log_text.tag_configure(
            "output", foreground="black"
        )  # Default color for command output

        self.check_prerequisites()
        self.create_widgets()
        self.refresh_all_statuses()  # Initial refresh
        self.process_queue()  # Start processing queue for live output (moved after initial refresh)

    def on_closing(self):
        if messagebox.askokcancel(
            "Quitter", "Voulez-vous vraiment quitter l'application ?"
        ):
            self.master.destroy()
            sys.exit(0)  # Ensure all threads and processes exit cleanly

    def check_prerequisites(self):
        # Check for Python version
        if not (sys.version_info.major >= 3 and sys.version_info.minor >= 8):
            messagebox.showerror(
                "Erreur de Prérequis",
                "Python 3.8 ou supérieur est requis pour ce script.",
            )
            self.master.destroy()
            sys.exit(1)

        # Check for Tkinter
        try:
            import tkinter
        except ImportError:
            messagebox.showerror(
                "Erreur de Prérequis",
                "Tkinter n'est pas installé. Veuillez exécuter 'sudo apt install python3-tk'.",
            )
            self.master.destroy()
            sys.exit(1)

        # Check for git and curl (for AI tools)
        if not self.check_command_exists("git"):
            messagebox.showwarning(
                "Prérequis manquant",
                "Git n'est pas installé. Certaines fonctionnalités IA (llama.cpp) pourraient ne pas fonctionner. Installez-le avec 'sudo apt install git'.",
            )
        if not self.check_command_exists("curl"):
            messagebox.showwarning(
                "Prérequis manquant",
                "Curl n'est pas installé. Certaines fonctionnalités IA (Ollama) pourraient ne pas fonctionner. Installez-le avec 'sudo apt install curl'.",
            )
        if not self.check_command_exists("pip3"):
            messagebox.showwarning(
                "Prérequis manquant",
                "pip3 n'est pas installé. Certaines fonctionnalités IA (Jupyter) pourraient ne pas fonctionner. Installez-le avec 'sudo apt install python3-pip'.",
            )

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Création des onglets
        self.tab_overview = ttk.Frame(self.notebook)
        self.tab_critical = ttk.Frame(self.notebook)
        self.tab_tools = ttk.Frame(self.notebook)
        self.tab_optimizations = ttk.Frame(self.notebook)
        self.tab_hardening = ttk.Frame(self.notebook)
        self.tab_ai = ttk.Frame(self.notebook)
        self.tab_strategic = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_overview, text="Vue d'ensemble")
        self.notebook.add(self.tab_critical, text="Points Critiques")
        self.notebook.add(self.tab_tools, text="Outils")
        self.notebook.add(self.tab_optimizations, text="Optimisations Générales")
        self.notebook.add(self.tab_hardening, text="Audit & Durcissement")
        self.notebook.add(self.tab_ai, text="Intégration IA")
        self.notebook.add(self.tab_strategic, text="Vision Stratégique")

        self.create_overview_tab()
        self.create_critical_tab()
        self.create_tools_tab()
        self.create_optimizations_tab()
        self.create_hardening_tab()
        self.create_ai_tab()
        self.create_strategic_tab()

        # Zone de log globale en bas (already initialized in __init__)
        self.log_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)
        self.log_text.pack(expand=True, fill="both")

        # Bouton pour effacer le log
        clear_log_btn = ttk.Button(
            self.log_frame, text="Effacer le Journal", command=self.clear_log
        )
        clear_log_btn.pack(side=tk.RIGHT, padx=5, pady=2)

        # Bouton pour rafraîchir tous les statuts (utile après des changements)
        refresh_btn = ttk.Button(
            self.master,
            text="Rafraîchir Tous les Statuts",
            command=self.refresh_all_statuses,
        )
        refresh_btn.pack(side=tk.BOTTOM, pady=5)

    def log_message(self, message, tag=None):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.master.update_idletasks()  # Force GUI update

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def get_sudo_password(self):
        global GLOBAL_SUDO_PASSWORD
        if not GLOBAL_SUDO_PASSWORD:
            dialog = SudoPasswordDialog(self.master)
            if dialog.result:  # dialog.result is True if password was entered
                return GLOBAL_SUDO_PASSWORD
            else:
                self.log_message(
                    "Opération sudo annulée : mot de passe non fourni.", "error"
                )
                return None
        return GLOBAL_SUDO_PASSWORD

    def run_command_threaded(
        self, description, command, needs_sudo=False, callback=None, *args
    ):
        def _run():
            self.output_queue.put((f"\n[ EXÉCUTION ] {description}", "info"))
            self.output_queue.put((f"Commande : {command}", "command"))
            self.output_queue.put(("--- Début de la sortie ---", "info"))

            full_command_list = []
            process = None
            return_code = 1  # Default to error
            full_output = ""

            try:
                if needs_sudo:
                    password = self.get_sudo_password()
                    if not password:
                        self.output_queue.put(
                            ("--- Fin de la sortie (Code de sortie : 1) ---", "error")
                        )
                        if callback:
                            self.output_queue.put((callback, (1, "", *args)))
                        return
                    full_command_list = ["sudo", "-S", "bash", "-c", command]
                    process = subprocess.Popen(
                        full_command_list,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )
                    if process.stdin:  # Check if stdin is not None
                        process.stdin.write(password + "\n")
                        process.stdin.flush()
                else:
                    full_command_list = ["bash", "-c", command]
                    process = subprocess.Popen(
                        full_command_list,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )

                output_lines = []
                if process.stdout:  # Check if stdout is not None
                    for line in process.stdout:
                        self.output_queue.put((line.strip(), "output"))
                        output_lines.append(line.strip())
                process.wait()
                return_code = process.returncode
                full_output = "\n".join(output_lines)

            except Exception as e:
                self.output_queue.put((f"Erreur d'exécution : {e}", "error"))
                full_output = f"Erreur d'exécution : {e}"
            finally:
                self.output_queue.put(
                    (
                        f"--- Fin de la sortie (Code de sortie : {return_code}) ---",
                        "success" if return_code == 0 else "error",
                    )
                )
                if callback:
                    # The callback itself is passed as the first item, followed by its arguments as a tuple.
                    # So, the queue item will be (callback_function, (return_code, full_output, *args))
                    self.output_queue.put(
                        (
                            callback,
                            (
                                return_code,
                                full_output if full_output is not None else "",
                                *args,
                            ),
                        )
                    )

        threading.Thread(target=_run).start()

    def process_queue(self):
        try:
            while True:
                item = self.output_queue.get_nowait()
                # Item can be (message_string, tag_string) OR (callback_func, callback_args_tuple)
                if isinstance(item, tuple) and len(item) == 2:
                    # Check if it's a callback item (first element is callable, second is a tuple)
                    if callable(item[0]) and isinstance(item[1], tuple):
                        callback_func = item[0]
                        callback_args = item[1]
                        callback_func(*callback_args)
                    # Otherwise, it's a log message item
                    elif isinstance(item[0], str) and (
                        item[1] is None or isinstance(item[1], str)
                    ):
                        message, tag = item
                        self.log_text.config(state=tk.NORMAL)
                        self.log_text.insert(tk.END, message + "\n", tag)
                        self.log_text.see(tk.END)
                        self.log_text.config(state=tk.DISABLED)
                    else:
                        self.log_message(
                            f"Unexpected tuple item in queue: {item}", "error"
                        )
                else:
                    self.log_message(
                        f"Unexpected non-tuple item in queue: {item}", "error"
                    )
        except queue.Empty:
            pass
        self.master.after(100, self.process_queue)  # Check again after 100ms

    def check_command_exists(self, cmd):
        return (
            subprocess.run(
                f"command -v {cmd}", shell=True, capture_output=True
            ).returncode
            == 0
        )

    def check_package_installed(self, pkg):
        return (
            subprocess.run(f"dpkg -s {pkg}", shell=True, capture_output=True).returncode
            == 0
        )

    def refresh_all_statuses(self):
        self.log_message("\nRafraîchissement de tous les statuts...", "info")
        self.update_overview_status()
        self.update_critical_status()
        self.update_tools_status()
        self.update_optimizations_status()
        self.update_hardening_status()
        self.update_ai_status()
        self.log_message("Statuts rafraîchis.", "info")

    # ==============================================================================
    # TAB: Vue d'ensemble
    # ==============================================================================
    def create_overview_tab(self):
        frame = ttk.Frame(self.tab_overview, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame, text="Informations Générales du Système", font=("Arial", 14, "bold")
        ).pack(pady=10)

        self.overview_labels = {}
        info_items = [
            "OS",
            "Noyau",
            "Architecture",
            "Modèle Système",
            "BIOS",
            "Uptime",
            "Utilisateur",
            "Heure Système",
            "Fuseau Horaire",
        ]
        for item in info_items:
            self.overview_labels[item] = ttk.Label(frame, text=f"{item}: Chargement...")
            self.overview_labels[item].pack(anchor="w", pady=2)

        ttk.Button(
            frame,
            text="Rafraîchir la Vue d'ensemble",
            command=self.update_overview_status,
        ).pack(pady=10)

    def update_overview_status(self):
        self.run_command_threaded(
            "Récupération OS Release",
            "lsb_release -d -s",
            callback=lambda rc, out, key="OS": self._update_label(rc, out, key),
        )
        self.run_command_threaded(
            "Récupération Noyau",
            "uname -r",
            callback=lambda rc, out, key="Noyau": self._update_label(rc, out, key),
        )
        self.run_command_threaded(
            "Récupération Architecture",
            "uname -m",
            callback=lambda rc, out, key="Architecture": self._update_label(
                rc, out, key
            ),
        )
        self.run_command_threaded(
            "Récupération Modèle Système",
            "sudo dmidecode -s system-product-name",
            needs_sudo=True,
            callback=lambda rc, out, key="Modèle Système": self._update_label(
                rc, out, key
            ),
        )
        self.run_command_threaded(
            "Récupération BIOS",
            "sudo dmidecode -s bios-version",
            needs_sudo=True,
            callback=lambda rc, out, key="BIOS": self._update_label(rc, out, key),
        )
        self.run_command_threaded(
            "Récupération Uptime",
            "uptime -p",
            callback=lambda rc, out, key="Uptime": self._update_label(rc, out, key),
        )
        self.run_command_threaded(
            "Récupération Utilisateur",
            "whoami",
            callback=lambda rc, out, key="Utilisateur": self._update_label(
                rc, out, key
            ),
        )
        self.run_command_threaded(
            "Récupération Heure Système",
            "date",
            callback=lambda rc, out, key="Heure Système": self._update_label(
                rc, out, key
            ),
        )
        self.run_command_threaded(
            "Récupération Fuseau Horaire",
            "timedatectl show --property=Timezone --value",
            callback=lambda rc, out, key="Fuseau Horaire": self._update_label(
                rc, out, key
            ),
        )

    def _update_label(self, return_code, output, label_key):
        if return_code == 0:
            self.overview_labels[label_key].config(
                text=f"{label_key}: {output.strip()}"
            )
        else:
            self.overview_labels[label_key].config(
                text=f"{label_key}: Erreur de récupération"
            )

    # ==============================================================================
    # TAB: Points Critiques
    # ==============================================================================
    def create_critical_tab(self):
        frame = ttk.Frame(self.tab_critical, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame,
            text="Gestion des Points Critiques (Priorité Absolue)",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Entropie
        entropy_frame = ttk.LabelFrame(frame, text="1. Entropie du système")
        entropy_frame.pack(fill="x", pady=5)
        self.entropy_status_label = ttk.Label(
            entropy_frame, text="Statut: Chargement..."
        )
        self.entropy_status_label.pack(anchor="w")
        ttk.Button(
            entropy_frame,
            text="Rafraîchir Entropie",
            command=self.update_entropy_status,
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            entropy_frame,
            text="Redémarrer haveged",
            command=lambda: self.run_command_threaded(
                "Redémarrage de haveged",
                "sudo systemctl restart haveged.service",
                needs_sudo=True,
                callback=self._process_entropy_status_callback,
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            entropy_frame,
            text="Activer rngd",
            command=lambda: self.run_command_threaded(
                "Activation de rngd",
                "sudo systemctl enable rngd --now",
                needs_sudo=True,
                callback=self._process_entropy_status_callback,
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            entropy_frame,
            text="Lancer rngtest",
            command=lambda: self.run_command_threaded(
                "Lancement de rngtest",
                "sudo rngtest -c 1000 < /dev/random",
                needs_sudo=True,
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            entropy_frame,
            text="Ajuster seuils noyau",
            command=self.adjust_kernel_entropy_thresholds,
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            entropy_frame,
            text="Vérifier TPM",
            command=lambda: self.run_command_threaded(
                "Vérification TPM",
                "lsmod | grep tpm_rng",
                needs_sudo=True,
                callback=lambda rc, out, key="TPM Status": messagebox.showinfo(
                    key,
                    (
                        "TPM module loaded."
                        if rc == 0
                        else "TPM module not loaded. Check BIOS/UEFI."
                    ),
                ),
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # UFW
        ufw_frame = ttk.LabelFrame(frame, text="2. Pare-feu UFW")
        ufw_frame.pack(fill="x", pady=5)
        self.ufw_status_label = ttk.Label(ufw_frame, text="Statut: Chargement...")
        self.ufw_status_label.pack(anchor="w")
        ttk.Button(
            ufw_frame, text="Rafraîchir UFW", command=self.update_ufw_status
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            ufw_frame, text="Activer UFW (Défaut)", command=self.activate_ufw_default
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Ubuntu Pro
        pro_frame = ttk.LabelFrame(frame, text="3. Ubuntu Pro")
        pro_frame.pack(fill="x", pady=5)
        self.pro_status_label = ttk.Label(pro_frame, text="Statut: Chargement...")
        self.pro_status_label.pack(anchor="w")
        ttk.Button(
            pro_frame, text="Rafraîchir Ubuntu Pro", command=self.update_pro_status
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            pro_frame, text="Attacher Ubuntu Pro", command=self.attach_ubuntu_pro
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Rétroéclairage clavier
        backlight_frame = ttk.LabelFrame(frame, text="4. Rétroéclairage du clavier")
        backlight_frame.pack(fill="x", pady=5)
        self.backlight_status_label = ttk.Label(
            backlight_frame, text="Statut: Chargement..."
        )
        self.backlight_status_label.pack(anchor="w")
        ttk.Button(
            backlight_frame,
            text="Rafraîchir Rétroéclairage",
            command=self.update_backlight_status,
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            backlight_frame,
            text="Appliquer Fix (Service)",
            command=self.apply_backlight_fix,
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            backlight_frame,
            text="Masquer Service Original",
            command=self.mask_original_backlight_service,
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            backlight_frame,
            text="Tester Manuellement",
            command=self.test_manual_backlight,
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # ACPI
        acpi_frame = ttk.LabelFrame(frame, text="5. Erreurs ACPI")
        acpi_frame.pack(fill="x", pady=5)
        self.acpi_status_label = ttk.Label(acpi_frame, text="Statut: Chargement...")
        self.acpi_status_label.pack(anchor="w")
        ttk.Button(
            acpi_frame, text="Rafraîchir ACPI", command=self.update_acpi_status
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            acpi_frame, text="Modifier GRUB (Nano)", command=self.edit_grub_config
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # FluidSynth/JACK
        audio_frame = ttk.LabelFrame(frame, text="6. Services FluidSynth et JACK")
        audio_frame.pack(fill="x", pady=5)
        self.audio_status_label = ttk.Label(audio_frame, text="Statut: Chargement...")
        self.audio_status_label.pack(anchor="w")
        ttk.Button(
            audio_frame, text="Rafraîchir Audio", command=self.update_audio_status
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            audio_frame,
            text="Purger FluidSynth/JACK",
            command=self.purge_audio_packages,
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # USB RODE
        usb_frame = ttk.LabelFrame(frame, text="7. Périphérique USB RODE NT-USB+")
        usb_frame.pack(fill="x", pady=5)
        self.usb_status_label = ttk.Label(usb_frame, text="Statut: Chargement...")
        self.usb_status_label.pack(anchor="w")
        ttk.Button(
            usb_frame, text="Rafraîchir USB", command=self.update_usb_status
        ).pack(side=tk.LEFT, padx=5, pady=2)

        ttk.Button(
            frame,
            text="Rafraîchir Tous les Statuts Critiques",
            command=self.update_critical_status,
        ).pack(pady=10)

    def update_critical_status(self):
        self.update_entropy_status()
        self.update_ufw_status()
        self.update_pro_status()
        self.update_backlight_status()
        self.update_acpi_status()
        self.update_audio_status()
        self.update_usb_status()

    def _process_entropy_status_callback(self, return_code, output):
        entropy_val = (
            int(output.strip()) if return_code == 0 and output.strip().isdigit() else 0
        )
        if entropy_val > 1000:
            self.entropy_status_label.config(
                text=f"Statut: ✅ Entropie adéquate ({entropy_val} bits)",
                foreground="green",
            )
        else:
            self.entropy_status_label.config(
                text=f"Statut: ❌ Entropie basse ({entropy_val} bits). Problème critique.",
                foreground="red",
            )
            # Intelligent suggestion: if low, try to activate rngd
            if (
                not self.check_package_installed("rng-tools")
                or subprocess.run(
                    "systemctl is-enabled rngd.service", shell=True, capture_output=True
                ).returncode
                != 0
            ):
                if messagebox.askyesno(
                    "Suggestion IA",
                    "L'entropie est basse et rngd ne semble pas actif. Voulez-vous l'activer maintenant ?",
                ):
                    self.run_command_threaded(
                        "Activation de rngd (suggestion IA)",
                        "sudo systemctl enable rngd --now",
                        needs_sudo=True,
                        callback=self._process_entropy_status_callback,
                    )

    def update_entropy_status(self):  # This is called by buttons/refresh
        self.run_command_threaded(
            "Vérification entropie",
            "cat /proc/sys/kernel/random/entropy_avail",
            callback=self._process_entropy_status_callback,
        )

    def adjust_kernel_entropy_thresholds(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous ajuster les seuils d'entropie du noyau (avancé) ? Un redémarrage est recommandé après.",
        ):
            self.run_command_threaded(
                "Ajout seuil lecture",
                'echo "kernel.random.read_wakeup_threshold = 1024" | sudo tee -a /etc/sysctl.d/99-custom-entropy.conf > /dev/null',
                needs_sudo=True,
            )
            self.run_command_threaded(
                "Ajout seuil écriture",
                'echo "kernel.random.write_wakeup_threshold = 2048" | sudo tee -a /etc/sysctl.d/99-custom-entropy.conf > /dev/null',
                needs_sudo=True,
            )
            self.run_command_threaded(
                "Application sysctl", "sudo sysctl -p", needs_sudo=True
            )
            messagebox.showinfo(
                "Info", "Seuils ajustés. Un redémarrage est recommandé."
            )

    def _process_ufw_status_callback(self, return_code, output):
        if "Status: active" in output:
            self.ufw_status_label.config(
                text="Statut: ✅ UFW est actif.", foreground="green"
            )
        else:
            self.ufw_status_label.config(
                text="Statut: ❌ UFW est inactif. Votre système est exposé.",
                foreground="red",
            )
            if messagebox.askyesno(
                "Suggestion IA",
                "UFW est inactif. Voulez-vous l'activer avec les règles par défaut maintenant ?",
            ):
                self.activate_ufw_default()

    def update_ufw_status(self):
        self.run_command_threaded(
            "Vérification UFW",
            "sudo ufw status verbose",
            needs_sudo=True,
            callback=self._process_ufw_status_callback,
        )

    def activate_ufw_default(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous ACTIVER UFW avec les règles par défaut (refuser tout entrant, autoriser tout sortant) ?",
        ):
            self.run_command_threaded(
                "Configuration UFW: refuser entrant",
                "sudo ufw default deny incoming",
                needs_sudo=True,
            )
            self.run_command_threaded(
                "Configuration UFW: autoriser sortant",
                "sudo ufw default allow outgoing",
                needs_sudo=True,
            )
            self.run_command_threaded(
                "Activation de UFW",
                "sudo ufw enable",
                needs_sudo=True,
                callback=self._process_ufw_status_callback,
            )
            messagebox.showinfo(
                "Info",
                "UFW activé. N'oubliez pas d'ajouter des règles spécifiques si vous hébergez des services (ex: 'sudo ufw allow ssh').",
            )

    def _process_pro_status_callback(self, return_code, output):
        if "attached to an Ubuntu Pro subscription" in output:
            self.pro_status_label.config(
                text="Statut: ✅ Votre machine est attachée à Ubuntu Pro. Excellent !",
                foreground="green",
            )
        else:
            self.pro_status_label.config(
                text="Statut: ❌ Votre machine n'est PAS attachée à Ubuntu Pro.",
                foreground="red",
            )
            if messagebox.askyesno(
                "Suggestion IA",
                "Ubuntu Pro n'est pas attaché. Voulez-vous l'attacher maintenant ?",
            ):
                self.attach_ubuntu_pro()

    def update_pro_status(self):
        self.run_command_threaded(
            "Vérification Ubuntu Pro",
            "pro security-status --format text",
            callback=self._process_pro_status_callback,
        )

    def attach_ubuntu_pro(self):
        token = simpledialog.askstring(
            "Ubuntu Pro Token", "Veuillez entrer votre jeton Ubuntu Pro:"
        )
        if token:
            self.run_command_threaded(
                "Attachement Ubuntu Pro",
                f"sudo pro attach {token}",
                needs_sudo=True,
                callback=self._process_pro_status_callback,
            )
        else:
            messagebox.showwarning("Annulé", "Aucun jeton fourni. Attachement annulé.")

    def _process_backlight_status_callback(self, return_code, output):
        # Check if kbd-backlight-fix.service is active or successfully exited (oneshot)
        fix_active = "Active: active (running)" in output or (
            "Active: inactive (dead)" in output
            and "code=exited, status=0/SUCCESS" in output
        )

        # Check if original service is masked
        original_masked_proc = subprocess.run(
            "systemctl is-masked systemd-backlight@leds:dell::kbd_backlight.service",
            shell=True,
            capture_output=True,
        )
        original_masked = (
            original_masked_proc.returncode == 0
        )  # is-masked returns 0 if masked

        status_text = ""
        if fix_active:
            status_text += "Fix (kbd-backlight-fix) est en place. "
        else:
            status_text += "Fix (kbd-backlight-fix) n'est pas actif. "

        if original_masked:
            status_text += "Service original masqué. "
        else:
            status_text += "Service original NON masqué. "
            if messagebox.askyesno(
                "Suggestion IA",
                "Le service de rétroéclairage original n'est pas masqué. Voulez-vous le masquer maintenant ?",
            ):
                self.mask_original_backlight_service()

        self.backlight_status_label.config(text=f"Statut: {status_text}")
        if not fix_active or not original_masked:
            self.backlight_status_label.config(
                text=self.backlight_status_label.cget("text") + " ❌ Problème détecté.",
                foreground="red",
            )
        else:
            self.backlight_status_label.config(
                text=self.backlight_status_label.cget("text")
                + " ✅ Semble fonctionnel.",
                foreground="green",
            )

    def update_backlight_status(self):
        self.run_command_threaded(
            "Statut kbd-backlight-fix.service",
            "systemctl status kbd-backlight-fix.service --no-pager",
            callback=self._process_backlight_status_callback,
        )

    def apply_backlight_fix(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous créer et activer le service 'kbd-backlight-fix.service' pour le rétroéclairage du clavier ?",
        ):
            service_content = """[Unit]
Description=Set Keyboard Backlight Brightness on Boot
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo 1 > /sys/class/leds/dell::kbd_backlight/brightness'

[Install]
WantedBy=multi-user.target
"""
            self.run_command_threaded(
                "Création service kbd-backlight-fix",
                f'echo "{service_content}" | sudo tee /etc/systemd/system/kbd-backlight-fix.service > /dev/null',
                needs_sudo=True,
            )
            self.run_command_threaded(
                "Activation service kbd-backlight-fix",
                "sudo systemctl enable kbd-backlight-fix.service --now",
                needs_sudo=True,
                callback=self.update_backlight_status,
            )
            messagebox.showinfo(
                "Info",
                "Service de rétroéclairage créé et activé. Redémarrez pour vérifier.",
            )

    def mask_original_backlight_service(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous masquer le service original 'systemd-backlight@leds:dell::kbd_backlight.service' pour éviter les conflits ?",
        ):
            self.run_command_threaded(
                "Masquage service original",
                "sudo systemctl mask systemd-backlight@leds:dell::kbd_backlight.service",
                needs_sudo=True,
                callback=self.update_backlight_status,
            )
            messagebox.showinfo("Info", "Service original masqué.")

    def test_manual_backlight(self):
        def _test_logic():
            try:
                # Get current brightness
                result_current = subprocess.run(
                    f"sudo -S bash -c 'cat /sys/class/leds/dell::kbd_backlight/brightness'",
                    shell=True,
                    capture_output=True,
                    text=True,
                    input=self.get_sudo_password() + "\n",
                )
                if result_current.returncode == 0:
                    current_brightness = result_current.stdout.strip()
                    self.log_message(
                        f"Luminosité actuelle: {current_brightness}", "info"
                    )
                else:
                    self.log_message(
                        f"Impossible de lire la luminosité actuelle: {result_current.stderr.strip()}",
                        "error",
                    )
                    messagebox.showerror(
                        "Erreur",
                        "Impossible de lire la luminosité actuelle. Vérifiez les permissions ou l'existence du fichier.",
                    )
                    return

                if messagebox.askyesno(
                    "Test Manuel",
                    "Voulez-vous éteindre (0) puis allumer (1) le rétroéclairage pour tester ?",
                ):
                    self.log_message("Tentative d'éteindre (0)...", "info")
                    subprocess.run(
                        f"sudo -S bash -c 'echo 0 > /sys/class/leds/dell::kbd_backlight/brightness'",
                        shell=True,
                        input=self.get_sudo_password() + "\n",
                    )
                    time.sleep(1)
                    self.log_message("Tentative d'allumer (1)...", "info")
                    subprocess.run(
                        f"sudo -S bash -c 'echo 1 > /sys/class/leds/dell::kbd_backlight/brightness'",
                        shell=True,
                        input=self.get_sudo_password() + "\n",
                    )
                    messagebox.showinfo(
                        "Test Terminé", "Vérifiez si le rétroéclairage a réagi."
                    )
                else:
                    self.log_message("Test manuel annulé.", "info")
            except Exception as e:
                self.log_message(f"Erreur lors du test manuel: {e}", "error")

        threading.Thread(target=_test_logic).start()

    def _process_acpi_status_callback(self, return_code, output):
        if "ACPI Error" in output:
            self.acpi_status_label.config(
                text="Statut: ❌ Des erreurs ACPI persistent. Vérifiez les logs.",
                foreground="red",
            )
            messagebox.showwarning(
                "Suggestion IA",
                "Des erreurs ACPI persistent. Envisagez une mise à jour du BIOS ou la modification de GRUB.",
            )
        else:
            self.acpi_status_label.config(
                text="Statut: ✅ Aucune erreur ACPI critique récente détectée.",
                foreground="green",
            )

    def update_acpi_status(self):
        self.run_command_threaded(
            "Vérification erreurs ACPI",
            'sudo journalctl -k -p err | grep "ACPI Error" | tail -n 10',
            needs_sudo=True,
            callback=self._process_acpi_status_callback,
        )

    def edit_grub_config(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous ouvrir /etc/default/grub avec nano pour le modifier ? (Nécessite sudo)",
        ):
            self.run_command_threaded(
                "Ouverture GRUB avec nano",
                "sudo nano /etc/default/grub",
                needs_sudo=True,
            )
            if messagebox.askyesno(
                "Confirmer",
                "Avez-vous modifié le fichier GRUB et voulez-vous exécuter 'sudo update-grub' ?",
            ):
                self.run_command_threaded(
                    "Mise à jour GRUB", "sudo update-grub", needs_sudo=True
                )
                messagebox.showinfo(
                    "Info",
                    "GRUB mis à jour. Un redémarrage est nécessaire pour appliquer les changements.",
                )

    def _process_audio_status_callback(self, return_code, output):
        status_text = ""
        pkgs_present = False
        if "fluidsynth" in output or "jackd1" in output or "jack-mixer" in output:
            status_text += "❌ Paquets FluidSynth/JACK détectés. "
            pkgs_present = True
        else:
            status_text += "✅ Aucun paquet FluidSynth/JACK détecté. "

        ps_output = subprocess.run(
            'ps aux | grep -i "jack\\|fluid" | grep -v grep',
            shell=True,
            capture_output=True,
            text=True,
        ).stdout
        if ps_output.strip():
            status_text += "❌ Processus FluidSynth/JACK actifs. "
            if pkgs_present and messagebox.askyesno(
                "Suggestion IA",
                "Des processus FluidSynth/JACK sont actifs et les paquets sont présents. Voulez-vous les purger maintenant ?",
            ):
                self.purge_audio_packages()
            elif not pkgs_present:
                messagebox.showwarning(
                    "Attention",
                    "Des processus FluidSynth/JACK sont actifs, mais les paquets ne sont pas détectés. Cela peut indiquer des résidus ou une application qui les lance sans les paquets APT. Redémarrez ou tuez les processus manuellement.",
                )
        else:
            status_text += "✅ Aucun processus FluidSynth/JACK actif. "

        self.audio_status_label.config(text=f"Statut: {status_text}")

    def update_audio_status(self):
        self.run_command_threaded(
            "Vérification paquets/processus audio",
            "dpkg -l | grep -E 'fluidsynth|jackd1|jack-mixer'",
            callback=self._process_audio_status_callback,
        )

    def purge_audio_packages(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous purger tous les paquets FluidSynth et JACK détectés ?",
        ):
            self.run_command_threaded(
                "Purge paquets audio",
                "sudo apt purge -y fluidsynth jackd1 jack-mixer",
                needs_sudo=True,
                callback=self.update_audio_status,
            )
            messagebox.showinfo(
                "Info", "Paquets audio purgés. Redémarrez si des processus persistent."
            )

    def _process_usb_status_callback(self, return_code, output):
        if "RODE Microphones RØDE NT-USB+" in output:
            self.usb_status_label.config(
                text="Statut: ✅ RODE NT-USB+ détecté et fonctionnel (malgré l'erreur dmesg).",
                foreground="green",
            )
        else:
            self.usb_status_label.config(
                text="Statut: ❓ RODE NT-USB+ non détecté ou statut inconnu.",
                foreground="orange",
            )

    def update_usb_status(self):
        self.run_command_threaded(
            "Vérification USB RODE", "lsusb", callback=self._process_usb_status_callback
        )

    # ==============================================================================
    # TAB: Outils
    # ==============================================================================
    def create_tools_tab(self):
        frame = ttk.Frame(self.tab_tools, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame,
            text="Installation et Configuration des Outils Manquants",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        self.tools_checkboxes = {}
        self.tools_status_labels = {}
        self.tools_info = {
            "cpufrequtils": "cpufreq-info (optimisation CPU Scaling Governor)",
            "preload": "Préchargement des applications",
            "fzf": "Optimisation du terminal",
            "tlp": "TLP (gestion énergie)",
            "powertop": "PowerTOP (gestion énergie)",
            "logwatch": "Logwatch (audit logs)",
            "fail2ban": "Fail2ban (sécurité)",
            "zram-tools": "zram-tools (swap compressé)",
            "tmpwatch": "tmpwatch (nettoyage temporaires)",
            "ncdu": "ncdu (analyse espace disque)",
            "e2fsprogs": "e2fsprogs (pour e4defrag)",
            "apt-listbugs": "apt-listbugs (bugs paquets)",
            "qemu-kvm": "qemu-kvm, libvirt, virt-manager (virtualisation)",
            "rng-tools": "rng-tools (pour rngd)",
        }

        for pkg, desc in self.tools_info.items():
            tool_frame = ttk.Frame(frame)
            tool_frame.pack(fill="x", pady=2)

            var = tk.BooleanVar()
            chk = ttk.Checkbutton(
                tool_frame, text=f"{pkg} ({desc})", variable=var, state=tk.DISABLED
            )  # Checkbox is for status, not interaction
            chk.pack(side=tk.LEFT)
            self.tools_checkboxes[pkg] = var

            status_label = ttk.Label(tool_frame, text="Statut: Inconnu")
            status_label.pack(side=tk.LEFT, padx=10)
            self.tools_status_labels[pkg] = status_label

            install_btn = ttk.Button(
                tool_frame,
                text="Installer/Activer",
                command=lambda p=pkg: self.install_tool(p),
            )
            install_btn.pack(side=tk.RIGHT)

        ttk.Button(
            frame, text="Rafraîchir Statuts Outils", command=self.update_tools_status
        ).pack(pady=10)

    def update_tools_status(self):
        for pkg, label in self.tools_status_labels.items():
            if self.check_package_installed(pkg):
                label.config(text="Statut: ✅ Installé", foreground="green")
                self.tools_checkboxes[pkg].set(True)
                # Check if service needs activation
                if pkg in ["preload", "tlp", "fail2ban", "zram-tools", "rng-tools"]:
                    service_name = pkg if pkg != "rng-tools" else "rngd"
                    if (
                        subprocess.run(
                            f"systemctl is-enabled {service_name}.service",
                            shell=True,
                            capture_output=True,
                        ).returncode
                        != 0
                    ):
                        label.config(
                            text=f"Statut: ✅ Installé (Service ❌ Inactif)",
                            foreground="orange",
                        )
                    else:
                        label.config(
                            text=f"Statut: ✅ Installé (Service ✅ Actif)",
                            foreground="green",
                        )
            else:
                label.config(text="Statut: ❌ Non installé", foreground="red")
                self.tools_checkboxes[pkg].set(False)

    def install_tool(self, pkg):
        if self.check_package_installed(pkg):
            messagebox.showinfo("Info", f"{pkg} est déjà installé.")
            # Try to activate service if applicable
            if pkg in ["preload", "tlp", "fail2ban", "zram-tools", "rng-tools"]:
                service_name = pkg if pkg != "rng-tools" else "rngd"
                if (
                    subprocess.run(
                        f"systemctl is-enabled {service_name}.service",
                        shell=True,
                        capture_output=True,
                    ).returncode
                    != 0
                ):
                    if messagebox.askyesno(
                        "Confirmer",
                        f"Le service {service_name} est installé mais inactif. L'activer ?",
                    ):
                        self.run_command_threaded(
                            f"Activation service {service_name}",
                            f"sudo systemctl enable {service_name}.service --now",
                            needs_sudo=True,
                            callback=self.update_tools_status,
                        )
                else:
                    messagebox.showinfo(
                        "Info", f"Le service {service_name} est déjà actif."
                    )
            return

        if messagebox.askyesno("Confirmer", f"Voulez-vous installer {pkg} ?"):
            install_cmd = f"sudo apt install -y {pkg}"
            if pkg == "qemu-kvm":  # Install all KVM related packages
                install_cmd = "sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager"

            self.run_command_threaded(
                f"Installation de {pkg}",
                install_cmd,
                needs_sudo=True,
                callback=lambda rc, out, p=pkg: self._post_install_tool(rc, out, p),
            )
        else:
            messagebox.showinfo("Annulé", f"Installation de {pkg} annulée.")

    def _post_install_tool(self, return_code, output, pkg):
        if return_code == 0:
            self.log_message(f"SUCCÈS : {pkg} installé.", "success")
            self.update_tools_status()
            # Special post-install actions
            if pkg == "qemu-kvm":
                self.run_command_threaded(
                    "Ajout utilisateur au groupe libvirt",
                    "sudo usermod -aG libvirt toni",
                    needs_sudo=True,
                )
                self.run_command_threaded(
                    "Ajout utilisateur au groupe kvm",
                    "sudo usermod -aG kvm toni",
                    needs_sudo=True,
                )
                messagebox.showinfo(
                    "Info",
                    "KVM/QEMU installé. Un redémarrage de la session est nécessaire pour que les changements de groupe prennent effet.",
                )
            elif pkg in ["preload", "tlp", "fail2ban", "zram-tools", "rng-tools"]:
                service_name = pkg if pkg != "rng-tools" else "rngd"
                if messagebox.askyesno(
                    "Confirmer",
                    f"{pkg} installé. Voulez-vous activer son service ({service_name}) maintenant ?",
                ):
                    self.run_command_threaded(
                        f"Activation service {service_name}",
                        f"sudo systemctl enable {service_name}.service --now",
                        needs_sudo=True,
                        callback=self.update_tools_status,
                    )
        else:
            self.log_message(f"ÉCHEC : Installation de {pkg} a échoué.", "error")

    # ==============================================================================
    # TAB: Optimisations Générales
    # ==============================================================================
    def create_optimizations_tab(self):
        frame = ttk.Frame(self.tab_optimizations, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame,
            text="Optimisations & Améliorations Générales",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Snaps
        snap_frame = ttk.LabelFrame(
            frame, text="1. Nettoyage des anciennes versions de Snaps"
        )
        snap_frame.pack(fill="x", pady=5)
        ttk.Button(
            snap_frame,
            text="Lister Snaps",
            command=lambda: self.run_command_threaded(
                "Liste des Snaps", "snap list --all"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            snap_frame, text="Purger Anciens Snaps", command=self.purge_old_snaps
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Fichiers volumineux
        files_frame = ttk.LabelFrame(
            frame,
            text="2. Gestion des fichiers volumineux dans le répertoire personnel",
        )
        files_frame.pack(fill="x", pady=5)
        ttk.Label(
            files_frame,
            text="Utilisez 'ollama list' et 'ollama rm <model_name>' pour les modèles Ollama.",
        ).pack(anchor="w")
        ttk.Label(
            files_frame,
            text="Pour les environnements Python: 'rm -rf venv' ou 'conda env remove -n <env_name>'.",
        ).pack(anchor="w")
        ttk.Button(
            files_frame,
            text="Lancer ncdu /home/toni",
            command=lambda: self.run_command_threaded(
                "Analyse espace disque avec ncdu", "ncdu /home/toni"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Caches système
        cache_frame = ttk.LabelFrame(
            frame, text="3. Nettoyage des caches système (APT, vignettes)"
        )
        cache_frame.pack(fill="x", pady=5)
        ttk.Button(
            cache_frame,
            text="Nettoyer Cache APT",
            command=lambda: self.run_command_threaded(
                "Nettoyage cache APT", "sudo apt clean", needs_sudo=True
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            cache_frame,
            text="Nettoyer Cache Vignettes",
            command=lambda: self.run_command_threaded(
                "Nettoyage cache vignettes", "rm -rf ~/.cache/thumbnails/*"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # SSD noatime
        ssd_frame = ttk.LabelFrame(
            frame, text="4. Optimisation des paramètres du noyau pour les SSD (noatime)"
        )
        ssd_frame.pack(fill="x", pady=5)
        self.noatime_status_label = ttk.Label(ssd_frame, text="Statut: Chargement...")
        self.noatime_status_label.pack(anchor="w")
        ttk.Button(
            ssd_frame, text="Vérifier/Appliquer noatime", command=self.apply_noatime_ssd
        ).pack(side=tk.LEFT, padx=5, pady=2)

        ttk.Button(
            frame,
            text="Rafraîchir Tous les Statuts d'Optimisation",
            command=self.update_optimizations_status,
        ).pack(pady=10)

    def update_optimizations_status(self):
        self.update_noatime_status()

    def purge_old_snaps(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous purger toutes les anciennes révisions de Snaps (gardant les 2 plus récentes) ?",
        ):

            def _purge_logic():
                snap_list_output = subprocess.run(
                    "snap list --all", shell=True, capture_output=True, text=True
                ).stdout
                lines = snap_list_output.splitlines()[1:]  # Skip header

                snaps_to_remove = []
                for line in lines:
                    parts = line.split()
                    if (
                        len(parts) >= 3 and parts[2] == "disabled"
                    ):  # Check if it's an old revision
                        snaps_to_remove.append(
                            (parts[0], parts[1])
                        )  # snapname, revision

                if not snaps_to_remove:
                    self.log_message(
                        "Aucune ancienne révision de Snap à purger.", "info"
                    )
                    return

                for snapname, revision in snaps_to_remove:
                    self.run_command_threaded(
                        f"Suppression Snap {snapname} révision {revision}",
                        f'sudo snap remove "{snapname}" --revision="{revision}"',
                        needs_sudo=True,
                    )
                self.log_message(
                    "Nettoyage des anciennes révisions de Snaps terminé.", "success"
                )
                self.log_message(
                    "Vous pouvez également exécuter 'sudo snap refresh --hold=false --cleanup' pour un nettoyage plus général.",
                    "info",
                )

            threading.Thread(target=_purge_logic).start()
        else:
            messagebox.showinfo(
                "Annulé", "Nettoyage des anciennes révisions de Snaps annulé."
            )

    def update_noatime_status(self):
        def _callback(return_code, output):
            if "noatime" in output or "relatime" in output:
                self.noatime_status_label.config(
                    text="Statut: ✅ 'noatime' ou 'relatime' est configuré pour le SSD.",
                    foreground="green",
                )
            else:
                self.noatime_status_label.config(
                    text="Statut: ❌ 'noatime' ou 'relatime' n'est PAS configuré pour le SSD.",
                    foreground="red",
                )

        self.run_command_threaded(
            "Vérification noatime",
            "grep -E 'noatime|relatime' /etc/fstab",
            callback=_callback,
        )

    def apply_noatime_ssd(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous ajouter 'noatime' à la partition racine de votre SSD (/dev/sda2) ? (Cela réduit les écritures et prolonge la durée de vie du SSD. Nécessite un redémarrage.)",
        ):
            self.run_command_threaded(
                "Ajout de noatime à /etc/fstab",
                "sudo sed -i 's/errors=remount-ro/errors=remount-ro,noatime/' /etc/fstab",
                needs_sudo=True,
            )
            messagebox.showinfo(
                "Info",
                "L'option 'noatime' a été ajoutée. Veuillez redémarrer pour que les changements prennent effet.",
            )
            self.update_noatime_status()

    # ==============================================================================
    # TAB: Audit & Durcissement
    # ==============================================================================
    def create_hardening_tab(self):
        frame = ttk.Frame(self.tab_hardening, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame,
            text="Vision & Audit Stratégique - Mise en Œuvre Avancée",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Kernel Hardening
        kernel_frame = ttk.LabelFrame(
            frame, text="1. Durcissement du noyau (Kernel Hardening)"
        )
        kernel_frame.pack(fill="x", pady=5)
        self.ptrace_scope_label = ttk.Label(
            kernel_frame, text="kernel.yama.ptrace_scope: Chargement..."
        )
        self.ptrace_scope_label.pack(anchor="w")
        ttk.Button(
            kernel_frame,
            text="Vérifier/Activer ptrace_scope",
            command=self.check_and_set_ptrace_scope,
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Unattended Upgrades
        unattended_frame = ttk.LabelFrame(
            frame, text="2. Gestion des mises à jour automatiques (unattended-upgrades)"
        )
        unattended_frame.pack(fill="x", pady=5)
        self.unattended_status_label = ttk.Label(
            unattended_frame, text="Statut: Chargement..."
        )
        self.unattended_status_label.pack(anchor="w")
        ttk.Button(
            unattended_frame,
            text="Vérifier/Installer/Configurer",
            command=self.manage_unattended_upgrades,
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # File Permissions
        perms_frame = ttk.LabelFrame(
            frame, text="3. Audit des permissions de fichiers sensibles"
        )
        perms_frame.pack(fill="x", pady=5)
        ttk.Button(
            perms_frame,
            text="Vérifier Permissions /etc /var/log /home",
            command=lambda: self.run_command_threaded(
                "Vérification permissions", "ls -ld /etc /var/log /home"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            perms_frame,
            text="Rechercher World-Writable dans /etc",
            command=lambda: self.run_command_threaded(
                "Recherche world-writable", "find /etc -type f -perm /002 -ls"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # CPU Scaling Governor
        cpu_gov_frame = ttk.LabelFrame(
            frame, text="4. Optimisation du CPU Scaling Governor"
        )
        cpu_gov_frame.pack(fill="x", pady=5)
        ttk.Button(
            cpu_gov_frame,
            text="Afficher Gouverneur CPU",
            command=lambda: self.run_command_threaded(
                "Affichage gouverneur CPU", "cpufreq-info"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            cpu_gov_frame,
            text="Définir Gouverneur Performance (Temp)",
            command=lambda: self.run_command_threaded(
                "Définir gouverneur performance",
                "sudo cpufreq-set -g performance",
                needs_sudo=True,
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Debsums
        debsums_frame = ttk.LabelFrame(
            frame, text="5. Vérification de l'intégrité des binaires (debsums)"
        )
        debsums_frame.pack(fill="x", pady=5)
        ttk.Button(
            debsums_frame,
            text="Lancer debsums -c",
            command=lambda: self.run_command_threaded(
                "Lancement debsums", "sudo debsums -c", needs_sudo=True
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Docker Security
        docker_sec_frame = ttk.LabelFrame(
            frame, text="6. Sécurité des conteneurs Docker"
        )
        docker_sec_frame.pack(fill="x", pady=5)
        ttk.Button(
            docker_sec_frame,
            text="Nettoyer Ressources Docker (prune)",
            command=lambda: self.run_command_threaded(
                "Nettoyage Docker", "sudo docker system prune -a", needs_sudo=True
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # AppArmor
        apparmor_frame = ttk.LabelFrame(frame, text="7. Utilisation d'AppArmor/SELinux")
        apparmor_frame.pack(fill="x", pady=5)
        ttk.Button(
            apparmor_frame,
            text="Afficher Statut AppArmor",
            command=lambda: self.run_command_threaded(
                "Statut AppArmor", "sudo aa-status", needs_sudo=True
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Network Services
        net_services_frame = ttk.LabelFrame(
            frame, text="8. Audit des services réseau (ports en écoute)"
        )
        net_services_frame.pack(fill="x", pady=5)
        ttk.Button(
            net_services_frame,
            text="Ports TCP en écoute",
            command=lambda: self.run_command_threaded(
                "Ports TCP", "sudo ss -tuln | grep LISTEN", needs_sudo=True
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            net_services_frame,
            text="Ports UDP en écoute",
            command=lambda: self.run_command_threaded(
                "Ports UDP", "sudo ss -uuln", needs_sudo=True
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        ttk.Button(
            frame,
            text="Rafraîchir Tous les Statuts d'Audit",
            command=self.update_hardening_status,
        ).pack(pady=10)

    def update_hardening_status(self):
        def _ptrace_callback(return_code, output):
            if "kernel.yama.ptrace_scope = 1" in output:
                self.ptrace_scope_label.config(
                    text="kernel.yama.ptrace_scope: ✅ Activé (1)", foreground="green"
                )
            else:
                self.ptrace_scope_label.config(
                    text="kernel.yama.ptrace_scope: ❌ Inactif (0)", foreground="red"
                )

        self.run_command_threaded(
            "Vérification ptrace_scope",
            "sysctl kernel.yama.ptrace_scope",
            callback=_ptrace_callback,
        )

        def _unattended_callback(return_code, output):
            if self.check_package_installed("unattended-upgrades"):
                if (
                    'APT::Periodic::Update-Package-Lists "1";' in output
                    and 'APT::Periodic::Unattended-Upgrade "1";' in output
                ):
                    self.unattended_status_label.config(
                        text="Statut: ✅ Installé et configuré pour les mises à jour auto.",
                        foreground="green",
                    )
                else:
                    self.unattended_status_label.config(
                        text="Statut: ✅ Installé (❌ Non configuré pour les mises à jour auto).",
                        foreground="orange",
                    )
            else:
                self.unattended_status_label.config(
                    text="Statut: ❌ Non installé.", foreground="red"
                )

        self.run_command_threaded(
            "Vérification unattended-upgrades",
            "cat /etc/apt/apt.conf.d/20auto-upgrades 2>/dev/null || echo 'Non configuré'",
            callback=_unattended_callback,
        )

    def check_and_set_ptrace_scope(self):
        def _callback(return_code, output):
            if "kernel.yama.ptrace_scope = 0" in output:
                if messagebox.askyesno(
                    "Confirmer",
                    "kernel.yama.ptrace_scope est à 0. L'activer à 1 pour renforcer l'isolation des processus ?",
                ):
                    self.run_command_threaded(
                        "Activation ptrace_scope",
                        'echo "kernel.yama.ptrace_scope = 1" | sudo tee -a /etc/sysctl.d/99-sysctl.conf > /dev/null',
                        needs_sudo=True,
                    )
                    self.run_command_threaded(
                        "Application sysctl",
                        "sudo sysctl -p",
                        needs_sudo=True,
                        callback=self.update_hardening_status,
                    )
                    messagebox.showinfo(
                        "Info",
                        "kernel.yama.ptrace_scope activé. Redémarrez pour une application complète si nécessaire.",
                    )
            else:
                messagebox.showinfo(
                    "Info", "kernel.yama.ptrace_scope est déjà activé ou configuré."
                )

        self.run_command_threaded(
            "Vérification ptrace_scope",
            "sysctl kernel.yama.ptrace_scope",
            callback=_callback,
        )

    def manage_unattended_upgrades(self):
        if not self.check_package_installed("unattended-upgrades"):
            if messagebox.askyesno(
                "Confirmer", "unattended-upgrades n'est pas installé. L'installer ?"
            ):
                self.run_command_threaded(
                    "Installation unattended-upgrades",
                    "sudo apt install -y unattended-upgrades",
                    needs_sudo=True,
                    callback=self.update_hardening_status,
                )
        else:
            if messagebox.askyesno(
                "Confirmer",
                "unattended-upgrades est installé. Voulez-vous le configurer pour les mises à jour de sécurité automatiques ?",
            ):
                self.run_command_threaded(
                    "Configuration unattended-upgrades",
                    "sudo dpkg-reconfigure --priority=low unattended-upgrades",
                    needs_sudo=True,
                    callback=self.update_hardening_status,
                )
                messagebox.showinfo(
                    "Info",
                    "unattended-upgrades configuré. Vérifiez le fichier '/etc/apt/apt.conf.d/20auto-upgrades' pour les détails.",
                )

    # ==============================================================================
    # TAB: Intégration IA
    # ==============================================================================
    def create_ai_tab(self):
        frame = ttk.Frame(self.tab_ai, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame,
            text="Intégration d'Outils d'Intelligence Artificielle Gratuits et Optimisés",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Ollama
        ollama_frame = ttk.LabelFrame(
            frame, text="1. Ollama : Gestionnaire de modèles LLM locaux"
        )
        ollama_frame.pack(fill="x", pady=5)
        self.ollama_status_label = ttk.Label(ollama_frame, text="Statut: Chargement...")
        self.ollama_status_label.pack(anchor="w")
        ttk.Button(
            ollama_frame, text="Vérifier/Installer Ollama", command=self.manage_ollama
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            ollama_frame,
            text="Lister Modèles",
            command=lambda: self.run_command_threaded(
                "Liste modèles Ollama", "ollama list"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            ollama_frame,
            text="Pull Mistral (4.1GB)",
            command=lambda: self.run_command_threaded(
                "Pull Mistral", "ollama pull mistral"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            ollama_frame,
            text="Lancer Mistral (Conversation)",
            command=lambda: self.run_command_threaded(
                "Lancer Mistral", "ollama run mistral"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            ollama_frame,
            text="Pull Llama3 (8GB)",
            command=lambda: self.run_command_threaded(
                "Pull Llama3", "ollama pull llama3"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            ollama_frame,
            text="Pull Phi3 (3.8GB)",
            command=lambda: self.run_command_threaded("Pull Phi3", "ollama pull phi3"),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            ollama_frame, text="Supprimer Modèle", command=self.delete_ollama_model
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Llama.cpp
        llama_cpp_frame = ttk.LabelFrame(
            frame, text="2. Llama.cpp : Exécution de LLM sur CPU"
        )
        llama_cpp_frame.pack(fill="x", pady=5)
        self.llama_cpp_status_label = ttk.Label(
            llama_cpp_frame, text="Statut: Chargement..."
        )
        self.llama_cpp_status_label.pack(anchor="w")
        ttk.Button(
            llama_cpp_frame,
            text="Vérifier/Installer Dépendances",
            command=lambda: self.run_command_threaded(
                "Installation dépendances Llama.cpp",
                "sudo apt install -y build-essential cmake",
                needs_sudo=True,
                callback=self.update_ai_status,
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            llama_cpp_frame,
            text="Cloner & Compiler Llama.cpp",
            command=self.clone_and_compile_llama_cpp,
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Jupyter Notebooks
        jupyter_frame = ttk.LabelFrame(
            frame,
            text="3. Jupyter Notebooks : Environnement de développement IA interactif",
        )
        jupyter_frame.pack(fill="x", pady=5)
        self.jupyter_status_label = ttk.Label(
            jupyter_frame, text="Statut: Chargement..."
        )
        self.jupyter_status_label.pack(anchor="w")
        ttk.Button(
            jupyter_frame,
            text="Vérifier/Installer Jupyter",
            command=lambda: self.run_command_threaded(
                "Installation Jupyter",
                "pip install notebook",
                callback=self._process_jupyter_status_callback,
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(
            jupyter_frame,
            text="Lancer Jupyter Notebook",
            command=lambda: self.run_command_threaded(
                "Lancement Jupyter", "jupyter notebook"
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Optimisation CPU pour l'IA
        cpu_ai_frame = ttk.LabelFrame(frame, text="4. Optimisation CPU pour l'IA")
        cpu_ai_frame.pack(fill="x", pady=5)
        self.numactl_status_label = ttk.Label(
            cpu_ai_frame, text="numactl: Chargement..."
        )
        self.numactl_status_label.pack(anchor="w")
        ttk.Button(
            cpu_ai_frame,
            text="Vérifier/Installer numactl",
            command=lambda: self.run_command_threaded(
                "Installation numactl",
                "sudo apt install -y numactl",
                needs_sudo=True,
                callback=self._process_numactl_status_callback,
            ),
        ).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(
            cpu_ai_frame,
            text="Utilisez 'taskset -c 0-3' pour assigner les processus aux cœurs CPU.",
        ).pack(anchor="w")
        ttk.Button(
            cpu_ai_frame,
            text="Vérifier OpenVINO/MKL",
            command=self.check_intel_ai_optimizations,
        ).pack(side=tk.LEFT, padx=5, pady=2)

        # Vision IA
        vision_ai_frame = ttk.LabelFrame(
            frame, text="5. Vision : Projets IA locaux pour votre PC"
        )
        vision_ai_frame.pack(fill="x", pady=5)
        ttk.Label(
            vision_ai_frame,
            text="Voici des idées pour exploiter l'IA sur votre machine, en mode 'God Ultimate IA free' :",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Assistant Personnel IA Local et Privé (Ollama + RAG avec vos documents)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Génération de Code et Complétion Intelligente (VS Code + LLM local)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Analyse de Données et Rapports Automatisés (Jupyter + LLM pour interprétation)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame, text="- Création de Contenu (Texte, Idées, Scripts)"
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Base de Connaissances Personnelle Intelligente (RAG sur vos notes)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame, text="- Apprentissage et Tutorat IA (LLM comme tuteur)"
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Automatisation Système Intelligente (Python + Ollama API pour tâches complexes)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Création Artistique (Texte-Image sur CPU via InvokeAI/Automatic1111 - lent)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Interaction Vocale Locale (STT/TTS + LLM pour assistant vocal)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Vie Privée et Contrôle (avantage clé de l'IA locale)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Optimisation Continue de l'IA Locale (quantification, fine-tuning, ONNX)",
        ).pack(anchor="w")
        ttk.Label(
            vision_ai_frame,
            text="- Edge AI / TinyML (pour projets avancés sur microcontrôleurs)",
        ).pack(anchor="w")

        ttk.Button(
            frame, text="Rafraîchir Tous les Statuts IA", command=self.update_ai_status
        ).pack(pady=10)

    def update_ai_status(self):
        def _ollama_callback(return_code, output):
            if return_code == 0:
                self.ollama_status_label.config(
                    text="Statut: ✅ Ollama est installé.", foreground="green"
                )
            else:
                self.ollama_status_label.config(
                    text="Statut: ❌ Ollama n'est pas installé.", foreground="red"
                )

        self.run_command_threaded(
            "Vérification Ollama", "command -v ollama", callback=_ollama_callback
        )

        def _llama_cpp_callback(return_code, output):
            if os.path.exists(os.path.expanduser("~/llama.cpp/main")):
                self.llama_cpp_status_label.config(
                    text="Statut: ✅ Llama.cpp est cloné et compilé.",
                    foreground="green",
                )
            else:
                self.llama_cpp_status_label.config(
                    text="Statut: ❌ Llama.cpp n'est pas cloné/compilé.",
                    foreground="red",
                )

        self.run_command_threaded(
            "Vérification Llama.cpp",
            "ls -l ~/llama.cpp/main",
            callback=_llama_cpp_callback,
        )  # Dummy command to trigger callback

        self.run_command_threaded(
            "Vérification Jupyter",
            "command -v jupyter",
            callback=self._process_jupyter_status_callback,
        )
        self.run_command_threaded(
            "Vérification numactl",
            "command -v numactl",
            callback=self._process_numactl_status_callback,
        )

    def _process_jupyter_status_callback(self, return_code, output):
        if return_code == 0:
            self.jupyter_status_label.config(
                text="Statut: ✅ Jupyter Notebook est installé.", foreground="green"
            )
        else:
            self.jupyter_status_label.config(
                text="Statut: ❌ Jupyter Notebook n'est pas installé.", foreground="red"
            )

    def _process_numactl_status_callback(self, return_code, output):
        if return_code == 0:
            self.numactl_status_label.config(
                text="numactl: ✅ Installé.", foreground="green"
            )
        else:
            self.numactl_status_label.config(
                text="numactl: ❌ Non installé.", foreground="red"
            )

    def manage_ollama(self):
        if not self.check_command_exists("ollama"):
            if messagebox.askyesno(
                "Confirmer", "Ollama n'est pas installé. L'installer ?"
            ):
                self.run_command_threaded(
                    "Installation Ollama",
                    "curl -fsSL https://ollama.com/install.sh | sh",
                    callback=self.update_ai_status,
                )
                messagebox.showinfo(
                    "Info",
                    "Ollama installé. Redémarrez votre terminal et relancez cette section si vous rencontrez des problèmes.",
                )
        else:
            messagebox.showinfo("Info", "Ollama est déjà installé.")

    def delete_ollama_model(self):
        if not self.check_command_exists("ollama"):
            messagebox.showwarning("Attention", "Ollama n'est pas installé.")
            return

        model_name = simpledialog.askstring(
            "Supprimer Modèle Ollama",
            "Quel modèle Ollama voulez-vous supprimer (ex: mistral) ?",
        )
        if model_name:
            if messagebox.askyesno(
                "Confirmer Suppression",
                f"Êtes-vous sûr de vouloir supprimer le modèle '{model_name}' ?",
            ):
                self.run_command_threaded(
                    f"Suppression modèle Ollama {model_name}",
                    f"ollama rm {model_name}",
                    callback=lambda rc, out, model=model_name: self.log_message(
                        (
                            f"Modèle {model} supprimé."
                            if rc == 0
                            else f"Échec suppression modèle {model}."
                        ),
                        "success" if rc == 0 else "error",
                    ),
                )
        else:
            messagebox.showinfo("Annulé", "Suppression de modèle annulée.")

    def clone_and_compile_llama_cpp(self):
        if not self.check_package_installed(
            "build-essential"
        ) or not self.check_package_installed("cmake"):
            messagebox.showwarning(
                "Attention",
                "Les dépendances 'build-essential' et 'cmake' ne sont pas installées. Veuillez les installer d'abord via le bouton dédié.",
            )
            return

        llama_cpp_path = os.path.expanduser("~/llama.cpp")
        if not os.path.exists(llama_cpp_path):
            if messagebox.askyesno(
                "Confirmer",
                f"Voulez-vous cloner llama.cpp dans {llama_cpp_path} et le compiler ?",
            ):
                self.run_command_threaded(
                    "Clonage de llama.cpp",
                    f"git clone https://github.com/ggerganov/llama.cpp.git {llama_cpp_path}",
                    callback=lambda rc, out, path=llama_cpp_path: self._compile_llama_cpp(
                        rc, out, path
                    ),
                )
        else:
            if messagebox.askyesno(
                "Confirmer",
                f"Llama.cpp est déjà cloné dans {llama_cpp_path}. Voulez-vous le recompiler (pour les mises à jour) ?",
            ):
                self.run_command_threaded(
                    "Recompilation de llama.cpp",
                    f"cd {llama_cpp_path} && make clean && make",
                    callback=self.update_ai_status,
                )

    def _compile_llama_cpp(self, return_code, output, llama_cpp_path):
        if return_code == 0:
            self.log_message(
                "Clonage de llama.cpp réussi. Compilation en cours...", "info"
            )
            self.run_command_threaded(
                "Compilation de llama.cpp",
                f"cd {llama_cpp_path} && make",
                callback=self.update_ai_status,
            )
        else:
            self.log_message("ÉCHEC : Clonage de llama.cpp a échoué.", "error")

    def check_intel_ai_optimizations(self):
        self.log_message(
            "\n[ VÉRIFICATION ] Optimisations IA Intel (OpenVINO/MKL)", "info"
        )

        # Check OpenVINO
        if self.check_command_exists("ov_core_info"):
            self.log_message("✅ OpenVINO semble installé.", "success")
        else:
            self.log_message(
                "❌ OpenVINO n'est pas détecté. OpenVINO peut accélérer l'inférence IA sur les CPU Intel.",
                "warning",
            )
            if messagebox.askyesno(
                "Suggestion IA",
                "Voulez-vous des instructions pour installer OpenVINO ?",
            ):
                messagebox.showinfo(
                    "Instructions OpenVINO",
                    "1. Visitez le site d'Intel OpenVINO pour les instructions d'installation pour Ubuntu.\n"
                    "2. Suivez les étapes pour configurer les variables d'environnement.\n"
                    "Ceci est une installation plus complexe, mais peut offrir des gains de performance significatifs pour l'IA sur CPU.",
                )

        # Check MKL (Math Kernel Library)
        # MKL is often integrated into scientific Python libraries like NumPy/SciPy
        # A simple check is to see if Python is linked against MKL
        mkl_check_cmd = "python3 -c 'import numpy; print(numpy.__config__.show())' 2>/dev/null | grep -i 'mkl'"
        result = subprocess.run(
            mkl_check_cmd, shell=True, capture_output=True, text=True
        )
        if result.returncode == 0 and "mkl" in result.stdout.lower():
            self.log_message(
                "✅ Python semble utiliser Intel MKL pour les opérations numériques, ce qui optimise les performances IA.",
                "success",
            )
        else:
            self.log_message(
                "❌ Intel MKL ne semble pas utilisé par Python. L'installation de 'intel-mkl-rt' et la configuration des environnements Python peuvent améliorer les performances.",
                "warning",
            )
            if messagebox.askyesno(
                "Suggestion IA",
                "Voulez-vous des instructions pour optimiser Python avec MKL ?",
            ):
                messagebox.showinfo(
                    "Instructions MKL",
                    "1. Installez le paquet MKL : 'sudo apt install intel-mkl-rt'.\n"
                    "2. Pour Conda, créez un environnement avec MKL : 'conda create -n mkl_env python numpy scipy mkl'.\n"
                    "3. Pour Pip, assurez-vous que NumPy/SciPy sont compilés avec MKL (souvent le cas avec les distributions Anaconda/Miniconda).",
                )

        # Check for Intel GPU tools (for potential offloading, though limited for LLMs)
        if self.check_command_exists("intel_gpu_top"):
            self.log_message("✅ Intel GPU tools sont installés.", "success")
        else:
            self.log_message(
                "❓ Intel GPU tools ne sont pas installés. Ils peuvent être utiles pour surveiller l'utilisation de votre GPU intégré.",
                "info",
            )
            if messagebox.askyesno(
                "Suggestion IA", "Voulez-vous installer 'intel-gpu-tools' ?"
            ):
                self.run_command_threaded(
                    "Installation intel-gpu-tools",
                    "sudo apt install -y intel-gpu-tools",
                    needs_sudo=True,
                )

    # ==============================================================================
    # TAB: Vision Stratégique
    # ==============================================================================
    def create_strategic_tab(self):
        frame = ttk.Frame(self.tab_strategic, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame,
            text="Vision Stratégique et Évolution (Recommandations Futures)",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Audit et Hardening
        ttk.Label(
            frame,
            text="\n--- 6.1. Audit et Hardening du Système ---",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="1. Authentification forte (2FA/MFA) : Envisager l'activation de l'authentification à deux facteurs pour les connexions SSH ou l'accès au système (ex: `libpam-google-authenticator`).",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="2. Stratégie de sauvegarde (Backup Strategy) : Mettre en place une solution de sauvegarde robuste et automatisée pour vos données critiques (ex: BorgBackup, rsync vers un NAS/cloud). C'est crucial.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="3. Chiffrement du disque (Disk Encryption) : Si ce n'est pas déjà fait, envisager le chiffrement complet du disque pour protéger les données en cas de vol physique (LUKS).",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="4. Gestion des secrets : Pour le développement, utiliser des outils de gestion de secrets (ex: HashiCorp Vault, `pass`) plutôt que de stocker les identifiants en clair.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="5. Politique de mots de passe : Appliquer une politique de mots de passe forts et renouvelés régulièrement. Utilisez un gestionnaire de mots de passe.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="6. Désactivation des services inutiles : Examiner la liste complète des services systemd ('systemctl list-unit-files --type=service') et désactiver ceux qui ne sont absolument pas nécessaires.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="7. Surveillance de l'intégrité des fichiers (FIM) : Utiliser des outils comme AIDE ou Tripwire pour détecter les modifications non autorisées des fichiers système.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="8. Sécurité du navigateur : Utiliser des extensions de sécurité (uBlock Origin, HTTPS Everywhere) et configurer les navigateurs pour une confidentialité maximale.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="9. VPN/Proxy : Utiliser un VPN pour les connexions non sécurisées ou pour masquer votre adresse IP publique.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="10. Analyse des vulnérabilités (Vulnerability Scanning) : Utiliser des outils comme Lynis ou OpenVAS pour scanner le système à la recherche de vulnérabilités connues.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="11. Plan de réponse aux incidents : Avoir une procédure claire en cas d'incident de sécurité (compromission, perte de données).",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="12. Gestion des versions de code : Utiliser Git de manière rigoureuse pour tous vos projets, avec des dépôts distants (GitHub, GitLab).",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="13. Conteneurisation des environnements de développement : Utiliser Docker ou Podman pour isoler les projets de développement et leurs dépendances, garantissant la reproductibilité.",
        ).pack(anchor="w")

        # Performances et Expérience Utilisateur
        ttk.Label(
            frame,
            text="\n--- 6.2. Optimisation des Performances et de l'Expérience Utilisateur ---",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="1. Nettoyage des caches système : Purger régulièrement les caches APT ('sudo apt clean'), les caches des vignettes ('rm -rf ~/.cache/thumbnails/*').",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="2. Gestion des tâches Cron : Examiner les tâches cron de l'utilisateur ('crontab -l') et du système (`/etc/cron.*`) pour s'assurer qu'elles sont pertinentes et optimisées.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="3. Optimisation du démarrage des applications : Réduire le nombre d'applications lancées au démarrage de la session KDE Plasma (Paramètres Système -> Démarrage et Arrêt -> Démarrage automatique).",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="4. Optimisation des paramètres du navigateur : Configurer Chrome/Opera pour une meilleure performance et une consommation de RAM réduite (ex: suspension d'onglets, désactivation de l'accélération matérielle si problèmes).",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="5. Mise à jour des pilotes graphiques Intel : S'assurer que les pilotes i915 sont à jour via les mises à jour du noyau pour de meilleures performances graphiques. Surveillez les logs pour les erreurs i915.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="6. Optimisation des services Docker : Configurer Docker pour utiliser des pilotes de stockage optimisés et limiter les ressources des conteneurs.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="7. Gestion des polices : Supprimer les polices inutilisées pour accélérer le rendu des applications et libérer de l'espace.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="8. Personnalisation de l'environnement de bureau : Désactiver les effets visuels lourds de KDE Plasma si les performances sont un souci (Paramètres Système -> Effets de bureau).",
        ).pack(anchor="w")

        # Vision Stratégique
        ttk.Label(
            frame,
            text="\n--- 6.3. Vision Stratégique et Évolution ---",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="1. Automatisation des tâches d'administration : Développer des scripts Ansible ou des playbooks pour automatiser les configurations et les déploiements sur votre machine.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="2. Intégration CI/CD locale : Mettre en place un pipeline CI/CD léger (ex: Gitea Actions, Drone CI) pour vos projets de développement personnels.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="3. Surveillance proactive : Utiliser des outils comme Prometheus et Grafana (en local) pour visualiser les métriques de performance du système en temps réel.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="4. Apprentissage continu : Se tenir informé des dernières avancées en matière de sécurité Linux, d'optimisation des performances et des outils de développement.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="5. Contribution Open Source : Participer à des projets open source pour améliorer vos compétences et contribuer à la communauté.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="6. Documentation personnelle : Maintenir une documentation de votre configuration système, de vos scripts et de vos solutions aux problèmes rencontrés.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="7. Évaluation des besoins matériels futurs : Planifier les futures mises à niveau matérielles (ex: plus de RAM, un SSD plus grand/NVMe si possible, une carte graphique dédiée si les besoins évoluent).",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="8. Considérations sur le cloud : Évaluer l'intégration avec des services cloud pour le stockage, le calcul ou le déploiement de vos applications.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="9. Optimisation des flux de travail (Workflow Optimization) : Analyser vos habitudes de travail et identifier les goulots d'étranglement pour les automatiser ou les rationaliser.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="10. Sécurité physique : Verrouiller physiquement l'ordinateur, utiliser un mot de passe BIOS/UEFI, et protéger l'accès physique.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="11. Gestion des identités et accès (IAM) : Pour des environnements plus complexes, envisager des solutions IAM même pour un usage personnel.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="12. Veille technologique : Suivre les blogs techniques, les conférences et les communautés pour rester à la pointe des technologies.",
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="13. Gestion des règles Udev personnalisées : Pour des problèmes matériels spécifiques (comme le rétroéclairage ou certains périphériques USB), la création de règles Udev personnalisées peut offrir une solution plus robuste.",
        ).pack(anchor="w")

        ttk.Button(
            frame,
            text="Retour au Menu Principal",
            command=lambda: self.notebook.select(self.tab_overview),
        ).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemAnalyzerApp(root)
    root.mainloop()
