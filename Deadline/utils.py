import tempfile
import os
import subprocess
from config import config

def submit(app,name,start,end,inputFilepath,outputPath,pluginArgs,submitArgs):
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
        
    submitFile=open((tempDir+'/submit_info.job'),'w')
    submitFile.write(submitData)
    submitFile.close()
    submitFile=(tempDir+'/submit_info.job')
    submitFile=submitFile.replace('\\','/')
    
    #submitting to deadline
    result=subprocess.Popen((config.deadlineCommand,submitFile,pluginFile,inputFilepath),stdout=subprocess.PIPE)
    
    #return job id from deadline result
    result=result.communicate()[0]
    
    #getting jobid from deadline submittal
    jobid=''
    for data in result.split('\n'):
        if data.startswith('JobID'):
            jobid=data.split('=')[1]
    
    return jobid