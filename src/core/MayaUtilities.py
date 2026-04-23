import maya.cmds as mc
import maya.mel as ml
from maya.OpenMaya import MVector

def ConfigureCtrlForJnt(jnt, ctrlName, doConstraint=True):
    ctrlGrpName = ctrlName + "_grp"
    mc.group(ctrlName, n=ctrlGrpName)

    mc.matchTransform(ctrlGrpName, jnt)
    if doConstraint:
        mc.orientConstraint(ctrlName, jnt)

    return ctrlName, ctrlGrpName

# make the plus shaped controller, will be used for FKIK blend
def CreatePlusController(namePrefix, size):
    ctrlName = f"ac_{namePrefix}_ikfk_blend"
    cmd = f"curve -n {ctrlName} -d 1 -p 0 0 0 -p 20 0 0 -p 20 0 20 -p 40 0 20 -p 40 0 40 -p 20 0 40 -p 20 0 60 -p 0 0 60 -p 0 0 40 -p -20 0 40 -p -20 0 20 -p 0 0 20 -p 0 0 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ;"
    ml.eval(cmd)

    mc.setAttr(f"{ctrlName}.scale", 0.3,0.3,0.3, type="double3")
    
    mc.makeIdentity(ctrlName, apply=True)
    
    mc.setAttr(f'{ctrlName}.translateX', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.translateY', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.translateZ', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.rotateX', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.rotateY', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.rotateZ', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.scaleX', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.scaleY', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.scaleZ', lock=True, k=0, cb=0)
    mc.setAttr(f'{ctrlName}.visibility', lock=True, k=0, cb=0)

    SetCurveLineWidth(ctrlName, 2)
    return ctrlName

def CreateArrowController(namePrefix, size):
    pass

def CreateCircleControllerForJnt(jnt, namePrefix, radius=10):
    ctrlName = f"ac_{namePrefix}_{jnt}"
    mc.circle(n=ctrlName, r = radius, nr=(1,0,0))
    SetCurveLineWidth(ctrlName, 2)
    return ConfigureCtrlForJnt(jnt, ctrlName)

def CreateBoxControllerForJnt(jnt, namePrefix, size=10):
    ctrlName = f"ac_{namePrefix}_{jnt}"
    cmd = f"curve -n {ctrlName} -d 1 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p 0.5 -0.5 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 ;"
    ml.eval(cmd)
    mc.setAttr(f"{ctrlName}.scale", size, size, size, type="double3")
    
    # freeze transforation basically
    mc.makeIdentity(ctrlName, apply=True)
    SetCurveLineWidth(ctrlName, 2)
    return ConfigureCtrlForJnt(jnt, ctrlName)

def GetObjectPositionAsMVec(objectName)->MVector:
    
    wsLoc = mc.xform(objectName, t=True, ws=True, q=True)
    return MVector(wsLoc[0], wsLoc[1], wsLoc[2])

def SetCurveLineWidth(curve, newWidth):
    shapes = mc.listRelatives(curve, s=True)
    for shape in shapes:
        mc.setAttr(f"{shape}.lineWidth", newWidth)