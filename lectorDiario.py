from loncheposReader import *
from getpass import getpass

password = "ManzanaCanela"

passVar = getpass(prompt="Contraseña:")

if passVar != password:
    print("Contraseña Incorrecta")
    input()
    exit()

fecha30 = contadorDiasActivos(30)[-1][0]
fecha91 = contadorDiasActivos(91)[-1][0]


print("VENTA TOTAL HOY =", mergeDailyTotals(0), "(SIN APLICACIONES =", calculadoraTotales(hoy)[0], ")")
print("VENTA TOTAL AYER =", mergeDailyTotals(1), "(SIN APLICACIONES =", calculadoraTotales(hoy - timedelta(1))[0], ")")
print("___________________________________________")

print("VENTA UBER HOY =", calculadoraTotalesApps(hoy, "U")[0])
print("VENTA UBER AYER =", calculadoraTotalesApps(hoy - timedelta(1), "U")[0])
print("___________________________________________")

print("VENTA DIDI HOY =", calculadoraTotalesApps(hoy, "D")[0])
print("TOTAL EFECTIVO DIDI HOY=", calculadoraEfectivoDidi(hoy))
print("VENTA DIDI AYER =", calculadoraTotalesApps(hoy - timedelta(1), "D")[0])
print("TOTAL EFECTIVO DIDI AYER=", calculadoraEfectivoDidi(hoy - timedelta(1)))
print("___________________________________________")

print("TOTAL PANES HOY =", cuentaPanes(hoy))
print("TOTAL PANES AYER =", cuentaPanes(hoy - timedelta(1)))
print("___________________________________________")

print("DESGLOSE POR ARTICULO DE HOY:")
mergeLonches = mergeArticulos(hoy, "LONCHES")
mergeLonc = mergeArticulos(hoy, "½ LONC")
mergeBebidas = mergeArticulos(hoy, "BEBIDAS")

mergesHoy = [mergeLonches, mergeLonc, mergeBebidas]

for m in mergesHoy:
    for key in sorted(m):
        print(key, ":", m[key])

print("___________________________________________")
print("DESGLOSE POR ARTICULO DE AYER:")
mergeLonches = mergeArticulos(hoy - timedelta(1), "LONCHES")
mergeLonc = mergeArticulos(hoy - timedelta(1), "½ LONC")
mergeBebidas = mergeArticulos(hoy - timedelta(1), "BEBIDAS")

mergesHoy = [mergeLonches, mergeLonc, mergeBebidas]

for m in mergesHoy:
    for key in sorted(m):
        print(key, ":", m[key])