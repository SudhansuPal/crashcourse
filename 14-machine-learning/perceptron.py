"""
The perceptron — a neuron that *learns* a rule from examples.

Every module before this one runs rules a human wrote. Machine learning inverts
that: we show the program examples of inputs and desired outputs, and it adjusts
itself until it gets them right. The perceptron (1958) is the simplest device
that does this, and the ancestor of every neural network.

A perceptron is one artificial neuron:

    output = step( w1*x1 + w2*x2 + ... + bias )

It multiplies each input by a **weight**, adds a **bias**, and fires (1) if the
total clears zero, else stays quiet (0). Learning means finding weights that make
the outputs match the examples. The rule is beautifully simple: for each example,
nudge every weight in the direction that reduces the error —

    weight += learning_rate * (target - prediction) * input

If the prediction was too low, weights on active inputs go up; too high, they go
down. Repeat over the examples and, *if the data is linearly separable*, the
weights provably converge to a correct answer.

The catch — and one of the most famous results in AI history — is that a single
perceptron can only learn **linearly separable** functions. It masters AND and
OR, but it can *never* learn XOR, because no straight line separates XOR's 1s
from its 0s. That limitation is exactly why we need multi-layer networks.
"""

from typing import List, Tuple


class Perceptron:
    """A single neuron trained with the perceptron learning rule."""

    def __init__(self, n_inputs: int, learning_rate: float = 0.1):
        # Start every weight and the bias at zero; learning will shape them.
        self.weights: List[float] = [0.0] * n_inputs
        self.bias: float = 0.0
        self.learning_rate = learning_rate

    def _activation(self, inputs: List[float]) -> float:
        """The weighted sum plus bias — how strongly the neuron is driven."""
        total = self.bias
        for w, x in zip(self.weights, inputs):
            total += w * x
        return total

    def predict(self, inputs: List[float]) -> int:
        """Fire (1) if the activation reaches the threshold (0), else 0."""
        return 1 if self._activation(inputs) >= 0 else 0

    def train(self, examples: List[Tuple[List[float], int]],
              epochs: int = 20) -> List[int]:
        """
        Learn from (inputs, target) examples for a number of passes (epochs).

        Returns the number of mistakes made in each epoch — a learning curve. If
        it reaches zero and stays there, the perceptron has converged. For a
        non-separable problem (like XOR) it never will, which the curve reveals.
        """
        errors_per_epoch: List[int] = []
        for _ in range(epochs):
            mistakes = 0
            for inputs, target in examples:
                prediction = self.predict(inputs)
                error = target - prediction        # -1, 0, or +1
                if error != 0:
                    mistakes += 1
                    # Nudge each weight toward reducing this error.
                    for i in range(len(self.weights)):
                        self.weights[i] += self.learning_rate * error * inputs[i]
                    self.bias += self.learning_rate * error
            errors_per_epoch.append(mistakes)
            if mistakes == 0:
                break                              # converged: nothing left to fix
        return errors_per_epoch


# Truth-table training sets for the classic logic functions.
def logic_dataset(fn) -> List[Tuple[List[float], int]]:
    """Build a 2-input training set from a Python boolean function fn(a, b)."""
    return [([a, b], int(fn(a, b))) for a in (0, 1) for b in (0, 1)]


AND_DATA = logic_dataset(lambda a, b: a and b)
OR_DATA = logic_dataset(lambda a, b: a or b)
XOR_DATA = logic_dataset(lambda a, b: a ^ b)
