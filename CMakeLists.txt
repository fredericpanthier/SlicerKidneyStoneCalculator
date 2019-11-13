cmake_minimum_required(VERSION 3.13.4)

project(KidneyStoneCalculator)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/KidneyStoneCalculator")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Frédéric Panthier, Lounes Illoul, Laurent Berthe, Steeve Doizi, Oliver Traxer")
set(EXTENSION_DESCRIPTION "“KidneyStoneCalculator” consists in a volumetric evaluation of kidney stones and also provides information on surgical duration. Moreover, it provides the estimated time of lithotripsy and consequently the operative time. It provides in a few seconds a 3D view of the stone(s) and axial, coronal and sagittal views with CT-scan DICOMs. ")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/fredericpanthier/SlicerKidneyStoneCalculator/master/icon.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/fredericpanthier/SlicerKidneyStoneCalculator/master/screenshot.jpg")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(KidneyStoneCalculator)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
