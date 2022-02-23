import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import csv
import Db


class DbIo(QWidget):
    """Import/Export the database To/From a CSV file."""

    def __init__(self, parent):
        """Init."""
        super().__init__(parent)

    def exportDb(self):
        """Export the database tables to CSV files."""
        caption = "Selecciona en donde guardar la base de datos"
        fileDir = QFileDialog.getExistingDirectory(parent=self, caption=caption,
                               directory="/",
                               options=QFileDialog.ShowDirsOnly |
                               QFileDialog.DontResolveSymlinks)

        db = Db.Db()
        tables = ["tickets", "ticketProducts", "productos", "cupones",
                  "categorias", "configuraciones", "appsData", "appTickets"]

        for table in tables:
            with open(fileDir + "/" + str(table) + ".csv", "w", newline="") as newFile:
                data = db.getTableItems(table)
                wr = csv.writer(newFile, quoting=csv.QUOTE_ALL)
                rawCol = db.getTableMeta(table)
                header = []
                header = [col[1] for col in rawCol]
                wr.writerow(header)
                wr.writerows(data)

    def importDb(self):
        """Import database table from csv file."""
        dataBases = ["categorias", "configuraciones", "productos", "cupones",
                     "ticketProducts", "tickets", "appsData", "appTickets"]
        caption = "Selecciona la base de datos que quieres actualizar"
        fileName = QFileDialog.getOpenFileName(parent=self, caption=caption,
                                               directory="/",
                                               filter="CSV (*.csv)")

        if fileName[0] != "":
            fileName = fileName[0]
            table = fileName.split("/")
            table = table[len(table) - 1].split(".")
            table = table[0]

            rows = []

            if not table not in dataBases:
                with open(fileName) as csvfile:
                    re = csv.reader(csvfile)
                    for row in re:
                        rows.append(row)

            db = Db.Db()
            db.overwriteTable(table, rows)


# x = True
#
# if x:
#     app = QApplication(sys.argv)
#     v = DbIo("database.db", None)
#     # v.exportDb()
#     v.importDb()
#     sys.exit(app.exec_())
