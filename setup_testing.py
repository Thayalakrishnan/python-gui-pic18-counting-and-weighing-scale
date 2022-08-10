import sys
from PyQt5.QtWidgets import QApplication

from testing.widget_serialtesting import RealTimeSender
from wac.theme import ApplicationTheme


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(ApplicationTheme())
    w = RealTimeSender()

    w.show()
    sys.exit(app.exec_())