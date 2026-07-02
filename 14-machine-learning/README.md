# 14 — Machine Learning

The final module, and a turning point. Every module before this one *executes
rules a human wrote*. Machine learning flips that around: we give the program
examples and let it *find the rule itself*. We build the two foundational pieces
from scratch — a **perceptron** that learns, and the **gradient descent** that
powers modern training — closing the course from a single transistor all the way
to a program that improves itself.

## The concept in plain language

A **perceptron** is one artificial neuron. It multiplies each input by a
**weight**, adds a **bias**, and fires if the total clears a threshold:

```
output = step( w1·x1 + w2·x2 + bias )
```

Learning means adjusting the weights until the outputs match the examples. The
perceptron's rule is delightfully simple — for each example, nudge the weights in
the direction that reduces the error:

```
weight += learning_rate · (target − prediction) · input
```

**Gradient descent** generalizes this. Define a **loss** measuring how wrong the
model is, compute which way to change each parameter to shrink the loss (the
**gradient**), take a small step that way, and repeat. The loss rolls downhill to
a minimum. We show it fitting a line `y = w·x + b`, where every piece — loss,
gradient, and the parameters converging — is visible.

## Why it matters

This is how modern AI works, all the way up to large language models: define a
loss, follow the gradient, repeat over enormous data. Seeing it on a single
neuron and a straight line demystifies the whole field — training is not magic,
it's **calculus rolling downhill**.

Just as important is the lesson in the perceptron's *failure*. It learns AND and
OR easily, but it can **never** learn XOR, because no single straight line
separates XOR's 1s from its 0s — XOR isn't *linearly separable*. This exact
limitation, published in 1969, stalled neural-network research for years and is
precisely why we need **multi-layer** networks (which stack neurons to bend the
decision boundary). The demo shows the perceptron converging on AND/OR and
thrashing forever on XOR.

## How the code demonstrates it

- **[`perceptron.py`](perceptron.py)** — a `Perceptron` trained with the
  perceptron learning rule. `train` returns the mistakes-per-epoch **learning
  curve**, which drops to 0 for AND/OR (converged) and never settles for XOR.
- **[`gradient_descent.py`](gradient_descent.py)** — `fit_line` learns `w` and
  `b` by gradient descent on the mean squared error, with the gradients derived
  from calculus and applied by hand. Returns the full loss history so you can
  watch it fall.

The demo trains the perceptron on all three gates and then fits a noisy line,
recovering `y ≈ 1.99x + 1.05` for a true line of `y = 2x + 1` while the loss
falls from ~85 to near zero. **No NumPy, no ML library** — just lists and
arithmetic, so the math is the lesson.

## Run it

```bash
# from the repo root

# perceptron on AND/OR/XOR, then gradient descent fitting a line
python 14-machine-learning/demo.py

# run the tests
pytest 14-machine-learning/
```

## Files

- `perceptron.py` — the neuron, the learning rule, and logic-gate datasets.
- `gradient_descent.py` — mean squared error and line-fitting by gradient descent.
- `demo.py` — perceptron learning curves and a gradient-descent fit.
- `test_ml.py` — AND/OR/NAND learned, XOR provably not, and gradient descent
  recovering known parameters and reducing loss.

## The end of the course

From a single transistor (module 02) to a program that learns (module 14), this
repo builds a computer and its software from first principles, each layer resting
on the one below. Thanks for climbing the whole stack. See the
[top-level README](../README.md) for the full map.
