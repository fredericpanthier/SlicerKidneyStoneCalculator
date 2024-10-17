
import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# KidneyStoneCalculator
#

class KidneyStoneCalculator(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "KidneyStoneCalculator" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Segmentation"]
    self.parent.dependencies = []
    self.parent.contributors = ["Frédéric Panthier (Urology Department, Tenon Hospital, APHP, Paris & Uurology Department, Hôpital Européen Georges Pompidou, APHP, Paris)",\
                                "Lounes Illoul (PIMM lab, Arts et Métiers Paris Tech, Paris)",\
                                "Laurent Berthe (PIMM lab, Arts et Métiers Paris Tech, Paris)",\
                                "Steeve Doizi (Urology Department, Tenon Hospital, APHP, Paris)",\
                                "Oliver Traxer (Urology Department, Tenon Hospital, APHP, Paris)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
KidneyStoneCalculator consists in a volumetric evaluation of kidney stones and also provides information on surgical duration.
Moreover, it provides the estimated time of lithotripsy and consequently the operative time.
It provides in a few seconds a 3D view of the stone(s) and axial, coronal and sagittal views with CT-scan DICOMs.
It's Licensed under the Slicer License.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Frédéric Panthier, Urology Department, Tenon Hospital, APHP, Paris et Uurology Department, Hôpital Européen Georges Pompidou, APHP, Paris.
""" # replace with organization, grant and thanks.

#
# KidneyStoneCalculatorWidget
#

class KidneyStoneCalculatorWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # threshold value
    #

    self.thresholdSlider = ctk.ctkRangeWidget()
    self.thresholdSlider.spinBoxAlignment = qt.Qt.AlignTop
    self.thresholdSlider.singleStep = 0.01
    self.thresholdSlider.minimum = 0
    self.thresholdSlider.maximum = 1
    self.thresholdSlider.minimumValue = 0
    self.thresholdSlider.maximumValue = 1
    self.thresholdSlider.enabled=False
    parametersFormLayout.addRow("Image threshold : min - max", self.thresholdSlider)

    #

    self.TLS_per_min_2=\
    {"TFL (High Peak Power)": {"272": {"Hard Stone": {"0.15": {"vpp": 0.007655, "f":  [i for i in range(5,105,5)]},
                                                       "0.5": {"vpp": 0.050916667,"f": [i for i in range(5,105,5)]},
                                                        "1.": {"vpp": 0.0744, "f":  [i for i in range(5,105,5)]},
                                                      },
                                       "Soft Stone": {"0.15": {"vpp": 0.00748, "f":  [i for i in range(5,105,5)]},
                                                       "0.5": {"vpp": 0.0524, "f":  [i for i in range(5,105,5)]},
                                                        "1.": {"vpp": 0.073966667, "f":  [i for i in range(5,105,5)]},
                                                      },
                                       },
                               "150": {"Hard Stone": {"0.15": {"vpp": 0.0059466667, "f":  [i for i in range(5,105,5)]},
                                                       "0.5": {"vpp": 0.031983333, "f":  [i for i in range(5,105,5)]},
                                                        "1.": {"vpp": 0.045788889, "f":  [i for i in range(5,105,5)]},
                                                      },
                                       "Soft Stone": {"0.15": {"vpp": 0.006295, "f":  [i for i in range(5,105,5)]},
                                                       "0.5": {"vpp": 0.034266667, "f":  [i for i in range(5,105,5)]},
                                                        "1.": {"vpp": 0.055733333, "f":  [i for i in range(5,105,5)]},
                                                      },
                                       },
                               },
    "Ho:YAG (Long Pulse)": {"272": {"Hard Stone": {"0.5": {"vpp": 0.01355, "f":  [i for i in range(5,105,5)]},
                                                    "1.": {"vpp": 0.035266667, "f":  [i for i in range(5,105,5)]}
                                                   },
                                    "Soft Stone": {"0.5": {"vpp": 0.019158333, "f":  [i for i in range(5,105,5)]},
                                                    "1.": {"vpp": 0.042888889, "f":  [i for i in range(5,105,5)]},
                                                   },
                                    },
                           },
    "p-Tm:YAG (Captive Fragmenting)": {"270": {"Hard Stone":{"0.6": {"vpp" :0.047975, "f": [i for i in range(5,105,5)]},
                                        "1.": {"vpp" :0.10565556, "f": [i for i in range(5,105,5)]},
                                       },
                         "Soft Stone":{"0.6": {"vpp" :0.047975, "f": [i for i in range(5,105,5)]},
                                        "1.": {"vpp" :0.08334444, "f": [i for i in range(5,105,5)]},
                                       },
                         },
                 "200": {"Hard Stone":{"0.6": {"vpp" :0.03073333, "f": [i for i in range(5,105,5)]},
                                        "1.": {"vpp" :0.08706667, "f": [i for i in range(5,105,5)]},
                                       },
                         "Soft Stone":{"0.6": {"vpp" :0.03843333, "f": [i for i in range(5,105,5)]},
                                        "1.": {"vpp" :0.0622, "f": [i for i in range(5,105,5)]},
                                       },
                         }, 
                },                       
    }

    self.lpreset=\
    [{"type": "p-Tm:YAG (Captive Fragmenting)", "name": "Dusting", "e": "0.6", "f": 20},
     {"type": "p-Tm:YAG (Captive Fragmenting)", "name": "Fragmentation", "e": "1.", "f": 15},
     {"type": "TFL (High Peak Power)", "name": "Dusting", "e": "0.5", "f": 30},
     {"type": "TFL (High Peak Power)", "name": "Fragmentation", "e": "1.", "f": 15},
     {"type": "Ho:YAG (Long Pulse)", "name": "Dusting", "e": "0.5", "f": 30},
     {"type": "Ho:YAG (Long Pulse)", "name": "Fragmentation", "e": "1.", "f": 15},
    ]

    self.laser_combobox=ctk.ctkComboBox()
    for i in self.TLS_per_min_2.keys():self.laser_combobox.addItem(i)
    self.laser_combobox.enabled=True
    parametersFormLayout.addRow("Laser source",self.laser_combobox)

    self.d_fiber_combobox=ctk.ctkComboBox()
    self.d_fiber_combobox.enabled=True    
    parametersFormLayout.addRow(u"laser fiber diameter (\u03BCm)",self.d_fiber_combobox)

    self.TypeOfStone_combobox=ctk.ctkComboBox()
    self.TypeOfStone_combobox.enabled=True    
    parametersFormLayout.addRow("Type of Stone",self.TypeOfStone_combobox)

    self.ManualPreset_combobox=ctk.ctkComboBox()
    self.ManualPreset_combobox.enabled=True
    parametersFormLayout.addRow(self.ManualPreset_combobox)

    self.EnergyJ_combobox=ctk.ctkComboBox()
    self.EnergyJ_combobox.enabled=True    
    parametersFormLayout.addRow("Energy (J)",self.EnergyJ_combobox)

    self.Frequence_combobox=ctk.ctkComboBox()
    self.Frequence_combobox.enabled=True    
    parametersFormLayout.addRow("Pulse Rate(Hz)",self.Frequence_combobox)

    #
    # voxels split
    #

    self.splitVoxelsCheckBox=ctk.ctkCheckBox()
    self.splitVoxelsCheckBox.checked=False
    parametersFormLayout.addRow("split islands to segments", self.splitVoxelsCheckBox)

    #

    self.minimumSizeSpinBox = qt.QSpinBox()
    self.minimumSizeSpinBox.setToolTip("Islands consisting of less voxels than this minimum size, will be deleted.")
    self.minimumSizeSpinBox.setMinimum(0)
    self.minimumSizeSpinBox.setMaximum(vtk.VTK_INT_MAX)
    self.minimumSizeSpinBox.setValue(1000)
    self.minimumSizeSpinBox.suffix = " voxels"
    parametersFormLayout.addRow("Minimum size:", self.minimumSizeSpinBox)
    self.minimumSizeSpinBox.enabled=False
    #
    # Preview results in 3D
    #

    self.previewShow3DCheckBox = qt.QCheckBox()
    self.previewShow3DCheckBox.setToolTip("Preview results in 3D.")
    self.previewShow3DCheckBox.enabled = True
    self.previewShow3DCheckBox.checked = False
    parametersFormLayout.addRow("Show in 3D", self.previewShow3DCheckBox)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    #

    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.splitVoxelsCheckBox.connect('clicked(bool)',self.onCheckSplit)
    self.previewShow3DCheckBox.connect('clicked(bool)',self.onCheckpreviewShow3D)


    self.laser_combobox.connect("activated(int)",self.onLaserSelect)
    self.d_fiber_combobox.connect("activated(int)",self.ondfiberSelect)
    self.TypeOfStone_combobox.connect("activated(int)",self.onTypeOfStoneSelect)
    self.ManualPreset_combobox.connect("activated(int)",self.onManualPresetSelect)
    self.EnergyJ_combobox.connect("activated(int)",self.onEnergyJSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

    self.onLaserSelect()

  def cleanup(self):
    pass

  def onLaserSelect(self):

    self.d_fiber_combobox.clear()
    for i in self.TLS_per_min_2[self.laser_combobox.currentText].keys():self.d_fiber_combobox.addItem(i)
    self.ondfiberSelect()
    
  def ondfiberSelect(self):

    self.TypeOfStone_combobox.clear()
    for i in self.TLS_per_min_2[self.laser_combobox.currentText][self.d_fiber_combobox.currentText].keys():self.TypeOfStone_combobox.addItem(i)
    self.onTypeOfStoneSelect()

  def onTypeOfStoneSelect(self):

    self.ManualPreset_combobox.clear()
    self.ManualPreset_combobox.addItem("Manual")
    for i in range(len(self.lpreset)): 
      if self.lpreset[i]["type"]==self.laser_combobox.currentText:self.ManualPreset_combobox.addItem(self.lpreset[i]["name"],i)

    self.onManualPresetSelect()

  def onManualPresetSelect(self):

    if self.ManualPreset_combobox.currentText == "Manual":
      self.EnergyJ_combobox.clear()
      for i in self.TLS_per_min_2[self.laser_combobox.currentText][self.d_fiber_combobox.currentText][self.TypeOfStone_combobox.currentText].keys():self.EnergyJ_combobox.addItem(i)
      self.onEnergyJSelect()
      self.EnergyJ_combobox.enabled=True
      self.Frequence_combobox.enabled=True
    else :
      self.EnergyJ_combobox.clear()
      self.Frequence_combobox.clear()
      i=self.ManualPreset_combobox.currentData
      self.EnergyJ_combobox.addItem(self.lpreset[i]["e"])
      self.Frequence_combobox.addItem(self.lpreset[i]["f"])
      self.EnergyJ_combobox.enabled=False
      self.Frequence_combobox.enabled=False

  def onEnergyJSelect(self):

    self.Frequence_combobox.clear()
    f=self.TLS_per_min_2[self.laser_combobox.currentText][self.d_fiber_combobox.currentText][self.TypeOfStone_combobox.currentText][self.EnergyJ_combobox.currentText]["f"]
    for i in range(len(f)):self.Frequence_combobox.addItem(f[i],i)
    
  def onCheckSplit(self):
    self.minimumSizeSpinBox.enabled=self.splitVoxelsCheckBox.checked

  def onCheckpreviewShow3D(self):

    inputVolume=self.inputSelector.currentNode()
    if inputVolume is not None:
      previewShow3D=self.previewShow3DCheckBox.checked
      logic = KidneyStoneCalculatorLogic()
      logic.setpreviewShow3D(inputVolume,previewShow3D)
       
  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() #and self.outputSelector.currentNode()

    if self.inputSelector.currentNode():
      logic = KidneyStoneCalculatorLogic()
      range = logic.get_min_max_data(self.inputSelector.currentNode())
      if range is not None :
        print (range)

        self.thresholdSlider.enabled=True
        self.thresholdSlider.minimum = range[0]
        self.thresholdSlider.maximum = range[1]
        self.thresholdSlider.minimumValue = range[0]
        self.thresholdSlider.maximumValue = range[1]

  def onApplyButton(self):
    logic = KidneyStoneCalculatorLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    imageThreshold_min=self.thresholdSlider.minimumValue
    imageThreshold_max=self.thresholdSlider.maximumValue
    minimumVoxelsize = self.minimumSizeSpinBox.value if self.minimumSizeSpinBox.enabled else None
    
    if self.ManualPreset_combobox.currentText == "Manual":
        f=self.TLS_per_min_2[self.laser_combobox.currentText][self.d_fiber_combobox.currentText][self.TypeOfStone_combobox.currentText]\
                            [self.EnergyJ_combobox.currentText]["f"][self.Frequence_combobox.currentData]
        vpp=self.TLS_per_min_2[self.laser_combobox.currentText][self.d_fiber_combobox.currentText][self.TypeOfStone_combobox.currentText]\
                            [self.EnergyJ_combobox.currentText]["vpp"]
    else :
      i=self.ManualPreset_combobox.currentData
      f=self.lpreset[i]["f"]
      vpp=self.TLS_per_min_2[self.laser_combobox.currentText][self.d_fiber_combobox.currentText][self.TypeOfStone_combobox.currentText]\
                            [self.lpreset[i]["e"]]["vpp"]

    tls_per_min=f*vpp*60.
    print ("tls (mm3/min): ",tls_per_min)

    logic.run(self.inputSelector.currentNode(), imageThreshold_min,imageThreshold_max,minimumVoxelsize,tls_per_min,enableScreenshotsFlag)#self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

#
# KidneyStoneCalculatorLogic
#

class KidneyStoneCalculatorLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def get_min_max_data(self,volumeNode):
    if volumeNode.GetImageData() is not None :
        return volumeNode.GetImageData().GetScalarRange()

  def setpreviewShow3D(self,inputVolume,previewShow3D):
    if not self.isValidInputData(inputVolume):
      slicer.util.errorDisplay('Input volume error.')
      
    masterVolumeNode=inputVolume

    # Cet segmentation
    SegmentationNodeCol=slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    SegmentationNodeCol.UnRegister(slicer.mrmlScene)
    b=False
    for SegmentationNode in SegmentationNodeCol:
      if SegmentationNode.GetName() == "rc_seg":
        b=True
        break
    
    if b:
      containsClosedSurfaceRepresentation = SegmentationNode.GetSegmentation().ContainsRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())
      if containsClosedSurfaceRepresentation :
        if not previewShow3D : SegmentationNode.RemoveClosedSurfaceRepresentation()
      elif previewShow3D: 
        SegmentationNode.CreateClosedSurfaceRepresentation()
        
    return True 

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

  def isValidInputData(self, inputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputData failed: no input volume node defined')
      return False
    return True

  def run(self, inputVolume, imageThreshold_min,imageThreshold_max,minimumVoxelsize,tls_per_min,enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputData(inputVolume):
      slicer.util.errorDisplay('Input volume error.')
      return False

    logging.info('Processing started')

    masterVolumeNode=inputVolume

    # Create segmentation
    SegmentationNodeCol=slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    SegmentationNodeCol.UnRegister(slicer.mrmlScene)
    b=True
    for SegmentationNode in SegmentationNodeCol:
        if SegmentationNode.GetName() == "rc_seg":
            SegmentationNode.GetSegmentation().RemoveAllSegments()
            SegmentationNode.GetDisplayNode().ClearSegmentDisplayProperties()
            print("segmantation rc_seg cleared ")
            b=False
            break
         
    if b : 
        SegmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        SegmentationNode.UnRegister(slicer.mrmlScene)
        SegmentationNode.SetName("rc_seg")
        print("segmantation created : ",SegmentationNode.GetName())
        SegmentationNode.CreateDefaultDisplayNodes() # only needed for display
        SegmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)

    addedSegmentID = SegmentationNode.GetSegmentation().AddEmptySegment(SegmentationNode.GetName()+"_")
  
    # Create temporary segment editor to get access to effects
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorNode.SetSelectedSegmentID(addedSegmentID)

    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(SegmentationNode)
    segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)

    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()

    # Fill by thresholding
    
    effect.setParameter("MinimumThreshold",str(imageThreshold_min))
    effect.setParameter("MaximumThreshold",str(imageThreshold_max))
    effect.self().onApply()

    # Fill by thresholding
    if minimumVoxelsize is not None :
        segmentEditorWidget.setActiveEffectByName("Islands")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("Operation", "SPLIT_ISLANDS_TO_SEGMENTS")
        effect.setParameter("MinimumSize",minimumVoxelsize)
        effect.self().onApply()

    # Compute segment volumes
    resultsTableNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')
    resultsTableNode.UnRegister(slicer.mrmlScene)

    import SegmentStatistics
    segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic.getParameterNode().SetParameter("Segmentation", SegmentationNode.GetID())
    segStatLogic.getParameterNode().SetParameter("ScalarVolume", masterVolumeNode.GetID())
    
    segStatLogic.getParameterNode().SetParameter("ClosedSurfaceSegmentStatisticsPlugin.enabled","False")
    segStatLogic.getParameterNode().SetParameter("ClosedSurfaceSegmentStatisticsPlugin.surface_mm2.enabled","False")
    segStatLogic.getParameterNode().SetParameter("ClosedSurfaceSegmentStatisticsPlugin.volume_cm3.enabled","False")
    segStatLogic.getParameterNode().SetParameter("ClosedSurfaceSegmentStatisticsPlugin.volume_mm3.enabled","False")
    
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.enabled","False")
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.volume_cm3.enabled","False")
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.volume_mm3.enabled","False")
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.voxel_count.enabled","False")
    
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.enabled","True")
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.max.enabled","True")
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.mean.enabled","True")
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.median.enabled","True")
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.min.enabled","True")
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.stdev.enabled","True")
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.volume_mm3.enabled","True")
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.volume_cm3.enabled","True")
    segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.voxel_count.enabled","False")
    
    segStatLogic.computeStatistics()
    segStatLogic.exportToTable(resultsTableNode)
    col=resultsTableNode.AddColumn()
    col.SetName("Time of lithotripsy [min:sec:1/100s]")
    id_colone_vmm3=resultsTableNode.GetColumnIndex("Volume [mm3]")
    if id_colone_vmm3 == -1: id_colone_vmm3=resultsTableNode.GetColumnIndex("Volume mm3")
    assert id_colone_vmm3 != -1
    
    id_colone_Tl=resultsTableNode.GetColumnIndex("Time of lithotripsy [min:sec:1/100s]")

    import math
    for i in range (resultsTableNode.GetNumberOfRows()):
        vol_i=float(resultsTableNode.GetCellText(i,id_colone_vmm3))
        tl_i=math.modf(vol_i/tls_per_min)
        tl_i_min=int(tl_i[1])
        tli_1=math.modf(60.*tl_i[0])
        tli_sec=int(tli_1[1])
        tli_cent=100*tli_1[0]
        resultsTableNode.SetCellText(i,id_colone_Tl,"{:d}:{:d}:{:.0f}".format(tl_i_min,tli_sec,tli_cent))

    segStatLogic.showTable(resultsTableNode)

    logging.info('Processing completed !')

    return True



class KidneyStoneCalculatorTest(ScriptedLoadableModuleTest):
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
    self.test_KidneyStoneCalculator1()

  def test_KidneyStoneCalculator1(self):
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
    logic = KidneyStoneCalculatorLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')

