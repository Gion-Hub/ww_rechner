"""Automatische Tests für berechnung.py. Ausführen mit: pytest"""

from wwrechner.berechnung import tagesbedarf_liter, waermebedarf_kwh


def test_tagesbedarf_liter():
    assert tagesbedarf_liter(8, 40) == 320


def test_waermebedarf_1000_liter():
    assert round(waermebedarf_kwh(1000, 60, 10), 2) == 58.15


def test_waermebedarf_ohne_temperaturdifferenz():
    assert waermebedarf_kwh(500, 10, 10) == 0