"""
Gradient descent — how learning actually happens, step by step downhill.

The perceptron's update rule works, but modern machine learning rests on a more
general and powerful idea: **gradient descent**. Define a "loss" that measures how
wrong the model is; compute which way to change each parameter to make the loss
smaller (the gradient); take a small step that way; repeat. Over many steps the
loss rolls downhill toward a minimum, and the model gets better.

We demonstrate it on the simplest possible model — fitting a straight line
`y = w*x + b` to data — because here we can see every piece: the loss, the
gradient, and the parameters converging to the right answer. This exact procedure,
scaled up to millions of parameters, is how neural networks are trained.

Everything is plain Python lists and arithmetic — no NumPy, no ML library. The
math is the lesson.
"""

from typing import List, Tuple


def mean_squared_error(xs: List[float], ys: List[float], w: float, b: float) -> float:
    """
    The loss: the average squared gap between our line's predictions and the
    true y-values. Squaring makes all errors positive and punishes big misses
    more; the average keeps it independent of how many points there are.
    """
    n = len(xs)
    total = 0.0
    for x, y in zip(xs, ys):
        prediction = w * x + b
        total += (prediction - y) ** 2
    return total / n


def fit_line(xs: List[float], ys: List[float], learning_rate: float = 0.01,
             epochs: int = 1000) -> Tuple[float, float, List[float]]:
    """
    Learn w and b for y = w*x + b by gradient descent on the mean squared error.

    At each step we compute the gradient of the loss with respect to w and b —
    the direction of steepest *increase* — and step the opposite way, scaled by
    the learning rate. Returns (w, b, loss_history).

    The gradients (from calculus, derivative of the squared error):
        dLoss/dw = (2/n) * sum( (w*x + b - y) * x )
        dLoss/db = (2/n) * sum(  w*x + b - y      )
    """
    w, b = 0.0, 0.0
    n = len(xs)
    history: List[float] = []
    for _ in range(epochs):
        grad_w = 0.0
        grad_b = 0.0
        for x, y in zip(xs, ys):
            error = (w * x + b) - y     # how far off this point is
            grad_w += (2 / n) * error * x
            grad_b += (2 / n) * error
        # Step downhill: subtract the gradient (scaled) from each parameter.
        w -= learning_rate * grad_w
        b -= learning_rate * grad_b
        history.append(mean_squared_error(xs, ys, w, b))
    return w, b, history
