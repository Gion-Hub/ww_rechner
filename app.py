"""Streamlit-Oberfläche. Nur Eingaben und Anzeige, keine Formeln."""

import pandas as pd
import streamlit as st

from wwrechner.berechnung import (
    aufrunden,
    ausstossverlust_kwh,
    ausstosszeit_s,
    bedarf_mit_streuung,
    bereitschaftsvolumen_kwh,
    endenergie_kwh,
    endenergie_jahr_kwh,
    ladeleistung_kw,
    leitungsinhalt_l,
    normbelegung,
    reserve_ladezeit_kwh,
    speicher_genuegt,
    speicherverlust_kwh,
    speichervolumen_erforderlich_l,
    spitzenstunde,
    stundenspitze_formel_kwh,
    stundenspitze_zapfung_kwh,
    tagesvolumen_grob_l,
    verbrauch_pro_stunde,
    waermebedarf_gesamt_kwh,
    waermebedarf_grob_kwh,
    waermebedarf_kwh,
    warmhaltekonzept_auswerten,
    wirkungsgrad_holz,
    zirkulationsverlust_kwh,
)
from wwrechner.datenbank import gruppen_laden, nutzungen_laden
from wwrechner.diagramme import ladeverlauf_diagramm, speicher_einzeln, speicher_schema, tagesprofil_diagramm
from wwrechner.ladung import ladung_auswerten, ladung_simulieren
from wwrechner.tabellen import (
    AUSSTOSSZEIT_MIT_WARMHALTUNG,
    AUSSTOSSZEIT_OHNE_WARMHALTUNG,
    DAEMMUNG_SPEICHER,
    DURCHFLUSS_ARMATUR,
    ETA_HOLZ_WW,
    F_STO,
    PROFIL_WOHNEN,
    PUMPE,
    STANDARD_SPITZE_L,
    T_KALTWASSER,
    T_WARMWASSER,
    VERLUSTZAHL_GRENZWERT,
    VERLUSTZAHL_ZIELWERT,
    WAERMEBEDARF_GROB,
    WARMHALTEKONZEPTE,
)

st.set_page_config(page_title="Warmwasser-Rechner SIA 385/2", layout="wide")

# Kompakte Darstellung: kleinere Titel, Kennzahlen und Abstände, damit möglichst wenig gescrollt werden muss
KOMPAKT_CSS = """
<style>
.block-container {padding-top: 3.2rem; padding-bottom: 1rem;}
h1 {font-size: 1.5rem !important; padding: 0 !important;}
h2 {font-size: 1.15rem !important; padding: 0.1rem 0 0.2rem 0 !important;}
h3 {font-size: 0.95rem !important; padding: 0.3rem 0 0.25rem 0 !important;}
[data-testid="stVerticalBlock"] {gap: 0.5rem;}
[data-testid="stMetricValue"] {font-size: 1.25rem;}
[data-testid="stMetricLabel"] p, [data-testid="stWidgetLabel"] p {font-size: 0.8rem;}
[data-testid="stAlertContainer"] {padding: 0.45rem 0.8rem;}
[data-testid="stAlertContainer"] p, [data-testid="stCaptionContainer"] p {font-size: 0.8rem;}
</style>
"""
st.markdown(KOMPAKT_CSS, unsafe_allow_html=True)

st.title("Warmwasser-Rechner SIA 385/2")
st.caption("Trinkwarmwasser-Speicherauslegung · Philipp & Gion")

tab_bedarf, tab_grob, tab_fein, tab_erzeuger = st.tabs(
    ["① WW-Tagesbedarf", "② Speicher (Grobauslegung)", "③ Speicher (Feinauslegung)", "④ Wärmeerzeugung und Ladeprinzip"]
)


