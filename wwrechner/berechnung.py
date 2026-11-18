"""Formeln für die Warmwasser-Auslegung. Jede Funktion bekommt Werte und gibt ein Ergebnis zurück."""
import math

from wwrechner.tabellen import (
    AUSSTOSS_10S,
    AUSSTOSS_15S,
    BEZUGSFLAECHE,
    C_WASSER,
    ETA_HOLZ_WW,
    GEWICHTUNG_HILFSENERGIE,
    HILFSENERGIE_BAND,
    JAHRESFAKTOR,
    KWH_PRO_LITER,
    PUMPE,
    SPEICHER_VERLUST_FAKTOR,
    STUTZEN_ZUSCHLAG,
    TAGE_PRO_JAHR,
    VERLUST_ZIRKULATION,
    WARMHALTEKONZEPTE,
    ZUSCHLAG_VERLUSTE_GROB,
)


# =====================================================================
# ① Bedarf
# =====================================================================

def tagesbedarf_liter(personen, liter_pro_person):
    """Tagesbedarf an Warmwasser in Litern."""
    return personen * liter_pro_person


def waermebedarf_kwh(volumen_l, t_warm, t_kalt):
    """Energie, um volumen_l Liter Wasser von t_kalt auf t_warm zu erwärmen, in kWh."""
    energie_wh = volumen_l * C_WASSER * (t_warm - t_kalt)
    return energie_wh / 1000


def verbrauch_pro_stunde(tagesbedarf_l, profil_prozent):
    """Verteilt den Tagesbedarf auf 24 Stunden. Gibt eine Liste mit Litern pro Stunde zurück."""
    stunden_liter = []
    for anteil in profil_prozent:
        stunden_liter.append(tagesbedarf_l * anteil / 100)
    return stunden_liter


def spitzenstunde(stunden_liter):
    """Stunde mit dem grössten Verbrauch. Gibt (Stunde, Liter) zurück."""
    maximum = max(stunden_liter)
    stunde = stunden_liter.index(maximum)
    return stunde, maximum


# =====================================================================
# ② Grobauslegung (Vorprojekt)
# =====================================================================

def normbelegung(flaeche_m2):
    """Personen pro Wohnung nach Fläche (Normbelegung SIA 385/2)."""
    return 3.3 - 2 / (1 + (flaeche_m2 / BEZUGSFLAECHE) ** 3)


def waermebedarf_grob_kwh(personen, kwh_pro_person):
    """Wärmebedarf Warmwasser Q'_W für die Grobauslegung in kWh/d."""
    return personen * kwh_pro_person


def tagesvolumen_grob_l(q_grob):
    """Täglich bereitzustellendes Warmwasservolumen V_W,d in Litern, inkl. +50 % Verluste."""
    return q_grob * ZUSCHLAG_VERLUSTE_GROB / KWH_PRO_LITER


def aufrunden(wert, schritt=100):
    """Rundet auf den nächsten Schritt auf, z. B. 372 l -> 400 l."""
    return math.ceil(wert / schritt) * schritt



def leitungslaenge_m(wohnungen, vorlauf_pro_we, ruecklauf_pro_we, mit_ruecklauf):
    """Warm gehaltene Leitungslänge im ganzen Gebäude in m."""
    pro_we = vorlauf_pro_we + (ruecklauf_pro_we if mit_ruecklauf else 0)
    return wohnungen * pro_we


def pumpenleistung_w(laenge_m, ansatz):
    """Elektrische Nennleistung der Umwälzpumpe in W (Grenz- oder Zielwert)."""
    werte = PUMPE[ansatz]
    return werte["grund_w"] + werte["pro_m_w"] * laenge_m


def verlustzahl(q_speicher, q_warmhaltung, e_hilf, f_hl, q_nutz):
    """Warmwasser-Verlustzahl ξ_ls (0.5 = 50 %)."""
    return (q_speicher + f_hl * q_warmhaltung + GEWICHTUNG_HILFSENERGIE * e_hilf) / q_nutz


def warmhaltekonzept_auswerten(konzept, wohnungen, vorlauf_pro_we, ruecklauf_pro_we,
                               q_speicher, q_nutz, pumpenansatz):
    """Rechnet ein Warmhaltekonzept durch. Gibt alle Zwischenwerte als Dictionary zurück."""
    k = WARMHALTEKONZEPTE[konzept]
    laenge = leitungslaenge_m(wohnungen, vorlauf_pro_we, ruecklauf_pro_we, k["mit_ruecklauf"])
    q_hl = laenge * k["verlust"]

    if k["pumpe"]:
        # Handout: Pumpe immer mit Vor- und Rücklauflänge
        laenge_pumpe = leitungslaenge_m(wohnungen, vorlauf_pro_we, ruecklauf_pro_we, True)
        p_pumpe = pumpenleistung_w(laenge_pumpe, pumpenansatz)
        e_hilf = p_pumpe * 24 / 1000
    else:
        p_pumpe = 0
        e_hilf = HILFSENERGIE_BAND * q_hl

    return {
        "laenge_m": laenge,
        "q_warmhaltung": q_hl,
        "pumpe_w": p_pumpe,
        "e_hilf": e_hilf,
        "xi": verlustzahl(q_speicher, q_hl, e_hilf, k["f_hl"], q_nutz),
    }

