import sys
import os
import subprocess
import threading
import uuid
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# --- Configuration Ollama ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# --- Configuration des Chemins ---
CREW_A_PATH = os.getenv("CREW_A_PATH", "crew_a")
CREW_B_PATH = os.getenv("CREW_B_PATH", "crew_b")
MODULE_A_NAME = "eve_genesis___crew_a_construction_eveil"
MODULE_B_NAME = "eve_genesis___crew_b"

# --- Configuration des Logs ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Base de Données en Mémoire ---
tasks_status: Dict[str, Dict[str, Any]] = {}

# --- Initialisation de l'API FastAPI ---
app = FastAPI(
    title="EVE GENESIS Orchestrator API - Ollama Edition",
    description="API d'orchestration pour le système EVE GENESIS utilisant Ollama",
    version="1.0.0",
)

# Middleware CORS pour permettre les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def setup_ollama_environment():
    """Configure l'environnement pour utiliser Ollama."""
    env_vars = {
        "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
        "OLLAMA_MODEL": OLLAMA_MODEL,
        "USE_OLLAMA": "true",
        "DISABLE_OPENAI": "true",
    }

    for key, value in env_vars.items():
        os.environ[key] = value
        logger.info(f"Variable d'environnement définie: {key}={value}")


def check_ollama_availability():
    """Vérifie si Ollama est accessible."""
    try:
        import requests

        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            logger.info("Ollama est accessible et fonctionne")
            return True
        else:
            logger.warning(f"Ollama répond avec le code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Impossible de contacter Ollama: {e}")
        return False


def run_crew(crew_path: str, module_name: str, crew_name: str, task_id: str) -> bool:
    """
    Exécute un crew avec l'environnement Ollama configuré.
    """
    original_directory = os.getcwd()

    try:
        # Configuration de l'environnement Ollama
        setup_ollama_environment()

        # Changement vers le répertoire du crew
        os.chdir(crew_path)

        # Vérification que le module existe
        module_path = f"src/{module_name}/main.py"
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Module non trouvé: {module_path}")

        command = [sys.executable, module_path, "run"]
        logger.info(f"Exécution de {crew_name}: {' '.join(command)}")

        # Mise à jour du statut
        tasks_status[task_id]["details"] = f"Exécution de {crew_name} en cours..."

        # Exécution avec timeout
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=3600,  # Timeout de 1 heure
        )

        # Gestion des résultats
        if result.returncode != 0:
            error_details = f"Échec de {crew_name} (code: {result.returncode})\n"
            error_details += "=== STDOUT ===\n"
            error_details += result.stdout or "Aucune sortie standard\n"
            error_details += "\n=== STDERR ===\n"
            error_details += result.stderr or "Aucune erreur standard\n"

            logger.error(error_details)
            tasks_status[task_id].update(
                {"status": "failed", "details": error_details, "crew": crew_name}
            )
            return False

        # Succès
        success_message = f"{crew_name} terminé avec succès"
        logger.info(success_message)

        # Sauvegarde des logs de sortie (tronqués)
        stdout_preview = (
            result.stdout[:1000] + "..." if len(result.stdout) > 1000 else result.stdout
        )
        tasks_status[task_id][
            "details"
        ] = f"{success_message}\nSortie: {stdout_preview}"

        return True

    except subprocess.TimeoutExpired:
        error_msg = f"Timeout atteint pour {crew_name} (>1h)"
        logger.error(error_msg)
        tasks_status[task_id].update(
            {"status": "failed", "details": error_msg, "crew": crew_name}
        )
        return False

    except Exception as e:
        error_msg = f"Erreur critique lors de l'exécution de {crew_name}: {str(e)}"
        logger.error(error_msg)
        tasks_status[task_id].update(
            {"status": "failed", "details": error_msg, "crew": crew_name}
        )
        return False

    finally:
        os.chdir(original_directory)


