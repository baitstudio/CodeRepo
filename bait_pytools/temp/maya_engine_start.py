import sys
sys.path.append('Z:/_CORE/Tank/tank/install/core/python')

import tank
tk = tank.tank_from_path('Z:/_CORE/Tank/00719_grandpa')

dirPath='Z:/WORK/00719_grandpa/assets/Characters/Grandpa/work/Rig'
ctx = tk.context_from_path(dirPath)

engine = tank.platform.start_engine('tk-maya', tk, ctx)
engine.init_app()
