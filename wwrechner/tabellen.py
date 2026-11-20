"""Konstanten und Normwerte. Nur Daten, keine Berechnungen."""


# =====================================================================
# Allgemein
# =====================================================================

# Physik
C_WASSER = 1.163  # Wh pro Liter und Kelvin

# Umrechnung Volumen -> Wärme: 1 l von 10 auf 60 °C (Norm, gerundet)
KWH_PRO_LITER = 0.058  # kWh/l

# Standard-Temperaturen
T_WARMWASSER = 60  # °C
T_KALTWASSER = 10  # °C


# =====================================================================
# ① Bedarf
# =====================================================================

# Nutzungsprofil Wohnungsbau Mo-Fr nach SIA 385/2
# Anteil am Tagesbedarf in Prozent, je Stunde von 00-01 Uhr bis 23-24 Uhr
PROFIL_WOHNEN = [
    1.698, 0.899, 0.4995, 0.2997, 0.3996, 0.5994,   # 00-06 Uhr
    3.2967, 6.1938, 8.3916, 5.7942, 4.9950, 4.9950,  # 06-12 Uhr
    5.7942, 5.9940, 4.6953, 4.0959, 3.7962, 4.4955,  # 12-18 Uhr
    5.5944, 6.5934, 6.3936, 6.0939, 4.9950, 3.3966,  # 18-24 Uhr
]


# =====================================================================
# ② Grobauslegung (Vorprojekt)
# =====================================================================

# Normbelegung Wohnen: n_P = 3.3 - 2 / (1 + (A_NF / A_0)^3)
BEZUGSFLAECHE = 100  # m², A_0

# Wärmebedarf Warmwasser pro Person für die Grobauslegung (Handout Abb. 13)
WAERMEBEDARF_GROB = {   # kWh/(P·d), 60 °C
    "EFH / Eigentumswohnung": 2.32,
    "MFH / Mietwohnung": 2.03,
    "Büro": 0.174,
}

# Erste Annahme: Wärmeverluste Speicher + Verteilung = +50 %
ZUSCHLAG_VERLUSTE_GROB = 1.5

# Dämmung Speicher (Handout S. 22): Faktor auf den Speicherverlust
DAEMMUNG_SPEICHER = {
    "Grenzwert": 1.00,
    "Zielwert": 0.73,
}

# Warmhaltekonzepte (Handout 4.2.3)
# verlust:       linearer Wärmeverlust in kWh/(m·d)
# mit_ruecklauf: True = Vor- und Rücklauf zählen (nur konventionelle Zirkulation)
# pumpe:         True = Umwälzpumpe, False = elektrisches Warmhalteband
# f_hl:          Gewichtung der Wärmeverluste in der Verlustzahl
WARMHALTEKONZEPTE = {
    "A: Konventionelle Zirkulation": {"verlust": 0.12, "mit_ruecklauf": True, "pumpe": True, "f_hl": 1.0},
    "B: Rohr-an-Rohr": {"verlust": 0.15, "mit_ruecklauf": False, "pumpe": True, "f_hl": 1.0},
    "C: Warmhalteband": {"verlust": 0.12, "mit_ruecklauf": False, "pumpe": False, "f_hl": 0.333},
}

# Elektrische Leistung Umwälzpumpe: Grundleistung + Leistung pro Meter Leitung (SIA 385/1)
PUMPE = {
    "Grenzwert": {"grund_w": 8, "pro_m_w": 0.20},
    "Zielwert": {"grund_w": 5, "pro_m_w": 0.16},
}

HILFSENERGIE_BAND = 2 / 3          # Warmhalteband: Hilfsenergie = 2/3 der Wärmeverluste
GEWICHTUNG_HILFSENERGIE = 2.5      # Strom zählt in der Verlustzahl 2.5-fach
VERLUSTZAHL_GRENZWERT = 0.50       # ξ_ls ≤ 50 %
VERLUSTZAHL_ZIELWERT = 0.40        # ξ_ls ≤ 40 %

