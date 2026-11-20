"""Tests für die Ladesimulation (Skript B4, Kap. 4.6). Ausführen mit: pytest"""

import pytest

from wwrechner.berechnung import reserve_ladezeit_kwh
from wwrechner.ladung import (
    auftrieb_ausgleichen,
    cop_waermepumpe,
    ladung_auswerten,
    ladung_simulieren,
    startprofil,
)


def test_startprofil():
    assert startprofil(10, 55, 10, 0.2) == [55, 55, 10, 10, 10, 10, 10, 10, 10, 10]


def test_auftrieb_mischt_warm_unter_kalt():
    assert auftrieb_ausgleichen([20, 40]) == [30, 30]
    assert auftrieb_ausgleichen([50, 30, 10]) == [50, 30, 10]   # stabil: nichts tun


def test_cop_carnot():
    # 0.45 · 332.15 / 59 = 2.53
    assert cop_waermepumpe(59, 0) == pytest.approx(2.53, abs=0.01)
    # unter 40 °C wird der COP nicht besser
    assert cop_waermepumpe(30, 0) == cop_waermepumpe(40, 0)


def test_reserve_ladezeit():
    assert reserve_ladezeit_kwh(24, 2) == pytest.approx(2.0)


def test_energiebilanz_schicht():
    # 500 l, 80 % von 10 auf 55 °C: 500 · 0.8 · 45 · 1.163 Wh = 20.9 kWh
    v = ladung_simulieren("Schichtladung", 500, 6, 55, 10, 0)
    assert ladung_auswerten(v, 55)["waerme_kwh"] == pytest.approx(20.9, rel=0.03)


def test_schicht_oben_immer_warm():
    v = ladung_simulieren("Schichtladung", 500, 6, 55, 10, 0, zapfung_l_h=30)
    assert ladung_auswerten(v, 55)["t_oben_min"] >= 54.5


def test_stufe_effizienter_als_schicht():
    schicht = ladung_auswerten(ladung_simulieren("Schichtladung", 500, 6, 55, 10, 0), 55)
    stufe = ladung_auswerten(ladung_simulieren("Stufenladung", 500, 6, 55, 10, 0), 55)
    gewinn = stufe["cop_mittel"] / schicht["cop_mittel"] - 1
    assert 0.10 < gewinn < 0.30       # Skript: 15–20 %
    assert stufe["fertig"] and schicht["fertig"]
    