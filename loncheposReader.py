from collections import defaultdict
from heapq import merge
import sqlite3
from datetime import date, datetime, timedelta
from time import time
from typing import DefaultDict
from collections import defaultdict

database = "database.db"
connection = sqlite3.connect(database)
hoy = date.today()
thisMonth = str(date.today())[5:7]

diasDeLaSemana = ["DOMINGO", "LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO"]

cursor = connection.cursor()
totales = []

def cuentaPanes(day):
    query = "SELECT COALESCE(SUM(ticketProducts.cantidad), 0) FROM tickets JOIN ticketProducts ON tickets.folio = ticketProducts.folio WHERE ticketProducts.categoria = 'LONCHES' AND tickets.fecha = '{}' AND tickets.cancelado <> 1;".format(day)
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    query = "SELECT COALESCE(SUM(ticketProducts.cantidad), 0) FROM appTickets JOIN ticketProducts ON appTickets.folio = ticketProducts.folio WHERE ticketProducts.categoria = 'LONCHES' AND appTickets.fecha = '{}' AND appTickets.cancelado <> 1;".format(day)
    cursor.execute(query)
    resultApp = cursor.fetchall()[0][0]
    query = "SELECT COALESCE(SUM(ticketProducts.cantidad), 0) FROM appTickets JOIN ticketProducts ON appTickets.folio = ticketProducts.folio WHERE ticketProducts.categoria = '½ LONC' AND appTickets.fecha = '{}' AND appTickets.cancelado <> 1;".format(day)
    cursor.execute(query)
    resultAppHalf = cursor.fetchall()[0][0]
    return result + resultApp + (resultAppHalf/2)

def percentageCalculator(rawSales):
    percentage = []
    sales = 0
    for sale in rawSales:
        sales += sale[0]
    for sale in rawSales:
        percentage.append([int(sale[1]), round((sale[0] / sales) * 100, 2)])
    return percentage


def calculadoraTotales(timeframe):
    query = "SELECT COALESCE(SUM(total), 0) FROM tickets WHERE fecha = '{}' AND cancelado <> 1;".format(timeframe)
    cursor.execute(query)
    ct = cursor.fetchone()
    return ct

def ventasEsteMes():
    query = "SELECT COALESCE(SUM(total), 0) FROM tickets WHERE strftime('%m', fecha) = '{}';".format(thisMonth)
    cursor.execute(query)
    ventas = cursor.fetchone()[0]
    return ventas

def ventasEsteMesApps():
    query = "SELECT COALESCE(SUM(total), 0) FROM appTickets WHERE strftime('%m', fecha) = '{}';".format(thisMonth)
    cursor.execute(query)
    ventas = cursor.fetchone()[0]
    return ventas

def calculadoraTotalesApps(day, initial):
    query = "SELECT COALESCE(SUM(total), 0) FROM appTickets WHERE folio LIKE '{}%' AND fecha = '{}' AND cancelado <> 1;".format(initial, day)
    cursor.execute(query)
    cta = cursor.fetchone()
    return cta

def calculadoraEfectivoDidi(day):
    query = "SELECT COALESCE(SUM(total), 0) FROM appTickets WHERE folio LIKE 'D%' AND cashOrder = 1 AND fecha = '{}' AND cancelado <> 1;".format(day)
    cursor.execute(query)
    ctd = cursor.fetchone()
    query = "SELECT COALESCE(SUM(cambio), 0) FROM appTickets WHERE folio LIKE 'D%' AND cashOrder = 1 AND fecha = '{}' AND cancelado <> 1 AND cambio < 0;".format(day)
    cursor.execute(query)
    cambio = cursor.fetchone()
    return ctd[0] - abs(cambio[0])

def ventaPorHora(timeframe):
    query = "SELECT SUM(total) AS sale_total, STRFTIME('%H', hora) AS Hour FROM tickets WHERE fecha <> DATE('now') AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%H', hora)".format(timeframe)
    cursor.execute(query)
    vph = cursor.fetchall()
    return vph

def ventaPorHoraApps(timeframe):
    query = "SELECT SUM(total) AS sale_total, STRFTIME('%H', hora) AS Hour FROM appTickets WHERE fecha <> DATE('now') AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%H', hora)".format(timeframe)
    cursor.execute(query)
    vphApps = cursor.fetchall()
    return vphApps

def ventaPorDiaSemana(timeframe):
    query = "SELECT SUM(total) AS sale_total, STRFTIME('%w', fecha) AS Dia FROM tickets WHERE fecha <> DATE('now') AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%w', fecha);".format(timeframe)
    cursor.execute(query)
    vpds = cursor.fetchall()
    return vpds

def ventaPorDiaSemanaApps(timeframe):
    query = "SELECT SUM(total) AS sale_total, STRFTIME('%w', fecha) AS Dia FROM appTickets WHERE fecha <> DATE('now') AND fecha >= '{}' AND cancelado <> 1 GROUP BY STRFTIME('%w', fecha);".format(timeframe)
    cursor.execute(query)
    vpds = cursor.fetchall()
    return vpds

