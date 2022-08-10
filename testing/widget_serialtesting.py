"""
RealTimeSender
This package contains the RealTimeSender class used for simulating and testing the serial connection
"""
import numpy as np
from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSlot, QTimer, QIODevice, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QLCDNumber,
    QWidget,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDial,
    QLabel,
    QFrame,
    QGroupBox,
    QGridLayout,
)

""" 
LCDWidgetHelper
This class creates an instance of the rangefiner application, inclduing the layout,
the serial connection and the plotting options. 
Buttons on the interface allow for interaction with the board

This Class subclasses the QtWidgets to create an instance

Methods from this class control the user interaction.
"""


def GenericLayoutHelper(layout_box, arr_widgets):
    for w in arr_widgets:
        layout_box.addWidget(w)
    return layout_box


def LCDWidgetHelper(
    lcd_object_name, lcd_has_decimal_point, lcd_size_width, lcd_size_height
) -> QLCDNumber:
    lcd = QLCDNumber()
    lcd.setFrameShape(QFrame.NoFrame)
    lcd.setFrameShadow(QFrame.Plain)
    lcd.setSmallDecimalPoint(lcd_has_decimal_point)
    lcd.setObjectName(lcd_object_name)
    lcd.setFixedSize(lcd_size_width, lcd_size_height)
    return lcd


SERIALTESTING_STYLE = """
QLabel {
    background-color: none;
    font-size: 36px;    
    border: none;  
}

QPushButton {
    font-size: 12px;    
    font-weight: bold;
}

QPushButton::hover {
    background-color: white;
    color: black;    
}


QVBoxLayout,
QHBoxLayout,
QLineEdit,
QTextEdit,
QPushButton,
QFrame, 
QLabel, 
QDial {
}

QGroupBox {
    font-size: 12px;
    font-weight: bold;
}


QGroupBox::title {
    subcontrol-origin: border;
    subcontrol-position: top left; 
}

"""


HEIGHT = 50
WIDTH = 200


