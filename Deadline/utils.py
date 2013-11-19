import tempfile
import os
import subprocess
from config import config

def submit(app,name,start,end,inputFilepath,outputPath,outputFiles,pluginArgs,submitArgs,
           shotgunContext=None,shotgunFields=None,shotgunUser=None,mayaGUI=False,limit=None,priority=None):
    '''
    usage:
    
        app='maya'
        name='maya_test'
        start=0
        end=10
        inputFilepath='N:/test/test.ma'
        outputPath='N:/test'
        pluginArgs=['']
        submitArgs=['Comment=testing deadline script']
        
        submit(app,name,start,end,inputFilepath,outputPath,pluginArgs,submitArgs)
    '''
    #get temp directory
    tempDir=tempfile.gettempdir()
    
    #generate plugin file
    pluginData=open((os.path.dirname(__file__)+'/config/'+str(app)+'_plugin.txt'),'r')
    pluginData=pluginData.read()
    pluginData+='\n'
    
    for arg in pluginArgs:
        pluginData+=arg+'\n'
    
    pluginData+='OutputFilePath='+outputPath+'/\n'
    
    #special case for arnold
    if app=='arnold':
        pluginData+='InputFile='+inputFilepath+'\n'
        
        pluginData+='OutputFile='+outputFiles[0].replace('\\','/').replace('?','')+'\n'
    else:
        pluginData+='SceneFile='+inputFilepath+'\n'
    
    pluginFile=open((tempDir+'/plugin_info.job'),'w')
    pluginFile.write(pluginData)
    pluginFile.close()
    pluginFile=(tempDir+'/plugin_info.job')
    pluginFile=pluginFile.replace('\\','/')

    #generate submit file
    submitData=open((os.path.dirname(__file__)+'/config/'+str(app)+'_submit.txt'),'r')
    submitData=submitData.read()
    submitData+='\n'
    
    for arg in submitArgs:
        submitData+=arg+'\n'
    
    submitData+='Name='+name+'\n'
    submitData+='Frames='+str(start)+'-'+str(end)+'\n'
    
    #generate output filename section
    for outputfile in outputFiles:
        
        count=outputFiles.index(outputfile)
        
        submitData+='OutputFilename%s=%s\n' % (count,outputfile.replace('\\','/'))
    
    #shotgun submittal
    if shotgunContext:
        
        submitData+='ExtraInfo0='+str(shotgunContext.task['name'])+'\n'
        submitData+='ExtraInfo1='+str(shotgunContext.project['name'])+'\n'
        submitData+='ExtraInfo2='+str(shotgunContext.entity['name'])+'\n'
        submitData+='ExtraInfo3='+str(shotgunFields['version'])+'\n'
        submitData+='ExtraInfo4=Version generated from Deadline\n'
        submitData+='ExtraInfo5='+str(shotgunUser['login'])+'\n'
        
        submitData+='ExtraInfoKeyValue0=TaskId='+str(shotgunContext.task['id'])+'\n'
        submitData+='ExtraInfoKeyValue1=ProjectId='+str(shotgunContext.project['id'])+'\n'
        submitData+='ExtraInfoKeyValue2=EntityId='+str(shotgunContext.entity['id'])+'\n'
        submitData+='ExtraInfoKeyValue3=EntityType='+str(shotgunContext.entity['type'])+'\n'
    
    #limit group editing
    if limit:
        
        submitLines=submitData.split('\n')
        
        for line in submitLines:
        
            if 'LimitGroups' in line:
        
                del(submitLines[submitLines.index(line)])
        
        submitLines.append('LimitGroups=%s' % limit)
        
        submitData='\n'.join(submitLines)
    
    #priority editing
    if priority:
        
        submitLines=submitData.split('\n')
        
        for line in submitLines:
        
            if 'Priority' in line:
        
                del(submitLines[submitLines.index(line)])
        
        submitLines.append('Priority=%s' % str(priority))
        
        submitData='\n'.join(submitLines)
    
    submitFile=open((tempDir+'/submit_info.job'),'w')
    submitFile.write(submitData)
    submitFile.close()
    submitFile=(tempDir+'/submit_info.job')
    submitFile=submitFile.replace('\\','/')
    
    #submitting to deadline
    #special case for maya, cause subprocess doesnt work in maya
    if mayaGUI:
        
        import maya.mel as mel
        
        cmd='call \\"'+config.deadlineCommand+'\\" \\"'+submitFile+'\\" \\"'+pluginFile+'\\"'
        result=mel.eval('system("%s");' % cmd)
    else:
        result=subprocess.Popen((config.deadlineCommand,submitFile,pluginFile),
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,shell=False)
        
        result=result.communicate()[0]
    
    #getting jobid from deadline submittal
    jobid=''
    for data in result.split('\n'):
        if data.startswith('JobID'):
            jobid=data.split('=')[1]
    
    return jobid

'''
app='arnoldExport'
name='maya_test'
start=1
end=113
inputFilepath='C:/Users/toke.jepsen/Desktop/sh504.light.v002.ma'
outputPath='C:/Users/toke.jepsen/Desktop/ass/'
outputFiles=['C:/Users/toke.jepsen/Desktop/ass/beauty/sh504.light.v001.#####.ass']
pluginArgs=['']
submitArgs=['Comment=testing deadline script']

print submit(app,name,start,end,inputFilepath,outputPath,outputFiles,pluginArgs,submitArgs,mayaGUI=True)
'''