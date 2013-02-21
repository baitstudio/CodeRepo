import os
import maya.cmds as cmds
import maya.mel as mel
from pymel.all import *

def testModule(var):
    print var

############### Prepare Cloth simulation
'''
grandpa = ['grandpa', 'test']
clothes = ['shirt', 'pants']
'''
#Make Cloth
def prepareClothSim(active, passive): 
 
    select(active)
    activeObj = ls(sl=True)   

    select(passive)
    passiveObj = ls(sl=True)
    
    for obj in activeObj:
        select(obj)
        rigidObj = mel.eval('''makeCollideNCloth;''')
        PyNode(rigidObj[0]).getParent().rename("Passive_" + obj)
        
    for obj in passiveObj:
        select(obj)
        clothObj = mel.eval('''createNCloth 0;''')
        PyNode(clothObj[0]).getParent().rename("Cloth_" + obj)
        
#######################################################################

###########  Alembic Import and export

'''
filename='Z:/Bait/grandpa/WORK/development/3D/cache/alembic/man_cartwheel.abc'
nodes='grandpa'
'''
        
def abcImport(filename, nodes):
    cmds.AbcImport(filename, mode="import", ct=nodes, crt=True);
    
#######################################################################


