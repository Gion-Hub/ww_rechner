"""SQLite-Datenbank mit den Kennwerten der Nutzungen (SIA 385/2, Anhang A.3).

Die Datenbank wird beim ersten Start automatisch aus daten/nutzungen.csv erstellt.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DATEN_ORDNER = Path(__file__).resolve().parent.parent / "daten"
CSV_DATEI = DATEN_ORDNER / "nutzungen.csv"
DB_DATEI = DATEN_ORDNER / "wwrechner.db"


def datenbank_erstellen(db_datei=DB_DATEI, csv_datei=CSV_DATEI):
    """Erstellt die Tabelle 'nutzungen' und füllt sie mit den Werten aus der CSV-Datei."""
    daten = pd.read_csv(csv_datei, sep=";")
    zeilen = daten.values.tolist()

    verbindung = sqlite3.connect(db_datei)
    verbindung.execute("DROP TABLE IF EXISTS nutzungen")
    verbindung.execute("""
        CREATE TABLE nutzungen (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            gruppe   TEXT NOT NULL,
            nutzung  TEXT NOT NULL,
            standard TEXT NOT NULL,
            einheit  TEXT NOT NULL,
            vw_l     REAL NOT NULL,
            sigma_v  REAL NOT NULL,
            qw_kwh   REAL NOT NULL,
            sigma_q  REAL NOT NULL
        )
    """)
    verbindung.executemany(
        "INSERT INTO nutzungen (gruppe, nutzung, standard, einheit, vw_l, sigma_v, qw_kwh, sigma_q) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        zeilen,
    )
    verbindung.commit()
    verbindung.close()


def verbinden(db_datei=DB_DATEI):
    """Öffnet die Datenbank. Gibt es sie noch nicht, wird sie zuerst erstellt."""
    if not Path(db_datei).exists():
        datenbank_erstellen(db_datei)
    return sqlite3.connect(db_datei)


def gruppen_laden(db_datei=DB_DATEI):
    """Liste aller Gruppen (Wohnen, Büro, Gastronomie …) in der Reihenfolge der Tabelle."""
    verbindung = verbinden(db_datei)
    zeilen = verbindung.execute(
        "SELECT gruppe FROM nutzungen GROUP BY gruppe ORDER BY MIN(id)"
    ).fetchall()
    verbindung.close()
    return [zeile[0] for zeile in zeilen]


def nutzungen_laden(gruppe, db_datei=DB_DATEI):
    """Alle Nutzungen einer Gruppe als pandas-Tabelle."""
    verbindung = verbinden(db_datei)
    tabelle = pd.read_sql(
        "SELECT * FROM nutzungen WHERE gruppe = ? ORDER BY id",
        verbindung,
        params=(gruppe,),
    )
    verbindung.close()
    return tabelle
