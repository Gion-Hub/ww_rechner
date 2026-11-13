"""Streamlit-Oberfläche. Nur Eingaben und Anzeige, keine Formeln."""

import streamlit as st

from wwrechner.berechnung import tagesbedarf_liter, waermebedarf_kwh
from wwrechner.tabellen import T_KALTWASSER, T_WARMWASSER

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
