from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QPushButton

DEBUGGING = False

class Command(QObject):
    # signals
    cmd_signal = pyqtSignal(object)
    cmd_success = pyqtSignal(bool)
    cmd_prompt = pyqtSignal(str, str)

    enable_button = pyqtSignal() # enables the parent button, if connected

    def __init__(
        self, 
        name:str="", 
        cmd:str="", 
        cmdType:str=None, 
        promptStatus:str="", 
        promptHowTo:str="",  
        promptProceed:str="",
        cmdStyle=None, 
        *args, 
        **kwargs
    ):
        super(Command, self).__init__(*args, **kwargs)
        self.name = name
        self.cmd = cmd
        self.cmdType = cmdType
        self.cmdStyle = cmdStyle
        self.promptStatus = promptStatus
        self.promptHowTo = promptHowTo
        self.promptProceed = promptProceed
        self.returnValue = 0

    def EmitCommand(self):
        self.cmd_signal.emit(self)

    def EnableButton(self):
        self.enable_button.emit()


class CommandButton(QPushButton):

    def __init__(self, cmd:Command=None, *args, **kwargs):
        super(CommandButton, self).__init__(*args, **kwargs)
        self.cmd = cmd
        self.runConnections()

    def runConnections(self):
        self.clicked.connect(self.ForwardSignal)
        self.clicked.connect(self.DisableButton)
        self.cmd.enable_button.connect(self.EnableButton)
        if DEBUGGING:
            self.clicked.connect(self.Debugging)

    def ConfigureButton(self):
        self.setText(self.cmd.name)

    @pyqtSlot()
    def ForwardSignal(self):
        self.cmd.EmitCommand()

    @pyqtSlot()
    def DisableButton(self):
        self.setDisabled(True)

    @pyqtSlot()
    def EnableButton(self):
        self.setEnabled(True)
    
    @pyqtSlot()
    def Debugging(self):
        print(f'[{self.cmd.name}] [{self.cmd.cmd}] ')



