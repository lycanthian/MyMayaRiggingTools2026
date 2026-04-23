from core.MayaWidget import MayaWidget
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QColorDialog
from PySide6.QtGui import QColor
import maya.cmds as mc
from maya.OpenMaya import MVector


import importlib
import core.MayaUtilities
importlib.reload(core.MayaUtilities)

from core.MayaUtilities import (CreateCircleControllerForJnt, 
                                CreateBoxControllerForJnt, 
                                CreatePlusController, 
                                ConfigureCtrlForJnt,
                                GetObjectPositionAsMVec)

class LimbRigger:
    def __init__(self):
        self.nameBase = ""
        self.controllerSize = 10
        self.blendControllerSize = 4
        self.controlColorRGBF = [0,0,0,0]

    def SetNameBase(self, newNameBase):
        self.nameBase = newNameBase
        print(f"The name base is [{self.nameBase}]")

    def setControllerSize(self, newControllerSize):
        self.controllerSize = newControllerSize

    def SetBlendControllerSize(self, newBlendControllerSize):
         self.blendControllerSize = newBlendControllerSize

    def SetControlColor(self, newControlColor):
        self.controlColorRGBF = newControlColor
        self.controlColorRGBF = self.controlColorRGBF.removeprefix('(').removesuffix(')')
        splitList = self.controlColorRGBF.split(",")
        for i in range(len(splitList)):
            splitList[i] = float(splitList[i])
        self.controlColorRGBF = splitList
        print(f"new control color is {self.controlColorRGBF}")
        
    def RigLimb(self):
        print("Start Rigging :0D!!!!!!")
        rootJnt, midJnt, endJnt = mc.ls(sl=True)
        print(f"root: {rootJnt}, mid: {midJnt}, end: {endJnt}")

        rootCtrl, rootCtrlGrp = CreateCircleControllerForJnt(rootJnt, "fk_"+self.nameBase, self.controllerSize)
        midCtrl, midCtrlGrp = CreateCircleControllerForJnt(midJnt, "fk_"+self.nameBase, self.controllerSize)
        endCtrl, endCtrlGrp = CreateCircleControllerForJnt(endJnt, "fk_"+self.nameBase, self.controllerSize)
        mc.parent(endCtrlGrp, midCtrl)
        mc.parent(midCtrlGrp, rootCtrl)

        endIKCtrl, endIKCtrlGrp = CreateBoxControllerForJnt(endJnt, "ik_" + self.nameBase, self.controllerSize)

        ikfkBlendCtrlPrefix = self.nameBase + "_ikfkBlend"
        ikfkBlendController = CreatePlusController(ikfkBlendCtrlPrefix, self.blendControllerSize) 
        ikfkBlendController, ikfkBlendControllerGrp = ConfigureCtrlForJnt(rootJnt, ikfkBlendController, False)

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikfkBlendController, ln=ikfkBlendAttrName, min=0, max=1, k=True)

        ikHandleName = "ikHandle_" + self.nameBase 
        mc.ikHandle(n=ikHandleName, sj = rootJnt, ee=endJnt, sol="ikRPsolver")

        rootJntLoc = GetObjectPositionAsMVec(rootJnt)
        endJntLoc = GetObjectPositionAsMVec(endJnt)
        
        poleVectorVals = mc.getAttr(f"{ikHandleName}.poleVector")[0]
        poleVectorDir = MVector(poleVectorVals[0], poleVectorVals[1], poleVectorVals[2])
        poleVectorDir.normalize()

        rootToEndVec = endJntLoc - rootJntLoc
        rootToEndDist = rootToEndVec.length()

        poleVectorCtrlLoc = rootJntLoc + rootToEndVec/2.0 + poleVectorDir * rootToEndDist

        poleVectorCtrlName = "ac_ik_" + self.nameBase + "poleVector"
        mc.spaceLocator(n=poleVectorCtrlName)
        
        poleVectorCtrlGrpName = poleVectorCtrlName + "_grp"
        mc.group(poleVectorCtrlName, n=poleVectorCtrlGrpName)

        mc.setAttr(f"{poleVectorCtrlGrpName}.translate", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, type="double3")
        mc.poleVectorConstraint(poleVectorCtrlName, ikHandleName)

        mc.parent(ikHandleName, endIKCtrl)
        mc.setAttr(f"{ikHandleName}.v", 0)

        mc.connectAttr(f"{ikfkBlendController}.{ikfkBlendAttrName}", f"{ikHandleName}.ikBlend")
        mc.connectAttr(f"{ikfkBlendController}.{ikfkBlendAttrName}", f"{endIKCtrlGrp}.v")
        mc.connectAttr(f"{ikfkBlendController}.{ikfkBlendAttrName}", f"{poleVectorCtrlGrpName}.v")

        reverseNodeName = f"{self.nameBase}_reverse"
        mc.createNode("reverse", n=reverseNodeName)

        mc.connectAttr(f"{ikfkBlendController}.{ikfkBlendAttrName}", f"{reverseNodeName}.inputX")
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{rootCtrlGrp}.v")

        orientConstraint = None
        wristConnections = mc.listConnections(endJnt)
        for connection in wristConnections:
            if mc.objectType(connection) == "orientConstraint":
                orientConstraint = connection
                break

        mc.connectAttr(f"{ikfkBlendController}.{ikfkBlendAttrName}", f"{orientConstraint}.{endIKCtrl}W1")
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{orientConstraint}.{endCtrl}W0")

        topGrpName = f"{self.nameBase}_rig_grp"
        mc.group(n=topGrpName, empty=True)

        mc.parent(rootCtrlGrp, topGrpName)
        mc.parent(ikfkBlendControllerGrp, topGrpName)
        mc.parent(endIKCtrlGrp, topGrpName)
        mc.parent(poleVectorCtrlGrpName, topGrpName)

        # add color override for topGrpName after making color picker to be the self.controlColorRGB
        print(self.controlColorRGBF[0], self.controlColorRGBF[1], self.controlColorRGBF[2])
        mc.setAttr(f"{topGrpName}.overrideEnabled", 1)
        mc.setAttr(f"{topGrpName}.overrideRGBColors", 1)
        mc.setAttr(f"{topGrpName}.overrideColorRGB",self.controlColorRGBF[0],self.controlColorRGBF[1],self.controlColorRGBF[2])