# =====================================================================
# ① WW-Tagesbedarf
# =====================================================================
with tab_bedarf:
    st.info(
    "Ausgangspunkt jeder Auslegung: Wie viel Warmwasser braucht das Gebäude pro Tag? "
    "Aus Nutzung und Belegung ergeben sich Tagesbedarf, Wärmebedarf und Tagesprofil. "
    "Die Werte fliessen in die Grob- und Feinauslegung ein."
    )
    eingabe, ergebnis, grafik = st.columns([1, 1, 2.6])
    with eingabe:
        st.subheader("Nutzung")
        gruppe = st.selectbox("Gruppe", gruppen_laden())
        nutzungen = nutzungen_laden(gruppe)
        bezeichnungen = (nutzungen["nutzung"] + " – " + nutzungen["standard"]).tolist()
        wahl = st.selectbox("Nutzung", bezeichnungen)
        nutzung = nutzungen.iloc[bezeichnungen.index(wahl)]

        anzahl_be = st.number_input(f"Anzahl {nutzung['einheit']}", min_value=1, max_value=5000, value=8)
        wohnungen = st.number_input("Anzahl Wohnungen", min_value=1, max_value=200, value=4)
        if nutzung["einheit"] == "Person":
            personen = anzahl_be
        else:
            personen = st.number_input("Anzahl Personen", min_value=1, max_value=5000, value=8)
    with ergebnis:
        st.subheader("Temperaturen")
        t_warm = st.number_input("Warmwassertemperatur [°C]", min_value=40, max_value=80, value=T_WARMWASSER)
        t_kalt = st.number_input("Kaltwassertemperatur [°C]", min_value=0, max_value=30, value=T_KALTWASSER)

    bedarf = bedarf_mit_streuung(nutzung["vw_l"], nutzung["sigma_v"], anzahl_be)
    energie = waermebedarf_kwh(bedarf, t_warm, t_kalt)
    stunden_liter = verbrauch_pro_stunde(bedarf, PROFIL_WOHNEN)
    stunde, liter = spitzenstunde(stunden_liter)

    with grafik:
        k1, k2, k3 = st.columns(3)
        k1.metric("Tagesbedarf", f"{bedarf:.0f} l/d")
        k2.metric("Wärmebedarf (Nutzwärme) QW", f"{energie:.2f} kWh/d")
        k3.metric("Spitzenstunde", f"{stunde:02d}–{stunde + 1:02d} Uhr", f"{liter:.1f} l/h", delta_color="off")
        st.pyplot(tagesprofil_diagramm(stunden_liter))

    tabelle = pd.DataFrame(
        [stunden_liter],
        index=["Verbrauch [l/h]"],
        columns=[f"{h:02d}" for h in range(24)],
    )
    st.dataframe(tabelle.round(0), width="stretch")

    with st.expander(f"Kennwerte {gruppe} aus der Datenbank (SIA 385/2, Anhang A.3)"):
        st.dataframe(nutzungen, hide_index=True, width="stretch")


