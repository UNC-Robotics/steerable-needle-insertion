# UserStudyNeedleStartPose

# Introduction
This repository contains a module for 3D Slicer (v5.2.2).
The purpose of this module is to create a platform for an academic user study 
simulating a surgical setup for the manual initial insertion of a multi-stage steerable needle robot 
conducting a liver biopsy. In practice, the variability in precision during the initial insertion of a steerable needle 
robot substantially influences the probability of success for a surgical procedure, such as a biopsy, under motion 
planning constraints. To refine this technology for reliable usage in a real surgical environment, it's essential 
to gather data on user behavior with respect to the precision of the initial insertion. The purpose of the proposed study is to gather this data. 

This module is intended to be used alongside a physical setup, mapping the virtual elements of the simulation 
to a physical environment. The virtual environment is registered in both position and orientation to the physical environment, 
and updates in the physical position of the needle controller are mapped to the virtual environment's corresponding 
model. However, the module is able to run independently of any hardware required for the user study.

# Installation
First, clone this repository to any location on your device.
To load the anatomical segmentations into the environment later on, you'll need to download some [segmentation files](https://drive.google.com/drive/folders/1-5JbVDJLhfWWK-OxQ-U0SFezlpGjRG-k?usp=sharing)[1]
to any directory. Ensure that all three files are located in the same directory, and file names are not altered. 
To run the module in 3D Slicer locally, you'll need to install 3D Slicer version 5.2.2 at https://download.slicer.org/.

After installing 3D Slicer v5.2.2, navigate to the module finder.
From there, select:

Extension Wizard > Switch to module > Select Extension

You'll be prompted to select a directory in your file explorer. Navigate to the cloned repository and select it. Next, you'll be prompted to add the paths of the following modules to your module selector:
- LoadSegmentations 
- UserStudy

Add both. The LoadSegmentations module is a helper module used to load the anatomical segmentation models into the virtual environment.

# UI Elements

With the UserStudy module selected, you will be presented a dropdown section titled "UserStudy" in your module panel on 3D Slicer.
This dropdown section contains the UI used to configure environment settings. The UserStudy module's functionality is designed to be
self-contained, so it isn't necessary to access other elements of the 3D Slicer UI to set up the virtual environment.

Within the module's UI, click the "Load Environment" button. You'll be prompted to select a directory. Select the directory containing
the segmentation files downloaded earlier. Once you've selected a directory, you will see a single 3D panel in Slicer, displaying a static model
of the needle controller. Additionally, other UI elements are enabled.

- **Select View**\
  &nbsp; &nbsp; The Select View dropdown menu allows you to select one of any preconfigured 16 layouts for your 3D views. These layouts span from one displayed 3D panel to five displayed 3D panels. Each view panel is associated with a virtual camera object defining the perspective of the view on the virtual environment. Read more about the views below.
- **Select Order**\
  &nbsp; &nbsp; The Select Order input field changes the order of the 3D views based on the input. Views are assigned order from left to right, top to bottom.
- **Stream Data**\
  &nbsp; &nbsp; Enable data streaming from physical needle controller.
- **Select Recording**\
  &nbsp; &nbsp; If a needle controller is not available, select a recording for needle movement playback.
- **Start/Stop Needle**\
  &nbsp; &nbsp; Start or pause needle movement. Can use with recordings or data streaming from needle controller.
- **Reset Needle**\
  &nbsp; &nbsp; Reset position and orientation of needle to its start pose.
- **Colored Regions**\
  &nbsp; &nbsp; Enable or disable display of color-changing regions, along with their corresponding color legends.

The entire module UI is included for research purposes. Participants will only be presented with the 3D panel views. To switch between participant and researcher views, press CTRL+B

# Views/Cameras:
- **View 1:**\
  &nbsp; &nbsp; The first view's camera is positioned to emulate the user study participant's perspective on the physical environment. This is a frontal view, partially looking down on the environment.
- **View 2:**\
  &nbsp; &nbsp; The second view's camera is an ego view fixed to the shaft of the needle. The camera's position updates dynamically as the needle moves through the environment.
- **View 3:**\
  &nbsp; &nbsp; The third view's camera is fixed directly behind the line representative of the desired start pose. In this view, the start pose appears as a point, and the cone representative of the accepted angles of insertion as a circle. Given that the needle model is positioned with exact precision, it will appear as a point overlaid on top of the start pose.
- **View 4:**\
  &nbsp; &nbsp; The fourth view's camera is positioned directly to the left of the environment, with the previously front facing part of the environment now facing towards the right.
- **View 5:**\
  &nbsp; &nbsp; The fifth view's camera is positioned directly above the environment as a bird's eye view. The previously front facing part of the environment is now facing downwards.

# User Study
The user study presents participants with a learning phase, during which the participant will learn how the physical movements of the needle controller map to the virtual environment. First, participants are instructed to position the tip of the needle inside the boundaries of a small sphere appearing in the virtual 3D space. Second, participants are instructed to match the needle's orientation to a line overlaid by a cone. Third, participants are instructed to match both the position of the tip of the needle inside the boundaries of a sphere, along with a desired orientation. Finally, the participant will complete the actual experiment, where they will attempt to match the needle's position to the desired start pose. The acceptable points of insertion are represented by a color-changing circle, with its center being the desired point of insertion. The acceptable angles of insertion are represented by a color-changing cone, with the needle's desired start pose located at its center.

Both the color-changing regions will change color indicative of precision, where green is most precise and red is least. Positional precision is calculated by the distance from the desired insertion point on the skin model to the position of the needle's tip. Any distance beyond the radius of the circle (or a sphere during the learning phase) is considered 0% precise. Similarly, orientational precision is calculated by the angular difference between the forward vectors of the desired start pose line, and the tip of the needle. Any angular difference exceeding the range of angles represented by the cone is considered 0% precise.

At any time during the study, participants are able to press spacebar to proceed to the next step.

# References

[1]I. Fried, A. J. Akulian, and R. Alterovitz, “A Clinical Dataset for the Evaluation of Motion Planners in Medical Applications,” 2022.
