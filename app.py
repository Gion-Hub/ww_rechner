"""Streamlit-Oberfläche. Nur Eingaben und Anzeige, keine Formeln."""

import pandas as pd
import streamlit as st

from wwrechner.berechnung import (
    aufrunden,
    ausstossverlust_kwh,
    ausstosszeit_s,
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
    stundenspitze_anteil,
    tagesbedarf_liter,
    tagesvolumen_grob_l,
    verbrauch_pro_stunde,
    waermebedarf_gesamt_kwh,
    waermebedarf_grob_kwh,
    waermebedarf_kwh,
    warmhaltekonzept_auswerten,
    wirkungsgrad_holz,
    zirkulationsverlust_kwh,
)

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
    T_KALTWASSER,
    T_WARMWASSER,
    VERLUSTZAHL_GRENZWERT,
    VERLUSTZAHL_ZIELWERT,
    WAERMEBEDARF_GROB,
    WARMHALTEKONZEPTE,
)

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
    st.info(
    "- Ausgangspunkt jeder Auslegung: Wie viel Warmwasser braucht das Gebäude pro Tag?\n"
    "- Aus Nutzung und Belegung ergeben sich Tagesbedarf, Wärmebedarf und Tagesprofil.\n"
    "- Die Werte fliessen in die Grob- und Feinauslegung ein."
    )
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
    st.dataframe(tabelle.round(0), width="stretch")


# =====================================================================
# ② Grobauslegung (Vorprojekt)
# =====================================================================
with tab_grob:
    st.header("Grobauslegung (Vorprojekt)")
    st.info(
    "- Erste Abschätzung mit vereinfachten Kennwerten und wenigen Eingaben.\n"
    "- Vergleich der Warmhaltekonzepte über die Verlustzahl ξ und Kontrolle der Ausstosszeiten.\n"
    "- Ergebnis: Systementscheid als Grundlage für die Feinauslegung."
    )


    # --- Belegung und Wärmebedarf ---
    st.subheader("Belegung und Wärmebedarf")
    links, rechts = st.columns(2)
    with links:
        nutzung_grob = st.selectbox("Nutzung (Abb. 13)", list(WAERMEBEDARF_GROB.keys()))
        belegung = st.radio("Personen bestimmen", ["Normbelegung aus Fläche", "Direkt eingeben"], horizontal=True)
    with rechts:
        if belegung == "Normbelegung aus Fläche":
            flaeche_we = st.number_input("Fläche pro Wohnung A_NF [m²]", min_value=20, max_value=1000, value=200, step=10)
            personen_pro_we = round(normbelegung(flaeche_we), 1)
            personen_grob = personen_pro_we * wohnungen
            st.caption(f"Normbelegung: {personen_pro_we} P/WE × {wohnungen} WE = {personen_grob:.1f} P")
            if nutzung_grob == "Büro":
                st.warning("Die Normbelegung gilt nur für Wohnungen. Für Büros Personen direkt eingeben.")
        else:
            personen_grob = st.number_input("Anzahl Personen", min_value=0.0, max_value=5000.0, value=float(personen), step=1.0)

    q_grob = waermebedarf_grob_kwh(personen_grob, WAERMEBEDARF_GROB[nutzung_grob])
    v_tag = tagesvolumen_grob_l(q_grob)

    # --- Speicher (Abschätzung) ---
    st.subheader("Speicher (Abschätzung)")
    links, rechts = st.columns(2)
    with links:
        v_grob = st.number_input(
            "Angenommenes Speichervolumen [l]", min_value=50, max_value=20000,
            value=aufrunden(v_tag), step=50, help="Startwert: V_W,d auf 100 l aufgerundet",
        )
        stutzen_grob = st.number_input("Wasserführende Stutzen n_cp", min_value=2, max_value=10, value=5)
    with rechts:
        daemmung = st.radio("Speicherdämmung", list(DAEMMUNG_SPEICHER.keys()), horizontal=True)

    q_sto_grob = speicherverlust_kwh(v_grob, stutzen_grob, DAEMMUNG_SPEICHER[daemmung])

    st.divider()
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Personen n_P", f"{personen_grob:.1f}")
    g2.metric("Wärmebedarf Q'W", f"{q_grob:.1f} kWh/d")
    g3.metric("Tagesvolumen V_W,d", f"{v_tag:.0f} l/d")
    g4.metric("Speicherverlust Q'W,sto,ls", f"{q_sto_grob:.1f} kWh/d")

    # --- Warmhaltekonzepte und Verlustzahl ---
    st.subheader("Warmhaltekonzepte und Verlustzahl ξ")
    links, rechts = st.columns(2)
    with links:
        vorlauf_we = st.number_input("Vorlauf pro Wohnung l_WWV [m]", min_value=0.0, max_value=500.0, value=10.0, step=1.0)
        ruecklauf_we = st.number_input("Rücklauf pro Wohnung l_WWR [m]", min_value=0.0, max_value=500.0, value=10.0, step=1.0,
                                       help="Zählt nur bei konventioneller Zirkulation")
    with rechts:
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
    st.subheader("Ausstosszeit")
    st.caption("Ungünstigste Entnahmestelle: alle nicht warm gehaltenen Leitungsabschnitte bis zur Armatur erfassen.")
    links, rechts = st.columns(2)
    with links:
        abschnitte = st.data_editor(
            pd.DataFrame({
                "Abschnitt": ["Verteiler", "Ausstossleitung"],
                "Innendurchmesser [mm]": [16.0, 11.6],
                "Länge [m]": [4.0, 12.0],
            }),
            num_rows="dynamic", hide_index=True, width="stretch",
        )
    with rechts:
        armatur = st.selectbox("Entnahmearmatur (Abb. 11)", list(DURCHFLUSS_ARMATUR.keys()), index=2)
        warm_gehalten = st.checkbox("Verteilleitungen warm gehalten", value=True)

    abschnitte = abschnitte.dropna()
    liste = list(zip(abschnitte["Innendurchmesser [mm]"], abschnitte["Länge [m]"]))
    inhalt = leitungsinhalt_l(liste)
    t_em = ausstosszeit_s(inhalt, DURCHFLUSS_ARMATUR[armatur])
    t_max = AUSSTOSSZEIT_MIT_WARMHALTUNG if warm_gehalten else AUSSTOSSZEIT_OHNE_WARMHALTUNG

    a1, a2 = st.columns(2)
    a1.metric("Wasserinhalt V_w,em", f"{inhalt:.2f} l")
    a2.metric("Ausstosszeit t_em", f"{t_em:.1f} s", f"max. {t_max} s", delta_color="off")
    if t_em <= t_max:
        st.success(f"Ausstosszeit {t_em:.1f} s ≤ {t_max} s → Anforderung erfüllt")
    else:
        st.error(f"Ausstosszeit {t_em:.1f} s > {t_max} s → Leitung kürzen, Durchmesser verkleinern oder Warmhaltung näher an die Entnahmestelle")


