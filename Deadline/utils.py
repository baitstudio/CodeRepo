'''
todo:
    ability to update/change predefined plugin/submit args

usage example:

    app='redline'
    name='temp'
    start=0
    end=100
    inputFilepath='C:/temp/A006_C005_01246Z.RDC/A006_C005_01246Z_002.R3D'
    outputPath='C:/temp1'
    outputFile='temp.R3D'
    pluginArgs=['']
    submitArgs=['Comment=something']
    
    submit(app,name,start,end,inputFilepath,outputPath,outputFile,sceneFile,pluginArgs,submitArgs)
'''

import tempfile
import os
import subprocess
from config import config

def submit(app,name,start,end,inputFilepath,outputPath,outputFile,sceneFile,pluginArgs,submitArgs):
    #get temp directory
    tempDir=tempfile.gettempdir()
    
    #generate plugin file
    pluginData=open((os.path.dirname(__file__)+'/config/'+str(app)+'_plugin.txt'),'r')
    pluginData=pluginData.read()
    pluginData+='\n'
    
    for arg in pluginArgs:
        pluginData+=arg+'\n'
    
    if inputFilepath!='':
        pluginData+='SceneFile='+inputFilepath+'\n'
    
    pluginData+='OutputFolder='+outputPath+'\n'
    pluginData+='OutputBaseName='+outputFile+'\n'
    
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
    submitData+='OutputDirectory0='+outputPath+'\n'
    submitData+='OutputFilename0='+outputFile+'\n'
        
    submitFile=open((tempDir+'/submit_info.job'),'w')
    submitFile.write(submitData)
    submitFile.close()
    submitFile=(tempDir+'/submit_info.job')
    submitFile=submitFile.replace('\\','/')
    
    #submitting to deadline
    if sceneFile!='':
        result=subprocess.Popen((config.deadlineCommand,submitFile,pluginFile,sceneFile),stdout=subprocess.PIPE)
    else:
        result=subprocess.Popen((config.deadlineCommand,submitFile,pluginFile),stdout=subprocess.PIPE)

    #removing temp files
    #os.remove(submitFile)
    #os.remove(pluginFile)
    
    #return job id from deadline result
    result=result.communicate()[0]
    
    #getting jobid from deadline submittal
    jobid=''
    for data in result.split('\n'):
        if data.startswith('JobID'):
            jobid=data.split('=')[1]
    
    return jobid

'''
app='maya'
name='maya_test'
start=0
end=10
inputFilepath='N:/testing_deadline/New_Project/scenes/test.ma'
sceneFile='N:/testing_deadline/New_Project/scenes/test.ma'
outputPath='N:/testing_deadline/New_Project/images'
outputFile='test.????.exr'
pluginArgs=['']
submitArgs=['Comment=testing deadline script']

submit(app,name,start,end,inputFilepath,outputPath,outputFile,sceneFile,pluginArgs,submitArgs)
'''