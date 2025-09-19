#!/usr/bin/env python
import sys
import os
import requests
import time
from eve_genesis___crew_b.crew import EveGenesisCrewBCrew

# Configuration optimisée pour EVE GENESIS Crew B
OLLAMA_BASE_URL = "http://localhost:11434"
REQUIRED_MODEL = "llama3:8b"


def check_ollama_health():
    """
    Vérifie que Ollama est accessible et que le modèle requis est disponible.
    """
    try:
        # Vérification de base d'Ollama
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code != 200:
            raise Exception(f"Ollama n'est pas accessible sur {OLLAMA_BASE_URL}")

        # Vérification que le modèle requis est disponible
        models = response.json().get("models", [])
        model_names = [model.get("name", "") for model in models]

        if not any(REQUIRED_MODEL in name for name in model_names):
            print(f"⚠️  Modèle {REQUIRED_MODEL} non trouvé.")
            print(f"📋 Modèles disponibles: {[name for name in model_names]}")
            print(f"🔄 Pour installer le modèle requis: ollama pull {REQUIRED_MODEL}")
            return False

        print(f"✅ Ollama opérationnel avec le modèle {REQUIRED_MODEL}")
        return True

    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à Ollama sur {OLLAMA_BASE_URL}")
        print("🚀 Assurez-vous qu'Ollama est démarré: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification d'Ollama: {e}")
        return False


def get_crew_inputs():
    """
    Prépare les inputs optimisés pour le Crew B d'EVE GENESIS.
    """
    return {
        "environment": "local_ollama",
        "model_config": {
            "base_url": OLLAMA_BASE_URL,
            "model": REQUIRED_MODEL,
            "timeout": 60,
        },
        "crew_type": "enrichment_and_evolution",
        "optimization_mode": True,
    }


def run():
    """
    Lance le Crew B d'EVE GENESIS avec optimisations Ollama.
    """
    print("🚀 Démarrage du Crew B - EVE GENESIS Enrichment & Evolution")

    if not check_ollama_health():
        print("❌ Impossible de démarrer sans Ollama opérationnel")
        sys.exit(1)

    print("🔧 Initialisation du Crew B avec 58 agents...")
    inputs = get_crew_inputs()

    try:
        crew = EveGenesisCrewBCrew().crew()
        print(f"📊 Crew configuré avec {len(crew.agents)} agents")
        print("🎯 Lancement de la séquence d'enrichissement...")

        result = crew.kickoff(inputs=inputs)
        print("✅ Crew B terminé avec succès !")
        return result

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du Crew B: {e}")
        raise


def train():
    """
    Entraîne le Crew B pour un nombre d'itérations donné.
    Optimisé pour l'environnement Ollama local.
    """
    if len(sys.argv) < 3:
        print("Usage: main.py train <n_iterations> <filename>")
        sys.exit(1)

    if not check_ollama_health():
        print("❌ Impossible d'entraîner sans Ollama opérationnel")
        sys.exit(1)

    inputs = get_crew_inputs()
    n_iterations = int(sys.argv[1])
    filename = sys.argv[2]

    print(f"🎓 Entraînement du Crew B pour {n_iterations} itérations")
    print(f"💾 Sauvegarde: {filename}")

    try:
        crew = EveGenesisCrewBCrew().crew()
        result = crew.train(n_iterations=n_iterations, filename=filename, inputs=inputs)
        print("✅ Entraînement terminé avec succès !")
        return result

    except Exception as e:
        print(f"❌ Erreur lors de l'entraînement: {e}")
        raise Exception(f"Échec de l'entraînement du Crew B: {e}")


def replay():
    """
    Rejoue l'exécution du Crew B depuis une tâche spécifique.
    """
    if len(sys.argv) < 2:
        print("Usage: main.py replay <task_id>")
        sys.exit(1)

    if not check_ollama_health():
        print("❌ Impossible de rejouer sans Ollama opérationnel")
        sys.exit(1)

    task_id = sys.argv[1]
    print(f"🔄 Rejeu du Crew B depuis la tâche: {task_id}")

    try:
        crew = EveGenesisCrewBCrew().crew()
        result = crew.replay(task_id=task_id)
        print("✅ Rejeu terminé avec succès !")
        return result

    except Exception as e:
        print(f"❌ Erreur lors du rejeu: {e}")
        raise Exception(f"Échec du rejeu du Crew B: {e}")


def test():
    """
    Teste le Crew B avec Ollama local (plus de référence OpenAI).
    """
    if len(sys.argv) < 3:
        print("Usage: main.py test <n_iterations> <test_scenario>")
        sys.exit(1)

    if not check_ollama_health():
        print("❌ Impossible de tester sans Ollama opérationnel")
        sys.exit(1)

    inputs = get_crew_inputs()
    n_iterations = int(sys.argv[1])
    test_scenario = sys.argv[2]  # Remplace openai_model_name

    # Configuration de test spécialisée
    inputs["test_mode"] = True
    inputs["test_scenario"] = test_scenario
    inputs["iterations"] = n_iterations

    print(f"🧪 Test du Crew B - Scénario: {test_scenario}")
    print(f"🔄 Itérations: {n_iterations}")

    try:
        crew = EveGenesisCrewBCrew().crew()
        result = crew.test(n_iterations=n_iterations, inputs=inputs)
        print("✅ Tests terminés avec succès !")
        return result

    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        raise Exception(f"Échec des tests du Crew B: {e}")


def show_status():
    """
    Affiche le statut du système EVE GENESIS Crew B.
    """
    print("📊 Statut EVE GENESIS - Crew B")
    print("=" * 50)

    # Vérification Ollama
    if check_ollama_health():
        print("🟢 Ollama: Opérationnel")
    else:
        print("🔴 Ollama: Non disponible")

    # Information sur le Crew
    try:
        crew = EveGenesisCrewBCrew().crew()
        print(f"👥 Agents configurés: {len(crew.agents)}")
        print(f"📋 Tâches configurées: {len(crew.tasks)}")
        print("🟢 Crew B: Prêt")
    except Exception as e:
        print(f"🔴 Crew B: Erreur de configuration - {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🎯 EVE GENESIS - Crew B (Enrichment & Evolution)")
        print("=" * 50)
        print("Usage: main.py <command> [<args>]")
        print("")
        print("Commandes disponibles:")
        print("  run                          - Lance le Crew B")
        print("  train <iterations> <file>    - Entraîne le Crew B")
        print("  replay <task_id>             - Rejoue depuis une tâche")
        print("  test <iterations> <scenario> - Teste le Crew B")
        print("  status                       - Affiche le statut système")
        print("")
        print("💡 Astuce: Assurez-vous qu'Ollama est démarré avec 'ollama serve'")
        sys.exit(1)

    command = sys.argv[1]

    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    elif command == "status":
        show_status()
    else:
        print(f"❌ Commande inconnue: {command}")
        print("💡 Utilisez 'main.py' sans arguments pour voir l'aide")
        sys.exit(1)
