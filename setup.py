from PyQt5.QtWidgets import QApplication

from wac.widget_main_window import MainWindow
from wac.theme import ApplicationTheme


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setPalette(ApplicationTheme())
    
    w = MainWindow()    
    w.show()
    sys.exit(app.exec_())