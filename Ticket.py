import sys
import textwrap
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *


class Ticket(QDialog):
    """Ticket widget."""

    def __init__(self, data, parent, simplified=None, cancelled=False):
        """Init."""
        super().__init__(parent)

        self.simplified = simplified

        self.parseData(data)

        self.setFixedWidth(250)

        if self.simplified:
            self.simplifiedTicket()
        else:
            self.ticket(cancelled)

    def ticket(self, cancelled=False):
        """Ticket visualization is created here."""
        layout = QVBoxLayout()

        header = self.ticketHeader()
        content = self.ticketContent()
        footer = self.ticketFooter(cancelled)

        layout.addLayout(header)
        layout.addLayout(content)

        if footer:
            layout.addLayout(footer)

        self.setLayout(layout)

    def simplifiedTicket(self):
        """Simplified visualization is created here."""
        layout = QVBoxLayout()

        header = self.simplifiedHeader()
        content = self.simplifiedContent()
        footer = self.simplifiedFooter()

        layout.addSpacing(50)
        layout.addLayout(header)
        layout.addLayout(content)
        layout.addLayout(footer)

        self.setLayout(layout)

    def ticketHeader(self):
        """Ticket header is created here."""
        header = QVBoxLayout()
        if self.image:
            label = QLabel()
            image = QPixmap(self.image)

            label.setPixmap(image.scaledToWidth(self.width() - 60, Qt.FastTransformation))
            label.setMargin(0)
            label.setAlignment(Qt.AlignCenter)

            header.setSpacing(0)
            header.addWidget(label)
        else:
            label = QLabel(self.title)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(self.width() - 20)
            label.setMargin(0)

            header.setSpacing(0)
            header.addWidget(label)

        header.addWidget(self.address)
        header.addWidget(self.regimenFiscal)
        header.addWidget(self.RFC)
        header.addWidget(self.name)
        header.addWidget(self.tel)
        header.addStretch()

        dateID = QGridLayout()

        styleBig = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 25pt;
                font-family: Asap;
            };"""
        styleSmall = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 15pt;
                font-family: Asap;
            };"""

        folioLabel = QLabel("FOLIO")
        folioLabel.setAlignment(Qt.AlignCenter)
        folioLabel.setStyleSheet(styleBig)
        dateID.addWidget(folioLabel, 0, 0)

        folio = QLabel(str(self.folio))
        folio.setAlignment(Qt.AlignCenter)
        folio.setStyleSheet(styleBig)
        dateID.addWidget(folio, 0, 1)

        date = QLabel(str(self.date))
        date.setAlignment(Qt.AlignCenter)
        date.setStyleSheet(styleSmall)
        dateID.addWidget(date, 1, 0, 1, 2)

        # hour = QLabel(str(self.hour))
        # hour.setAlignment(Qt.AlignCenter)
        # hour.setStyleSheet(styleSmall)
        # dateID.addWidget(hour, 1, 1)

        header.addLayout(dateID)

        return header

    def ticketContent(self):
        """Ticket content is created here."""
        content = QGridLayout()

        titles = {"Name": "Descripción", "Price": "P. Unit.", "Quant": "Cant.",
                  "Total": "Total"}

        x = 0
        for key, value in titles.items():
            setattr(self, key, QLabel(value))
            item = getattr(self, key)
            item.setAlignment(Qt.AlignCenter)
            content.addWidget(item, 0, x)
            x += 1

        y = 1
        for product in self.products:
            x = 0
            for key, value in titles.items():
                val = getattr(product, "get" + key)()
                if isinstance(val, float):
                    val = "$" + str(val)
                setattr(self, key, QLabel(str(val)))
                if x == 0:
                    getattr(self, key).setAlignment(Qt.AlignLeft)
                else:
                    getattr(self, key).setAlignment(Qt.AlignCenter)
                content.addWidget(getattr(self, key), y, x)
                x += 1
            y += 1

        paga = QLabel("$ " + str(self.paga))
        pagaLabel = QLabel("PAGA CON")
        content.addWidget(pagaLabel, y + 1, 2)
        content.addWidget(paga, y + 1, 3)

        cambio = QLabel("$ " + str(self.cambio))
        cambioLabel = QLabel("CAMBIO")
        content.addWidget(cambioLabel, y + 2, 2)
        content.addWidget(cambio, y + 2, 3)

        if self.factura:
            z = 1
            if self.dcto:
                total = self.total * abs(self.dcto - 1)
                dcto = round(self.total * self.dcto, 2)
                print(dcto)
                content.addWidget(QLabel("DCTO"), y + z, 0)
                content.addWidget(QLabel("$" + str(dcto)), y + z, 1)
                z += 1
            else:
                total = self.total
            content.addWidget(QLabel("SUBTOTAL"), y + z, 0)
            content.addWidget(QLabel("$" + str(self.subtotal)), y + z, 1)
            z += 1
            content.addWidget(QLabel("IVA"), y + z, 0)
            content.addWidget(QLabel("$" + str(self.iva)), y + z, 1)
            z += 1
            content.addWidget(QLabel("TOTAL"), y + z, 0)
            content.addWidget(QLabel("$" + str(total)), y + z, 1)
        else:
            z = 1
            if self.dcto:
                total = self.total * abs(self.dcto - 1)
                dcto = round(self.total * self.dcto, 2)
                content.addWidget(QLabel("DCTO"), y + z, 0)
                content.addWidget(QLabel("$" + str(dcto)), y + z, 1)
                z += 1
            else:
                total = self.total
            content.addWidget(QLabel("TOTAL"), y + z, 0)
            content.addWidget(QLabel("$" + str(total)), y + z, 1)

        return content

    def ticketFooter(self, cancelled):
        """Ticket footer is created here."""
        if cancelled:
            layout = QVBoxLayout()
            style = """QLabel {
                font-weight: boldest;
                font-size: 25pt;
            }"""
            cancelLabel = QLabel("CANCELADO")
            cancelLabel.setAlignment(Qt.AlignCenter)
            cancelLabel.setStyleSheet(style)
            layout.addWidget(cancelLabel)
            return layout
        else:
            return None

    def simplifiedHeader(self):
        """Simplified header is created here."""
        header = QVBoxLayout()

        style = """
        QLabel {
            color: black;
            font-weight: bold;
            font-size: 17pt;
            font-family: Source Code Pro;
        };"""

        if self.nombre:
            nombre = QLabel(str(self.nombre))
            nombre.setWordWrap(True)
            nombre.setAlignment(Qt.AlignCenter)
            nombre.setStyleSheet(style)
            header.addWidget(nombre)

        if self.nombre and self.notes:
            line = QLabel("______________")
            line.setAlignment(Qt.AlignCenter)
            line.setStyleSheet(style)
            header.addWidget(line)

        if self.notes:
            notes = textwrap.wrap(str(self.notes), 18)
            x = 0
            for linea in notes:
                setattr(self, "line" + str(x), QLabel(str(linea)))
                getattr(self, "line" + str(x)).setAlignment(Qt.AlignCenter)
                getattr(self, "line" + str(x)).setStyleSheet(style)
                getattr(self, "line" + str(x)).setMargin(0)
                header.addWidget(getattr(self, "line" + str(x)))
                x += 1

        if self.nombre or self.notes:
            header.setSpacing(0)
            return header
        else:
            return None

    def simplifiedContent(self):
        """Simplified ticket content is created here."""
        content = QGridLayout()

        titles = {"Quant": "Cant.", "Name": "Descripción"}

        styleProducts = """
        QLabel {
            color: black;
            font-weight: bold;
            font-size: 18pt;
            font-family: Asap;
        };"""

        styleTotal = """
        QLabel {
            color: black;
            font-weight: bold;
            font-size: 18pt;
            font-family: Asap;
            text-decoration: underline;
        };"""

        styleHour = """
        QLabel {
            color: black;
            font-weight: bold;
            font-size: 18pt;
            font-family: Asap;
        };"""

        y = 1
        for product in self.products:
            x = 0
            for key, value in titles.items():
                val = getattr(product, "get" + key)()
                setattr(self, key, QLabel(str(val)))
                getattr(self, key).setStyleSheet(styleProducts)
                if x == 0:
                    getattr(self, key).setAlignment(Qt.AlignCenter)
                else:
                    getattr(self, key).setAlignment(Qt.AlignLeft)
                getattr(self, key).setMargin(0)
                content.addWidget(getattr(self, key), y, x)
                x += 1
            y += 1

        if self.factura:
            total = QLabel("$" + str(self.total))
            total.setAlignment(Qt.AlignCenter)
            total.setStyleSheet(styleTotal)
            content.addWidget(total, y + 1, 1)
        else:
            total = QLabel("$" + str(self.total))
            total.setAlignment(Qt.AlignCenter)
            total.setStyleSheet(styleTotal)
            content.addWidget(total, y + 1, 1)

        hour = QLabel(str(self.hour))

        hour.setStyleSheet(styleHour)
        hour.setAlignment(Qt.AlignCenter)

        content.addWidget(hour, y + 1, 0)
        content.setSpacing(0)

        return content

    def simplifiedFooter(self):
        """Simplified footer is created here."""
        footer = QHBoxLayout()

        style = """
        QLabel {
            color: black;
            font-weight: bold;
            font-size: 35pt;
            font-family: Asap;
        };"""
        style2 = """
        QLabel {
            color: black;
            font-weight: bold;
            font-size: 25pt;
            font-family: Asap;
        };"""

        folio = QLabel(str(self.folio))
        folio.setAlignment(Qt.AlignCenter)
        folio.setStyleSheet(style)

        if self.status == 0:
            np = QLabel("P")
        else:
            np = QLabel("NP")
        np.setAlignment(Qt.AlignCenter)
        np.setStyleSheet(style2)

        if self.takeOut == 0:
            lleva = QLabel("LL")
        else:
            lleva = QLabel("AQ")
        lleva.setAlignment(Qt.AlignCenter)
        lleva.setStyleSheet(style2)

        footer.addWidget(folio)
        footer.addWidget(np)
        footer.addWidget(lleva)

        return footer

    def parseData(self, data):
        """Parse and organize the data for the ticket."""
        self.image = data["imagen"]
        self.title = data["titulo"]

        self.address = QLabel(data["direccion"])
        self.address.setWordWrap(True)
        self.address.setAlignment(Qt.AlignCenter)

        self.regimenFiscal = QLabel(data["regimen"])
        self.regimenFiscal.setWordWrap(True)
        self.regimenFiscal.setAlignment(Qt.AlignCenter)

        self.RFC = QLabel(data["RFC"])
        self.RFC.setWordWrap(True)
        self.RFC.setAlignment(Qt.AlignCenter)

        self.name = QLabel(data["nombreFiscal"])
        self.name.setWordWrap(True)
        self.name.setAlignment(Qt.AlignCenter)

        self.tel = QLabel(data["telLocal"])
        self.tel.setWordWrap(True)
        self.tel.setAlignment(Qt.AlignCenter)

        self.date = data["fecha"]
        self.hour = data["hora"]

        self.folio = data["folio"]
        self.nombre = data["nombre"]
        self.takeOut = data["llevar"]  # AQUÍ[FALSE] / LLEVAR[TRUE]
        self.status = data["pagado"]  # PAG[TRUE] / NP[FALSE]
        self.notes = data["notas"]
        self.factura = data["factura"]
        self.total = data["total"]
        self.subtotal = round(data["subtotal"], 2)
        self.iva = data["iva"]
        self.dcto = data["descuento"]
        self.paga = data["paga"]
        self.cambio = data["cambio"]
        self.cancelado = data["cancelado"]
        self.products = data["productos"]

    def getSize(self):
        """Return ticket size."""
        self.layout().update()
        self.layout().activate()
        return [self.width(), self.height()]

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)


# app = QApplication(sys.argv)
# window = Ticket()
# window.show()
# window.Print()
# sys.exit(app.exec_())
