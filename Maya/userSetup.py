import os
import sys
import shutil
import maya.cmds as cmds

#loading tapp
import tapp_maya

#loading alembic
cmds.evalDeferred('cmds.loadPlugin("AbcExport.mll",quiet=True)')
cmds.evalDeferred('cmds.loadPlugin("AbcImport.mll",quiet=True)')

shelfDir = "K:/CodeRepo/Maya/shelves/"
user = os.environ.get( "USERNAME" )
localShelves = "C:/Users/" + user + "/Documents/maya/2014-x64/prefs/shelves/"
shelves = os.listdir(shelfDir)
for shelf in shelves:     
    shutil.copyfile(shelfDir + shelf, localShelves + shelf) 