# =====================================================================
# ③ Feinauslegung (Bauprojekt)
# =====================================================================
with tab_fein:
    st.header("Feinauslegung (Bauprojekt)")
    st.info(
    "- Baut auf dem in der Grobauslegung gewählten System auf.\n"
    "- Detaillierte Wärmebilanz: Nutzwärme plus Speicher-, Leitungs- und Ausstossverluste.\n"
    "- Bestimmung von Stundenspitze, Ladestrategie und Speichervolumen mit Nachweis."
    )

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
        ladezeit = st.number_input("Ladezeit pro Ladung [h]", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
        ladeart = st.radio("Ladeprinzip (Skript B4, Kap. 4.6)", ["Schichtladung", "Stufenladung"], horizontal=True,
                           help="Stufenladung: Wärme erst am Ladeende nutzbar → Reserve für die Ladezeit nötig")        

    # Berechnung: Verluste mit dem gewählten Speicher, daraus das erforderliche Volumen
    anteil = stundenspitze_anteil(personen)
    spitze_liter = bedarf * anteil
    q_zirk = zirkulationsverlust_kwh(zirk_laenge)
    q_ausstoss = ausstossverlust_kwh(wohnungen, personen / wohnungen, warmhaltung)
    q_speicher = speicherverlust_kwh(v_gewaehlt)
    q_gesamt = waermebedarf_gesamt_kwh(energie, q_speicher, q_zirk, q_ausstoss)
    q_bereit = bereitschaftsvolumen_kwh(energie, anteil, q_gesamt, ladezyklen)
    q_reserve = reserve_ladezeit_kwh(q_gesamt, ladezeit) if ladeart == "Stufenladung" else 0
    q_bereit = q_bereit + q_reserve
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
    e3.metric("Bereitschaftsvolumen", f"{q_bereit:.2f} kWh",
          f"davon Reserve Stufenladung {q_reserve:.2f} kWh" if q_reserve else None, delta_color="off")
    e4.metric("f_sto", f"{f_sto:.2f}")

    if speicher_genuegt(v_gewaehlt, v_erf):
        st.success(f"Erforderlich: {v_erf:.0f} l · Gewählt: {v_gewaehlt} l → Nachweis erfüllt")
    else:
        st.error(f"Erforderlich: {v_erf:.0f} l · Gewählt: {v_gewaehlt} l → Speicher zu klein, grösseren Typ wählen")


# =====================================================================
# ④ Wärmeerzeugung & Speicherladung
# =====================================================================
with tab_erzeuger:
    st.header("Wärmeerzeugung & Ladung")
    st.info(
    "- Übernimmt Wärmebedarf und Ladestrategie aus der Feinauslegung.\n"
    "- Bestimmt die Ladeleistung und simuliert den Ladeverlauf im Speicher (Schicht- vs. Stufenladung).\n"
    "- Vergleicht Wärmeerzeuger über Nutzungsgrad bzw. COP und Endenergie pro Tag und Jahr."
    )

    phi_gen = ladeleistung_kw(q_gesamt, ladezyklen, ladezeit)
    st.metric("Ladeleistung ΦW,gen", f"{phi_gen:.1f} kW", f"{ladezyklen} Ladungen à {ladezeit} h", delta_color="off")

    erzeuger = st.radio("Wärmeerzeuger", ["Wärmepumpe", "Holzfeuerung"], horizontal=True)
    links, rechts = st.columns(2)
    if erzeuger == "Holzfeuerung":
        with links:
            brennstoff = st.selectbox("Brennstoff", list(ETA_HOLZ_WW.keys()))
        with rechts:
            kondensation = st.checkbox("Mit Abgaskondensation")
            modulierend = st.checkbox("Modulierender / mehrstufiger Brenner")
    else:
        with links:
            t_quelle = st.number_input("Quellentemperatur [°C]", min_value=-20.0, max_value=20.0, value=0.0, step=1.0,
                                       help="Erdsonde ca. 0 °C, Aussenluft im Jahresmittel ca. 5 °C")
        with rechts:
            st.caption("COP = Gütegrad · T_VL / (T_VL − T_Quelle) mit T in Kelvin, "
                       "Gütegrad und Mindest-Kondensationstemperatur siehe tabellen.py")

    # --- Ladeverlauf ---
    st.subheader("Ladeverlauf im Speicher")
    links, rechts = st.columns(2)
    with links:
        anteil_warm = st.slider("Warmer Anteil beim Ladestart [%]", 0, 80, 20, step=5,
                                help="Restinhalt über dem Fühler EIN (Spitzendeckung)") / 100
    with rechts:
        zapfung = st.number_input("Zapfung während der Ladung [l/h]", min_value=0, max_value=500, value=0, step=10,
                                  help="Skript S. 47: Gleichzeitiger Bezug stört vor allem die Stufenladung")

    t_q = t_quelle if erzeuger == "Wärmepumpe" else 0
    verlaeufe = {}
    for art in ["Schichtladung", "Stufenladung"]:
        verlaeufe[art] = ladung_simulieren(art, v_gewaehlt, phi_gen, t_warm, t_kalt, t_q,
                                           anteil_warm=anteil_warm, zapfung_l_h=zapfung)
    auswertung = {art: ladung_auswerten(v, t_warm) for art, v in verlaeufe.items()}

    anzeige = st.radio("Ladeprinzip anzeigen", ["Schichtladung", "Stufenladung"], horizontal=True,
                       index=["Schichtladung", "Stufenladung"].index(ladeart))
    verlauf = verlaeufe[anzeige]
    a = auswertung[anzeige]
    if not a["fertig"]:
        st.warning("Ladung nach 10 h nicht abgeschlossen: Zapfung zu gross oder Leistung zu klein.")

    st.pyplot(speicher_schema(verlauf, anzeige, t_kalt, t_warm))

    minute = st.slider("Zeitpunkt [min]", 0, verlauf[-1]["minute"], verlauf[-1]["minute"] // 3)
    bild_links, bild_rechts = st.columns([1, 3])
    with bild_links:
        st.pyplot(speicher_einzeln(verlauf[minute]["temp"], anzeige, t_kalt, t_warm, f"{minute} min"))
    with bild_rechts:
        st.pyplot(ladeverlauf_diagramm(verlauf, anzeige, markierung=minute))

    vergleich = pd.DataFrame({
        "Ladeprinzip": list(verlaeufe),
        "Ladedauer [min]": [auswertung[x]["dauer_min"] for x in verlaeufe],
        "Wärme [kWh]": [auswertung[x]["waerme_kwh"] for x in verlaeufe],
        "Strom WP [kWh]": [auswertung[x]["strom_kwh"] for x in verlaeufe],
        "COP Mittel [-]": [auswertung[x]["cop_mittel"] for x in verlaeufe],
        "Min. Temperatur oben T1 [°C]": [auswertung[x]["t_oben_min"] for x in verlaeufe],
    })
    st.dataframe(vergleich.round(2), hide_index=True, width="stretch")
    if erzeuger == "Wärmepumpe":
        gewinn = auswertung["Stufenladung"]["cop_mittel"] / auswertung["Schichtladung"]["cop_mittel"] - 1
        st.caption(f"Stufenladung ist in dieser Simulation {gewinn * 100:.0f} % effizienter (Skript: 15–20 %).")

    # --- Endenergie ---
    st.subheader("Endenergie")
    if erzeuger == "Holzfeuerung":
        eta = wirkungsgrad_holz(brennstoff, kondensation, modulierend)
        name_eta = "Nutzungsgrad η_per,W"
    else:
        eta = auswertung[ladeart]["cop_mittel"]
        name_eta = f"COP ({ladeart})"

    if eta is None:
        st.warning(f"{brennstoff} ist in Abb. 22 nicht mit modulierendem Brenner aufgeführt.")
    else:
        e_tag = endenergie_kwh(q_gesamt, eta)
        w1, w2, w3 = st.columns(3)
        w1.metric(name_eta, f"{eta:.2f}")
        w2.metric("Endenergie pro Tag", f"{e_tag:.1f} kWh/d")
        w3.metric("Endenergie pro Jahr", f"{endenergie_jahr_kwh(e_tag):,.0f} kWh/a".replace(",", "'"))