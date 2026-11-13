"""Formeln für die Warmwasser-Auslegung. Jede Funktion bekommt Werte und gibt ein Ergebnis zurück."""

from wwrechner.tabellen import (
    AUSSTOSS_MIT_WARMHALTUNG,
    AUSSTOSS_OHNE_WARMHALTUNG,
    C_WASSER,
    SPEICHER_VERLUST_FAKTOR,
    STUTZEN_ZUSCHLAG,
    VERLUST_ZIRKULATION,
)



def tagesbedarf_liter(personen, liter_pro_person):
    """Tagesbedarf an Warmwasser in Litern."""
    return personen * liter_pro_person


def waermebedarf_kwh(volumen_l, t_warm, t_kalt):
    """Energie, um volumen_l Liter Wasser von t_kalt auf t_warm zu erwärmen, in kWh."""
    energie_wh = volumen_l * C_WASSER * (t_warm - t_kalt)
    return energie_wh / 1000


def verbrauch_pro_stunde(tagesbedarf_l, profil_prozent):
    """Verteilt den Tagesbedarf auf 24 Stunden. Gibt eine Liste mit Litern pro Stunde zurück."""
    stunden_liter = []
    for anteil in profil_prozent:
        stunden_liter.append(tagesbedarf_l * anteil / 100)
    return stunden_liter


def spitzenstunde(stunden_liter):
    """Stunde mit dem grössten Verbrauch. Gibt (Stunde, Liter) zurück."""
    maximum = max(stunden_liter)
    stunde = stunden_liter.index(maximum)
    return stunde, maximum



# --- Stundenspitze und Verluste (SIA 385/2) ---

def stundenspitze_anteil(personen):
    """Anteil des Tagesbedarfs, der in der stärksten Stunde gezapft wird (0.30 = 30 %)."""
    if personen >= 10:
        return 0.09 + 0.66 / personen**0.5 + 1.98 / personen
    return 1.3227 * personen**-0.428


def zirkulationsverlust_kwh(leitungslaenge_m):
    """Wärmeverlust der Zirkulationsleitung pro Tag in kWh."""
    return leitungslaenge_m * VERLUST_ZIRKULATION


def ausstossverlust_kwh(wohnungen, mit_warmhaltung):
    """Ausstossverluste Wohnen pro Tag in kWh. Entnahmen pro Tag = 2 + 5 × Wohnungen."""
    entnahmen = 2 + 5 * wohnungen
    if mit_warmhaltung:
        return entnahmen * AUSSTOSS_MIT_WARMHALTUNG
    return entnahmen * AUSSTOSS_OHNE_WARMHALTUNG


def speicherverlust_kwh(volumen_l, stutzen=2):
    """Bereitschaftsverlust des Speichers pro Tag in kWh."""
    return SPEICHER_VERLUST_FAKTOR * volumen_l**0.5 + STUTZEN_ZUSCHLAG * (stutzen - 2)
