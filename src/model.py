import numpy as np

class Pathway:
    """
    Definines pathways characteristics
    """
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
        return np.array([-self.T/self.tau_T, -self.E/self.tau_E, self.beat*self.T*P])