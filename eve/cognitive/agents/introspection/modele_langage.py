# -*- coding: utf-8 -*-
"""
modele_langage.py (v1.1 - Gestion des textes courts)

Gère le chargement et l'utilisation d'un modèle de langage (NLP)
pour analyser et résumer le contenu du code source.
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# --- Configuration du Modèle ---
MODEL_NAME = "facebook/bart-large-cnn"

class ModeleAnalyseCode:
    """
    Encapsule le modèle NLP pour garantir qu'il n'est chargé qu'une seule fois.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("[NLP] Création d'une nouvelle instance du modèle de langage.")
            cls._instance = super(ModeleAnalyseCode, cls).__new__(cls)
            cls._instance.initialiser_modele()
        return cls._instance

    def initialiser_modele(self):
        """
        Charge le tokenizer et le modèle depuis Hugging Face.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[NLP] Utilisation du périphérique : {self.device.upper()}")

        try:
            print(f"[NLP] Chargement du tokenizer '{MODEL_NAME}'...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

            print(f"[NLP] Chargement du modèle '{MODEL_NAME}'...")
            model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

            self.summarizer = pipeline(
                "summarization",
                model=model,
                tokenizer=tokenizer,
                device=self.device
            )
            print("[NLP] Modèle de langage prêt.")

        except Exception as e:
            print(f"[ERREUR NLP] Impossible de charger le modèle : {e}")
            self.summarizer = None

    def resumer_code(self, code_text: str) -> str:
        """
        Génère un résumé intelligent du code fourni.
        """
        if not self.summarizer:
            return "Le modèle NLP n'est pas disponible."

        try:
            # On compte le nombre de "mots" (tokens) pour éviter les erreurs
            nombre_tokens = len(self.summarizer.tokenizer.encode(code_text))

            min_input_length = 50

            if nombre_tokens < min_input_length:
                return "Le code est trop court pour générer un résumé pertinent."

            max_length = 150
            min_length = 25

            summary = self.summarizer(
                code_text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )

            return summary[0]['summary_text']
        except Exception as e:
            # On capture les erreurs spécifiques au modèle comme 'index out of range'
            return f"Erreur lors de la génération du résumé : {e}"
