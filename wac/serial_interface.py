from PyQt5 import QtSerialPort
from PyQt5.QtCore import QTime, pyqtSignal, pyqtSlot, QTimer

from wac.command_button import Command


"""
ctrl + m for enter on putty
ctrl + j 
"""
DELAY = 1
COM_PORT = "COM5"
BAUD_RATE = 9600


class SerialInterface(QtSerialPort.QSerialPort):

    finished = pyqtSignal()  # when the object is killed
    serial_send = pyqtSignal(str)  # serial data that is sent
    serial_receive = pyqtSignal(str)  # serial data that is received

    serial_status = pyqtSignal(bool)  # serial serial_status : Connected | Disconnected
    serial_cmd_response = pyqtSignal(object)
    serial_terminate = pyqtSignal(bool)

    # control signals
    serial_connected = pyqtSignal()
    serial_disconnected = pyqtSignal()

    serial_process = pyqtSignal()
    serial_protocol = pyqtSignal()

    live_data = pyqtSignal(str)

    prompt = pyqtSignal(str, str)

    autoconnect_success = pyqtSignal()
    autoconnect_fail = pyqtSignal()
    autoconnect = pyqtSignal(bool)

    def __init__(self, commandDict: dict = {}, parent=None):
        super(SerialInterface, self).__init__(parent)
        self.port_name = COM_PORT
        self.baud_rate = 9600
        self.running = False
        self.isLiveWeight = False
        self.commandDict = commandDict

        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.SerialStatus()
        self.readyRead.connect(self.Receive)

    # receive config info
    @pyqtSlot(str, int)
    def SerialConfig(self, port_name: str, baud_rate: int):
        self.baud_rate = baud_rate
        self.port_name = port_name

    @pyqtSlot(str)
    def AutoConnect(self, port_name):
        self.port_name = port_name
        self.setPortName(port_name)
        if self.running:
            self.SerialStatus()

        else:
            self.running = self.open(self.ReadWrite)

        self.autoconnect.emit(self.running)

    # this connect method should be ssubscribed to the emitting of the combobox for
    @pyqtSlot(object)
    def Connect(self, cmd):
        # set port name and baud rate
        self.setPortName(self.port_name)
        self.setBaudRate(self.baud_rate)
        # check if the serial is already connected
        if self.running:
            self.SerialStatus()

        else:
            # if not , connect  and start the timer
            self.running = self.open(self.ReadWrite)

        if self.running:
            self.serial_cmd_response.emit(cmd)
            self.serial_connected.emit()

        if not self.running:
            self.serial_disconnected.emit()
        self.SerialStatus()

    # [Slot] Disconnect the serial connection
    @pyqtSlot(object)
    def Disconnect(self, cmd):

        if self.running:
            self.close()
            self.timer.stop()
            self.running = False

        self.serial_cmd_response.emit(cmd)
        self.serial_disconnected.emit()
        self.SerialStatus()

    # [Slot] Terminate the Serial Connection and the associated thread
    @pyqtSlot()
    def Terminate(self):
        self.running = True if self.isOpen() else False

        if self.running:
            self.close()

        if self.timer.isActive():
            self.timer.stop()

        print("Terminating Thread")
        self.serial_terminate.emit(True)
        self.finished.emit()

    """
    [Slot] Receive serial input 
    """

    def Receive(self):
        """
        when using readLine, reads a line of ascii characters up to a max size,
        the characters are stored in 'data', it also returns the number of bytes read
        a terminating '\\0' is always added. a newline characters is also added
        """
        while self.canReadLine():
            print("receiving")
            raw_input = self.readLine().data().decode()

            self.serial_receive.emit(raw_input)
            self.live_data.emit(raw_input)

            print(list(raw_input))
            if self.currentCmd:
                if "-" in raw_input:
                    start = raw_input.index("-")
                    command = "".join(raw_input[start : start + 2])
                    if self.currentCmd.cmd == command:
                        self.serial_cmd_response.emit(self.currentCmd)
                        self.currentCmd = None

                elif "#" in raw_input:
                    start, end = raw_input.index("#"), raw_input.index("&")
                    val = int(raw_input[start + 1 : end])
                    self.currentCmd.returnValue = val
                    self.serial_cmd_response.emit(self.currentCmd)
                    self.currentCmd = None

    def ReceiveLiveWeight(self):
        while self.canReadLine():
            raw_input = self.readLine().data().decode()
            self.serial_receive.emit(raw_input)
            self.live_data.emit(raw_input)
            print(list(raw_input))

    @pyqtSlot(str)
    def Send(self, msg):

        if self.running:
            self.write(msg.encode())
            self.serial_send.emit(msg)

        self.waitForBytesWritten(1000)

    # [Slot] Send a command, wait for the response
    @pyqtSlot(object)
    def RunCommand(self, cmd):
        command = f"{cmd.cmd}\r"
        self.currentCmd = cmd
        if self.running:
            self.write(command.encode())

    # emit the current serial status
    def SerialStatus(self):
        self.serial_status.emit(self.running)

        # Workers run method

    def run(self):
        self.SerialStatus()
