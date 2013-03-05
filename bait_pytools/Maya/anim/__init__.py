import os
import sys

#tools path
sys.path.append('Z:/_CORE/PythonRepo')

import maya.cmds as cmds
import tank

import bait_pytools.Maya.utils as mu
reload(mu)

def SetupScene():
    
    #referencing latest rigs
    assets=mu.getLatestShotAssets('rig')
    
    for asset in assets:
        
        mu.referenceAsset(asset['path']['local_path_windows'])
    
    #referencing latest camera track
    camData=mu.getLatestShotFile('track')
    
    camNodes=mu.referenceAsset(camData['path']['local_path_windows'])
    
    #getting camera node
    for node in camNodes:
        
        if cmds.nodeType(node)=='camera':
            cam=node
    
    #sets up plate
    
    #getting tank engine
    filePath=cmds.file(q=True,sn=True)
    dirPath=os.path.dirname(filePath)
    tk = tank.tank_from_path(dirPath)
    
    ctx=tk.context_from_path(filePath)
    maya_work=tk.templates['shot_work_area_maya']
    
    fields=ctx.as_template_fields(maya_work)
    
    low_plate=tk.templates['low_resolution_plate']
    plateDir=low_plate.parent.apply_fields(fields)
    
    firstFile=os.listdir(plateDir)[0]
    
    imagePath=plateDir+'/'+firstFile
    mu.imagePlane(cam, imagePath)

def ExportCache():
    
    #getting tank engine
    filePath=cmds.file(q=True,sn=True)
    dirPath=os.path.dirname(filePath)
    tk = tank.tank_from_path(dirPath)
    
    assets={}
    nodes=[]
    
    for node in cmds.ls(type='transform'):
        
        if (cmds.attributeQuery('asset',n=node,ex=True))==True:
            
            assetName=cmds.getAttr(node+'.asset')
            assets[assetName]=[]
            
            nodes.append(node)
    if len(nodes)>0:
        for node in nodes:
            
            assetName=cmds.getAttr(node+'.asset')
            assets[assetName].append(node)
    
    for asset in assets:
        
        ctx=tk.context_from_path(filePath)
        maya_work=tk.templates['shot_work_area_maya']
        
        fields=ctx.as_template_fields(maya_work)
        fields['sg_asset_type']=asset
        
        cache_alembic=tk.templates['cache_alembic']
        cachePath=cache_alembic.apply_fields(fields)
        
        nodes=assets[asset]
        startFrame=cmds.playbackOptions(q=True,minTime=True)
        endFrame=cmds.playbackOptions(q=True,maxTime=True)
        
        mu.alembicExport(startFrame, endFrame,cachePath, nodes)