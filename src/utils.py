import matplotlib.pyplot as plt


def weak_event(time, i, s, e):
    return {"time": time, "type": "weak", "i": i, "s": s, "e": e}


def strong_event(time, i, s, e, P):
    return {"time": time, "type": "strong", "i": i, "s": s, "e": e, "P": P}


def plot_strengths(t, strengths, labels, s_base, title=None, ax=None):
    """Plot synaptic strength over time for one or more pathways."""
    own_fig = ax is None
    if own_fig:
        _, ax = plt.subplots()

    for s, label in zip(strengths, labels):
        ax.plot(t, s, label=label)

    ax.axhline(s_base, color="grey", ls=":", lw=1)
    ax.set_xlabel("time (min)")
    ax.set_ylabel("strength (% baseline)")
    if title:
        ax.set_title(title)
    ax.legend()

    if own_fig:
        plt.tight_layout()
        plt.show()


def delay_sweep(neuron_factory, strong_ev, weak_ev_template, delays, end):
    """
    Run the two-pathway capture experiment across a range of delays.

    neuron_factory  -- callable() that returns a fresh Neuron each iteration
    strong_ev       -- strong-stimulus event dict (applied at time 0 on pathway 0)
    weak_ev_template -- weak-stimulus event dict with time=0; time is overwritten per delay
    delays          -- iterable of delay values (same units as the ODE time axis)
    end             -- simulation end time

    Returns (delays, final_L1_values, t_arrays, strength_arrays) where
    strength_arrays[k] = (s0, s1) for delay k.
    """
    final_L = []
    ts = []
    strength_curves = []

    for d in delays:
        neuron = neuron_factory()
        weak_ev = {**weak_ev_template, "time": d}
        events = [strong_ev, weak_ev] if d == 0 else [strong_ev, weak_ev]
        t, y = neuron.run(events, end)
        final_L.append(y[5][-1])
        ts.append(t)
        strength_curves.append(neuron.strengths(y))

    return list(delays), final_L, ts, strength_curves


def plot_delay_sweep(delays, final_L, ts, strength_curves, s_base):
    """Produce the two standard delay-sweep figures."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    cmap = plt.cm.viridis
    strong_plotted = False
    for k, (d, (s0, s1)) in enumerate(zip(delays, strength_curves)):
        if not strong_plotted:
            axes[0].plot(ts[k], s0, color="crimson", lw=2.5, label="pathway 0 (strong)")
            strong_plotted = True
        axes[0].plot(ts[k], s1, color=cmap(k / max(len(delays) - 1, 1)),
                     lw=1.8, label=f"weak, delay {d}")

    axes[0].axhline(s_base, color="grey", ls=":", lw=1)
    axes[0].set_xlabel("time (min)")
    axes[0].set_ylabel("strength (% baseline)")
    axes[0].legend(fontsize=7)

    axes[1].plot(delays, final_L, "o-", lw=2)
    axes[1].axhline(0, color="grey", ls=":", lw=1)
    axes[1].set_xlabel("delay between strong and weak tetanus (min)")
    axes[1].set_ylabel("captured late-LTP  (final L1)")
    axes[1].set_title("Capture vs. timing: the product-availability window")

    plt.tight_layout()
    plt.show()
