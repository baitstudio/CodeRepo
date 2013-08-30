import sys

#tools path
sys.path.append('K:/CodeRepo')

import maya.mel as mel
import tank
import pymel.core as pm
import maya.cmds as cmds

def SetupSimScene(platform):
    
    
    
    # get the current scene path and extract fields from it
    # using the work template:
    scene_path = os.path.abspath(cmds.file(query=True, sn=True))
    fields = work_template.get_fields(scene_path)
    publish_version = fields["version"]

    #prepare all the paths and variables
    clothFile = "Z:/work/00719_grandpa/assets/Props/Main_Outift/publish/mainOutfit.cloth.v001.ma"
    abcFile = "Y:/RENDERS/00719_grandpa/000_dummy/0000/cache/grandpa.abc"
    ncachePath = "Y:/RENDERS/00719_grandpa/000_dummy/0000/cache/nCache"
    abcNodes = "shoes l_eye r_eye topTeeth bottomTeeth body"
    
    #loading alembic plugin
    cmds.loadPlugin('AbcImport.mll')
    
    #import all the necessary data
    pm.newFile(f=1, type='mayaAscii')
    pm.importFile(clothFile)
    pm.AbcImport(abcFile, mode="import", ct=abcNodes, ftr=True, crt=True, sts=True)
    
    #query time data
    startTime=pm.playbackOptions(q=True,animationStartTime=True)
    endTime=pm.playbackOptions(q=True,animationEndTime=True)
    
    pm.currentTime(startTime)
    
    #find all nCloth objects
    clothObjects = pm.ls(type='nCloth')
    
    #create simulation cache for all nCloth nodes in the scene
    print ('caching theses nCloth objects: ' + str(clothObjects))
    cacheFiles = pm.cacheFile(cnd=clothObjects, st=startTime, et=endTime, dir=ncachePath, dtf=True, fm='OneFile', r=True, ws=True)
    
    #apply created cache to simulated objects
    cacheShapes = pm.ls('outputCloth*')
    i=0
    for shape in cacheShapes:
        switch = mel.eval('createHistorySwitch(\"' + str(shape) + '\",false)')
        cacheNode = pm.cacheFile(f=cacheFiles[i], cnm=str(shape), ia='%s.inp[0]' % switch ,attachFile=True, dir=ncachePath)
        pm.setAttr( '%s.playFromCache' % switch, 1 )
        i += 1