# =====================================================================
# ② Speicher (Grobauslegung, Vorprojekt)
# =====================================================================
with tab_grob:
    st.info(
    "Erste Abschätzung mit vereinfachten Kennwerten und wenigen Eingaben. "
    "Vergleich der Warmhaltekonzepte über die Verlustzahl ξ und Kontrolle der Ausstosszeiten. "
    "Ergebnis: Systementscheid als Grundlage für die Feinauslegung."
    )

    # --- Belegung, Wärmebedarf und Speicher (eine Zeile) ---
    st.subheader("Belegung, Wärmebedarf und Speicher")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1:
        nutzung_grob = st.selectbox("Nutzung (Abb. 13)", list(WAERMEBEDARF_GROB.keys()))
    with s2:
        belegung = st.radio("Personen bestimmen", ["Normbelegung aus Fläche", "Direkt eingeben"])
    with s3:
        if belegung == "Normbelegung aus Fläche":
            flaeche_we = st.number_input("Fläche pro Wohnung A_NF [m²]", min_value=20, max_value=1000, value=200, step=10)
            personen_pro_we = round(normbelegung(flaeche_we), 1)
            personen_grob = personen_pro_we * wohnungen
            st.caption(f"{personen_pro_we} P/WE × {wohnungen} WE = {personen_grob:.1f} P")
        else:
            personen_grob = st.number_input("Anzahl Personen", min_value=0.0, max_value=5000.0, value=float(personen), step=1.0)

    q_grob = waermebedarf_grob_kwh(personen_grob, WAERMEBEDARF_GROB[nutzung_grob])
    v_tag = tagesvolumen_grob_l(q_grob)

    with s4:
        v_grob = st.number_input(
            "Angenommenes Speichervolumen [l]", min_value=50, max_value=20000,
            value=aufrunden(v_tag), step=50, help="Startwert: V_W,d auf 100 l aufgerundet",
        )
    with s5:
        stutzen_grob = st.number_input("Wasserführende Stutzen n_cp", min_value=2, max_value=10, value=5)
    with s6:
        daemmung = st.radio("Speicherdämmung", list(DAEMMUNG_SPEICHER.keys()))

    if belegung == "Normbelegung aus Fläche" and nutzung_grob == "Büro":
        st.warning("Die Normbelegung gilt nur für Wohnungen. Für Büros Personen direkt eingeben.")

    q_sto_grob = speicherverlust_kwh(v_grob, stutzen_grob, DAEMMUNG_SPEICHER[daemmung])

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Personen n_P", f"{personen_grob:.1f}")
    g2.metric("Wärmebedarf Q'W", f"{q_grob:.1f} kWh/d")
    g3.metric("Tagesvolumen V_W,d", f"{v_tag:.0f} l/d")
    g4.metric("Speicherverlust Q'W,sto,ls", f"{q_sto_grob:.1f} kWh/d")

    links, rechts = st.columns([3, 2], gap="large")

    # --- Warmhaltekonzepte und Verlustzahl ---
    with links:
        st.subheader("Warmhaltekonzepte und Verlustzahl ξ")
        w1, w2, w3 = st.columns(3)
        with w1:
            vorlauf_we = st.number_input("Vorlauf pro WE l_WWV [m]", min_value=0.0, max_value=500.0, value=10.0, step=1.0)
        with w2:
            ruecklauf_we = st.number_input("Rücklauf pro WE l_WWR [m]", min_value=0.0, max_value=500.0, value=10.0, step=1.0,
                                           help="Zählt nur bei konventioneller Zirkulation")
        with w3:
            pumpenansatz = st.radio("Pumpenleistung", list(PUMPE.keys()), horizontal=True)

        zeilen = []
        for konzept in WARMHALTEKONZEPTE:
            r = warmhaltekonzept_auswerten(konzept, wohnungen, vorlauf_we, ruecklauf_we,
                                           q_sto_grob, q_grob, pumpenansatz)
            zeilen.append({
                "Konzept": konzept,
                "Länge [m]": r["laenge_m"],
                "Q'W,hl,ls [kWh/d]": r["q_warmhaltung"],
                "Pumpe [W]": r["pumpe_w"],
                "E'W,aux [kWh/d]": r["e_hilf"],
                "ξ [%]": r["xi"] * 100,
                "Grenzwert 50 %": "✓" if r["xi"] <= VERLUSTZAHL_GRENZWERT else "✗",
                "Zielwert 40 %": "✓" if r["xi"] <= VERLUSTZAHL_ZIELWERT else "✗",
            })
        vergleich = pd.DataFrame(zeilen)
        st.dataframe(vergleich.round(2), hide_index=True, width="stretch")

        konzept_gewaehlt = st.selectbox(
            "Gewähltes Warmhaltekonzept (für die Feinauslegung)", list(WARMHALTEKONZEPTE.keys()),
            index=int(vergleich["ξ [%]"].idxmin()),
            help="Vorgewählt ist das Konzept mit der kleinsten Verlustzahl",
        )

    # --- Ausstosszeiten ---
    with rechts:
        st.subheader("Ausstosszeit")
        st.caption("Ungünstigste Entnahmestelle: alle nicht warm gehaltenen Leitungsabschnitte bis zur Armatur.")
        abschnitte = st.data_editor(
            pd.DataFrame({
                "Abschnitt": ["Verteiler", "Ausstossleitung"],
                "Innendurchmesser [mm]": [16.0, 11.6],
                "Länge [m]": [4.0, 12.0],
            }),
            num_rows="dynamic", hide_index=True, width="stretch",
        )
        a1, a2 = st.columns(2)
        with a1:
            armatur = st.selectbox("Entnahmearmatur (Abb. 11)", list(DURCHFLUSS_ARMATUR.keys()), index=2)
        with a2:
            warm_gehalten = st.checkbox("Verteilleitungen warm gehalten", value=True)

        abschnitte = abschnitte.dropna()
        liste = list(zip(abschnitte["Innendurchmesser [mm]"], abschnitte["Länge [m]"]))
        inhalt = leitungsinhalt_l(liste)
        t_em = ausstosszeit_s(inhalt, DURCHFLUSS_ARMATUR[armatur])
        t_max = AUSSTOSSZEIT_MIT_WARMHALTUNG if warm_gehalten else AUSSTOSSZEIT_OHNE_WARMHALTUNG

        if t_em <= t_max:
            st.success(f"Inhalt {inhalt:.2f} l → Ausstosszeit {t_em:.1f} s ≤ {t_max} s → Anforderung erfüllt")
        else:
            st.error(f"Inhalt {inhalt:.2f} l → Ausstosszeit {t_em:.1f} s > {t_max} s → Leitung kürzen, "
                     "Durchmesser verkleinern oder Warmhaltung näher an die Entnahmestelle")


