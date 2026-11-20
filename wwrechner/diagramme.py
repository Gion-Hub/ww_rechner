"""Diagramme mit Matplotlib. Jede Funktion gibt eine fertige Figure zurück."""

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

from wwrechner.tabellen import FUEHLER_HOEHEN, LADESTUTZEN_STUFE



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

# ---------------------------------------------------------------------
# Ladung: Speicherschema und Ladeverlauf (Skript B4, Abb. 24/25)
# ---------------------------------------------------------------------

# Farben wie im Skript: kalt grün, lauwarm gelb, warm rot
FARBEN_SPEICHER = LinearSegmentedColormap.from_list("speicher", ["#c6dfa6", "#f3dc8e", "#e9a07c", "#d9817f"])


def speicher_zeichnen(ax, temp, t_min, t_max, art, titel=""):
    """Zeichnet einen Speicher als Säule, eingefärbt nach Temperatur, mit Fühlern T1–T5."""
    bild = [[t] for t in temp]                  # Spalte: oben = Index 0
    flaeche = ax.imshow(bild, cmap=FARBEN_SPEICHER, vmin=t_min, vmax=t_max,
                        extent=(0, 1, 0, 1), aspect="auto", interpolation="bilinear")
    rahmen = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.08",
                            fill=False, lw=1.5, transform=ax.transData)
    ax.add_patch(rahmen)
    flaeche.set_clip_path(rahmen)

    for nr, h in enumerate(FUEHLER_HOEHEN, start=1):
        y = 1 - h
        ax.plot([1, 1.08], [y, y], color="k", lw=0.8)
        ax.text(1.1, y, f"T{nr}", va="center", fontsize=7)

    # Ladeeintritt: Schicht ganz oben, Stufe auf Höhe Ladestutzen
    y_ein = 0.95 if art == "Schichtladung" else 1 - LADESTUTZEN_STUFE
    ax.annotate("", xy=(0.35, y_ein), xytext=(-0.25, y_ein),
                arrowprops=dict(arrowstyle="-|>", color="#b0201a", lw=1.5))
    ax.annotate("", xy=(-0.25, 0.04), xytext=(0.35, 0.04),
                arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.5))

    ax.set_xlim(-0.3, 1.35)
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(titel, fontsize=9)
    ax.axis("off")
    return flaeche


def speicher_einzeln(temp, art, t_kalt, t_soll, titel):
    """Ein einzelner Speicher (für den Zeitpunkt-Regler in der App)."""
    fig, ax = plt.subplots(figsize=(2.2, 3.4))
    speicher_zeichnen(ax, temp, t_kalt, t_soll, art, titel)
    return fig


def speicher_schema(verlauf, art, t_kalt, t_soll, anzahl=4):
    """Mehrere Speicher nebeneinander: vom Ladestart (links) bis Ladeende (rechts)."""
    letzte = len(verlauf) - 1
    indizes = [round(i * letzte / (anzahl - 1)) for i in range(anzahl)]
    fig, axes = plt.subplots(1, anzahl, figsize=(2.2 * anzahl, 3.4))
    for ax, i in zip(axes, indizes):
        flaeche = speicher_zeichnen(ax, verlauf[i]["temp"], t_kalt, t_soll, art, f"{verlauf[i]['minute']} min")
    fig.colorbar(flaeche, ax=axes, label="Temperatur [°C]", shrink=0.8)
    fig.suptitle(f"{art}: Speicher von Ladestart bis Ladeende", fontsize=10)
    return fig


def ladeverlauf_diagramm(verlauf, art, markierung=None):
    """Temperaturen T1–T5, Vor-/Rücklauf Wärmepumpe und COP über die Ladedauer (wie Abb. 24/25)."""
    minuten = [s["minute"] for s in verlauf]
    fig, ax = plt.subplots(figsize=(8, 4))
    for nr in range(len(FUEHLER_HOEHEN)):
        ax.plot(minuten, [s["fuehler"][nr] for s in verlauf], color="#1f2f3f",
                lw=1.2, alpha=1 - 0.13 * nr, label=f"T{nr + 1}")
        # Beschriftung dort, wo die Kurve die Mitte zwischen kalt und warm kreuzt (wie im Skript)
        werte = [s["fuehler"][nr] for s in verlauf]
        mitte = (min(werte) + max(werte)) / 2
        i = next((k for k, t in enumerate(werte) if t >= mitte), 0)
        ax.annotate(f"T{nr + 1}", (minuten[i], werte[i]), fontsize=8,
                    bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="k", lw=0.6))
    ax.plot(minuten, [s["h_vl"] for s in verlauf], color="#d62728", lw=1.8, label="H_VL (Vorlauf WP)")
    ax.plot(minuten, [s["h_rl"] for s in verlauf], color="#17becf", lw=1.8, label="H_RL (Rücklauf WP)")
    ax.set_xlabel("Ladedauer [min]")
    ax.set_ylabel("Temperatur [°C]")

    ax2 = ax.twinx()
    ax2.plot(minuten, [s["cop"] for s in verlauf], color="grey", ls=":", lw=1.5, label="COP")
    ax2.set_ylabel("COP [-]")
    ax2.set_ylim(0, max(s["cop"] for s in verlauf) * 1.3)

    if markierung is not None:
        ax.axvline(markierung, color="k", lw=0.8, ls="--")

    linien = ax.get_legend_handles_labels()
    linien2 = ax2.get_legend_handles_labels()
    ax.legend(linien[0][-2:] + linien2[0], linien[1][-2:] + linien2[1], loc="lower right", fontsize=8)
    ax.set_title(f"{art}: Temperaturen im Ladeverlauf")
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    fig.tight_layout()
    return fig