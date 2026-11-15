"""Konstanten und Normwerte. Nur Daten, keine Berechnungen."""

# Physik
C_WASSER = 1.163  # Wh pro Liter und Kelvin

# Standard-Temperaturen
T_WARMWASSER = 60  # °C
T_KALTWASSER = 10  # °C


# Nutzungsprofil Wohnungsbau Mo-Fr nach SIA 385/2
# Anteil am Tagesbedarf in Prozent, je Stunde von 00-01 Uhr bis 23-24 Uhr
PROFIL_WOHNEN = [
    1.698, 0.899, 0.4995, 0.2997, 0.3996, 0.5994,   # 00-06 Uhr
    3.2967, 6.1938, 8.3916, 5.7942, 4.9950, 4.9950,  # 06-12 Uhr
    5.7942, 5.9940, 4.6953, 4.0959, 3.7962, 4.4955,  # 12-18 Uhr
    5.5944, 6.5934, 6.3936, 6.0939, 4.9950, 3.3966,  # 18-24 Uhr
]


# --- Verluste nach SIA 385/2 ---
# Zirkulation: Wärmeverlust pro Meter Leitung und Tag
VERLUST_ZIRKULATION = 0.12  # kWh/(m·d), konventionelle Zirkulation

# Ausstossverluste Wohnen: Wärme pro Zapfung, bis das Wasser warm kommt
AUSSTOSS_MIT_WARMHALTUNG = 0.10   # kWh pro Entnahme
AUSSTOSS_OHNE_WARMHALTUNG = 0.14  # kWh pro Entnahme

# Speicherverlust: 0.11 · √V  plus Zuschlag je Anschlussstutzen über 2
SPEICHER_VERLUST_FAKTOR = 0.11  # kWh/d pro √Liter
STUTZEN_ZUSCHLAG = 0.1          # kWh/d pro zusätzlichem Stutzen

# Faktor f_sto je nach Ladeart des Speichers (Handout, Abb. 21)
F_STO = {
    "Innenliegender Wärmeübertrager": 1.25,
    "Externer Wärmeübertrager mit Misch- und Kaltzone": 1.10,
    "Externer Wärmeübertrager ohne Misch- und Kaltzone": 1.00,
}

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