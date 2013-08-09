import nuke, re


def Mocha_AE_Import():

  #Open textfile with tracking data
  
  textfile = nuke.getFilename('Open Mocha File', '*.txt')
  
  if textfile:
      text = open(textfile, 'r')
  
  
      #Create CornerPin node
  
      myNode = nuke.createNode('CornerPin2D')
      myNode.knob('label').setValue('Mocha Track')
  
  
      #Initialize variables
  
      corner_number = 0
  
  
      #Work through textfile
  
      for line in text:
          line = re.split(r'[ \t\n]', line.rstrip('\n'))
  
          if len(line) > 2:
  
  
              #Use tracking data for animation
  
              if str(line[1]).isdigit():
                  time = float(line[1])
                  x_value = float(line[2])
                  y_value = height - float(line[3])
  
                  myNode.knob(corner).setValueAt(x_value, time, 0)
                  myNode.knob(corner).setValueAt(y_value, time, 1)
  
  
              #Get height of tracked video
  
              elif str(line[2]) == 'Height':
                  height = float(line[3])
  
  
              #Pick corner
  
              elif str(line[1]) == 'ADBE':
                  corner_number = corner_number + 1
                  corner = 'to' + str(corner_number)
  
                  if corner == 'to3':
                      corner = 'to4'
  
                  elif corner == 'to4':
                      corner = 'to3'
  
                  myNode.knob(corner).setAnimated()