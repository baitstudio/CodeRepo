import os

import Shotgun.tools as su
import Deadline.utils as du

shotsList=open(r'C:\Users\toke.jepsen\Desktop/shotsList.txt','r')

shotNames=[]
for line in shotsList.readlines():
    shotNames.append(line.replace('\n',''))

for name in shotNames:
    
    nameIndex=shotNames.index(name)
    
    try:
        publishedFile=su.getPublishedFileFromShotname(name, 'Nuke Script')
        renderFile=su.getPublishedFileFromShotname(name, 'Comp Render')
        
        path=publishedFile['path']['local_path_windows']
        fileName=os.path.basename(path)
        fileSplit=fileName.split('.')
        fileSplit[-2]='v%03d' % (publishedFile['version_number']+1)
        
        work_filename='.'.join(fileSplit)
        work_dir=os.path.dirname(path)
        work_dir=os.path.join(os.path.split(work_dir)[0],'work')
        
        work_file=None
        if os.path.exists(os.path.join(work_dir,work_filename)):
            work_file=os.path.join(work_dir,work_filename)
        
        if work_file:
            
            nuke='"C:/Program Files/Nuke7.0v8/Nuke7.0.exe"'
            script='K:/CodeRepo/Nuke/readToPrecomp.py'
            read_path='M:/00719_grandpa/assets/Environments/Meadow/publish/meadowStill_v004.tif'
            precomp_path='M:/00719_grandpa/assets/Environments/Meadow/work/Meadow_background.comp.v001.nk'
            
            os.environ['NUKE_PATH']=r'K:\Tank\tank\install\apps\app_store\tk-nuke-writenode\v0.1.10\gizmos'
            
            cmd=nuke
            cmd+=' -t'
            cmd+=' '+script
            cmd+=' '+work_file
            cmd+=' '+read_path
            cmd+=' '+precomp_path
            
            #os.system(cmd)
            
            #getting shotgun data
            shotgunData=su.getDeadlineData(publishedFile['entity']['name'], 'toke.jepsen',
                                           publishedFile['version_number']+1,
                                           publishedFile['task']['name'],
                                           publishedFile['task']['id'])
            
            print shotgunData
            
            framerange=su.getFramerangeFromShotname(publishedFile['entity']['name'])
            
            print framerange
            
            print renderFile
            dirSplit=list(os.path.split(os.path.dirname(renderFile['path']['local_path_windows'])))
            print dirSplit
            dirSplit[-1]='v%03d' % (publishedFile['version_number']+1)
            outputPath=os.path.join(dirSplit[0],dirSplit[-1])
            
            '''
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
            
            fileSplit=os.path.basename(renderFile['path']['local_path_windows']).split('.')
            
            for item in fileSplit:
                
                index=fileSplit.index(item)
                
                if item.startswith('%'):
                    
                    fileSplit[index]='?????'
                
                if item.startswith('v'):
                    
                    fileSplit[index]='v%03d' % (publishedFile['version_number']+1)
            
            outputFiles=[os.path.join(outputPath,'.'.join(fileSplit))]
        
            pluginArgs=['']
            submitArgs=['Comment=ScriptBot submission']
            limit='nuke_render'
            
            du.submitRaw('nuke', work_filename, framerange['cut_in'], framerange['cut_out'], work_file, outputPath,
                         outputFiles,pluginArgs=pluginArgs,submitArgs=submitArgs,shotgunData=shotgunData,limit=limit,
                         priority=40)
                         '''
                                 
        print 'Successfull %s of %s: %s' % (nameIndex+1,len(shotNames),name)
    except Exception as e:
        print 'Failed %s of %s: %s\n%s' % (nameIndex+1,len(shotNames),name,e)
        
        f=open(r'C:\Users\toke.jepsen\Desktop/failedShots.txt','r')
        
        data=f.readlines()
        data.append(name+'\n')
        data=''.join(data)
        
        f=open(r'C:\Users\toke.jepsen\Desktop/failedShots.txt','w')
        f.write(data)
        f.close()