from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from CommandButton import  Command

'''

example route:
route = {
    "PROTOCOL": self.Protocol,
    "WEIGH": self.Weigh,
    "REWEIGH": self.ReWeigh,
    "COUNT": self.Count,
    "RECOUNT": self.ReCount,
}

To use this as a middleperson, connect the forward signal and the process signal
[signals]
    [command] ---> x
    [process] ---> Process
    connect a signal to Process, to route the signal
        a route dict must be assigned or passed in
    
    [forward] ---> Forward
    connect a signal to Forward, to automatically forward a signal
[slots]
'''
class Router(QObject):

    command = pyqtSignal(object)
    forward = pyqtSignal(object)
    process = pyqtSignal(object)
    
    def __init__(self, route:dict={}, routeBy:str="cmdType", *args, **kwargs): 
        super(Router, self).__init__(*args, **kwargs)
        self.route = route
        self.routeBy = routeBy
        self.process.connect(self.Process)
        self.setName()
    
    def __name__(self):
        return "Router"
    
    def setRoute(self, route:dict={}) -> None:
        self.route = route
    
    def setName(self, name:str=None) -> None:
        if name:
            objName = name
        elif self.parent():
            parent = self.parent()
            parentName = parent.objectName()
            objName = f"{parentName}{self.__name__()}"
        else:
            objName = f'{self.__name__()}'
        self.setObjectName(objName)
        
    '''
    [Slot] Processes commands passed via signals.
    Routes the signal, with the command object to the correct handler.
    1) check if a route has been passed in as asn arg
    2) if note use the native route assigned to the class
    
    Paramters
    ---------
    cmd
    '''
    @pyqtSlot(object)
    def Process(self, cmd:Command):
        #print(f"[{self.objectName()}] Processing")
        cmdAttr = cmd.__getattribute__(self.routeBy)
        fn = self.route[cmdAttr]
        fn(cmd)
    
    '''
    Use this to forward signals automatically 
    '''
    @pyqtSlot(object)
    def Forward(self, cmd:Command) -> None:
        self.forward.emit(cmd)
        