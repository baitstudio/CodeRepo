import os
import shutil

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

def referenceAsset(filePath,namespace=None):
    ''' References maya file in maya scene.
        Takes namespace from file.
    '''
    if not namespace:
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
    
    cmds.setAttr(imagePlane+'.depth',200)
    #return
    return imagePlane

def alembicExport(startFrame,endFrame,filePath,nodes,attributes=None):
    ''' Exports alembic file '''
    
    #making sure plugin is loaded
    pm.loadPlugin('AbcExport')
    
    # defining variables
    nodesString=''
    
    # node loop
    for node in nodes:
        nodesString+='-root '+node+' '
        
    attrstring = ''
    if attributes!=None:
        if len(attributes)>0:
            for attr in attributes:
                attrstring+='-a '+ attr + ' '
    
    # export alembic file
    pm.AbcExport(j='-frameRange %s %s %s-stripNamespaces -uvWrite -worldSpace -wholeFrameGeo -writeVisibility %s-file %s' % (startFrame,endFrame,attrstring,nodesString,filePath))
    #pm.AbcExport(filePath, )
    
def alembicImport(filePath, mode, parent=None, nodes=None):
    ''' Imports Alembic File'''    
    
    #making sure plugin is loaded
    pm.loadPlugin('AbcImport')
    
    if mode=='parent':
        pm.AbcImport(filePath, mode="import", ftr=True, sts=True, rpr=parent) 
         
    elif mode=='merge':
        nodesString=''
                
        for node in nodes:
            nodesString+='-root '+node+' '
        pm.AbcImport(filePath, mode="import", ct=nodesString, ftr=True, sts=True)
        
    else:
        pm.AbcImport(filePath, mode="import", ftr=True, sts=True)

def ExportSceneCache(exportAttr=None):
    ''' Exports any nodes with an asset attribute.
        Defaults to search in selection, else entire scene.
    
    '''
    
    #getting tank engine
    filePath=cmds.file(q=True,sn=True)
    dirPath=os.path.dirname(filePath)
    tk = tank.tank_from_path(dirPath)
    
    assets={}
    nodes = pm.ls(sl=True)
    
    if len(nodes)>0:  
        for node in nodes:        
            if pm.PyNode(node).hasAttr('asset'):            
                assetName=cmds.getAttr(node+'.asset')
                assets[assetName]=[]            
    else:     
        for node in pm.ls(type='transform'):        
            if pm.PyNode(node).hasAttr('asset'):            
                assetName=cmds.getAttr(node+'.asset')
                assets[assetName]=[]            
                nodes.append(node)
    
    if len(nodes)>0:
        for node in nodes:               
            assetName=cmds.getAttr(node+'.asset')
            assets[assetName].append(node)

    publish_arg_dic={}
        
    for asset in assets:
        
        ctx=tk.context_from_path(filePath)
        maya_work=tk.templates['shot_work_area_maya']
        
        fields=ctx.as_template_fields(maya_work)
        fields['Asset']=asset
        
        cache_alembic=tk.templates['cache_alembic']
        cachePath=cache_alembic.apply_fields(fields)
        
        nodes=assets[asset]
        startFrame=cmds.playbackOptions(q=True,animationStartTime=True)
        endFrame=cmds.playbackOptions(q=True,animationEndTime=True)
        
        alembicExport(startFrame,endFrame,cachePath,nodes,attributes=exportAttr)       
        publish_arg_dic.update({asset : {'publish_path':cachePath, 'tank_type': 'Alembic Cache', 'publish_name': (asset + ' Alembic')}})
        
    return publish_arg_dic

def set_arnold_subd(level):
       
    nodes = pm.ls(sl=True)
    meshes = []
    for node in nodes:
        meshes.append(node.getShape())
        for mesh in meshes:
            try:        
                mesh.aiSubdivType.set(1);
                mesh.aiSubdivIterations.set(level);
            except:
                print (mesh + ' could not be processed!')
 
 
 
def set_shadowcatchers(vis, selfshadow, opaque):
    nodes = pm.ls(sl=True)
    meshes = []
    for node in nodes:
        meshes.append(node.getShape()) 
        for mesh in meshes:
            try:        
                mel.eval('editRenderLayerAdjustment "%s.primaryVisibility";' % mesh)
                mesh.primaryVisibility.set(vis)
                mel.eval('editRenderLayerAdjustment "%s.aiSelfShadows";' % mesh)
                mesh.aiSelfShadows.set(selfshadow)
                mel.eval('editRenderLayerAdjustment "%s.aiOpaque";' % mesh)
                mesh.aiOpaque.set(opaque)
            except:
                print ('override couldn\'t be created. You are probably in the default layer. Setting default attribute instead.')
                mesh.primaryVisibility.set(vis)      
                mesh.aiSelfShadows.set(selfshadow)                         
            ShadowCatcherSG = 'ShadowCatcher_matSG'
            pm.sets(ShadowCatcherSG, e=True, forceElement=mesh)

