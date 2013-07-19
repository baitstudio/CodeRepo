'''
Created on 18 Jul 2013

@author: toke.jepsen
'''


import maya.cmds as cmds
import maya.mel as mel 


from sgtk import TankError
import sgtk

#getting context- THIS NEED TO USE THE APP CONTEXT INSTEAD!
#projectPath=cmds.workspace(q=True,fullName=True)
#tk = sgtk.sgtk_from_path(projectPath)
#ctx=tk.context_from_path(projectPath)
ctx=self._app.context.entity
 
#flush namespaces
cmds.namespace(setNamespace="::")
currentNameSpaces = cmds.namespaceInfo(listOnlyNamespaces=True)
 
def removeNamespaces(namespace='::'):
    
    ignoreNamespaces = ['UI', 'shared']
    
    cmds.namespace(setNamespace=namespace)
    childNamespaces = cmds.namespaceInfo(listOnlyNamespaces=True)
    if childNamespaces:
    
        namespaces=list(set(childNamespaces)-set(ignoreNamespaces))
        for n in namespaces:
            removeNamespaces(':'+n)
    else:
        parent=':'+cmds.namespaceInfo(parent=True)
        cmds.namespace(setNamespace=parent)
        
        cmds.namespace(moveNamespace=[namespace,parent],force=True)
        
        cmds.namespace(removeNamespace=namespace)
        
        if parent!='::':
            removeNamespaces(parent)
 
removeNamespaces()
 
#deleting history
for mesh in cmds.ls(type='mesh'):
    
    if cmds.objExists(mesh):
        
        #delete history
        cmds.delete(mesh,ch=True)
 
invisibleMeshes=[]
#check scene for invisible meshes
for mesh in cmds.ls(type='mesh'):
    
    if cmds.objExists(mesh):
        
        transform=cmds.listRelatives(mesh,parent=True)[0]
        
        #make visible - need to raise error if some objects are invisible---
        if cmds.getAttr(transform+'.v')==0:
            invisibleMeshes.append(transform)
 
 
if invisibleMeshes:
    
    listString=''
    for mesh in invisibleMeshes:
        listString+=mesh+','
    
    #raise sgtk.TankError("Unable to perform pre-publish for invisible meshes %s" % listString)
 
#flush any tranforms that arent a mesh
for transform in cmds.ls(type='transform'):
    
    if cmds.objExists(transform):
        shapes=cmds.listRelatives(transform,shapes=True,fullPath=True)
        
        #deleting empty transforms
        if shapes:
            check=False
            for shape in shapes:
                
                #deleting everything but meshes
                shapeType=cmds.nodeType(shape)
                if shapeType=='mesh':
                    check=True
                if shapeType=='camera':
                    cams=['front','top','persp','side']
                    if transform in cams:
                        check=True
            
            if not check:
                cmds.delete(transform)
        else:
            cmds.delete(transform)
 
#geo group
geogrp=cmds.group(empty=True,n='geo')
 
meshes=[]
#process meshes
for mesh in cmds.ls(type='mesh'):
    
    if cmds.objExists(mesh):
        
        transform=cmds.listRelatives(mesh,parent=True)[0]
        parent=cmds.listRelatives(transform,parent=True)
        if parent!=None:
            parent=parent[0]
        
        #make visible - need to raise error if some objects are invisible---
        #if cmds.getAttr(transform+'.v')==0:
        #    raise cmds.error()
        
        #set pivot to world zero
        posGrp=cmds.group(empty=True)
        
        pivotTranslate = cmds.xform (posGrp, q = True, ws = True, rotatePivot = True)
        
        cmds.parent(transform, posGrp)
        cmds.makeIdentity(transform, a = True, t = True, r = True, s = True)
        cmds.xform (transform, ws = True, pivots = pivotTranslate)
        
        if parent!=None:
            cmds.parent(transform,parent)
        else:
            cmds.parent(transform,w=True)
        
        cmds.delete(posGrp)
        
        #deleting any unused nodes
        cmd='MLdeleteUnused;'
        mel.eval(cmd)
        
        #adding asset tag
        if not cmds.objExists(transform+'.asset'):
            cmds.addAttr(transform,ln='asset',dt='string')
        cmds.setAttr(transform+'.asset',ctx.entity['name'],type='string')
        
        #add to group
        if parent!=geogrp:
            cmds.parent(transform,geogrp)