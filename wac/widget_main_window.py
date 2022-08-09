from PyQt5 import QtWidgets, QtSerialPort
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QLabel,
    QProgressBar,
    QStyle,
    QWidget,
    QVBoxLayout,
    QApplication,
    QGridLayout,
    QStatusBar,
    QTextEdit,
    QMessageBox,
    QLCDNumber,
    QGroupBox,
)
from PyQt5.QtCore import (
    QObject,
    QStateMachine,
    QTimer,
    pyqtSignal,
    pyqtSlot,
    QThread,
    QState,
    Qt,
)


from wac.widget_calibration import CalibrationWidget
from wac.command_button import Command
from wac.widget_prompt import PromptWidget
from wac.widget_serialconnection import SerialConnectionWidget
from wac.serial_interface import SerialInterface
from wac.widget_weighandcount import WeighAndCountWidget


QSSLED = """
QLCDNumber {
    background-color: none;
    color: red;
    font-szie: 24px;    
    border: none;  
}
"""

QSSLEDLABEL = """
QLCDNumber {
    background-color: none;
    color: red;
    font-szie: 36px;    
    border: none;  
}
"""

QSSLEDGBOX = """
QLabel {
    background-color: black;
    border-radius: 2px;
    padding: 10px;
    color: red;
}
"""
ROW = 1
COL = 1


