import os
import sys

#shotgun path
sys.path.append('Z:/_CORE/Shotgun/python-api')

import maya.cmds as cmds
import maya.mel as mel
from shotgun_api3 import Shotgun
import tank

def getShotgunServer():
    ''' Returns baitTools shotgun server. '''
    
    path='https://bait.shotgunstudio.com'
    name='baitTools'   
    key='58a765d77a0a9d3d778ab2e389ca132a3c79170a'
    
    return Shotgun(path,name,key)

def getFileContext():
    
    #getting tank engine
    filePath=cmds.file(q=True,sn=True)
    dirPath=os.path.dirname(filePath)
    tk = tank.tank_from_path(dirPath)
    
    #getting scene data
    ctx=tk.context_from_path(filePath)
    
    #return
    return ctx

def getLatestShotFile(filetag):
    ''' Gets latest files connected to opened file.
        
        filetag = string
        
        Returns latest TankPublishFile dictionary.
    '''
    
    #getting shot data
    sg=getShotgunServer()
    
    ctx=getFileContext()
    
    shot=sg.find_one('Shot', filters=[['id','is',ctx.entity['id']]])
    
    #getting tank data
    tankfiles=sg.find('TankPublishedFile', filters=[['entity','is',shot]],fields=['version_number','task','path'])
    
    publishFiles={}
    for f in tankfiles:
        
        data=sg.find_one('Task',filters=[['id','is',f['task']['id']]],fields=['sg_filetag'])
        
        if data['sg_filetag']==filetag:
            publishFiles[f['version_number']]=f['id']
    
    #return latest tank publish
    if len(publishFiles)>0:
        latestVersion=max(publishFiles, key=publishFiles.get)
        latestId=publishFiles[latestVersion]
        for f in tankfiles:
            if f['id']==latestId:
                
                return f

def getLatestShotAssets(filetag):
    ''' Gets latest assets connected to opened file.
        
        filetag = string
        
        Returns list of TankPublishedFile dictionaries.
    '''
    
    #return variable
    result=[]
    
    #getting assets
    sg=getShotgunServer()
    
    ctx=getFileContext()
    
    assets=sg.find_one('Shot', filters=[['id','is',ctx.entity['id']]],fields=['assets'])['assets']
    
    for asset in assets:
        tankfiles=sg.find('TankPublishedFile', filters=[['entity','is',asset]],fields=['version_number','task','path'])
        
        publishFiles={}
        for f in tankfiles:
            
            data=sg.find_one('Task',filters=[['id','is',f['task']['id']]],fields=['sg_filetag'])
            
            if data['sg_filetag']==filetag:
                publishFiles[f['version_number']]=f['id']
        
        if len(publishFiles)>0:
            latestVersion=max(publishFiles, key=publishFiles.get)
            latestId=publishFiles[latestVersion]
            for f in tankfiles:
                if f['id']==latestId:
                    
                    f['assetName']=asset['name']
                    
                    result.append(f)
    
    #return
    return result

def referenceAsset(filePath):
    ''' References maya file in maya scene.
        Takes namespace from file.
    '''
    
    namespace=os.path.basename(filePath).split('.')[0]
    
    return cmds.file(filePath,reference=True,namespace=namespace,
                     returnNewNodes=True)

def imagePlane(cam,filePath):
    ''' Sets up image plane in scene.
        
        Returns name of image plane.
    '''
    
    #create a new image plane
    imagePlane = cmds.createNode("imagePlane")
    
    #assign the imagePlane to the camera
    mel.eval( 'cameraImagePlaneUpdate "%s" "%s";' % (cam, imagePlane) )
    
    #Connect the image to imagePlane
    cmds.setAttr( "%s.imageName" % imagePlane, filePath, type="string")
    
    #enable image sequence
    cmds.setAttr(imagePlane+'.useFrameExtension',1)
    
    #return
    return imagePlane

def alembicExport(startFrame,endFrame,filePath,nodes):
    ''' Exports alembic file with meta data file (*.abcMeta) '''
    
    # defining variables
    nodesString=''
    
    # node loop
    for node in nodes:
        nodesString+='-root '+node+' '
    
    # export alembic file
    cmds.AbcExport(j='-frameRange %s %s -stripNamespaces -uvWrite -wholeFrameGeo -worldSpace -writeVisibility %s-file %s' % (startFrame,endFrame,nodesString,filePath))