from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import DbIO


class DctDialog(QDialog):
    """Pop-Up window to set a discount for an order."""

    def __init__(self, total, parent, percentage=None, amount=None, code=None):
        """Init."""
        super().__init__(parent, Qt.FramelessWindowHint |
                         Qt.WindowSystemMenuHint)

        self.parent = parent
        self.total = total
        self.newTotal = total
        self.percentage = percentage
        self.amount = amount
        self.code = code

        self.initUi()

        self.newTotalUpdate()

        self.setFixedSize(320, 250)

    def initUi(self):
        """UI setup."""
        styleInputs = """QLineEdit {
                     border-radius: 20%;
                     padding-left: 10px;
                     font-family: Asap;
                     font-weight: bold;
                     font-size: 25pt;
                     }"""

        styleLabels = """QLabel {
                     font-family: Asap;
                     font-weight: bold;
                     font-size: 25pt;
                     color: white;
                     }"""

        self.newTotalLabel = QLabel("$" + str(self.total))
        self.newTotalLabel.setAlignment(Qt.AlignCenter)
        self.newTotalLabel.setStyleSheet(styleLabels)
        btnOk = QPushButton("Aceptar")
        btnOk.clicked.connect(self.returnDcto)
        btnCancel = QPushButton("Cancelar")
        btnCancel.clicked.connect(self.reject)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(btnOk)
        btnLayout.addWidget(btnCancel)

        layout = QVBoxLayout()
        layout.addStretch()

        items = {"percentage": "%:", "amount": "Cantidad:", "code": "Cupón:"}
        x = 0
        inputsLayout = QGridLayout()
        for key, value in items.items():
            setattr(self, key + "Input", QLineEdit())
            # getattr(self, key + "Input").setFixedWidth(150)
            getattr(self, key + "Input").setStyleSheet(styleInputs)
            if getattr(self, key):
                getattr(self, key + "Input").setText(str(getattr(self, key)))
            setattr(self, key + "Label", QLabel(value))
            getattr(self, key + "Label").setStyleSheet(styleLabels)
            getattr(self, key + "Label").setAlignment(Qt.AlignRight)
            inputsLayout.addWidget(getattr(self, key + "Label"), x, 0)
            inputsLayout.addWidget(getattr(self, key + "Input"), x, 1)
            x += 1

        layout.addLayout(inputsLayout)
        self.percentageInput.textChanged.connect(lambda:
                                                 self.setPercentageDcto(
                                                 self.percentageInput.text()
                                                 ))

        validator = QIntValidator(0, 100, self)
        validator2 = QIntValidator(0, int(self.total), self)
        self.percentageInput.setValidator(validator)
        self.amountInput.setValidator(validator2)

        self.amountInput.textChanged.connect(lambda:
                                             self.setAmountDcto(
                                             self.amountInput.text()))

        layout.addStretch()
        layout.addWidget(self.newTotalLabel)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

    def setAmountDcto(self, dcto):
        """Set discount amount."""
        try:
            dcto = int(dcto)
            if dcto and dcto > 0:
                self.amount = dcto
            else:
                self.amount = None
            self.newTotalUpdate()
        except ValueError:
            self.amount = None
            self.newTotalUpdate()

    def setPercentageDcto(self, dcto):
        """Set discount percentage."""
        try:
            dcto = int(dcto)
            if dcto and dcto > 0:
                self.percentage = dcto
            else:
                self.percentage = None
            self.newTotalUpdate()
        except ValueError:
            self.percentage = None
            self.newTotalUpdate()

    def setCodeDcto(self, code):
        """Search and apply a code discount.

        The search returns a list with 2 items, the first item is the type of
        discount, the second item is the amount of discount.
        """
        pass

    def newTotalUpdate(self):
        """Update total with new discounts."""
        self.newTotal = self.total
        if self.percentage or self.amount:
            if self.amount:
                self.newTotal = self.newTotal - self.amount

            if self.percentage and self.percentage > 0:
                self.newTotal = self.newTotal - (self.newTotal *
                                                 (self.percentage / 100))
        else:
            self.newTotal = self.total

        self.newTotal = round(self.newTotal, 2)

        self.newTotalLabel.setText("$" + str(self.newTotal))

    def returnDcto(self):
        """Update the order with the discount."""
        if self.newTotal != self.total:
            dcto = [None, None, None, None]
            dcto[0] = 1 - (self.newTotal / self.total)
            dcto[1] = self.percentage
            dcto[2] = self.amount
            dcto[3] = self.code
        else:
            dcto = [0, None, None, None]
        self.parent.orderTotal.updateDcto(dcto)
        self.accept()

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(p)


