import os

import maya.cmds as cmds
import maya.mel as mel

def referenceAsset(filePath):
    ''' References maya file in maya scene.
        Takes namespace from file.
    '''
    
    namespace=os.path.basename(filePath).split('.')[0]
    
    cmds.file(filePath,reference=True,namespace=namespace)

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

def alembicExport(startFrame,endFrame,fileName,fileDir,nodes):
    ''' Exports alembic file with meta data file (*.abcMeta) '''
    
    # defining variables
    nodesString=''
    
    # node loop
    for node in nodes:
        nodesString+='-root '+node+' '
    
    # export alembic file
    filePath=fileDir+'/'+fileName+'.abc'
    cmds.AbcExport(j='-frameRange %s %s -stripNamespaces -uvWrite -wholeFrameGeo -worldSpace -writeVisibility %s-file %s' % (startFrame,endFrame,nodesString,filePath))