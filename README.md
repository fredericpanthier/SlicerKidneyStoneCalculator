SlicerKidneyStoneCalculator
===========================

“KidneyStoneCalculator” consists in a volumetric evaluation of kidney stones and also provides information on surgical duration. Moreover, it provides the estimated time of lithotripsy and consequently the operative time. It provides in a few seconds a 3D view of the stone(s) and axial, coronal and sagittal views with CT-scan DICOMs.
It's Licensed under the [Slicer License](https://github.com/Slicer/Slicer/blob/master/License.txt). 

Running and Using
=================

Below, we describe the Instructions Guide to use KidneyStoneCalculator:

1. Open 3DSlicer and download “KidneyStoneCalculator” using the “Extension Manager”
2. Import DICOM data from a CT-scan (better with non-enhanced series)
3. Open “Crop Volume” module 
   - a. “Create a new annotation ROI” (Region Of Interest)
   - b. Size the ROI in x, y and z axes using axial (red), sagittal (yellow) and coronal (green) view in four-up disposition. 
   - c. Create a new volume (name will be: “name cropped”)
   - d. Click “Apply” button
4. Open “KidneyStoneCalculator” module:
   - a. Select volume: “name cropped”
   - b. Choose threshold (houndfields units) minimum and maximun to fit to the stone
   - c. If there are multiples stones select “split islands into segments” with a recommended “minimum size” of 40 voxels
   - d. Select a mode of treatment (laser source, core-diameter of laser fiber, laser settings and stone type)
   - e. Select “show 3D” if you want to visualize in 3D-view the segmented stone(s)
   - f. Click “Apply” button. A table will appear to show the segment’s name, volume (mm3) and time of lithotripsy (min)

[Wiki documentation](https://www.slicer.org/wiki/Documentation/Nightly/Modules/KidneyStoneCalculator)

Dependencies
=======================

1. Git    (www.git-scm.com)
2. Slicer (www.slicer.org)

*Developped by : Frédéric Panthier (1,2), Lounès Illoul (3), Laurent Berthe (3), Steeve Doizi (1), Oliver Traxer (1).
(1) Urology Department, Tenon Hospital, APHP, Paris.
(2) Uurology Department, Hôpital Européen Georges Pompidou, APHP, Paris.
(3) PIMM lab, Arts et Métiers Paris Tech, Paris.
 
