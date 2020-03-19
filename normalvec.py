import numpy as np
from scipy.misc import derivative

def func(t):
    return np.array([t**2,t])

def deriv(func, p):
    der = round(derivative(func, p, dx=1e-6),2)
    return der

def gradient(func, p):
    def func_x(t):
        return func(t)[0]

    def func_y(t):
        return func(t)[1]
    dx = deriv(func_x, p)
    dy = deriv(func_y, p)
    vec = np.array([dx, dy])
    if np.linalg.norm(vec) == 0.:
        return vec
    return vec/np.linalg.norm(vec)

def normal(func, p):
    grad = gradient(func, p)
    return np.array([grad[1],-grad[0]])
