import sqlite3


class Db(object):
    """Database communication class."""

    def __init__(self):
        """Init."""
        self.database = "database.db"

        self.initializer()

    def recordTicket(self, data):
        """Add order to database."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        label = "'" + str(data["label"]) + "'"
        folio = "'" + str(data["folio"]) + "'"
        nombre = "'" + str(data["nombre"]) + "'"
        llevar = data["llevar"]
        pagado = data["pagado"]
        sexo = data["sexo"]
        edad = data["edad"]
        notas = "'" + str(data["notas"]) + "'"
        factura = data["factura"]
        total = data["total"]
        subtotal = data["subtotal"]
        iva = data["iva"]
        descuento = data["descuento"]
        descuentoa = data["descuentoa"]
        descuentop = data["descuentop"]
        cupon = "'" + str(data["cupon"]) + "'"
        paga = data["paga"]
        cambio = data["cambio"]
        cancelado = data["cancelado"]
        fecha = "'" + str(data["fecha"]) + "'"
        hora = "'" + str(data["hora"]) + "'"
        rfc = "'" + data["facRfc"] + "'"
        telefono = "'" + str(data["facTelefono"]) + "'"
        email = "'" + str(data["facEmail"]) + "'"
        nombref = "'" + str(data["facNombre"]) + "'"
        uso = "'" + str(data["facUso"]) + "'"
        cashOrder = 1 if data["cashOrder"] else 0
        credit = 1 if data["credit"] else 0
        debit = 1 if data["debit"] else 0

        productos = data["productos"]

        if label == folio:
            table = "tickets"
        else:
            table = "appTickets"
        if label != folio:
            query = """INSERT INTO {} VALUES({}, {}, {}, {}, {}, {}, {},
                    {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
                    {}, {}, {}, {}, {}, {});""".format(table, folio, nombre, llevar, pagado, sexo,
                                            edad, notas, factura, total,
                                            subtotal, iva, descuento,
                                            descuentop, descuentoa, cupon, paga,
                                            cambio, cancelado, fecha, hora, rfc,
                                            telefono, email, nombref, uso, label, cashOrder)
        else:
            query = """INSERT INTO {} VALUES({}, {}, {}, {}, {}, {}, {},
                    {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
                    {}, {}, {}, {}, {}, {}, {});""".format(table, folio, nombre, llevar, pagado, sexo,
                                            edad, notas, factura, total,
                                            subtotal, iva, descuento,
                                            descuentop, descuentoa, cupon, paga,
                                            cambio, cancelado, fecha, hora, rfc,
                                            telefono, email, nombref, uso, label, credit, debit)
        cursor.execute(query)

        for product in productos:
            tNombre = "'" + str(product.getName()) + "'"
            tPrecio = product.getPrice()
            tCantidad = product.getQuant()
            tTotal = product.getTotal()
            tCategoria = product.getCat()

            query = """INSERT INTO ticketProducts VALUES({}, {}, {}, {},
            {}, '{}');""".format(folio, tNombre, tPrecio, tCantidad, tTotal, tCategoria)
            cursor.execute(query)

        connection.commit()
        connection.close()

    def getDiscountCodes(self):
        """Return all the data for all the discount codes."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = """SELECT * FROM cupones;"""
        cursor.execute(query)
        appsData = cursor.fetchall()

        connection.commit()
        connection.close()

        return appsData

    def getDiscountCode(self, code):
        """Return all the data for a single discount code."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = "SELECT * FROM cupones WHERE codigo = '{}';".format(code)
        cursor.execute(query)
        appsData = cursor.fetchall()

        if appsData:
            appsData = appsData[0]

        connection.commit()
        connection.close()

        return appsData


    def updateDiscountCodeCounter(self, code):
        """Increase the counter for the used code by 1."""
        connection = sqlite3.connect(self.database)
        
        cursor = connection.cursor()
        print(code)

        query = "UPDATE cupones SET usos = usos + 1 WHERE codigo = '{}'".format(code)
        cursor.execute(query)
        print(query)

        connection.commit()
        connection.close()

    def getAppsData(self):
        """Return all the data for all the registered apps."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = """SELECT * FROM appsData;"""
        cursor.execute(query)
        appsData = cursor.fetchall()

        connection.commit()
        connection.close()

        return appsData

    def getSingleAppData(self, appName):
        """Return the product data."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = "SELECT * FROM appsData WHERE nombre = {};".format(appName)
        cursor.execute(query)
        appData = cursor.fetchone()

        connection.commit()
        connection.close()
        return appData

    def getSingleAppDataByID(self, appID):
        """Return the product data."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = "SELECT * FROM appsData WHERE appID = {};".format(appID)
        cursor.execute(query)
        appData = cursor.fetchone()

        connection.commit()
        connection.close()
        return appData

    def getFolio(self):
        """Return the next ticket number."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = """SELECT MAX(folio) FROM tickets;"""
        cursor.execute(query)
        folio = cursor.fetchone()

        connection.commit()
        connection.close()

        if folio[0] is None:
            return 0
        else:
            return folio[0]

    def verifyFolioApp(self, folio):
        """Return True if the passed folio exists, False if it doesn't"""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()
        query = "SELECT folio FROM appTickets WHERE folio = '{}';".format(folio)
        cursor.execute(query)
        folio = cursor.fetchall()
        if folio:
            return True
        else:
            return False

    def getProduct(self, product):
        """Return the product data."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = "SELECT * FROM tickets WHERE id = {};".format(product)
        cursor.execute(query)
        product = cursor.fetchone()

        connection.commit()
        connection.close()
        return product

    def getProducts(self, catNombre, catTipo):
        """Return products list with metadata from the category passed."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        catNombre = "'" + catNombre + "'"  # formatting category for sql query

        query = "SELECT * FROM productos WHERE nombreCategoria = {} AND tipoCategoria = '{}';".format(catNombre, catTipo)
        cursor.execute(query)
        products = cursor.fetchall()

        connection.commit()
        connection.close()

        return products

    def getCategories(self):
        """Return a list of categories and their color."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = """SELECT * FROM categorias WHERE categoria = 0;"""
        cursor.execute(query)
        category = cursor.fetchall()

        connection.commit()
        connection.close()

        return category

    def getAppCategories(self, category):
        """
        Return a list of categories and their color.

            The 'category' attribute is an INT other than 0.
            
            * made as an alt function to avoid modifying all existent code
        """
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = "SELECT * FROM categorias WHERE categoria='{}';".format(category)
        cursor.execute(query)
        category = cursor.fetchall()

        connection.commit()
        connection.close()

        return category

    def getTableItems(self, table):
        """Return all items from table."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        query = """SELECT * FROM {};""".format(table)
        cursor.execute(query)
        items = cursor.fetchall()

        connection.commit()
        connection.close()

        return items

    def getConfigGroup(self, group):
        """Return data for the ticket header."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        query = """SELECT * FROM configuraciones WHERE grupo='{}';""".format(
            str(group))
        cursor.execute(query)
        items = cursor.fetchall()

        connection.commit()
        connection.close()

        dic = {}
        for item in items:
            dic[item[0]] = item[1]

        return dic

    def getTableMeta(self, table):
        """Return table columnt titles."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        query = """PRAGMA table_info({});""".format(table)
        cursor.execute(query)
        items = cursor.fetchall()

        connection.commit()
        connection.close()

        return items

    def overwriteTable(self, table, data):
        """Clean table and fil with new data."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        query = "DELETE FROM {}".format(table)
        cursor.execute(query)

        del data[0]

        rows = []
        for item in data:
            row = []
            for col in item:
                try:
                    col = float(col)
                except ValueError:
                    pass
                finally:
                    if isinstance(col, float):
                        if col % 1 == 0:
                            col = int(col)
                row.append(col)
            rows.append(row)

        for row in rows:
            valstr = "?"
            if len(row) > 1:
                for val in range((len(row) - 1)):
                    valstr += ", ?"
            query = "INSERT INTO {} VALUES({});".format(table, valstr)
            cursor.execute(query, row)

        connection.commit()
        connection.close()

    def initializer(self):
        """If table not exists create it."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        query = """CREATE TABLE IF NOT EXISTS tickets(folio INTEGER PRIMARY KEY,
                    nombre TEXT, llevar INT, pagado INT, sexo INT, edad INT,
                    notas TEXT, factura INT, total FLOAT, subtotal FLOAT,
                    iva FLOAT, descuento FLOAT, descuentoa FLOAT,
                    descuentop FLOAT, cupon TEXT, paga INT, cambio INT,
                    cancelado INT, fecha DATE, hora TIME, rfc TEXT,
                    telefono VARCHAR, email VARCHAR, nombref TEXT,
                    uso TEXT, label TEXT, credit INT, debit INT);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS appTickets(folio TEXT PRIMARY KEY,
                    nombre TEXT, llevar INT, pagado INT, sexo INT, edad INT,
                    notas TEXT, factura INT, total FLOAT, subtotal FLOAT,
                    iva FLOAT, descuento FLOAT, descuentoa FLOAT,
                    descuentop FLOAT, cupon TEXT, paga INT, cambio INT,
                    cancelado INT, fecha DATE, hora TIME, rfc TEXT,
                    telefono VARCHAR, email VARCHAR, nombref TEXT,
                    uso TEXT, label TEXT, cashOrder INT);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS ticketProducts(folio TEXT,
         producto TEXT, precio FLOAT, cantidad INT, total INT, categoria INT);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS productos(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto TEXT, precio FLOAT, nombreCategoria TEXT, tipoCategoria INT);"""
        cursor.execute(query)

        query = """SELECT * FROM productos;"""
        cursor.execute(query)

        tb = cursor.fetchall()

        if len(tb) == 0:
            query = """INSERT INTO productos('producto', 'precio', 'nombreCategoria', 'tipoCategoria')
                       VALUES ('DUMMY', '10', 'DUMMY', 0);"""
            cursor.execute(query)
            query = """INSERT INTO productos('producto', 'precio', 'nombreCategoria', 'tipoCategoria')
                       VALUES ('DUMMY', '11', 'DUMMY2', 0);"""
            cursor.execute(query)
            query = """INSERT INTO productos('producto', 'precio', 'nombreCategoria', 'tipoCategoria')
                       VALUES ('DUMMY', '12', 'DUMMY', 1);"""
            cursor.execute(query)
            query = """INSERT INTO productos('producto', 'precio', 'nombreCategoria', 'tipoCategoria')
                       VALUES ('DUMMY', '13', 'DUMMY', 2);"""
            cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS cupones(codigo TEXT PRIMARY KEY,
                    tipo int, descuento float, usos int, caducidad date);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS categorias(ID INTEGER PRIMARY KEY,
                    nombre TEXT, color VARCHAR, categoria INT);"""
        cursor.execute(query)

        query = """SELECT * FROM categorias;"""
        cursor.execute(query)

        tb = cursor.fetchall()

        if len(tb) == 0:
            query = """INSERT INTO categorias VALUES(0, 'DUMMY', '29, 235, 130', 0);"""
            cursor.execute(query)
            query = """INSERT INTO categorias VALUES(1, 'DUMMY2', '29, 235, 130', 0);"""
            cursor.execute(query)
            query = """INSERT INTO categorias VALUES(2, 'DUMMY', '255, 0, 0', 1);"""
            cursor.execute(query)
            query = """INSERT INTO categorias VALUES(3, 'DUMMY', '0, 0, 255', 2);"""
            cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS appsData(appID ID INTEGER PRIMARY KEY,
                    nombre TEXT, logo INT, tarifa FLOAT, telefono TEXT);"""
        cursor.execute(query)

        query = """INSERT INTO appsData VALUES('appNombre', 'PATH', 'tarifa', 'telefono');"""

        query = """CREATE TABLE IF NOT EXISTS configuraciones(descripcion TEXT,
                    valor VARCHAR, tipo INT, grupo INT, categoria TEXT);"""
        cursor.execute(query)

        # Placeholders for the data needed for the ticket.
        # FIX the appSessions need to print a different dataset
        if len(tb) == 0:
            query = """INSERT INTO configuraciones VALUES('imagen_ticket','','link','LOCAL','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('titulo','','texto','LOCAL','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('direccion','','texto','LOCAL','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('regimen_fiscal','','texto','LOCAL','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('RFC','','texto','LOCAL','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('nombre','','texto','LOCAL','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('telefono','','texto','LOCAL','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('imagen_ticket','','link','APP','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('titulo','','texto','APP','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('direccion','','texto','APP','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('regimen_fiscal','','texto','APP','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('RFC','','texto','APP','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('nombre','','texto','APP','headerConfig');"""
            cursor.execute(query)
            query = """INSERT INTO configuraciones VALUES('telefono','','texto','APP','headerConfig');"""
            cursor.execute(query)

        connection.commit()
        connection.close()

# db = Db()
# db.initializer()
# db.filler()
