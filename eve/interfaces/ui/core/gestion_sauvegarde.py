import zipfile
import json
import pickle
import time
from pathlib import Path
import shutil
from gestion_sauvegarde_utils import (
    ValidateurSauvegarde,
    GenerateurMetadata,
    ArchiveurLogs,
)


class GestionnaireSauvegarde:
    """
    Système de sauvegarde et chargement robuste.
    Implémente les Directives 82 et 49.
    """

    def __init__(self, dossier_sauvegardes="sauvegardes"):
        self.dossier_sauvegardes = Path(dossier_sauvegardes)
        self.dossier_sauvegardes.mkdir(exist_ok=True)
        self.dossier_checkpoints = self.dossier_sauvegardes / "checkpoints"
        self.dossier_checkpoints.mkdir(exist_ok=True)

    def sauvegarder_etat(self, cerveau, nom_sauvegarde=None, auto_checkpoint=False):
        """Sauvegarde l'état complet du cerveau."""
        try:
            if not ValidateurSauvegarde.valider_cerveau(cerveau):
                print("ERREUR: Cerveau non sérialisable")
                return None

            if nom_sauvegarde is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                nom_sauvegarde = (
                    f"{'checkpoint' if auto_checkpoint else 'sauvegarde'}_{timestamp}"
                )

            dossier_cible = (
                self.dossier_checkpoints
                if auto_checkpoint
                else self.dossier_sauvegardes
            )
            chemin_sauvegarde = dossier_cible / f"{nom_sauvegarde}.zip"
            return self._creer_archive(cerveau, chemin_sauvegarde, auto_checkpoint)

        except (OSError, pickle.PicklingError) as e:
            print(f"ERREUR lors de la sauvegarde: {e}")
            return None
            return None

    def _creer_archive(self, cerveau, chemin_sauvegarde, auto_checkpoint):
        """Crée l'archive de sauvegarde."""
        dossier_temp = Path("temp_sauvegarde")
        dossier_temp.mkdir(exist_ok=True)
        try:
            # Sauvegarde du cerveau
            with open(dossier_temp / "cerveau.pkl", "wb") as f:
                pickle.dump(cerveau, f, protocol=pickle.HIGHEST_PROTOCOL)

            # Métadonnées
            # Métadonnées
            metadata = GenerateurMetadata.creer_metadata(cerveau, auto_checkpoint)
            with open(dossier_temp / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # Logs récents
            ArchiveurLogs.archiver_logs_recents(dossier_temp)

            # Création de l'archive
            with zipfile.ZipFile(chemin_sauvegarde, "w", zipfile.ZIP_DEFLATED) as zipf:
                for fichier in dossier_temp.rglob("*"):
                    if fichier.is_file():
                        zipf.write(fichier, fichier.relative_to(dossier_temp))

            if auto_checkpoint:
                self._nettoyer_anciens_checkpoints()

            print(f"✓ Sauvegarde créée: {chemin_sauvegarde}")
            return str(chemin_sauvegarde)

        finally:
            shutil.rmtree(dossier_temp, ignore_errors=True)

    def charger_etat(self, chemin_sauvegarde):
        """Charge un état depuis une sauvegarde."""
        try:
            chemin_sauvegarde = Path(chemin_sauvegarde)
            if not chemin_sauvegarde.exists():
                print(f"ERREUR: Fichier introuvable: {chemin_sauvegarde}")
                return None

            if not ValidateurSauvegarde.tester_integrite_archive(chemin_sauvegarde):
                print("ERREUR: Archive corrompue")
                return None

            return self._extraire_cerveau(chemin_sauvegarde)

        except Exception as e:
            print(f"ERREUR lors du chargement: {e}")
            return None

    def _extraire_cerveau(self, chemin_sauvegarde):
        """Extrait le cerveau d'une archive."""
        dossier_temp = Path("temp_chargement")
        dossier_temp.mkdir(exist_ok=True)

        try:
            with zipfile.ZipFile(chemin_sauvegarde, "r") as zipf:
                zipf.extractall(dossier_temp)

            metadata = GenerateurMetadata.extraire_metadata_archive(chemin_sauvegarde)
            if metadata:
                print(
                    f"Chargement sauvegarde du {metadata.get('date_creation', 'inconnue')}"
                )

            cerveau_path = dossier_temp / "cerveau.pkl"
            cerveau_path = dossier_temp / "cerveau.pkl"
            if cerveau_path.exists():
                with open(cerveau_path, "rb") as f:
                    cerveau = pickle.load(f)
                return cerveau

            return None

        finally:
            shutil.rmtree(dossier_temp, ignore_errors=True)

    def lister_sauvegardes(self):
        """Liste toutes les sauvegardes disponibles."""
        sauvegardes = []
        for fichier in self.dossier_sauvegardes.glob("*.zip"):
            try:
                metadata = GenerateurMetadata.extraire_metadata_archive(fichier)
                sauvegardes.append(
                    {
                        "fichier": str(fichier),
                        "nom": fichier.stem,
                        "date": metadata.get("date_creation", "Inconnue"),
                        "concepts": metadata.get("concepts_appris", 0),
                        "phase": metadata.get("phase_de_vie", "Inconnue"),
                    }
                )
            except:
                continue

        return sorted(sauvegardes, key=lambda x: x["date"], reverse=True)

    def _nettoyer_anciens_checkpoints(self):
        """Garde seulement les 10 checkpoints les plus récents."""
        checkpoints = list(self.dossier_checkpoints.glob("checkpoint_*.zip"))
        checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        for ancien_checkpoint in checkpoints[10:]:
            try:
                ancien_checkpoint.unlink()
            except:
                continue


gestionnaire_sauvegarde = GestionnaireSauvegarde()


def sauvegarder_etat(cerveau, nom_sauvegarde=None):
    return gestionnaire_sauvegarde.sauvegarder_etat(cerveau, nom_sauvegarde)


def charger_etat(chemin_sauvegarde):
    return gestionnaire_sauvegarde.charger_etat(chemin_sauvegarde)


def checkpoint_automatique(cerveau):
    return gestionnaire_sauvegarde.sauvegarder_etat(cerveau, auto_checkpoint=True)
