"""
RealTimeSender
This package contains the RealTimeSender class used for simulating and testing the serial connection
"""
import sys
import numpy as np
from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSlot, QTimer, QIODevice
from PyQt5.QtWidgets import (
    QLCDNumber,
    QApplication,
    QWidget,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDial,
    QFrame
)

from theme import ApplicationTheme


""" RangeFinder Class
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


class RealTimeSender(QWidget):
    """The constructor."""

    def __init__(self, parent=None):
        super(RealTimeSender, self).__init__(parent)

        """
        Text and Line Edits
        """
        self.lineedit_message = QLineEdit()
        self.lineedit_message.setFixedSize(200, 50)

        self.textedit_output = QTextEdit(readOnly=True)
        # self.textedit_output.setFixedWidth(500)

        """ Timers (ms) """
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)

        """ Buttons """
        self.button_send = QPushButton(text="Send to Board", clicked=self.send)
        self.button_send.setFixedSize(200, 50)

        self.button_connect = QPushButton(
            text="Connect", checkable=True, toggled=self.on_toggled
        )
        self.button_connect.setStyleSheet("background-color: red")
        self.button_connect.setFixedSize(200, 50)

       
        self.button_start_weigh = QPushButton(text="Start Weigh [Response]", clicked=self.button_start_weigh_clicked)
        self.button_start_weigh.setFixedSize(200, 50)
        
        self.button_weigh = QPushButton(text="Weigh/Re-Weigh [Response]", clicked=self.button_weigh_clicked)
        self.button_weigh.setFixedSize(200, 50)
        
        self.button_count = QPushButton(text="Count/Re-count [Response]", clicked=self.button_count_clicked)
        self.button_count.setFixedSize(200, 50)
                
        self.button_start_count = QPushButton(text="Start Count [Response]", clicked=self.button_start_count_clicked)
        self.button_start_count.setFixedSize(200, 50)
        
        self.button_finish = QPushButton(text="Finish/Reset [Response]", clicked=self.button_finish_clicked)
        self.button_finish.setFixedSize(200, 50)
        
        self.button_calibrate = QPushButton(text="Calibrate [Response]", clicked=self.button_calibrate_clicked)
        self.button_calibrate.setFixedSize(200, 50)

        self.button_tare = QPushButton(text="Tare [Response]", clicked=self.button_tare_clicked)
        self.button_tare.setFixedSize(200, 50)
        
        
        self.button_startup = QPushButton(text="Startup [Response]", clicked=self.button_startup_clicked)
        self.button_startup.setFixedSize(200, 50)
        
        """
        Dial
        """
        self.dial_weight = QDial()
        # self.dial_weight.notchSize = 
        self.dial_weight.setNotchesVisible(True)
        self.dial_weight.setWrapping(False)
        self.dial_weight.setMinimum(0)
        self.dial_weight.setMaximum(1000)
        self.dial_weight.setFixedSize(200, 200)
        
        self.label_dial__weight = LCDWidgetHelper("dial_weight", False, 200, 50)
        self.dial_weight.valueChanged.connect(
            self.label_dial__weight.display
        )

        """ Layout """
        VBox = QVBoxLayout(self)

        vbox_layout_one = GenericLayoutHelper(
            QVBoxLayout(),
            [
                self.label_dial__weight,
                self.dial_weight,
                self.lineedit_message,
                self.button_send,
                self.button_connect,
            ],
        )
        vbox_layout_two = GenericLayoutHelper(
            QVBoxLayout(),
            [
                self.button_calibrate,
                self.button_tare,
                self.button_weigh,
                self.button_count,
                self.button_start_weigh,
                self.button_start_count,
                self.button_finish,
                self.button_startup
            ],
        )

        vbox_layout_three = GenericLayoutHelper(
            QVBoxLayout(),
            [
                self.textedit_output
            ],
        )

        hbox_layout_one = QHBoxLayout()
        hbox_layout_one.addLayout(vbox_layout_one)
        hbox_layout_one.addLayout(vbox_layout_two)
        hbox_layout_one.addLayout(vbox_layout_three)
        VBox.addLayout(hbox_layout_one)
        self.setWindowTitle("WAC Testing Module")

        """ commands """
        self.command_d = "d"
        self.command_h = "h"

        self.plotbank = []

        """ Serial Connection configuration """
        self.serial = QtSerialPort.QSerialPort(
            "COM6",
            baudRate=QtSerialPort.QSerialPort.Baud9600,
            readyRead=self.receive,
        )
        self.rng = np.random.default_rng(12345)
        self.serial.open(self.serial.ReadWrite)

    """ Method to read from serial, convert the data and send it to be plotted  """
    #  @param self The object pointer
    @pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            raw_input_data = self.serial.readLine().data().decode()
            self.textedit_output.append(f"[Received] {raw_input_data}")
            print(f"[Received] {raw_input_data}")

    """ Method to send commands via serial
    #  @param self The object pointer"""

    @pyqtSlot()
    def send(self):
        # command = f'[Sent] {self.lineedit_message.text()}\r'
        """
         #%d&
        # """
        
        for i in range(1000):
            weight_from_dial = self.dial_weight.value()
            weight_low = weight_from_dial - 5
            weight_high = weight_from_dial + 5
            
            weight = self.rng.integers(low=weight_low, high=weight_high)
            command = f"{weight}\r\n"
            self.serial.write(command.encode())
            #self.textedit_output.append(f"[Sent {i}] {command.encode()}")

    """ Method to create a serial connection with the board
    #  @param self The object pointer"""

    @pyqtSlot(bool)
    def on_toggled(self, checked):
        self.textedit_output.append(f"{'Connected' if checked else 'Disconnected'}")

        self.button_connect.setText("Disconnect" if checked else "Connect")
        self.button_connect.setStyleSheet(
            "background-color: green" if checked else "background-color: red"
        )
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QIODevice.ReadWrite):
                    self.button_connect.setChecked(False)
        else:
            self.serial.close()


    def button_calibrate_clicked(self):
        self.send_command('-d')

    def button_tare_clicked(self):
        self.send_command('-e')

    def button_weigh_clicked(self):
        self.send_command('-f')

    def button_count_clicked(self):
        self.send_command('-g')

    def button_start_weigh_clicked(self):
        self.send_command('-h')

    def button_start_count_clicked(self):
        self.send_command('-i')

    def button_finish_clicked(self):
        self.send_command('-j')

    def button_startup_clicked(self):
        self.send_command('-k')
        
    def send_command(self, command):
        to_send = f"{command}\r\n"
        self.serial.write(to_send.encode())
        self.textedit_output.append(f"[Sent] {to_send.encode()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(ApplicationTheme())
    w = RealTimeSender()

    """ 
    Initialise the Sliders 
    """

    w.show()
    sys.exit(app.exec_())
