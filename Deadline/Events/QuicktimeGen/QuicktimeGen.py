import re

from System.IO import *
from System.Text import *

from Deadline.Events import *
from Deadline.Scripting import *

######################################################################
## This is the function that Deadline calls to get an instance of the
## main DeadlineEventListener class.
######################################################################
def GetDeadlineEventListener():
    return MyEvent()


######################################################################
## This is the main DeadlineEventListener class for MyEvent.
######################################################################
class MyEvent(DeadlineEventListener):
    def __init__(self):
        self.OnJobFinishedCallback += self.OnJobFinished

    def OnJobFinished(self, job):

        movieSettings = self.GetConfigEntryWithDefault("QTSettings", "").strip()

        # Only submit a QT job for finished Nuke jobs, and only if a QT settings file has been set.
        if job.JobExtraInfo0 != "qt":
            return

        outputDirectories = job.JobOutputDirectories
        outputFilenames = job.JobOutputFileNames
        paddingRegex = re.compile("[^\\?#]*([\\?#]+).*")

        # Submit a QT job for each output sequence.
        for i in range(0, len(outputFilenames)):

            outputDirectory = outputDirectories[i]
            outputFilename = outputFilenames[i]
            outputPath = Path.Combine(outputDirectory, outputFilename).replace("//", "/")

            # Swap out the padding character for an actual frame.
            m = re.match(paddingRegex, outputPath)
            if ( m != None):
                padding = m.group(1)
                frame = StringUtils.ToZeroPaddedString(job.JobFramesList[0], len(padding), False)
                outputPath = outputPath.replace(padding, frame)

            inputFilename = outputPath
            movieFilename = Path.ChangeExtension(FrameUtils.GetFilenameWithoutPadding(inputFilename), ".mov")
            movieName = Path.GetFileNameWithoutExtension(movieFilename)
            movieFrames = job.JobFrames

            # Create job info file.
            jobInfoFilename = Path.Combine(ClientUtils.GetDeadlineTempPath(), "quicktime_job_info.job")
            writer = StreamWriter(jobInfoFilename, False, Encoding.Unicode)
            writer.WriteLine("Plugin=Quicktime")
            writer.WriteLine("Name=%s" % movieName)
            writer.WriteLine("Comment=Auto-submitted QT")
            writer.WriteLine("Department=%s" % job.JobDepartment)
            writer.WriteLine("Pool=%s" % job.JobPool)
            writer.WriteLine("Group=%s" % job.JobGroup)
            writer.WriteLine("Priority=%s" % job.JobPriority)
            writer.WriteLine("MachineLimit=1")
            writer.WriteLine("Frames=%s" % movieFrames)
            writer.WriteLine("ChunkSize=100000")
            writer.WriteLine("OutputFilename0=%s" % movieFilename)
            writer.Close()

            # Create plugin info file.
            pluginInfoFilename = Path.Combine(ClientUtils.GetDeadlineTempPath(), "quicktime_plugin_info.job")
            writer = StreamWriter(pluginInfoFilename, False, Encoding.Unicode)
            writer.WriteLine("InputImages=%s" % inputFilename)
            writer.WriteLine("OutputFile=%s" % movieFilename)
            writer.WriteLine("FrameRate=25")
            writer.WriteLine("Codec=QuickTime Movie")
            writer.Close()

            # Now submit the job.
            ClientUtils.ExecuteCommand((jobInfoFilename, pluginInfoFilename, movieSettings))

