from loncheposReader import *
import csv
import inspect
from datetime import date
from getpass import getpass

password = "ManzanaCanela"

passVar = getpass(prompt="Contraseña:")

if passVar != password:
    print("Contraseña Incorrecta")
    input()
    exit()


print("VENTAS TOTALES DEL LOCAL ESTE MES =", ventasEsteMes())
print("VENTAS TOTALES DE LAS APLICACIONES ESTE MES =", ventasEsteMesApps())
print("___________________________________________")

print("DESGLOSE POR ARTICULO DE ESTE MES:")
mergeLonches = mergeArticulosMes("LONCHES")
mergeLonc = mergeArticulosMes("½ LONC")
mergeBebidas = mergeArticulosMes("BEBIDAS")

mergesHoy = [mergeLonches, mergeLonc, mergeBebidas]

for m in mergesHoy:
    for key in sorted(m):
        print(key, ":", m[key])

filePath = inspect.stack()[0][1].split('\\')

ventasMes = [(contarArticulosMes("LONCHES"), "Lonches"), (contarArticulosMes("½ LONC"), "Medios_Lonches"), (contarArticulosMes("BEBIDAS"), "Bebidas")]
ventasMesApp = [(contarArticulosAppsMes("LONCHES"), "Lonches_Apps"), (contarArticulosAppsMes("½ LONC"), "Medios_Lonches_Apps"), (contarArticulosAppsMes("BEBIDAS"), "Bebidas_Apps")]

def exportDb():
    """Export the database tables to CSV files."""
    for m in ventasMes:
        monthYear = str(date.today())[0:7]
        fileDir = "\\".join(filePath[0:-1]) + "\\ventas{}_{}".format(monthYear, m[1]) + ".csv"
        with open(fileDir, "w", newline="") as newFile:
            wr = csv.writer(newFile, quoting=csv.QUOTE_ALL)
            title = ["Ventas en el local", monthYear, m[1]]
            wr.writerow(title)
            header = ["producto", "cantidad"]
            wr.writerow(header)
            for item in m[0]:
                wr.writerow([item[0], item[1]])

    for m in ventasMesApp:
        monthYear = str(date.today())[0:7]
        fileDir = "\\".join(filePath[0:-1]) + "\\ventas{}_{}".format(monthYear, m[1]) + ".csv"
        with open(fileDir, "w", newline="") as newFile:
            wr = csv.writer(newFile, quoting=csv.QUOTE_ALL)
            title = ["Ventas en las aplicaciones", monthYear, m[1]]
            wr.writerow(title)
            header = ["producto", "cantidad"]
            wr.writerow(header)
            for item in m[0]:
                wr.writerow([item[0], item[1]])

exportDb()