#!/usr/bin/env python
import sys
import os
import logging
import time
from typing import Dict, Any
from eve_genesis___crew_a_construction_eveil.crew import (
    EveGenesisCrewALIngenieurAdaptatifSupervisable41AgentsCrew,
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration Ollama par défaut
OLLAMA_CONFIG = {
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "model": os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
    "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
    "timeout": int(os.getenv("OLLAMA_TIMEOUT", "300")),
}


def setup_ollama_environment():
    """Configure l'environnement pour utiliser Ollama au lieu d'OpenAI."""
    ollama_env = {
        "OLLAMA_BASE_URL": OLLAMA_CONFIG["base_url"],
        "OLLAMA_MODEL": OLLAMA_CONFIG["model"],
        "OLLAMA_TEMPERATURE": str(OLLAMA_CONFIG["temperature"]),
        "OLLAMA_TIMEOUT": str(OLLAMA_CONFIG["timeout"]),
        "USE_OLLAMA": "true",
        "DISABLE_OPENAI": "true",
        "LLM_PROVIDER": "ollama",
        # Désactiver les clés OpenAI pour forcer l'utilisation d'Ollama
        "OPENAI_API_KEY": "",
        "OPENAI_API_BASE": "",
    }

    for key, value in ollama_env.items():
        os.environ[key] = value
        logger.debug(f"Variable d'environnement configurée: {key}={value}")

    logger.info(f"Configuration Ollama activée - Modèle: {OLLAMA_CONFIG['model']}")


def check_ollama_availability():
    """Vérifie si Ollama est accessible avant de lancer le crew."""
    try:
        import requests

        # Test de connectivité de base
        response = requests.get(f"{OLLAMA_CONFIG['base_url']}/api/tags", timeout=10)

        if response.status_code != 200:
            logger.error(f"Ollama répond avec le code d'erreur: {response.status_code}")
            return False

        # Vérifier que le modèle requis est disponible
        models_data = response.json()
        available_models = [
            model.get("name", "") for model in models_data.get("models", [])
        ]

        if OLLAMA_CONFIG["model"] not in available_models:
            logger.warning(f"Modèle {OLLAMA_CONFIG['model']} non trouvé")
            logger.info(f"Modèles disponibles: {', '.join(available_models)}")

            # Tenter de télécharger le modèle automatiquement
            logger.info(
                f"Tentative de téléchargement du modèle {OLLAMA_CONFIG['model']}..."
            )
            pull_response = requests.post(
                f"{OLLAMA_CONFIG['base_url']}/api/pull",
                json={"name": OLLAMA_CONFIG["model"]},
                timeout=600,  # 10 minutes pour le téléchargement
            )

            if pull_response.status_code == 200:
                logger.info(f"Modèle {OLLAMA_CONFIG['model']} téléchargé avec succès")
            else:
                logger.error(
                    f"Échec du téléchargement du modèle: {pull_response.status_code}"
                )
                return False

        logger.info("Ollama est accessible et le modèle est disponible")
        return True

    except requests.exceptions.ConnectionError:
        logger.error("Impossible de se connecter à Ollama")
        logger.error("Assurez-vous qu'Ollama est démarré avec: ollama serve")
        return False
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de la connexion à Ollama")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification d'Ollama: {e}")
        return False


def run():
    """
    Exécute le crew avec la configuration Ollama.
    """
    logger.info("=== DÉMARRAGE EVE GENESIS CREW A (Construction & Éveil) ===")

    # Configuration Ollama
    setup_ollama_environment()

    # Vérification de la disponibilité d'Ollama
    if not check_ollama_availability():
        logger.error("Ollama n'est pas accessible. Impossible de continuer.")
        sys.exit(1)

    try:
        # Inputs par défaut pour le crew
        inputs = {
            "project_name": "EVE_GENESIS",
            "phase": "construction_eveil",
            "ollama_model": OLLAMA_CONFIG["model"],
            "timestamp": time.strftime("%Y-%m-%d_%H-%M-%S"),
        }

        logger.info("Initialisation du crew...")
        crew_instance = EveGenesisCrewALIngenieurAdaptatifSupervisable41AgentsCrew()

        logger.info("Lancement de la séquence de construction et d'éveil...")
        start_time = time.time()

        # Exécution du crew
        result = crew_instance.crew().kickoff(inputs=inputs)

        end_time = time.time()
        execution_time = end_time - start_time

        logger.info(f"=== CREW A TERMINÉ AVEC SUCCÈS ===")
        logger.info(f"Temps d'exécution: {execution_time:.2f} secondes")
        logger.info(f"Résultat: {result}")

        return result

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du crew: {e}")
        logger.error("Trace complète:", exc_info=True)
        sys.exit(1)


