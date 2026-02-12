#!/bin/bash

a=$(dirname "$(realpath $0)")

{
echo [Desktop Entry]
echo Path=$a
echo Exec=python3 $a/saver.py
echo Icon=$a/images/desktop_icon.png
echo Name=Image Collector
echo GenericName=Image Collector
echo Comment=Application for taking images of fruit, saving the images locally and then uploading them to AWS.
echo Terminal=false
echo Type=Application
echo Categories=Application;
}>~/Desktop/imagecollector.desktop

chmod +x ~/Desktop/imagecollector.desktop
gio set ~/Desktop/imagecollector.desktop "metadata::trusted" yes