def run_full_sequence(task_id: str):
    """
    Exécute la séquence complète Crew A -> Crew B avec Ollama.
    """
    logger.info(f"[{task_id}] Démarrage de la séquence EVE GENESIS")

    # Vérification initiale d'Ollama
    if not check_ollama_availability():
        tasks_status[task_id].update(
            {
                "status": "failed",
                "details": "Ollama n'est pas accessible. Vérifiez qu'Ollama est démarré.",
            }
        )
        return

    tasks_status[task_id].update(
        {
            "status": "running",
            "details": "Initialisation - Vérification d'Ollama réussie",
            "progress": 0,
        }
    )

    # Étape 1: Crew A (Construction & Éveil)
    logger.info(f"[{task_id}] Phase 1: Exécution du Crew A (Construction & Éveil)")
    tasks_status[task_id].update(
        {
            "details": "Phase 1: Crew A (Construction & Éveil) en cours...",
            "progress": 10,
        }
    )

    if not run_crew(CREW_A_PATH, MODULE_A_NAME, "Crew A", task_id):
        logger.error(f"[{task_id}] Échec du Crew A - Arrêt de la séquence")
        return

    # Étape 2: Crew B (Enrichissement & Évolution)
    logger.info(
        f"[{task_id}] Phase 2: Exécution du Crew B (Enrichissement & Évolution)"
    )
    tasks_status[task_id].update(
        {
            "details": "Phase 2: Crew B (Enrichissement & Évolution) en cours...",
            "progress": 60,
        }
    )

    if not run_crew(CREW_B_PATH, MODULE_B_NAME, "Crew B", task_id):
        logger.error(f"[{task_id}] Échec du Crew B - Arrêt de la séquence")
        return

    # Finalisation
    tasks_status[task_id].update(
        {
            "status": "completed",
            "details": "Séquence EVE GENESIS terminée avec succès ! EVE est maintenant opérationnelle.",
            "progress": 100,
        }
    )
    logger.info(f"[{task_id}] Séquence EVE GENESIS terminée avec succès")


@app.get("/")
def root():
    """Point d'entrée racine de l'API."""
    return {
        "message": "EVE GENESIS Orchestrator API - Ollama Edition",
        "version": "1.0.0",
        "ollama_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "status": "operational",
    }


@app.get("/health")
def health_check():
    """Vérification de santé de l'API et d'Ollama."""
    ollama_status = check_ollama_availability()
    return {
        "api_status": "healthy",
        "ollama_status": "available" if ollama_status else "unavailable",
        "ollama_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL,
    }


@app.post("/start_eve_genesis")
def start_sequence():
    """
    Démarre la séquence complète EVE GENESIS avec Ollama.
    """
    # Vérification préalable d'Ollama
    if not check_ollama_availability():
        raise HTTPException(
            status_code=503,
            detail="Ollama n'est pas accessible. Vérifiez qu'Ollama est démarré et accessible.",
        )

    task_id = str(uuid.uuid4())
    tasks_status[task_id] = {
        "status": "pending",
        "details": "Séquence en attente de démarrage...",
        "progress": 0,
        "created_at": str(uuid.uuid1().time),
    }

    # Lancement asynchrone
    thread = threading.Thread(target=run_full_sequence, args=(task_id,))
    thread.daemon = True  # Thread daemon pour éviter les blocages
    thread.start()

    logger.info(f"Nouvelle séquence EVE GENESIS démarrée: {task_id}")

    return {
        "message": "Séquence EVE GENESIS démarrée avec Ollama",
        "task_id": task_id,
        "ollama_model": OLLAMA_MODEL,
        "status_url": f"/status/{task_id}",
    }


@app.get("/status/{task_id}")
def get_status(task_id: str):
    """
    Récupère le statut d'une tâche en cours.
    """
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail=f"Tâche {task_id} non trouvée")

    return tasks_status[task_id]


@app.get("/tasks")
def list_tasks():
    """
    Liste toutes les tâches en cours et terminées.
    """
    return {"total_tasks": len(tasks_status), "tasks": tasks_status}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    """
    Supprime une tâche de l'historique.
    """
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail=f"Tâche {task_id} non trouvée")

    del tasks_status[task_id]
    return {"message": f"Tâche {task_id} supprimée"}


if __name__ == "__main__":
    print("=" * 60)
    print("EVE GENESIS Orchestrator API - Ollama Edition")
    print("=" * 60)
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print(f"Modèle: {OLLAMA_MODEL}")
    print("=" * 60)

    # Vérification initiale d'Ollama
    if check_ollama_availability():
        print("✅ Ollama est accessible")
    else:
        print("❌ Ollama n'est pas accessible")
        print("   Assurez-vous qu'Ollama est démarré avec: ollama serve")

    print("🚀 Démarrage du serveur API...")
    print("📖 Documentation: http://127.0.0.1:8000/docs")
    print("🔍 Santé: http://127.0.0.1:8000/health")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