class RealTimeSender(QWidget):
    """The constructor."""

    def __init__(self, parent=None):
        super(RealTimeSender, self).__init__(parent)

        self.final_weight = 0
        self.final_weight_count = 0
        self.final_count = 0

        """
        Text and Line Edits
        """
        self.lineedit_message = QLineEdit()
        self.lineedit_message.setFixedHeight(HEIGHT)

        self.textedit_output = QTextEdit(readOnly=True)
        self.textedit_output.setFixedWidth(WIDTH)

        """ Timers (ms) """
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)

        """ Buttons """
        self.btn_lineedit_send = QPushButton(
            text="Send to Board", clicked=self.btn_lineedit_send_clicked
        )
        self.btn_lineedit_send.setFixedSize(WIDTH, HEIGHT)

        self.btn_send = QPushButton(
            text="Send Data (Initial Weight)", clicked=self.send
        )
        self.btn_send.setFixedSize(WIDTH, HEIGHT)

        self.btn_connect = QPushButton(
            text="Connect", checkable=True, toggled=self.on_toggled
        )
        self.btn_connect.setStyleSheet("background-color:red;color:black;")
        self.btn_connect.setFixedSize(WIDTH, HEIGHT)

        self.btn_start_weigh = QPushButton(
            text="Start Weigh", clicked=self.btn_start_weigh_clicked
        )
        self.btn_start_weigh.setFixedSize(WIDTH, HEIGHT)

        self.btn_weigh = QPushButton(
            text="Weigh/Re-Weigh", clicked=self.btn_weigh_clicked
        )
        self.btn_weigh.setFixedSize(WIDTH, HEIGHT)

        self.btn_count = QPushButton(
            text="Count/Re-count", clicked=self.btn_count_clicked
        )
        self.btn_count.setFixedSize(WIDTH, HEIGHT)

        self.btn_start_count = QPushButton(
            text="Start Count", clicked=self.btn_start_count_clicked
        )
        self.btn_start_count.setFixedSize(WIDTH, HEIGHT)

        self.btn_finish = QPushButton(
            text="Finish/Reset", clicked=self.btn_finish_clicked
        )
        self.btn_finish.setFixedSize(WIDTH, HEIGHT)

        self.btn_calibrate = QPushButton(
            text="Calibrate", clicked=self.btn_calibrate_clicked
        )
        self.btn_calibrate.setFixedSize(WIDTH, HEIGHT)

        self.btn_tare = QPushButton(text="Tare", clicked=self.btn_tare_clicked)
        self.btn_tare.setFixedSize(WIDTH, HEIGHT)

        self.btn_startup = QPushButton(text="Startup", clicked=self.btn_startup_clicked)
        self.btn_startup.setFixedSize(WIDTH, HEIGHT)

        """
        fonts
        """
        lcd_font = QFont("Consolas")

        """
        Initial Weight Dial
        """
        self.dial_initial_weight = QDial()
        self.dial_initial_weight.setNotchesVisible(True)
        self.dial_initial_weight.setWrapping(False)
        self.dial_initial_weight.setMinimum(0)
        self.dial_initial_weight.setMaximum(1000)
        self.dial_initial_weight.setFixedSize(WIDTH, 200)
        self.dial_initial_weight.setValue(74)

        self.lbl_dial_initial_weight = QLabel(self, text=f"{0:03d}g")
        self.lbl_dial_initial_weight.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.lbl_dial_initial_weight.setFont(lcd_font)
        self.lbl_dial_initial_weight.setNum(74)
        self.lbl_dial_initial_weight.setFixedSize(WIDTH, HEIGHT)
        self.dial_initial_weight.valueChanged.connect(self.set_weight_dial_lbl_value)

        """
        Count Weight Dial
        """
        self.dial_count_weight = QDial()
        self.dial_count_weight.setNotchesVisible(True)
        self.dial_count_weight.setWrapping(False)
        self.dial_count_weight.setMinimum(0)
        self.dial_count_weight.setMaximum(1000)
        self.dial_count_weight.setFixedSize(WIDTH, 200)
        self.dial_count_weight.setValue(565)

        self.lbl_dial_count_weight = QLabel(self, text=f"{0:03d}g")
        self.lbl_dial_count_weight.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.lbl_dial_count_weight.setFont(lcd_font)
        self.lbl_dial_count_weight.setNum(565)
        self.lbl_dial_count_weight.setFixedSize(WIDTH, HEIGHT)
        self.dial_count_weight.valueChanged.connect(self.set_count_dial_lbl_value)

        """ Layout """
        gbox_initial_weight = QGroupBox(self, title="Initial Weight")
        weight_dial_layout = QVBoxLayout()
        weight_dial_layout.addWidget(self.lbl_dial_initial_weight)
        weight_dial_layout.addWidget(self.dial_initial_weight)
        gbox_initial_weight.setLayout(weight_dial_layout)

        gbox_count_weight = QGroupBox(self, title="Count Weight")
        count_dial_layout = QVBoxLayout()
        count_dial_layout.addWidget(self.lbl_dial_count_weight)
        count_dial_layout.addWidget(self.dial_count_weight)
        gbox_count_weight.setLayout(count_dial_layout)

        gbox_lineedit = QGroupBox(self, title="Send Custom Command")
        lineedit_layout = QHBoxLayout()
        lineedit_layout.addWidget(self.lineedit_message)
        lineedit_layout.addWidget(self.btn_lineedit_send)
        gbox_lineedit.setLayout(lineedit_layout)

        gbox_btns = QGroupBox(self, title="Interface Buttons")
        btn_grid = QGridLayout()
        btn_grid.addWidget(self.btn_send, 0, 0)
        btn_grid.addWidget(self.btn_connect, 0, 1)
        btn_grid.addWidget(self.btn_calibrate, 0, 2)
        btn_grid.addWidget(self.btn_tare, 1, 0)
        btn_grid.addWidget(self.btn_startup, 1, 1)
        btn_grid.addWidget(self.btn_weigh, 1, 2)
        btn_grid.addWidget(self.btn_count, 2, 0)
        btn_grid.addWidget(self.btn_start_weigh, 2, 1)
        btn_grid.addWidget(self.btn_start_count, 2, 2)
        btn_grid.addWidget(self.btn_finish, 3, 0)
        gbox_btns.setLayout(btn_grid)

        gbox_textedit = QGroupBox(self, title="Serial View")
        textedit_layout = QVBoxLayout()
        textedit_layout.addWidget(self.textedit_output)
        gbox_textedit.setLayout(textedit_layout)

        widget_grid = QGridLayout(self)
        widget_grid.addWidget(gbox_initial_weight, 0, 0)
        widget_grid.addWidget(gbox_count_weight, 0, 1)
        widget_grid.addWidget(gbox_lineedit, 1, 0, 1, 3)
        widget_grid.addWidget(gbox_btns, 2, 0, 2, 3)
        widget_grid.addWidget(gbox_textedit, 0, 2)

        self.setLayout(widget_grid)
        self.setWindowTitle("WAC Testing Module")

        """ 
        Serial Connection configuration 
        """
        self.serial = QtSerialPort.QSerialPort(
            "COM6",
            baudRate=QtSerialPort.QSerialPort.Baud9600,
            readyRead=self.receive,
        )
        self.rng = np.random.default_rng(12345)
        self.serial.open(self.serial.ReadWrite)

        self.setStyleSheet(SERIALTESTING_STYLE)

    """ 
    Method to read from serial, convert the data and send it to be plotted
    """
    #  @param self The object pointer
    @pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            raw_input_data = self.serial.readLine().data().decode()
            command = raw_input_data.rstrip("\r\n")
            self.textedit_output.append(f"[Received] {command}")

            if command == "-f":
                self.send_weight_data()
                self.send_command("-f")
            elif command == "-g":
                self.send_count_data()
                self.send_command("-g")
            else:
                self.send_command(command)

    """ Method to send commands via serial
    #  @param self The object pointer"""

    @pyqtSlot()
    def send(self):
        for i in range(1000):
            weight = self.get_weight(self.dial_initial_weight.value())
            self.send_weight(weight)

    """ Method to create a serial connection with the board
    #  @param self The object pointer"""

    @pyqtSlot()
    def send_weight_data(self):

        for i in range(1000):
            weight = self.get_weight(self.dial_initial_weight.value())
            self.send_weight(weight)

        for i in range(1000):
            weight = self.get_weight(self.dial_initial_weight.value())
            self.send_weight(weight)

        self.final_weight = self.get_weight(self.dial_initial_weight.value())
        self.send_final_value(self.final_weight)

    @pyqtSlot()
    def send_count_data(self):

        for i in range(1000):
            weight = self.get_weight(self.dial_count_weight.value())
            self.send_weight(weight)

        for i in range(1000):
            weight = self.get_weight(self.dial_count_weight.value())
            self.send_weight(weight)

        self.final_weight_count = self.get_weight(self.dial_count_weight.value())
        self.final_count = int(self.final_weight_count // self.final_weight)
        self.send_final_value(self.final_count)

    @pyqtSlot(bool)
    def on_toggled(self, checked):
        self.textedit_output.append(f"{'Connected' if checked else 'Disconnected'}")

        self.btn_connect.setText("Disconnect" if checked else "Connect")
        self.btn_connect.setStyleSheet(
            "background-color:green;color:white;"
            if checked
            else "background-color:red;color:black;"
        )
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QIODevice.ReadWrite):
                    self.btn_connect.setChecked(False)
        else:
            self.serial.close()

    def set_weight_dial_lbl_value(self):
        self.lbl_dial_initial_weight.setNum(self.dial_initial_weight.value())

    def set_count_dial_lbl_value(self):
        self.lbl_dial_count_weight.setNum(self.dial_count_weight.value())

    def get_weight(self, initial):
        low, high = initial - 2, initial + 2
        return self.rng.integers(low=low, high=high)

    def send_weight(self, weight):
        command = f"{weight}\r\n"
        self.serial.write(command.encode())

    def send_final_value(self, value):
        command = f"#{value}&\r\n"
        self.serial.write(command.encode())

    @pyqtSlot()
    def btn_lineedit_send_clicked(self):
        msg = self.lineedit_message.text()
        command = f"{msg}\r\n"
        self.serial.write(command.encode())
        self.textedit_output.append(f"[Sent] {command}")

    def btn_calibrate_clicked(self):
        self.send_command("-d")

    def btn_tare_clicked(self):
        self.send_command("-e")

    def btn_weigh_clicked(self):
        self.send_command("-f")

    def btn_count_clicked(self):
        self.send_command("-g")

    def btn_start_weigh_clicked(self):
        self.send_command("-h")

    def btn_start_count_clicked(self):
        self.send_command("-i")

    def btn_finish_clicked(self):
        self.send_command("-j")

    def btn_startup_clicked(self):
        self.send_command("-k")

    def send_command(self, command):
        to_send = f"{command}\r\n"
        self.serial.write(to_send.encode())
        self.textedit_output.append(f"[Sent] {to_send}")


"""
doesnt start start the process, only the protocol
name="Start Weigh",
cmd="-h",
cmdType="STARTWEIGH",

name="Start Count",
cmd="-i",
cmdType="STARTCOUNT",


name="Finish",
cmd="-j",
cmdType="FINISH",


name="Weigh",
cmd="-f",
cmdType="WEIGH",

name="Re-Weigh",
cmd="-f",
cmdType="REWEIGH",


name="Reset",
cmd="-l",
cmdType="RESET",



name="Log Item",
cmd="-m",
cmdType="LOGITEM",


name="Count",
cmd="-g",
cmdType="COUNT",


name="Re-Count",
cmd="-g",
cmdType="RECOUNT",


name="Calibrate",
cmd="-d",
cmdType="CALIBRATE",

name="Tare",
cmd="-e",
cmdType="TARE",

name="Open Viewer",
cmd="-o",
cmdType="OPENVIEWER",

name="Close Viewer",
cmd="-v",
cmdType="CLOSEVIEWER",


name="Disconnected",
cmd="-k",
cmdType="CONNECT",

name="Connected",
cmd="-k",
cmdType="DISCONNECT",



"""
