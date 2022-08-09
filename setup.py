from PyQt5.QtWidgets import QApplication

from wac.widget_main_window import MainWindow


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = MainWindow()    
    w.show()
    sys.exit(app.exec_())