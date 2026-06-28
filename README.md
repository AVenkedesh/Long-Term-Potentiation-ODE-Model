# A Minimal ODE Model of Synaptic Tagging and Capture in Hippocampal LTP

The synaptic tagging and capture (STC) hypothesis of Frey and Morris explains how a transient, locally induced change at a synapse can be converted into a long-lasting one by capturing diffusible plasticity products generated elsewhere in the same neuron. The hypothesis is normally stated verbally, as a set of qualitative principles. This project translates those principles into a minimal system of ordinary differential equations (ODEs), implements the system in Python, and uses it to reproduce the landmark two-pathway result: a weakly stimulated synapse that would otherwise show only short-lasting potentiation becomes persistently potentiated when a separate set of synapses on the same neuron receives strong stimulation. The deliverable is a small, documented model that recovers the three canonical STC regimes (weak-only, strong-only, weak-plus-strong) and demonstrates the temporal-overlap requirement that is the signature prediction of the hypothesis.

## Model

Each pathway (dendrite) tracks three state variables:

| Variable | Meaning |
|----------|---------|
| `T` | Synaptic tag — decays with time constant `tau_T` |
| `E` | Early-phase potentiation — decays with time constant `tau_E` |
| `L` | Late-phase potentiation — grows when a tag is present and plasticity products `P` are available |

The soma holds a shared pool of plasticity products `P` (time constant `tau_p`) that is replenished by strong stimulation and captured by any tagged synapse.

The core ODE per dendrite is:

```
dT/dt = -T / tau_T
dE/dt = -E / tau_E
dL/dt =  beta * T * P
dP/dt = -P / tau_p          (soma)
```

## Project Structure

```
.
├── src/
│   ├── model.py          # Dendrite, Soma, and Neuron classes
│   ├── utils.py          # Utility helpers
│   └── validation.ipynb  # Reproduces the three canonical STC regimes
└── requirements.txt
```

### Key classes (`src/model.py`)

- **`Dendrite(tau_T, tau_E, beta)`** — a single synaptic pathway.
- **`Soma(tau_p)`** — the soma compartment holding shared plasticity products.
- **`Neuron(dendrites, soma, s_base)`** — integrates the full system. Call `neuron.run(events, end)` with a list of stimulus events to get back time and state arrays.

Stimulus events have the form:

```python
# Weak stimulus on pathway i
{"type": "weak",   "time": t, "i": i, "s": s, "e": e}

# Strong stimulus on pathway i (also injects plasticity products P into soma)
{"type": "strong", "time": t, "i": i, "s": s, "e": e, "P": P}
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.model import Dendrite, Soma, Neuron

dendrites = [Dendrite(tau_T=30, tau_E=60, beta=0.01),
             Dendrite(tau_T=30, tau_E=60, beta=0.01)]
soma = Soma(tau_p=120)
neuron = Neuron(dendrites, soma, s_base=1.0)

events = [
    {"type": "weak",   "time": 0,   "i": 0, "s": 0.5, "e": 0.5},
    {"type": "strong", "time": 10,  "i": 1, "s": 1.0, "e": 1.0, "P": 2.0},
]

t, y = neuron.run(events, end=300)
strengths = neuron.strengths(y)  # synaptic strength over time for each pathway
```

## Canonical STC Regimes

| Regime | Outcome |
|--------|---------|
| Weak only | Early potentiation that decays — no late LTP |
| Strong only | Persistent late LTP at the strong pathway |
| Weak + strong (overlapping) | Weak pathway captures plasticity products and also expresses late LTP |

The temporal-overlap requirement — the signature prediction of the STC hypothesis — is validated in `src/validation.ipynb`.
