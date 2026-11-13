"""Formeln für die Warmwasser-Auslegung. Jede Funktion bekommt Werte und gibt ein Ergebnis zurück."""

from wwrechner.tabellen import C_WASSER


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