from __main__ import vtk, qt, ctk, slicer
import numpy as np
import os
import ExtractCenterline
import CurvedPlanarReformat

#
# FullAutoStraight
#

class FullAutoStraight:
    def __init__(self, parent):
        parent.title = "Full Auto Straightened Volume"
        parent.categories = ["Biosignal Modules"]
        parent.dependencies = []
        parent.contributors = ["Lucas / Biosignal Group"]
        parent.helpText = """
    Starting with a data set DICOM, this module creates a straightened volume, running all the process needed for that
    automatically.
    """
        parent.acknowledgementText = """
    This module is based in the test 1, 2, 3, 4."""
        self.parent = parent

#
# FullAutoStraightWidget
#

class FullAutoStraightWidget:
    def __init__(self, parent=None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):

        # The user interface includes: collapsible button, a part for the volumes
        # and a button. Note: tests using a file QtDesigner is needed.

        # Collapsible button: cb_1
        self.cb_1 = ctk.ctkCollapsibleButton()
        self.cb_1.text = "Section: Points"
        self.layout.addWidget(self.cb_1)

        # Layout 1: la_1
        self.la_1 = qt.QFormLayout(self.cb_1)

        # Volumes selectors
        self.inputFrame = qt.QFrame(self.cb_1)
        self.inputFrame.setLayout(qt.QHBoxLayout())
        self.la_1.addWidget(self.inputFrame)
        self.inputSelector = qt.QLabel("Chose input volume: ", self.inputFrame)
        self.inputFrame.layout().addWidget(self.inputSelector)
        self.inputSelector = slicer.qMRMLNodeComboBox(self.inputFrame)
        self.inputSelector.nodeTypes = (("vtkMRMLScalarVolumeNode"), "")
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False
        self.inputSelector.setMRMLScene(slicer.mrmlScene)
        self.inputFrame.layout().addWidget(self.inputSelector)

        # Apply button: b_1
        b_1 = qt.QPushButton("Point selection")
        b_1.toolTip = "Select just two points."
        self.la_1.addWidget(b_1)
        b_1.connect('clicked(bool)', self.onb_1Apply)

        # Apply button: b_2
        b_2 = qt.QPushButton("Run the process")
        b_2.toolTip = "Select two points and then run."
        self.la_1.addWidget(b_2)
        b_2.connect('clicked(bool)', self.onb_2Apply)

        # Add vertical spacer
        self.layout.addStretch(1)

