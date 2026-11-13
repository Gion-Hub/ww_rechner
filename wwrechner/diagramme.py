"""Diagramme mit Matplotlib. Jede Funktion gibt eine fertige Figure zurück."""

import matplotlib.pyplot as plt


def tagesprofil_diagramm(stunden_liter):
    """Säulendiagramm: Warmwasserverbrauch pro Stunde über den Tag."""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    stunden = list(range(24))
    ax.bar(stunden, stunden_liter, color="#c4372b")
    ax.set_xlabel("Uhrzeit [h]")
    ax.set_ylabel("Verbrauch [l/h]")
    ax.set_title("Tagesprofil Warmwasserverbrauch")
    ax.set_xticks(range(0, 24, 2))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig