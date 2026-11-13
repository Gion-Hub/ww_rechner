
#Teil A
volumen = 1000 #Liter
t_kalt = 10 #Grad Celsius
t_warm = 60 #Grad Celsius
c_wasser = 1.163 #Wh pro Liter und Kelvin

delta_t = t_warm - t_kalt
energie_wh = volumen * c_wasser * delta_t
energie_kwh = energie_wh / 1000

print("temperaturdifferenz: ", delta_t, "K")
print(f"energie: {energie_kwh:.2f} kWh ")


#Teil B
def waermebedarf_kwh(volumen_l, t_warm, t_kalt):
    """Energie, um Wasser von t_kalt auf t_warm zu erwärmen, in kWh."""
    c_wasser = 1.163
    energie_wh = volumen_l * c_wasser * (t_warm - t_kalt)
    return energie_wh / 1000


q1 = waermebedarf_kwh(1000, 60, 10)
q2 = waermebedarf_kwh(200, 60, 10)
print(f"1000 Liter: {q1:.2f} kWh")
print(f"200 Liter: {q2:.2f} kWh")

#Teil C
def pruefe_sicherheitsfaktor(sf_prozent):
    """Nachweis: Sicherheitsfaktor muss mindestens 125 % sein."""
    if sf_prozent >= 125:
        return "erfüllt"
    else:
        return "nicht erfüllt"


print("SF 306 %:", pruefe_sicherheitsfaktor(306))
print("SF 110 %:", pruefe_sicherheitsfaktor(110))

#Teil D
verbrauch_pro_wohnung = [120, 95, 150, 80]   # Liter pro Tag

print("Anzahl Wohnungen:", len(verbrauch_pro_wohnung))
print("Total:", sum(verbrauch_pro_wohnung), "l/d")
print("Grösster Verbrauch:", max(verbrauch_pro_wohnung), "l/d")
print("Erste Wohnung:", verbrauch_pro_wohnung[0], "l/d")

for liter in verbrauch_pro_wohnung:
    q = waermebedarf_kwh(liter, 60, 10)
    print(f"{liter} l  ->  {q:.2f} kWh")


# Teil E
def tagesbedarf_liter(personen, liter_pro_person):
    """Tagesbedarf an Warmwasser in Litern."""
    return personen * liter_pro_person


bedarf = tagesbedarf_liter(8, 40)
print("Tagesbedarf:", bedarf, "Liter")

energie = waermebedarf_kwh(bedarf, 60, 10)
print(f"Energie dafür: {energie:.2f} kWh")