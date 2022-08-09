from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QGridLayout, QGroupBox
from PyQt5.QtCore import QObject, QStateMachine, pyqtSignal, pyqtSlot, QThread, QState

from wac.command_button import (
    Command,
    MultiCommandButton,
    CalibrationCommands,
    CommandButton,
)
from wac.router import Router

PADDING = 10
SPACING = 10
MARGIN = 10

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Request(Router):
    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.route = {
            "CALIBRATE": self.Calibrate,
            "TARE": self.Tare,
        }

    def Calibrate(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def Tare(self, cmd: Command) -> None:
        self.command.emit(cmd)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Response(Router):
    # trigger the next state
    calibration_complete = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        self.route = {
            "CALIBRATE": self.Calibrate,
            "TARE": self.Tare,
        }

    def Calibrate(self, cmd: Command) -> None:
        self.calibration_complete.emit()

    def Tare(self, cmd: Command) -> None:
        self.calibration_complete.emit()


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class CalibrationWidget(QWidget):

    """The constructor."""

    def __init__(self, parent=None):
        super(CalibrationWidget, self).__init__(parent)
        self.request = Request(parent=self)
        self.response = Response(parent=self)
        self.setupUi()
        self.setupStates()
        self.machine.start()

    def setupUi(self):
        self.setObjectName("CalibrationWidget")
        # generate the commands
        cmdList = self.ConnectButtons(CalibrationCommands(parent=self))
        cmd_calibrate, cmd_tare = cmdList[0], cmdList[1]

        self.Calibration_Button = CommandButton(cmd=cmd_calibrate)
        self.Tare_Button = CommandButton(cmd=cmd_tare)

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        self.vbox.setSpacing(PADDING)
        self.vbox.addWidget(self.Calibration_Button)
        self.vbox.addWidget(self.Tare_Button)

        self.GBox_Calibration = QGroupBox(self, title="Calibration")
        self.GBox_Calibration.setLayout(self.vbox)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(PADDING)
        self.gridLayout.addWidget(self.GBox_Calibration, 0, 0, 1, 1)
        self.setLayout(self.gridLayout)

    """
    Connect the button signals to the Processor handling all the Requests and Responses
    use a list to iterate over a list of commands
    """

    def ConnectButtons(self, cmd_list: list = None):
        for cmd in cmd_list:
            cmd.cmd_signal.connect(self.request.process)
        return cmd_list

    # setup states
    def setupStates(self):
        self.state_start = QState()
        self.state_calibrate = QState()
        self.state_tare = QState()

        self.state_start.addTransition(
            self.Calibration_Button.clicked, self.state_calibrate
        )
        self.state_start.addTransition(self.Tare_Button.clicked, self.state_tare)

        self.state_calibrate.addTransition(
            self.response.calibration_complete, self.state_start
        )
        self.state_tare.addTransition(
            self.response.calibration_complete, self.state_start
        )

        self.state_start.entered.connect(self.EntryStart)
        self.state_calibrate.entered.connect(self.EntryCalibrate)
        self.state_tare.entered.connect(self.EntryTare)

        self.machine = QStateMachine()
        self.machine.addState(self.state_start)
        self.machine.addState(self.state_calibrate)
        self.machine.addState(self.state_tare)
        self.machine.setInitialState(self.state_start)

    @pyqtSlot()
    def EntryStart(self):
        self.Calibration_Button.setEnabled(True)
        self.Tare_Button.setEnabled(True)
        self.Calibration_Button.ConfigureButton()
        self.Tare_Button.ConfigureButton()

    @pyqtSlot()
    def EntryCalibrate(self):
        self.Calibration_Button.setText("Calibrating...")
        self.Calibration_Button.setEnabled(False)
        self.Tare_Button.setEnabled(False)

    @pyqtSlot()
    def EntryTare(self):
        self.Tare_Button.setText("Taring...")
        self.Tare_Button.setEnabled(False)
        self.Calibration_Button.setEnabled(False)
