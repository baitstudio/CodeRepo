import sys

#tools path
sys.path.append('Z:/_CORE/PythonRepo')

import maya.mel as mel
import tank
import pymel.core as pm
import maya.cmds as cmds

import bait_pytools.Maya.utils as mu
reload(mu)

def maya_light_setup(self):
    
    tk=self.parent.tank      
    ctx=self.parent.context
    
      
    cache_alembic=tk.templates['cache_alembic']
    fields=ctx.as_template_fields(cache_alembic)
    abcFile = cache_alembic.apply_fields(fields)
         
    
    pm.newFile(f=1, type='mayaAscii')
    
    #reference light setup scene
    lightSetup=mu.getLatestShotAssets('light')
    
    for asset in lightSetup:
        
        mu.referenceAsset(asset['path']['local_path_windows'])
    
    #referencing latest camera file
    camData=mu.getLatestShotFile('cam')
    
    if len(camData)<1:
            camData=mu.getLatestShotFile(self, 'cam')
            
            camNodes=mu.referenceAsset(camData['path']['local_path_windows'])
    else:
            camNodes=mu.referenceAsset(camData['path']['local_path_windows'])
            
    for node in camNodes:       
        if cmds.nodeType(node)=='camera':
            cam=node
    
    
    #loading alembic plugin
    pm.loadPlugin('AbcImport.mll')
    
    #import all alembic files for given shot
    shotAssets=mu.getLatestShotAssets(self,'rig',specific='Grandpa')
    
    mu.alembicImport(abcFile, 'root')
            
            
            
            
            
      