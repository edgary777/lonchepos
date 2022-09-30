"""GUI placement for the order data."""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Holder(QWidget):
    """This holds and shows and manipulates all orders."""

    def __init__(self, parent):
        """Init."""
        super().__init__(parent)

        self.parent = parent
        self.initUI()
        self.addOrder(Order(parent=self))

    def initUI(self):
        """Ui is created here."""
        # This is set as a QScrollArea so oversized orders can be seen
        layout = QVBoxLayout()
        self.area = QScrollArea()

        # This must be done so it can update dynamically
        self.area.setWidgetResizable(True)

        layout.addWidget(self.area)
        self.setLayout(layout)

    def addOrder(self, order):
        """Add an order."""
        self.order = order
        self.area.setWidget(order)

    def getOrder(self):
        """Return the order."""
        return self.order

    def printOrder(self):
        """Print an order."""
        pass

    def recordOrder(self):
        """Add order to data base."""
        pass

    def getParent(self):
        """Return holder's parent."""
        return self.parent


class Order(QWidget):
    """This holds and shows all the selected items for the order."""

    def __init__(self, parent, discount=None):
        """Init."""
        super().__init__(parent)

        self.parent = parent
        self.items = []

        self.initUi()

    def initUi(self):
        """Ui is created here."""
        self.orderLayout = QGridLayout()
        self.orderLayout.setSpacing(0)
        self.orderLayout.setColumnStretch(0, 1)
        self.orderLayout.setColumnStretch(1, 11)

        self.titles = self.createTitles()
        self.orderLayout.addLayout(self.titles, 0, 1)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.orderLayout)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def createTitles(self):
        """Add titles to layout."""
        titles = ["ARTICULO", "CANTIDAD", "PRECIO", "TOTAL"]
        layout = QHBoxLayout()
        for title in titles:
            setattr(self, title, QLabel(title))
            getattr(self, title).setAlignment(Qt.AlignCenter)
            layout.addWidget(getattr(self, title))
            index = titles.index(title)
            if title == "ARTICULO":
                layout.setStretchFactor(getattr(self, title), 3)
            else:
                layout.setStretchFactor(getattr(self, title), 1)
            if index < 3:
                setattr(self, "i" + str(index), Vdivider(parent=self))
                layout.addWidget(getattr(self, "i" + str(index)))
        return layout

    def addItem(self, item):
        """Add an item."""
        # the passed variable item is a list of 3 things, name, ammount and
        # price, in that order
        itemObj = Item(item, parent=self)

        # We search the list of items already in the order, if the item is
        # already in the order then it is added 1.
        search = self.searchItem(item[0])
        if search:
            self.editItem(search, search.getQuant() + 1)
        else:
            self.items.append(itemObj)
            self.update()

    def multiAdd(self, items):
        """Add many items at once."""
        for item in items:
            itemObj = Item(item, parent=self)
            self.items.append(itemObj)
        self.update()

    def decreaseItem(self, item, amount):
        """Decrease item by amount."""
        # the passed variable item is a list of 3 things, name, ammount and
        # price, in that order

        # We search the list of items already in the order, if the item is
        # already in the order then it is decreased by 'amount', if the
        # operation results is 0 or less than 0 then the item is removed.
        search = self.searchItem(item[0])
        if search:
            if search.getQuant() - amount > 0:
                self.editItem(search, search.getQuant() - amount)
            else:
                self.removeItem(search)

    def searchItem(self, item):
        """Pass a name as a string and returns the item with that name."""
        result = None
        for x in self.items:
            if x.getName() == item:
                result = x
        if result:
            return result
        else:
            return None

    def removeItem(self, item):
        """Remove an item."""
        try:
            self.items.remove(item)
            self.update()
        except ValueError:
            print("There was an error removing the item.")

    def multiRemove(self, items):
        """Remove multiple items at once."""
        try:
            for item in items:
                self.items.remove(item)
            self.update()
        except ValueError:
            print("There was an error removing the item.")

    def clean(self):
        """Remove all items."""
        self.items = []
        self.update()

    def extractItem(self, item):
        """Extract an item.

        Remove the item from the list and return it to add it to other list.
        """
        item = self.items.pop(self.items.index(item))
        self.update()
        return item

    def editItem(self, item, edit):
        """Edit an item."""
        item.editQuant(edit)
        self.update()

    def multiEdit(self, edits):
        """Edit many items at once."""
        for item, edit in edits:
            item.editQuant(edit)
        self.update()

    def removeEverything(self):
        """Remove all items from the layout."""
        for i in reversed(range(self.orderLayout.count())):
            if i > 0:
                it = self.orderLayout.itemAt(i)
                try:
                    ob = self.orderLayout.takeAt(i).widget()
                    ob.setParent(None)
                    ob.deleteLater()
                    # self.orderLayout.takeAt(i).widget().deleteLater()
                except AttributeError:
                    for i in reversed(range(it.count())):
                        it.takeAt(i).widget().setParent(None)
                    self.orderLayout.removeItem(it)

    def addEverything(self):
        """Add all items to the layout."""
        if self.items:
            for item in self.items:
                index = self.items.index(item)
                itui = ItemUI(item, index, parent=self)

                self.orderLayout.addWidget(itui.getBtn(), index + 1, 0)
                self.orderLayout.addLayout(itui.getItem(), index + 1, 1)

    def update(self):
        """Update the UI to show changes."""
        # First remove all items.
        self.removeEverything()

        # Then if any left add them back.
        self.addEverything()

        holderParent = self.parent.getParent()
        holderParent.orderTotal.updateTotal(self.getTotal())

    def getTotal(self):
        """Update the UI to show changes."""
        total = 0
        for item in self.items:
            total += item.getTotal()
        return total

    def getItems(self):
        """Return the order products."""
        return self.items

    def getParent(self):
        """Return the order parent."""
        return self.parent


