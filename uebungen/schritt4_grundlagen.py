volumen = 1000 #Liter
t_kalt = 10 #Grad Celsius
t_warm = 60 #Grad Celsius
c_wasser = 1.163 #Wh pro Liter und Kelvin

delta_t = t_warm - t_kalt
energie_wh = volumen * c_wasser * delta_t
energie_kwh = energie_wh / 1000

print("temperaturdifferenz: ", delta_t, "K")
print(f"energie: {energie_kwh:.2f} kWh ")

def waermebedarf_kwh(volumen_l, t_warm, t_kalt):
    """Energie, um Wasser von t_kalt auf t_warm zu erwärmen, in kWh."""
    c_wasser = 1.163
    energie_wh = volumen_l * c_wasser * (t_warm - t_kalt)
    return energie_wh / 1000


q1 = waermebedarf_kwh(1000, 60, 10)
q2 = waermebedarf_kwh(200, 60, 10)
print(f"1000 Liter: {q1:.2f} kWh")
print(f"200 Liter: {q2:.2f} kWh")
