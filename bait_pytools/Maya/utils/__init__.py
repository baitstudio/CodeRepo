import os
import sys

#shotgun path
sys.path.append('Z:/_CORE/Shotgun/python-api')

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from shotgun_api3 import Shotgun
import tank

def getLatestShotFile(platform,filetag):
    ''' Gets latest files connected to opened file.
        
        filetag = string
        
        Returns latest TankPublishFile dictionary.
    '''
    
    #getting shot data
    sg=platform.parent.shotgun
    
    ctx=platform.parent.context
    
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

def getLatestShotAssets(platform,filetag,specific=None):
    ''' Gets latest assets connected to opened file.
        
        filetag = string
        
        Returns list of TankPublishedFile dictionaries.
    '''
    
    #return variable
    result=[]
    
    #getting assets
    sg=platform.parent.shotgun
    
    ctx=platform.parent.context
    
    assets=sg.find_one('Shot', filters=[['id','is',ctx.entity['id']]],fields=['assets'])['assets']
    
    if specific==None:
    
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
    else:
        
        for asset in assets:
            if asset['name']==specific:
                
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
    ''' Exports alembic file '''
    
    # defining variables
    nodesString=''
    
    # node loop
    for node in nodes:
        nodesString+='-root '+node+' '
    
    # export alembic file
    cmds.AbcExport(j='-frameRange %s %s -stripNamespaces -uvWrite -wholeFrameGeo -worldSpace -writeVisibility %s-file %s' % (startFrame,endFrame,nodesString,filePath))
    
    
def alembicImport(filePath, mode, parent=None, nodes=None):
    ''' Imports Alembic File'''    
    
    if mode=='parent':
        pm.AbcImport(filePath, mode="import", ftr=True, sts=True, rpr=parent) 
         
    elif mode=='merge':
        nodesString=''
                
        for node in nodes:
            nodesString+='-root '+node+' '
        pm.AbcImport(filePath, mode="import", ct=nodesString, ftr=True, sts=True)
        
    else:
        pm.AbcImport(filePath, mode="import", ftr=True, sts=True)
    