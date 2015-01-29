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


class ProjectMaxVersionMenu:

    def __init__(self):
        hiero.core.events.registerInterest("kShowContextMenu/kBin",
                                           self.eventHandler)
        self._projectMaxVersion = self.createMenuAction("Project Max Version",
                                                        self.projectMaxVersion)

    def createMenuAction(self, title, method):
        action = QtGui.QAction(title, None)
        action.triggered.connect(method)
        return action

    def eventHandler(self, event):
        event.menu.addAction(self._projectMaxVersion)

    def projectMaxVersion(self):

        selection = hiero.ui.activeView().selection()

        if len(selection) == 0:
            return None

        for selectionItem in selection:
            if isinstance(selectionItem, hiero.core.Bin):
                updates = []
                project = selectionItem.project()
                for item in hiero.core.findItemsInProject(project,
                                                          'TrackItem'):

                    # removing any update tags
                    for tag in item.tags():
                        if tag.name() == 'updated':
                            item.removeTag(tag)

                    currentVersion = item.currentVersion()
                    if currentVersion:
                        binItem = currentVersion.parent()

                        file = binItem.activeItem()
                        file = file.mediaSource().fileinfos()[0]
                        folder = os.path.dirname(file.filename())
                        currentVersion = os.path.basename(folder)

                        check = True
                        try:
                            temp = int(currentVersion.replace('v', ''))
                            currentVersionNumber = temp
                        except:
                            check = False

                        if check:
                            pDir = os.path.join(folder, os.pardir)
                            pDir = os.path.abspath(pDir)
                            latestVersion = get_immediate_subdirectories(pDir)
                            latestVersion = natsorted(latestVersion)[-1]
                            temp = int(latestVersion.replace('v', ''))
                            latestVersionNumber = temp
                            if currentVersionNumber < latestVersionNumber:
                                temp = file.filename().replace(currentVersion,
                                                               latestVersion)
                                newFilename = temp
                                newClip = hiero.core.Clip(newFilename)
                                newVersion = hiero.core.Version(newClip)
                                binItem.addVersion(newVersion)
                                binItem.maxVersion()
                                item.maxVersion()

                                data = {'clip': binItem,
                                        'oldVersion': currentVersion,
                                        'newVersion': latestVersion}
                                updates.append(data)

                                tag = hiero.core.Tag('updated')
                                item.addTag(tag)

                infoBox = QtGui.QMessageBox(hiero.ui.mainWindow())
                infoBox.setIcon(QtGui.QMessageBox.Information)
                if len(updates) == 0:
                    infoBox.setText('No Clips were updated!')
                else:
                    infoBox.setText('Some Clips were updated!')
                    infoBox.setInformativeText("Show Details for more info.")
                    msg = ''
                    for clip in updates:
                        msg += 'Clip: %s,' % clip['clip'].name()
                        msg += 'Old Version: %s, ' % clip['oldVersion']
                        msg += 'New Version: %s\n' % clip['newVersion']
                    infoBox.setDetailedText(msg)

                infoBox.show()
            else:
                infoBox = QtGui.QMessageBox(hiero.ui.mainWindow())
                infoBox.setIcon(QtGui.QMessageBox.Information)

                msg = '"Project Max Version" works on Bins only.'
                msg += 'Please select a Bin'
                infoBox.setText(msg)
                infoBox.show()

pmvm = ProjectMaxVersionMenu()
