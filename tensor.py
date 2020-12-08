import torch
import numpy as np
from equationdata import EquationData
data = EquationData("equation")

data.traverseLatex(r"""\[ \intop{a}^{b} x^2 \,dx \]""")
# x_train = np.empty([])

# x_train, y_train, x_valid, y_valid = map(torch.tensor, (x_train, y_train, x_valid, y_valid))
# n, c = x_train.shape
# x_train, x_train.shape, y_train.min(), y_train.max()
# print(x_train, y_train)
# print(x_train.shape)
# print(y_train.min(), y_train.max())