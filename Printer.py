from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *


class Print(object):
    """Print a Qdialog object."""

    def __init__(self):
        """Init."""
        pass

    def Print(self, dialog, simplified=None, other=None):
        """Print the passed dialog."""
        if simplified:
            printer.setDocName("COMANDA")
        elif other:
            printer.setDocName(str(other))
        else:
            printer.setDocName("TICKET")
        painter = QPainter()
        p = dialog.palette()
        p.setColor(dialog.backgroundRole(), Qt.white)
        dialog.setPalette(p)
        painter.begin(printer)

        xscale = printer.pageRect().width() / dialog.width()
        yscale = printer.pageRect().height() / dialog.height()
        scale = min(xscale, yscale)

        painter.translate(printer.paperRect().x() + printer.pageRect().width() / 2,
                          dialog.height() * 1.39)  # dont know why but 1.39 works

        painter.scale(scale, scale)

        painter.translate(-1 * dialog.width() / 2, -1 * dialog.height() / 2)
        dialog.render(painter)
        painter.end()
