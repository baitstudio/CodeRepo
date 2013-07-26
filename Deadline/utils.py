'''

need to submit files outputpath

'''

import tempfile
import os
import subprocess
from config import config

def submit(app,name,start,end,inputFilepath,outputPath,outputFiles,pluginArgs,submitArgs,
           shotgunContext=None,shotgunFields=None,shotgunUser=None,mayaGUI=False):
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
        
    submitFile=open((tempDir+'/submit_info.job'),'w')
    submitFile.write(submitData)
    submitFile.close()
    submitFile=(tempDir+'/submit_info.job')
    submitFile=submitFile.replace('\\','/')
    
    #submitting to deadline
    #special case for maya, cause subprocess doesnt work in maya
    if mayaGUI:
        
        import maya.mel as mel
        
        cmd='call \\"'+config.deadlineCommand+'\\" \\"'+submitFile+'\\" \\"'+pluginFile+'\\" \\"'+inputFilepath+'\\"'
        mel.eval('system("%s");' % cmd)
        
    else:
        result=subprocess.Popen((config.deadlineCommand,submitFile,pluginFile,inputFilepath),
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,shell=False)
    '''
    #return job id from deadline result
    result=result.communicate()[0]
    
    #getting jobid from deadline submittal
    jobid=''
    for data in result.split('\n'):
        if data.startswith('JobID'):
            jobid=data.split('=')[1]
    
    return jobid
    '''

'''
app='maya'
name='maya_test'
start=0
end=10
inputFilepath='M:/00719_grandpa/episodes/000_dummy/0000/Light/work/deadline_testing.light.v001.ma'
outputPath='M:/00719_grandpa/episodes/000_dummy/0000/Light/work/images'
pluginArgs=['']
submitArgs=['Comment=testing deadline script']
shotgunFields=None
shotgunContext=None

submit(app,name,start,end,inputFilepath,outputPath,pluginArgs,submitArgs,shotgunContext=shotgunContext,shotgunFields=shotgunFields)
'''