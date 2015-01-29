import os

from PySide import QtGui
import hiero

def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]

def try_int(s):
    "Convert to integer if possible."
    try:
        return int(s)
    except:
        return s


def natsort_key(s):
    "Used internally to get a tuple by which s is sorted."
    import re
    return map(try_int, re.findall(r'(\d+|\D+)', s))


def natcmp(a, b):
    "Natural string comparison, case sensitive."
    return cmp(natsort_key(a), natsort_key(b))


def natcasecmp(a, b):
    "Natural string comparison, ignores case."
    return natcmp(a.lower(), b.lower())


def natsort(seq, cmpl=natcmp):
    "In-place natural string sort."
    seq.sort(cmpl)


def natsorted(seq, cmpl=natcmp):
    "Returns a copy of seq, sorted by natural string sort."
    import copy
    temp = copy.copy(seq)
    natsort(temp, cmpl)
    return temp

class FlagUpdatesMenu:

    def __init__(self):
        hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)
        self._flagUpdates = self.createMenuAction("Flag Updates", self.flagUpdates)

    def createMenuAction(self, title, method):
        action = QtGui.QAction(title,None)
        action.triggered.connect( method )
        return action

    def eventHandler(self, event):
        event.menu.addAction(self._flagUpdates)

    def flagUpdates(self):
        selection = hiero.ui.activeView().selection()

        if len(selection)==0:
            return None

        for bin in selection:
            #getting updatable clips
            manualClips = []
            for clip in bin.clips():
                clip.maxVersion()

                file = None
                try:
                    file = clip.activeItem().mediaSource().fileinfos()[0]
                except:
                    pass

                if file:
                    folder = os.path.dirname(file.filename())
                    currentVersion = os.path.basename(folder)
                    parentFolder = os.path.abspath(os.path.join(folder, os.pardir))
                    latestVersion = natsorted(get_immediate_subdirectories(parentFolder))[-1]
                    if currentVersion != latestVersion:
                        data = {'clip':clip, 'currentVersion':currentVersion, 'latestVersion':latestVersion}
                        manualClips.append(data)
            
            infoBox = QtGui.QMessageBox(hiero.ui.mainWindow())
            infoBox.setIcon(QtGui.QMessageBox.Information)
            infoBox.setModal(False)
            if len(manualClips) <=0:
                infoBox.setText("No Clips needs manual updating in %s" % bin)
                infoBox.setInformativeText("All clips are using the latest version!")
            else:
                infoBox.setText("Some Clips weren't updated in %s, and needs manual attention!" % bin)
                infoBox.setInformativeText("Show Details for more info.")
                msg = ''
                for clip in manualClips:
                    msg += 'Clip: %s, Current Version: %s, Latest Version: %s\n' % (clip['clip'].name(), clip['currentVersion'], clip['latestVersion'])
                infoBox.setDetailedText(msg)
            
            infoBox.show()

ubm = FlagUpdatesMenu()
