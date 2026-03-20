import numpy as np

class TinyPolicyNet:
    def __init__(self):
        np.random.seed(42)
        self.W1 = np.random.randn(64, 32) * 0.1
        self.b1 = np.zeros(32)
        self.W2 = np.random.randn(32, 1) * 0.1
        self.b2 = np.zeros(1)

    def forward(self, x):
        h = np.maximum(0, x @ self.W1 + self.b1)
        y = 1 / (1 + np.exp(-(h @ self.W2 + self.b2)))
        return float(y.item())
