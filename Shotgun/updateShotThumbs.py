import os

import shotgun_api3 as shotgun
import config

#connecting to shotgun and finding projects
print 'connecting to shotgun...\n'

sg=shotgun.Shotgun(config.base_url, config.script_name, config.api_key)

fields = ['name']
filters=[]
projects=sg.find("Project",filters,fields)

#presenting the user with the projects
for project in projects:
    
    print '%s: id=%s' % (project['name'],project['id'])

print '\n\n'

#user input
project_id=int(raw_input('Enter Project ID:'))
episode_code=raw_input('Enter Episode Name:')

#collecting shots
fields = []
filters = [['project','is',{'type':'Project','id':project_id}],
           ['code','is',episode_code]]
episode=sg.find_one("Scene",filters,fields)

if episode!=None:

    fields = ['sg_path_to_thumbs','code']
    filters = [['sg_scene','is',{'type':'Scene','id':episode['id']}]]
    shots=sg.find("Shot",filters,fields)
    
    #processing shots
    total=len(shots)
    for shot in shots:
        
        count=shots.index(shot)+1
        
        thumb_path=shot['sg_path_to_thumbs']
        if thumb_path!=None:
            
            thumbs=os.listdir(thumb_path)
            
            sorted_thumbs=[]
            for thumb in sorted(thumbs):
                sorted_thumbs.append(thumb)
            
            try:
                middle_thumb=sorted_thumbs[int(len(sorted_thumbs)/2)]
                
                middle_thumb_path=os.path.join(thumb_path,middle_thumb)
                
                sg.upload_thumbnail("Shot",shot['id'],middle_thumb_path)
                
                print 'Done "%s",%s of %s' % (shot['code'],str(count),str(total))
            except:
                
                print 'FAILED "%s",%s of %s' % (shot['code'],str(count),str(total))
else:
    print 'Could not find episode: "%s"' % episode_code

raw_input("press any key to exit")