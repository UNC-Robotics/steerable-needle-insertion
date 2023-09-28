import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# LoadSegmentations
#

class LoadSegmentations(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Load Segmentations" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Needle Interface"]
    self.parent.dependencies = []
    self.parent.contributors = ["UNC Computational Robotics"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# LoadSegmentationsWidget
#

class LoadSegmentationsWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    self.initVariables()
    self.initUI()

  def initVariables(self):

    self.minor_version = slicer.app.mainApplicationMinorVersion
    self.logic = LoadSegmentationsLogic()

    self.defaultInputFolder = os.path.dirname(os.path.abspath(__file__))
    self.inputFolder = ''
    self.segmentationFolder = ''

    # Create segment editor to get access to effects.
    self.segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    self.segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    self.segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    self.segNodes = []


  def initUI(self):
    collapsibleButton = ctk.ctkCollapsibleButton()
    collapsibleButton.text = "Load Segmentations"
    self.layout.addWidget(collapsibleButton)
    formLayout = qt.QFormLayout(collapsibleButton)

    # set workspace
    self.SetWorkSpaceButton = qt.QPushButton("Set workspace")
    self.SetWorkSpaceButton.toolTip = "Select current experiment data" 
    self.SetWorkSpaceButton.enabled = True
    self.SetWorkSpaceButton.connect('clicked(bool)', self.onSetWorkSpaceClicked)

    # load segmentations
    self.LoadSegmentationsButton = qt.QPushButton("Load segmentations")
    self.LoadSegmentationsButton.enabled = False
    self.LoadSegmentationsButton.connect('clicked(bool)', self.onLoadSegmentationsButton)

    # visibility checkboxes for each segmentation
    self.showRegionSegmentationCheck = qt.QCheckBox("Region")
    self.showRegionSegmentationCheck.enabled = False
    self.showRegionSegmentationCheck.setChecked(False)
    self.showRegionSegmentationCheck.connect('stateChanged(int)',self.onShowRegionChecked)

    self.showBronchSegmentationCheck = qt.QCheckBox("Bone")
    self.showBronchSegmentationCheck.enabled = False
    self.showBronchSegmentationCheck.setChecked(False)
    self.showBronchSegmentationCheck.connect('stateChanged(int)',self.onShowBronchChecked)

    self.showVesselSegmentationCheck = qt.QCheckBox("Vessel")
    self.showVesselSegmentationCheck.enabled = False
    self.showVesselSegmentationCheck.setChecked(False)
    self.showVesselSegmentationCheck.connect('stateChanged(int)',self.onShowVesselChecked)

    # display layout
    formLayout.addRow(self.createHLayout([self.SetWorkSpaceButton, self.LoadSegmentationsButton]))
    formLayout.addRow(self.createHLayout([self.showRegionSegmentationCheck, self.showBronchSegmentationCheck, self.showVesselSegmentationCheck]))
    self.layout.addStretch(1)


  def cleanup(self):
    # To Do!!!!!!!!! Idk how to delete the segmentation nodes
    pass


  def createHLayout(self, elements):
    rowLayout = qt.QHBoxLayout()
    for element in elements:
        rowLayout.addWidget(element)
    return rowLayout


  def onSetWorkSpaceClicked(self):
    print("Please set work space directory first!")

    # interactive folder selection
    self.inputFolder = str(qt.QFileDialog.getExistingDirectory(None, 'Work space', self.defaultInputFolder, qt.QFileDialog.ShowDirsOnly)) + "/"

    # if (not os.path.exists(self.inputFolder + "Segmentation")):
    #     print ("No Segmentation folder in the current workspace found. Please try again!")
    #     return

    self.segmentationFolder = self.inputFolder 
    self.LoadSegmentationsButton.enabled = True
    

  def onLoadSegmentationsButton(self):
    if not os.path.exists(self.segmentationFolder):
        print (self.segmentationFolder + " does not exist! Cannot load segmentations!")
        return

    success = True
    segmentations=["Ribs", "Vessels", "LiverTissue"]
    colors=[[244.0/255,170.0/255,147.0/255], \
            [1, 0, 0], [0.85, 0.8, 0.8], \
            [34.0/255,74.0/255,235.0/255], \
            [128.0/255,174.0/255,128.0/255]] #beige, red, greyish, dark blue
    opacity=[1.0, 0.5, 0.2, 0.5, 0.5]
    for i in range(len(segmentations)):
        if not os.path.exists(self.segmentationFolder + segmentations[i] + ".nii"):
            print (segmentations[i] + " does not exist! Skip!")
            success = False
            continue
        segNode = self.createSegmentation(segmentations[i], colors[i], opacity[i])
        if segNode is not None:
            self.segNodes.append(segNode)

    # reset the 3D view to the segmentations
    layoutManager = slicer.app.layoutManager().threeDWidget(0).threeDView()
    layoutManager.resetFocalPoint()

    if not success:
        print("Not all segmentations loaded successfully, please check and retry!")

    self.showRegionSegmentationCheck.enabled = True
    self.showRegionSegmentationCheck.setChecked(True)

    self.showBronchSegmentationCheck.enabled = True
    self.showBronchSegmentationCheck.setChecked(True)

    self.showVesselSegmentationCheck.enabled = True
    self.showVesselSegmentationCheck.setChecked(True)

    self.segmentations_loaded = True


  def onShowSegmentationChecked(self):
    showSeg = False
    if self.showSegmentationCheck.isChecked():
        showSeg = True

    for node in self.logic.segNodes:
        node.GetDisplayNode().SetVisibility(showSeg)

  def onShowRegionChecked(self):
    node = self.segNodes[2]
    node.GetDisplayNode().SetVisibility(self.showRegionSegmentationCheck.isChecked())

  def onShowBronchChecked(self):
    node = self.segNodes[0]
    node.GetDisplayNode().SetVisibility(self.showBronchSegmentationCheck.isChecked())

  def onShowVesselChecked(self):
    node = self.segNodes[1]
    node.GetDisplayNode().SetVisibility(self.showVesselSegmentationCheck.isChecked())

  def createSegmentation(self, name, color, opacity):  
    filename = name + ".nii"
    if self.minor_version <=10:
      volumeNode = slicer.util.loadVolume(self.segmentationFolder + filename)

    volumeArray = slicer.util.arrayFromVolume(volumeNode)
    if volumeArray.max() < 255:
        return None

    # Create segmentation
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(volumeNode)
    addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment(name)

    # Create segment editor to get access to effects
    self.segmentEditorWidget.setMRMLSegmentEditorNode(self.segmentEditorNode)
    self.segmentEditorWidget.setSegmentationNode(segmentationNode)
    self.segmentEditorWidget.setSourceVolumeNode(volumeNode)

    # Thresholding
    self.segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = self.segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold","125")
    effect.setParameter("MaximumThreshold","256")
    effect.self().onApply()

    segmentationNode.CreateClosedSurfaceRepresentation()
    segmentationNode.GetDisplayNode().SetOpacity3D(opacity)
    segmentation = segmentationNode.GetSegmentation()

    # https://www.slicer.org/wiki/Documentation/4.5/Extensions/Reporting
    segment = segmentation.GetSegment(name)
    segment.SetColor(color)

    return segmentationNode

#
# LoadSegmentationsLogic
#

class LoadSegmentationsLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
        self.initVariables()


  def initVariables(self):
    self.segNodes = []


  def cleanup(self):
    for s in self.segNodes:
      slicer.mrmlScene.RemoveNode(s)
  
  def loadSeg(self, workspace):

    instance = LoadSegmentationsWidget()
    
    instance.onSetWorkSpaceClicked()

    instance.onLoadSegmentationsButton()    


class LoadSegmentationsTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_LoadSegmentations1()

  def test_LoadSegmentations1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = LoadSegmentationsLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
