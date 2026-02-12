# Image Collector GUI
## Overview
This software allows the user to take images of fruit and label them (fruit type, fruit variety, defects, weight), and then upload them to cloud storage on AWS.

## Installation
In order for the gui to run correctly, ROS 1 needs to be installed (Melodic) on a machine running on Ubuntu 18.04. This also depends on python3 so do not use with python2.

## The following packages are also required:

### Installing python 3:
    apt install python3 python3-pip python3-venv python3-tk

### Installing the python environment:
    python3 -m venv ./venv

### Installing required dependancies:
    pip3 install -r requirements.txt

## Files
### desktop_maker.sh 
A script which dynamically generates a desktop icon to launch the gui.

### upload.sh
A script which sync's the images from the local files (/images/<fruit type>) to AWS.

### config.yaml
A configuration file which contains all the fruit names, as well as options to switch between fruits and decide whether only colour images are saved.

### saver.py
The python script for the application.

## Deb file

To make a deb file run the following in the root of the project:
    make installer; make deb-package

Please note that this needs to be built on an 18.04 PC. This should mean that
the installer will work on an 18.04+ Ubuntu installation.
# image-collector