HEIGHT = 1
WIDTH = 1
SPACING = 10
MARGIN = 10


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Request(QObject):
    # output the chosen command to serial output
    command = pyqtSignal(object)
    reset_progresscounter = pyqtSignal()

    # serial connection signal
    terminate_serial = pyqtSignal()

    # to output to the prompt widget
    prompt = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)

    @pyqtSlot(object)
    def Process(self, cmd: Command, route: dict = {}):
        self.reset_progresscounter.emit()
        route = {
            "CONNECT": self.Connect,
            "DISCONNECT": self.Disconnect,
            "CALIBRATE": self.Calibrate,
            "TARE": self.Tare,
            "COUNT": self.Count,
            "RECOUNT": self.Recount,
            "WEIGH": self.Weigh,
            "REWEIGH": self.Reweigh,
            "STARTWEIGH": self.StartWeigh,
            "STARTCOUNT": self.StartCount,
            "FINISH": self.Finish,
            "RESET": self.Reset,
            "LOGITEM": self.LogItem,
        }
        fn = route[cmd.cmdType]
        fn(cmd)

    def Connect(self, cmd: Command) -> None:
        # self.serial_connection.emit(cmd)
        pass

    def Disconnect(self, cmd: Command) -> None:
        # self.serial_connection.emit(cmd)
        pass

    def Calibrate(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def Tare(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptStatus)
        self.command.emit(cmd)

    def Count(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptStatus)
        self.command.emit(cmd)

    def Recount(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptStatus)
        self.command.emit(cmd)

    def Weigh(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptStatus)
        self.command.emit(cmd)

    def Reweigh(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptStatus)
        self.command.emit(cmd)

    def StartWeigh(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptHowTo)
        self.command.emit(cmd)

    def StartCount(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptHowTo)
        self.command.emit(cmd)

    def Finish(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptHowTo)
        self.command.emit(cmd)

    def Reset(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptStatus)
        self.command.emit(cmd)

    def LogItem(self, cmd: Command) -> None:
        self.command.emit(cmd)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Response(QObject):
    # trigger the next state
    command = pyqtSignal(object)

    calibration = pyqtSignal(object)
    weigh_and_count = pyqtSignal(object)
    serial_connection = pyqtSignal(object)
    return_home = pyqtSignal()
    prompt = pyqtSignal(str)

    calibration_complete = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)

    """
    Processes that occur after a response is received fromt he PIC18
    """

    @pyqtSlot(object)
    def Process(self, cmd: Command, route: dict = {}):
        print("[serial] receive response")
        route = {
            "CONNECT": self.Connect,
            "DISCONNECT": self.Disconnect,
            "CALIBRATE": self.Calibrate,
            "TARE": self.Tare,
            "COUNT": self.Count,
            "RECOUNT": self.Recount,
            "WEIGH": self.Weigh,
            "REWEIGH": self.Reweigh,
            "STARTWEIGH": self.StartWeigh,
            "STARTCOUNT": self.StartCount,
            "FINISH": self.Finish,
            "RESET": self.Reset,
            "LOGITEM": self.LogItem,
        }
        fn = route[cmd.cmdType]
        fn(cmd)

    def Connect(self, cmd: Command) -> None:
        self.prompt.emit("Connected")

    def Disconnect(self, cmd: Command) -> None:
        self.prompt.emit("Disconnected")

    def Calibrate(self, cmd: Command) -> None:
        self.prompt.emit("Calibration Complete")

        self.calibration_complete.emit()
        self.calibration.emit(cmd)

    def Tare(self, cmd: Command) -> None:
        self.prompt.emit("Tare Complete")

        self.calibration_complete.emit()
        self.calibration.emit(cmd)

    def Weigh(self, cmd: Command) -> None:
        text = f"Item weighs {cmd.returnValue} grams.\n\n{cmd.promptProceed}"
        self.prompt.emit(text)
        self.weigh_and_count.emit(cmd)

    def Reweigh(self, cmd: Command) -> None:
        text = f"Item weighs {cmd.returnValue} grams.\n\n{cmd.promptProceed}"
        self.prompt.emit(text)
        self.weigh_and_count.emit(cmd)

    def Count(self, cmd: Command) -> None:
        text = (
            f"There are {cmd.returnValue} items, in the basket.\n\n{cmd.promptProceed}"
        )
        self.prompt.emit(text)
        self.weigh_and_count.emit(cmd)

    def Recount(self, cmd: Command) -> None:
        text = (
            f"There are {cmd.returnValue} items, in the basket.\n\n{cmd.promptProceed}"
        )
        self.prompt.emit(text)
        self.weigh_and_count.emit(cmd)

    def StartWeigh(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptHowTo)
        self.weigh_and_count.emit(cmd)

    def StartCount(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptHowTo)
        self.weigh_and_count.emit(cmd)

    def Finish(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptStatus)
        self.weigh_and_count.emit(cmd)

    def Reset(self, cmd: Command) -> None:
        text = "Scales Reset!"
        self.prompt.emit(text)
        self.weigh_and_count.emit(cmd)

    def LogItem(self, cmd: Command) -> None:
        self.prompt.emit(cmd.promptStatus)
        self.weigh_and_count.emit(cmd)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

QSS_STATUSBAR = """
QStatusBar {
    background: black;
    border-radius: 2px;
    padding: 10px;
    color: red;
}
"""


