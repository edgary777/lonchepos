import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt5.QtCore import Qt
import Session
import logging
import os
import traceback

path = os.path.realpath(__file__)
# Configure logger to write to a file...
logging.basicConfig(filename=path + '.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger()


def my_handler(type, value, tb):
    """Exception loger format."""
    tr = traceback.extract_tb(tb)
    trace = ""
    for row in tr:
        trace += str(row) + "\n"
    logger.exception("""Uncaught exception: {} | value {} | trace: \n{}""".format(str(value), value, trace))


# Install exception handler
sys.excepthook = my_handler


class MainWindow(QWidget):
    """Main window widget."""

    def __init__(self):
        """Init."""
        super().__init__()

        self.initUi()

    def initUi(self):
        """Ui Setup."""
        start = Session.MultiSession(self)
        layout = QVBoxLayout()
        layout.addWidget(start)

        self.setLayout(layout)

    def paintEvent(self, event):
        """Set window background color."""
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)


app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()
sys.exit(app.exec_())
