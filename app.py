"""Streamlit-Oberfläche. Nur Eingaben und Anzeige, keine Formeln."""

import pandas as pd
import streamlit as st

from wwrechner.berechnung import (
    ausstossverlust_kwh,
    bereitschaftsvolumen_kwh,
    endenergie_kwh,
    endenergie_jahr_kwh,
    ladeleistung_kw,
    speicher_genuegt,
    speicherverlust_kwh,
    speichervolumen_erforderlich_l,
    spitzenstunde,
    stundenspitze_anteil,
    tagesbedarf_liter,
    verbrauch_pro_stunde,
    waermebedarf_gesamt_kwh,
    waermebedarf_kwh,
    wirkungsgrad_holz,
    zirkulationsverlust_kwh,
)
from wwrechner.diagramme import tagesprofil_diagramm
from wwrechner.tabellen import ETA_HOLZ_WW, F_STO, PROFIL_WOHNEN, T_KALTWASSER, T_WARMWASSER


st.set_page_config(page_title="Warmwasser-Rechner SIA 385/2", layout="wide")
st.title("Warmwasser-Rechner SIA 385/2")
st.caption("Trinkwarmwasser-Speicherauslegung · Philipp & Gion")

tab_bedarf, tab_grob, tab_fein, tab_erzeuger = st.tabs(
    ["① Bedarf", "② Grobauslegung", "③ Feinauslegung", "④ Wärmeerzeuger"]
)


# =====================================================================
# ① Bedarf
# =====================================================================
with tab_bedarf:
    st.header("Warmwasserbedarf")

    links, rechts = st.columns(2)
    with links:
        st.subheader("Nutzung")
        wohnungen = st.number_input("Anzahl Wohnungen", min_value=1, max_value=200, value=4)
        personen = st.number_input("Anzahl Personen", min_value=1, max_value=500, value=8)
        liter_pro_person = st.number_input("Warmwasser pro Person [l/Tag]", min_value=10, max_value=200, value=40)
    with rechts:
        st.subheader("Temperaturen")
        t_warm = st.number_input("Warmwassertemperatur [°C]", min_value=40, max_value=80, value=T_WARMWASSER)
        t_kalt = st.number_input("Kaltwassertemperatur [°C]", min_value=0, max_value=30, value=T_KALTWASSER)

    bedarf = tagesbedarf_liter(personen, liter_pro_person)
    energie = waermebedarf_kwh(bedarf, t_warm, t_kalt)

    st.divider()
    k1, k2 = st.columns(2)
    k1.metric("Tagesbedarf", f"{bedarf} l/d")
    k2.metric("Wärmebedarf (Nutzwärme) QW", f"{energie:.2f} kWh/d")

    st.subheader("Tagesprofil")
    stunden_liter = verbrauch_pro_stunde(bedarf, PROFIL_WOHNEN)
    stunde, liter = spitzenstunde(stunden_liter)

    st.metric("Spitzenstunde", f"{stunde:02d}–{stunde + 1:02d} Uhr", f"{liter:.1f} l/h", delta_color="off")
    st.pyplot(tagesprofil_diagramm(stunden_liter))

    tabelle = pd.DataFrame(
        [stunden_liter],
        index=["Verbrauch [l/h]"],
        columns=[f"{h:02d}" for h in range(24)],
    )
    st.dataframe(tabelle.round(0), use_container_width=True)


# =====================================================================
# ② Grobauslegung (Vorprojekt)
# =====================================================================
with tab_grob:
    st.header("Grobauslegung (Vorprojekt)")
    st.info("In Arbeit: Speicherabschätzung, Warmhaltekonzepte, Verlustzahl ξ und Ausstosszeiten.")


