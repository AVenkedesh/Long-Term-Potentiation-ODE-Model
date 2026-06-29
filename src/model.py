import numpy as np
from scipy.integrate import solve_ivp

class Dendrite:
    """
    Definines dendrite characteristics. Important to note that this reflects 
    actually reflects a pathway, but I'm using dendrite just as a naming convention
    here.
    """
    def __init__(self, tau_T, tau_E, beta):
        self.T = 0.0 # tags in the dendrite in terms of arbitrary magnitude
        self.E = 0.0 # early-LTP in the dendrite in terms of arbitrary magnitude
        self.L = 0.0 # late-LTP in the dendrite in terms of arbitrary magnitude
        self.tau_T = tau_T # the timeconstant of tag decay in the dendrite
        self.tau_E = tau_E # the time constant of early-LTP decay in the dendrite
        self.beta = beta # capture rate constant

    def stimulate(self, s, e):
        """
        Stimulates the neuron. Each stimulation increases the magnitude of 
        T (tags) and E (early-LTP).
        """
        self.T += s
        self.E += e

    def derivatives(self, P):
        """
        Returns an array of derivatives for tag depletion, early-LTP depletion
        and instantaneous rate of late-LTP formation
        """
        return np.array([-self.T/self.tau_T, -self.E/self.tau_E, self.beta*self.T*P])
    
    def strength(self, s_base):
        """
        Computes the strength of the dendrite/synapses as a function of
        base strength, early-LTP and late-LTP.
        """
        return s_base + self.E + self.L
    
    def get_state(self):
        """
        Returns the current state of the dendrite with information on
        tags, early-LTP and late-LTP.
        """
        return np.array([self.T, self.E, self.L])
    
    def set_state(self, new_state):
        """
        Sets a new state for the dendrite.
        """
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

    def unpack(self, y):
        for i, dendrite in enumerate(self.dendrites):
            dendrite.set_state(y[3*i : 3*i + 3])
        self.soma.P = y[-1]

    def rhs(self, t, y):
        self.unpack(y)
        P = self.soma.P
        derivatives = [dendrite.derivatives(P) for dendrite in self.dendrites]
        dP = self.soma.derivatives()
        return np.concatenate(derivatives + [[dP]])
    
    def weak_stimulus(self, i, s, e):
        dendrite = self.dendrites[i]
        dendrite.stimulate(s,e)
    
    def strong_stimulus(self, i, s, e,P):
        dendrite = self.dendrites[i]
        dendrite.stimulate(s,e)
        self.soma.add_product(P)

    def run(self, events, end, max_step=1.0):
        boundaries = [e["time"] for e in events] + [end]
        ts, ys = [], []

        for k, event in enumerate(events):
            if event["type"] == "strong":
                self.strong_stimulus(event["i"], event["s"], event["e"], event["P"])
            else:
                self.weak_stimulus(event["i"], event["s"], event["e"])
            
            y0 = self.pack()

            solution = solve_ivp(self.rhs, (boundaries[k], boundaries[k+1]), y0, max_step=max_step, dense_output=False)

            self.unpack(solution.y[:, -1])

            if k == 0:
                ts.append(solution.t); ys.append(solution.y)
            else:
                ts.append(solution.t[1:]); ys.append(solution.y[:, 1:])

        return np.concatenate(ts), np.concatenate(ys, axis=1)
    
    def strengths(self, y):
        curves = []
        for i in range(len(self.dendrites)):
            E = y[3*i+1]
            L = y[3*i+2]
            curves.append(self.s_base + E + L)
        return curves