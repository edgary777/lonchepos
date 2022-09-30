"""Deprecated visualizer for the database."""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import Db


class Visualizer(QWidget):
    """Database visualizer."""

    def __init__(self):
        """Init."""
        super().__init__()

        self.tableTicket = QTableWidget(100, 25)
        self.tableTicketProducts = QTableWidget(100, 5)
        self.tableProductos = QTableWidget(100, 4)
        self.tableCupones = QTableWidget(100, 5)
        self.tableCategorias = QTableWidget(100, 3)
        self.tableConfiguraciones = QTableWidget(100, 5)
        self.tables = [self.tableTicket, self.tableTicketProducts,
                       self.tableProductos, self.tableCupones,
                       self.tableCategorias, self.tableConfiguraciones]

        btnUpdate = QPushButton("Update")
        btnUpdate.clicked.connect(self.updateTables)
        btnOk = QPushButton("OK")
        btnOk.clicked.connect(self.accept)

        ticketLayout = QVBoxLayout()
        ticketLabel = QLabel("Ticket")
        ticketLabel.setAlignment(Qt.AlignCenter)
        ticketLayout.addWidget(ticketLabel)
        ticketLayout.addWidget(self.tableTicket)

        TicketProductsLayout = QVBoxLayout()
        TicketProductsLabel = QLabel("Productos ticket")
        TicketProductsLabel.setAlignment(Qt.AlignCenter)
        TicketProductsLayout.addWidget(TicketProductsLabel)
        TicketProductsLayout.addWidget(self.tableTicketProducts)

        productosLayout = QVBoxLayout()
        productosLabel = QLabel("Productos")
        productosLabel.setAlignment(Qt.AlignCenter)
        productosLayout.addWidget(productosLabel)
        productosLayout.addWidget(self.tableProductos)

        cuponesLayout = QVBoxLayout()
        cuponesLabel = QLabel("Cupones")
        cuponesLabel.setAlignment(Qt.AlignCenter)
        cuponesLayout.addWidget(cuponesLabel)
        cuponesLayout.addWidget(self.tableCupones)

        categoriasLayout = QVBoxLayout()
        categoriasLabel = QLabel("Categorias")
        categoriasLabel.setAlignment(Qt.AlignCenter)
        categoriasLayout.addWidget(categoriasLabel)
        categoriasLayout.addWidget(self.tableCategorias)

        configuracionesLayout = QVBoxLayout()
        configuracionesLabel = QLabel("Configuraciones")
        configuracionesLabel.setAlignment(Qt.AlignCenter)
        configuracionesLayout.addWidget(configuracionesLabel)
        configuracionesLayout.addWidget(self.tableConfiguraciones)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(btnUpdate)
        btnLayout.addWidget(btnOk)

        layout = QGridLayout()
        layout.addLayout(ticketLayout, 0, 0, 1, 2)
        layout.addLayout(TicketProductsLayout, 0, 2, 3, 1)
        layout.addLayout(productosLayout, 1, 0)
        layout.addLayout(cuponesLayout, 1, 1)
        layout.addLayout(categoriasLayout, 2, 0)
        layout.addLayout(configuracionesLayout, 2, 1)
        layout.addLayout(btnLayout, 3, 0, 1, 3)
        # layout.setColumnStretch(0, 2)
        # layout.setColumnStretch(2, 1)
        layout.setRowStretch(0, 3)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)
        self.setLayout(layout)
        self.updateTables()
        self.updateTables()

    def updateTables(self):
        """Update tables."""
        db = Db.Db()
        tables = ["tickets", "ticketProducts", "productos", "cupones",
                  "categorias", "configuraciones"]
        t = 0
        for table in tables:
            data = db.getTableItems(table)
            tableObj = self.tables[t]
            r = 0
            rawCol = db.getTableMeta(table)
            colNames = [x[1] for x in rawCol]
            tableObj.setHorizontalHeaderLabels(colNames)
            for row in data:
                c = 0
                for column in row:
                    prevItem = tableObj.item(r, c)
                    item = QTableWidgetItem(str(column))
                    item.setTextAlignment(Qt.AlignRight|
                                          Qt.AlignVCenter)
                    if prevItem:
                        if prevItem.text() != str(column):
                            item.setForeground(Qt.white)
                            item.setBackground(Qt.red)
                    else:
                        item.setForeground(Qt.white)
                        item.setBackground(Qt.red)

                    tableObj.setItem(r, c, item)
                    c += 1
                r += 1
            tableObj.resizeColumnsToContents()
            tableObj.resizeRowsToContents()
            t += 1

    def accept(self):
        """Accept."""
        QWidget.close(self)


app = QApplication(sys.argv)
v = Visualizer()
v.showMaximized()
sys.exit(app.exec_())
