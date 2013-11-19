import os, sys, subprocess, traceback
import nuke, nukescripts

def GetRepositoryRoot():
    # On OSX, we look for the DEADLINE_PATH file. On other platforms, we use the environment variable.
    if os.path.exists( "/Users/Shared/Thinkbox/DEADLINE_PATH" ):
        with open( "/Users/Shared/Thinkbox/DEADLINE_PATH" ) as f: deadlineBin = f.read().strip()
        deadlineCommand = deadlineBin + "/deadlinecommand"
    else:
        try:
            deadlineBin = os.environ['DEADLINE_PATH']
        except KeyError:
            return ""
    
        if os.name == 'nt':
            deadlineCommand = deadlineBin + "\\deadlinecommand.exe"
        else:
            deadlineCommand = deadlineBin + "/deadlinecommand"
    
    startupinfo = None
    if os.name == 'nt' and hasattr( subprocess, 'STARTF_USESHOWWINDOW' ): #not all python versions have this
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    proc = subprocess.Popen([deadlineCommand, "-root"], cwd=deadlineBin, stdout=subprocess.PIPE, startupinfo=startupinfo)
    
    root = proc.stdout.read()
    root = root.replace("\n","").replace("\r","")
    return root

def main():
    # Get the repository root
    path = GetRepositoryRoot()
    if path != "":
        path += "/submission/Nuke/Main"
        path = path.replace( "\\", "/" )
        
        # Add the path to the system path
        if path not in sys.path :
            print "Appending \"" + path + "\" to system path to import SubmitNukeToDeadline module"
            sys.path.append( path )

        # Import the script and call the main() function
        try:
            import SubmitNukeToDeadline
            SubmitNukeToDeadline.SubmitToDeadline( path )
        except:
            print traceback.format_exc()
            nuke.message( "The SubmitNukeToDeadline.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository." )
    else:
        nuke.message( "The SubmitNukeToDeadline.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is set in the DEADLINE_PATH environment variable, and that the Deadline Client has been configured to point to a valid Repository." )
