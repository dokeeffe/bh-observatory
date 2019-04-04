#!/bin/bash
timestamp=`date -u "+%F_%H_%M"`
convert -resize 25% -delay 5 -loop 0 ~/Pictures/allsky/stage/allsky*.jpg ~/Dropbox/allsky-25${timestamp}.gif
#convert -resize 50% -delay 5 -loop 0 ~/Pictures/allsky/allsky*.jpg ~/Dropbox/allsky-50${timestamp}.gif
ffmpeg -framerate 15 -pattern_type glob -i '/home/dokeeffe/Pictures/allsky/stage/allsky*.jpg' -c:v libx264 ~/Dropbox/allsky${timestamp}.mp4
