from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class OrderTotal(QWidget):
    """Object to show the total of the order in a session."""

    def __init__(self, total, parent):
        """Init."""
        super().__init__(parent)

        self.total = total
        self.subtotal = 0
        self.vat = 0  # Value Added Tax

        # discount [total discount, amount, percentage, code]
        self.dcto = [0, None, None, None]

        self.invoice = False  # Boolean option to activate invoice options

        self.color = QColor(Qt.black)
        self.rounded = 20
        self.setMaximumHeight(75)

        self.initUi()

    def initUi(self):
        """Init."""
        style = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 25pt;
                font-family: Asap;
            };
            """

        self.totalLabel = QLabel(str(self.total))
        self.totalLabel.setAlignment(Qt.AlignRight)
        self.totalLabel.setStyleSheet(style)

        totalLayout = QVBoxLayout()
        totalLayout.addStretch()
        totalLayout.addWidget(self.totalLabel)
        totalLayout.addStretch()

        extrasLayout = self.extraData()

        layout = QHBoxLayout()
        layout.addLayout(extrasLayout)
        layout.addStretch()
        layout.addLayout(totalLayout)

        self.setLayout(layout)

    def updateTotal(self, total, dcto=None):
        """Update the total shown."""
        if dcto and dcto > 0:
            total = total * dcto
        self.total = total
        self.updateUi()

    def toggleTax(self):
        """Toggle whether tax is calculated or not."""
        self.invoice = not self.invoice
        self.updateUi()

    def updateDcto(self, dcto):
        """Toggle whether tax is calculated or not."""
        self.dcto = dcto
        self.updateUi()

    def getInvoice(self):
        """Return the invoice status."""
        return self.invoice

    def getDcto(self):
        """Return the discount if exists."""
        return self.dcto

    def getTotal(self):
        """Return the order total before taxes."""
        if self.dcto:
            if self.invoice:
                total = round((self.total * (1 - self.dcto[0])) * 1.16, 2)
            else:
                total = round(self.total * (1 - self.dcto[0]), 2)
        else:
            if self.invoice:
                total = round(self.total * 1.16, 2)
            else:
                total = round(self.total, 2)
        return total

    def getSubtotal(self):
        """Return the order total before taxes."""
        return self.subtotal

    def getVat(self):
        """Return the order VAT."""
        return self.vat

    def updateUi(self):
        """Update the Ui."""
        if self.dcto:
            if self.invoice:
                self.subtotal = (self.total * (1 - self.dcto[0])) if self.total > 0 else 0
                self.subtotal = round(self.subtotal, 2)
                self.vat = self.subtotal * 0.16 if self.subtotal > 0 else 0
                self.vat = round(self.vat, 2)
                self.subtotalLabel.setText(str(self.subtotal))
                self.dctoLabel.setText(str(round(self.total * self.dcto[0], 2)))
                self.vatLabel.setText(str(self.vat))
                self.totalLabel.setText("$" + str(round((self.total * (1 - self.dcto[0])) * 1.16, 2)))
            else:
                self.subtotal = round(self.total, 2)
                self.vat = 0
                self.totalLabel.setText("$" + str(round(self.total * (1 - self.dcto[0]), 2)))
                self.dctoLabel.setText(str(round(self.total * self.dcto[0], 2)))
                self.subtotalLabel.setText(str(self.subtotal))
                self.vatLabel.setText(str(self.vat))
        else:
            self.dcto = 0
            if self.invoice:
                self.subtotal = self.total if self.total > 0 else 0
                self.subtotal = round(self.subtotal, 2)
                self.vat = self.subtotal * 0.16 if self.subtotal > 0 else 0
                self.vat = round(self.vat, 2)
                self.subtotalLabel.setText(str(self.subtotal))
                self.vatLabel.setText(str(self.vat))
                self.totalLabel.setText("$" + str(round(self.total * 1.16, 2)))
            else:
                self.subtotal = 0
                self.vat = 0
                self.totalLabel.setText("$" + str(self.total))
                self.subtotalLabel.setText(str(self.subtotal))
                self.vatLabel.setText(str(self.vat))

    def extraData(self):
        """Extra data labels generator."""
        extraData = {"subtotal": "SUBTOTAL", "vat": "IVA", "dcto": "DESCUENTO"}
        layout = QGridLayout()
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(10)
        layout.setContentsMargins(10, 1, 1, 1)

        styleLabel = """
            QLabel {
                color: black;
                font-size: 10pt;
                font-family: Asap;
            };
            """

        styleNum = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 12pt;
                font-family: Asap;
            };
            """
        x = 0
        for key, value in extraData.items():
            setattr(self, key + "Layout1", QVBoxLayout())
            setattr(self, key + "Layout2", QVBoxLayout())

            if key != "dcto":
                setattr(self, key + "Label", QLabel(str(getattr(self, key))))
            else:
                setattr(self, key + "Label", QLabel(str(getattr(self, key)[0])))
            getattr(self, key + "Label").setAlignment(Qt.AlignLeft)
            getattr(self, key + "Label").setStyleSheet(styleNum)

            setattr(self, key + "Caption", QLabel(value))
            getattr(self, key + "Caption").setAlignment(Qt.AlignLeft)
            getattr(self, key + "Caption").setStyleSheet(styleLabel)

            layout.addWidget(getattr(self, key + "Caption"), x, 0)
            layout.addWidget(getattr(self, key + "Label"), x, 1)
            x += 1
        extraLayout = QVBoxLayout()
        extraLayout.addStretch()
        extraLayout.addLayout(layout)
        extraLayout.addStretch()
        return extraLayout

    def paintEvent(self, event):
        """Paint Event."""
        # Set up the painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create the path for the big figure
        path = QPainterPath()
        path.addRoundedRect(QRectF(0.0, 0.0, self.width(), self.height()),
                            self.rounded, self.rounded)

        # Calculate the percentage ratio to get a 3 px margin
        ratioX = (1 - ((3 / self.width()) * 2))
        ratioY = (1 - ((3 / self.height()) * 2))

        # calculate the distance the shape has to be moved to be centered
        x = (self.width() - (self.width() * ratioX)) / 2
        y = (self.height() - (self.height() * ratioY)) / 2

        # Create the path for the small figure
        path2 = QPainterPath()
        path2.addRoundedRect(QRectF(x, y, self.width() * ratioX,
                             self.height() * ratioY), self.rounded - 5
                             * ratioY, self.rounded - 5 * ratioY)

        # Fill the paths with color
        painter.fillPath(path, self.color)
        painter.fillPath(path2, Qt.white)
