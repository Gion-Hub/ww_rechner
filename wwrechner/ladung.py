"""Ladesimulation Warmwasserspeicher: Schicht- vs. Stufenladung (Skript B4, Kap. 4.6).

Modell: Der Speicher wird in gleich grosse Schichten geteilt (oben = Index 0).
Pro Minute passieren drei Dinge:
  1. Ladung:   Wasser wird unten entnommen, im Plattentauscher erwärmt und wieder eingeführt
               (Schicht: ganz oben mit Solltemperatur, Stufe: auf Höhe Ladestutzen mit +ΔT).
  2. Zapfung:  Warmwasser oben raus, gleich viel Kaltwasser unten rein.
  3. Auftrieb: Liegt warmes Wasser unter kälterem, werden die beiden Schichten gemischt.
"""

from wwrechner.tabellen import (
    C_WASSER,
    DELTA_T_STUFE,
    FUEHLER_HOEHEN,
    GRAEDIGKEIT_PWT,
    GUETEGRAD_WP,
    T_KONDENSATION_MIN,
    LADESTUTZEN_STUFE,
    SCHICHTEN,
)


# ---------------------------------------------------------------------
# Bausteine
# ---------------------------------------------------------------------

def startprofil(schichten, t_warm, t_kalt, anteil_warm):
    """Temperaturen beim Ladestart: oben anteil_warm warm (Spitzendeckung), Rest kalt."""
    n_warm = round(schichten * anteil_warm)
    return [t_warm] * n_warm + [t_kalt] * (schichten - n_warm)


def verschieben_nach_unten(temp, von, menge_l, t_ein, v_schicht):
    """Strömung nach unten: bei Schicht `von` kommt menge_l mit t_ein rein, unten geht gleich viel raus.
    Jede Schicht mischt sich mit dem Anteil, der von oben nachrückt (Upwind)."""
    anteil = menge_l / v_schicht
    neu = temp[:]
    for i in range(von, len(temp)):
        oben = t_ein if i == von else temp[i - 1]
        neu[i] = temp[i] + anteil * (oben - temp[i])
    return neu


def verschieben_nach_oben(temp, menge_l, t_ein, v_schicht):
    """Zapfung: oben geht menge_l raus, unten kommt Kaltwasser mit t_ein nach."""
    anteil = menge_l / v_schicht
    neu = temp[:]
    for i in range(len(temp)):
        unten = t_ein if i == len(temp) - 1 else temp[i + 1]
        neu[i] = temp[i] + anteil * (unten - temp[i])
    return neu


def auftrieb_ausgleichen(temp):
    """Liegt eine Schicht wärmer als die darüber, steigt sie auf: beide werden gemischt.
    Wiederholen, bis von oben nach unten alles kälter wird (stabile Schichtung)."""
    temp = temp[:]
    geaendert = True
    while geaendert:
        geaendert = False
        for i in range(len(temp) - 1, 0, -1):
            if temp[i] > temp[i - 1] + 0.01:
                mittel = (temp[i] + temp[i - 1]) / 2
                temp[i] = temp[i - 1] = mittel
                geaendert = True
    return temp


def cop_waermepumpe(t_vorlauf, t_quelle, guetegrad=GUETEGRAD_WP):
    """COP über den Carnot-Wirkungsgrad: COP = η_g · T_VL / (T_VL − T_Quelle), Temperaturen in K.
    Unter T_KONDENSATION_MIN wird der COP nicht mehr besser (Mindest-Druckverhältnis Verdichter)."""
    t_h = max(t_vorlauf, T_KONDENSATION_MIN) + 273.15
    t_c = t_quelle + 273.15
    return guetegrad * t_h / (t_h - t_c)


def fuehler(temp):
    """Temperaturen an den Fühlern T1 (oben) … T5 (unten)."""
    n = len(temp)
    return [temp[min(int(h * n), n - 1)] for h in FUEHLER_HOEHEN]


# ---------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------

def ladung_simulieren(art, v_speicher, phi_kw, t_soll, t_kalt, t_quelle,
                      anteil_warm=0.2, zapfung_l_h=0.0, delta_t_stufe=DELTA_T_STUFE,
                      dauer_max_min=600, schichten=SCHICHTEN):
    """Simuliert eine Ladung im Minutentakt. art = "Schichtladung" oder "Stufenladung".
    Gibt eine Liste mit einem Dictionary pro Minute zurück."""
    v_schicht = v_speicher / schichten
    temp = startprofil(schichten, t_soll, t_kalt, anteil_warm)
    stutzen = 0 if art == "Schichtladung" else round(LADESTUTZEN_STUFE * schichten)
    q_max_wh_min = phi_kw * 1000 / 60            # Wärme pro Minute bei Volllast

    verlauf = []
    for minute in range(dauer_max_min + 1):
        t_unten = temp[-1]

        # 1. Ladung: Volumenstrom und Eintrittstemperatur
        if art == "Schichtladung":
            # Volumenstrom wird so geregelt, dass genau t_soll in den Speicher kommt
            t_ein = t_soll
            menge = q_max_wh_min / (C_WASSER * max(t_soll - t_unten, 0.5))
        else:
            # fester Volumenstrom (ausgelegt auf ΔT bei Volllast), Eintritt ungeregelt
            menge = q_max_wh_min / (C_WASSER * delta_t_stufe)
            t_ein = min(t_unten + delta_t_stufe, t_soll)
        q_wh = menge * C_WASSER * (t_ein - t_unten)

        t_vl = t_ein + GRAEDIGKEIT_PWT            # Vorlauf Wärmepumpe H_VL
        t_rl = t_unten + GRAEDIGKEIT_PWT          # Rücklauf Wärmepumpe H_RL
        cop = cop_waermepumpe(t_vl, t_quelle)

        verlauf.append({
            "minute": minute, "temp": temp[:], "fuehler": fuehler(temp),
            "h_vl": t_vl, "h_rl": t_rl, "cop": cop,
            "q_wh": q_wh, "e_el_wh": q_wh / cop,
        })

        # Ende: Fühler unten (T5) hat die Solltemperatur bis auf 2 K erreicht
        if fuehler(temp)[-1] >= t_soll - 2:
            break

        # in Teilschritte zerlegen, damit nie mehr als eine halbe Schicht pro Schritt fliesst
        teile = max(1, int(2 * max(menge, zapfung_l_h / 60) / v_schicht) + 1)
        for _ in range(teile):
            temp = verschieben_nach_unten(temp, stutzen, menge / teile, t_ein, v_schicht)
            temp = verschieben_nach_oben(temp, zapfung_l_h / 60 / teile, t_kalt, v_schicht)
            temp = auftrieb_ausgleichen(temp)

    return verlauf


def ladung_auswerten(verlauf, t_soll):
    """Kennzahlen einer Ladung: Dauer, Wärme, Strom, mittlerer COP."""
    q = sum(s["q_wh"] for s in verlauf[:-1]) / 1000
    e = sum(s["e_el_wh"] for s in verlauf[:-1]) / 1000
    return {
        "dauer_min": verlauf[-1]["minute"],
        "waerme_kwh": q,
        "strom_kwh": e,
        "cop_mittel": q / e if e > 0 else 0,
        "t_oben_min": min(s["fuehler"][0] for s in verlauf),
        "fertig": verlauf[-1]["fuehler"][-1] >= t_soll - 2,
    }