class PopOrderDialog(QDialog):
    """Dialog to hold PopOrderWidget."""

    def __init__(self, parent):
        """Init."""
        super().__init__(parent, Qt.FramelessWindowHint |
                         Qt.WindowSystemMenuHint)

        self.parent = parent

        self.setMaximumHeight(800)
        self.setFixedWidth(350)

        self.initUi()

    def initUi(self):
        """Ui is created here."""
        self.pop = PopOrderWidget(self)

        layout = QVBoxLayout()

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(self.pop)

        btnOk = QPushButton("OK")
        btnOk.clicked.connect(self.aceptar)
        btnCancel = QPushButton("Cancelar")
        btnCancel.clicked.connect(self.reject)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(btnOk)
        btnLayout.addWidget(btnCancel)

        layout.addWidget(area)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

    def getParent(self):
        """Return parent."""
        return self.parent

    def aceptar(self):
        """Ok button signal."""
        items = []  # List of items to be added to a new order
        removeItems = []
        editItems = []
        for x in range(len(self.pop.items)):
            quant = getattr(self.pop, "quant" + str(x)).value()
            if quant > 0:  # if the user selected 1 or more items to be popped
                # We get the order that holds them
                order = self.parent.holder.getOrder()
                # We get the item from our pop widget list.
                item = self.pop.items[x]
                if (item.getQuant() - quant) == 0:
                    # When an item is popped and it results in there being 0
                    # of it in the original order, we first get a copy of its
                    # attributes and append it to the list of items to be Added
                    # to the new order, and then we delete it.
                    items.append([item.getName(), quant, item.getPrice()])
                    removeItems.append(item)
                else:
                    # If the item being popped does not result in it being 0
                    # in the original order, then we must modify the original
                    # order item and create a new object with the user selection
                    # in the new order
                    items.append([item.getName(), quant, item.getPrice()])
                    editItems.append([item, item.getQuant() - quant])
        if items:
            session = self.parent.getParent().createSession()
            order = session.holder.getOrder()
            order.multiAdd(items)
        order = self.parent.holder.getOrder()
        if removeItems:
            order.multiRemove(removeItems)
        if editItems:
            order.multiEdit(editItems)
        self.accept()

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(p)


class PopOrderWidget(QWidget):
    """Widget to select items to pop from one order to another one."""

    def __init__(self, parent):
        """Init."""
        super().__init__(parent)

        self.parent = parent
        self.order = self.parent.getParent().holder.getOrder()
        self.items = self.order.getItems()

        self.initUi()

    def initUi(self):
        """UI setup."""
        style = """QLabel {
                     font-family: Asap;
                     font-weight: bold;
                     font-size: 25pt;
                     }
                    QSpinBox {
                     font-family: Asap;
                     font-weight: bold;
                     font-size: 25pt;
                    }"""

        layout = QVBoxLayout()
        x = 0
        for item in self.items:
            name = item.getName()
            x1 = str(x)
            setattr(self, "layout" + x1, QHBoxLayout())
            setattr(self, "quant" + x1, QSpinBox())
            getattr(self, "quant" + x1).setFixedWidth(80)
            getattr(self, "quant" + x1).setStyleSheet(style)
            getattr(self, "quant" + x1).setRange(0, item.getQuant())
            setattr(self, "label" + x1, QLabel(name))
            getattr(self, "label" + x1).setStyleSheet(style)
            getattr(self, "layout" + x1).addWidget(getattr(self, "quant" + x1))
            getattr(self, "layout" + x1).addWidget(getattr(self, "label" + x1))
            getattr(self, "layout" + x1).setStretchFactor(getattr(self, "quant" + x1), 1)
            getattr(self, "layout" + x1).setStretchFactor(getattr(self, "label" + x1), 5)
            layout.addLayout(getattr(self, "layout" + x1))
            x += 1

        layout.addStretch()

        self.setLayout(layout)

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)