# =====================================================================
# ③ Feinauslegung (Bauprojekt)
# =====================================================================

def stundenspitze_anteil(personen):
    """Anteil des Tagesbedarfs, der in der stärksten Stunde gezapft wird (0.30 = 30 %)."""
    if personen >= 10:
        return 0.09 + 0.66 / personen**0.5 + 1.98 / personen
    return 1.3227 * personen**-0.428


def zirkulationsverlust_kwh(leitungslaenge_m):
    """Wärmeverlust der Zirkulationsleitung pro Tag in kWh."""
    return leitungslaenge_m * VERLUST_ZIRKULATION


def ausstossverlust_kwh(wohnungen, personen_pro_we, mit_warmhaltung):
    """Ausstosswärmeverluste Wohnen pro Tag in kWh (Handout 5.1.4)."""
    werte = AUSSTOSS_10S if mit_warmhaltung else AUSSTOSS_15S
    entnahmen_dusche = personen_pro_we
    entnahmen_spueltisch = 6 + 2 * personen_pro_we
    entnahmen_waschtisch = 3 + 2 * personen_pro_we
    pro_wohnung = (
        entnahmen_dusche * werte["dusche"]
        + entnahmen_spueltisch * werte["spueltisch"]
        + entnahmen_waschtisch * werte["waschtisch"]
    )
    return wohnungen * pro_wohnung


def speicherverlust_kwh(volumen_l, stutzen=2, daemmfaktor=1.0):
    """Bereitschaftsverlust des Speichers pro Tag in kWh."""
    verlust = SPEICHER_VERLUST_FAKTOR * volumen_l**0.5 + STUTZEN_ZUSCHLAG * (stutzen - 2)
    return verlust * daemmfaktor


def waermebedarf_gesamt_kwh(q_nutz, q_speicher, q_zirkulation, q_ausstoss):
    """Wärme, die der Wärmeerzeuger pro Tag liefern muss (QW,gen,out), in kWh."""
    return q_nutz + q_speicher + q_zirkulation + q_ausstoss


def bereitschaftsvolumen_kwh(q_nutz, spitze_anteil, q_gesamt, ladezyklen):
    """Wärmemenge, die der Speicher bereithalten muss (QW,sto,cont), in kWh."""
    q_spitze = q_nutz * spitze_anteil          # Stundenspitze QW,pk
    return q_spitze + q_gesamt / ladezyklen


def speichervolumen_erforderlich_l(q_bereitschaft, t_speicher, t_kalt, f_sto):
    """Erforderliches Speichervolumen in Litern (VW,sto)."""
    kwh_pro_liter = C_WASSER / 1000 * (t_speicher - t_kalt)
    return q_bereitschaft / kwh_pro_liter * f_sto


def speicher_genuegt(v_gewaehlt, v_erforderlich):
    """True, wenn der gewählte Speicher gross genug ist."""
    return v_gewaehlt >= v_erforderlich


# =====================================================================
# ④ Wärmeerzeuger
# =====================================================================

def ladeleistung_kw(q_gesamt, ladezyklen, ladezeit_h):
    """Erforderliche Leistung des Wärmeerzeugers (ΦW,gen) in kW.
    Pro Ladung muss q_gesamt / ladezyklen in der Ladezeit nachgeladen werden."""
    q_pro_ladung = q_gesamt / ladezyklen
    return q_pro_ladung / ladezeit_h


def wirkungsgrad_holz(brennstoff, kondensation, modulierend):
    """Nutzungsgrad η_per,W aus Abb. 22. Gibt None zurück, wenn die Kombination nicht existiert."""
    return ETA_HOLZ_WW[brennstoff].get((kondensation, modulierend))


def endenergie_kwh(q_gesamt, wirkungsgrad):
    """Endenergie (EWW), die der Wärmeerzeuger dafür braucht, in kWh."""
    return q_gesamt / wirkungsgrad


def endenergie_jahr_kwh(e_tag):
    """Endenergie pro Jahr in kWh (Tageswert · 365 · 0.8)."""
    return e_tag * TAGE_PRO_JAHR * JAHRESFAKTOR
