import shotgun_api3 as shotgun
import config

sg=shotgun.Shotgun(config.base_url, config.script_name, config.api_key)

def getFramerangeFromShotname(shotname):
    
    fields = ['sg_cut_in','sg_cut_out','sg_cut_duration']
    filters = [['code','is',shotname]]
    shot=sg.find_one("Shot",filters,fields)
    
    return {'cut_in':shot['sg_cut_in'],'cut_out':shot['sg_cut_out'],
            'cut_duration':shot['sg_cut_duration']}

def getDeadlineData(shotCode,userLogin,version,taskName,taskId):

    filters=[['code','is',shotCode]]
    fields=['project','code']
    shot=sg.find_one('Shot',filters,fields)
    
    shotgunData={}
    shotgunData['task']={}
    shotgunData['project']={}
    shotgunData['entity']={}
    
    shotgunData['project']['name']=shot['project']['name']
    shotgunData['project']['id']=shot['project']['id']
    shotgunData['entity']['name']=shot['code']
    shotgunData['entity']['id']=shot['id']
    shotgunData['entity']['type']='Shot'
    shotgunData['login']=userLogin
    shotgunData['version']=version
    shotgunData['task']['name']=taskName
    shotgunData['task']['id']=taskId
    
    return shotgunData

def getPublishedFileFromShotname(shotname,publishedType):
        
    fields = []
    filters = [['code','is',shotname]]
    shot=sg.find_one("Shot",filters,fields)
    
    publishedFiles=getLatestShotFile(shot['id'],publishedType=publishedType)
    
    publishedFile=None
    version=0
    if len(publishedFiles)!=1:
        for f in publishedFiles:
            if f['version_number']>version:
                publishedFile=f
                version=f['version_number']
    else:
        publishedFile=publishedFiles[0]
    
    return publishedFile

def getLatestShotFile(shotId,publishedType=None,filetag=None, step=None):
    
    #return variable
    result=[]
    
    shot=sg.find_one('Shot', filters=[['id','is',shotId]])
    
    #getting tank data
    fields=['version_number','task','path','published_file_type', 'name', 'sg_step','entity']
    filters=[['entity','is',shot]]
    tankfiles=sg.find('PublishedFile', filters,fields)
    
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