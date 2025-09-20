# ALMA_BASE_DIR/Outils/cedille_interface.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import logging
import platform # Pour des informations système si besoin à l'avenir
import sys # <--- CORRECTION : Import de sys

# --- Configuration du Logger ---
logger = logging.getLogger("ALMA.CedilleInterface")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)-7s - [%(threadName)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False

# --- Import des bibliothèques ML ---
TRANSFORMERS_AVAILABLE = False
HF_AutoTokenizer = None
HF_AutoModelForCausalLM = None

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    HF_AutoTokenizer = AutoTokenizer
    HF_AutoModelForCausalLM = AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
    logger.info("Bibliothèques Transformers (AutoTokenizer, AutoModelForCausalLM) chargées.")
except ImportError as e_transformers:
    logger.error(f"Échec de l'import de 'transformers': {e_transformers}. Veuillez l'installer ('pip install transformers torch').")
except Exception as e_gen_import:
    logger.error(f"Erreur inattendue lors de l'import des bibliothèques ML: {e_gen_import}")


class CedilleApp(tk.Tk):
    """TODO: Add docstring."""
    AVAILABLE_MODELS = {
        "GPT-2 French Small (dbddv01)": "dbddv01/gpt2-french-small",
        "Cédille Small (Coddity)": "Coddity/Cedille-small-6k",
        "Cédille (Benchlab - Gated?)": "benchlab/cedille",
    }
    DEFAULT_MODEL_KEY = "GPT-2 French Small (dbddv01)"

    """TODO: Add docstring."""
    def __init__(self):
        super().__init__()
        self.title("Interface Cédille ALMA")
        self.geometry("700x550")
        self.minsize(600, 450)

        self.tokenizer = None
        self.model = None
        # Initialisation de model_var ici, même si le combobox est optionnel
        self.model_var = tk.StringVar(value=self.DEFAULT_MODEL_KEY) # <--- CORRECTION : Initialisation
        self.current_model_id = self.AVAILABLE_MODELS[self.DEFAULT_MODEL_KEY]
        self.model_loaded = False
        self.model_loading_in_progress = False

        if not TRANSFORMERS_AVAILABLE:
            logger.critical("Transformers non disponible. L'application ne peut pas démarrer.")
            self.after(100, self.destroy)
            return

        self._setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        logger.info("Interface Cédille initialisée.")
            """TODO: Add docstring."""

    def _setup_ui(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Section de Sélection du Modèle ---
        model_frame = ttk.LabelFrame(self.main_frame, text="Modèle Cédille")
        model_frame.pack(pady=10, fill=tk.X, padx=5)
        # self.model_var est déjà initialisé dans __init__
        model_selector = ttk.Combobox(model_frame, textvariable=self.model_var,
                                      values=list(self.AVAILABLE_MODELS.keys()), state="readonly",
                                      font=("Segoe UI", 9))
        model_selector.pack(side=tk.LEFT, padx=5, pady=5)
        model_selector.bind("<<ComboboxSelected>>", self.on_model_select)

        input_frame = ttk.LabelFrame(self.main_frame, text="Votre Prompt")
        input_frame.pack(pady=10, fill=tk.X, padx=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, height=6, width=80, wrap=tk.WORD,
                                                    font=("Segoe UI", 10))
        self.input_text.pack(pady=5, padx=5, fill=tk.X, expand=True)

        self.generate_button = ttk.Button(self.main_frame, text="Générer avec Cédille",
                                          command=self.start_generation_thread, style="Accent.TButton")
        self.generate_button.pack(pady=10)
        if not TRANSFORMERS_AVAILABLE: # S'assurer qu'il est désactivé si l'import a échoué
            self.generate_button.config(state=tk.DISABLED)


        output_frame = ttk.LabelFrame(self.main_frame, text="Réponse de Cédille")
        output_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80, wrap=tk.WORD,
                                                     state=tk.DISABLED, font=("Segoe UI", 10))
        self.output_text.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value=f"Modèle '{self.model_var.get()}' non chargé. Cliquez sur 'Générer'.")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_label.pack(pady=(10,5), fill=tk.X, padx=5)

        style = ttk.Style()
            """TODO: Add docstring."""
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=5)

    def on_model_select(self, event=None):
        selected_key = self.model_var.get() # self.model_var est maintenant défini
        new_model_id = self.AVAILABLE_MODELS.get(selected_key)
        if new_model_id and new_model_id != self.current_model_id:
            logger.info(f"Changement de modèle demandé : de '{self.current_model_id}' à '{new_model_id}'")
            self.current_model_id = new_model_id
            self.model = None
            self.tokenizer = None
            self.model_loaded = False
            self._update_status(f"Modèle '{selected_key}' sélectionné. Cliquez sur 'Générer' pour charger.")
                """TODO: Add docstring."""
        elif not new_model_id:
            logger.warning(f"Clé de modèle sélectionnée inconnue : {selected_key}")

    def _update_status(self, message: str, is_error: bool = False):
        """TODO: Add docstring."""
        self.status_var.set(message)
        self.status_label.config(foreground="red" if is_error else "")
        self.update_idletasks()

    def load_model_if_needed(self):
        if self.model_loaded or self.model_loading_in_progress:
            return self.model_loaded

        self.model_loading_in_progress = True
        self.generate_button.config(state=tk.DISABLED)
        self._update_status(f"Chargement du modèle '{self.current_model_id}' en cours...")
        logger.info(f"Début du chargement du modèle : {self.current_model_id}")

        try:
            if not HF_AutoTokenizer or not HF_AutoModelForCausalLM:
                raise ImportError("Les classes AutoTokenizer ou AutoModelForCausalLM de Transformers ne sont pas chargées.")
            self.tokenizer = HF_AutoTokenizer.from_pretrained(self.current_model_id)
            self.model = HF_AutoModelForCausalLM.from_pretrained(self.current_model_id)
            self.model_loaded = True
            logger.info(f"Modèle '{self.current_model_id}' et tokenizer chargés avec succès.")
            self._update_status(f"Modèle '{self.current_model_id}' chargé. Prêt à générer.")
        except ImportError as e_imp:
            logger.critical(f"Erreur d'import critique lors du chargement du modèle: {e_imp}", exc_info=True)
            messagebox.showerror("Erreur Critique", f"Dépendance Transformers manquante ou corrompue:\n{e_imp}")
            self._update_status(f"Erreur critique de dépendance Transformers.", is_error=True)
            self.model_loaded = False
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle '{self.current_model_id}': {e}", exc_info=True)
            messagebox.showerror("Erreur Modèle", f"Impossible de charger le modèle '{self.current_model_id}':\n{e}")
            self._update_status(f"Erreur de chargement du modèle '{self.current_model_id}'.", is_error=True)
            self.model_loaded = False
        finally:
            self.model_loading_in_progress = False
            # Réactiver le bouton seulement si transformers est disponible ET si le chargement n'est plus en cours
            # La logique de réactivation est mieux gérée dans _generation_task_with_button_re_enable
                """TODO: Add docstring."""
            if not self.model_loaded: # Si le chargement a échoué
                 self.generate_button.config(state=tk.NORMAL if TRANSFORMERS_AVAILABLE else tk.DISABLED)

        return self.model_loaded

    def generate_text_sync(self):
        if not self.load_model_if_needed():
            # Si le chargement a échoué, load_model_if_needed aura déjà réactivé le bouton si approprié
            return

        # <--- CORRECTION : Vérifier que tokenizer et model sont chargés ---
        if not self.tokenizer or not self.model:
            logger.error("Tokenizer ou Modèle non initialisé avant la génération.")
            self._update_status("Erreur : Tokenizer ou Modèle non prêt.", is_error=True)
            messagebox.showerror("Erreur Interne", "Le tokenizer ou le modèle n'a pas pu être initialisé correctement.")
            return

        prompt = self.input_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Entrée Manquante", "Veuillez entrer un texte pour la génération.")
            return

        self._update_status("Génération en cours...")
        logger.info(f"Début de la génération pour le prompt : \"{prompt[:50]}...\"")

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            outputs = self.model.generate( # <--- Accès à self.model.generate
                **inputs,
                max_new_tokens=150,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id, # <--- Accès à self.tokenizer.eos_token_id
                eos_token_id=self.tokenizer.eos_token_id, # <--- Accès à self.tokenizer.eos_token_id
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7,
                no_repeat_ngram_size=3
            )
            generated_text_only = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True) # <--- Accès à self.tokenizer.decode
            full_generated_text = prompt + " " + generated_text_only # Ajout d'un espace

            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, full_generated_text)
            self.output_text.config(state=tk.DISABLED)
            self._update_status("Génération terminée.")
            logger.info(f"Texte généré avec succès. Longueur de la réponse : {len(generated_text_only)} char.")
                """TODO: Add docstring."""

        except Exception as e:
            logger.error(f"Erreur lors de la génération de texte: {e}", exc_info=True)
            messagebox.showerror("Erreur Génération", f"Une erreur est survenue lors de la génération:\n{e}")
                """TODO: Add docstring."""
            self._update_status("Erreur de génération.", is_error=True)

    def start_generation_thread(self):
        self.generate_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._generation_task_with_button_re_enable, daemon=True)
        thread.start()
            """TODO: Add docstring."""

    def _generation_task_with_button_re_enable(self):
        try:
            self.generate_text_sync()
        finally:
            if hasattr(self, 'after') and self.winfo_exists(): # Vérifier si la fenêtre existe encore
                self.after(0, lambda: self.generate_button.config(state=tk.NORMAL))

    def on_closing(self):
        logger.info("Fermeture de l'interface Cédille demandée.")
        if self.model_loading_in_progress:
            if messagebox.askyesno("Chargement en Cours",
                                   "Le modèle est en cours de chargement. Voulez-vous vraiment quitter ?"):
                logger.warning("Fermeture pendant le chargement du modèle.")
                self.destroy()
            else:
                return
        self.destroy()
        logger.info("Interface Cédille fermée.")

