from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QGridLayout,
    QGroupBox,
    QPushButton,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

from wac.command_button import Command
from wac.router import Router

import sys
from matplotlib.pyplot import text
import numpy as np
import pyqtgraph as pg

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
PADDING = 10
SPACING = 10
MARGIN = 10
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Request(Router):
    # output the chosen command to serial output
    command = pyqtSignal(object)

    # serial specific signals
    viewer_open = pyqtSignal()
    viewer_close = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.setObjectName("Prompt_Request")

        self.route = {
            "OPENVIEWER": self.OpenViewer,
            "CLOSEVIEWER": self.CloseViewer,
        }

    def OpenViewer(self, cmd: Command) -> None:
        self.viewer_open.emit(cmd)

    def CloseViewer(self, cmd: Command) -> None:
        self.viewer_close.emit(cmd)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Response(Router):

    # serial specific signals
    viewer_opened = pyqtSignal()
    viewer_closed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        self.setObjectName("Prompt_Response")

        self.route = {
            "OPENVIEWER": self.OpenViewer,
            "CLOSEVIEWER": self.CloseViewer,
        }

    def OpenViewer(self, cmd: Command) -> None:
        self.viewer_opened.emit(cmd)

    def CloseViewer(self, cmd: Command) -> None:
        self.viewer_closed.emit(cmd)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class PromptWidget(QWidget):

    """The constructor."""

    def __init__(self, parent=None):
        super(PromptWidget, self).__init__(parent)
        self.request = Request(parent=parent)
        self.response = Response(parent=parent)

        self.serial_data_viewer = SerialDataViewer()

        self.setupUi()

        self.PButton_SerialDataViewer.toggled.connect(self.serial_data_viewer.show)
        self.PButton_SerialDataViewer.toggled.connect(self.LaunchDataViewer)
        self.serial_data_viewer.viewer_closed.connect(
            self.PButton_SerialDataViewer.toggle
        )

    def setupUi(self):
        self.setObjectName("PromptWidget")

        self.TextEdit_Prompt = QTextEdit()
        self.TextEdit_Prompt.setText("")
        self.TextEdit_Prompt.setReadOnly(True)
        self.PButton_SerialDataViewer = QPushButton(
            self,
            text="Launch Serial Data Viewer",
            checked=False,
            checkable=True,
        )

        # Grid Layout
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        self.vbox.setSpacing(PADDING)
        self.vbox.addWidget(self.TextEdit_Prompt)
        self.vbox.addWidget(self.PButton_SerialDataViewer)

        self.GBox_Prompt = QGroupBox(self, title="Prompt")
        self.GBox_Prompt.setLayout(self.vbox)

        # Grid Layout
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(PADDING)
        self.gridLayout.addWidget(self.GBox_Prompt, 0, 0, 1, 1)
        self.setLayout(self.gridLayout)
        self.setWindowTitle("Prompt Widget")

    @pyqtSlot(bool)
    def LaunchDataViewer(self, checked: bool = False):
        if checked:
            self.PButton_SerialDataViewer.setDisabled(True)
        else:
            self.PButton_SerialDataViewer.setDisabled(False)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class LivePlotter(QWidget):
    def __init__(self, parent=None):
        super(LivePlotter, self).__init__(parent)
        self.setupUi()

    def setupUi(self):

        self.verticalLayout = QVBoxLayout()
        pen = pg.mkPen(color="r")
        self.win = pg.GraphicsLayoutWidget()
        self.myPlot = self.win.addPlot()
        self.data = np.zeros(1000)
        self.curve = self.myPlot.plot(self.data, pen=pen)

        self.myPlot.setYRange(0, 1000)
        self.verticalLayout.addWidget(self.win)
        self.setLayout(self.verticalLayout)
        self.setStyleSheet("border-radius: 3px;")

    @pyqtSlot(int)
    def update(self, rawInt):
        print(rawInt)
        self.data[:-1] = self.data[1:]
        self.data[-1] = rawInt
        self.curve.setData(self.data)


"""
SerialDataViewer Class: enables viewing of the serial input, output and status
data

Parameters
----------
None

Methods
----------
setupUi: None
    set up the UI
Signals
----------

Slots
----------
SerialSend: None
SerialReceive: None
SerialStatus: None
"""


class SerialDataViewer(QWidget):

    STATUS = {
        "CONNECTED": "[SerialIO][Connect] Connected",
        "DISCONNECTED": "[SerialIO][Disconnect] Disconnected",
        "TERMINATED": "[SerialIO][Terminate] Terminated",
    }

    viewer_closed = pyqtSignal()

    live_plot_update = pyqtSignal(int)

    def __init__(self, parent=None):
        super(SerialDataViewer, self).__init__(parent)
        self.setupUi()
        self.live_plot_update.connect(self.LivePlot.update)

    def setupUi(self):
        """Serial output Text box"""
        self.TextEdit_SerialStatus = QTextEdit(readOnly=True)
        self.LivePlot = LivePlotter()
        self.LivePlot.setMaximumSize(300, 300)
        self.TextEdit_DataReceived = QTextEdit(readOnly=True)

        self.Label_SerialSend = QLabel(text="Live Plot")
        self.Label_SerialSend.setAlignment(Qt.AlignCenter)

        self.Label_SerialReceive = QLabel(text="Receive")
        self.Label_SerialReceive.setAlignment(Qt.AlignCenter)

        self.Label_SerialStatus = QLabel(text="Status")
        self.Label_SerialStatus.setAlignment(Qt.AlignCenter)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.Label_SerialStatus)
        self.vbox.addWidget(self.TextEdit_SerialStatus)

        self.vbox.addWidget(self.Label_SerialSend)
        self.vbox.addWidget(self.LivePlot)

        self.vbox.addWidget(self.Label_SerialReceive)
        self.vbox.addWidget(self.TextEdit_DataReceived)

        self.setWindowTitle("Serial Data Viewer")
        self.setLayout(self.vbox)

    @pyqtSlot(int)
    def ViewDataSent(self, serSend: int):
        self.live_plot_update.emit(serSend)

    @pyqtSlot(str)
    def ViewDataReceived(self, serRec: str):
        self.TextEdit_DataReceived.append(serRec)

    @pyqtSlot(bool)
    def ViewSerialStatus(self, serStat: bool):
        text = self.STATUS["CONNECTED"] if serStat else self.STATUS["DISCONNECTED"]
        self.TextEdit_SerialStatus.append(text)

    def closeEvent(self, event):
        self.viewer_closed.emit()
        event.accept()