class MultiCommandButton(QPushButton):

    def __init__(self, cmd:Command=None, cmdList:list=[], *args, **kwargs):
        super(MultiCommandButton, self).__init__(*args, **kwargs)
        self.cmdList = cmdList
        self.cmdGen = self.CommandGenerator()
        self.cmd = next(self.cmdGen)
        self.runConnections()


    def runConnections(self):
        self.clicked.connect(self.ForwardSignal)
        self.clicked.connect(self.DisableButton)
        for command in self.cmdList:
            command.enable_button.connect(self.EnableButton)
        
        if DEBUGGING:
            self.clicked.connect(self.Debugging)

    def ConfigureButton(self):
        self.setText(self.cmd.name)

    @pyqtSlot()
    def ForwardSignal(self):
        self.cmd.EmitCommand()

    def NextCommand(self):
        self.cmd = next(self.cmdGen)
        self.ConfigureButton()

    # create a circular generator
    def CommandGenerator(self):
        while True:
            for cmd in self.cmdList:
                yield cmd

    @pyqtSlot()
    def DisableButton(self):
        self.setDisabled(True)

    @pyqtSlot()
    def EnableButton(self):
        self.setEnabled(True)
    
    def SetDefaultCmd(self, cmdName:str):
        for cmd in self.cmdList:
            if cmd.name == cmdName:
                self.cmd = cmd
    
    @pyqtSlot()
    def Debugging(self):
        print(f'[{self.cmd.name}] [{self.cmd.cmd}] ')

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def ProtocolCommands(parent=None) -> list:
    cmd_startWeigh = Command(
        name="Start Weigh", 
        cmd="-h", 
        cmdType="STARTWEIGH", 
        promptStatus="",
        promptHowTo="To Weigh an item, place the item in the basket, then press 'Weigh'",
        parent=parent,
        )
    cmd_startCount = Command(
        name="Start Count", 
        cmd="-i", 
        cmdType="STARTCOUNT", 
        promptStatus="",
        promptHowTo="To Count items, place the items in the basket, then press 'Count'.\n\n To Re-weigh the item, press 'Re-Weigh'.\n\n To finish weighing this item, press 'Finish",
        parent=parent,
        )
    cmd_finish = Command(
        name="Finish", 
        cmd="-j", 
        cmdType="FINISH", 
        promptStatus="Finalising measurement, returning to home. ",
        promptHowTo="To Re-Count the items, press 'Re-Count', otherwise, press 'Finish' to finalise the measurement",
        parent=parent,
        )
    return [cmd_startWeigh, cmd_startCount, cmd_finish]
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def WeighCommands(parent=None) -> list:
    cmd_weigh = Command(
        name="Weigh", 
        cmd="-f", 
        cmdType="WEIGH", 
        promptStatus="Weighing item, please wait",
        promptHowTo="",
        promptProceed="To Re-Weigh the item, press 'Re-Weigh'. To start counting items, press 'Start Count",
        parent=parent,
        )
    cmd_re_weigh = Command(
        name="Re-Weigh", 
        cmd="-f", 
        cmdType="REWEIGH", 
        promptStatus="Re-Weighing item, please wait",
        promptHowTo="",
        promptProceed="To Re-Weigh the item, press 'Re-Weigh'. To start counting items, press 'Start Count",
        parent=parent,
        )
    return [cmd_weigh, cmd_re_weigh]
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def ResetAndLogCommands(parent=None) -> list:
    cmd_reset = Command(
        name="Reset", 
        cmd="-l", 
        cmdType="RESET", 
        promptStatus="Resetting scales, please wait",
        promptHowTo="",
        promptProceed="To exit the current procedure, back to the home state, press 'Reset'",
        parent=parent,
        )
    cmd_log = Command(
        name="Log Item", 
        cmd="-m", 
        cmdType="LOGITEM", 
        promptStatus="Logging item, please wait",
        promptHowTo="",
        promptProceed="To log the item, press the 'Log Item' button after weighing the item initially",
        parent=parent,
        )
    return [cmd_reset, cmd_log]
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def CountCommands(parent=None) -> list:
    cmd_count = Command(
        name="Count", 
        cmd="-g", 
        cmdType="COUNT", 
        promptStatus="Counting items, please wait",
        promptHowTo="",
        promptProceed="To Re-Count the items, press 'Re-Count'. To finalise the count, press 'Finish'",
        parent=parent,
        )
    cmd_re_count = Command(
        name="Re-Count", 
        cmd="-g", 
        cmdType="RECOUNT", 
        promptStatus="Re-Counting items, please wait",
        promptHowTo="",
        promptProceed="To Re-Count the items, press 'Re-Count'. To finalise the count, press 'Finish'",
        parent=parent,
        )
    return [cmd_count, cmd_re_count]
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def CalibrationCommands(parent=None) -> list:
    cmd_calibrate = Command(
        name="Calibrate", 
        cmd="-d", 
        cmdType="CALIBRATE", 
        promptStatus="Calibrating scales, please wait",
        promptHowTo="To calibrate the scales, make sure the basket is empty, then press the 'Calibrate' button located in the Calibration Box.",
        parent=parent,
        )
    cmd_tare = Command(
        name="Tare", 
        cmd="-e", 
        cmdType="TARE", 
        promptStatus="Taring scales, please wait",
        promptHowTo="To zero the scales, make sure the basket is empty, then press the 'Tare' button located in the Calibration Box",
        parent=parent,
        )
    return [cmd_calibrate, cmd_tare]
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def SerialDataViewerCommands(parent=None) -> list:
    cmd_openViewer = Command(
        name="Open Viewer", 
        cmd="-o", 
        cmdType="OPENVIEWER", 
        promptStatus="",
        promptHowTo="",
        parent=parent,
        )
    cmd_closeViewer = Command(
        name="Close Viewer", 
        cmd="-v", 
        cmdType="CLOSEVIEWER", 
        promptStatus="",
        promptHowTo="",
        parent=parent,
        )
    return [cmd_openViewer, cmd_closeViewer]
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def SerialCommands(parent=None) -> list:
    cmd_connect = Command(
        name="Disconnected",
        cmd="-k",
        cmdType="CONNECT",
        promptStatus="Connecting to scales, please wait",
        promptHowTo="To connect to the scales, ensure that the scales are plugged in, then press 'Connect'",
        parent=parent
        )
    cmd_disconnect = Command(
        name="Connected",
        cmd="-k",
        cmdType="DISCONNECT",
        promptStatus="Disconnecting from scales, please wait",
        promptHowTo="To disconnect from the scales, press 'Disconnect' below, then unplug the cable from the computer.",
        parent=parent
        )
    return [cmd_connect, cmd_disconnect]
