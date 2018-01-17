import sqlite3


class Db(object):
    """Database communication class."""

    def __init__(self):
        """Init."""
        self.database = "database.db"

    def recordTicket(self, data):
        """Add order to database."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        folio = data["folio"]
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
        rfc = "'" + data["rfc"] + "'"
        telefono = "'" + str(data["telefono"]) + "'"
        email = "'" + str(data["email"]) + "'"
        nombref = "'" + str(data["nombre2"]) + "'"
        uso = "'" + str(data["uso"]) + "'"

        productos = data["productos"]

        query = """INSERT INTO tickets VALUES({}, {}, {}, {}, {}, {}, {},
                {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
                {}, {}, {}, {});""".format(folio, nombre, llevar, pagado, sexo,
                                           edad, notas, factura, total,
                                           subtotal, iva, descuento,
                                           descuentop, descuentoa, cupon, paga,
                                           cambio, cancelado, fecha, hora, rfc,
                                           telefono, email, nombref, uso)
        cursor.execute(query)

        for product in productos:
            tNombre = "'" + str(product.getName()) + "'"
            tPrecio = product.getPrice()
            tCantidad = product.getQuant()
            tTotal = product.getTotal()

            query = """INSERT INTO ticketProducts VALUES({}, {}, {}, {},
            {});""".format(folio, tNombre, tPrecio, tCantidad, tTotal)
            cursor.execute(query)

        connection.commit()
        connection.close()

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

    def getProducts(self, cat):
        """Return products list with metadata from the category passed."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        cat = "'" + cat + "'"  # formatting category for sql query

        query = "SELECT * FROM productos WHERE categoria = {};".format(cat)
        cursor.execute(query)
        products = cursor.fetchall()

        connection.commit()
        connection.close()

        return products

    def getCategories(self):
        """Return a list of categories and their color."""
        connection = sqlite3.connect(self.database)

        cursor = connection.cursor()

        query = """SELECT * FROM categorias;"""
        cursor.execute(query)
        category = cursor.fetchall()

        connection.commit()
        connection.close()

        return category

    def getTableItems(self, table):
        """Return all items from table."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        query = """SELECT * FROM {}""".format(table)
        cursor.execute(query)
        items = cursor.fetchall()

        connection.commit()
        connection.close()

        return items

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
            if len(row)> 1:
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
                    uso TEXT);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS ticketProducts(folio INTEGER,
         producto TEXT, precio FLOAT, cantidad INT, total INT);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS productos(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto TEXT, precio FLOAT, categoria TEXT);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS cupones(codigo TEXT PRIMARY KEY,
                    tipo int, descuento float, usos int, caducidad date);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS categorias(categoria TEXT,
                    color VARCHAR);"""
        cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS configuraciones(descripcion TEXT,
                    valor VARCHAR, tipo INT, grupo INT, categoria TEXT);"""
        cursor.execute(query)

        connection.commit()
        connection.close()

    def filler(self):
        """Fill the db with data for testing."""
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        query = """INSERT INTO categorias VALUES('LONCHES', '29, 235, 130');"""
        cursor.execute(query)
        query = """INSERT INTO categorias VALUES('BEBIDAS', '194, 29, 235');"""
        cursor.execute(query)
        products = [("JAMÓN", "30", "LONCHES"),
                    ("CARNES FRIAS", "42", "LONCHES"),
                    ("CAMPIRANA", "46", "LONCHES"),
                    ("CHORIQUESO", "46", "LONCHES"),
                    ("CUBANA", "53", "LONCHES"),
                    ("BISTEC", "52", "LONCHES"),
                    ("PIBIL", "52", "LONCHES"),
                    ("PIERNA", "48", "LONCHES"),
                    ("PECHUGA", "50", "LONCHES"),
                    ("ADOBADA", "70", "LONCHES"),
                    ("TORREÓN", "80", "LONCHES"),
                    ("ARRACHERA", "70", "LONCHES"),
                    ("VEGETARIANA", "70", "LONCHES"),
                    ("COCA-COLA", "14", "BEBIDAS"),
                    ("COCA-LIGHT", "14", "BEBIDAS"),
                    ("FANTAF", "14", "BEBIDAS"),
                    ("FANTA", "14", "BEBIDAS"),
                    ("SPRITE", "14", "BEBIDAS"),
                    ("FRESCA", "14", "BEBIDAS"),
                    ("TOPOCHICO", "14", "BEBIDAS"),
                    ("MANZANITA", "14", "BEBIDAS"),
                    ("COCA-COLA", "14", "BEBIDAS"),
                    ("AGUA", "10", "BEBIDAS"),
                    ("NARANJADA", "16", "BEBIDAS"),
                    ("LIMONADA", "16", "BEBIDAS"),
                    ("VALLEFRUT", "14", "BEBIDAS"),
                    ("NDURAZNO", "14", "BEBIDAS"),
                    ("NGUAYABA", "14", "BEBIDAS"),
                    ("NMANZANA", "14", "BEBIDAS"),
                    ("NMANGO", "14", "BEBIDAS"),
                    ("JMANZANA", "14", "BEBIDAS"),
                    ]

        for product in products:
            query = "INSERT INTO productos('producto', 'precio', 'categoria')VALUES({}, {}, {});".format("'" + product[0] + "'", product[1], "'" + product[2] + "'")
            cursor.execute(query)

        connection.commit()
        connection.close()


# db = Db()
# db.initializer()
# db.filler()
