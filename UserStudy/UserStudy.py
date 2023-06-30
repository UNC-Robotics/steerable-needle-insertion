import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import math
import numpy as np

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
    self.parent.title = "UserStudy" # TODO make this more human readable by adding spaces
    self.parent.categories = ["User Study"]
    self.parent.dependencies = []
    self.parent.contributors = ["Janine Hoelscher"] # replace with "Firstname Lastname (Organization)"
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
# UserStudyWidget
#

class UserStudyWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  ##########
  #UI Setup#
  ##########

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    self.initVariables()
    self.initUI()


  def initVariables(self):
    self.logic = UserStudyLogic()
    self.inputFolder = os.path.dirname(os.path.abspath(__file__)) + "/Resources/Data/" #Hardcode input path here for testing purposes
    print(self.inputFolder)


  def initUI(self):

    # load environment visualization elements
    self.loadEnvironmentButton = qt.QPushButton("Load Environment")
    self.loadEnvironmentButton.toolTip = "Load experiment environment visualization"
    self.loadEnvironmentButton.enabled = True
    self.loadEnvironmentButton.connect('clicked(bool)', self.onLoadEnvironmentClicked)

    self.clearEnvironmentButton = qt.QPushButton("Clear Environment")
    self.clearEnvironmentButton.toolTip = "Clear experiment environment visualization"
    self.clearEnvironmentButton.enabled = True
    self.clearEnvironmentButton.connect('clicked(bool)', self.onClearEnvironmentClicked)

    self.userStudySection = self.newSection("User Study")
    self.userStudyLayout = self.newHItemLayout(self.userStudySection,
                                                   [[None, self.loadEnvironmentButton],
                                                    [None, self.clearEnvironmentButton]])
    


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
    #User Study Environment Methods#
    ################################

  def onSetWorkspaceClicked(self):
    # interactive folder selection
    self.inputFolder = str(qt.QFileDialog.getExistingDirectory(None, 'Work space', self.inputFolder,
                                                               qt.QFileDialog.ShowDirsOnly)) + "/"

  def onClearEnvironmentClicked(self):
    slicer.mrmlScene.GetSubjectHierarchyNode().RemoveAllItems(True)

  #create vtk objects representing parts of the environment
  def onLoadEnvironmentClicked(self):

    self.createCompositeNeedle()
    self.createTissue() #cuboid
    self.createObstacles() #spheres
    self.createInsertionPose()  #cylinder
    self.createInsertionRegion() #cylinder
    self.createInsertionAngle() #cone
    self.createPlan() #line object
    self.createNeedle() #cylinder?
    self.createGoal() #fiducial  

    #Set camera and bounding box initial positions
    camera = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLCameraNode")
    camera.SetPosition([225.0, -929.8879627522049, 114.1622183434929])
    camera.SetViewUp(0,0,1)
    slicer.app.layoutManager().threeDWidget(0).threeDController().resetFocalPoint()
    
  def createCompositeNeedle(self):
    opacity = .6
    white = [1,1,1]
    black = [.1,.1,.1]

    tipLength = 5
    tipAngle = 15

    shaftLength = 70
    handleLength = 40

    needleTip = self.makeCone(tipLength, tipAngle)
    radius = needleTip.GetRadius()
    needleShaft = self.makeCylinderLine([0,0,0+tipLength], shaftLength, radius)
    needleHandle = self.makeEllipsoid([0,0,shaftLength+handleLength],
                                      [handleLength/10,handleLength/10,handleLength])

    transform = np.eye(4)
    cleanup_transforms = []

    needleTip = self.initModel(needleTip, transform, "CompositeNeedleTip", white, opacity)
    needleShaft = self.initModel(needleShaft, transform, "CompositeNeedleShaft", white, opacity)
    needleHandle = self.initModel(needleHandle, transform, "CompositeNeedleHandle", black, opacity)

    cleanup_transforms.append(needleTip[2])
    cleanup_transforms.append(needleShaft[2])
    cleanup_transforms.append(needleHandle[2])


    self.initCompositeModel([needleTip[0], needleShaft[0], needleHandle[0]], transform, "CompositeNeedle")

    for node in cleanup_transforms:
       slicer.mrmlScene.RemoveNode(node)

  #create tissue rectangle
  def createTissue(self):
    #read in object size
    tissue_data = self.loadDataFromFile(self.inputFolder + "tissue.txt", ignoreFirstLines=1) #data in list
    print(tissue_data)
    corner1 = np.array(tissue_data[0])
    corner2 = np.array(tissue_data[1])
    center = (corner2 - corner1)/2
    size = np.absolute(corner2 - corner1)

    transform = np.eye(4)
    transform[0:3,3] = center
    print(transform)
    model = self.makeCube(size[0],size[1], size[2])
    color = [0.8, 0.8, 0.6]
    opacity = 0.2
    self.initModel(model, transform, "Tissue", color, opacity)

  #create spherical obstacles
  def createObstacles(self):
    obstacle1_data = self.loadDataFromFile(self.inputFolder + "obstacle1.txt", ignoreFirstLines=1)
    obstacle2_data = self.loadDataFromFile(self.inputFolder + "obstacle2.txt", ignoreFirstLines=1)
    obstacle1_data = obstacle1_data[0]
    obstacle2_data = obstacle2_data[0]

    obstacle1_center = np.array(obstacle1_data[:3])
    obstacle2_center = np.array(obstacle2_data[:3])

    obstacle1_transform = np.eye(4)
    obstacle2_transform = np.eye(4)

    obstacle1_transform[:3,3] = obstacle1_center
    obstacle2_transform[:3,3] = obstacle2_center

    color = [0.8, 0.2, 0.1]
    opacity = 1

    obstacle1_model = self.makeSphere(obstacle1_data[3])
    obstacle2_model = self.makeSphere(obstacle2_data[3])
    
    self.initModel(obstacle1_model, obstacle1_transform, "Obstacle1", color, opacity)
    self.initModel(obstacle2_model, obstacle2_transform, "Obstacle2", color, opacity)

  def createInsertionPose(self):
    """Given .txt file, creates pose at insertion point"""
    pose_data = self.loadDataFromFile(self.inputFolder + "startpose.txt", ignoreFirstLines=1)
    pose_data = pose_data[0]

    transform = np.eye(4)

    theta = np.radians(90-pose_data[5])
    phi = np.radians(pose_data[6])

    #X axis rotation matrix
    rotation_matrix_x = np.array([[1,0,0,0],
                                [0,np.cos(theta),-np.sin(theta),0],
                                [0,np.sin(theta),np.cos(theta),0],
                                [0,0,0,1]])
    
    #Z axis rotation matrix
    rotation_matrix_z = np.array([[np.cos(phi),-np.sin(phi),0,0],
                                  [np.sin(phi),np.cos(phi),0,0],
                                  [0,0,1,0],
                                  [0,0,0,1]])

    #Apply x rotation
    transform = np.matmul(rotation_matrix_x, transform)
    #Apply z rotation
    transform = np.matmul(rotation_matrix_z, transform)
    
    transform = np.round(transform, 2)

    #Move pose to desired start coordinates
    start_coords = np.eye(4)
    start_coords[:3,3] = pose_data[:3]
    transform = np.matmul(start_coords, transform)

    color = [0, 0, 1]
    opacity = .3

    model = self.makeCylinder(pose_data[3], pose_data[4])

    self.initModel(model, transform, "StartPose", color, opacity)
  
  def createInsertionRegion(self):
    region_data = self.loadDataFromFile(self.inputFolder + "region.txt", ignoreFirstLines=1)
    region_data = region_data[0]

    transform = np.eye(4)
    transform[:3,3] = region_data[:3]

    theta = np.radians(90)

    rotation_matrix_x = np.array([[1,0,0,0],
                                [0,np.cos(theta),-np.sin(theta),0],
                                [0,np.sin(theta),np.cos(theta),0],
                                [0,0,0,1]])
    
    transform = np.matmul(transform, rotation_matrix_x)
    transform = np.round(transform, 2)

    color = [117/255,157/255,230/255]
    opacity = .5

    model = self.makeCylinder(.5, region_data[3])

    self.initModel(model, transform, "InsertionRegion", color, opacity)

  def createInsertionAngle(self):
    angle_data = self.loadDataFromFile(self.inputFolder + "angle.txt", ignoreFirstLines=1)
    angle_data = angle_data[0]

    transform = np.eye(4)

    theta = np.radians(angle_data[5])
    phi = np.radians(angle_data[6])

    #X axis rotation matrix
    rotation_matrix_x = np.array([[1,0,0,0],
                                [0,np.cos(theta),-np.sin(theta),0],
                                [0,np.sin(theta),np.cos(theta),0],
                                [0,0,0,1]])
    
    #Z axis rotation matrix
    rotation_matrix_z = np.array([[np.cos(phi),-np.sin(phi),0,0],
                                  [np.sin(phi),np.cos(phi),0,0],
                                  [0,0,1,0],
                                  [0,0,0,1]])
    
    #Apply x rotation
    transform = np.matmul(rotation_matrix_x, transform)
    #Apply z rotation
    transform = np.matmul(rotation_matrix_z, transform)

    #Move cone to desired start coordinates
    start_coords = np.eye(4)
    start_coords[:3,3] = angle_data[:3]

    transform = np.matmul(start_coords, transform)

    color = [.2, .8, .1]
    opacity = .2

    model = self.makeCone(angle_data[3], angle_data[4])

    self.initModel(model, transform, "InsertionAngle", color, opacity)

  def createNeedle(self):
    """Given .txt file, creates needle at desired point"""
    needle_data = self.loadDataFromFile(self.inputFolder + "needle.txt", ignoreFirstLines=1)
    needle_data = needle_data[0]

    transform = np.eye(4)

    theta = np.radians(90-needle_data[5])
    phi = np.radians(needle_data[6])

    #X axis rotation matrix
    rotation_matrix_x = np.array([[1,0,0,0],
                                [0,np.cos(theta),-np.sin(theta),0],
                                [0,np.sin(theta),np.cos(theta),0],
                                [0,0,0,1]])
    
    #Z axis rotation matrix
    rotation_matrix_z = np.array([[np.cos(phi),-np.sin(phi),0,0],
                                  [np.sin(phi),np.cos(phi),0,0],
                                  [0,0,1,0],
                                  [0,0,0,1]])

    #Apply x rotation
    transform = np.matmul(rotation_matrix_x, transform)
    #Apply z rotation
    transform = np.matmul(rotation_matrix_z, transform)
    
    transform = np.round(transform, 2)

    #Move needle to desired start coordinates
    start_coords = np.eye(4)
    start_coords[:3,3] = needle_data[:3]
    transform = np.matmul(start_coords, transform)

    color = [1, 1, 1]
    opacity = 1
    model = self.makeCylinder(needle_data[3], needle_data[4])

    self.initModel(model, transform, "Needle", color, opacity)

  def createPlan(self):
    plan_data = self.loadDataFromFile(self.inputFolder + "plan.txt", ignoreFirstLines=1) 
    plan = np.array(plan_data)
    print(plan)

    plan_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode")
    plan_node.SetName("Plan")
    plan_node.GetDisplayNode().SetSelectedColor([0,0,0])
    plan_node.SetDisplayVisibility(True)
    
    for index, row in enumerate(plan):
      plan_node.AddControlPoint(row[0], row[1], row[2], f"Plan{index}")

  #create fiducial at goal pos
  def createGoal(self):
    goal_data = self.loadDataFromFile(self.inputFolder + "goal.txt", ignoreFirstLines=1) #data in list
    goal = goal_data[0]
    fiducial_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    fiducial_node.SetName("Goal")
    fiducial_node.GetDisplayNode().SetSelectedColor([1, 0, 0])
    fiducial_node.SetDisplayVisibility(True)
    fiducial_node.AddControlPoint(goal[0], goal[1], goal[2], "Goal")

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
    sphereModel.SetCenter(0,0,0)
    sphereModel.SetRadius(radius)
    sphereModel.SetThetaResolution(sphereModel.GetThetaResolution()*10)
    sphereModel.SetPhiResolution(sphereModel.GetPhiResolution()*10)
    sphereModel.Update()
    return sphereModel

  def makeCylinder(self, height, radius):
    cylinderModel = vtk.vtkCylinderSource()
    cylinderModel.SetHeight(height)
    cylinderModel.SetRadius(radius)
    cylinderModel.SetCenter(0,height/2,0)
    cylinderModel.SetResolution(cylinderModel.GetResolution()*10)
    cylinderModel.Update()
    return cylinderModel

  def makeCone(self, height, angle):
    coneModel = vtk.vtkConeSource()
    radius = (np.tan(np.radians(angle))*height)
    coneModel.SetHeight(height)
    coneModel.SetRadius(radius)
    coneModel.SetDirection(0,0,-1)
    coneModel.SetCenter(0,0,height/2)
    coneModel.SetResolution(coneModel.GetResolution()*10)
    coneModel.CappingOff()
    coneModel.Update()
    return coneModel
  
  def makeCylinderLine(self, point: list[float], height, radius):
    lineModel = vtk.vtkLineSource()
    lineModel.SetPoint1(point)
    point[2] += height
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
    model.SetScale(radius[0]/radius[2], radius[1]/radius[2], radius[2]/radius[2])
    model.SetAxisOfSymmetry(2)
    model.SetThetaResolution(model.GetThetaResolution()*10)
    model.SetPhiResolution(model.GetPhiResolution()*10)
    model.SetPhiRoundness(model.GetPhiRoundness()*.5)
    model.SetThetaRoundness(model.GetThetaRoundness()*.5)
    model.Update()
    return model

  def initCompositeModel(self, models, transform, name):
    composite_transform = slicer.vtkMRMLLinearTransformNode()
    composite_transform.SetMatrixTransformToParent(self.npToVtkMatrix(transform))
    composite_transform.SetName(name+"Transform")
    slicer.mrmlScene.AddNode(composite_transform)

    for model in models:
      model.SetAndObserveTransformNodeID(composite_transform.GetID())


  #add a model to the slicer environment and make it visible
  def initModel(self, model, transform, name, color, opacity=1.0):

    #add model to slicer environment
    model_node = slicer.vtkMRMLModelNode()
    model_node.SetName(name)
    model_node.SetPolyDataConnection(model.GetOutputPort())

    display_node = slicer.vtkMRMLModelDisplayNode()
    display_node.SetColor(color[0],color[1],color[2])
    display_node.SetOpacity(opacity)
    slicer.mrmlScene.AddNode(display_node)
    model_node.SetAndObserveDisplayNodeID(display_node.GetID())
    # Add to scene
    slicer.mrmlScene.AddNode(model_node)

    #add a transform to interactively move the model
    model_transform = slicer.vtkMRMLLinearTransformNode()
    model_transform.SetMatrixTransformToParent(self.npToVtkMatrix(transform))
    model_transform.SetName(name+"Transform")
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
          T_R[0:3,0:3] = self.rotateAroundX(angle)
        if axis == 1:
          T_R[0:3,0:3] = self.rotateAroundY(angle)
        if axis == 2:
          T_R[0:3,0:3] = self.rotateAroundZ(angle)
        return T_R

    #translate by vector T
  def translate(self, t):
        T_t = np.eye(4)
        T_t[0:3,3] = t
        #T_result = np.matmul(T, T_t)
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
        np_mat = self.convertVtkMatrix(vtk_mat)
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
        return np.array([
            [1.0 - q[2, 2] - q[3, 3], q[1, 2] - q[3, 0], q[1, 3] + q[2, 0]],
            [q[1, 2] + q[3, 0], 1.0 - q[1, 1] - q[3, 3], q[2, 3] - q[1, 0]],
            [q[1, 3] - q[2, 0], q[2, 3] + q[1, 0], 1.0 - q[1, 1] - q[2, 2]]])

  def rodriguesRotation(self, normal_vec, so, beta):
        so_rot = (np.cos(beta) * so) + (np.sin(beta) * np.cross(normal_vec, so)) + ((1 - np.cos(beta)) * np.dot(normal_vec, so) * normal_vec)
        return so_rot

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
                fields[-1] = fields[:-1]

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


  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('UserStudyTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True

  def readLastLine(self, filename):
    fin = open(filename)
    lines = fin.readlines()
    pos = []
    quat = []
    if (len(lines) > 0):
        latestLine = lines[-1]
        fields = latestLine.split(" ")
        if fields[-1] == "\n":
            n = len(fields)
            fields = fields[0:n-1]

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
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_UserStudy1()

  def test_UserStudy1(self):
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
    logic = UserStudyLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
