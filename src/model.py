import numpy as np

class Dendrite:
    """
    Definines dendrite characteristics. Important to note that this reflects 
    actually reflects a pathway, but I'm using dendrite just as a naming convention
    here.
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
        return np.array([-self.T/self.tau_T, -self.E/self.tau_E, self.beta*self.T*P])
    
    def strength(self, s_base):
        return s_base + self.E + self.L
    
    def get_state(self):
        return np.array([self.T, self.E, self.L])
    
    def set_state(self, new_state):
        self.T, self.E, self.L = new_state

class Soma:
    """
    This is the part that holds the shared plasticity products.
    """
    def __init__(self, tau_p):
        self.P = 0.0
        self.tau_p = tau_p
    
    def derivatives(self):
        return -self.P/self.tau_p
    
    def add_product(self, P):
        self.P += P

class Neuron:
    """
    Brings everything together.
    """
    def __init__(self, dendrites, soma, s_base):
        self.dendrites = dendrites
        self.soma = soma
        self.s_base = s_base
    
    def pack(self):
        dendrites_vec = [dendrite.get_state() for dendrite in self.dendrites]
        return np.concatenate(dendrites_vec + [[self.soma.P]])