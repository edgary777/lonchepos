from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import Menu
import TextInput
import Holder
import Buttons
import OrderTotal
import Dialogs
import Ticket
import Printer
import datetime
from Db import Db
from hashlib import sha256


class MultiSession(QWidget):
    """Object meant to hold sessions.

    This object handles the sessions creation, destruction and switching.
    """

    def __init__(self, parent):
        """Init."""
        super().__init__(parent)

        self.sessions = []

        self.sessionsLayout = QStackedLayout()
        self.btnLayout = QHBoxLayout()

        # We always start with the session 0 from the array
        self.activeSession = 0

        self.createSession()

        self.initUi()

    def initUi(self):
        """Ui is created here."""
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.sessionsLayout)
        self.layout.addLayout(self.btnLayout)

        self.setLayout(self.layout)

    def createSession(self, appID=None):
        """Create a new session, pass an app name if you want to make it an app session."""
        print("appID 1=", appID)
        if appID:
            session = AppSession(self, appID)
        else:
            session = Session(self)
        self.sessions.append(session)
        self.UpdateUi()
        self.activeSession = self.sessions.index(session)
        self.switchSession(self.activeSession)
        return session

    def kilAll(self):
        """Delete all sessions."""
        self.sessions = []
        self.UpdateUi()

    def deleteSession(self, session, index):
        """Delete a session."""
        if session.getID() == self.activeSession:
            if index > 0:
                # If the activeSession is not 0 then the previous one in the
                # index is the one that is selected.
                self.activeSession = self.sessions[index - 1].getID()
            else:
                # I used try in here because I couldn't think of any other
                # way to not crash the program when the activeSession is 0
                # and there are no other sessions.
                try:
                    self.activeSession = self.sessions[index + 1].getID()
                except IndexError:
                    pass  # nothing to be done here, just avoiding a crash
        self.sessions.remove(session)
        self.UpdateUi()

        # If the active session is the same than the session being deleted,
        # then the activeSession is switched to the one that has the index
        # the one being deleted had, this is to make deleting sessions less
        # confusing
        for session in self.sessions:
            if self.activeSession == session.getID():
                self.switchSession(self.sessions.index(session))
                break

    def switchSession(self, index):
        """Switch session."""
        self.activeSession = self.sessions[index].getID()
        self.UpdateUi()
        self.sessionsLayout.setCurrentIndex(index)

    def cancelOrder(self, session, index):
        """Cancel passed session."""
        # if the order has items, cancel and save to the database
        if session.orderTotal.getTotal() > 0:
            question = "SEGURO QUE QUIERES CANCELAR ESTA ORDEN?"
            dialog = Dialogs.QuestionDialog(self, question)
            if dialog.exec_():
                session.cancelado = 1
                session.printTicket(cancelled=True)
        # if the order is empty, cancel only if it is the last order in the list.
        else:
            if (len(self.sessions) - 1) == self.sessions.index(session):
                self.deleteSession(session, self.sessions.index(session))

    def addEverything(self):
        """Add all Sessions to the layout."""
        # Buttons configuration
        width = 90
        height = 90
        roundness = 10
        color1 = qRgb(101, 60, 240)
        color2 = qRgb(18, 157, 226)
        style = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 25pt;
                font-family: Asap;
            };
            """

        # We loop through all session objects in the self.sessions list and
        # create some UI buttons for each of them
        for session in self.sessions:
            indexN = self.sessions.index(session)  # Get the session index
            sessionID = session.getID()  # Get the session ID (Folio)
            sessionLabel = session.getLabel()
            print("sessionID=", sessionID)
            print("sessionLabel=", sessionLabel)

            # The button object is created
            btn = Buttons.SessionBtn(width, height, roundness, color1, color2,
                                     sessionID, sessionLabel, style, parent=self, obj=self,
                                     index=indexN)

            # the button object is added to the layout
            self.sessionsLayout.addWidget(session)
            self.btnLayout.addWidget(btn)

        # This is the button that creates new sessions.
        dBa = Db()
        appsData = dBa.getAppsData()
        NewSessionBtn = Buttons.NewSessionBtn(width, height, roundness, color1,
                                              style, parent=self, obj=self, apps=appsData)

        # The button that creates new sessions is only added when there are
        # less than 13 sessions on the screen because otherwise they overflow
        # the screen.
        if len(self.sessions) < 13:
            self.btnLayout.addWidget(NewSessionBtn)

    def removeEverything(self):
        """Remove all Sessions from the layout."""
        for i in reversed(range(self.sessionsLayout.count())):
            self.sessionsLayout.takeAt(i).widget().setParent(None)
            # self.sessionsLayout.takeAt(i).widget().deleteLater()

        for i in reversed(range(self.btnLayout.count())):
            # self.btnLayout.takeAt(i).widget().setParent(None)
            # The comment above this comment was the original way to delete the
            # buttons from the buttons layout, and while it worked fine in
            # windows it crashed on linux, so it was changed and it now works
            # on both.
            self.btnLayout.takeAt(i).widget().deleteLater()

    def sessionIndex(self, session):
        """Return session index."""
        return self.sessions.index(session)

    def UpdateUi(self):
        """Update the Ui."""
        self.removeEverything()

        self.addEverything()

        # if all sessions are deleted then a new one is created
        if not self.sessions:
            self.createSession()


class Session(QWidget):
    """Object meant to hold all objects pertaining to an order.

    To enable multi-sessions, each order must be a Session object, all sessions
    objects need to be in either a QStackedLayout or QStackedWidget to be able
    to switch between them.
    """

    def __init__(self, parent, *args, **kwargs):
        """Init."""
        super(Session, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.ticket = None

        self.date = None
        self.hour = None

        self.paga = 0
        self.cambio = 0

        self.llevar = None
        self.np = None

        self.sexo = 0
        self.edad = 0

        self.invoiceRfc = ""
        self.invoiceTel = ""
        self.invoiceEmail = ""
        self.invoiceName = ""
        self.invoiceUse = ""

        self.cancelado = 0

        self.configGroup = None
        if not self.configGroup:
            self.ID = None
            self.setID()
            self.label = self.ID
            self.initUi()


    def initUi(self):
        """Ui is created here.

        DO NOT USE 'x' AS A VARIABLE HERE AGAIN, IT WILL BREAK THE CODE
        """
        self.holder = Holder.Holder(parent=self)

        self.orderTotal = OrderTotal.OrderTotal(0, self)

        dBa = Db()

        categories = dBa.getCategories()
        itemsLayout = QStackedLayout()
        tabs = {}
        x = 0  # this is he only x that can be used in init

        payStyle = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 25pt;
                font-family: Asap;
            };
            """

        llevaStyle = """
            QLabel {
                color: Black;
                font-weight: bold;
                font-size: 15pt;
                font-family: Asap;
            };
            """

        tinyStyle = """
            QRadioButton {
                color: Black;
                font-weight: bold;
                font-family: Asap;
                font-size: 15pt;
            }
            QRadioButton::indicator::unchecked{
                border: 1px solid darkgray;
                border-radius: 10px;
                background-color: yellow;
                width: 20px;
                height: 20px;
                margin-left: 5px;
            }
            QRadioButton::indicator::checked{
                border: 1px solid darkgray;
                border-radius: 10px;
                background-color: black;
                width: 20px;
                height: 20px;
                margin-left: 5px;
            };
            """

        self.payBtn = Buttons.StrokeBtn2(100, 60, 15, qRgb(226,224,33),
                                         "PAGAR", payStyle, self, sWidth=10,
                                         hExpand=True)
        self.payBtn.clicked.connect(self.pay)

        self.llevaBtn = Buttons.StrokeBtn2(100, 60, 15, qRgb(33,46,226),
                                           "L?", llevaStyle, self, sWidth=10)
        self.llevaBtn.clicked.connect(self.toggleLleva)

        self.npBtn = Buttons.StrokeBtn2(100, 60, 15, qRgb(33,46,226),
                                           "P?", llevaStyle, self, sWidth=10)
        self.npBtn.clicked.connect(self.toggleNp)

        sexAgeLayout = QHBoxLayout()

        sexAgeLayout.addStretch()
        sexM = QRadioButton("M")
        sexH = QRadioButton("H")
        self.sexo = QButtonGroup(self)
        self.sexBtns = [sexM, sexH]
        z = 0
        for btn in self.sexBtns:
            btn.setStyleSheet(tinyStyle)
            self.sexo.addButton(btn, x)
            sexAgeLayout.addWidget(btn)
            z += 1

        sexAgeLayout.addSpacing(20)

        age1 = QRadioButton("1")
        age2 = QRadioButton("2")
        age3 = QRadioButton("3")
        age4 = QRadioButton("4")
        self.edad = QButtonGroup(self)
        self.ageBtns = [age1, age2, age3, age4]
        z = 1
        for btn in self.ageBtns:
            btn.setStyleSheet(tinyStyle)
            self.edad.addButton(btn, x)
            sexAgeLayout.addWidget(btn)
            z += 1
        sexAgeLayout.addStretch()

        for category in categories:
            products = dBa.getProducts(category[1], category[3])
            setattr(self, "menu" + category[1], Menu.Menu(products,
                    category[2], self, hold=self.holder))
            itemsLayout.addWidget(getattr(self, "menu" + category[1]))
            tabs[category[0]] = (category[1], x, itemsLayout)
            x += 1
        tabsWidget = Menu.Tabs(tabs, parent=self)
        tabsLayout = QHBoxLayout()
        tabsLayout.addWidget(tabsWidget)

        self.inputField = TextInput.TextInput(parent=self)
        self.nameField = TextInput.TextInputSmall(parent=self)
        self.nameField.setFixedHeight(55)

        nameLayout = QVBoxLayout()
        nameLayout.setSpacing(0)
        nameLayout.addWidget(self.nameField)
        nameLayout.addLayout(sexAgeLayout)

        orderTopLayout = QHBoxLayout()
        orderTopLayout.addLayout(nameLayout)
        orderTopLayout.addWidget(self.orderTotal)

        layoutC11 = QHBoxLayout()
        layoutC11.addWidget(self.npBtn)
        layoutC11.addWidget(self.llevaBtn)
        layoutC11.addWidget(self.payBtn)

        layoutC1 = QVBoxLayout()
        layoutC1.addLayout(orderTopLayout)
        layoutC1.addWidget(self.holder)
        layoutC1.addLayout(layoutC11)

        layoutH1C1 = QHBoxLayout()
        layoutH1C1.addLayout(self.imgBtns())
        layoutH1C1.addLayout(layoutC1)

        layoutC2 = QVBoxLayout()
        layoutC2.addLayout(tabsLayout)
        layoutC2.addLayout(itemsLayout)
        layoutC2.addWidget(self.inputField)

        layout = QHBoxLayout()
        layout.addLayout(layoutH1C1)
        layout.addLayout(layoutC2)

        self.setLayout(layout)

    def imgBtns(self):
        """Image buttons generator and layout creator."""
        names = ["separate", "print", "dcto", "iva", "close", "gear"]
        layout = QVBoxLayout()
        for name in names:
            setattr(self, "picBtn" + name,
                    Buttons.PicButton("Resources/s-" + name,
                                      "Resources/h-" + name,
                                      "Resources/c-" + name, self))
            layout.addWidget(getattr(self, "picBtn" + name))
        layout.addStretch()

        # self.picBtnseparate.clicked.connect(self.separateItems)
        self.picBtnseparate.setActionL(self.separateItems)

        # self.picBtnprint.clicked.connect(self.printSimplified)
        self.picBtnprint.setActionL(self.printSimplified)

        # self.picBtndcto.clicked.connect(self.setDcto)
        self.picBtndcto.setActionL(self.setDcto)

        # self.picBtniva.clicked.connect(lambda: self.orderTotal.toggleTax())
        # self.picBtniva.clicked.connect(self.test)
        self.picBtniva.setActionL(self.taxToggler)
        self.picBtniva.setActionR(self.invoiceD)

        # self.picBtnclose.clicked.connect(lambda:
        #                                  self.holder.getOrder().clean())
        self.picBtnclose.setActionL(self.orderCleaner)

        # self.picBtngear.clicked.connect(self.settingsD)
        self.picBtngear.setActionL(self.settingsD)

        return layout

    def taxToggler(self):
        """Toggle tax state."""
        self.orderTotal.toggleTax()

    def orderCleaner(self):
        """Toggle tax state."""
        self.holder.getOrder().clean()

    def invoiceD(self):
        """Test."""
        dialog = Dialogs.InvoiceData(self.invoiceRfc, self.invoiceTel,
                                     self.invoiceEmail, self.invoiceName,
                                     self.invoiceUse, self)
        if dialog.exec_():
            pass

    def settingsD(self):
        """Show settings dialog."""
        dialog = Dialogs.IODialog(self)
        if dialog.exec_():
            self.parent.kilAll()

    def pay(self):
        """Print, record, and delete order."""
        if self.llevar is not None and self.np is not None:
            dialog = Dialogs.PayDialog(self, self.orderTotal.getTotal())

            if dialog.exec_():
                pass

    def toggleLleva(self):
        """Toggle lleva option."""
        if self.llevar is None:
            self.llevar = False

        if self.llevar is False:
            self.llevar = True
            self.llevaBtn.setText("AQUI")
        else:
            self.llevar = False
            self.llevaBtn.setText("LLEVAR")

    def toggleNp(self):
        """Toggle no option."""
        if self.np is None:
            self.np = False

        if self.np is False:
            self.np = True
            self.npBtn.setText("NP")
        else:
            self.np = False
            self.npBtn.setText("PAG")

    def getSex(self):
        """Return customer sex.

        0 is Mujer -- 1 is Hombre
        """
        sexo = self.sexo.checkedId()
        return 0 if sexo < 0 else sexo

    def getAge(self):
        """Return customer age."""
        edad = self.edad.checkedId()
        return 0 if edad < 0 else edad

    def setTime(self):
        """Fix order time to current."""
        if not self.date:
            self.date = datetime.date.today()
        if not self.hour:
            self.hour = datetime.datetime.now().time().strftime("%H:%M")

    def printBoth(self, forceBoth=False):
        """Print simple and complete tickes."""
        # If the session has no set date the order hasn't been printed
        # before, so we print both, otherwise we just print the ticket.
        if self.orderTotal.getTotal() == 0:
            self.parent.deleteSession(self, self.parent.sessionIndex(self))
        if not self.date or forceBoth is True:
            self.printSimplified()
        self.printTicket()

    def printTicket(self, cancelled=False):
        """Simplified ticket printer."""
        if self.orderTotal.getTotal() > 0:
            self.setTime()
            ticket = Ticket.Ticket(self.collector(), self, cancelled=cancelled)
            # if ticket.exec_():
            #     pass
            printer = Printer.Print()
            printer.Print(ticket)
            printer = None
            ticket.setParent(None)
            db = Db()
            db.recordTicket(self.collector())
            self.parent.deleteSession(self, self.parent.sessionIndex(self))

    def printSimplified(self):
        """Simplified ticket printer."""
        if self.orderTotal.getTotal() > 0:
            if self.llevar is not None and self.np is not None:
                self.setTime()
                ticket = Ticket.Ticket(self.collector(), self, simplified=True)
                # if ticket.exec_():
                #     pass
                printer = Printer.Print()
                printer.Print(ticket, simplified=True)
                printer = None
                ticket.setParent(None)

    def separateItems(self):
        """Toggle and update discount."""
        if self.orderTotal.getTotal() > 0:
            dialog = Dialogs.PopOrderDialog(self)

            if dialog.exec_():
                pass

    def setDcto(self):
        """Toggle and update discount."""
        if self.orderTotal.getTotal() > 0:
            dcto = self.orderTotal.getDcto()
            dialog = Dialogs.DctDialog(self.orderTotal.getTotal(nodcto=True), parent=self,
                                       percentage=dcto[1], amount=dcto[2],
                                       code=dcto[3])
            if dialog.exec_():
                pass

    def setID(self):
        """Set an id for the session."""
        sessions = self.parent.sessions
        db = Db()
        if not sessions:
            self.ID = db.getFolio() + 1
        else:
            looping = True
            x_iter = 1
            while looping:
                if not sessions[len(sessions) - x_iter].getID():
                    x_iter += 1
                else:
                    self.ID = sessions[len(sessions) - (x_iter)].getID() + 1
                    looping = False
            if self.ID < db.getFolio() + 1:
                self.ID = db.getFolio() + 1

    def getID(self):
        """Return an id for the session."""
        return self.ID
    
    def getLabel(self):
        """Return the session label."""
        return self.label

    def getParent(self):
        """Return the order parent."""
        return self.parent

    def collector(self):
        """Collect and return all data to be recorded on the database."""
        items = {"factura": self.orderTotal.getInvoice(),
                 "descuento": self.orderTotal.getDcto()[0],
                 "descuentop": self.orderTotal.getDcto()[1],
                 "descuentoa": self.orderTotal.getDcto()[2],
                 "Np": self.np,
                 "Llevar": self.llevar}

        for key, value in items.items():
            if not value or value is False:
                setattr(self, key, 0)
            else:
                if value is True:
                    value = 1
                setattr(self, key, value)

        db = Db()
        if not self.configGroup:
            headerConfig = db.getConfigGroup("LOCAL")
        else:
            headerConfig = db.getConfigGroup(self.configGroup)

        data = {
            "imagen": headerConfig["imagen_ticket"],
            "titulo": headerConfig["titulo"],
            "direccion": headerConfig["direccion"],
            "regimen": headerConfig["regimen_fiscal"],
            "RFC": headerConfig["RFC"],
            "nombreFiscal": headerConfig["nombre"],
            "telLocal": headerConfig["telefono"],
            "folio": self.getID(),
            "nombre": self.nameField.getText(),
            "llevar": self.Llevar,  # Capitalized because different
            "pagado": self.Np,  # Capitalized because different
            "sexo": self.getSex(),
            "edad": self.getAge(),
            "notas": self.inputField.getText(),
            "factura": self.factura,
            "total": self.orderTotal.getTotal(nodcto=True),
            "subtotal": self.orderTotal.getSubtotal(),
            "iva": self.orderTotal.getVat(),
            "descuento": self.descuento,
            "descuentoa": self.descuentoa,
            "descuentop": self.descuentop,
            "cupon": self.orderTotal.getDcto()[3],
            "paga": self.paga,
            "cambio": self.cambio,
            "cancelado": self.cancelado,
            "productos": self.holder.getOrder().getItems(),
            "fecha": self.date,
            "hora": self.hour,
            "facRfc": self.invoiceRfc,
            "facTelefono": self.invoiceTel,
            "facEmail": self.invoiceEmail,
            "facNombre": self.invoiceName,
            "facUso": self.invoiceUse
        }
        return data