if __name__ == "__main__":
    if not TRANSFORMERS_AVAILABLE:
        try:
            root_err = tk.Tk()
            root_err.withdraw()
            messagebox.showerror("Erreur Dépendance Critique",
                                 "La bibliothèque 'transformers' est manquante.\n"
                                 "L'interface Cédille ne peut pas fonctionner.\n\n"
                                 "Veuillez l'installer dans l'environnement ALMA:\n"
                                 "pip install transformers torch", parent=None)
            root_err.destroy()
        except tk.TclError:
            print("CRITICAL ERROR: Transformers library is missing AND Tkinter error occurred.", file=sys.stderr) # <--- Utilisation de sys
        sys.exit(1) # <--- Utilisation de sys
    else:
        try:
            app = CedilleApp()
            app.mainloop()
        except Exception as e_main:
            logger.critical(f"Erreur non interceptée dans le mainloop de CedilleApp: {e_main}", exc_info=True)
            try:
                root_fatal = tk.Tk()
                root_fatal.withdraw()
                messagebox.showerror("Erreur Fatale - Interface Cédille",
                                     f"Une erreur fatale est survenue:\n{e_main}\n\nConsultez les logs pour plus de détails.",
                                     parent=None)
                root_fatal.destroy()
            except: # NOSONAR
                pass
            sys.exit(1) # <--- Utilisation de sys