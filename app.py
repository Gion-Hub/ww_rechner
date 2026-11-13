"""Streamlit-Oberfläche. Nur Eingaben und Anzeige, keine Formeln."""

import pandas as pd
import streamlit as st

from wwrechner.berechnung import spitzenstunde, tagesbedarf_liter, verbrauch_pro_stunde, waermebedarf_kwh
from wwrechner.diagramme import tagesprofil_diagramm
from wwrechner.tabellen import PROFIL_WOHNEN, T_KALTWASSER, T_WARMWASSER


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