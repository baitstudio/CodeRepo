# An example which shows how to spawn multiple exports from a Sequence from right-click menu in the Project Bin
import os.path
import hiero.core
import hiero.ui
import glob

from PySide.QtGui import *
from PySide.QtCore import *

class MultiExportAction(QAction):

  class MultiExportDialog(QDialog):
    def __init__(self,  selection, selectedPresets, parent=None):
      super(MultiExportAction.MultiExportDialog, self).__init__(parent)
      self.setWindowTitle("MultiExport")
      self.setSizeGripEnabled(True)

      self._exportTemplate = None

      layout = QVBoxLayout()
      formLayout = QFormLayout()

      presetNames = [preset.name() for preset in hiero.core.taskRegistry.localPresets()]

      # List box for track selection
      presetListModel = QStandardItemModel()
      presetListView = QListView()
      presetListView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
      presetListView.setModel(presetListModel)
      for preset in presetNames:
        item = QStandardItem(preset)
        if preset in selectedPresets:
          item.setCheckState(Qt.Checked)
        else:
          item.setCheckState(Qt.Unchecked)

        item.setCheckable(True)
        presetListModel.appendRow(item)

      self._presetListModel = presetListModel
      presetListView.clicked.connect(self.presetSelectionChanged)

      formLayout.addRow("Presets:", presetListView)

      layout.addLayout(formLayout)

      self._exportTemplate = hiero.core.ExportStructure2()
      self._exportTemplateViewer = hiero.ui.ExportStructureViewer(self._exportTemplate)

      layout.addWidget(self._exportTemplateViewer)



      # Add the standard ok/cancel buttons, default to ok.
      self._buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
      self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setText("Export")
      self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
      self._buttonbox.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Executes exports on selection for each selected preset")
      self._buttonbox.accepted.connect(self.acceptTest)
      self._buttonbox.rejected.connect(self.reject)
      layout.addWidget(self._buttonbox)

      self.setLayout(layout)

    def acceptTest(self):
      self.accept()


    def presetSelectionChanged (self, index):
      if index.isValid():
        item = self._presetListModel.itemFromIndex(index)
        presetName = item.text()
        checked = item.checkState() == Qt.Checked

        self._preset = hiero.core.taskRegistry.processorPresetByName(presetName)
        self._exportTemplate.restore(self._preset._properties["exportTemplate"])
        if self._preset._properties["exportRoot"] != "None":
          self._exportTemplate.setExportRootPath(self._preset._properties["exportRoot"])
        self._exportTemplateViewer.setExportStructure(self._exportTemplate)
        self._resolver = self._preset.createResolver().addEntriesToExportStructureViewer(self._exportTemplateViewer)

    def presets(self):
      presets = []
      for row in range(0, self._presetListModel.rowCount()):
        item = self._presetListModel.item(row)
        presetName = item.text()
        checked = item.checkState() == Qt.Checked
        if checked:
          presets.append(presetName)

      return presets

  def __init__(self):
      QAction.__init__(self, "Multi Export", None)
      self.triggered.connect(self.doit)
      hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)
      self._selectedPresets = []

  class CustomItemWrapper:
    def __init__ (self, item):
      self._item = item

      if isinstance(self._item, hiero.core.BinItem):
        self._item = self._item.activeItem()


    def isNull (self):
      return self._item == None

    def sequence (self):
      if isinstance(self._item, hiero.core.Sequence):
        return self._item
      return None

    def clip (self):
      if isinstance(self._item, hiero.core.Clip):
        return self._item
      return None

    def trackItem (self):
      if isinstance(self._item, hiero.core.TrackItem):
        return self._item
      return None

    def name (self):
      return self._item.name()

  def doit(self):

    # Prepare list of selected items for export
    selection = [MultiExportAction.CustomItemWrapper(item) for item in hiero.ui.activeView().selection()]

    # Create dialog
    dialog = self.MultiExportDialog(selection, self._selectedPresets)
    # If dialog returns true
    if dialog.exec_():
      # Grab list of selected preset names
      self._selectedPresets = dialog.presets()
      for presetName in self._selectedPresets:
        # Grab preset from registry
        preset = hiero.core.taskRegistry.processorPresetByName(presetName)
        # Launch export
        hiero.core.taskRegistry.createAndExecuteProcessor(preset, selection, "Local")


  def eventHandler(self, event):
    if not hasattr(event.sender, 'selection'):
      # Something has gone wrong, we shouldn't only be here if raised
      # by the timeline view which will give a selection.
      return

    s = event.sender.selection()
    if s is None:
      s = () # We disable on empty selection.
    title = "Multi Export"
    self.setText(title)
    if len(s)>0:
      event.menu.addAction(self)

# Instantiate the action to get it to register itself.
multiExportAction = MultiExportAction()
