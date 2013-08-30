print 'connecting to shotgun...'

import shotgun_api3 as shotgun

sg=shotgun.Shotgun('https://bait.shotgunstudio.com/', 'thumb_uploader', '2a31b48f3b39e7afc3da36d425aa8ef65ba26ec8')

fields = ['sg_path_to_frames','image','code']
project_id = 99
filters = [
    ['project','is',{'type':'Project','id':project_id}],
    ['sg_category','is','Reference']
    ]

elements=sg.find("Element",filters,fields)


elementsThumbless=[]
for element in elements:

    if element['sg_path_to_frames']!=None and element['image']==None:

        elementsThumbless.append(element)


total=len(elementsThumbless)
if total!=0:

    for element in elementsThumbless:

        count=elementsThumbless.index(element)+1

        thumbnail = element['sg_path_to_frames']
        sg.upload_thumbnail("Element",element['id'],thumbnail)

        print 'Done "%s",%s of %s' % (element['code'],str(count),str(total))
else:
    print 'No thumbless elements found!'

raw_input("press any key to exit")