#
## Logic section
#

    def onb_1Apply(self):
        # Set points
        placeModePersistence = 0
        slicer.modules.markups.logic().StartPlaceMode(placeModePersistence)

    def onb_2Apply(self):

        ###################### First Process: Definition initial points ############
        # Take coordinates of points and creation of center point base on them
        pun1 = vtk.vtkVector3d(0, 0, 0) #np.array([0, 0, 0])
        pun2 = vtk.vtkVector3d(0, 0, 0)
        pointListNode = slicer.util.getNode("F")
        pointListNode.GetNthControlPointPosition(0, pun1)
        pointListNode.GetNthControlPointPosition(1, pun2)
        punc = vtk.vtkVector3d((pun1[0]+pun2[0])/2, (pun1[1]+pun2[1])/2, (pun1[2]+pun2[2])/2)


        ###################### Process: Definition ROI ######################
        # Create a new ROI
        roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLAnnotationROINode")
        roiNode.SetXYZ(punc)
        punc_d = vtk.vtkVector3d((abs(pun1[0]-pun2[0]))/2, (abs(pun1[1]-pun2[1]))/2, (abs(pun1[2]-pun2[2]))/2)
        roiNode.SetRadiusXYZ(punc_d)


        ###################### Process: Crop ###############################
        # Make the crop and create new volume
        inputVolume = self.inputSelector.currentNode()
        cropVolumeLogic = slicer.modules.cropvolume.logic()
        cropVolumeParameterNode = slicer.vtkMRMLCropVolumeParametersNode()
        cropVolumeParameterNode.SetROINodeID(roiNode.GetID())
        cropVolumeParameterNode.SetInputVolumeNodeID(inputVolume.GetID())
        cropVolumeParameterNode.SetVoxelBased(True)
        cropVolumeParameterNode.SetSpacingScalingConst(0.0)
        cropVolumeLogic.Apply(cropVolumeParameterNode)
        croppedVolume = slicer.mrmlScene.GetNodeByID(cropVolumeParameterNode.GetOutputVolumeNodeID())


        ###################### Process: Segmentation ######################
        # Create segmentation
        segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segmentationNode.CreateDefaultDisplayNodes()
        segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(croppedVolume)
        addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment("skin")

        # Create segment editor to get access to effects
        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode)
        segmentEditorWidget.setMasterVolumeNode(croppedVolume)

        # Thresholding
        segmentEditorWidget.setActiveEffectByName("Threshold")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("MinimumThreshold", "160")
        effect.setParameter("MaximumThreshold", "700")
        effect.self().onApply()

        # Clean up the segmentEditorWidget
        segmentEditorWidget = None
        slicer.mrmlScene.RemoveNode(segmentEditorNode)


        ###################### Process: Extract center line ##################
        # Segment data needed
        segmentName = 'skin'
        segmentID = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName(segmentName)

        extractLogic = ExtractCenterline.ExtractCenterlineLogic()

        # Preprocess the surface
        inputSurfacePolyData = extractLogic.polyDataFromNode(segmentationNode, segmentID)
        targetNumberOfPoints = 5000.0
        decimationAggressiveness = 4 # I had to lower this to 3.5 in at least one case to get it to work, 4 is the default in the module
        subdivideInputSurface = False
        preprocessedPolyData = extractLogic.preprocess(inputSurfacePolyData, targetNumberOfPoints, decimationAggressiveness, subdivideInputSurface)

        # Extract the centerline
        centerlineCurveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode", "Centerline curve")
        centerlinePolyData, voronoiDiagramPolyData = extractLogic.extractCenterline(preprocessedPolyData, pointListNode)
        centerlinePropertiesTableNode = None
        extractLogic.createCurveTreeFromCenterline(centerlinePolyData, centerlineCurveNode, centerlinePropertiesTableNode)


        ###################### Process: Straightened Volume ################################
        # Settings of the process
        fieldOfView = [40.0, 40.0]
        outputSpacing = [0.5, 0.5, 1.0]

        # Calling logic section of the module CurvedPlanarReformat
        logic = CurvedPlanarReformat.CurvedPlanarReformatLogic()

        # Creating node and using the module
        straighteningTransformNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTransformNode','Straightening transform')
        logic.computeStraighteningTransform(straighteningTransformNode, centerlineCurveNode, fieldOfView, outputSpacing[2])
        straightenedVolume = slicer.modules.volumes.logic().CloneVolume(inputVolume,inputVolume.GetName()+' straightened')
        logic.straightenVolume(straightenedVolume, inputVolume, outputSpacing, straighteningTransformNode)

        # Remove this node because its not necessary to show it
        slicer.mrmlScene.RemoveNode(straighteningTransformNode)


        ###################### Last Process: Save output ###################################
        f_older = slicer.mrmlScene.GetNodeByID('vtkMRMLScalarVolumeNode1').GetName()
        os.mkdir(f_older)

        P_oints = slicer.util.getNode('vtkMRMLMarkupsFiducialNode1')
        V_olumecropped = slicer.util.getNode('vtkMRMLScalarVolumeNode2')
        S_egmen = slicer.util.getNode('vtkMRMLSegmentationNode1')
        C_enterLine = slicer.util.getNode('vtkMRMLMarkupsCurveNode1')
        St_raightenedVolume = slicer.util.getNode('vtkMRMLScalarVolumeNode3')

        slicer.util.saveNode(P_oints, '/idiap/home/lstel/Desktop/Data/Slicer-5.0.3-linux-amd64/'+str(f_older)+'/initialpoints_'+str(f_older)+'.json')
        slicer.util.saveNode(V_olumecropped, '/idiap/home/lstel/Desktop/Data/Slicer-5.0.3-linux-amd64/'+str(f_older)+'/croppvolume_'+str(f_older)+'.nrrd')
        slicer.util.saveNode(S_egmen, '/idiap/home/lstel/Desktop/Data/Slicer-5.0.3-linux-amd64/'+str(f_older)+'/segmentation_'+str(f_older)+'.seg.nrrd')
        slicer.util.saveNode(C_enterLine, '/idiap/home/lstel/Desktop/Data/Slicer-5.0.3-linux-amd64/'+str(f_older)+'/centerline_'+str(f_older)+'.json')
        slicer.util.saveNode(St_raightenedVolume, '/idiap/home/lstel/Desktop/Data/Slicer-5.0.3-linux-amd64/' + str(f_older)+'/straightenedVolume_'+str(f_older)+'.nrrd')

