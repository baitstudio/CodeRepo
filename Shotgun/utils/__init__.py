

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