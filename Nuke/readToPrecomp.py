import nuke
import sys

if len ( sys.argv ) != 4:
    print 'Usage: NUKE readToPrecomp.py <nuke_script> <read_path> <precomp_path>'
    sys.exit(-1)

nuke_script = sys.argv[1]
read_path = sys.argv[2].replace('\\','/')
precomp_path = sys.argv[3].replace('\\','/')

nuke.scriptOpen(nuke_script)

readNode=None
for node in nuke.allNodes():
    if node.Class() == 'Read':
        if node['file'].value() == read_path:
            readNode=node

if readNode:
    
    #getting read node data before deletion
    xpos = readNode['xpos'].value()
    ypos = readNode['ypos'].value()

    dependent = readNode.dependent()

    nuke.delete(readNode)
    
    #create and setup precomp
    precomp=nuke.createNode('Precomp')

    precomp['file'].setValue(precomp_path)
    precomp['xpos'].setValue(xpos)
    precomp['ypos'].setValue(ypos)

    for node in dependent:
        node.setInput(0,precomp)

nuke.scriptSave(nuke_script)