class LimbRiggerWidget(MayaWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limb Rigger")
        self.rigger = LimbRigger()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.masterLayout.addWidget(QLabel("Select the 3 joints of the limb, from base to end, and then:"))
        self.infoLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.infoLayout)
        self.infoLayout.addWidget(QLabel("Name Base:"))

        self.nameBaseLineEdit = QLineEdit()
        self.infoLayout.addWidget(self.nameBaseLineEdit)

        self.setNameBaseBtn = QPushButton("Set Name Base")
        self.setNameBaseBtn.clicked.connect(self.SetNameBaseBtnClicked)
        self.infoLayout.addWidget(self.setNameBaseBtn)

        # add a color pick widget to the self.masterLayout
        # listen for color change & connect to a function
        # function needs to update the color of the limbRigger: self.rigger.controlColorRGB
        self.setColorBtn = QPushButton("Set Color")
        self.masterLayout.addWidget(self.setColorBtn)
        self.setColorBtn.clicked.connect(self.SetColorBtnClicked)

        self.rigLimbBtn = QPushButton("Rig Limb")
        self.rigLimbBtn.clicked.connect(self.RigLimbBtnClicked)
        self.masterLayout.addWidget(self.rigLimbBtn)

    def SetColorBtnClicked(self):

        dialog = QColorDialog()
        newColor = QColorDialog.getColor(initial=QColor("blue"), title="Select a Color")
        controlColorRGBF = newColor
        controlColorRGBF = str(controlColorRGBF).replace("PySide6.QtGui.QColor.fromRgbF","")
        print(f"new control color:", controlColorRGBF)
        self.rigger.SetControlColor(controlColorRGBF)


    def SetNameBaseBtnClicked(self):
        self.rigger.SetNameBase(self.nameBaseLineEdit.text())

    def RigLimbBtnClicked(self):
        self.rigger.RigLimb()

    def GetWidgetHash(self):
            return "ac5f62fa55da53cef51991229a8897984b18d953e4b066bc06ab9af00f564ba7"
    
def Run():
    limbRiggerWidget = LimbRiggerWidget()
    limbRiggerWidget.show()

Run()