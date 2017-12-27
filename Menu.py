from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import Buttons


class Menu(QWidget):
    """Food Menu widget."""

    def __init__(self, items, color, parent, hold=None):
        """Init."""
        super().__init__(parent)

        self.hold = hold  # This is the holder object that contains this menu

        self.color = color
        self.items = items
        self.initUi()

    def initUi(self):
        """Ui Setup."""
        # List setup
        layout = QGridLayout()

        # Common style settings for the buttons
        width = 150
        height = 60
        roundness = 20
        style = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 17pt;
                font-family: Asap;
            };
            """

        # Starting QGridLayout coords for the buttons
        x = 0
        y = 0

        for item in self.items:
            # Buttons color
            color = self.color

            # Buttons creator
            setattr(self, "btn" + item[1], Buttons.MenuBtn(width, height, roundness,
                                                color, item, style,
                                                parent=self, holder=self.hold))
            if y == 4:
                x += 1
                y = 0
            layout.addWidget(getattr(self, "btn" + item[1]), x, y)
            y += 1
        self.setLayout(layout)


class Tabs(QWidget):
    """Food Menu widget."""

    def __init__(self, items, parent=None):
        """Init."""
        super().__init__(parent)

        self.items = items
        self.initUi()

    def initUi(self):
        """Ui Setup."""
        # List setup
        # items = self.items
        # items = [item.strip() for item in items.split(',')]

        # Buttons configuration
        width = 150
        height = 70
        roundness = 20
        color = qRgb(154, 179, 174)
        style = """
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 30pt;
                font-family: Asap;
            };
            """

        # Buttons creator
        layout = QHBoxLayout()
        for key, value in self.items.items():
            setattr(self, key, Buttons.StrokeBtn(width, height, roundness,
                    color, key, style, index=value[0], obj=value[1],
                    parent=self))
            layout.addWidget(getattr(self, key))
        self.setLayout(layout)
