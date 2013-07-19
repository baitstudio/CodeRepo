import os
import sys
sys.path.append('Z:/_CORE/Tank/tank/install/core/python')

import tank
import maya.cmds as cmds

filePath=cmds.file(q=True,sn=True)
dirPath=os.path.dirname(filePath)
tk = tank.tank_from_path(dirPath)
#ctx = tk.context_from_path(path)


template_path=tk.templates['maya_shot_work']
data=template_path.get_fields(filePath)

fields={"Episode":"000_dummy", "Shot":"0000", "Step":"Track", "name":"awesomeTrack", "version":1}
#print template_path.apply_fields(fields)
#print tank.util.find_publish(tk,filePath)
print tk.context_from_entity('TankPublishedFile', 32)

#engine = tank.platform.start_engine('tk-maya', tk, ctx)
#engine.init_app()

#print tank.platform.current_engine()