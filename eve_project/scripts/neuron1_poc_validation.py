# eve_project/scripts/neuron1_poc_validation.py

import sys
import os
import numpy as np

# Ajout du chemin du projet EVE au PYTHONPATH pour l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from cognitive.neuron1.simple_neuron import SimpleNeuron

print("--- Début de la Validation PoC du Premier Neurone d'EVE ---")

try:
    # Initialisation du neurone
    num_inputs = 4
    neuron = SimpleNeuron(num_inputs)
    print(f"Neurone EVE initialisé avec {num_inputs} entrées.")

    # Simulation d'une série d'inputs et vérification des outputs
    test_inputs = [
        np.array([0.1, 0.2, 0.3, 0.4]),
        np.array([-0.5, 0.1, 0.0, 0.8]),
        np.array([1.0, 1.0, 1.0, 1.0]),
    ]

    expected_outputs_range_min = -1.0  # Plage d'outputs attendue après calcul
    expected_outputs_range_max = 1.0

    success_count = 0
    total_tests = len(test_inputs)

    for i, inputs in enumerate(test_inputs):
        print(f"\nTest {i+1}/{total_tests} avec inputs: {inputs}")
        output = neuron.forward(inputs)
        print(f"Output du neurone: {output}")

        # Vérification simple: l'output est dans une plage raisonnable
        if expected_outputs_range_min <= output <= expected_outputs_range_max:
            print(
                f"  ✅ Output dans la plage attendue ({expected_outputs_range_min} - {expected_outputs_range_max})."
            )
            success_count += 1
        else:
            print(f"  ❌ Output HORS de la plage attendue.")

    if success_count == total_tests:
        print(
            "\n--- ✅ Validation PoC du Premier Neurone d'EVE réussie ! Tous les outputs sont dans la plage. ---"
        )
        sys.exit(0)  # Succès
    else:
        print(
            f"\n--- ❌ Validation PoC du Premier Neurone d'EVE ÉCHOUÉE ! {success_count}/{total_tests} tests réussis. ---"
        )
        sys.exit(1)  # Échec

except Exception as e:
    print(f"\n--- ❌ Erreur critique lors de la validation PoC : {e} ---")
    sys.exit(1)  # Échec en cas d'exception
