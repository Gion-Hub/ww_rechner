"""Automatische Tests für berechnung.py. Ausführen mit: pytest"""

from wwrechner.berechnung import (
    spitzenstunde,
    tagesbedarf_liter,
    verbrauch_pro_stunde,
    waermebedarf_kwh,
)
from wwrechner.tabellen import PROFIL_WOHNEN


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