#!/bin/bash
convert -resize 25% -delay 5 -loop 0 ~/Pictures/allsky/allsky*.jpg ~/Dropbox/allsky-25.gif
# convert -resize 50% -delay 5 -loop 0 ~/Pictures/allsky/allsky*.jpg ~/Dropbox/allsky-50.gif
ffmpeg -framerate 15 -pattern_type glob -i '/home/dokeeffe/Pictures/allsky/allsky*.jpg' -c:v libx264 ~/Dropbox/allsky.mp4