class ItemUI(QWidget):
    """This is the UI representation of each product chosen."""

    def __init__(self, item, index, parent):
        """Init."""
        super().__init__(parent)
        """Item UI and Data representations are separated because I don't.
        want to keep tracking and updating the index of each item in the order.
        I'd rather delete all UI representations every time there is a change
        and create them again from the updated list of items.
        """
        self.item = item
        self.index = index
        self.parent = parent

    def getItem(self):
        """Return Item Ui."""
        attr = ["Name", "Quant", "Price", "Total"]
        layout = QHBoxLayout()
        layout.setSpacing(0)
        style = """QLabel {
                     font-family: Lato Black;
                     font-weight: bold;
                     font-size: 18pt;
                     }"""
        for x in attr:
            label = QLabel(str(getattr(self.item, "get" + x)()))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(style)
            setattr(self, x, WidgetItem(self, label))
            layout.addWidget(getattr(self, x))
            if x == "Name":
                layout.setStretchFactor(getattr(self, x), 3)
            else:
                layout.setStretchFactor(getattr(self, x), 1)
            index = attr.index(x)
            if index < 3:
                setattr(self, "i" + str(index), Vdivider(parent=self))
                layout.addWidget(getattr(self, "i" + str(index)))
        return layout

    def getBtn(self):
        """Return the button to delete the item."""
        style = """QPushButton {
            color: red;
            font-weight: bold;
            font-size: 18pt;
        }"""
        btn = QPushButton("X")
        btn.setStyleSheet(style)
        btn.clicked.connect(lambda: self.parent.removeItem(self.item))
        close = WidgetItem(self, btn)
        return close


class Item(QWidget):
    """This is the data representation of each product chosen."""

    def __init__(self, data, parent):
        """Init."""
        super().__init__(parent)

        self.name = data[0]
        self.quant = data[1]
        self.price = data[2]
        self.total = float(self.quant) * float(self.price)
        self.category = data[3]

    def getCat(self):
        """Return the item category."""
        return self.category

    def editQuant(self, new):
        """Edits the quantity of products and updates the total."""
        self.quant = new
        self.total = self.quant * self.price

    def getName(self):
        """Return the name of the Item."""
        return self.name

    def getQuant(self):
        """Return the amount of items."""
        return self.quant

    def getPrice(self):
        """Return the price of the item."""
        return self.price

    def getTotal(self):
        """Return the total cost of the items."""
        return self.total

    def getCategory(self):
        """Return the category of the item."""
        return self.category


class WidgetItem(QWidget):
    """Widget Item with a border on the top and bottom."""

    def __init__(self, parent, item):
        """Init."""
        super().__init__(parent)

        self.item = item

        self.initUi()

    def initUi(self):
        """Ui creator."""
        topBar = Hdivider(self)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(topBar)
        layout.addWidget(self.item)

        self.setLayout(layout)


class Vdivider(QWidget):
    """Vertical divider."""

    def __init__(self, parent):
        """Init."""
        super().__init__(parent)
        self.setFixedWidth(2)

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)


class Hdivider(QWidget):
    """Vertical divider."""

    def __init__(self, parent):
        """Init."""
        super().__init__(parent)
        self.setFixedHeight(2)

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
