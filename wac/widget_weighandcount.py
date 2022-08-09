from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QGroupBox
from PyQt5.QtCore import QStateMachine, pyqtSignal, pyqtSlot, QState

from wac.command_button import (
    Command,
    CommandButton,
    MultiCommandButton,
    ProtocolCommands,
    WeighCommands,
    CountCommands,
    ResetAndLogCommands,
)
from wac.router import Router

PADDING = 10
SPACING = 10
MARGIN = 10


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Request(Router):
    # output the chosen command to serial output
    command = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.setObjectName("WeighAndCount_Request")
        self.route = {
            "STARTWEIGH": self.StartWeigh,
            "STARTCOUNT": self.StartCount,
            "FINISH": self.Finish,
            "WEIGH": self.Weigh,
            "REWEIGH": self.ReWeigh,
            "COUNT": self.Count,
            "RECOUNT": self.ReCount,
            "RESET": self.Reset,
            "LOGITEM": self.LogItem,
        }

    def StartWeigh(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def StartCount(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def Finish(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def Weigh(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def ReWeigh(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def Count(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def ReCount(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def Reset(self, cmd: Command) -> None:
        self.command.emit(cmd)

    def LogItem(self, cmd: Command) -> None:
        self.command.emit(cmd)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Response(Router):
    # trigger the next state
    next_state = pyqtSignal()
    weigh_and_count_finished = pyqtSignal()
    initiated = pyqtSignal()
    reset_state = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        self.setObjectName("WeighAndCount_Response")

        self.route = {
            "STARTWEIGH": self.StartWeigh,
            "STARTCOUNT": self.StartCount,
            "FINISH": self.Finish,
            "WEIGH": self.Weigh,
            "REWEIGH": self.ReWeigh,
            "COUNT": self.Count,
            "RECOUNT": self.ReCount,
            "RESET": self.Reset,
            "LOGITEM": self.LogItem,
        }

    def StartWeigh(self, cmd: Command) -> None:
        self.next_state.emit()

    def StartCount(self, cmd: Command) -> None:
        self.next_state.emit()

    def Finish(self, cmd: Command) -> None:
        self.next_state.emit()
        self.weigh_and_count_finished.emit()

    def Weigh(self, cmd: Command) -> None:
        self.next_state.emit()

    def ReWeigh(self, cmd: Command) -> None:
        cmd.EnableButton()

    def Count(self, cmd: Command) -> None:
        self.next_state.emit()

    def ReCount(self, cmd: Command) -> None:
        cmd.EnableButton()

    def Reset(self, cmd: Command) -> None:
        self.reset_state.emit()

    def LogItem(self, cmd: Command) -> None:
        pass


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class WeighAndCountWidget(QWidget):

    """The constructor."""

    def __init__(self, parent=None):
        super(WeighAndCountWidget, self).__init__(parent)

        self.request = Request(parent=parent)
        self.response = Response(parent=parent)

        self.setupUi()
        self.response.reset_state.connect(self.ResetStateSignal)
        self.setupStates()
        self.machine.start()

    def setupUi(self):
        # generate the commands
        cmdList = self.ConnectButtons(ProtocolCommands(parent=self))
        self.Protocol_Button = MultiCommandButton(
            cmd=cmdList[0], cmdList=cmdList, parent=self
        )

        # generate the commands
        cmdList = self.ConnectButtons(WeighCommands(parent=self))
        self.Weigh_Button = MultiCommandButton(
            cmd=cmdList[0], cmdList=cmdList, parent=self
        )

        # generate the commands
        cmdList = self.ConnectButtons(CountCommands(parent=self))
        self.Count_Button = MultiCommandButton(
            cmd=cmdList[0], cmdList=cmdList, parent=self
        )

        # generate the commands
        cmdList = self.ConnectButtons(ResetAndLogCommands(parent=self))
        cmd_reset, cmd_log = cmdList[0], cmdList[1]

        self.Reset_Button = CommandButton(cmd=cmd_reset)
        self.Reset_Button.ConfigureButton()

        self.Log_Button = CommandButton(cmd=cmd_log)
        self.Log_Button.ConfigureButton()

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        self.vbox.setSpacing(PADDING)

        [self.vbox.addWidget(btn) for btn in self.findChildren(MultiCommandButton)]
        self.vbox.addWidget(self.Log_Button)
        self.vbox.addWidget(self.Reset_Button)

        self.GBox_WeighAndCount = QGroupBox(self, title="Weigh and Count")
        self.GBox_WeighAndCount.setLayout(self.vbox)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(PADDING)
        self.gridLayout.addWidget(self.GBox_WeighAndCount, 0, 0, 1, 1)
        self.setLayout(self.gridLayout)

        self.setObjectName("WeighAndCountWidget")

    """
    Connect the button signals to the Processor handling all the Requests and Responses
    use a list to iterate over a list of commands
    """

    def ConnectButtons(self, cmd_list: list = None):
        for cmd in cmd_list:
            cmd.cmd_signal.connect(self.request.Process)
        return cmd_list

    # setup states
    def setupStates(self):
        self.state_start = QState()
        self.state_weigh = QState()
        self.state_reweigh = QState()
        self.state_count = QState()
        self.state_recount = QState()

        self.state_start.addTransition(self.response.next_state, self.state_weigh)
        self.state_weigh.addTransition(self.response.next_state, self.state_reweigh)
        self.state_reweigh.addTransition(self.response.next_state, self.state_count)
        self.state_count.addTransition(self.response.next_state, self.state_recount)
        self.state_recount.addTransition(self.response.next_state, self.state_start)

        self.state_weigh.addTransition(self.Reset_Button.clicked, self.state_start)
        self.state_reweigh.addTransition(self.Reset_Button.clicked, self.state_start)
        self.state_count.addTransition(self.Reset_Button.clicked, self.state_start)
        self.state_recount.addTransition(self.Reset_Button.clicked, self.state_start)

        self.state_start.entered.connect(self.EntryStart)
        self.state_weigh.entered.connect(self.EntryWeigh)
        self.state_reweigh.entered.connect(self.EntryReWeigh)
        self.state_count.entered.connect(self.EntryCount)
        self.state_recount.entered.connect(self.EntryReCount)
        self.state_recount.exited.connect(self.ResetState)

        self.machine = QStateMachine()
        self.machine.addState(self.state_start)
        self.machine.addState(self.state_weigh)
        self.machine.addState(self.state_reweigh)
        self.machine.addState(self.state_count)
        self.machine.addState(self.state_recount)
        self.machine.setInitialState(self.state_start)

    @pyqtSlot()
    def EntryStart(self):
        self.Protocol_Button.setEnabled(True)
        self.Weigh_Button.setEnabled(False)
        self.Count_Button.setEnabled(False)
        self.Log_Button.ConfigureButton()
        self.Log_Button.setEnabled(False)
        self.Reset_Button.setEnabled(False)
        self.ConfigureButtons()

    @pyqtSlot()
    def EntryWeigh(self):
        self.response.initiated.emit()
        self.Protocol_Button.NextCommand()
        self.Protocol_Button.setEnabled(False)
        self.Weigh_Button.setEnabled(True)
        self.Count_Button.setEnabled(False)
        self.Log_Button.setEnabled(False)
        self.Reset_Button.setEnabled(True)
        self.ConfigureButtons()

    @pyqtSlot()
    def EntryReWeigh(self):
        self.Weigh_Button.NextCommand()
        self.Protocol_Button.setEnabled(True)
        self.Weigh_Button.setEnabled(True)
        self.Count_Button.setEnabled(False)
        self.Log_Button.setText("Log Item")
        self.Log_Button.setEnabled(False)
        self.Reset_Button.setEnabled(True)
        self.ConfigureButtons()

    @pyqtSlot()
    def EntryCount(self):
        self.Protocol_Button.NextCommand()
        self.Protocol_Button.setEnabled(True)
        self.Weigh_Button.setEnabled(False)
        self.Count_Button.setEnabled(True)
        # self.Log_Button.setText("Log Item and Weight")
        self.Log_Button.setEnabled(False)
        self.Reset_Button.setEnabled(True)
        self.ConfigureButtons()

    @pyqtSlot()
    def EntryReCount(self):
        self.Count_Button.NextCommand()
        self.Protocol_Button.setEnabled(True)
        self.Weigh_Button.setEnabled(False)
        self.Count_Button.setEnabled(True)
        # self.Log_Button.setText("Log Item")
        self.Log_Button.setEnabled(False)
        self.Reset_Button.setEnabled(True)
        self.ConfigureButtons()

    @pyqtSlot()
    def ResetState(self):
        self.Protocol_Button.NextCommand()
        self.Weigh_Button.NextCommand()
        self.Count_Button.NextCommand()

        self.Protocol_Button.setEnabled(True)
        self.Weigh_Button.setEnabled(False)
        self.Count_Button.setEnabled(False)
        self.ConfigureButtons()

    @pyqtSlot()
    def ResetStateSignal(self):
        self.Protocol_Button.SetDefaultCmd("Start Weigh")
        self.Weigh_Button.SetDefaultCmd("Weigh")
        self.Count_Button.SetDefaultCmd("Count")

        self.Protocol_Button.setEnabled(True)
        self.Weigh_Button.setEnabled(False)
        self.Count_Button.setEnabled(False)
        self.ConfigureButtons()

    def ConfigureButtons(self):
        self.Protocol_Button.ConfigureButton()
        self.Weigh_Button.ConfigureButton()
        self.Count_Button.ConfigureButton()
