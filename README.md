# About this repository

## Objective
Processing of medical images for the identification and processing of the renal artery, in order to generate new images processed only with this artery to generate input data for a disease prediction model.

## The project involves two stages:
- Systematic generation of processed images for subsequent use (this git project).
- Training and execution of the prediction model (..) using these images.

## Other info
- [Here](https://docum-project.readthedocs.io/en/latest/index.html) its possible to find some of the week reports, in a readthedocs project
- Project carried out at the IDIAP institute, Valais Switzerland.
- Images of the Lausanne Hospital.
- Software used 3dSlicer and (..), programming languages ​​python and qt.

## Brief explanation of stages
### Gui interface
- Defining the point on the display or manually providing the start and end of the element you want to study, in this case the renal artery.
- Selection of DICOM study volumes.

### Process
- Take coordinates of the sectioned points.
- From the points create an ROI.
- Trimming of the original volume based on the defined ROI.
- Segmentation of the new volume.
- Identification of the study element and extraction of the central line.
- Volume straightening.
- Save straightened image to use as input for prediction model.

## In this repository:
- Source code.
- General scheme.

## Contact
[Lucas Stel](mailto:stel.lucas.ch@gmail.com)
