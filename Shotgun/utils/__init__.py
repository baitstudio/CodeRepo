import maya.cmds as cmds
import sgtk

projectPath=cmds.workspace(q=True,fullName=True)
tk = sgtk.sgtk_from_path(projectPath)
ctx=tk.context_from_path(projectPath)
sg=tk.shotgun


def getLatestShotFile(tk,ctx,publishedType=None,filetag=None, step=None):
    
    #return variable
    result=[]
    
    shot=sg.find_one('Shot', filters=[['id','is',ctx.entity['id']]])
    
    #getting tank data
    tankfiles=sg.find('PublishedFile', filters=[['entity','is',shot]],fields=['version_number','task','path','published_file_type', 'name', 'sg_step'])
    
    publishFiles={}
    abcFiles=[]
    
    if publishedType and step:
        for f in tankfiles:   
            if f['sg_step']==step:
                if f['published_file_type']['name'] == publishedType:               
                    if f['name'] in publishFiles:                
                        name=f['name']
                        temp_dic={'id':f['id'],'version_number':f['version_number']}                  
                        if publishFiles[name]['version_number']<f['version_number']:
                            publishFiles[name] = temp_dic
                    else:
                        temp_dic={'id':f['id'],'version_number':f['version_number']}
                        publishFiles[f['name']]= temp_dic       
        #return latest tank publish
        if len(publishFiles)>0:
            for file in publishFiles.items():
                for f in tankfiles:
                    if f['id']==file[1]['id']:
                        result.append(f)
    elif step:
        for f in tankfiles:        
            if f['sg_step']==step:
                publishFiles[f['version_number']]=f['id']
        #return latest tank publish
        if len(publishFiles)>0:
            latestVersion=max(publishFiles, key=publishFiles.get)
            latestId=publishFiles[latestVersion]
            for f in tankfiles:
                if f['id']==latestId:
                    result.append(f)
     
    elif publishedType:
        for f in tankfiles:   
            if f['published_file_type']['name'] == publishedType:            
                if f['name'] in publishFiles:                   
                    name=f['name']
                    temp_dic={'id':f['id'],'version_number':f['version_number']}                  
                    if publishFiles[name]['version_number']<f['version_number']:
                        publishFiles[name] = temp_dic
                else:
                    temp_dic={'id':f['id'],'version_number':f['version_number']}
                    publishFiles[f['name']]= temp_dic   
        #return latest tank publish
        if len(publishFiles)>0:
            for file in publishFiles.items():
                for f in tankfiles:
                    if f['id']==file[1]['id']:
                        result.append(f)
                                 
    elif filetag:
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
                    result.append(f)
                
    return result


def getLatestShotAssets(tk,ctx,filetag=None, specific=None, publishedType=None, category=None):
    ''' Gets latest assets connected to opened file.
        
        filetag = string
        
        Returns list of TankPublishedFile dictionaries.
    '''
    
    #return variable
    result=[]
    
    #getting assets
    #sg=platform.parent.shotgun
    
    #ctx=platform.parent.context
    
    assets=sg.find_one('Shot', filters=[['id','is',ctx.entity['id']]],fields=['assets'])['assets']
    

    if category!=None:     
        for asset in assets:
            sg_asset = sg.find_one('Asset', filters=[['id','is',asset['id']]],fields=['sg_asset_type'])
            if sg_asset['sg_asset_type'] == category:
                tankfiles=sg.find('PublishedFile', filters=[['entity','is',asset]],fields=['version_number','task','path','published_file_type'])
                
                publishFiles={}
                for f in tankfiles:
                    if f['published_file_type']['name'] == publishedType:
                    #data=sg.find_one('Task',filters=[['id','is',f['task']['id']]],fields=['sg_filetag']) 
                    #if data['sg_filetag']==filetag:
                        publishFiles[f['version_number']]=f['id']
                
                if len(publishFiles)>0:
                    latestVersion=max(publishFiles, key=publishFiles.get)
                    latestId=publishFiles[latestVersion]
                    for f in tankfiles:
                        if f['id']==latestId:
                            
                            f['assetName']=asset['name']
                            
                            result.append(f)
    
    elif specific!=None:        
        for asset in assets:
            if asset['name']==specific:
                
                tankfiles=sg.find('PublishedFile', filters=[['entity','is',asset]],fields=['version_number','task','path','published_file_type'])
                
                publishFiles={}
                for f in tankfiles:
                    if f['published_file_type']['name'] == publishedType:
                    #data=sg.find_one('Task',filters=[['id','is',f['task']['id']]],fields=['sg_filetag']) 
                    #if data['sg_filetag']==filetag:
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
            tankfiles=sg.find('PublishedFile', filters=[['entity','is',asset]],fields=['version_number','task','path','published_file_type',])
            
            publishFiles={}
            for f in tankfiles:
                if f['published_file_type']['name'] == publishedType:
                #data=sg.find_one('Task',filters=[['id','is',f['task']['id']]],fields=['sg_filetag'])               
                #if data['sg_filetag']==filetag:
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