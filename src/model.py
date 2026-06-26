import numpy as np

class Pathway:
    def __init__(self, tau_T, tau_E, beta):
        self.T = 0.0
        self.E = 0.0
        self.L = 0.0
        self.tau_T = tau_T
        self.tau_E = tau_E
        self.beta = beta

    def stimulate(self, s, e):
        self.T += s
        self.E += e

    def derivatives(self, P):
        return np.array([-self.T/self.tau_T, -self.E/self.tau_E, self.beta*self.T*P])

class Pool:
    def __init__(self, tau_p):
        self.P = 0.0
        self.tau_p = tau_p
    
    def derivatives(self):
        return -self.P/self.tau_p
    
    def add_product(self, P):
        self.P += P