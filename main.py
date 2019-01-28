import sys
import os
import atexit
import logging
import inspect
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt5.QtCore import Qt
import Session

# Logging errors to a file should only happen when the program has been freezed.
# The logging will only be used when the file path and python path are the same.

# Find the file path and split it to a list.
filePath = inspect.stack()[0][1].split('/')
# Remove the file from the path to get the directory.
del filePath[len(filePath) - 1]
# Turn the path into a string again.
filePath = "/".join(filePath)

if os.path.dirname(sys.executable) == filePath:

    logging.basicConfig(filmoveename=os.path.dirname(sys.executable) + '/errors.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger('mylogger')

    def my_handler(type, value, tb):
        """Error handler."""
        logger.exception("Uncaught exception: {0}".format(str(value)))

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
