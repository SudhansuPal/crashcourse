"""
Runnable demonstration of a learning perceptron and gradient descent.

Run from the repo root:

    python 14-machine-learning/demo.py

First a perceptron learns AND and OR (and visibly fails at XOR). Then gradient
descent fits a line to noisy data, with the loss falling toward zero.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from perceptron import Perceptron, AND_DATA, OR_DATA, XOR_DATA  # noqa: E402
from gradient_descent import fit_line, mean_squared_error  # noqa: E402


def train_and_report(name: str, data) -> None:
    p = Perceptron(n_inputs=2, learning_rate=0.1)
    history = p.train(data, epochs=20)
    final_mistakes = history[-1]
    verdict = "LEARNED IT" if final_mistakes == 0 else "COULD NOT LEARN IT"
    print(f"\n  {name}:  {verdict}")
    print(f"    mistakes per epoch: {history}")
    print(f"    weights={[round(w, 2) for w in p.weights]}, "
          f"bias={round(p.bias, 2)}")
    print("    a b | target predicted")
    print("    ----+-----------------")
    for inputs, target in data:
        print(f"    {inputs[0]} {inputs[1]} |   {target}       {p.predict(inputs)}")


def demo_perceptron() -> None:
    print("=" * 60)
    print("PERCEPTRON  (learning logic gates from examples)")
    print("=" * 60)
    train_and_report("AND", AND_DATA)
    train_and_report("OR", OR_DATA)
    train_and_report("XOR", XOR_DATA)
    print("\n  XOR is not linearly separable — no single line splits its 1s")
    print("  from its 0s — so one perceptron can never learn it. This is the")
    print("  famous limitation that drove the invention of multi-layer networks.")


def demo_gradient_descent() -> None:
    print("\n" + "=" * 60)
    print("GRADIENT DESCENT  (fitting y = w*x + b to noisy data)")
    print("=" * 60)
    # True line: y = 2x + 1, with a little noise added to each point.
    true_w, true_b = 2.0, 1.0
    noise = [0.3, -0.2, 0.1, -0.3, 0.2, -0.1, 0.25, -0.15]
    xs = [float(i) for i in range(8)]
    ys = [true_w * x + true_b + noise[i] for i, x in enumerate(xs)]

    print(f"  true line: y = {true_w}x + {true_b}  (plus noise)")
    print(f"  starting loss (w=0, b=0): {mean_squared_error(xs, ys, 0, 0):.3f}\n")

    w, b, history = fit_line(xs, ys, learning_rate=0.01, epochs=1000)

    print("  loss falls as the model learns:")
    for epoch in (0, 10, 50, 200, 999):
        print(f"    epoch {epoch:4}: loss = {history[epoch]:.4f}")
    print(f"\n  learned line: y = {w:.3f}x + {b:.3f}   "
          f"(true: y = {true_w}x + {true_b})")
    print(f"  final loss: {history[-1]:.4f}  (near zero = good fit)")


if __name__ == "__main__":
    demo_perceptron()
    demo_gradient_descent()