class MainWindow(QWidget):

    process_serial_response = pyqtSignal(object)
    led_display_raw = pyqtSignal(int)
    dataviewer_liveupdate = pyqtSignal(int)

    autoconnect = pyqtSignal(str)
    autoconnect_success = pyqtSignal()
    autoconnect_fail = pyqtSignal()

    """ The constructor."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.is_connected = False
        self.request = Request()
        self.response = Response()

        self.prompt = PromptWidget(parent=self)
        self.prompt.setMinimumWidth(300)
        self.calibration = CalibrationWidget(parent=self)
        self.weigh_and_count = WeighAndCountWidget(parent=self)
        self.serial_connection = SerialConnectionWidget(parent=self)
        self.setupUi()
        self.List_Of_Commands = self.findChildren(Command)
        self.CmdPromptDict = {_.cmdType: _.promptHowTo for _ in self.List_Of_Commands}
        self.CmdCommandDict = {_.cmd: _ for _ in self.List_Of_Commands}
        self.currentState = "DISCONNECTED"

        self.progressCounter = 0

        self.runSerialConnection()
        self.runConnections()
        self.setupStates()

        self.HomePrompt()
        text = "To begin using the sclaes, ensure it is plugged in, then press connect"
        self.request.prompt.emit(text)
        self.machine.start()

    def setupUi(self):
        self.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        self.setWindowTitle("Weigh and Counter 3000")

        uiFont = QFont("Segoe UI")
        uiFont.setPointSize(14)
        self.setFont(uiFont)

        lcdFont = QFont("Consolas")
        lcdFont.setPointSize(60)

        self.lcdoutput = QLabel(self, text=f"{0:03d} g")
        self.lcdoutput.setStyleSheet(QSSLEDLABEL)
        self.lcdoutput.setFont(lcdFont)
        self.lcdoutput.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.GBox_Led = QtWidgets.QGroupBox(self)
        self.GBox_Led.setContentsMargins(10, 10, 10, 10)
        self.GBox_Led.setTitle("Weight")
        self.GBox_Led.setStyleSheet(QSSLEDGBOX)

        self.Vbox_Led = QtWidgets.QVBoxLayout(self)
        self.Vbox_Led.setContentsMargins(10, 10, 10, 10)
        self.Vbox_Led.setSpacing(10)
        self.Vbox_Led.addWidget(self.lcdoutput)
        self.GBox_Led.setLayout(self.Vbox_Led)

        self.progressbar = QProgressBar(self)
        self.progressbar.setTextVisible(False)
        self.progressbar.setMaximum(1900)
        self.progressbar.setMinimum(0)

        self.GBox_ProgressBar = QtWidgets.QGroupBox(self)
        self.GBox_ProgressBar.setContentsMargins(10, 10, 10, 10)
        self.GBox_ProgressBar.setTitle("Progress")
        self.Vbox_ProgressBar = QtWidgets.QVBoxLayout(self)
        self.Vbox_ProgressBar.setContentsMargins(10, 10, 10, 10)
        self.Vbox_ProgressBar.setSpacing(10)
        self.Vbox_ProgressBar.addWidget(self.progressbar)
        self.GBox_ProgressBar.setLayout(self.Vbox_ProgressBar)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        self.gridLayout.setSpacing(SPACING)

        # row, column, rowSpan, columnSpan
        self.gridLayout.addWidget(
            self.GBox_Led, 0 * ROW, 0 * COL, 1 * HEIGHT, 2 * WIDTH
        )
        self.gridLayout.addWidget(self.prompt, 1 * ROW, 0 * COL, 3 * HEIGHT, 1 * WIDTH)
        self.gridLayout.addWidget(
            self.serial_connection, 1 * ROW, 1 * COL, 1 * HEIGHT, 1 * WIDTH
        )
        self.gridLayout.addWidget(
            self.weigh_and_count, 2 * ROW, 1 * COL, 1 * HEIGHT, 1 * WIDTH
        )
        self.gridLayout.addWidget(
            self.calibration, 3 * ROW, 1 * COL, 1 * HEIGHT, 1 * WIDTH
        )
        self.gridLayout.addWidget(
            self.GBox_ProgressBar, 4 * ROW, 0 * COL, 1 * HEIGHT, 2 * WIDTH
        )
        self.setLayout(self.gridLayout)

    # function to establish a serial connection on a separate thread
    def runSerialConnection(self):
        self.thread = QThread()
        self.worker = SerialInterface(commandDict=self.CmdCommandDict)
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

        # for sending and receiving this is required
        ## Mainwindow ---> Worker
        self.request.command.connect(self.worker.RunCommand)
        ## Worker ---> Mainwindow
        self.worker.serial_cmd_response.connect(self.response.Process)

    def runConnections(self):
        # Calibration <---> MainWindow
        self.calibration.request.command.connect(self.request.Process)
        self.response.calibration.connect(self.calibration.response.Process)

        # WeighAndCount <---> MainWindow
        self.weigh_and_count.request.command.connect(self.request.Process)
        self.response.weigh_and_count.connect(self.weigh_and_count.response.Process)

        # SerialConnection <---> MainWindow
        self.serial_connection.request.command.connect(self.request.Process)
        self.response.serial_connection.connect(self.serial_connection.response.Process)

        # SerialConnection <---> Worker
        self.serial_connection.request.connect.connect(self.worker.Connect)
        self.serial_connection.request.disconnect.connect(self.worker.Disconnect)

        self.worker.serial_disconnected.connect(
            self.serial_connection.response.disconnected
        )
        self.worker.serial_connected.connect(self.serial_connection.response.connected)

        # worker <---> SerialDataViewer
        # self.worker.serial_send.connect(self.prompt.serial_data_viewer.ViewDataSent)
        self.worker.serial_receive.connect(
            self.prompt.serial_data_viewer.ViewDataReceived
        )
        self.worker.serial_status.connect(
            self.prompt.serial_data_viewer.ViewSerialStatus
        )

        # MainWindow ---> Worker
        self.request.terminate_serial.connect(self.worker.Terminate)

        # Mainwindow ---> Prompt
        self.request.prompt.connect(self.prompt.TextEdit_Prompt.setText)
        self.response.prompt.connect(self.prompt.TextEdit_Prompt.setText)

        self.serial_connection.request.prompt.connect(
            self.prompt.TextEdit_Prompt.setText
        )
        self.worker.live_data.connect(self.LCDLiveData)

        self.request.reset_progresscounter.connect(self.ResetProgressBar)
        self.dataviewer_liveupdate.connect(
            self.prompt.serial_data_viewer.live_plot_update
        )

        self.autoconnect.connect(self.worker.AutoConnect)
        self.worker.autoconnect.connect(self.AutoConnectResult)

        self.autoconnect_success.connect(self.serial_connection.response.autoconnected)

    # setup states
    def setupStates(self):
        self.state_disconnected = QState()
        self.state_home = QState()
        self.state_calibration = QState()
        self.state_weighandcount = QState()

        # disconnected
        self.state_disconnected.addTransition(
            self.serial_connection.response.connected, self.state_home
        )
        self.state_disconnected.addTransition(self.autoconnect_success, self.state_home)

        # home --->
        # home ---> calibration
        self.state_home.addTransition(
            self.calibration.Tare_Button.clicked, self.state_calibration
        )
        self.state_home.addTransition(
            self.calibration.Calibration_Button.clicked, self.state_calibration
        )
        # home ---> weigh and count
        self.state_home.addTransition(
            self.weigh_and_count.response.initiated, self.state_weighandcount
        )
        # home ---> disconnected
        self.state_home.addTransition(
            self.serial_connection.response.disconnected, self.state_disconnected
        )

        # calibration ---> home
        self.state_calibration.addTransition(
            self.calibration.response.calibration_complete, self.state_home
        )
        self.state_calibration.addTransition(
            self.serial_connection.response.disconnected, self.state_disconnected
        )

        # weigh and count ---> home
        self.state_weighandcount.addTransition(
            self.weigh_and_count.response.weigh_and_count_finished, self.state_home
        )
        self.state_weighandcount.addTransition(
            self.serial_connection.response.disconnected, self.state_disconnected
        )
        self.state_weighandcount.addTransition(
            self.weigh_and_count.response.reset_state, self.state_home
        )

        self.state_disconnected.entered.connect(self.EntryDisconnected)
        self.state_home.entered.connect(self.EntryHome)
        self.state_calibration.entered.connect(self.EntryCalibration)
        self.state_weighandcount.entered.connect(self.EntryWeighAndCount)

        self.machine = QStateMachine()
        self.machine.addState(self.state_disconnected)
        self.machine.addState(self.state_home)
        self.machine.addState(self.state_calibration)
        self.machine.addState(self.state_weighandcount)
        self.machine.setInitialState(self.state_disconnected)

    def HomePrompt(self):
        cmds, text = ["STARTWEIGH", "CALIBRATE", "TARE"], ""
        for _, cmd in enumerate(cmds):
            text = text + f"{_+1}) {self.CmdPromptDict[cmd]}\n\n"
        self.CmdPromptDict.update({"HOMEPROMPT": text})

    def EntryDisconnected(self):
        self.serial_connection.setDisabled(False)
        self.weigh_and_count.setDisabled(True)
        self.calibration.setDisabled(True)
        self.AutoConnect()

    def EntryHome(self):
        print("State: Home")
        # self.autoConnectTimer.stop()
        self.request.prompt.emit(self.CmdPromptDict["HOMEPROMPT"])
        self.prompt.TextEdit_Prompt.setText(self.CmdPromptDict["HOMEPROMPT"])
        self.serial_connection.setDisabled(True)
        self.weigh_and_count.setDisabled(False)
        self.calibration.setDisabled(False)
        self.ResetButtonEvent()

    def EntryCalibration(self):
        print("State: Calibration")
        self.serial_connection.setDisabled(True)
        self.weigh_and_count.setDisabled(True)
        self.calibration.setDisabled(True)

    def EntryWeighAndCount(self):
        print("State: Weigh and count")
        self.serial_connection.setDisabled(True)
        self.weigh_and_count.setDisabled(False)
        self.calibration.setDisabled(True)

    # override close event slot to ensure proper serial
    # termination and thread termination
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Window Close",
            "Are you sure you want to close the window?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:

            self.request.terminate_serial.emit()
            # if self.autoConnectTimer.isActive:
            #    self.autoConnectTimer.stop()

            try:
                if self.prompt.serial_data_viewer.isVisible():
                    self.prompt.serial_data_viewer.close()
            except RuntimeError:
                pass

            event.accept()
            print("Window closed")
        else:
            event.ignore()

    @pyqtSlot(str)
    def SerialParser(self, serIn):
        if "-" in serIn:
            start = serIn.index("-")
            command = "".join(serIn[start : start + 2])
            print(command)
            commandx = self.CmdCommandDict[command]
            self.process_serial_response.emit(commandx)

    @pyqtSlot(str)
    def LCDLiveData(self, serIn):
        try:
            rawint = int(serIn)
            if rawint > 950:
                self.lcdoutput.setText("ERROR!")
                self.prompt.TextEdit_Prompt.setText(
                    "ERROR: Too heavy! Maximum Wieght Reached!"
                )
            else:
                self.lcdoutput.setText(f"{rawint:03d} g")
                self.progressCounter += 1
                self.progressbar.setValue(self.progressCounter)
                self.dataviewer_liveupdate.emit(rawint)
                # self.lcdoutput.display(f'{rawint}g')
        except ValueError:
            pass

    def ResetProgressBar(self):
        self.progressbar.reset()
        self.progressCounter = 0

    @pyqtSlot()
    def ResetButtonEvent(self):
        self.lcdoutput.setText(f"{0:03d} g")
        self.ResetProgressBar()

    def AutoConnect(self):

        text = "Auto Connecting to Weighing Scales, please wait"

        self.request.prompt.emit(text)

        # while not self.is_connected:
        avbPorts = QtSerialPort.QSerialPortInfo.availablePorts()

        for p in avbPorts:
            if f"{p.manufacturer()}" == "Prolific":
                self.autoconnect.emit(f"{p.portName()}")
            else:
                text = "Wieghing Scale Not Detected! Please ensure the device is connected properly and has sufficient power."
                self.request.prompt.emit(text)

    @pyqtSlot(bool)
    def AutoConnectResult(self, result: bool):
        if result:
            self.is_connected = True
            self.autoconnect_success.emit()
        else:
            self.autoconnect_fail.emit()
            self.is_connected = False


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
