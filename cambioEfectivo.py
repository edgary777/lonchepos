"""Plugin to modify the data of a printed app ticket to a cash order."""
import sqlite3
from datetime import date, timedelta


database = "database.db"
connection = sqlite3.connect(database)

cursor = connection.cursor()
    
def checkStatus(folio):
    """Check if the ticket is already set to cash order."""
    data = fetchData(folio)
    if data[4][0] != "D":
        input("EL TICKET NO ES DE DIDI Y NO PUEDE SER PAGO EN EFECTIVO")
        exit()
    if data[2] == 1 :
        input("EL TICKET ESTA CANCELADO")
        exit()
    if data[3] == 1 :
        input("EL TICKET YA ESTA MARCADO COMO EFECTIVO")
        exit()
    return data

def fetchData(folio):
    """Get the ticket Data."""
    query = "SELECT total, hora, cancelado, cashOrder, folio FROM appTickets WHERE folio = '{}';".format(folio)
    cursor.execute(query)
    data = cursor.fetchall()[0]
    return data

def askCash(total):
    """Query for a payment."""
    respuesta = float(input("CUANTO PAGO EL REPARTIDOR? "))
    if respuesta <= total:
        result = float(total) - respuesta
        return result
    else:
        print("EL PAGO TIENE QUE SER MENOR O IGUAL AL TOTAL DE LA ORDEN")
        askCash(total)

folio = input("ESCRIBE EL FOLIO QUE QUIERES CAMBIAR: ")
data = checkStatus(folio)
total = data[0]
hora = data[1]
status = data[2]
respuesta1 = input("EL TOTAL DE EL FOLIO {} ES ${} Y SE REGISTRO A LAS {}, SEGURO QUE QUIERES CAMBIAR ESTE TICKET A PAGO CON EFECTIVO?(s/n)".format(folio, total, hora))
if respuesta1 == "SI" or respuesta1 == "si" or respuesta1 == "s" or respuesta1 == "S":
    respuesta2 = input("SEGURO QUE QUIERES CAMBIAR EL FOLIO {}? (s/n)".format(folio))
    if respuesta2 == "SI" or respuesta2 == "si" or respuesta2 == "s" or respuesta2 == "S":
        respuesta3 = askCash(total)
        query = "UPDATE appTickets SET cashOrder = '1', cambio = {} WHERE folio = '{}'".format(respuesta3, folio)
        cursor.execute(query)
        connection.commit()
        checkStatus(folio)
    else:
        input("NO SE REALIZO NINGUN CAMBIO")
        pass
else:
    input("NO SE REALIZO NINGUN CAMBIO")
    pass
    