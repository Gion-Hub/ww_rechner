"""Streamlit-Oberfläche. Nur Eingaben und Anzeige, keine Formeln."""

import pandas as pd
import streamlit as st

from wwrechner.berechnung import (
    ausstossverlust_kwh,
    bereitschaftsvolumen_kwh,
    speicher_genuegt,
    speicherverlust_kwh,
    speichervolumen_erforderlich_l,
    spitzenstunde,
    stundenspitze_anteil,
    tagesbedarf_liter,
    verbrauch_pro_stunde,
    waermebedarf_gesamt_kwh,
    waermebedarf_kwh,
    zirkulationsverlust_kwh,
)
from wwrechner.diagramme import tagesprofil_diagramm
from wwrechner.tabellen import F_STO, PROFIL_WOHNEN, T_KALTWASSER, T_WARMWASSER


st.title("Warmwasser-Rechner SIA 385/2")
st.caption("Trinkwarmwasser-Speicherauslegung · Philipp & Gion")

# --- Eingaben ---
st.header("Eingaben")
personen = st.number_input("Anzahl Personen", min_value=1, max_value=500, value=8)
liter_pro_person = st.number_input("Warmwasser pro Person [l/Tag]", min_value=10, max_value=200, value=40)
t_warm = st.number_input("Warmwassertemperatur [°C]", min_value=40, max_value=80, value=T_WARMWASSER)
t_kalt = st.number_input("Kaltwassertemperatur [°C]", min_value=0, max_value=30, value=T_KALTWASSER)

# --- Berechnung: nur Funktionen aus wwrechner aufrufen ---
bedarf = tagesbedarf_liter(personen, liter_pro_person)
energie = waermebedarf_kwh(bedarf, t_warm, t_kalt)

# --- Ergebnisse ---
st.header("Ergebnisse")
spalte1, spalte2 = st.columns(2)
spalte1.metric("Tagesbedarf", f"{bedarf} l/Tag")
spalte2.metric("Wärmebedarf", f"{energie:.2f} kWh/Tag")


# --- Tagesprofil ---
st.header("Tagesprofil")
stunden_liter = verbrauch_pro_stunde(bedarf, PROFIL_WOHNEN)
stunde, liter = spitzenstunde(stunden_liter)

st.metric("Spitzenstunde", f"{stunde:02d}–{stunde + 1:02d} Uhr", f"{liter:.1f} l/h", delta_color="off")
st.pyplot(tagesprofil_diagramm(stunden_liter))

tabelle = pd.DataFrame({"Stunde": range(24), "Verbrauch [l/h]": stunden_liter})
st.dataframe(tabelle.round(1), hide_index=True)



# --- Stundenspitze und Verluste ---
st.header("Stundenspitze und Verluste")
wohnungen = st.number_input("Anzahl Wohnungen", min_value=1, max_value=200, value=4)
zirk_laenge = st.number_input("Länge Zirkulationsleitung [m]", min_value=0, max_value=2000, value=50)
warmhaltung = st.checkbox("Mit Warmhaltung (Zirkulation)", value=True)

anteil = stundenspitze_anteil(personen)
spitze_liter = bedarf * anteil
q_zirk = zirkulationsverlust_kwh(zirk_laenge)
q_ausstoss = ausstossverlust_kwh(wohnungen, warmhaltung)

st.metric("Stundenspitze SIA 385/2", f"{spitze_liter:.0f} l/h", f"{anteil * 100:.1f} % des Tagesbedarfs", delta_color="off")


# --- Speicherauslegung ---
st.header("Speicherauslegung")
speicherart = st.selectbox("Ladeart des Speichers", list(F_STO.keys()))
f_sto = F_STO[speicherart]
ladezyklen = st.number_input("Ladezyklen pro Tag", min_value=1, max_value=24, value=2)
v_gewaehlt = st.number_input("Gewählter Speicher [l]", min_value=50, max_value=10000, value=500, step=50)

# Berechnung: Verluste mit dem gewählten Speicher, daraus das erforderliche Volumen
q_speicher = speicherverlust_kwh(v_gewaehlt)
q_gesamt = waermebedarf_gesamt_kwh(energie, q_speicher, q_zirk, q_ausstoss)
q_bereit = bereitschaftsvolumen_kwh(energie, anteil, q_gesamt, ladezyklen)
v_erf = speichervolumen_erforderlich_l(q_bereit, t_warm, t_kalt, f_sto)

v1, v2, v3 = st.columns(3)
v1.metric("Zirkulation", f"{q_zirk:.2f} kWh/d")
v2.metric("Ausstoss", f"{q_ausstoss:.2f} kWh/d")
v3.metric("Speicher", f"{q_speicher:.2f} kWh/d")

e1, e2, e3 = st.columns(3)
e1.metric("Wärmebedarf gesamt", f"{q_gesamt:.2f} kWh/d")
e2.metric("Bereitschaftsvolumen", f"{q_bereit:.2f} kWh")
e3.metric("f_sto", f"{f_sto:.2f}")

if speicher_genuegt(v_gewaehlt, v_erf):
    st.success(f"Erforderlich: {v_erf:.0f} l · Gewählt: {v_gewaehlt} l → Nachweis erfüllt")
else:
    st.error(f"Erforderlich: {v_erf:.0f} l · Gewählt: {v_gewaehlt} l → Speicher zu klein, grösseren Typ wählen")