# =====================================================================
# ③ Feinauslegung (Bauprojekt)
# =====================================================================
with tab_fein:
    st.header("Feinauslegung (Bauprojekt)")

    links, rechts = st.columns(2)
    with links:
        st.subheader("Warmhaltung")
        warmhaltung = st.checkbox("Mit Warmhaltung (Zirkulation)", value=True)
        zirk_laenge = st.number_input("Länge Zirkulationsleitung [m]", min_value=0, max_value=2000, value=50)
    with rechts:
        st.subheader("Speicher")
        speicherart = st.selectbox("Ladeart des Speichers", list(F_STO.keys()))
        f_sto = F_STO[speicherart]
        ladezyklen = st.number_input("Ladezyklen pro Tag", min_value=1, max_value=24, value=2)
        v_gewaehlt = st.number_input("Gewählter Speicher [l]", min_value=50, max_value=10000, value=500, step=50)

    # Berechnung: Verluste mit dem gewählten Speicher, daraus das erforderliche Volumen
    anteil = stundenspitze_anteil(personen)
    spitze_liter = bedarf * anteil
    q_zirk = zirkulationsverlust_kwh(zirk_laenge)
    q_ausstoss = ausstossverlust_kwh(wohnungen, personen / wohnungen, warmhaltung)
    q_speicher = speicherverlust_kwh(v_gewaehlt)
    q_gesamt = waermebedarf_gesamt_kwh(energie, q_speicher, q_zirk, q_ausstoss)
    q_bereit = bereitschaftsvolumen_kwh(energie, anteil, q_gesamt, ladezyklen)
    v_erf = speichervolumen_erforderlich_l(q_bereit, t_warm, t_kalt, f_sto)

    st.divider()
    st.subheader("Wärmeverluste")
    v1, v2, v3 = st.columns(3)
    v1.metric("Zirkulation", f"{q_zirk:.2f} kWh/d")
    v2.metric("Ausstoss", f"{q_ausstoss:.2f} kWh/d")
    v3.metric("Speicher", f"{q_speicher:.2f} kWh/d")

    st.subheader("Speichervolumen")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Stundenspitze", f"{spitze_liter:.0f} l/h", f"{anteil * 100:.1f} % des Tagesbedarfs", delta_color="off")
    e2.metric("Wärmebedarf gesamt", f"{q_gesamt:.2f} kWh/d")
    e3.metric("Bereitschaftsvolumen", f"{q_bereit:.2f} kWh")
    e4.metric("f_sto", f"{f_sto:.2f}")

    if speicher_genuegt(v_gewaehlt, v_erf):
        st.success(f"Erforderlich: {v_erf:.0f} l · Gewählt: {v_gewaehlt} l → Nachweis erfüllt")
    else:
        st.error(f"Erforderlich: {v_erf:.0f} l · Gewählt: {v_gewaehlt} l → Speicher zu klein, grösseren Typ wählen")


# =====================================================================
# ④ Wärmeerzeuger
# =====================================================================
with tab_erzeuger:
    st.header("Wärmeerzeuger")

    links, rechts = st.columns(2)
    with links:
        st.subheader("Ladung")
        ladezeit = st.number_input("Ladezeit pro Ladung [h]", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
    with rechts:
        st.subheader("Holzfeuerung")
        brennstoff = st.selectbox("Brennstoff", list(ETA_HOLZ_WW.keys()))
        kondensation = st.checkbox("Mit Abgaskondensation")
        modulierend = st.checkbox("Modulierender / mehrstufiger Brenner")

    eta = wirkungsgrad_holz(brennstoff, kondensation, modulierend)
    phi_gen = ladeleistung_kw(q_gesamt, ladezyklen, ladezeit)

    st.divider()
    st.metric("Ladeleistung ΦW,gen", f"{phi_gen:.1f} kW")

    if eta is None:
        st.warning(f"{brennstoff} ist in Abb. 22 nicht mit modulierendem Brenner aufgeführt.")
    else:
        e_tag = endenergie_kwh(q_gesamt, eta)
        w1, w2, w3 = st.columns(3)
        w1.metric("Nutzungsgrad η_per,W", f"{eta:.2f}")
        w2.metric("Endenergie pro Tag", f"{e_tag:.1f} kWh/d")
        w3.metric("Endenergie pro Jahr", f"{endenergie_jahr_kwh(e_tag):,.0f} kWh/a".replace(",", "'"))