# =====================================================================
# ③ Speicher (Feinauslegung, Bauprojekt)
# =====================================================================
with tab_fein:
    st.info(
    "Baut auf dem in der Grobauslegung gewählten System auf. "
    "Detaillierte Wärmebilanz: Nutzwärme plus Speicher-, Leitungs- und Ausstossverluste. "
    "Bestimmung von Stundenspitze, Ladestrategie und Speichervolumen mit Nachweis."
    )

    f1, f2, f3, f4 = st.columns(4, gap="medium")
    with f1:
        st.subheader("Warmhaltung")
        warmhaltung = st.checkbox("Mit Warmhaltung (Zirkulation)", value=True)
        zirk_laenge = st.number_input("Länge Zirkulationsleitung [m]", min_value=0, max_value=2000, value=50)
    with f2:
        st.subheader("Speicher")
        speicherart = st.selectbox("Ladeart des Speichers", list(F_STO.keys()))
        f_sto = F_STO[speicherart]
        v_gewaehlt = st.number_input("Gewählter Speicher [l]", min_value=50, max_value=10000, value=500, step=50)
    with f3:
        st.subheader("Ladestrategie")
        ladezyklen = st.number_input("Ladezyklen pro Tag", min_value=1, max_value=24, value=2)
        ladezeit = st.number_input("Ladezeit pro Ladung [h]", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
        ladeart = st.radio("Ladeprinzip (Skript B4, Kap. 4.6)", ["Schichtladung", "Stufenladung"], horizontal=True,
                           help="Stufenladung: Wärme erst am Ladeende nutzbar → Reserve für die Ladezeit nötig")
    with f4:
        st.subheader("Stundenspitze")
        methode = st.selectbox("Methode", ["Formel SIA 385/2", "Zapfmenge in der Spitzenstunde", "Direkte Eingabe"],
                               index=0 if personen >= 10 else 1,
                               help="Die Formel gilt nur für Wohnen ab 10 Personen")
        if methode == "Formel SIA 385/2":
            if personen < 10:
                st.warning("Die Formel gilt erst ab 10 Personen. Für kleine Gebäude die Zapfmenge verwenden.")
            q_spitze = stundenspitze_formel_kwh(energie, personen)
        elif methode == "Zapfmenge in der Spitzenstunde":
            spitze_l = st.number_input("Zapfmenge in der stärksten Stunde [l]", min_value=0, max_value=10000,
                                       value=STANDARD_SPITZE_L, step=10,
                                       help="Startwert: Badewanne 110 l + 2 Duschen à 30 l")
            q_spitze = stundenspitze_zapfung_kwh(spitze_l)
        else:
            q_spitze = st.number_input("Stundenspitze QW,pk [kWh]", min_value=0.0, max_value=1000.0, value=10.0, step=0.5)

    # Berechnung: Verluste mit dem gewählten Speicher, daraus das erforderliche Volumen
    q_zirk = zirkulationsverlust_kwh(zirk_laenge)
    q_ausstoss = ausstossverlust_kwh(wohnungen, personen / wohnungen, warmhaltung)
    q_speicher = speicherverlust_kwh(v_gewaehlt)
    q_gesamt = waermebedarf_gesamt_kwh(energie, q_speicher, q_zirk, q_ausstoss)
    q_bereit = bereitschaftsvolumen_kwh(q_spitze, q_gesamt, ladezyklen)
    q_reserve = reserve_ladezeit_kwh(q_gesamt, ladezeit) if ladeart == "Stufenladung" else 0
    q_bereit = q_bereit + q_reserve
    v_erf = speichervolumen_erforderlich_l(q_bereit, t_warm, t_kalt, f_sto)

    st.subheader("Wärmeverluste und Speichervolumen")
    e1, e2, e3, e4, e5, e6, e7 = st.columns(7)
    e1.metric("Zirkulation", f"{q_zirk:.2f} kWh/d")
    e2.metric("Ausstoss", f"{q_ausstoss:.2f} kWh/d")
    e3.metric("Speicher", f"{q_speicher:.2f} kWh/d")
    e4.metric("Wärmebedarf gesamt", f"{q_gesamt:.2f} kWh/d")
    e5.metric("Stundenspitze QW,pk", f"{q_spitze:.2f} kWh", methode, delta_color="off")
    e6.metric("Bereitschaftsvolumen", f"{q_bereit:.2f} kWh",
              f"davon Reserve Stufenladung {q_reserve:.2f} kWh" if q_reserve else None, delta_color="off")
    e7.metric("f_sto", f"{f_sto:.2f}")

    if speicher_genuegt(v_gewaehlt, v_erf):
        st.success(f"Erforderlich: {v_erf:.0f} l · Gewählt: {v_gewaehlt} l → Nachweis erfüllt")
    else:
        st.error(f"Erforderlich: {v_erf:.0f} l · Gewählt: {v_gewaehlt} l → Speicher zu klein, grösseren Typ wählen")


# =====================================================================
# ④ Wärmeerzeugung und Ladeprinzip
# =====================================================================
with tab_erzeuger:
    st.info(
    "Übernimmt Wärmebedarf und Ladestrategie aus der Feinauslegung, bestimmt die Ladeleistung "
    "und simuliert den Ladeverlauf im Speicher (Schicht- vs. Stufenladung). "
    "Vergleicht Wärmeerzeuger über Nutzungsgrad bzw. COP und Endenergie pro Tag und Jahr."
    )

    phi_gen = ladeleistung_kw(q_gesamt, ladezyklen, ladezeit)

    # --- Eingaben in einer Zeile ---
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        erzeuger = st.radio("Wärmeerzeuger", ["Wärmepumpe", "Holzfeuerung"])
    if erzeuger == "Holzfeuerung":
        with c2:
            brennstoff = st.selectbox("Brennstoff", list(ETA_HOLZ_WW.keys()))
        with c3:
            kondensation = st.checkbox("Mit Abgaskondensation")
            modulierend = st.checkbox("Modulierender Brenner")
    else:
        with c2:
            t_quelle = st.number_input("Quellentemperatur [°C]", min_value=-20.0, max_value=20.0, value=0.0, step=1.0,
                                       help="Erdsonde ca. 0 °C, Aussenluft im Jahresmittel ca. 5 °C")
        with c3:
            st.caption("COP = Gütegrad · T_VL / (T_VL − T_Quelle), T in Kelvin. "
                       "Gütegrad und Mindest-Kondensationstemperatur in tabellen.py")
    with c4:
        anteil_warm = st.slider("Warmer Anteil beim Ladestart [%]", 0, 80, 20, step=5,
                                help="Restinhalt über dem Fühler EIN (Spitzendeckung)") / 100
    with c5:
        zapfung = st.number_input("Zapfung während der Ladung [l/h]", min_value=0, max_value=500, value=0, step=10,
                                  help="Skript S. 47: Gleichzeitiger Bezug stört vor allem die Stufenladung")
    with c6:
        anzeige = st.radio("Ladeprinzip anzeigen", ["Schichtladung", "Stufenladung"],
                           index=["Schichtladung", "Stufenladung"].index(ladeart))

    # --- Simulation beider Ladeprinzipien ---
    t_q = t_quelle if erzeuger == "Wärmepumpe" else 0
    verlaeufe = {}
    for art in ["Schichtladung", "Stufenladung"]:
        verlaeufe[art] = ladung_simulieren(art, v_gewaehlt, phi_gen, t_warm, t_kalt, t_q,
                                           anteil_warm=anteil_warm, zapfung_l_h=zapfung)
    auswertung = {art: ladung_auswerten(v, t_warm) for art, v in verlaeufe.items()}
    verlauf = verlaeufe[anzeige]
    a = auswertung[anzeige]

    # --- Kennzahlen inkl. Endenergie in einer Zeile ---
    if erzeuger == "Holzfeuerung":
        eta = wirkungsgrad_holz(brennstoff, kondensation, modulierend)
        name_eta = "Nutzungsgrad η_per,W"
    else:
        eta = auswertung[ladeart]["cop_mittel"]
        name_eta = f"COP ({ladeart})"

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Ladeleistung ΦW,gen", f"{phi_gen:.1f} kW", f"{ladezyklen} Ladungen à {ladezeit} h", delta_color="off")
    m2.metric(f"Ladedauer ({anzeige})", f"{a['dauer_min']} min", f"{a['dauer_min'] / 60:.1f} h", delta_color="off")
    if eta is None:
        m3.metric(name_eta, "–")
        st.warning(f"{brennstoff} ist in Abb. 22 nicht mit modulierendem Brenner aufgeführt.")
    else:
        e_tag = endenergie_kwh(q_gesamt, eta)
        m3.metric(name_eta, f"{eta:.2f}")
        m4.metric("Endenergie pro Tag", f"{e_tag:.1f} kWh/d")
        m5.metric("Endenergie pro Jahr", f"{endenergie_jahr_kwh(e_tag):,.0f} kWh/a".replace(",", "'"))
    if not a["fertig"]:
        st.warning("Ladung nach 10 h nicht abgeschlossen: Zapfung zu gross oder Leistung zu klein.")

    # --- Ladeverlauf: Speicher zum Zeitpunkt, Temperaturverlauf, Übersicht ---
    minute = st.slider("Zeitpunkt [min]", 0, verlauf[-1]["minute"], verlauf[-1]["minute"] // 3)
    bild1, bild2, bild3 = st.columns([0.9, 3.2, 3.0])
    with bild1:
        st.pyplot(speicher_einzeln(verlauf[minute]["temp"], anzeige, t_kalt, t_warm, f"{minute} min"))
    with bild2:
        st.pyplot(ladeverlauf_diagramm(verlauf, anzeige, markierung=minute))
    with bild3:
        st.pyplot(speicher_schema(verlauf, anzeige, t_kalt, t_warm))

    vergleich = pd.DataFrame({
        "Ladeprinzip": list(verlaeufe),
        "Ladedauer [min]": [auswertung[x]["dauer_min"] for x in verlaeufe],
        "Wärme [kWh]": [auswertung[x]["waerme_kwh"] for x in verlaeufe],
        "Strom WP [kWh]": [auswertung[x]["strom_kwh"] for x in verlaeufe],
        "COP Mittel [-]": [auswertung[x]["cop_mittel"] for x in verlaeufe],
        "Min. Temperatur oben T1 [°C]": [auswertung[x]["t_oben_min"] for x in verlaeufe],
    })
    tab_links, tab_rechts = st.columns([3, 1])
    with tab_links:
        st.dataframe(vergleich.round(2), hide_index=True, width="stretch")
    with tab_rechts:
        if erzeuger == "Wärmepumpe":
            gewinn = auswertung["Stufenladung"]["cop_mittel"] / auswertung["Schichtladung"]["cop_mittel"] - 1
            st.caption(f"Stufenladung ist in dieser Simulation {gewinn * 100:.0f} % effizienter "
                       "(Skript: 15–20 %, gemessen).")
