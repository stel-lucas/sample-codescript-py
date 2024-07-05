# About this repository

## Objective
Process real medical images to identify the renal artery, generating new images processed only with this artery and then generate input data for a disease prediction model.

Scripts developped in py, interact with functions and kernel from opensource code. This is late propagated use the HPC with model to do a large processing, calculation and prediction.

## The project involves two stages:
- Systematic generation of processed images for subsequent use (this git project).
- Training and execution of prediction models ML and HPC using these images.

## Other info
- [Here](https://docum-project.readthedocs.io/en/latest/index.html) its possible to find some of the week reports, in a readthedocs project
- Project carried out at the IDIAP institute, Valais Switzerland.
- Images of the Lausanne Hospital.
- Functions form 3dSlicer, others, programming languages ​​python and qt.

## Brief explanation of stages
### Gui interface
- Defining the points on the display or manually providing the start and end of the element we want to study, in this case the renal artery.
- Selection of DICOM study volumes.

![image](https://github.com/stel-lucas/sample-codescript-py/blob/main/Img/1.png)

### Process
- Take coordinates of the sectioned points.
- From the points create an ROI.
- Trimming of the original volume based on the defined ROI.
- Segmentation of the new volume.
![image](https://github.com/stel-lucas/sample-codescript-py/blob/main/Img/2.png)
- Identification of the study element and extraction of the central line.
![image](https://github.com/stel-lucas/sample-codescript-py/blob/main/Img/3.png)
- Volume straightening.
- Save straightened image to use as input for prediction model.

![image](https://github.com/stel-lucas/sample-codescript-py/blob/main/Img/4.png)

## In this repository:
- Source code.
- General scheme.

## Contact
[Lucas Stel](mailto:stel.lucas.ch@gmail.com)
