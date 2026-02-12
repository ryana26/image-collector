#!/bin/bash

if [ $# -eq 0 ]; then
exit

else
a=$(dirname "$(realpath $0)")
b=$HOSTNAME
c=$(date +'%Y-%m-%d')
d=$1
aws s3 mv $a/images/$d s3://image-collector/$b/$c/$d --exclude "*" --include "*.jpg" --include "*.ply" --recursive
fi
aws s3 cp $a/image_details.csv s3://image-collector/$b/image_details.csv
