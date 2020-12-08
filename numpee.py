import numpy as np

x = np.arange(12, dtype=np.int64).reshape(3, 4)
print("x = ")
print(x)
x[1:, ::2] = -99
print("x = ")
print(x)
# xr = x.reshape(3, 4)
# print(xr)