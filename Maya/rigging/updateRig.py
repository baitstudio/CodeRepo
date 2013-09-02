import os

import maya.cmds as cmds

#getting the reference file info
node=cmds.ls(selection=True)[0]

referenceNode=cmds.referenceQuery( node, referenceNode=True,topReference=True)

filepath=cmds.referenceQuery( referenceNode, filename=True)
filename=os.path.basename(filepath)
fileprefix=os.path.basename(filepath).split('.v')[0]

dirPath=os.path.dirname(filepath)

#get latest file in dirPath
latestFile=''
version=0
for f in os.listdir(dirPath):
    
    if f.startswith(fileprefix):
        
        v=int(f.split('.v')[-1].split('.')[0])
        if v>version:
            
            latestFile=f
            version=v

#saving file
cmds.file(save=True)

#editing ma file
currentFile=cmds.file(q=True,sn=True)

cmds.file(newFile=True)

f=open(currentFile,'r')
fdata=f.read()
fdata=fdata.replace(filename,latestFile)
f.close()

f=open(currentFile,'w')
f.write(fdata)
f.close()

#reloading the file
cmds.file(currentFile,open=True)