class AppSession(Session):
    """Subclass of Session meant to hold all objects pertaining to an app order"""

    def __init__(self, parent, appID, *args, **kwargs):
        self.appID = appID
        self.configGroup = "APP"
        super(AppSession, self).__init__(parent, *args, **kwargs)
        self.label = "app"
        self.ID = self.setID()
        self.newAppFolio = None

    def initUi(self):
        """Ui is created here.

        DO NOT USE 'x' AS A VARIABLE HERE AGAIN, IT WILL BREAK THE CODE
        """
        self.holder = Holder.Holder(self)

        self.orderTotal = OrderTotal.OrderTotal(0, self)

        dBa = Db()

        categories = dBa.getAppCategories(self.appID)
        itemsLayout = QStackedLayout()
        tabs = {}
        x = 0  # this is he only x that can be used in init

        payStyle = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 25pt;
                font-family: Asap;
            };
            """

        llevaStyle = """
            QLabel {
                color: Black;
                font-weight: bold;
                font-size: 15pt;
                font-family: Asap;
            };
            """

        tinyStyle = """
            QRadioButton {
                color: Black;
                font-weight: bold;
                font-family: Asap;
                font-size: 15pt;
            }
            QRadioButton::indicator::unchecked{
                border: 1px solid darkgray;
                border-radius: 10px;
                background-color: yellow;
                width: 20px;
                height: 20px;
                margin-left: 5px;
            }
            QRadioButton::indicator::checked{
                border: 1px solid darkgray;
                border-radius: 10px;
                background-color: black;
                width: 20px;
                height: 20px;
                margin-left: 5px;
            };
            """

        self.payBtn = Buttons.StrokeBtn2(100, 60, 15, qRgb(226,0,0),
                                         "PAGAR", payStyle, self, sWidth=10,
                                         hExpand=True)
        self.payBtn.clicked.connect(self.pay)

        self.llevaBtn = Buttons.StrokeBtn2(100, 60, 15, qRgb(33,46,226),
                                           "L?", llevaStyle, self, sWidth=10)
        self.llevaBtn.clicked.connect(self.toggleLleva)

        self.npBtn = Buttons.StrokeBtn2(100, 60, 15, qRgb(33,46,226),
                                           "P?", llevaStyle, self, sWidth=10)
        self.npBtn.clicked.connect(self.toggleNp)

        sexAgeLayout = QHBoxLayout()

        sexAgeLayout.addStretch()
        sexM = QRadioButton("M")
        sexH = QRadioButton("H")
        self.sexo = QButtonGroup(self)
        self.sexBtns = [sexM, sexH]
        z = 0
        for btn in self.sexBtns:
            btn.setStyleSheet(tinyStyle)
            self.sexo.addButton(btn, x)
            sexAgeLayout.addWidget(btn)
            z += 1

        sexAgeLayout.addSpacing(20)

        age1 = QRadioButton("1")
        age2 = QRadioButton("2")
        age3 = QRadioButton("3")
        age4 = QRadioButton("4")
        self.edad = QButtonGroup(self)
        self.ageBtns = [age1, age2, age3, age4]
        z = 1
        for btn in self.ageBtns:
            btn.setStyleSheet(tinyStyle)
            self.edad.addButton(btn, x)
            sexAgeLayout.addWidget(btn)
            z += 1
        sexAgeLayout.addStretch()

        for category in categories:
            products = dBa.getProducts(category[1], category[3])
            setattr(self, "menu" + category[1], Menu.Menu(products,
                    category[2], self, hold=self.holder))
            itemsLayout.addWidget(getattr(self, "menu" + category[1]))
            tabs[category[0]] = (category[1], x, itemsLayout)
            x += 1
        tabsWidget = Menu.Tabs(tabs, parent=self)
        tabsLayout = QHBoxLayout()
        tabsLayout.addWidget(tabsWidget)

        self.inputField = TextInput.TextInput(parent=self)
        self.nameField = TextInput.TextInputSmall(parent=self)
        self.nameField.setFixedHeight(55)

        nameLayout = QVBoxLayout()
        nameLayout.setSpacing(0)
        nameLayout.addWidget(self.nameField)
        nameLayout.addLayout(sexAgeLayout)

        orderTopLayout = QHBoxLayout()
        orderTopLayout.addLayout(nameLayout)
        orderTopLayout.addWidget(self.orderTotal)

        layoutC11 = QHBoxLayout()
        layoutC11.addWidget(self.npBtn)
        layoutC11.addWidget(self.llevaBtn)
        layoutC11.addWidget(self.payBtn)

        layoutC1 = QVBoxLayout()
        layoutC1.addLayout(orderTopLayout)
        layoutC1.addWidget(self.holder)
        layoutC1.addLayout(layoutC11)

        layoutH1C1 = QHBoxLayout()
        layoutH1C1.addLayout(self.imgBtns())
        layoutH1C1.addLayout(layoutC1)

        layoutC2 = QVBoxLayout()
        layoutC2.addLayout(tabsLayout)
        layoutC2.addLayout(itemsLayout)
        layoutC2.addWidget(self.inputField)

        layout = QHBoxLayout()
        layout.addLayout(layoutH1C1)
        layout.addLayout(layoutC2)

        self.setLayout(layout)

    def printBoth(self, forceBoth=False):
        """Print simple and complete tickes."""
        # If the session has no set date the order hasn't been printed
        # before, so we print both, otherwise we just print the ticket.
        self.printTicket()

    def printTicket(self, cancelled=False):
        """Simplified ticket printer."""
        if self.orderTotal.getTotal() > 0:
            self.setTime()
            ticket = Ticket.Ticket(self.collector(), self, cancelled=cancelled, simplified=True)
            # if ticket.exec_():
            #     pass
            printer = Printer.Print()
            printer.Print(ticket)
            printer = None
            ticket.setParent(None)
            db = Db()
            db.recordTicket(self.collector())
            self.parent.deleteSession(self, self.parent.sessionIndex(self))

    def printSimplified(self):
        """Regular ticket printer."""
        if self.orderTotal.getTotal() > 0:
            if self.llevar is not None and self.np is not None:
                self.setTime()
                ticket = Ticket.Ticket(self.collector(), self)
                # if ticket.exec_():
                #     pass
                printer = Printer.Print()
                printer.Print(ticket, simplified=True)
                printer = None
                ticket.setParent(None)

    def setID(self):
        """Set an id for the session."""
        # I honestly don't know why this is working, it is working on the belief
        # that getID will return None, but it shouldn't be returning None,
        # it should be returning the ID.
        sessions = self.parent.sessions
        db = Db()
        if not sessions:
            folio = db.getFolio() + 1
        else:
            looping = True
            x_iter = 1
            while looping:
                if not sessions[len(sessions) - x_iter].getID():
                    x_iter += 1
                else:
                    folio = sessions[len(sessions) - x_iter].getID()
                    looping = False
            print("folio", folio)
            folio = folio + 1
            if folio < db.getFolio() + 1:
                folio = db.getFolio() + 1
        self.setNewAppID(folio, x_iter)

    def setNewAppID(self, folio, x_iter):
        """Set a different appID for the apps"""
        self.ID = folio + x_iter
        newAppID = str(folio + x_iter)
        if folio < 10:
            folio = "0" + str(folio - 1)
        else:
            folio = str(folio - 1)
        hashedID = sha256(newAppID.encode()).hexdigest()[:2]
        newAppID = folio + hashedID
        self.label = newAppID
