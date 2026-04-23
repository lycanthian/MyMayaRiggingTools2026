# need extensions MayaCode & MayaPy
# type in MEL file in maya -- commandPort -n "localhost:7001"
import maya.cmds as mc
from PySide6.QtWidgets import QWidget, QMainWindow 
from PySide6.QtCore import Qt
import maya.OpenMayaUI as omui
from shiboken6 import wrapInstance

def GetMayaMainWindow()->QMainWindow:
    mayaMainWindow = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mayaMainWindow), QMainWindow)

def RemoveWidgetWithName(objectName):
    for widget in GetMayaMainWindow().findChildren(QWidget, objectName):
        widget.deleteLater()

class MayaWidget(QWidget):
    def __init__(self):
        super().__init__(parent=GetMayaMainWindow())
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Maya Widget")
        RemoveWidgetWithName(self.GetWidgetHash())
        self.setObjectName(self.GetWidgetHash())

    def GetWidgetHash(self):
        return "a459f3b9252e23f257ebc7b19925e59a0662e1b48ea3ecc62c53e29d8e9853ca"