class PayDialog(QDialog):
    """Dialog to accept payment for an order."""

    def __init__(self, parent, total):
        """Init."""
        super().__init__(parent, Qt.FramelessWindowHint |
                         Qt.WindowSystemMenuHint)

        self.parent = parent
        self.total = total

        self.ok = False

        self.initUi()

    def initUi(self):
        """Ui setup."""
        style = """QLineEdit {
                     border-radius: 20%;
                     padding-left: 10px;
                     font-family: Asap;
                     font-weight: bold;
                     font-size: 25pt;
                }
                QLabel {
                     font-family: Asap;
                     font-weight: bold;
                     font-size: 25pt;
                     color:white;
                }
                QPushButton {
                    font-family: Asap;
                    font-weight: bold;
                    font-size: 20pt;
                }"""

        btnOk = QPushButton("Aceptar")
        btnOk.clicked.connect(self.acceptMe)
        btnOk.setStyleSheet(style)
        btnCancel = QPushButton("Cancelar")
        btnCancel.setStyleSheet(style)
        btnCancel.clicked.connect(self.reject)

        total = QLabel(str(self.total))
        total.setStyleSheet(style)
        totalLabel = QLabel("Total:")
        totalLabel.setStyleSheet(style)

        self.payment = QLineEdit()
        self.payment.setStyleSheet(style)
        payLabel = QLabel("Paga con:")
        payLabel.setStyleSheet(style)

        validator = QDoubleValidator(0.0, 10000.0, 1, self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.payment.setValidator(validator)

        self.payment.textChanged.connect(lambda: self.setChange(self.payment))

        self.change = QLabel("ERROR")
        self.change.setStyleSheet(style)
        changeLabel = QLabel("Cambio:")
        changeLabel.setStyleSheet(style)

        layout = QGridLayout()

        layout.addWidget(totalLabel, 0, 0)
        layout.addWidget(total, 0, 1)
        layout.addWidget(payLabel, 1, 0)
        layout.addWidget(self.payment, 1, 1)
        layout.addWidget(changeLabel, 2, 0)
        layout.addWidget(self.change, 2, 1)
        layout.addWidget(btnOk, 3, 0)
        layout.addWidget(btnCancel, 3, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def setChange(self, payment):
        """Update the change total."""
        if len(payment.text()) > 0:
            payment = float(payment.text())
            if payment - self.total < 0:
                self.ok = False
                self.change.setText("ERROR")
            else:
                self.ok = True

                self.change.setText(str(round(float(self.payment.text()) - self.total, 2)))
        else:
            self.ok = False
            self.change.setText("ERROR")

    def acceptMe(self):
        """Accept."""
        if self.ok is True:
            payment = float(self.payment.text())
            self.parent.paga = round(payment, 2)
            self.parent.cambio = round(payment - self.total, 2)
            self.parent.printBoth()
            self.accept()

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(p)


class QuestionDialog(QDialog):
    """Dialog to ask a question."""

    def __init__(self, parent, question, style=None):
        """Init."""
        super().__init__(parent, Qt.FramelessWindowHint |
                         Qt.WindowSystemMenuHint)

        self.question = str(question)
        self.style = style

        self.initUi()

    def initUi(self):
        """Ui Setup."""
        self.questionLabel = QLabel(self.question)
        self.questionLabel.setWordWrap(True)

        styleBtn = """
        QPushButton {
            font-family: Asap;
            font-weight: bold;
            font-size: 20pt;
        }"""

        if not self.style:
            self.style = """
            QLabel {
                font-family: Asap;
                font-weight: bold;
                font-size: 45pt;
            }"""
        self.questionLabel.setStyleSheet(self.style)
        self.questionLabel.setAlignment(Qt.AlignCenter)

        btnOk = QPushButton("Aceptar")
        btnOk.setStyleSheet(styleBtn)
        btnOk.clicked.connect(self.accept)
        btnCancel = QPushButton("Cancelar")
        btnCancel.setStyleSheet(styleBtn)
        btnCancel.clicked.connect(self.reject)

        layout = QVBoxLayout()

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(btnOk)
        btnLayout.addWidget(btnCancel)

        layout.addWidget(self.questionLabel)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(p)


class IODialog(QDialog):
    """Dialog to import or export the databases."""

    def __init__(self, parent):
        """Init."""
        super().__init__(parent, Qt.FramelessWindowHint |
                         Qt.WindowSystemMenuHint)

        self.db = DbIO.DbIo(self)
        self.initUi()

    def initUi(self):
        """Ui Setup."""
        style = """
        QPushButton {
            font-family: Asap;
            font-weight: bold;
            font-size: 20pt;
        }
        QLabel {
            font-family: Asap;
            font-weight: bold;
            font-size: 45pt;
        }"""

        btnExport = QPushButton("Exportar")
        btnExport.setStyleSheet(style)
        btnExport.clicked.connect(self.eDb)

        btnImport = QPushButton("Importar")
        btnImport.setStyleSheet(style)
        btnImport.clicked.connect(self.iDb)

        btnCancel = QPushButton("Cancelar")
        btnCancel.setStyleSheet(style)
        btnCancel.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(btnExport)
        layout.addWidget(btnImport)
        layout.addWidget(btnCancel)

        self.setLayout(layout)

    def iDb(self):
        """Import a database and refresh."""
        try:
            self.db.importDb()
            self.accept()
        except PermissionError:
            self.reject()

    def eDb(self):
        """Export all databases."""
        self.db.exportDb()
        self.reject()

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(p)


class InvoiceData(QDialog):
    """Dialog to capture the customer data for the invoice."""

    def __init__(self, rfc, tel, email, name, use, parent):
        """Init."""
        super().__init__(parent, Qt.FramelessWindowHint |
                         Qt.WindowSystemMenuHint)
        self.parent = parent

        self.rfc = rfc
        self.tel = tel
        self.email = email
        self.name = name
        self.use = use

        self.initUi()

    def initUi(self):
        """Ui Setup."""
        style = """
                QLineEdit {
                    border-radius: 20%;
                    padding-left: 10px;
                    font-family: Asap;
                    font-weight: bold;
                    font-size: 25pt;
                }
                QLabel {
                    font-family: Asap;
                    font-weight: bold;
                    font-size: 25pt;
                    color: white;
                }
                QPushButton {
                    font-family: Asap;
                    font-weight: bold;
                    font-size: 20pt;
                }"""

        data = {"rfc": "RFC", "tel": "Telefono", "email": "Email",
                "name": "Nombre", "use": "Uso"}

        x = 0
        inputsLayout = QGridLayout()
        for key, value in data.items():
            setattr(self, key + "Input", QLineEdit())
            # getattr(self, key + "Input").setFixedWidth(150)
            getattr(self, key + "Input").setStyleSheet(style)
            if getattr(self, key):
                getattr(self, key + "Input").setText(str(getattr(self, key)))
            setattr(self, key + "Label", QLabel(value))
            getattr(self, key + "Label").setStyleSheet(style)
            getattr(self, key + "Label").setAlignment(Qt.AlignRight)
            inputsLayout.addWidget(getattr(self, key + "Label"), x, 0)
            inputsLayout.addWidget(getattr(self, key + "Input"), x, 1)
            x += 1

        btnOk = QPushButton("Aceptar")
        btnOk.clicked.connect(self.acceptMe)
        btnOk.setStyleSheet(style)
        btnCancel = QPushButton("Cancelar")
        btnCancel.clicked.connect(self.reject)
        btnCancel.setStyleSheet(style)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(btnOk)
        btnLayout.addWidget(btnCancel)

        layout = QVBoxLayout()
        layout.addLayout(inputsLayout)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

    def verify(self):
        """Verify all fields are filled."""
        data = ["rfc", "tel", "email", "name", "use"]
        state = False
        for item in data:
            if getattr(self, item + "Input").text() != "":
                state = True
            else:
                return False
        return state

    def acceptMe(self):
        """Accept dialog and store values."""
        if self.verify() is True:
            self.parent.invoiceRfc = self.rfcInput.text()
            self.parent.invoiceTel = self.telInput.text()
            self.parent.invoiceEmail = self.emailInput.text()
            self.parent.invoiceName = self.nameInput.text()
            self.parent.invoiceUse = self.useInput.text()
            self.accept()

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(p)
