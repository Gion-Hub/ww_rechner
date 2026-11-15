"""Automatische Tests für berechnung.py. Ausführen mit: pytest"""

from wwrechner.berechnung import (
    ausstossverlust_kwh,
    bereitschaftsvolumen_kwh,
    endenergie_kwh,
    endenergie_jahr_kwh,
    ladeleistung_kw,
    speicher_genuegt,
    speicherverlust_kwh,
    speichervolumen_erforderlich_l,
    spitzenstunde,
    stundenspitze_anteil,
    tagesbedarf_liter,
    verbrauch_pro_stunde,
    waermebedarf_gesamt_kwh,
    waermebedarf_kwh,
    wirkungsgrad_holz,
    zirkulationsverlust_kwh,
)
from wwrechner.tabellen import PROFIL_WOHNEN


# =====================================================================
# ① Bedarf
# =====================================================================

def test_tagesbedarf_liter():
    assert tagesbedarf_liter(8, 40) == 320


def test_waermebedarf_1000_liter():
    assert round(waermebedarf_kwh(1000, 60, 10), 2) == 58.15


def test_waermebedarf_ohne_temperaturdifferenz():
    assert waermebedarf_kwh(500, 10, 10) == 0


def test_profil_hat_24_stunden_und_100_prozent():
    assert len(PROFIL_WOHNEN) == 24
    assert round(sum(PROFIL_WOHNEN)) == 100


def test_verbrauch_pro_stunde_summe_gleich_tagesbedarf():
    stunden = verbrauch_pro_stunde(1000, PROFIL_WOHNEN)
    assert round(sum(stunden)) == 1000


def test_spitzenstunde_morgens_um_8():
    stunden = verbrauch_pro_stunde(1000, PROFIL_WOHNEN)
    stunde, liter = spitzenstunde(stunden)
    assert stunde == 8
    assert round(liter, 1) == 83.9


# =====================================================================
# ② Grobauslegung (Vorprojekt)
# =====================================================================

# Folgt: Tests Grobauslegung gegen Handout


# =====================================================================
# ③ Feinauslegung (Bauprojekt)
# =====================================================================

def test_stundenspitze_25_personen():
    assert round(stundenspitze_anteil(25), 4) == 0.3012


def test_stundenspitze_uebergang_bei_10_personen():
    # Beide Formeln sollen bei 10 Personen fast gleich sein (kein Sprung)
    assert abs(stundenspitze_anteil(10) - stundenspitze_anteil(9.99)) < 0.01


def test_zirkulationsverlust():
    assert zirkulationsverlust_kwh(50) == 6.0


def test_ausstossverlust_handout():
    # Handout 5.1.4: 2 WE à 3.1 Personen, mit Warmhaltung -> 1.99 kWh/WE, total 3.98 kWh/d
    assert round(ausstossverlust_kwh(2, 3.1, True), 2) == 3.98


def test_speicherverlust_1000_liter():
    assert round(speicherverlust_kwh(1000), 2) == 3.48
    assert round(speicherverlust_kwh(1000, stutzen=6), 2) == 3.88


def test_waermebedarf_gesamt():
    assert waermebedarf_gesamt_kwh(10.0, 2.46, 6.0, 2.2) == 20.66


def test_bereitschaftsvolumen():
    # 10 kWh Nutzwärme, 30 % Spitze, 20.66 kWh gesamt, 2 Ladungen pro Tag
    assert round(bereitschaftsvolumen_kwh(10.0, 0.30, 20.66, 2), 2) == 13.33


def test_speichervolumen_erforderlich():
    # 13.33 kWh, 60 °C / 10 °C, f_sto = 1.0
    assert round(speichervolumen_erforderlich_l(13.33, 60, 10, 1.0), 1) == 229.2


def test_speicher_genuegt():
    assert speicher_genuegt(500, 460) is True
    assert speicher_genuegt(400, 460) is False


# =====================================================================
# ④ Wärmeerzeuger
# =====================================================================

def test_ladeleistung():
    # 24 kWh pro Tag, 2 Ladungen, je 3 h Ladezeit -> 12 kWh / 3 h = 4 kW
    assert round(ladeleistung_kw(24.0, 2, 3), 2) == 4.0


def test_wirkungsgrad_holz():
    assert wirkungsgrad_holz("Pellets", False, False) == 0.60
    assert wirkungsgrad_holz("Hackschnitzel", True, True) == 0.65
    assert wirkungsgrad_holz("Stückholz", True, True) is None


def test_endenergie():
    # 20 kWh Wärme bei Wirkungsgrad 0.8 -> 25 kWh Endenergie
    assert round(endenergie_kwh(20.0, 0.8), 2) == 25.0


def test_endenergie_handout():
    # Handout 5.4: (18 + 10) kWh/d bei η = 0.60 -> ca. 47 kWh/d
    assert round(endenergie_kwh(18 + 10, 0.60)) == 47


def test_endenergie_jahr_handout():
    # Handout 5.4: 47 kWh/d · 365 · 0.8 = 13'724 kWh/a
    assert round(endenergie_jahr_kwh(47)) == 13724
