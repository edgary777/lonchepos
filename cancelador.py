"""Plugin to cancel a ticket."""
import sqlite3
from datetime import date, timedelta


database = "database.db"
connection = sqlite3.connect(database)

cursor = connection.cursor()
    
def checkStatus(folio):
    """Check the status of a given ticket."""
    data = fetchData(folio)
    if data[2] == 1:
        input("EL TICKET YA FUE CANCELADO")
        exit()
    return data

def fetchData(folio):
    """Return the data of the given ticket."""
    query = "SELECT total, hora, cancelado FROM tickets WHERE folio = '{}';".format(folio)
    cursor.execute(query)
    data = cursor.fetchall()[0]
    return data

def checkStatusApp(folio):
    """Check the status of a given ticket if it's from an app sale."""
    data = fetchDataApp(folio)
    if data[2] == 1:
        input("EL TICKET YA FUE CANCELADO")
        exit()
    return data

def fetchDataApp(folio):
    """Get the data of the given ticket if it's from an app sale."""
    query = "SELECT total, hora, cancelado FROM appTickets WHERE folio = '{}';".format(folio)
    cursor.execute(query)
    data = cursor.fetchall()[0]
    return data

def cancelarFolio(folio):
    """Cancel the given ticket."""
    query = "UPDATE tickets SET cancelado = '1' WHERE folio = '{}'".format(folio)
    cursor.execute(query)
    connection.commit()

def cancelarFolioApp(folio):
    """Cancel the given ticket if it's from an app sale."""
    query = "UPDATE appTickets SET cancelado = '1' WHERE folio = '{}'".format(folio)
    cursor.execute(query)
    connection.commit()


folio = input("ESCRIBE EL FOLIO QUE QUIERES CANCELAR: ")
isApp = False

if isinstance(folio[0], int):
    data = checkStatus(folio)
else:
    isApp = True
    data = checkStatusApp(folio)
total = data[0]
hora = data[1]
status = data[2]
respuesta1 = input("EL TOTAL DE EL FOLIO {} ES ${} Y SE REGISTRO A LAS {}, SEGURO QUE QUIERES CANCELAR ESTE TICKET?(s/n)".format(folio, total, hora))
if respuesta1 == "SI" or respuesta1 == "si" or respuesta1 == "s" or respuesta1 == "S":
    respuesta2 = input("SEGURO QUE QUIERES CANCELAR EL FOLIO {}? (s/n)".format(folio))
    if respuesta2 == "SI" or respuesta2 == "si" or respuesta2 == "s" or respuesta2 == "S":
        if not isApp:
            cancelarFolio(folio)
            checkStatus(folio)
        else:
            cancelarFolioApp(folio)
            checkStatusApp(folio)
    else:
        input("NO SE CANCELO NINGUN TICKET")
        pass
else:
    input("NO SE CANCELO NINGUN TICKET")
    pass