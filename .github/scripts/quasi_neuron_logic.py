# .github/scripts/quasi_neuron_logic.py
import json
import argparse
import os

# --- Paramètres du Neurone ---
V_RESET = -65.0
V_THRESHOLD = -50.0
TAU_M = 20.0  # Constante de temps de la membrane (ms)
R_M = 10.0    # Résistance de la membrane (MOhms)
V_REST = -65.0
REFRACTORY_PERIOD = 5 # Période réfractaire (ms)
DT = 1.0      # Pas de temps de simulation (ms) - chaque appel de workflow est un "pas"

def load_neuron_state(neuron_state_file):
    if os.path.exists(neuron_state_file):
        with open(neuron_state_file, 'r') as f:
            return json.load(f)
    else:
        # État initial si le fichier n'existe pas
        return {
            "V": V_REST,
            "refractory_countdown": 0,
            "synaptic_weight": 0.5 # Poids initial
        }

def save_neuron_state(neuron_state_file, state):
    os.makedirs(os.path.dirname(neuron_state_file), exist_ok=True)
    with open(neuron_state_file, 'w') as f:
        json.dump(state, f, indent=2)

def simulate_neuron_step(state, stimulus_strength):
    V = state["V"]
    refractory_countdown = state["refractory_countdown"]
    synaptic_weight = state["synaptic_weight"]

    fired = False

    if refractory_countdown > 0:
        refractory_countdown -= DT
        # Le potentiel de membrane peut quand même fuir pendant la période réfractaire
        dVdt_leak = -(V - V_REST) / TAU_M
        V += dVdt_leak * DT
        if V < V_REST: V = V_REST # Ne pas descendre en dessous du potentiel de repos
    else:
        # Calcul du courant synaptique (entrée * poids)
        I_synaptic = stimulus_strength * synaptic_weight

        # Équation du potentiel de membrane (Leaky Integrate-and-Fire)
        dVdt = (-(V - V_REST) + R_M * I_synaptic) / TAU_M
        V += dVdt * DT

        if V >= V_THRESHOLD:
            fired = True
            V = V_RESET
            refractory_countdown = REFRACTORY_PERIOD

    # --- Règle d'apprentissage (STDP simplifiée ou renforcement) ---
    if fired and stimulus_strength > 0.5:
        synaptic_weight = min(1.0, synaptic_weight + 0.01)
    elif not fired and stimulus_strength > 0.7 and V < V_THRESHOLD:
        synaptic_weight = max(0.1, synaptic_weight - 0.005)

    state["V"] = V
    state["refractory_countdown"] = max(0, refractory_countdown)
    state["synaptic_weight"] = synaptic_weight

    return fired, state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simule un pas d'un neurone quasi-réel.")
    parser.add_argument("--neuron-id", type=str, required=True, help="ID unique du neurone (ex: '001')")
    parser.add_argument("--stimulus-strength", type=float, required=True, help="Force du stimulus d'entrée (ex: 0.0 à 1.0)")

    args = parser.parse_args()

    neuron_state_file = f".github/neuron_states/neuron_{args.neuron_id}.json"

    current_state = load_neuron_state(neuron_state_file)

    fired, new_state = simulate_neuron_step(current_state, args.stimulus_strength)

    save_neuron_state(neuron_state_file, new_state)

    # Afficher les outputs pour GitHub Actions
    print(f"neuron_fired={str(fired).lower()}")
    print(f"current_potential={new_state['V']:.2f}")
    print(f"new_synaptic_weight={new_state['synaptic_weight']:.3f}")
    print(f"refractory_countdown={new_state['refractory_countdown']:.2f}")