def train():
    """
    Entraîne le crew avec Ollama pour un nombre donné d'itérations.
    """
    if len(sys.argv) < 4:
        logger.error("Usage: main.py train <n_iterations> <filename>")
        sys.exit(1)

    try:
        n_iterations = int(sys.argv[2])
        filename = sys.argv[3]

        logger.info(f"=== ENTRAÎNEMENT CREW A ===")
        logger.info(f"Itérations: {n_iterations}, Fichier: {filename}")

        # Configuration Ollama
        setup_ollama_environment()

        if not check_ollama_availability():
            logger.error("Ollama n'est pas accessible. Impossible de continuer.")
            sys.exit(1)

        inputs = {"training_mode": True, "ollama_model": OLLAMA_CONFIG["model"]}

        crew_instance = EveGenesisCrewALIngenieurAdaptatifSupervisable41AgentsCrew()

        # Note: Adaptation pour Ollama - remplace openai_model_name par ollama_model
        result = crew_instance.crew().train(
            n_iterations=n_iterations, filename=filename, inputs=inputs
        )

        logger.info("Entraînement terminé avec succès")
        return result

    except ValueError:
        logger.error("Le nombre d'itérations doit être un entier valide")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur durant l'entraînement: {e}")
        sys.exit(1)


def replay():
    """
    Rejoue l'exécution du crew à partir d'une tâche spécifique.
    """
    if len(sys.argv) < 3:
        logger.error("Usage: main.py replay <task_id>")
        sys.exit(1)

    try:
        task_id = sys.argv[2]

        logger.info(f"=== REPLAY CREW A ===")
        logger.info(f"Task ID: {task_id}")

        # Configuration Ollama
        setup_ollama_environment()

        if not check_ollama_availability():
            logger.error("Ollama n'est pas accessible. Impossible de continuer.")
            sys.exit(1)

        crew_instance = EveGenesisCrewALIngenieurAdaptatifSupervisable41AgentsCrew()
        result = crew_instance.crew().replay(task_id=task_id)

        logger.info("Replay terminé avec succès")
        return result

    except Exception as e:
        logger.error(f"Erreur durant le replay: {e}")
        sys.exit(1)


def test():
    """
    Teste l'exécution du crew avec Ollama.
    """
    if len(sys.argv) < 3:
        logger.error("Usage: main.py test <n_iterations> [model_name]")
        sys.exit(1)

    try:
        n_iterations = int(sys.argv[2])
        # Utilise le modèle Ollama configuré au lieu d'OpenAI
        model_name = sys.argv[3] if len(sys.argv) > 3 else OLLAMA_CONFIG["model"]

        logger.info(f"=== TEST CREW A ===")
        logger.info(f"Itérations: {n_iterations}, Modèle: {model_name}")

        # Configuration Ollama
        setup_ollama_environment()

        if not check_ollama_availability():
            logger.error("Ollama n'est pas accessible. Impossible de continuer.")
            sys.exit(1)

        inputs = {"test_mode": True, "ollama_model": model_name}

        crew_instance = EveGenesisCrewALIngenieurAdaptatifSupervisable41AgentsCrew()

        # Adaptation pour Ollama - utilise ollama_model au lieu d'openai_model_name
        result = crew_instance.crew().test(n_iterations=n_iterations, inputs=inputs)

        logger.info("Test terminé avec succès")
        return result

    except ValueError:
        logger.error("Le nombre d'itérations doit être un entier valide")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur durant le test: {e}")
        sys.exit(1)


def print_usage():
    """Affiche les instructions d'utilisation."""
    print("=" * 60)
    print("EVE GENESIS CREW A - Construction & Éveil")
    print("=" * 60)
    print("Usage: main.py <command> [<args>]")
    print()
    print("Commandes disponibles:")
    print("  run                    - Exécute le crew complet")
    print("  train <iter> <file>   - Entraîne le crew")
    print("  replay <task_id>      - Rejoue une tâche spécifique")
    print("  test <iter> [model]   - Teste le crew")
    print()
    print(f"Configuration Ollama:")
    print(f"  URL: {OLLAMA_CONFIG['base_url']}")
    print(f"  Modèle: {OLLAMA_CONFIG['model']}")
    print(f"  Température: {OLLAMA_CONFIG['temperature']}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "run":
            run()
        elif command == "train":
            train()
        elif command == "replay":
            replay()
        elif command == "test":
            test()
        else:
            logger.error(f"Commande inconnue: {command}")
            print_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Exécution interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        sys.exit(1)
