# UserStudyNeedleStartPose

# Introduction
This repository contains a module for 3D Slicer (v5.2.2).
The purpose of this module is to create a platform for an academic user study 
simulating a surgical setup for the manual initial insertion of a multi-stage steerable needle robot 
conducting a liver biopsy. In practice, precision variability upon the initial insertion of a steerable needle 
robot substantially influences the probability of success for a surgical procedure, such as a biopsy, under motion 
planning constraints. To refine this technology for reliable usage in a real surgical environment, it's essential 
to gather data on user behavior with respect to the precision of the initial insertion and the potential for visual elements 
to alter such behavior. The purpose of the proposed study is to gather this data. 

This module is intended to be used alongside a physical setup, mapping the virtual elements of the simulation 
to a physical environment. The corresponding physical needle controller is registered to the virtual environment, 
and updates changes in physical position to the virtual environment. However, the module is able to run independently of
any hardware required for the user study.

# Installation
First, clone this repository to any location on your device.
To load the anatomical segmentations into the environment later on, you'll need to download some [segmentation files](https://drive.google.com/drive/folders/1-5JbVDJLhfWWK-OxQ-U0SFezlpGjRG-k?usp=sharing)
to any directory. Ensure that all three files are located in the same directory, and file names are not altered. 
To run the module in 3D Slicer locally, you'll need to 3D Slicer version 3.2.2 at https://download.slicer.org/.

Once 3D Slicer v5.2.2 is installed, navigate to the module finder.
From there, select:

Extension Wizard > Switch to module > Select Extension

You'll be prompted to select a directory in your file explorer. Navigate to the cloned repository and select it. Next, you'll be prompted to add the following module's paths to your module selector:
- LoadSegmentations 
- UserStudy

Add both. The LoadSegmentations module is a helper module used to load the segmentation files into the virtual environment.

# Usage

With the UserStudy module selected, you should have a dropdown section titled "UserStudy" in your module panel on 3D Slicer.
This dropdown section contains the UI used to configure environment settings. The UserStudy module's functionality is designed to be
self-contained, so it isn't be necessary to access other elements of the 3D Slicer UI to set up the virtual environment.

Within the module's UI, click the "Load Environment" button. You'll be prompted to select a directory. Select the directory containing
the segmentation files downloaded earlier. Once you've selected a directory, you should see a single 3D panel in Slicer, containing a static model
of the needle controller. Additionally, other UI elements are enabled.

#### UI Elements:
- Select View\
  &nbsp; &nbsp; The Select View dropdown menu allows you to select one of any preconfigured 16 layouts for your 3D views. These views span from 1 displayed 3D panel to 5 displayed 3D panels. Each view panel is associated with a virtual camera object defining the perspective of the view on the virtual environment.