def contadorDiasActivos(timeframe):
    query = "SELECT fecha FROM tickets WHERE fecha <> DATE('now') GROUP BY fecha ORDER BY fecha DESC;"
    cursor.execute(query)
    cda = cursor.fetchmany(timeframe)
    return cda

def contarArticulos(day, categoria):
    query = "SELECT ticketProducts.producto AS item, SUM(ticketProducts.cantidad) AS total FROM tickets JOIN ticketProducts ON tickets.folio = ticketProducts.folio WHERE ticketProducts.categoria = '{}' AND tickets.fecha = '{}' AND tickets.cancelado <> 1 GROUP BY ticketProducts.producto;".format(categoria, day)
    cursor.execute(query)
    ventasLocal = cursor.fetchall()
    return ventasLocal

def contarArticulosApps(day, categoria):
    query = "SELECT ticketProducts.producto AS item, SUM(ticketProducts.cantidad) AS total FROM appTickets JOIN ticketProducts ON appTickets.folio = ticketProducts.folio WHERE ticketProducts.categoria = '{}' AND appTickets.fecha = '{}' AND appTickets.cancelado <> 1 GROUP BY ticketProducts.producto;".format(categoria, day)
    cursor.execute(query)
    ventasLocal = cursor.fetchall()
    return ventasLocal

def contarArticulosMes(categoria):
    query = "SELECT ticketProducts.producto AS item, SUM(ticketProducts.cantidad) AS total FROM tickets JOIN ticketProducts ON tickets.folio = ticketProducts.folio WHERE ticketProducts.categoria = '{}' AND strftime('%m', tickets.fecha) = '{}' AND tickets.cancelado <> 1 GROUP BY ticketProducts.producto;".format(categoria, thisMonth)
    cursor.execute(query)
    ventasLocal = cursor.fetchall()
    return ventasLocal

def contarArticulosAppsMes(categoria):
    query = "SELECT ticketProducts.producto AS item, SUM(ticketProducts.cantidad) AS total FROM appTickets JOIN ticketProducts ON appTickets.folio = ticketProducts.folio WHERE ticketProducts.categoria = '{}' AND strftime('%m', appTickets.fecha) = '{}' AND appTickets.cancelado <> 1 GROUP BY ticketProducts.producto;".format(categoria, thisMonth)
    cursor.execute(query)
    ventasLocal = cursor.fetchall()
    return ventasLocal

def minMax(data1, data2, position):
    x1 = [x[position] for x in data1]
    y1 = [y[position] for y in data2]
    maxV = int(max(max(x1), max(y1)))
    minV = int(min(min(x1), min(y1)))
    return [minV, maxV]

def mergeSalesHourly(timeframe):
    inStoreSales = ventaPorHora(timeframe)
    appSales = ventaPorHoraApps(timeframe)
    minMaxVals = minMax(inStoreSales, appSales, 1)
    inStoreSales = dict((int(y), x) for x, y in inStoreSales)
    appSales = dict((int(y), x) for x, y in appSales)

    mergedSales = []

    for i in range(minMaxVals[0], minMaxVals[1] + 1):
        mergedSales.append([inStoreSales[i] + appSales[i], i])
    return mergedSales

def mergeArticulos(day, categoria):
    inStore = contarArticulos(day, categoria)
    apps = contarArticulosApps(day, categoria)

    articulos = [inStore, apps]

    mergedSales = defaultdict(int)

    for d in articulos:
        for item in d:
            mergedSales[item[0]]+=item[1]
    return dict(mergedSales)

def mergeArticulosMes(categoria):
    inStore = contarArticulosMes(categoria)
    apps = contarArticulosAppsMes(categoria)

    articulos = [inStore, apps]

    mergedSales = defaultdict(int)

    for d in articulos:
        for item in d:
            mergedSales[item[0]]+=item[1]
    return dict(mergedSales)


def mergeSalesWeekly(timeframe):
    inStoreSales = ventaPorDiaSemana(timeframe)
    appSales = ventaPorDiaSemanaApps(timeframe)
    minMaxVals = minMax(inStoreSales, appSales, 1)
    inStoreSales = dict((int(y), x) for x, y in inStoreSales)
    appSales = dict((int(y), x) for x, y in appSales)

    mergedSales = []
    for i in range(minMaxVals[0], minMaxVals[1] + 1):
        try:
            mergedSales.append([inStoreSales[i] + appSales[i], i])
        except:
            pass
    return mergedSales

def moreDataHourly(timeframe):
    """Returns a boolean state depending on which dataset has more data points."""
    inStoreSales = True
    appSales = False
    if ventaPorHoraApps(timeframe) < ventaPorHora(timeframe):
        return inStoreSales
    else:
        return appSales


def mergeDailyTotals(timeframe):
    total = 0
    apps = ["D", "U"]
    fecha = hoy - timedelta(timeframe)
    total += calculadoraTotales(fecha)[0]
    for app in apps:
        total += calculadoraTotalesApps(fecha, app)[0]
    return total