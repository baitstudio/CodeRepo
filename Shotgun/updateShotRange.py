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

    fields = ['sg_path_to_plate','code']
    filters = [['sg_scene','is',{'type':'Scene','id':episode['id']}]]
    shots=sg.find("Shot",filters,fields)
    
    #processing shots
    total=len(shots)
    for shot in shots:
        
        count=shots.index(shot)+1
        
        plate_path=shot['sg_path_to_plate']
        
        
        if plate_path!=None:
            if os.path.exists(plate_path):
            
                plates=os.listdir(plate_path)
                
                sorted_plates=[]
                for plate in sorted(plates):
                    sorted_plates.append(plate)
                
                try:
                    startFrame=int(sorted_plates[0].split('.')[1])
                    endFrame=int(sorted_plates[-1].split('.')[1])
                    duration=len(sorted_plates)
                    
                    data={'sg_cut_in':startFrame,'sg_cut_out':endFrame,
                          'sg_cut_duration':duration}
                    sg.update("Shot", shot['id'], data)
                
                    print 'Done "%s",%s of %s' % (shot['code'],str(count),str(total))
                except:
                    
                    print 'FAILED "%s",%s of %s' % (shot['code'],str(count),str(total))
            else:
                print 'Plates directory doesnt exist for %s' % shot
        else:
            print 'Plates directory doesnt exist for %s' % shot
else:
    print 'Could not find episode: "%s"' % episode_code

raw_input("press any key to exit")