from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QGridLayout, QGroupBox
from PyQt5.QtCore import QStateMachine,  pyqtSignal, pyqtSlot, QState, Qt

from CommandButton import  Command, MultiCommandButton
from Router import Router
from CommandButton import SerialCommands


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
QSS_CONNECT = """
QPushButton {
    background-color: green;
    color: white;      
    font-size: 16px;
}
"""

QSS_DISCONNECT = """
QPushButton {
    background-color: red;
    color: white;
    font-size: 16px;
}
"""

PADDING = 10
SPACING = 10
MARGIN = 10

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Request(Router):
    # output the chosen command to serial output
    command = pyqtSignal(object)
    prompt = pyqtSignal(str)
    
    # serial specific signals
    connect = pyqtSignal(object)
    disconnect = pyqtSignal(object)
    
    def __init__(self, *args, **kwargs): 
        super(Request, self).__init__(*args, **kwargs)
        self.setObjectName("SerialConnection_Request")

        self.route = {
            "CONNECT": self.Connect,
            "DISCONNECT": self.Disconnect,
        }

    def Connect(self, cmd:Command) -> None:
        self.connect.emit(cmd)
        print("[serial request] Connect button")
        
    def Disconnect(self, cmd:Command) -> None:
        self.disconnect.emit(cmd)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Response(Router):
    
    # serial specific signals
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    autoconnected= pyqtSignal()
    
    def __init__(self, *args, **kwargs): 
        super(Response, self).__init__(*args, **kwargs)
        self.setObjectName("SerialConnection_Response")

        self.route = {
            "CONNECT": self.Connect,
            "DISCONNECT": self.Disconnect,
        }
    
    def Connect(self, cmd:Command) -> None:
        self.connected.emit()
    
    def Disconnect(self, cmd:Command) -> None:
        self.disconnected.emit()
    
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

class SerialConnectionWidget(QWidget):

    
    """ The constructor."""
    def __init__(self, parent=None): 
        super(SerialConnectionWidget, self).__init__(parent)       
        self.request = Request(parent=parent)
        self.response = Response(parent=parent)

        self.setupUi()
        
        self.setupStates()
        self.Connection_Button.SetDefaultCmd("Connect")
        self.request.prompt.emit(self.Connection_Button.cmd.promptHowTo)
        self.machine.start()
    
    def setupUi(self):    
        self.setObjectName("SerialConnectionWidget")        
        
        # generate the commands
        cmdList = self.ConnectButtons(SerialCommands(parent=self))
        self.Connection_Button = MultiCommandButton(
            cmd=cmdList[0], 
            cmdList=cmdList, 
            parent=self
            )
        self.Connection_Button.setMinimumHeight(50)
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        self.vbox.setSpacing(PADDING)
        self.vbox.addWidget(self.Connection_Button)
        
        self.GBox_SerialConnection = QGroupBox(self, title="Serial Connection")
        self.GBox_SerialConnection.setLayout(self.vbox)
        
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(PADDING)
        self.gridLayout.addWidget(self.GBox_SerialConnection, 0, 0, 1, 11)
        self.setLayout(self.gridLayout)

    
    '''
    Connect the button signals to the Processor handling all the Requests and Responses
    use a list to iterate over a list of commands
    '''
    def ConnectButtons(self, cmd_list:list=None):
        for cmd in cmd_list:
            cmd.cmd_signal.connect(self.request.Process)
        return cmd_list
        

    # setup states
    def setupStates(self):
        self.state_disconnected = QState()
        self.state_connected = QState()

        self.state_disconnected.addTransition(self.response.connected, self.state_connected)
        self.state_connected.addTransition(self.response.disconnected, self.state_disconnected)
        self.state_disconnected.addTransition(self.response.autoconnected, self.state_connected)
        
        self.state_disconnected.entered.connect(self.EntryDisconnected)
        self.state_connected.entered.connect(self.EntryConnected)
        
        self.machine = QStateMachine()
        self.machine.addState(self.state_disconnected)
        self.machine.addState(self.state_connected)
        self.machine.setInitialState(self.state_disconnected)
        
    @pyqtSlot()
    def EntryDisconnected(self):
        self.Connection_Button.SetDefaultCmd("Connect")
        self.Connection_Button.setStyleSheet(QSS_DISCONNECT)
        self.Connection_Button.setEnabled(True)
        self.Connection_Button.ConfigureButton()
        
    @pyqtSlot()
    def EntryConnected(self):
        self.Connection_Button.NextCommand()
        self.Connection_Button.setStyleSheet(QSS_CONNECT)
        self.Connection_Button.setEnabled(True)
        self.Connection_Button.ConfigureButton()
        

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

