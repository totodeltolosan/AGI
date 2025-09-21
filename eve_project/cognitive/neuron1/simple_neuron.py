# eve_project/cognitive/neuron1/simple_neuron.py

import numpy as np

class SimpleNeuron:
    def __init__(self, num_inputs):
        self.weights = np.random.rand(num_inputs) * 0.1 # Petits poids aléatoires
        self.bias = np.random.rand() * 0.1
        print(f"Neurone créé avec {num_inputs} entrées. Poids initiaux: {self.weights}, Biais: {self.bias}")

    def forward(self, inputs):
        """Calcule la sortie du neurone (somme pondérée + biais)."""
        if len(inputs) != len(self.weights):
            raise ValueError("Le nombre d'entrées ne correspond pas au nombre de poids.")
        output = np.dot(inputs, self.weights) + self.bias
        print(f"Entrée: {inputs}, Sortie: {output}")
        return output

    def update_weights(self, new_weights, new_bias):
        """Met à jour les poids et le biais du neurone."""
        if len(new_weights) != len(self.weights):
            raise ValueError("Le nombre de nouveaux poids ne correspond pas au nombre de poids existants.")
        self.weights = new_weights
        self.bias = new_bias
        print("Poids et biais mis à jour.")

if __name__ == "__main__":
    # Exemple d'utilisation
    neuron = SimpleNeuron(num_inputs=3)
    input_data = np.array([0.5, 0.2, 0.8])
    output = neuron.forward(input_data)
    print(f"Test initial du neurone: {output}")

    # Simulation d'une mise à jour des poids
    new_w = np.array([0.1, 0.2, 0.3])
    new_b = 0.5
    neuron.update_weights(new_w, new_b)
    output_updated = neuron.forward(input_data)
    print(f"Test après mise à jour: {output_updated}")