# Ausstosszeiten (Handout 4.1.1)
# Durchfluss der Entnahmearmatur in l/s (Handout Abb. 11)
DURCHFLUSS_ARMATUR = {
    "Waschtisch": 0.1,
    "Dusche": 0.2,
    "Spültisch": 0.2,
    "Badewanne": 0.3,
}
AUSSTOSSZEIT_MIT_WARMHALTUNG = 10   # s, max. Wartezeit, wenn Verteilleitungen warm gehalten
AUSSTOSSZEIT_OHNE_WARMHALTUNG = 15  # s


# =====================================================================
# ③ Feinauslegung (Bauprojekt)
# =====================================================================

# Stundenspitze ohne Formel: Zapfmenge in der stärksten Stunde (Handout, kleine Gebäude)
# Annahme: Badewanne 110 l + 2 Duschen à 30 l
STANDARD_SPITZE_L = 170  # l

# Zirkulation: Wärmeverlust pro Meter Leitung und Tag
VERLUST_ZIRKULATION = 0.12  # kWh/(m·d), konventionelle Zirkulation

# Ausstossverluste Wohnen pro Entnahme in kWh (Handout Abb. 19)
# 10 s = mit Warmhaltung, 15 s = ohne Warmhaltung
# Verlust hängt vom Leitungsinhalt ab: Armaturen mit grösserem Durchfluss
# (Dusche, Spültisch 0.2 l/s) dürfen bei gleicher Ausstosszeit mehr Inhalt haben
# als der Waschtisch (0.1 l/s) -> mehr Wasser kühlt nach jeder Entnahme aus.
AUSSTOSS_10S = {"dusche": 0.10, "spueltisch": 0.10, "waschtisch": 0.05}
AUSSTOSS_15S = {"dusche": 0.15, "spueltisch": 0.14, "waschtisch": 0.08}

# Speicherverlust: 0.11 · √V  plus Zuschlag je Anschlussstutzen über 2
SPEICHER_VERLUST_FAKTOR = 0.11  # kWh/d pro √Liter
STUTZEN_ZUSCHLAG = 0.1          # kWh/d pro zusätzlichem Stutzen

# Faktor f_sto je nach Ladeart des Speichers (Handout, Abb. 21)
F_STO = {
    "Innenliegender Wärmeübertrager": 1.25,
    "Externer Wärmeübertrager mit Misch- und Kaltzone": 1.10,
    "Externer Wärmeübertrager ohne Misch- und Kaltzone": 1.00,
}


# =====================================================================
# ④ Wärmeerzeuger
# =====================================================================

# Nutzungsgrad Warmwasser η_per,W für Holzfeuerungen (Handout Abb. 22, SIA 384/3:2020)
# Schlüssel: (Abgaskondensation, modulierender Brenner)
ETA_HOLZ_WW = {
    "Pellets": {
        (True, True): 0.70, (True, False): 0.65,
        (False, True): 0.65, (False, False): 0.60,
    },
    "Hackschnitzel": {
        (True, True): 0.65, (True, False): 0.60,
        (False, True): 0.60, (False, False): 0.55,
    },
    "Stückholz": {  # nur ohne modulierenden Brenner
        (True, False): 0.60, (False, False): 0.55,
    },
}

# Umrechnung Tag -> Jahr (Handout 5.4)
TAGE_PRO_JAHR = 365
JAHRESFAKTOR = 0.8  # Jahresnutzungsgrad nach SIA 2024

# =====================================================================
# ④ Ladesimulation (Skript B4, Kap. 4.6 Stufen- vs. Schichtladung)
# =====================================================================

SCHICHTEN = 30                  # Speicher wird in 30 gleich grosse Schichten geteilt
FUEHLER_HOEHEN = [0.10, 0.30, 0.50, 0.70, 0.90]   # T1 … T5, Anteil der Höhe von oben
LADESTUTZEN_STUFE = 0.30        # Ladestutzen Stufenladung auf Höhe T2 (Abb. 25)
GRAEDIGKEIT_PWT = 2.0           # K, Plattentauscher (Skript S. 47: 1–2 K)
GUETEGRAD_WP = 0.45             # Gütegrad Wärmepumpe (Anteil am Carnot-COP), Annahme
T_KONDENSATION_MIN = 40.0       # °C, darunter steigt der COP nicht mehr, Annahme
DELTA_T_STUFE = 10.0            # K, Temperaturhub pro Durchgang bei Stufenladung (fester Volumenstrom)