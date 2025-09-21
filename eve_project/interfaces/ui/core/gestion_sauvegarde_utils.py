import pickle
import zipfile
import json
import time
from pathlib import Path
from datetime import datetime


class ValidateurSauvegarde:
    """Utilitaires de validation pour le système de sauvegarde."""

    @staticmethod
    def valider_cerveau(cerveau) -> bool:
        """Valide qu'un objet cerveau est sérialisable."""
        try:
            pickle.dumps(cerveau, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception:
            return False

    @staticmethod
    def valider_taille_archive(chemin: Path, limite_mo: int = 100) -> bool:
        """Valide que l'archive ne dépasse pas la taille limite."""
        try:
            if not chemin.exists():
                return True
            taille_mo = chemin.stat().st_size / (1024 * 1024)
            return taille_mo <= limite_mo
        except Exception:
            return False

    @staticmethod
    def tester_integrite_archive(chemin: Path) -> bool:
        """Teste l'intégrité d'une archive ZIP."""
        try:
            with zipfile.ZipFile(chemin, "r") as zipf:
                return zipf.testzip() is None
        except Exception:
            return False


class GenerateurMetadata:
    """Génère les métadonnées des sauvegardes."""

    @staticmethod
    def creer_metadata(cerveau, auto_checkpoint: bool = False) -> dict:
        """Crée les métadonnées d'une sauvegarde."""
        return {
            "version": "1.0",
            "timestamp": time.time(),
            "date_creation": datetime.now().isoformat(),
            "mode_actuel": getattr(cerveau, "mode_actuel", "INCONNU"),
            "phase_de_vie": getattr(cerveau.comportement, "phase_de_vie", "INCONNUE"),
            "concepts_appris": len(
                cerveau.modele_monde.graphe_connaissances.get("noeuds", {})
            ),
            "auto_checkpoint": auto_checkpoint,
        }

    @staticmethod
    def extraire_metadata_archive(chemin: Path) -> dict:
        """Extrait les métadonnées d'une archive."""
        try:
            with zipfile.ZipFile(chemin, "r") as zipf:
                if "metadata.json" in zipf.namelist():
                    with zipf.open("metadata.json") as f:
                        return json.load(f)
            return {}
        except Exception:
            return {}


class ArchiveurLogs:
    """Gère l'archivage des logs avec les sauvegardes."""

    @staticmethod
    def archiver_logs_recents(dossier_temp: Path):
        """Archive les 1000 dernières lignes de chaque log."""
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return

        dossier_logs_temp = dossier_temp / "logs"
        dossier_logs_temp.mkdir(exist_ok=True)

        for log_file in logs_dir.glob("*.log"):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lignes = f.readlines()

                lignes_recentes = lignes[-1000:] if len(lignes) > 1000 else lignes

                with open(
                    dossier_logs_temp / log_file.name, "w", encoding="utf-8"
                ) as f:
                    f.writelines(lignes_recentes)
            except Exception:
                continue
