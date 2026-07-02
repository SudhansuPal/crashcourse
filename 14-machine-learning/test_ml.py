"""
Unit tests for the perceptron and gradient descent.

Run from the repo root:

    pytest 14-machine-learning/
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from perceptron import Perceptron, AND_DATA, OR_DATA, XOR_DATA  # noqa: E402
from gradient_descent import fit_line, mean_squared_error  # noqa: E402


# ---- perceptron -----------------------------------------------------------

def test_perceptron_learns_and():
    p = Perceptron(2, learning_rate=0.1)
    p.train(AND_DATA, epochs=50)
    for inputs, target in AND_DATA:
        assert p.predict(inputs) == target


def test_perceptron_learns_or():
    p = Perceptron(2, learning_rate=0.1)
    p.train(OR_DATA, epochs=50)
    for inputs, target in OR_DATA:
        assert p.predict(inputs) == target


def test_perceptron_converges_to_zero_errors():
    p = Perceptron(2, learning_rate=0.1)
    history = p.train(AND_DATA, epochs=50)
    assert history[-1] == 0             # reached perfect classification


def test_perceptron_cannot_learn_xor():
    """The famous result: a single perceptron never nails XOR."""
    p = Perceptron(2, learning_rate=0.1)
    history = p.train(XOR_DATA, epochs=100)
    # It never converges, so at least one example stays wrong every epoch.
    assert all(mistakes > 0 for mistakes in history)
    correct = sum(1 for inputs, target in XOR_DATA if p.predict(inputs) == target)
    assert correct < 4                  # cannot get all four right


def test_perceptron_learns_nand():
    nand_data = [([a, b], int(not (a and b))) for a in (0, 1) for b in (0, 1)]
    p = Perceptron(2, learning_rate=0.1)
    p.train(nand_data, epochs=50)
    for inputs, target in nand_data:
        assert p.predict(inputs) == target


def test_perceptron_early_stops_on_convergence():
    p = Perceptron(2, learning_rate=0.1)
    history = p.train(OR_DATA, epochs=100)
    assert len(history) < 100           # stopped early once errors hit 0


# ---- gradient descent -----------------------------------------------------

def test_gradient_descent_reduces_loss():
    xs = [0.0, 1.0, 2.0, 3.0, 4.0]
    ys = [1.0, 3.0, 5.0, 7.0, 9.0]      # exactly y = 2x + 1
    _, _, history = fit_line(xs, ys, learning_rate=0.01, epochs=500)
    # Loss should decrease monotonically-ish and end much lower than it started.
    assert history[-1] < history[0]
    assert history[-1] < 0.01


def test_gradient_descent_recovers_parameters():
    xs = [float(i) for i in range(10)]
    ys = [3.0 * x - 2.0 for x in xs]    # true line y = 3x - 2
    w, b, _ = fit_line(xs, ys, learning_rate=0.01, epochs=5000)
    assert abs(w - 3.0) < 0.05
    assert abs(b - (-2.0)) < 0.1


def test_gradient_descent_fits_noisy_data():
    xs = [float(i) for i in range(8)]
    noise = [0.1, -0.1, 0.05, -0.05, 0.1, -0.1, 0.05, -0.05]
    ys = [2.0 * x + 1.0 + noise[i] for i, x in enumerate(xs)]
    w, b, history = fit_line(xs, ys, learning_rate=0.01, epochs=3000)
    assert abs(w - 2.0) < 0.1
    assert abs(b - 1.0) < 0.2
    assert history[-1] < history[0]


def test_mean_squared_error_zero_for_perfect_fit():
    xs = [1.0, 2.0, 3.0]
    ys = [3.0, 5.0, 7.0]                # y = 2x + 1 exactly
    assert mean_squared_error(xs, ys, 2.0, 1.0) == 0.0


def test_loss_history_length_matches_epochs():
    xs = [0.0, 1.0, 2.0]
    ys = [0.0, 1.0, 2.0]
    _, _, history = fit_line(xs, ys, epochs=123)
    assert len(history) == 123
