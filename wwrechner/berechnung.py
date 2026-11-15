"""Formeln für die Warmwasser-Auslegung. Jede Funktion bekommt Werte und gibt ein Ergebnis zurück."""

from wwrechner.tabellen import (
    AUSSTOSS_MIT_WARMHALTUNG,
    AUSSTOSS_OHNE_WARMHALTUNG,
    C_WASSER,
    ETA_HOLZ_WW,
    JAHRESFAKTOR,
    SPEICHER_VERLUST_FAKTOR,
    STUTZEN_ZUSCHLAG,
    TAGE_PRO_JAHR,
    VERLUST_ZIRKULATION,
)



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



# --- Stundenspitze und Verluste (SIA 385/2) ---

def stundenspitze_anteil(personen):
    """Anteil des Tagesbedarfs, der in der stärksten Stunde gezapft wird (0.30 = 30 %)."""
    if personen >= 10:
        return 0.09 + 0.66 / personen**0.5 + 1.98 / personen
    return 1.3227 * personen**-0.428


def zirkulationsverlust_kwh(leitungslaenge_m):
    """Wärmeverlust der Zirkulationsleitung pro Tag in kWh."""
    return leitungslaenge_m * VERLUST_ZIRKULATION


def ausstossverlust_kwh(wohnungen, mit_warmhaltung):
    """Ausstossverluste Wohnen pro Tag in kWh. Entnahmen pro Tag = 2 + 5 × Wohnungen."""
    entnahmen = 2 + 5 * wohnungen
    if mit_warmhaltung:
        return entnahmen * AUSSTOSS_MIT_WARMHALTUNG
    return entnahmen * AUSSTOSS_OHNE_WARMHALTUNG


def speicherverlust_kwh(volumen_l, stutzen=2):
    """Bereitschaftsverlust des Speichers pro Tag in kWh."""
    return SPEICHER_VERLUST_FAKTOR * volumen_l**0.5 + STUTZEN_ZUSCHLAG * (stutzen - 2)


# --- Feinauslegung ---

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

def ladeleistung_kw(q_gesamt, ladezyklen, ladezeit_h):
    """Erforderliche Leistung des Wärmeerzeugers (ΦW,gen) in kW.
    Pro Ladung muss q_gesamt / ladezyklen in der Ladezeit nachgeladen werden."""
    q_pro_ladung = q_gesamt / ladezyklen
    return q_pro_ladung / ladezeit_h


def endenergie_kwh(q_gesamt, wirkungsgrad):
    """Endenergie (EWW), die der Wärmeerzeuger dafür braucht, in kWh."""
    return q_gesamt / wirkungsgrad

def wirkungsgrad_holz(brennstoff, kondensation, modulierend):
    """Nutzungsgrad η_per,W aus Abb. 22. Gibt None zurück, wenn die Kombination nicht existiert."""
    return ETA_HOLZ_WW[brennstoff].get((kondensation, modulierend))


def endenergie_jahr_kwh(e_tag):
    """Endenergie pro Jahr in kWh (Tageswert · 365 · 0.8)."""
    return e_tag * TAGE_PRO_JAHR * JAHRESFAKTOR