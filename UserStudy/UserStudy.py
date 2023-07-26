import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import math
import numpy as np
import Resources.UI.Layouts as layouts
import re
import time
import LoadSegmentations

_EPS = np.finfo(float).eps * 4.0
#
# UserStudy
#


class UserStudy(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = (
            "UserStudy"  # TODO make this more human readable by adding spaces
        )
        self.parent.categories = ["User Study"]
        self.parent.dependencies = []
        self.parent.contributors = [
            "Janine Hoelscher"
        ]  # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
        # self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""  # replace with organization, grant and thanks.


#
# UserStudyWidget
#


class UserStudyWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    ##########
    # UI Setup#
    ##########

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.scene = slicer.mrmlScene
        self.initVariables()
        self.initUI()

    def initVariables(self):
        self.logic = UserStudyLogic()
        self.inputFolder = (
            os.path.dirname(os.path.abspath(__file__)) + "/Resources/Data/"
        )  # Hardcode input path here for testing purposes
        self.composite_needle = None
        self.eventCount = 0
        self.eventChanged = False

        self.coloredAngle = []
        self.coloredAngleModel = None
        self.coloredRegion = []
        self.coloredRegionRadius = None
        self.insertionPose = []
        self.insertionPoseLength = None

        print(self.inputFolder)

        defaultTimeInterval = 20
        self.timer = qt.QTimer()
        self.timer.setInterval(defaultTimeInterval)
        self.timer.connect("timeout()", self.onTimeOut)

        self.needleMovementSelected = False
        self.needle_update = False
        self.needle_file = self.inputFolder
        self.needle_pose_index = 0
        self.needle_data = []

        # hardcoded values for recorded data
        self.needle_registration = np.eye(4)
        self.needle_registration = np.array([[0,-1,0,236.0],
                                            [-1,0,0,170.0],
                                            [0,0,-1,47.0],
                                            [0,0,0,1]])
        self.stream_live_data = False

    def initUI(self):
        # load environment visualization elements
        self.userSwitched = False
        self.viewSelected = False
        self.viewSelectedLayout = layouts.VIEW_MAP[""]
        self.currentLayout = 100

        self.loadEnvironmentButton = qt.QPushButton("Load Environment")
        self.loadEnvironmentButton.toolTip = "Load experiment environment visualization"
        self.loadEnvironmentButton.enabled = True
        self.loadEnvironmentButton.connect(
            "clicked(bool)", self.onLoadEnvironmentClicked
        )

        self.clearEnvironmentButton = qt.QPushButton("Clear Environment")
        self.clearEnvironmentButton.toolTip = (
            "Clear experiment environment visualization"
        )
        self.clearEnvironmentButton.enabled = True
        self.clearEnvironmentButton.connect(
            "clicked(bool)", self.onClearEnvironmentClicked
        )

        self.moveNeedleButton = qt.QPushButton("Move Needle")
        self.moveNeedleButton.toolTip = ""
        self.moveNeedleButton.enabled = False
        self.moveNeedleButton.connect("clicked(bool)", self.onMoveNeedleClicked)

        self.StartButton = qt.QPushButton("Start needle")
        self.StartButton.toolTip = "Start/stop needle movement"
        self.StartButton.enabled = False
        self.StartButton.connect("clicked(bool)", self.onStartNeedleClicked)

        self.needleSettings = qt.QLabel("Needle Movement Settings")
        self.needleSettings.enabled = False
        self.needleSettings.setAlignment(qt.Qt.AlignCenter)

        self.dropDownMovement = qt.QComboBox()
        self.dropDownMovementLabel = qt.QLabel("Select recording: ")
        self.dropDownMovementLabel.enabled = False
        self.dropDownMovementLabel.setAlignment(qt.Qt.AlignCenter)
        self.dropDownMovement.enabled = False
        self.dropDownMovement.addItems(
            [
                "",
                "recording1.txt",
                "recording2.txt",
                "recording3.txt",
                "recording4.txt",
                "recording5.txt",
            ]
        )
        for index in range(self.dropDownMovement.model().rowCount()):
            self.dropDownMovement.setItemData(
                index, qt.Qt.AlignCenter, qt.Qt.TextAlignmentRole
            )
        self.dropDownMovement.currentIndexChanged.connect(self.onDropDownMovementSelect)

        self.streamingCheckBox = qt.QCheckBox("Stream data?")
        self.streamingCheckBox.setStyleSheet("margin-left:25%; margin-right:25%;")
        self.streamingCheckBox.setLayoutDirection(qt.Qt.RightToLeft)
        self.streamingCheckBox.setChecked(False)
        self.streamingCheckBox.enabled = False
        self.streamingCheckBox.toggled.connect(self.onStreamingCheck)
        self.streamingCheckBoxWidget = qt.QWidget()
        self.streamingCheckBoxLayout = qt.QHBoxLayout(self.streamingCheckBoxWidget)
        self.streamingCheckBoxLayout.addWidget(self.streamingCheckBox)
        self.streamingCheckBoxLayout.setAlignment(
            self.streamingCheckBox, qt.Qt.AlignCenter
        )

        self.comboDropDownMovement = qt.QWidget()
        self.comboDropDownMovementLayout = qt.QHBoxLayout(self.comboDropDownMovement)
        self.comboDropDownMovementLayout.addWidget(self.dropDownMovementLabel)
        self.comboDropDownMovementLayout.addWidget(self.dropDownMovement)

        self.resetNeedleButton = qt.QPushButton("Reset needle")
        self.resetNeedleButton.toolTip = "Resets needle data"
        self.resetNeedleButton.enabled = False
        self.resetNeedleButton.connect("clicked(bool)", self.onResetNeedleButton)

        self.dropDownViewSelector = qt.QComboBox()
        # self.dropDownViewSelector.setStyleSheet("margin-left:100%; margin-right:100%;")
        self.dropDownViewSelectorLabel = qt.QLabel("Select View: ")
        self.dropDownViewSelectorLabel.enabled = True
        self.dropDownViewSelectorLabel.setAlignment(qt.Qt.AlignCenter)
        self.dropDownViewSelector.enabled = True
        self.dropDownViewSelector.addItems(list(layouts.VIEW_MAP.keys()))
        # for index in range(self.dropDownViewSelector.model().rowCount()):
        #   self.dropDownViewSelector.setItemData(index, qt.Qt.AlignCenter, qt.Qt.TextAlignmentRole)
        self.dropDownViewSelector.currentIndexChanged.connect(self.onDropDownViewSelect)

        self.orderSelect = qt.QLineEdit()
        self.orderSelectLabel = qt.QLabel("Select Order:")
        self.orderSelect.setMaxLength(self.viewSelectedLayout[1])
        self.orderSelect.returnPressed.connect(self.onOrderSelectEnter)

        self.comboViewSelectOrder = qt.QWidget()
        self.comboViewSelectOrderLayout = qt.QHBoxLayout(self.comboViewSelectOrder)
        self.comboViewSelectOrderLayout.addWidget(self.dropDownViewSelector)
        self.comboViewSelectOrderLayout.addWidget(self.orderSelect)
        self.comboViewSelectOrderLayout.setStretch(0, 1)
        self.comboViewSelectOrderLayout.setStretch(1, 1)

        self.toggleVisualizers = qt.QCheckBox("Colored Regions")
        self.toggleVisualizers.setStyleSheet("margin-left:25%; margin-right:25%;")
        self.toggleVisualizers.setLayoutDirection(qt.Qt.RightToLeft)
        self.toggleVisualizers.enabled = False
        self.toggleVisualizers.setChecked(True)
        self.toggleVisualizers.toggled.connect(self.onToggleVisualizers)
        self.toggleVisualizersWidget = qt.QWidget()
        self.toggleVisualizersLayout = qt.QHBoxLayout(self.toggleVisualizersWidget)
        self.toggleVisualizersLayout.addWidget(self.toggleVisualizers)
        self.toggleVisualizersLayout.setAlignment(
            self.toggleVisualizers, qt.Qt.AlignCenter
        )

        self.userStudySection = self.newSection("User Study")
        self.userStudyLayout = self.newHItemLayout(
            self.userStudySection,
            [
                [None, self.dropDownViewSelectorLabel, self.orderSelectLabel],
                [None, self.comboViewSelectOrder],
                [None, self.loadEnvironmentButton],
                [None, self.clearEnvironmentButton],
                [None, self.needleSettings],
                [None, self.streamingCheckBoxWidget, self.comboDropDownMovement],
                [None, self.StartButton, self.resetNeedleButton],
                [None, self.toggleVisualizersWidget],
            ],
        )

        slicer.util.setDataProbeVisible(True)
        slicer.util.setModuleHelpSectionVisible(False)
        slicer.util.setModulePanelTitleVisible(False)
        slicer.util.setPythonConsoleVisible(True)
        slicer.util.setStatusBarVisible(True)
        slicer.util.setToolbarsVisible(False)
        slicer.util.setToolbarsVisible(
            True,
            [
                slicer.util.mainWindow().findChild(
                    qt.QToolBar, "SequenceBrowserToolBar"
                ),
                slicer.util.mainWindow().findChild(qt.QToolBar, "MarkupsToolBar"),
            ],
        )

        self.switchUserShortcut = qt.QShortcut(
            qt.QKeySequence("Ctrl+B"), slicer.util.mainWindow()
        )
        self.switchUserShortcut.connect("activated()", self.switchUser)

        defaultView = "(5) Two Top Three Bottom"

        self.currentLayout = max(slicer.app.layoutManager().layout, self.currentLayout)

        slicer.app.layoutManager().layoutLogic().GetLayoutNode().AddLayoutDescription(
            self.currentLayout + 1, layouts.VIEW_MAP[defaultView][0]("12345")
        )
        slicer.app.layoutManager().setLayout(self.currentLayout + 1)
        self.currentLayout += 1
        slicer.mrmlScene.Clear(False)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutNone)

        # print(self.currentLayout)

        interval = 20

        self.regionColorTimer = qt.QTimer()
        self.regionColorTimer.setInterval(interval)
        self.regionColorTimer.connect("timeout()", self.updateRegionColor)

        self.startAngleColorTimer = qt.QTimer()
        self.startAngleColorTimer.setInterval(interval)
        self.startAngleColorTimer.connect("timeout()", self.updateAngleColor)

        self.spaceBarPress = qt.QShortcut(
            qt.QKeySequence("Space"), slicer.util.mainWindow()
        )
        self.spaceBarPress.connect("activated()", self.eventChange)

        slicer.util.mainWindow().setWindowTitle("User Study")

        for n in range(5):
            viewName = slicer.app.layoutManager().threeDWidget(n).threeDView().mrmlViewNode().GetName()
            if viewName ==  "View1":
                self.View1Controller = slicer.app.layoutManager().threeDWidget(n).threeDController()
                print(f"1: n={n}")
            if viewName ==  "View2":
                self.View2Controller = slicer.app.layoutManager().threeDWidget(n).threeDController()
                print(f"2: n={n}")
            if viewName ==  "View3":
                self.View3Controller = slicer.app.layoutManager().threeDWidget(n).threeDController()
                print(f"3: n={n}")
            if viewName ==  "View4":
                self.View4Controller = slicer.app.layoutManager().threeDWidget(n).threeDController()
                print(f"4: n={n}")
            if viewName ==  "View5":
                self.View5Controller = slicer.app.layoutManager().threeDWidget(n).threeDController()
                print(f": n={n}")

    def eventChange(self):
        if not self.eventChanged:
            with open(self.inputFolder + "timestamps.txt", "w") as file:
                pass
            self.startTime = time.time()
            self.eventChanged = True
        else:
            timePassed = time.time() - self.startTime
            with open(self.inputFolder + "timestamps.txt", "a") as file:
                file.write(f"{timePassed}\n")

        flag = self.eventCount < 15

        if self.eventCount == 0:
            self.startText.SetDisplayVisibility(False)
            self.dropDownViewSelector.setCurrentIndex(8)
            self.orderSelect.setText("1245")
            self.onOrderSelectEnter()
            # self.resetAngle()

        if self.eventCount < 5:
            self.resetRegion()
            self.createInsertionRegion(self.eventCount, flag)
            self.onToggleVisualizers()
            self.regionColorTimer.start()

        if self.eventCount == 5:
            self.resetRegion()
            self.onToggleVisualizers()
            self.dropDownViewSelector.setCurrentIndex(13)
            self.orderSelect.setText("12345")
            self.onOrderSelectEnter()

        if self.eventCount < 10 and self.eventCount >= 5:
            self.resetAngle()
            self.createInsertionAngle(self.eventCount - 5)
            self.createInsertionPose(self.eventCount - 5)
            self.setCamera3()
            self.setCamera3()
            self.onToggleVisualizers()
            self.startAngleColorTimer.start()

        if self.eventCount < 15 and self.eventCount >= 10:
            self.resetRegion()
            self.createInsertionRegion(self.eventCount - 5, flag)
            self.resetAngle()
            self.createInsertionAngle(self.eventCount - 5)
            self.createInsertionPose(self.eventCount - 5)
            self.setCamera3()
            self.onToggleVisualizers()
            self.regionColorTimer.start()
            self.startAngleColorTimer.start()

        if self.eventCount < 30 and self.eventCount >= 15:
            self.phaseTwo()
            self.resetRegion()
            self.createInsertionRegion(self.eventCount - 5, flag)
            self.resetAngle()
            self.createInsertionAngle(self.eventCount - 5)
            self.createInsertionPose(self.eventCount - 5)
            self.setCamera3()
            self.regionColorTimer.start()
            self.startAngleColorTimer.start()

        if self.eventCount == 30:
            self.dropDownViewSelector.setCurrentIndex(0)

        self.eventCount += 1

    def resetRegion(self):
        self.regionColorTimer.stop()
        for node in self.coloredRegion:
            if slicer.mrmlScene.IsNodePresent(node):
                slicer.mrmlScene.RemoveNode(node)
                node = None
        self.coloredRegion = []
        self.coloredRegionRadius = None

    def resetAngle(self):
        self.startAngleColorTimer.stop()
        for node in self.coloredAngle:
            if slicer.mrmlScene.IsNodePresent(node):
                slicer.mrmlScene.RemoveNode(node)
                node = None
        for node in self.insertionPose:
            if slicer.mrmlScene.IsNodePresent(node):
                slicer.mrmlScene.RemoveNode(node)
                node = None
        self.coloredAngle = []
        self.insertionPose = []
        self.insertionPoseLength = None

    def validateOrder(self, text):
        regex = re.compile(f"[1-5]*")
        match = regex.fullmatch(text)
        if match:
            seen = []
            for char in text:
                if char in seen:
                    return False
                seen.append(char)
            return True
        else:
            return False

    def onOrderSelectEnter(self):
        inputText = self.orderSelect.text
        if (
            self.viewSelected
            and self.validateOrder(inputText)
            and len(inputText) == self.viewSelectedLayout[1]
        ):
            self.currentLayout = max(
                slicer.app.layoutManager().layout, self.currentLayout
            )
            slicer.app.layoutManager().layoutLogic().GetLayoutNode().AddLayoutDescription(
                self.currentLayout + 1, self.viewSelectedLayout[0](inputText)
            )
            slicer.app.layoutManager().setLayout(self.currentLayout + 1)
            self.currentLayout += 1
            # print(self.currentLayout)
            self.orderSelect.setStyleSheet("border: 1px solid green;")
            timer = qt.QTimer()
            timer.singleShot(1000, self.changeOrderColor)
        elif not inputText == "":
            self.orderSelect.setStyleSheet("border: 1px solid red;")
            timer = qt.QTimer()
            timer.singleShot(1000, self.changeOrderColor)
        for view in slicer.mrmlScene.GetNodesByClass("vtkMRMLViewNode"):
            view.SetAxisLabelsVisible(False)
            view.SetBoxVisible(False)

    def changeOrderColor(self):
        self.orderSelect.setStyleSheet("")

    def onDropDownViewSelect(self, index):
        text = self.dropDownViewSelector.itemText(index)
        if text == "":
            self.viewSelected = False
            self.viewSelectedLayout = layouts.VIEW_MAP[text]
            self.orderSelect.setMaxLength(self.viewSelectedLayout[1])
            slicer.app.layoutManager().setLayout(
                slicer.vtkMRMLLayoutNode.SlicerLayoutNone
            )
        else:
            self.viewSelectedLayout = layouts.VIEW_MAP[text]
            self.orderSelect.setMaxLength(self.viewSelectedLayout[1])
            self.viewSelected = True
            self.onOrderSelectEnter()

    def switchUser(self):
        # print("ctrl b")
        if self.userSwitched:
            slicer.util.setMenuBarsVisible(True)
            slicer.util.mainWindow().findChild(
                qt.QWidget, "PanelDockWidget"
            ).setVisible(True)
            slicer.util.setToolbarsVisible(
                True,
                [
                    slicer.util.mainWindow().findChild(
                        qt.QToolBar, "SequenceBrowserToolBar"
                    ),
                    slicer.util.mainWindow().findChild(qt.QToolBar, "MarkupsToolBar"),
                ],
            )
            slicer.util.setDataProbeVisible(True)
            slicer.util.setModuleHelpSectionVisible(False)
            slicer.util.setModulePanelTitleVisible(False)
            slicer.util.setPythonConsoleVisible(True)
            slicer.util.setStatusBarVisible(True)
            slicer.util.setViewControllersVisible(True)
            self.userSwitched = False
        else:
            slicer.util.mainWindow().findChild(
                qt.QWidget, "PanelDockWidget"
            ).setVisible(False)
            slicer.util.setMenuBarsVisible(False)
            slicer.util.setDataProbeVisible(False)
            slicer.util.setModuleHelpSectionVisible(False)
            slicer.util.setModulePanelTitleVisible(False)
            slicer.util.setPythonConsoleVisible(False)
            slicer.util.setStatusBarVisible(False)
            slicer.util.setToolbarsVisible(False)
            slicer.util.setViewControllersVisible(False)
            self.userSwitched = True

    def createHLayout(self, elements):
        rowLayout = qt.QHBoxLayout()
        for element in elements:
            rowLayout.addWidget(element)
        return rowLayout

    def newHItemLayout(self, section, items):
        newLayout = qt.QFormLayout(section)
        for i in range(len(items)):
            HLayout = self.createHLayout(items[i][1:])
            if items[i][0] != None:
                newLayout.addRow(qt.QLabel(items[i][0]), HLayout)
            else:
                newLayout.addRow(HLayout)
        return newLayout

    def newSection(self, sectionTitle, toolTip=None):
        section = ctk.ctkCollapsibleButton()
        section.text = sectionTitle
        if toolTip != None:
            section.toolTip = toolTip
        self.layout.addWidget(section)
        return section

    def cleanup(self):
        pass

        ################################
        # User Study Environment Methods#
        ################################

    def onSetWorkspaceClicked(self):
        # interactive folder selection
        self.inputFolder = (
            str(
                qt.QFileDialog.getExistingDirectory(
                    None, "Work space", self.inputFolder, qt.QFileDialog.ShowDirsOnly
                )
            )
            + "/"
        )

    def onMoveNeedleClicked(self):
        if self.composite_needle == None:
            raise AttributeError("Composite needle not created")
            return
        translation = np.eye(4)
        translation[:3, 3] = 10

        original = self.getTransformMat(self.composite_needle.GetName())

        update_transform = np.matmul(translation, original)

        self.composite_needle.SetMatrixTransformToParent(
            self.npToVtkMatrix(update_transform)
        )

    def onStartNeedleClicked(self):
        # if data is already streaming, turn it off
        if self.needle_file.endswith("Data/"):
            raise AttributeError("Needle movement file not selected")
        if self.composite_needle == None:
            raise AttributeError("Composite needle not created")

        if self.needle_update:
            self.clearEnvironmentButton.enabled = True
            self.needle_update = False
            self.StartButton.text = "Start needle"
            self.timer.stop()
            self.resetNeedleButton.enabled = True

        # if not yet running, turn it on
        else:
            self.clearEnvironmentButton.enabled = False
            self.resetNeedleButton.enabled = False
            self.dropDownMovement.enabled = False
            self.dropDownMovementLabel.enabled = False
            self.streamingCheckBox.enabled = False
            self.needle_update = True
            self.StartButton.text = "Stop needle"
            self.timer.start()

    def onTimeOut(self):
        self.timer.stop()
        if self.needle_update:
            success = self.onNeedleRefresh()
            self.timer.start()

    def onNeedleRefresh(self):
        if (not os.path.isfile(self.needle_file)) or (
            not os.path.exists(self.needle_file)
        ):
            print(self.needle_file + " does not exist!")
            return False

        # pre-recorded data
        if not self.stream_live_data:
            if (
                not self.needle_data
            ):  # start streaming for the first time: load data from file
                self.needle_data = self.loadDataFromFile(self.needle_file, 0)
                self.needle_pose_index = 0

            if self.needle_pose_index >= len(self.needle_data) - 1:  # last line reached
                self.needle_pose_index = 0
                self.onStartNeedleClicked()  # click 'stop' button

            self.needle_pose_index += 1

        # live data via ROS
        else:
            d = self.loadDataFromFile(self.needle_file, 0)
            if not d == []:
                self.needle_data = d

        data = self.needle_data[self.needle_pose_index]
        if not len(data) == 7:
            print("Unexpected file format")
            print(data)
            return False

        pos = data[0:3]
        quat = data[3:7]

        success = self.updateNeedle(pos, quat)
        return success

    def updateNeedle(self, pos, quat):
        if len(pos) != 3 or len(quat) != 4:
            return False
        current = self.getTransformRot(pos, self.quaternionToRotationMatrix(quat))
        T = np.matmul(self.needle_registration, current)
        print(current[0:3,3])
        #print(self.needle_registration)
        print(T)
        self.composite_needle.SetMatrixTransformToParent(self.npToVtkMatrix(T))
        return True

    def onDropDownMovementSelect(self, index):
        text = self.dropDownMovement.itemText(index)
        if text == "":
            self.needleMovementSelected = False
            self.StartButton.enabled = False
        else:
            self.StartButton.enabled = True
            self.needleMovementSelected = True
        self.needle_file = self.inputFolder + text
        # print(self.needle_file)

    def onStreamingCheck(self):
        checked = self.streamingCheckBox.isChecked()

        if checked:
            self.dropDownMovement.setCurrentIndex(0)
            self.dropDownMovement.enabled = False
            self.dropDownMovementLabel.enabled = False
            self.stream_live_data = True
            self.needle_file = self.inputFolder + "needle-tracker.txt"
            self.StartButton.enabled = True
            # print(self.needle_file)
        else:
            self.StartButton.enabled = False
            self.stream_live_data = False
            self.needle_file = self.inputFolder
            self.dropDownMovement.enabled = True
            self.dropDownMovementLabel.enabled = True
            self.StartButton.enabled = False
            # print(self.needle_file)

    def onToggleVisualizers(self):
        checked = self.toggleVisualizers.isChecked()

        if checked:
            if self.coloredAngle != []:
                self.coloredAngle[1].VisibilityOn()
                slicer.mrmlScene.GetFirstNodeByName(
                    "AngleLegendModelDisplay"
                ).SetVisibility(True)
            else:  # Checked, but no colored cone model in scene
                slicer.mrmlScene.GetFirstNodeByName(
                    "AngleLegendModelDisplay"
                ).SetVisibility(False)
            if self.coloredRegion != []:
                self.coloredRegion[1].VisibilityOn()
                slicer.mrmlScene.GetFirstNodeByName(
                    "RegionLegendModelDisplay"
                ).SetVisibility(True)
            else:  # Checked, but no colored region model in scene
                slicer.mrmlScene.GetFirstNodeByName(
                    "RegionLegendModelDisplay"
                ).SetVisibility(False)
        else:  # Not checked -> regions and legends off
            if self.coloredAngle != []:
                self.coloredAngle[1].VisibilityOff()
                slicer.mrmlScene.GetFirstNodeByName(
                    "AngleLegendModelDisplay"
                ).SetVisibility(False)
            if self.coloredRegion != []:
                self.coloredRegion[1].VisibilityOff()
                slicer.mrmlScene.GetFirstNodeByName(
                    "RegionLegendModelDisplay"
                ).SetVisibility(False)

    def onResetNeedleButton(self):
        self.needle_pose_index = 0
        self.needle_data = []

        self.needle_registration = np.eye(4)
        self.needle_registration[0:3, 3] = np.array(
            [330.0, -20.0, 250.0]
        )  # hardcoded values for recorded data

        self.streamingCheckBox.enabled = True
        self.dropDownMovement.enabled = True
        self.dropDownMovementLabel.enabled = True

        self.dropDownMovement.setCurrentIndex(0)
        self.streamingCheckBox.setChecked(False)
        self.resetNeedleButton.enabled = False

        initial_position = np.eye(4)
        initial_position[:3, 3] = [225.0, 150.0, 175.0]
        self.composite_needle.SetMatrixTransformToParent(
            self.npToVtkMatrix(initial_position)
        )

    def onClearEnvironmentClicked(self):
        slicer.mrmlScene.GetSubjectHierarchyNode().RemoveAllItems(True)

        self.dropDownMovement.setCurrentIndex(0)
        self.dropDownViewSelector.setCurrentIndex(0)
        self.streamingCheckBox.setChecked(False)

        self.initVariables()
        self.needleSettings.enabled = False
        self.streamingCheckBox.enabled = False
        self.StartButton.enabled = False
        self.resetNeedleButton.enabled = False
        self.dropDownMovement.enabled = False
        self.dropDownMovementLabel.enabled = False
        self.loadEnvironmentButton.enabled = True
        self.toggleVisualizers.enabled = False

        self.regionColorTimer.stop()
        self.startAngleColorTimer.stop()

        slicer.mrmlScene.Clear(False)

    # create vtk objects representing parts of the environment
    def onLoadEnvironmentClicked(self):
        slicer.util.mainWindow().setWindowTitle("User Study")

        self.loadEnvironmentButton.enabled = False
        self.clearEnvironmentButton.enabled = True

        self.createCompositeNeedle()
        self.createTissue()
        self.createCloth()
        self.createColorRegionLegend()
        self.createColorAngleLegend()

        self.needleSettings.enabled = True
        self.streamingCheckBox.enabled = True
        self.StartButton.enabled = False
        self.resetNeedleButton.enabled = False
        self.dropDownMovement.enabled = True
        self.dropDownMovementLabel.enabled = True
        self.toggleVisualizers.enabled = True

        self.setCameras()

        self.tissue[1].VisibilityOff()

        self.createSegmentations()
        self.createStartText()

        self.dropDownViewSelector.setCurrentIndex(1)
        self.orderSelect.setText("1")
        self.onOrderSelectEnter()

    def createCloth(self):
        # read in object size
        path = self.inputFolder + "cloth.obj"
        slicer.util.loadModel(path)
        color = [119 / 255, 153 / 255, 189 / 255]
        self.clothDisplay = slicer.mrmlScene.GetFirstNodeByName(
            "cloth"
        ).GetDisplayNode()
        self.clothDisplay.SetColor(color)
        self.clothDisplay.SetVisibility(False)

    def createSegmentations(self):
        self.segLogic = slicer.util.getModuleLogic("LoadSegmentations")

        self.segLogic.loadSeg(os.path.dirname(os.getcwd()))
        self.resetCameras()

        transform = np.eye(4)
        self.segTransform = slicer.vtkMRMLLinearTransformNode()
        self.segTransform.SetMatrixTransformToParent(self.npToVtkMatrix(transform))
        self.segTransform.SetName("SegmentationTransform")
        slicer.mrmlScene.AddNode(self.segTransform)

        nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")

        for node in nodes:
            node.SetDisplayVisibility(False)
            node.SetAndObserveTransformNodeID(self.segTransform.GetID())

        transform = np.array(
            [
                [-0.116671, -4.996e-16, 0.993171, 381.00],
                [-0.179286, -0.983571, -0.0210613, 167.79],
                [0.976854, -0.180519, 0.114754, -23.50],
                [0, 0, 0, 1],
            ]
        )
        self.segTransform.SetMatrixTransformToParent(self.npToVtkMatrix(transform))

    def phaseTwo(self):
        self.tissue[1].VisibilityOn()
        self.clothDisplay.SetVisibility(True)
        nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
        for node in nodes:
            node.SetDisplayVisibility(True)

    def setCameras(self):
        self.resetFocals()

        camera = slicer.mrmlScene.GetFirstNodeByName("Camera")
        camera.SetPosition(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetPosition([222.5576399470194, -185.12465478378599, 266.6817368815024])
        camera.SetViewUp([-0.0025715218187866242, 0.2989896106755466, 0.9542529014803259])

        camera_2 = slicer.mrmlScene.GetFirstNodeByName("Camera_1")
        camera_2.SetPosition(0, 0, 0)
        camera_2.SetViewUp(0, 0, 1)
        camera_2.SetFocalPoint(0, 0, 0)

        handle_views = []
        shaft_views = []
        for view in slicer.mrmlScene.GetNodesByClass("vtkMRMLViewNode"):
            if view.GetName() == "View1":
                slicer.mrmlScene.GetFirstNodeByName(
                    "RegionLegendModelDisplay"
                ).SetViewNodeIDs([view.GetID()])
                slicer.mrmlScene.GetFirstNodeByName(
                    "AngleLegendModelDisplay"
                ).SetViewNodeIDs([view.GetID()])
            if view.GetName() == "View2":
                self.compositeNeedleEgoShaft[1].SetViewNodeIDs([view.GetID()])
            view.SetAxisLabelsVisible(False)
            view.SetBoxVisible(False)
            if not view.GetName() == "View3":
                handle_views.append(view.GetID())
            if not view.GetName() == "View2":
                shaft_views.append(view.GetID())

        self.compositeNeedleHandle[1].SetViewNodeIDs(handle_views)
        self.compositeNeedleShaft[1].SetViewNodeIDs(shaft_views)

        camera_4 = slicer.mrmlScene.GetFirstNodeByName("Camera_3")
        camera_4.SetPosition(-185.75776903637114, 155.14580392440647, 151.69601919675594)
        camera_4.SetViewUp(0,0,1)
        camera_4.SetFocalPoint(0, 0, 0)

        camera_5 = slicer.mrmlScene.GetFirstNodeByName("Camera_4")
        camera_5.SetPosition(225.0, 144.69855415401824, 467.6163285076625)
        camera_5.SetViewUp(0, 1, 0)
        camera_5.SetFocalPoint(0, 0, 0)

        camera_2.SetAndObserveTransformNodeID(self.composite_needle.GetID())
        initial_position = np.eye(4)
        initial_position[:3, 3] = [225.0, 150.0, 175.0]
        self.composite_needle.SetMatrixTransformToParent(
            self.npToVtkMatrix(initial_position)
        )
        # origin = self.getTransformMat(self.composite_needle.GetName())[:3,3]

        camera_2.SetPosition(224.975, 150.8, 200.68612593136095)
        camera_2.SetViewUp(
            0.004463893312410369, 0.9978291656684652, -0.06570410792233823
        )

        camera_2_focal = camera_2.GetFocalPoint()

        self.resetFocals()

        camera_2.SetFocalPoint(camera_2_focal)

        self.camera = [camera.GetPosition(), camera.GetViewUp(), camera.GetFocalPoint()]
        self.camera_2 = [
            camera_2.GetPosition(),
            camera_2.GetViewUp(),
            camera_2.GetFocalPoint(),
        ]
        self.camera_4 = [
            camera_4.GetPosition(),
            camera_4.GetViewUp(),
            camera_4.GetFocalPoint(),
        ]
        self.camera_5 = [
            camera_5.GetPosition(),
            camera_5.GetViewUp(),
            camera_5.GetFocalPoint(),
        ]

    def resetCameras(self):
        camera = slicer.mrmlScene.GetFirstNodeByName("Camera")
        camera_2 = slicer.mrmlScene.GetFirstNodeByName("Camera_1")
        try:
            camera_3 = slicer.mrmlScene.GetFirstNodeByName("Camera_2")
        except:
            pass
        camera_4 = slicer.mrmlScene.GetFirstNodeByName("Camera_3")
        camera_5 = slicer.mrmlScene.GetFirstNodeByName("Camera_4")

        camera.SetPosition(self.camera[0])
        camera.SetViewUp(self.camera[1])
        camera.SetFocalPoint(self.camera[2])
        camera_2.SetPosition(self.camera_2[0])
        camera_2.SetViewUp(self.camera_2[1])
        camera_2.SetFocalPoint(self.camera_2[2])
        try:
            camera_3.SetPosition(self.camera_3[0]); camera_3.SetViewUp(self.camera_3[1]); camera_3.SetFocalPoint(self.camera_3[2])
        except:
            pass
        camera_4.SetPosition(self.camera_4[0])
        camera_4.SetViewUp(self.camera_4[1])
        camera_4.SetFocalPoint(self.camera_4[2])
        camera_5.SetPosition(self.camera_5[0])
        camera_5.SetViewUp(self.camera_5[1])
        camera_5.SetFocalPoint(self.camera_5[2])


    def resetFocals(self):
        for n in range(5):
            slicer.app.layoutManager().threeDWidget(
                n
            ).threeDController().resetFocalPoint()
    

    def setCamera3(self):
        self.View3Controller.resetFocalPoint()
        camera_3 = slicer.mrmlScene.GetFirstNodeByName("Camera_2")
        camera_3.SetPosition(0, 0, 0)
        camera_3.SetViewUp(0, 0, 1)
        camera_3.SetFocalPoint(0, 0, 0)
        insertionPoseTransform = self.getTransformMat(self.insertionPose[2].GetName())
        view_up_pose = insertionPoseTransform[:3, 1]
        insert_position = insertionPoseTransform[:3, 3]
        camera_3.SetViewUp(-view_up_pose[0], -view_up_pose[1], -view_up_pose[2])
        translation_factor = 2
        translation_vector = (
            self.insertionPoseLength
            * translation_factor
            * insertionPoseTransform[:3, 2]
        )
        new_pos = insert_position + translation_vector
        camera_3.SetPosition(new_pos[0], new_pos[1], new_pos[2])
        # slicer.app.layoutManager().threeDWidget(2).threeDController().resetFocalPoint()
        camera_3.SetFocalPoint(insert_position)
        self.camera_3 = [
            camera_3.GetPosition(),
            camera_3.GetViewUp(),
            camera_3.GetFocalPoint(),
        ]

    def createCompositeNeedle(self):
        opacity = 1
        white = [1, 1, 1]
        black = [0.1, 0.1, 0.1]

        tipLength = 5/2
        tipAngle = 15/2
        shaftLength = 70/2
        handleLength = 40/2

        compositeNeedleTip = self.makeTip(tipLength, tipAngle, 3)
        radius = compositeNeedleTip.GetRadius()
        compositeNeedleShaft = self.makeCylinderLine(
            [0, 0, -(0 + tipLength)], shaftLength, radius, -1
        )
        compositeNeedleHandle = self.makeEllipsoid(
            [0, 0, -(shaftLength + handleLength)],
            [handleLength / 10, handleLength / 10, handleLength],
        )

        transform = np.eye(4)
        cleanup_transforms = []

        self.compositeNeedleTip = self.initModel(
            compositeNeedleTip, transform, "CompositeNeedleTip", white, opacity
        )
        self.compositeNeedleShaft = self.initModel(
            compositeNeedleShaft, transform, "CompositeNeedleShaft", white, opacity
        )
        self.compositeNeedleEgoShaft = self.initModel(
            compositeNeedleShaft, transform, "CompositeNeedleEgoShaft", white, opacity
        )
        self.compositeNeedleHandle = self.initModel(
            compositeNeedleHandle, transform, "CompositeNeedleHandle", black, opacity
        )

        cleanup_transforms.append(self.compositeNeedleTip[2])
        cleanup_transforms.append(self.compositeNeedleShaft[2])
        cleanup_transforms.append(self.compositeNeedleHandle[2])
        cleanup_transforms.append(self.compositeNeedleEgoShaft[2])

        self.composite_needle = self.initCompositeModel(
            [
                self.compositeNeedleTip[0],
                self.compositeNeedleShaft[0],
                self.compositeNeedleEgoShaft[0],
                self.compositeNeedleHandle[0],
            ],
            transform,
            "CompositeNeedle",
        )

        self.compositeNeedleEgoShaft[1].SetAmbient(0.73)
        self.compositeNeedleEgoShaft[1].SetDiffuse(0.91)
        self.compositeNeedleEgoShaft[1].SetSpecular(1)
        self.compositeNeedleEgoShaft[1].SetPower(1)

        for node in cleanup_transforms:
            slicer.mrmlScene.RemoveNode(node)

    # create tissue rectangle
    def createTissue(self):
        # read in object size
        tissue_data = self.loadDataFromFile(
            self.inputFolder + "tissue.txt", ignoreFirstLines=1
        )[0]  # data in list
        # print(tissue_data)
        center = np.array([tissue_data[0], tissue_data[1], tissue_data[2]])

        transform = np.eye(4)
        transform[0:3, 3] = center
        # print(transform)
        model = self.makeCube(tissue_data[3], tissue_data[4], tissue_data[5])
        color = [210 / 255, 187 / 255, 186 / 255]
        opacity = 1
        self.tissue = self.initModel(model, transform, "Tissue", color, opacity)
        self.tissue[1].SetAmbient(0.7)
        self.tissue[1].SetDiffuse(0.29)

    # create spherical obstacles
    def createObstacles(self):
        obstacle1_data = self.loadDataFromFile(
            self.inputFolder + "obstacle1.txt", ignoreFirstLines=1
        )
        obstacle2_data = self.loadDataFromFile(
            self.inputFolder + "obstacle2.txt", ignoreFirstLines=1
        )
        obstacle1_data = obstacle1_data[0]
        obstacle2_data = obstacle2_data[0]

        obstacle1_center = np.array(obstacle1_data[:3])
        obstacle2_center = np.array(obstacle2_data[:3])

        obstacle1_transform = np.eye(4)
        obstacle2_transform = np.eye(4)

        obstacle1_transform[:3, 3] = obstacle1_center
        obstacle2_transform[:3, 3] = obstacle2_center

        color = [0.8, 0.2, 0.1]
        opacity = 1

        obstacle1_model = self.makeSphere(obstacle1_data[3])
        obstacle2_model = self.makeSphere(obstacle2_data[3])

        self.obstacle1 = self.initModel(
            obstacle1_model, obstacle1_transform, "Obstacle1", color, opacity
        )
        self.obstacle2 = self.initModel(
            obstacle2_model, obstacle2_transform, "Obstacle2", color, opacity
        )

    def createInsertionPose(self, ignore_lines):
        """Given .txt file, creates pose at insertion point"""
        pose_data = self.loadDataFromFile(
            self.inputFolder + "startpose.txt", ignoreFirstLines=1 + ignore_lines
        )
        pose_data = pose_data[0]

        transform = np.eye(4)

        theta = np.radians(pose_data[5])
        phi = np.radians(pose_data[6])

        # X axis rotation matrix
        rotation_matrix_x = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(theta), -np.sin(theta), 0],
                [0, np.sin(theta), np.cos(theta), 0],
                [0, 0, 0, 1],
            ]
        )

        # Z axis rotation matrix
        rotation_matrix_z = np.array(
            [
                [np.cos(phi), -np.sin(phi), 0, 0],
                [np.sin(phi), np.cos(phi), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        # Apply x rotation
        transform = np.matmul(rotation_matrix_x, transform)
        # Apply z rotation
        transform = np.matmul(rotation_matrix_z, transform)

        transform = np.round(transform, 2)

        # Move pose to desired start coordinates
        start_coords = np.eye(4)
        start_coords[:3, 3] = pose_data[:3]
        transform = np.matmul(start_coords, transform)

        color = [0, 0, 1]
        opacity = 0.3

        self.insertionPoseLength = pose_data[3]

        model = self.makeCylinderLine([0, 0, 0], pose_data[3], pose_data[4])
        # model = self.makeCylinder(pose_data[3], pose_data[4])

        self.insertionPose = self.initModel(
            model, transform, "StartPose", color, opacity
        )

    def createInsertionRegion(self, ignored_lines, flag):
        """Creates insertion region, sphere or cylinder based on flag=true or flag=false"""
        region_data = self.loadDataFromFile(
            self.inputFolder + "region.txt", ignoreFirstLines=1 + ignored_lines
        )
        region_data = region_data[0]

        transform = np.eye(4)
        transform[:3, 3] = region_data[:3]

        theta = np.radians(90)

        rotation_matrix_x = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(theta), -np.sin(theta), 0],
                [0, np.sin(theta), np.cos(theta), 0],
                [0, 0, 0, 1],
            ]
        )

        transform = np.matmul(transform, rotation_matrix_x)
        transform = np.round(transform, 2)

        color = [1, 0, 0]
        opacity = 0.5

        radius = region_data[3]

        model = self.makeCylinder(0.5, radius)
        if flag:
            model = self.makeSphere(radius)

        self.coloredRegionRadius = region_data[3]

        self.coloredRegion = self.initModel(
            model, transform, "InsertionRegion", color, opacity
        )

    def createInsertionAngle(self, ignore_lines):
        angle_data = self.loadDataFromFile(
            self.inputFolder + "angle.txt", ignoreFirstLines=1 + ignore_lines
        )
        angle_data = angle_data[0]

        transform = np.eye(4)

        theta = np.radians(angle_data[5])
        phi = np.radians(angle_data[6])

        # X axis rotation matrix
        rotation_matrix_x = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(theta), -np.sin(theta), 0],
                [0, np.sin(theta), np.cos(theta), 0],
                [0, 0, 0, 1],
            ]
        )

        # Z axis rotation matrix
        rotation_matrix_z = np.array(
            [
                [np.cos(phi), -np.sin(phi), 0, 0],
                [np.sin(phi), np.cos(phi), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        # Apply x rotation
        transform = np.matmul(rotation_matrix_x, transform)
        # Apply z rotation
        transform = np.matmul(rotation_matrix_z, transform)

        # Move cone to desired start coordinates
        start_coords = np.eye(4)
        start_coords[:3, 3] = angle_data[:3]

        transform = np.matmul(start_coords, transform)

        color = [1, 0, 0]
        opacity = 0.2

        self.coloredAngleModel = self.makeCone(angle_data[3], angle_data[4], 10)

        self.coloredAngle = self.initModel(
            self.coloredAngleModel, transform, "InsertionAngle", color, opacity
        )

    def createNeedle(self):
        """Given .txt file, creates needle at desired point"""
        needle_data = self.loadDataFromFile(
            self.inputFolder + "needle.txt", ignoreFirstLines=1
        )
        needle_data = needle_data[0]

        transform = np.eye(4)

        theta = np.radians(90 - needle_data[5])
        phi = np.radians(needle_data[6])

        # X axis rotation matrix
        rotation_matrix_x = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(theta), -np.sin(theta), 0],
                [0, np.sin(theta), np.cos(theta), 0],
                [0, 0, 0, 1],
            ]
        )

        # Z axis rotation matrix
        rotation_matrix_z = np.array(
            [
                [np.cos(phi), -np.sin(phi), 0, 0],
                [np.sin(phi), np.cos(phi), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        # Apply x rotation
        transform = np.matmul(rotation_matrix_x, transform)
        # Apply z rotation
        transform = np.matmul(rotation_matrix_z, transform)

        transform = np.round(transform, 2)

        # Move needle to desired start coordinates
        start_coords = np.eye(4)
        start_coords[:3, 3] = needle_data[:3]
        transform = np.matmul(start_coords, transform)

        color = [1, 1, 1]
        opacity = 1
        model = self.makeCylinder(needle_data[3], needle_data[4])

        self.initModel(model, transform, "Needle", color, opacity)

    def createPlan(self):
        plan_data = self.loadDataFromFile(
            self.inputFolder + "plan.txt", ignoreFirstLines=1
        )
        plan = np.array(plan_data)

        plan_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode")
        plan_node.SetName("Plan")
        plan_node.GetDisplayNode().SetSelectedColor([0, 0, 0])
        plan_node.SetDisplayVisibility(True)

        for index, row in enumerate(plan):
            plan_node.AddControlPoint(row[0], row[1], row[2], f"Plan{index}")

    # create fiducial at goal pos
    def createGoal(self):
        goal_data = self.loadDataFromFile(
            self.inputFolder + "goal.txt", ignoreFirstLines=1
        )  # data in list
        goal = goal_data[0]
        fiducial_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
        fiducial_node.SetName("Goal")
        fiducial_node.GetDisplayNode().SetSelectedColor([1, 0, 0])
        fiducial_node.SetDisplayVisibility(True)
        fiducial_node.AddControlPoint(goal[0], goal[1], goal[2], "Goal")
        self.goal = fiducial_node

    def createStartText(self):
        data = self.loadDataFromFile(
            self.inputFolder + "starttext.txt", ignoreFirstLines=1
        )  # data in list
        text = data[0]
        fiducial_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
        fiducial_node.SetName("Goal")
        fiducial_node.GetDisplayNode().SetSelectedColor([1, 0, 0])
        fiducial_node.AddControlPoint(text[0], text[1], text[2], "Press Space To Begin")
        fiducial_node.GetDisplayNode().SetTextScale(22)
        fiducial_node.GetDisplayNode().SetGlyphScale(0)
        fiducial_node.SetDisplayVisibility(True)
        self.startText = fiducial_node

    def makeCube(self, size_x, size_y, size_z):
        cubeModel = vtk.vtkCubeSource()
        cubeModel.SetXLength(size_x)
        cubeModel.SetYLength(size_y)
        cubeModel.SetZLength(size_z)
        cubeModel.SetCenter(0.0, 0.0, 0.0)
        cubeModel.Update()
        return cubeModel

    def makeSphere(self, radius):
        sphereModel = vtk.vtkSphereSource()
        sphereModel.SetCenter(0, 0, 0)
        sphereModel.SetRadius(radius)
        sphereModel.SetThetaResolution(sphereModel.GetThetaResolution() * 20)
        sphereModel.SetPhiResolution(sphereModel.GetPhiResolution() * 20)
        sphereModel.Update()
        return sphereModel

    def makeCylinder(self, height, radius):
        cylinderModel = vtk.vtkCylinderSource()
        cylinderModel.SetHeight(height)
        cylinderModel.SetRadius(radius)
        cylinderModel.SetCenter(0, height / 2, 0)
        cylinderModel.SetResolution(cylinderModel.GetResolution() * 20)
        cylinderModel.Update()
        return cylinderModel

    def makeCone(self, height, angle, resolution):
        coneModel = vtk.vtkConeSource()
        radius = np.tan(np.radians(angle)) * height
        coneModel.SetHeight(height)
        coneModel.SetRadius(radius)
        coneModel.SetDirection(0, 0, -1)
        coneModel.SetCenter(0, 0, height / 2)
        coneModel.SetResolution(coneModel.GetResolution() * resolution * 2)
        coneModel.CappingOff()
        coneModel.Update()
        return coneModel

    def makeTip(self, height, angle, resolution):
        coneModel = vtk.vtkConeSource()
        radius = np.tan(np.radians(angle)) * height
        coneModel.SetHeight(height)
        coneModel.SetRadius(radius)
        coneModel.SetDirection(0, 0, 1)
        coneModel.SetCenter(0, 0, -(height / 2))
        coneModel.SetResolution(coneModel.GetResolution() * resolution * 2)
        coneModel.CappingOff()
        coneModel.Update()
        return coneModel

    def makeCylinderLine(self, point: list[float], height, radius, direction=1):
        lineModel = vtk.vtkLineSource()
        lineModel.SetPoint1(point)
        point[2] += (height * direction)
        lineModel.SetPoint2(point)
        lineModel.Update()

        tubeFilter = vtk.vtkTubeFilter()
        tubeFilter.SetInputConnection(lineModel.GetOutputPort())
        tubeFilter.SetRadius(radius)
        tubeFilter.SetNumberOfSides(30)
        tubeFilter.Update()
        return tubeFilter

    def makeEllipsoid(self, center: list[float], radius: list[float]):
        model = vtk.vtkSuperquadricSource()
        model.SetCenter(center)
        model.SetSize(radius[2])
        model.SetScale(
            radius[0] / radius[2], radius[1] / radius[2], radius[2] / radius[2]
        )
        model.SetAxisOfSymmetry(2)
        model.SetThetaResolution(model.GetThetaResolution() * 20)
        model.SetPhiResolution(model.GetPhiResolution() * 20)
        model.SetPhiRoundness(model.GetPhiRoundness() * 0.5)
        model.SetThetaRoundness(model.GetThetaRoundness() * 0.5)
        model.Update()
        return model

    def initCompositeModel(self, models, transform, name):
        composite_transform = slicer.vtkMRMLLinearTransformNode()
        composite_transform.SetMatrixTransformToParent(self.npToVtkMatrix(transform))
        composite_transform.SetName(name + "Transform")
        slicer.mrmlScene.AddNode(composite_transform)

        for model in models:
            model.SetAndObserveTransformNodeID(composite_transform.GetID())

        return composite_transform

    # add a model to the slicer environment and make it visible
    def initModel(self, model, transform, name, color, opacity=1.0):
        # add model to slicer environment
        model_node = slicer.vtkMRMLModelNode()
        model_node.SetName(name)
        model_node.SetPolyDataConnection(model.GetOutputPort())

        display_node = slicer.vtkMRMLModelDisplayNode()
        display_node.SetColor(color[0], color[1], color[2])
        display_node.SetOpacity(opacity)
        if name == "InsertionRegion" or name == "InsertionAngle":
            if self.toggleVisualizers.isChecked():
                display_node.VisibilityOn()
            else:
                display_node.VisibilityOff()
        slicer.mrmlScene.AddNode(display_node)
        model_node.SetAndObserveDisplayNodeID(display_node.GetID())
        # Add to scene
        slicer.mrmlScene.AddNode(model_node)

        # add a transform to interactively move the model
        model_transform = slicer.vtkMRMLLinearTransformNode()
        model_transform.SetMatrixTransformToParent(self.npToVtkMatrix(transform))
        model_transform.SetName(name + "Transform")
        slicer.mrmlScene.AddNode(model_transform)
        model_node.SetAndObserveTransformNodeID(model_transform.GetID())

        return model_node, display_node, model_transform

        ############################################
        # Matrix transform and other helper methods#
        ############################################

        # rotate around x axis by an angle

    def rotateAroundX(self, angle):
        R = np.eye(3)
        R[1, 1] = np.cos(angle)
        R[1, 2] = -np.sin(angle)
        R[2, 1] = np.sin(angle)
        R[2, 2] = np.cos(angle)

        return R

    # rotate around y axis by an angle
    def rotateAroundY(self, angle):
        R = np.eye(3)
        R[0, 0] = np.cos(angle)
        R[0, 2] = np.sin(angle)
        R[2, 0] = -np.sin(angle)
        R[2, 2] = np.cos(angle)
        return R

    # rotate around t axis by an angle
    def rotateAroundZ(self, angle):
        R = np.eye(4)
        R[0, 0] = np.cos(angle)
        R[0, 1] = -np.sin(angle)
        R[1, 0] = np.sin(angle)
        R[1, 1] = np.cos(angle)
        return R

    def rotate(self, angle, axis):
        T_R = np.eye(4)
        if axis == 0:
            T_R[0:3, 0:3] = self.rotateAroundX(angle)
        if axis == 1:
            T_R[0:3, 0:3] = self.rotateAroundY(angle)
        if axis == 2:
            T_R[0:3, 0:3] = self.rotateAroundZ(angle)
        return T_R

    # translate by vector T
    def translate(self, t):
        T_t = np.eye(4)
        T_t[0:3, 3] = t
        # T_result = np.matmul(T, T_t)
        return T_t

    def vtkToNpMatrix(self, vtk_mat):
        np_mat = np.eye(4)
        for r in range(np_mat.shape[0]):
            for c in range(np_mat.shape[1]):
                x = vtk_mat.GetElement(r, c)
                np_mat[r, c] = x
        return np_mat

    def npToVtkMatrix(self, np_mat):
        matrix = vtk.vtkMatrix4x4()
        for r in range(np_mat.shape[0]):
            for c in range(np_mat.shape[1]):
                matrix.SetElement(r, c, np_mat[r, c])
        return matrix

    # get np matrix from transform node by name
    def getTransformMat(self, name):
        vtk_mat = vtk.vtkMatrix4x4()
        transform_node = slicer.util.getNode(name)
        transform_node.GetMatrixTransformToWorld(vtk_mat)
        np_mat = self.vtkToNpMatrix(vtk_mat)
        # self.planeMat = np_mat
        # print(np_mat)
        return np_mat

    # create a 4x4 transform from a rotation matrix and a translation vector
    def getTransformRot(self, pos, rot):
        t = np.expand_dims(np.array(pos), 1)
        R = rot
        mat = np.eye(4)
        mat[0:3, 0:3] = R
        mat[0:3, 3:4] = t
        return mat

    # convert a quaternion into a rotation matrix
    def quaternionToRotationMatrix(self, quaternion):
        # quaterion = [qw, qx, qy, qz]

        q = np.array(quaternion, dtype=np.float64, copy=True)
        n = np.dot(q, q)
        if n < 0.0000001:
            return np.identity(3)

        q *= math.sqrt(2.0 / n)
        q = np.outer(q, q)
        return np.array(
            [
                [1.0 - q[2, 2] - q[3, 3], q[1, 2] - q[3, 0], q[1, 3] + q[2, 0]],
                [q[1, 2] + q[3, 0], 1.0 - q[1, 1] - q[3, 3], q[2, 3] - q[1, 0]],
                [q[1, 3] - q[2, 0], q[2, 3] + q[1, 0], 1.0 - q[1, 1] - q[2, 2]],
            ]
        )

    def rodriguesRotation(self, normal_vec, so, beta):
        so_rot = (
            (np.cos(beta) * so)
            + (np.sin(beta) * np.cross(normal_vec, so))
            + ((1 - np.cos(beta)) * np.dot(normal_vec, so) * normal_vec)
        )
        return so_rot

    def distance(self, T1, T2):
        """Given two transform nodes, calculates distance between their reference points"""
        pos1 = self.getTransformMat(T1.GetName())[:3, 3]
        pos2 = self.getTransformMat(T2.GetName())[:3, 3]

        x1, y1, z1 = pos1
        x2, y2, z2 = pos2

        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    def updateRegionColor(self):
        needle_pos = self.composite_needle
        region_pos = self.coloredRegion[2]
        region_display = self.coloredRegion[1]

        distance = self.distance(needle_pos, region_pos)

        color_map_index_length = layouts.colorMap(0)[1] - 1

        if distance > self.coloredRegionRadius:
            color = [1, 0, 0]
            colorPos = 0
        else:
            colorPos = int(
                (1 - distance / self.coloredRegionRadius) * color_map_index_length
            )
            color = layouts.colorMap(colorPos)[0]

        region_display.SetColor(color)

        if (
            self.colorTableRegionIndex is not None
            and self.colorTableRegionIndex != colorPos
        ):
            prev = self.colorTableRegionPrev
            self.colorTableRegion.SetColor(
                self.colorTableRegionIndex, prev[0], prev[1], prev[2], 1
            )

        if self.colorTableRegionIndex != colorPos:
            self.colorTableRegionIndex = colorPos
            self.colorTableRegionPrev = color
            self.colorTableRegion.SetColor(colorPos, 0, 0, 0, 1)

    def updateAngleColor(self):
        cone_direction = self.getTransformMat(self.coloredAngle[2].GetName())[:3, 2]
        needle_direction = -self.getTransformMat(self.composite_needle.GetName())[:3, 2]

        cos_theta = np.dot(cone_direction, needle_direction) / (
            np.linalg.norm(cone_direction) * np.linalg.norm(needle_direction)
        )

        cos_theta = np.clip(cos_theta, -1, 1)
        theta = np.arccos(cos_theta)

        angle_difference = np.degrees(theta)

        color_map_index_length = layouts.colorMap(0)[1] - 1

        cone_angle = self.coloredAngleModel.GetAngle()

        if angle_difference > cone_angle:
            colorPos = 0
            color = [1, 0, 0]
        else:
            colorPos = int((1 - angle_difference / cone_angle) * color_map_index_length)
            color = layouts.colorMap(colorPos)[0]

        self.coloredAngle[1].SetColor(color)

        if (
            self.colorTableAngleIndex is not None
            and self.colorTableAngleIndex != colorPos
        ):
            prev = self.colorTableAnglePrev
            self.colorTableAngle.SetColor(
                self.colorTableAngleIndex, prev[0], prev[1], prev[2], 1
            )

        if self.colorTableAngleIndex != colorPos:
            self.colorTableAngleIndex = colorPos
            self.colorTableAnglePrev = color
            self.colorTableAngle.SetColor(colorPos, 0, 0, 0, 1)

    def createColorRegionLegend(self):
        self.colorTableRegion = slicer.vtkMRMLColorTableNode()
        self.colorTableRegion.SetTypeToUser()
        self.colorTableRegion.SetNumberOfColors(layouts.colorMap(0)[1])
        self.colorTableRegionIndex = None
        self.colorTableRegionPrev = None

        for n in range(layouts.colorMap(0)[1]):
            color = layouts.colorMap(n)[0]
            self.colorTableRegion.SetColor(n, color[0], color[1], color[2], 1)

        slicer.mrmlScene.AddNode(self.colorTableRegion)

        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(1)
        legendModel = slicer.vtkMRMLModelNode()
        legendModel.SetPolyDataConnection(sphere.GetOutputPort())
        legendModel.SetName("RegionLegendModel")
        slicer.mrmlScene.AddNode(legendModel)

        displayLegend = slicer.vtkMRMLModelDisplayNode()
        displayLegend.SetName("RegionLegendModelDisplay")
        displayLegend.SetActiveScalarName("Normals")
        displayLegend.SetScalarRange(0, 100)
        displayLegend.SetScalarRangeFlag(0)
        displayLegend.SetVisibility(False)
        displayLegend.SetAndObserveColorNodeID(self.colorTableRegion.GetID())
        slicer.mrmlScene.AddNode(displayLegend)
        legendModel.SetAndObserveDisplayNodeID(displayLegend.GetID())

        displayLegendNode = slicer.vtkMRMLColorLegendDisplayNode()
        displayLegendNode.SetName("ColorRegionLegend")
        slicer.mrmlScene.AddNode(displayLegendNode)
        displayLegendNode.SetAndObservePrimaryDisplayNode(displayLegend)
        legendModel.AddAndObserveDisplayNodeID(displayLegendNode.GetID())

        displayLegendNode.SetNumberOfLabels(2)
        displayLegendNode.SetMaxNumberOfColors(100)
        displayLegendNode.SetSize(0.1, 0.85)
        displayLegendNode.SetPosition(0.85, 0.4)
        displayLegendNode.SetTitleText("Position")
        displayLegendNode.GetTitleTextProperty().SetFontSize(20)
        displayLegendNode.GetLabelTextProperty().SetFontFamilyToArial()

    def createColorAngleLegend(self):
        self.colorTableAngle = slicer.vtkMRMLColorTableNode()
        self.colorTableAngle.SetTypeToUser()
        self.colorTableAngle.SetNumberOfColors(layouts.colorMap(0)[1])
        self.colorTableAngleIndex = None
        self.colorTableAnglePrev = None

        for n in range(layouts.colorMap(0)[1]):
            color = layouts.colorMap(n)[0]
            self.colorTableAngle.SetColor(n, color[0], color[1], color[2], 1)

        slicer.mrmlScene.AddNode(self.colorTableAngle)

        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(1)
        legendModel = slicer.vtkMRMLModelNode()
        legendModel.SetPolyDataConnection(sphere.GetOutputPort())
        legendModel.SetName("AngleLegendModel")
        slicer.mrmlScene.AddNode(legendModel)

        displayLegend = slicer.vtkMRMLModelDisplayNode()
        displayLegend.SetName("AngleLegendModelDisplay")
        displayLegend.SetActiveScalarName("Normals")
        displayLegend.SetScalarRange(0, 100)
        displayLegend.SetScalarRangeFlag(0)
        displayLegend.SetVisibility(False)
        displayLegend.SetAndObserveColorNodeID(self.colorTableAngle.GetID())
        slicer.mrmlScene.AddNode(displayLegend)
        legendModel.SetAndObserveDisplayNodeID(displayLegend.GetID())

        displayLegendNode = slicer.vtkMRMLColorLegendDisplayNode()
        displayLegendNode.SetName("ColorAngleLegend")
        slicer.mrmlScene.AddNode(displayLegendNode)
        displayLegendNode.SetAndObservePrimaryDisplayNode(displayLegend)
        legendModel.AddAndObserveDisplayNodeID(displayLegendNode.GetID())

        displayLegendNode.SetNumberOfLabels(2)
        displayLegendNode.SetMaxNumberOfColors(100)
        displayLegendNode.SetSize(0.1, 0.85)
        displayLegendNode.SetPosition(0.98, 0.4)
        displayLegendNode.SetTitleText("Orientation")
        displayLegendNode.GetTitleTextProperty().SetFontSize(20)
        displayLegendNode.GetLabelTextProperty().SetFontFamilyToArial()

    def loadDataFromFile(self, fullPath, ignoreFirstLines=1):
        print("Loading points from " + str(fullPath))

        planFile = open(fullPath)
        lines = planFile.readlines()
        count = 0

        data = []
        linecount = -1

        for line in lines:
            linecount += 1
            if ignoreFirstLines > linecount:
                continue
            fields = line.split(" ")

            if fields[-1] == "\n":  # Remove newline
                fields = fields[:-1]

            if fields[-1][-1] == "\n":  # Remove newline not separated from last number
                fields[-1] = fields[-1][:-1]

            if len(fields) > 1:
                d = [float(f) for f in fields]
                data.append(d)
                count += 1

        planFile.close()
        print(str(count) + " lines loaded.")

        return data


#
# UserStudyLogic
#


class UserStudyLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        self.currentFileDir = os.path.dirname(os.path.abspath(__file__))

    def hasImageData(self, volumeNode):
        """This is an example logic method that
        returns true if the passed in volume
        node has valid image data
        """
        if not volumeNode:
            logging.debug("hasImageData failed: no volume node")
            return False
        if volumeNode.GetImageData() is None:
            logging.debug("hasImageData failed: no image data in volume node")
            return False
        return True

    def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
        """Validates if the output is not the same as input"""
        if not inputVolumeNode:
            logging.debug("isValidInputOutputData failed: no input volume node defined")
            return False
        if not outputVolumeNode:
            logging.debug(
                "isValidInputOutputData failed: no output volume node defined"
            )
            return False
        if inputVolumeNode.GetID() == outputVolumeNode.GetID():
            logging.debug(
                "isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error."
            )
            return False
        return True

    def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
        """
        Run the actual algorithm
        """

        if not self.isValidInputOutputData(inputVolume, outputVolume):
            slicer.util.errorDisplay(
                "Input volume is the same as output volume. Choose a different output volume."
            )
            return False

        logging.info("Processing started")

        # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
        cliParams = {
            "InputVolume": inputVolume.GetID(),
            "OutputVolume": outputVolume.GetID(),
            "ThresholdValue": imageThreshold,
            "ThresholdType": "Above",
        }
        cliNode = slicer.cli.run(
            slicer.modules.thresholdscalarvolume,
            None,
            cliParams,
            wait_for_completion=True,
        )

        # Capture screenshot
        if enableScreenshots:
            self.takeScreenshot("UserStudyTest-Start", "MyScreenshot", -1)

        logging.info("Processing completed")

        return True

    def readLastLine(self, filename):
        fin = open(filename)
        lines = fin.readlines()
        pos = []
        quat = []
        if len(lines) > 0:
            latestLine = lines[-1]
            fields = latestLine.split(" ")
            if fields[-1] == "\n":
                n = len(fields)
                fields = fields[0 : n - 1]

            if len(fields) == 7:
                fieldsPos = fields[:3]
                fieldsQuat = fields[3:]
                pos = map(float, fieldsPos)
                quat = map(float, fieldsQuat)
        # else:
        # print(filename + " is empty!")

        fin.close()
        return [pos, quat]


class UserStudyTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_UserStudy1()

    def test_UserStudy1(self):
        """Ideally you should have several levels of tests.  At the lowest level
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
            nodeNames="FA",
            fileNames="FA.nrrd",
            uris="http://slicer.kitware.com/midas3/download?items=5767",
        )
        self.delayDisplay("Finished with download and loading")

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = UserStudyLogic()
        self.assertIsNotNone(logic.hasImageData(volumeNode))
        self.delayDisplay("Test passed!")
