"""Konstanten und Normwerte. Nur Daten, keine Berechnungen."""

#Physik
C_Wasser = 1.163 #Wh pro Liter und Kelvin

#Standart-Temperaturen
T_WARMWASSER = 60 #°C
T_KALTWASSER = 10 #°C

#Teil B
""""Formeln für die Warmwasser-Auslegung. Jede Funktion bekommt Werte und gibt ein Ergebnis zurück."""

from ww.rechner.tabellen import C_WASSER

def tagesbedarf_liter(personen, liter_pro_person):
    """Tagesbedarf an Warmwasser in Litern."""
    return personen * liter_pro_person

def waermebedarf_kwh(volumen_l, t_warm, t_kalt):
    """Energie, um Volumen_l Liter Wasser von t_kalt auf t_warm zu erwärmen, in kWh."""
    energie_wh = volumen_l * C_WASSER * (t_warm - t_kalt)
    return energie_wh / 1000

#Teil C
"""Automatischer Test für berechnung.py. Ausführen mit: pytest"""

from ww.rechner.berechnung import tagesbedarf_liter, waermebedarf_kwh

def test_tagesbedarf_liter():
    assert tagesbedarf_liter(8, 40) == 320

def test_waermebedarf_1000_liter():
    assert round(waermebedarf_kwh(1000, 60, 10), 2) == 58.15
    
