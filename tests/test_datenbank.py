"""Tests für die Nutzungs-Datenbank. Jeder Test arbeitet mit einer eigenen, temporären Datenbank."""

from wwrechner.berechnung import bedarf_mit_streuung
from wwrechner.datenbank import datenbank_erstellen, gruppen_laden, nutzungen_laden


def test_datenbank_enthaelt_28_nutzungen(tmp_path):
    db = tmp_path / "test.db"
    datenbank_erstellen(db)
    anzahl = sum(len(nutzungen_laden(g, db)) for g in gruppen_laden(db))
    assert anzahl == 28


def test_gruppen_in_richtiger_reihenfolge(tmp_path):
    db = tmp_path / "test.db"
    datenbank_erstellen(db)
    assert gruppen_laden(db) == ["Wohnen", "Büro", "Gastronomie", "Beherbergung", "Heimwesen", "Weitere"]


def test_restaurant_kennwerte(tmp_path):
    db = tmp_path / "test.db"
    datenbank_erstellen(db)
    gastro = nutzungen_laden("Gastronomie", db)
    restaurant = gastro[gastro["standard"] == "mehrere Gänge"].iloc[0]
    assert restaurant["einheit"] == "Mahlzeit"
    assert restaurant["vw_l"] == 10


def test_datenbank_wird_automatisch_erstellt(tmp_path):
    db = tmp_path / "neu.db"
    assert not db.exists()
    gruppen_laden(db)
    assert db.exists()


def test_bedarf_mit_streuung_wenige_einheiten():
    # EFH einfach, 4 Personen: (40 + 2 · 5) · 4 = 200 l/d
    assert bedarf_mit_streuung(40, 5.0, 4) == 200


def test_bedarf_mit_streuung_viele_einheiten():
    # MFH, 20 Personen: (35 + 2 · 5 / √20) · 20 = 744.7 l/d
    assert round(bedarf_mit_streuung(35, 5.0, 20), 1) == 744.7