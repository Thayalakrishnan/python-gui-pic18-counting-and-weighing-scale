from PyQt5 import QtGui, QtCore, QtSerialPort
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtWidgets import (
    QLCDNumber,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QStatusBar,
    QWidget,
    QMainWindow,
)

import sys
from matplotlib.pyplot import text
import numpy as np
import pyqtgraph as pg

# pg.setConfigOption('foreground', 'r')

COM_PORT = "COM9"
BAUD_RATE = 9600


QSS = """
QLCDNumber {
    background-color: black;
    color: red;
    font-szie: 24px;      
}
"""


class SerialInterface(QtSerialPort.QSerialPort):

    finished = pyqtSignal()  # when the object is killed
    serial_receive = pyqtSignal(int)  # serial data that is received

    # status signals
    serial_status = pyqtSignal(bool)  # serial serial_status : Connected | Disconnected
    serial_terminate = pyqtSignal(bool)

    # response signals
    serial_connected = pyqtSignal()
    serial_disconnected = pyqtSignal()

    def __init__(self, parent=None):
        super(SerialInterface, self).__init__(parent)
        self.port_name = COM_PORT
        self.baud_rate = BAUD_RATE
        self.running = False
        self.timer = QTimer(self)
        self.timer.setInterval(10)

        self.SerialStatus()

    # [Slot] Terminate the Serial Connection and the associated thread
    @pyqtSlot()
    def Terminate(self):
        self.running = True if self.isOpen() else False
        if self.running:
            self.close()
            self.timer.stop()
            self.running = False

        self.SerialStatus()
        print("Terminating Thread")
        self.serial_terminate.emit(True)
        self.finished.emit()

    """
    [Slot] Receive serial input 
    """

    def Receive(self):
        while self.canReadLine():
            raw_as_input = self.readLine().data()
            print(raw_as_input)
            raw_input = raw_as_input.decode()
            self.serial_receive.emit(int(raw_input))

    # emit the current serial status
    def SerialStatus(self):
        self.serial_status.emit(self.running)

    # Workers run method
    def run(self):
        # set port name and baud rate
        self.setPortName(self.port_name)
        self.setBaudRate(self.baud_rate)

        # check if the serial is already connected
        if self.running:
            self.serial_status.emit(self.running)

        else:
            # if not , connect  and start the timer
            self.running = self.open(self.ReadWrite)
            self.timer.start()
            self.timer.timeout.connect(self.Receive)

        self.SerialStatus()


class LivePlotter(QWidget):
    def __init__(self, parent=None):
        super(LivePlotter, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.verticalLayout = QVBoxLayout()
        pen = pg.mkPen(color="r")
        self.win = pg.GraphicsLayoutWidget()
        self.myPlot = self.win.addPlot()
        self.data = np.zeros(10000)
        self.curve = self.myPlot.plot(self.data, pen=pen)

        self.myPlot.setYRange(0, 1000)
        self.verticalLayout.addWidget(self.win)
        self.setLayout(self.verticalLayout)

    @pyqtSlot(int)
    def update(self, rawInt):
        print(rawInt)
        self.data[:-1] = self.data[1:]
        self.data[-1] = rawInt
        self.curve.setData(self.data)


class MainWindow(QMainWindow):

    terminate_serial = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.live_plotter = LivePlotter()
        self.setupUi()

    def setupUi(self):
        self.setAutoFillBackground(False)
        self.centralwidget = QtGui.QWidget(self)
        self.btnconnect = QPushButton(text="Connect", clicked=self.runSerialConnection)

        self.lcdoutput = QLCDNumber(self)
        self.lcdoutput.setSegmentStyle(QLCDNumber.Flat)
        self.lcdoutput.setStyleSheet(QSS)
        self.lcdoutput.setMinimumHeight(50)

        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.addWidget(self.btnconnect)
        self.verticalLayout.addWidget(self.live_plotter)
        self.verticalLayout.addWidget(self.lcdoutput)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setSpacing(10)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

    # function to establish a serial connection on a separate thread
    def runSerialConnection(self):
        self.thread = QThread()
        self.worker = SerialInterface()
        # move the worker the thread
        self.worker.moveToThread(self.thread)
        # start the worker
        self.thread.started.connect(self.worker.run)
        # connect the workers finished signal
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        # connect the threads finished signals
        self.thread.finished.connect(self.thread.deleteLater)
        # start the thread
        self.thread.start()

        ## Worker ---> Mainwindow
        self.terminate_serial.connect(self.worker.Terminate)
        self.worker.serial_receive.connect(self.live_plotter.update)
        self.worker.serial_receive.connect(self.lcdoutput.display)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Window Close",
            "Are you sure you want to close the window?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.terminate_serial.emit()
            event.accept()
            print("Window closed")
        else:
            event.ignore()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
    print("DONE")
