# eve_project/tests/cognitive/neuron1/test_simple_neuron.py

import pytest
import numpy as np
from eve_project.cognitive.neuron1.simple_neuron import SimpleNeuron


def test_neuron_initialization():
    """Test l'initialisation du neurone."""
    neuron = SimpleNeuron(num_inputs=5)
    assert neuron.weights.shape == (5,)
    assert isinstance(neuron.bias, float) or isinstance(neuron.bias, np.float64)


def test_neuron_forward_pass():
    """Test la propagation avant du neurone."""
    neuron = SimpleNeuron(num_inputs=2)
    neuron.weights = np.array([0.5, -0.5])
    neuron.bias = 0.1

    inputs = np.array([1.0, 1.0])
    output = neuron.forward(inputs)
    assert np.isclose(output, (1.0 * 0.5) + (1.0 * -0.5) + 0.1)

    inputs_2 = np.array([2.0, 0.0])
    output_2 = neuron.forward(inputs_2)
    assert np.isclose(output_2, (2.0 * 0.5) + (0.0 * -0.5) + 0.1)


def test_neuron_forward_pass_value_error():
    """Test la gestion d'erreur si le nombre d'entrées ne correspond pas."""
    neuron = SimpleNeuron(num_inputs=3)
    with pytest.raises(
        ValueError, match="Le nombre d'entrées ne correspond pas au nombre de poids."
    ):
        neuron.forward(
            np.array([1.0, 2.0])
        )  # Fournit 2 entrées pour un neurone à 3 entrées


def test_neuron_weight_update():
    """Test la mise à jour des poids et du biais."""
    neuron = SimpleNeuron(num_inputs=2)
    initial_weights = neuron.weights.copy()
    initial_bias = neuron.bias

    new_weights = np.array([0.7, 0.3])
    new_bias = 0.2
    neuron.update_weights(new_weights, new_bias)

    assert np.array_equal(neuron.weights, new_weights)
    assert np.isclose(neuron.bias, new_bias)


def test_neuron_weight_update_value_error():
    """Test la gestion d'erreur si le nombre de nouveaux poids est incorrect."""
    neuron = SimpleNeuron(num_inputs=3)
    with pytest.raises(
        ValueError,
        match="Le nombre de nouveaux poids ne correspond pas au nombre de poids existants.",
    ):
        neuron.update_weights(
            np.array([0.1, 0.2]), 0.5
        )  # Fournit 2 poids pour un neurone à 3 entrées