def __exportPlayblast__(filePath,camera,width=640,height=360,exportType='movie',HUD=None):
    ''' Exports playblast to filePath
        
        type=['movie','still','sequence']
            movie = exports video
            still = exports image from middle of timeline
            sequence = exports image sequence
        
        HUD is a list of dictionaries following this format:
        HUD=[]
        HUD.append({'label':'Animator: Toke Jepsen',
                    'block':1,
                    'section':5,
                    'labelFontSize':'small',
                    'dataFontSize':'small'})
    '''
    
    result=cmds.objExists(camera)
    
    if result:
        
        #string $visPanels[] = `getPanel -vis`; < for fail safe of active panel
        panel = "modelPanel4"
        prevcam=cmds.modelEditor(panel, q=True,camera=True)
        
        mel.eval("lookThroughModelPanel "+camera+" "+panel)
        
        #getting current settings
        currentTime=cmds.currentTime(q=True)
        displayFilmGate=cmds.camera(camera,q=True,displayFilmGate=True)
        displayResolution=cmds.camera(camera,q=True,displayResolution=True)
        overscan=cmds.camera(camera,q=True,overscan=True)
        grid=cmds.modelEditor(panel,q=True,grid=True)
        displayAppearance=cmds.modelEditor(panel,q=True,displayAppearance=True)
        nurbsCurves=cmds.modelEditor(panel,q=True,nurbsCurves=True)
        
        #prepping for playblast
        cmds.camera(camera,edit=True,displayFilmGate=False,displayResolution=False,overscan=1)
        cmds.modelEditor(panel,e=True,grid=False,
                         displayAppearance='smoothShaded',
                         nurbsCurves=False)
        
        #query and hide previous huds
        prevHUD={}
        for headsup in cmds.headsUpDisplay(listHeadsUpDisplays=True):
            
            vis=cmds.headsUpDisplay(headsup,q=True,vis=True)
            prevHUD[headsup]=vis
            
            cmds.headsUpDisplay(headsup,e=True,vis=False)
        
        #creating custom huds
        customHUD=[]
        if HUD!=None:
            itr=1
            for headsup in HUD:
                
                cmd='cmds.headsUpDisplay(\'temp'+str(itr)+'\''
                for key in headsup:
                    if type(headsup[key])==str:
                        cmd+=','+key+'=\''+str(headsup[key])+'\''
                    else:
                        cmd+=','+key+'='+str(headsup[key])
                
                cmd+=')'
                eval(cmd)
                
                customHUD.append('temp'+str(itr))
                
                itr+=1
        
        #playblasting
        if exportType=='movie':
            
            result=cmds.playblast(f=filePath,format='qt',forceOverwrite=True,offScreen=True,percent=100,
                                   compression='H.264',quality=100,width=width,height=height,
                                   viewer=False)
        elif exportType=='still':
            
            startTime=cmds.playbackOptions(q=True,minTime=True)
            endTime=cmds.playbackOptions(q=True,maxTime=True)
            
            midTime=((endTime-startTime)/2)+startTime
            
            result=cmds.playblast(f=filePath,format='iff',forceOverwrite=True,offScreen=True,percent=100,
                                   compression='png',quality=100,startTime=midTime,endTime=midTime,
                                   width=width,height=height,viewer=False,showOrnaments=True)
            
            path=result.split('.')[0]
            ext=result.split('.')[-1]
            
            oldfile=filePath+'.'+str(int(midTime)).zfill(4)+'.'+ext
            newfile=path+'.'+ext
            
            shutil.move(oldfile,newfile)
            
            result=newfile
        elif exportType=='sequence':
            
            startTime=cmds.playbackOptions(q=True,minTime=True)
            endTime=cmds.playbackOptions(q=True,maxTime=True)
            
            result=cmds.playblast(f=filePath,format='iff',forceOverwrite=True,offScreen=True,percent=100,
                                   compression='png',quality=100,startTime=startTime,endTime=endTime,
                                   width=width,height=height,viewer=False,showOrnaments=True)
        
        #revert to settings
        cmds.currentTime(currentTime)
        cmds.camera(camera,edit=True,displayFilmGate=displayFilmGate,
                    displayResolution=displayResolution,
                    overscan=overscan)
        cmds.modelEditor(panel,e=True,grid=grid,
                         displayAppearance=displayAppearance,
                         nurbsCurves=nurbsCurves)
        
        for headsup in prevHUD:
            
            cmds.headsUpDisplay(headsup,e=True,vis=prevHUD[headsup])
        
        for headsup in customHUD:
            
            cmds.headsUpDisplay(headsup,remove=True)
        
        mel.eval("lookThroughModelPanel "+prevcam+" "+panel)
        
        return result
    else:
        cmds.warning('Requested camera cant be found!')
        
        return None